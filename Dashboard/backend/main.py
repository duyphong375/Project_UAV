"""Loopback FastAPI MOCK service with owned startup/shutdown tasks."""

import asyncio
import sqlite3
import time
from contextlib import asynccontextmanager

import anyio
from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware

from .config import Settings
from .mock_source import run_mock
from .replay_engine import ReplayEngine
from .schemas import ReplaySeekRequest, ReplaySpeedRequest, ReplayStartRequest
from .sqlite_logger import SQLiteLogger
from .state import Hub, MissionStore


async def send_events(websocket, client, hub):
    while True:
        event = await client.queue.get()
        try:
            await asyncio.wait_for(websocket.send_json(event), hub.store.settings.send_timeout_sec)
        except TimeoutError:
            hub.fail(client, timeout=True)
            return
        finally:
            client.queue.task_done()


def create_app(
    settings=Settings(), *, replay_clock=time.monotonic,
    replay_sleeper=asyncio.sleep, hardware=None,
):
    async def stop_mock_source(hub):
        if hub.source_task:
            hub.source_task.cancel()
            await asyncio.gather(hub.source_task, return_exceptions=True)
            hub.source_task = None

    async def start_mock_source(hub):
        if settings.enable_mock and hub.source_task is None:
            hub.source_task = asyncio.create_task(run_mock(hub), name="kvc-mock-source")

    async def wait_logger_commits(hub):
        if not hub.logger:
            return
        deadline = asyncio.get_running_loop().time() + settings.logger_flush_timeout_sec
        while True:
            status = hub.logger.status()
            if status["queue_depth"] == 0 and status["inflight"] == 0:
                return
            if asyncio.get_running_loop().time() >= deadline:
                raise RuntimeError("Logger did not reach a committed boundary before replay")
            await asyncio.sleep(0.01)

    def broadcast_live_reset(hub):
        hub.store = MissionStore(settings)
        snapshot = hub.store.snapshot(hub.diagnostics())
        payload = {key: snapshot[key] for key in (
            "telemetry", "target", "has_target", "hardware_link", "diagnostics",
            "alerts", "camera_position", "bounding_boxes", "replay_metadata",
        )}
        return hub.publish("SNAPSHOT", **payload)

    @asynccontextmanager
    async def lifespan(app):
        logger = None
        if settings.storage_dir is not None:
            logger = SQLiteLogger(settings.storage_dir, settings.logger_queue_capacity)
            await asyncio.to_thread(logger.start)
        hub = Hub(MissionStore(settings), logger)
        app.state.hub = hub
        app.state.logger = logger
        replay = None if settings.storage_dir is None else ReplayEngine(
            hub, settings.storage_dir, clock=replay_clock,
            sleeper=replay_sleeper, hardware=hardware,
        )
        app.state.replay = replay
        await start_mock_source(hub)
        try:
            yield
        finally:
            if replay:
                await replay.shutdown()
            await stop_mock_source(hub)
            for client in tuple(hub.clients):
                client.close_code = 1001
                client.stopped.set()
            if logger:
                await asyncio.to_thread(logger.stop, settings.logger_flush_timeout_sec)

    app = FastAPI(title="KVC MOCK GCS", lifespan=lifespan)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["http://127.0.0.1:5173", "http://localhost:5173"],
        allow_methods=["GET", "POST"], allow_headers=["Accept", "Content-Type"],
    )

    @app.get("/api/health")
    async def health():
        hub = app.state.hub
        replay = app.state.replay
        source_healthy = (
            (replay is not None and replay.active)
            or not settings.enable_mock
            or (hub.source_task is not None and not hub.source_task.done())
        )
        logger_healthy = hub.logger is None or hub.logger.status()["status"] == "OK"
        healthy = source_healthy and logger_healthy
        return {"status": "ok" if healthy else "degraded", "service": "kvc-gcs",
                "uptime_sec": hub.store.now_ms() / 1000, "source_mode": hub.store.source_mode}

    @app.get("/api/status")
    async def status():
        result = app.state.hub.status()
        result["replay"] = app.state.replay.status() if app.state.replay else {"active": False}
        return result

    @app.get("/api/state/snapshot")
    async def snapshot():
        hub = app.state.hub
        return hub.store.snapshot(hub.diagnostics())

    @app.get("/api/sessions")
    async def sessions():
        hub = app.state.hub
        return {
            "active_session_id": hub.store.session_id,
            "storage_implemented": hub.logger is not None,
            "sessions": hub.logger.sessions() if hub.logger else [],
        }

    @app.post("/api/sessions/new")
    async def new_session():
        hub = app.state.hub
        if app.state.replay and app.state.replay.active:
            raise HTTPException(status_code=409, detail="Stop replay before creating a live session")
        snapshot = hub.rotate_session()
        return {
            "status": "session_created",
            "new_session_id": snapshot["session_id"],
            "persistence": "PENDING" if hub.logger else "DISABLED",
        }

    def require_replay():
        if app.state.replay is None:
            raise HTTPException(status_code=409, detail="Storage is disabled")
        return app.state.replay

    @app.post("/api/replay/start")
    async def replay_start(request: ReplayStartRequest):
        hub = app.state.hub
        replay = require_replay()
        if replay.active:
            raise HTTPException(status_code=409, detail="Stop the active replay before starting another")
        await stop_mock_source(hub)
        try:
            await wait_logger_commits(hub)
            await replay.start(request.session_id, request.speed)
        except FileNotFoundError as exc:
            await start_mock_source(hub)
            raise HTTPException(status_code=404, detail=str(exc)) from exc
        except (ValueError, RuntimeError, sqlite3.Error) as exc:
            await start_mock_source(hub)
            raise HTTPException(status_code=409, detail=str(exc)) from exc
        return {"status": "replay_started", "replay": replay.status()}

    @app.post("/api/replay/pause")
    async def replay_pause():
        replay = require_replay()
        try:
            metadata = await replay.pause()
        except RuntimeError as exc:
            raise HTTPException(status_code=409, detail=str(exc)) from exc
        return {"status": "replay_paused", "replay": metadata}

    @app.post("/api/replay/resume")
    async def replay_resume():
        replay = require_replay()
        try:
            metadata = await replay.resume()
        except RuntimeError as exc:
            raise HTTPException(status_code=409, detail=str(exc)) from exc
        return {"status": "replay_resumed", "replay": metadata}

    @app.post("/api/replay/seek")
    async def replay_seek(request: ReplaySeekRequest):
        replay = require_replay()
        try:
            metadata = await replay.seek(request.timestamp_ms)
        except RuntimeError as exc:
            raise HTTPException(status_code=409, detail=str(exc)) from exc
        return {"status": "seek_ok", "replay": metadata}

    @app.post("/api/replay/speed")
    async def replay_speed(request: ReplaySpeedRequest):
        replay = require_replay()
        try:
            metadata = await replay.set_speed(request.speed)
        except (ValueError, RuntimeError) as exc:
            raise HTTPException(status_code=409, detail=str(exc)) from exc
        return {"status": "speed_ok", "replay": metadata}

    @app.post("/api/replay/stop")
    async def replay_stop():
        replay = require_replay()
        if not replay.active:
            raise HTTPException(status_code=409, detail="Replay is not active")
        await replay.stop()
        snapshot = broadcast_live_reset(app.state.hub)
        await start_mock_source(app.state.hub)
        return {
            "status": "replay_stopped",
            "source_mode": snapshot["source_mode"],
            "session_id": snapshot["session_id"],
        }

    @app.websocket("/ws/telemetry")
    async def telemetry(websocket: WebSocket):
        # Browser origins limited to the same loopback development origins.
        origin = websocket.headers.get("origin")
        if origin and origin not in {"http://127.0.0.1:5173", "http://localhost:5173"}:
            await websocket.close(code=1008)
            return
        await websocket.accept()
        hub = app.state.hub
        client = hub.subscribe()

        async def receive():
            # Read-only protocol: no application commands are accepted over WS.
            while True:
                message = await websocket.receive()
                if message["type"] == "websocket.disconnect":
                    return
                if message.get("text") is not None or message.get("bytes") is not None:
                    client.close_code = 1008
                    return

        tasks = [
            asyncio.create_task(send_events(websocket, client, hub), name="kvc-ws-sender"),
            asyncio.create_task(receive(), name="kvc-ws-receiver"),
            asyncio.create_task(client.stopped.wait(), name="kvc-ws-stop"),
        ]
        try:
            done, _ = await asyncio.wait(tasks, return_when=asyncio.FIRST_COMPLETED)
            for task in done:
                task.result()
        except (WebSocketDisconnect, RuntimeError, OSError, asyncio.CancelledError):
            pass
        finally:
            # ASGI/TestClient may cancel the connection scope during disconnect;
            # cleanup must still await all owned workers.
            with anyio.CancelScope(shield=True):
                for task in tasks:
                    task.cancel()
                await asyncio.gather(*tasks, return_exceptions=True)
                hub.clients.discard(client)
                try:
                    await asyncio.wait_for(websocket.close(code=client.close_code), settings.send_timeout_sec)
                except (WebSocketDisconnect, RuntimeError, OSError, TimeoutError):
                    pass

    return app


app = create_app()

if __name__ == "__main__":
    import uvicorn
    settings = Settings()
    uvicorn.run(app, host=settings.host, port=settings.port)

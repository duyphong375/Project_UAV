# KVC MOCK application backend

Tasks KVC-PRE-GCS-BACKEND-001, KVC-PRE-GCS-LOGGER-001 and KVC-PRE-GCS-REPLAY-001. Live acquisition in this slice is MOCK with inference SIMULATED. Replay reads committed application events and exposes them as source REPLAY while preserving `original_source_mode` and `inference_device`. HTTP/WS connectivity is independent of hardware status; hardware is UNKNOWN and no serial port is opened. Serial ingestion remains unimplemented. MOCK counters are application event counts (`mock_events_emitted`); USB packet/CRC counters remain zero.

From repository root (Windows PowerShell):

```powershell
python -m venv .venv
.venv/Scripts/python.exe -m pip install -r Dashboard/backend/requirements.txt
.venv/Scripts/python.exe -m Dashboard.backend.main
```

Default server: `127.0.0.1:8000`. Use one process/worker: application state and client queues are in memory; accepted records are durable only after the logger commit counter/ticket acknowledges them. Runtime databases default to `data/sessions/<session_id>.db`. The module does not start tasks during import; FastAPI lifespan owns the generator, SQLite writer and shutdown. CORS/browser WS origins allow only localhost/127.0.0.1 port 5173. This is a local development service, not a remotely exposed service.

Endpoints:

- GET `/api/health`: liveness, source and monotonic uptime.
- GET `/api/status`: hardware link, logger RAM/commit/drop/error counters, mock counters, queue depths/high-water and task state.
- GET `/api/state/snapshot`: full accumulated application snapshot with domain ages and all retained alerts.
- GET `/api/sessions`: active application session and committed SQLite session summaries.
- POST `/api/sessions/new`: rotate application state/session and enqueue its full snapshot; response persistence is `PENDING`, never a durable-success claim.
- POST `/api/replay/start`: body `{ "session_id": "SES-...", "speed": 0.5|1|2 }`; stop MOCK generation, open only that committed SQLite session read-only and broadcast a full REPLAY snapshot before patches.
- POST `/api/replay/pause` and `/api/replay/resume`: freeze/resume the application virtual clock. Resume is an application control, not a hardware command.
- POST `/api/replay/seek`: body `{ "timestamp_ms": 0 }`; clamp to the session duration, clear accumulated state and rebuild from the first record through the requested relative timestamp.
- POST `/api/replay/speed`: body `{ "speed": 0.5|1|2 }`; change application playback rate without discontinuity. It is not a hardware command.
- POST `/api/replay/stop`: cancel the replay task, broadcast a clean MOCK snapshot and restart the configured MOCK generator. Replay target/camera/alerts are not retained under a live label.
- WS `/ws/telemetry`: read-only JSON stream, full snapshot first, then event patches. Client commands are rejected with 1008.

Replay time is relative to the first committed `pc_rx_monotonic_ms` in the selected session. A paused replay position and its telemetry/target/camera ages do not advance with host wall time. Seek in either direction reconstructs state deterministically, so fields from records later than the seek point cannot survive. Replay uses a new `SES-REPLAY-*` application session; `source_session_id` identifies the recorded session. The logger path is disabled for replay publishes, therefore playback is not re-acquired or mislabeled as a new REAL/MOCK record. The injected hardware boundary is never invoked; tests assert zero open/read/write calls. These are host application properties, not hardware verification.

Each client has its own queue, at most 64 pending messages. Overflow or a send taking longer than 1 second closes only that client with 1008; discarded pending/new messages are counted and loss is latched. Reconnect after 2 seconds receives current state. A slow client's send is never awaited by broadcast or another client. Frame-local mock observations have no persistent track identity and are unconfirmed.

The logger has a separate bounded queue of at most 1024 records and one dedicated SQLite writer thread. `Hub.publish` uses only `put_nowait`; disk I/O never sits in the WS/ingress event loop. SQLite applies `journal_mode=WAL` and `synchronous=FULL` on each writer connection. `accepted_to_memory_total` counts successful RAM enqueue, while `committed_total` increments only after COMMIT. Queue overflow reports `LOG_DEGRADED`; open/write failures report `STORAGE_ERROR`; both increment `logger_drops_total` and latch data loss. Shutdown drains the queue within five seconds or reports remaining/in-flight work as drops.

Each record stores the application session, receive clocks, original source, validation outcome/reject reason and canonical parsed JSON. MOCK has no hardware byte capture, so `raw_envelope_hex` and `rf_payload_hex` remain SQL `NULL`. Rejected application events are logged without mutating mission state. The logger schema follows section 5.1 of `docs/gcs/KVC_GCS_DATA_CONTRACT.md`. Section 7 describes the current MOCK/logger/replay application implementation.

The generator repeats a 30-second scenario: person → lifebuoy → negative → invalid sensors → severity escalation → delayed data/stale → sensor recovery → new session. It does not synthesize camera coordinates or RF measurements. Status events continue during data silence and do not refresh telemetry/target age. A generated new session starts a new database file when its snapshot reaches the writer.

Frontend: set the public build-time setting `VITE_MOCK_TRANSPORT=BACKEND` while keeping source mode MOCK. `LOCAL` is the default and uses the existing in-browser generator. BACKEND never starts the local generator or falls back when the socket fails. Run Vite on port 5173. No local `.env` is written by this task; PowerShell example:

```powershell
$env:VITE_MOCK_TRANSPORT='BACKEND'
Set-Location Dashboard/frontend
npm run dev -- --host 127.0.0.1 --port 5173
```

Validation from repository root:

```powershell
.venv/Scripts/python.exe -B -m pytest Dashboard/backend/tests -q -p no:cacheprovider
.venv/Scripts/python.exe -B -m Dashboard.backend.tests.test_api_websocket
.venv/Scripts/python.exe -u -B -m Dashboard.backend.tests.test_api_websocket --soak
```

The last command runs 1800 seconds with real loopback TCP clients. The loopback harness disables durable storage; logger tests create databases only in pytest-managed temporary directories. Same-process RSS includes server, both clients and harness, providing a conservative combined memory figure. Thresholds are declared in the task before the run; stdout should be captured only under its review directory. Unit tests use injected clocks only for boundary semantics; the soak uses real monotonic time.

Application patch/null/session examples: `docs/gcs/KVC_GCS_DATA_CONTRACT.md` section 7; SQLite columns and PRAGMAs: section 5.1. The recovery test terminates only its known child PID after five commit ACKs and then reopens/integrity-checks that temporary database. This is host process-crash evidence, not proof against physical power loss. Serial/parser/hardware remain separate tasks. SOURCE-VERIFIED and SIMULATED/loopback evidence do not establish hardware verification.

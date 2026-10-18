"""ESP32-C3 WebSocket Ingress Client and 32-Byte RF Payload Parser.

Connects to the ESP32 Gateway at ws://192.168.4.1:8080/telemetry,
unpacks Little-Endian 32-byte RF telemetry, and injects events into Hub.
"""

import asyncio
import json
import logging
import struct
from typing import Any

import websockets

logger = logging.getLogger("kvc.esp32_ingress")


def parse_rf_payload(rf_payload_hex: str) -> dict[str, Any]:
    """Parse 64-char hex string (32 bytes Little-Endian) per IF_MCU_LORA_RF.md."""
    raw_bytes = bytes.fromhex(rf_payload_hex.strip())
    if len(raw_bytes) != 32:
        raise ValueError(f"Payload must be 32 bytes, got {len(raw_bytes)}")

    fmt = "<2sBBIIIhhHBBBB4sH"
    (
        sync, msg_id, seq_num, timestamp_ms,
        lat_scaled, lon_scaled,
        x_local_cm, y_local_cm,
        lidar_cm, class_id, confidence,
        sensor_flags, battery_raw, reserved, crc16,
    ) = struct.unpack(fmt, raw_bytes)

    gps_valid = bool(sensor_flags & 0x01)
    lidar_valid = bool(sensor_flags & 0x02)
    imu_valid = bool(sensor_flags & 0x04)
    ai_detected = bool(sensor_flags & 0x08)

    # Class mapping: 1 = person (người), 2 = boat (tàu thuyền)
    class_name = "person" if class_id == 1 else "boat" if class_id == 2 else "unknown"

    # Battery percentage calculation: 10.5V (0%) to 12.6V (100%), 0.1V/bit
    battery_v = battery_raw * 0.1
    battery_pct = int(min(100, max(0, (battery_v - 10.5) / (12.6 - 10.5) * 100)))

    has_target = ai_detected and (class_id in (1, 2))

    target_data = None
    if has_target:
        # Determine coordinate frame
        if gps_valid and lat_scaled != 0 and lon_scaled != 0:
            target_data = {
                "track_id": seq_num or 1,
                "class_id": class_id,
                "class_name": class_name,
                "confidence": min(100, max(0, confidence)),
                "target_confirmed": True,
                "pos_valid": True,
                "coordinate_frame": "WGS84",
                "latitude": lat_scaled / 1e7,
                "longitude": lon_scaled / 1e7,
                "local_x_cm": None,
                "local_y_cm": None,
                "origin_id": None,
            }
        else:
            target_data = {
                "track_id": seq_num or 1,
                "class_id": class_id,
                "class_name": class_name,
                "confidence": min(100, max(0, confidence)),
                "target_confirmed": True,
                "pos_valid": True,
                "coordinate_frame": "LOCAL_GRID",
                "latitude": None,
                "longitude": None,
                "local_x_cm": float(x_local_cm),
                "local_y_cm": float(y_local_cm),
                "origin_id": 1,
            }

    return {
        "sync_valid": sync == b"\xaa\x55",
        "msg_id": msg_id,
        "seq_num": seq_num,
        "device_measurement_time_ms": timestamp_ms,
        "telemetry": {
            "battery_pct": battery_pct,
            "lidar_range_cm": lidar_cm if (lidar_valid and 20 <= lidar_cm <= 800) else None,
            "gps_valid": gps_valid,
            "lidar_valid": lidar_valid,
            "imu_valid": imu_valid,
            "ai_detected": ai_detected,
        },
        "has_target": has_target,
        "target": target_data,
    }


def inject_envelope(hub: Any, data: dict[str, Any]) -> dict[str, Any]:
    """Inject a parsed envelope into the Hub."""
    hub.store.original_source_mode = "REAL"
    rf_hex = data.get("rf_payload_hex")
    if not rf_hex:
        raise ValueError("Missing rf_payload_hex field")

    parsed = parse_rf_payload(rf_hex)
    rssi = data.get("rssi_dbm")
    snr = data.get("snr_db")

    telem = parsed["telemetry"]
    if rssi is not None and -127 <= rssi <= 0:
        telem["packet_rssi_dbm"] = int(rssi)
    if snr is not None:
        telem["packet_snr_db"] = float(snr)

    hub.publish("LINK_STATUS", hardware_link={"status": "CONNECTED", "port": "ESP32_WIFI"})
    hub.publish("TELEMETRY_UPDATE", telemetry=telem)

    if parsed["has_target"]:
        hub.publish("TARGET_UPDATE", has_target=True, target=parsed["target"])
    else:
        hub.publish("TARGET_UPDATE", has_target=False, target=None)

    return parsed


async def probe_gateway_url(ip: str) -> str | None:
    """Probe an IP address for active KVC ESP32 Gateway WebSocket."""
    url = f"ws://{ip}:8080/telemetry"
    try:
        async with websockets.connect(url, open_timeout=0.35, close_timeout=0.35) as ws:
            msg = await asyncio.wait_for(ws.recv(), timeout=0.5)
            if "KVC_ESP32_GATEWAY" in msg or "transport_version" in msg:
                return url
    except Exception:
        return None
    return None


async def discover_esp32_gateway() -> str | None:
    """Auto-discover ESP32 Gateway WebSocket URL across common subnets."""
    # 1. First probe known static IPs
    for ip in ("192.168.1.175", "192.168.4.1", "192.168.1.15"):
        res = await probe_gateway_url(ip)
        if res:
            return res

    # 2. Fast parallel scan on 192.168.1.1-254
    tasks = [probe_gateway_url(f"192.168.1.{i}") for i in range(1, 255)]
    results = await asyncio.gather(*tasks, return_exceptions=True)
    for r in results:
        if isinstance(r, str) and r:
            return r
    return None


async def run_esp32_ingress(hub: Any, ws_url: str = "ws://192.168.1.175:8080/telemetry") -> None:
    """Async task connecting to ESP32 Gateway WebSocket with automatic reconnect and auto-discovery."""
    reconnect_delay = 2.0
    last_status = None
    current_url = ws_url
    fail_count = 0

    while True:
        try:
            logger.info("Connecting to ESP32 Gateway at %s...", current_url)
            async with websockets.connect(current_url, close_timeout=1.0) as ws:
                fail_count = 0
                last_status = "CONNECTED"
                hub.publish("LINK_STATUS", hardware_link={"status": "CONNECTED", "port": current_url})
                logger.info("Connected to ESP32 Gateway at %s.", current_url)

                # Đảm bảo nếu có mock source nào đang chạy ngầm thì hủy ngay lập tức
                if hasattr(hub, "source_task") and hub.source_task is not None:
                    hub.source_task.cancel()
                    hub.source_task = None

                async for message in ws:
                    try:
                        envelope = json.loads(message)
                        # Nếu nhận gói tin Handshake chào mừng từ ESP32 (không có rf_payload_hex)
                        if envelope.get("status") == "CONNECTED" and "rf_payload_hex" not in envelope:
                            logger.info("ESP32 Handshake received: %s", envelope)
                            hub.publish("LINK_STATUS", hardware_link={"status": "CONNECTED", "port": current_url})
                            continue

                        inject_envelope(hub, envelope)
                    except Exception as err:
                        logger.warning("Error processing packet from ESP32: %s", err)
        except (websockets.ConnectionClosed, OSError, TimeoutError) as exc:
            fail_count += 1
            # CHỈ publish LINK_STATUS khi trạng thái thực sự thay đổi sang DISCONNECTED (tránh spam packet mỗi 2 giây)
            if last_status != "DISCONNECTED":
                last_status = "DISCONNECTED"
                hub.publish("LINK_STATUS", hardware_link={"status": "DISCONNECTED", "port": current_url, "error_message": str(exc)})

            # Tự động dò tìm IP mới của ESP32 nếu kết nối cũ thất bại
            if fail_count >= 2:
                discovered = await discover_esp32_gateway()
                if discovered and discovered != current_url:
                    logger.info("ESP32 Gateway auto-discovered at %s! Updating target URL.", discovered)
                    current_url = discovered
                    fail_count = 0

            await asyncio.sleep(reconnect_delay)
        except asyncio.CancelledError:
            break


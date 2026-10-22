"""Tests for ESP32 ingress decoding and envelope injection."""

from fastapi.testclient import TestClient

from Dashboard.backend.config import Settings
from Dashboard.backend.esp32_ingress import parse_rf_payload
from Dashboard.backend.main import create_app


def test_parse_rf_payload_person():
    # Little-endian 32-byte payload:
    # Sync: aa 55, MsgID: 01, Seq: 2a (42), Monotonic: 1000 ms,
    # Lat: 107723450 (scaled), Lon: 1066578900 (scaled),
    # X: 150 cm, Y: 320 cm, LiDAR: 240 cm,
    # Class: 1 (person), Conf: 92%, Flags: 0x0f (GPS|LiDAR|IMU|AI), Battery: 126 (12.6V),
    # Reserved: 00 00 00 00, CRC16: 00 00
    import struct
    fmt = "<2sBBIIIhhHBBBB4sH"
    raw = struct.pack(
        fmt, b"\xaa\x55", 1, 42, 1000,
        107723450, 1066578900,
        150, 320, 240, 1, 92,
        0x0f, 126, b"\x00\x00\x00\x00", 0x1234,
    )
    hex_str = raw.hex()
    parsed = parse_rf_payload(hex_str)
    assert parsed["sync_valid"] is True
    assert parsed["seq_num"] == 42
    assert parsed["telemetry"]["battery_pct"] == 100
    assert parsed["telemetry"]["lidar_range_cm"] == 240
    assert parsed["has_target"] is True
    assert parsed["target"]["class_id"] == 1
    assert parsed["target"]["class_name"] == "person"
    assert abs(parsed["target"]["latitude"] - 10.772345) < 1e-5


def test_parse_rf_payload_boat():
    # Class 2 = boat (tàu thuyền)
    import struct
    fmt = "<2sBBIIIhhHBBBB4sH"
    raw = struct.pack(
        fmt, b"\xaa\x55", 1, 43, 2000,
        107723450, 1066578900,
        0, 0, 300, 2, 88,
        0x0f, 120, b"\x00\x00\x00\x00", 0x1234,
    )
    hex_str = raw.hex()
    parsed = parse_rf_payload(hex_str)
    assert parsed["target"]["class_id"] == 2
    assert parsed["target"]["class_name"] == "boat"


def test_parse_rf_payload_with_imu():
    # Roll = +15.2 deg (152), Pitch = -3.5 deg (-35) đóng gói trong 4 byte reserved
    import struct
    fmt = "<2sBBIIIhhHBBBB4sH"
    reserved = struct.pack("<hh", 152, -35)
    raw = struct.pack(
        fmt, b"\xaa\x55", 1, 44, 3000,
        107723450, 1066578900,
        0, 0, 300, 1, 95,
        0x04, 126, reserved, 0x1234,
    )
    parsed = parse_rf_payload(raw.hex())
    assert parsed["telemetry"]["imu_valid"] is True
    assert parsed["imu"] is not None
    assert parsed["imu"]["roll_deg"] == 15.2
    assert parsed["imu"]["pitch_deg"] == -3.5


def test_http_ingress_envelope_api():
    app = create_app(Settings(storage_dir=None, enable_mock=False))
    client = TestClient(app)
    with client:
        import struct
        fmt = "<2sBBIIIhhHBBBB4sH"
        raw = struct.pack(
            fmt, b"\xaa\x55", 1, 1, 100,
            0, 0, 100, 200, 250, 2, 90,
            0x0e, 122, b"\x00\x00\x00\x00", 0x0000,
        )
        res = client.post("/api/ingress/envelope", json={
            "rf_payload_hex": raw.hex(),
            "rssi_dbm": -65,
            "snr_db": 9.0,
        })
        assert res.status_code == 200
        snap = client.get("/api/state/snapshot").json()
        assert snap["hardware_link"]["status"] == "CONNECTED"
        assert snap["has_target"] is True
        assert snap["target"]["class_name"] == "boat"
        assert snap["telemetry"]["packet_rssi_dbm"] == -65


def test_session_inactivity_auto_close():
    import struct
    import asyncio
    app = create_app(Settings(storage_dir=None, enable_mock=False))
    client = TestClient(app)
    with client:
        hub = app.state.hub
        fmt = "<2sBBIIIhhHBBBB4sH"
        raw = struct.pack(
            fmt, b"\xaa\x55", 1, 1, 100,
            0, 0, 100, 200, 250, 1, 90,
            0x0e, 122, b"\x00\x00\x00\x00", 0x0000,
        )
        res = client.post("/api/ingress/envelope", json={
            "rf_payload_hex": raw.hex(),
            "rssi_dbm": -65,
            "snr_db": 9.0,
        })
        assert res.status_code == 200
        old_session = hub.store.session_id
        assert hub.store.original_source_mode == "REAL"
        assert hub.store.times["rx"] is not None

        # Simulate 61 seconds elapsed on times["rx"]
        hub.store.times["rx"] -= 61000

        # Trigger check_session_inactivity
        check_fn = app.state.check_session_inactivity
        rotated = asyncio.run(check_fn(hub, timeout_sec=60.0))
        assert rotated is True
        new_session = hub.store.session_id
        assert new_session != old_session
        assert hub.store.times["rx"] is None
        assert "SESSION_AUTO_CLOSED" in hub.store.alerts


def test_phase3_self_mock_scenarios():
    """Verify all 3 Phase 3 Self-Mock telemetry scenarios from ESP32."""
    import struct
    fmt = "<2sBBIIIhhHBBBB4sH"

    # Scenario 0: Person WGS-84 (Đà Nẵng)
    raw_person = struct.pack(
        fmt, b"\xaa\x55", 1, 1, 1000,
        160738520, 1081499210,
        0, 0, 250, 1, 95,
        0x0F, 125, b"\x00\x00\x00\x00", 0x0000,
    )
    p0 = parse_rf_payload(raw_person.hex())
    assert p0["sync_valid"] is True
    assert p0["has_target"] is True
    assert p0["target"]["coordinate_frame"] == "WGS84"
    assert p0["target"]["class_name"] == "person"
    assert p0["target"]["confidence"] == 95
    assert abs(p0["target"]["latitude"] - 16.073852) < 1e-6
    assert abs(p0["target"]["longitude"] - 108.149921) < 1e-6
    assert p0["telemetry"]["lidar_range_cm"] == 250
    assert p0["telemetry"]["battery_pct"] == 95  # (12.5 - 10.5) / 2.1 * 100 = 95%

    # Scenario 1: Boat WGS-84 (Đà Nẵng)
    raw_boat = struct.pack(
        fmt, b"\xaa\x55", 1, 2, 2000,
        160751000, 1081512000,
        0, 0, 230, 2, 92,
        0x0F, 124, b"\x00\x00\x00\x00", 0x0000,
    )
    p1 = parse_rf_payload(raw_boat.hex())
    assert p1["has_target"] is True
    assert p1["target"]["coordinate_frame"] == "WGS84"
    assert p1["target"]["class_name"] == "boat"
    assert p1["target"]["confidence"] == 92
    assert abs(p1["target"]["latitude"] - 16.075100) < 1e-6
    assert abs(p1["target"]["longitude"] - 108.151200) < 1e-6
    assert p1["telemetry"]["lidar_range_cm"] == 230

    # Scenario 2: Local Grid (Sa bàn thực nghiệm)
    raw_local = struct.pack(
        fmt, b"\xaa\x55", 1, 3, 3000,
        0, 0,
        150, 320, 245, 1, 89,
        0x0E, 123, b"\x00\x00\x00\x00", 0x0000,
    )
    p2 = parse_rf_payload(raw_local.hex())
    assert p2["has_target"] is True
    assert p2["target"]["coordinate_frame"] == "LOCAL_GRID"
    assert p2["target"]["class_name"] == "person"
    assert p2["target"]["confidence"] == 89
    assert p2["target"]["local_x_cm"] == 150.0
    assert p2["target"]["local_y_cm"] == 320.0
    assert p2["telemetry"]["lidar_range_cm"] == 245
    assert p2["telemetry"]["gps_valid"] is False
    assert p2["telemetry"]["lidar_valid"] is True



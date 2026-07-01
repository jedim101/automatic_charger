"""Decode Tesla fleet telemetry websocket messages."""

from __future__ import annotations

import struct
from datetime import datetime, timezone
from typing import Any

import vehicle_data_pb2

MESSAGE_FLATBUFFERS_STREAM = 4
MESSAGE_FLATBUFFERS_STREAM_ACK = 5


def _u32(buf: bytes, pos: int) -> int:
    return struct.unpack_from("<I", buf, pos)[0]


def _i32(buf: bytes, pos: int) -> int:
    return struct.unpack_from("<i", buf, pos)[0]


def _u16(buf: bytes, pos: int) -> int:
    return struct.unpack_from("<H", buf, pos)[0]


def _vtable_field(buf: bytes, table_pos: int, field_idx: int) -> int:
    vtable = table_pos - _i32(buf, table_pos)
    return _u16(buf, vtable + 4 + field_idx * 2)


def _read_vector(buf: bytes, table_pos: int, field_idx: int) -> bytes | None:
    off = _vtable_field(buf, table_pos, field_idx)
    if off == 0:
        return None
    field_pos = table_pos + off
    rel = _u32(buf, field_pos)
    vec_len_pos = field_pos + rel
    length = _u32(buf, vec_len_pos)
    start = vec_len_pos + 4
    return buf[start : start + length]


def _read_subtable(buf: bytes, table_pos: int, field_idx: int) -> int | None:
    off = _vtable_field(buf, table_pos, field_idx)
    if off == 0:
        return None
    rel = _u32(buf, table_pos + off)
    return table_pos + off + rel


def _read_byte(buf: bytes, table_pos: int, field_idx: int) -> int | None:
    off = _vtable_field(buf, table_pos, field_idx)
    if off == 0:
        return None
    return buf[table_pos + off]


def unwrap_stream_message(data: bytes) -> dict[str, Any]:
    """Extract metadata and protobuf bytes from a FlatBuffers websocket frame."""
    if isinstance(data, str):
        data = data.encode("latin-1")

    root = _u32(data, 0)
    topic = _read_vector(data, root, 1)
    txid = _read_vector(data, root, 0)
    message_type = _read_byte(data, root, 2)
    message_id = _read_vector(data, root, 4)
    stream = _read_subtable(data, root, 3)

    if message_type == MESSAGE_FLATBUFFERS_STREAM_ACK:
        return {
            "kind": "ack",
            "topic": topic.decode() if topic else None,
            "txid": txid.decode() if txid else None,
            "message_id": message_id.decode() if message_id else None,
        }

    if message_type != MESSAGE_FLATBUFFERS_STREAM:
        raise ValueError(f"unsupported flatbuffer message type: {message_type}")

    if stream is None:
        raise ValueError("stream message missing payload table")

    protobuf_bytes = _read_vector(data, stream, 2)
    if not protobuf_bytes:
        raise ValueError("stream message missing protobuf payload")

    return {
        "kind": "stream",
        "topic": topic.decode() if topic else None,
        "txid": txid.decode() if txid else None,
        "message_id": message_id.decode() if message_id else None,
        "sender_id": (_read_vector(data, stream, 1) or b"").decode(),
        "device_type": (_read_vector(data, stream, 3) or b"").decode(),
        "device_id": (_read_vector(data, stream, 4) or b"").decode(),
        "protobuf_bytes": protobuf_bytes,
    }


def decode_value(value: vehicle_data_pb2.Value) -> Any:
    which = value.WhichOneof("value")
    if which is None:
        return None

    raw = getattr(value, which)

    if which in {"string_value"}:
        return raw
    if which in {"int_value", "long_value", "float_value", "double_value", "boolean_value", "invalid"}:
        return raw
    if which == "location_value":
        return {"latitude": raw.latitude, "longitude": raw.longitude}
    if which == "door_value":
        return {
            "DriverFront": raw.DriverFront,
            "DriverRear": raw.DriverRear,
            "PassengerFront": raw.PassengerFront,
            "PassengerRear": raw.PassengerRear,
            "TrunkFront": raw.TrunkFront,
            "TrunkRear": raw.TrunkRear,
        }
    if which == "tire_location_value":
        return {
            "front_left": raw.front_left,
            "front_right": raw.front_right,
            "rear_left": raw.rear_left,
            "rear_right": raw.rear_right,
        }
    if which == "time_value":
        return {"hour": raw.hour, "minute": raw.minute, "second": raw.second}
    if which.endswith("_value") and hasattr(raw, "Name"):
        return raw.Name(raw)

    return raw


def decode_payload(protobuf_bytes: bytes) -> dict[str, Any]:
    payload = vehicle_data_pb2.Payload()
    payload.ParseFromString(protobuf_bytes)

    created_at = None
    if payload.HasField("created_at"):
        created_at = payload.created_at.ToDatetime(timezone.utc).isoformat()

    fields: dict[str, Any] = {}
    for datum in payload.data:
        field_name = vehicle_data_pb2.Field.Name(datum.key)
        fields[field_name] = decode_value(datum.value)

    return {
        "vin": payload.vin or None,
        "created_at": created_at,
        "is_resend": payload.is_resend,
        "fields": fields,
    }


def decode_telemetry_message(data: bytes) -> dict[str, Any]:
    """Decode a websocket frame into metadata plus vehicle_data.Payload fields."""
    frame = unwrap_stream_message(data)
    if frame["kind"] == "ack":
        return frame

    decoded = decode_payload(frame.pop("protobuf_bytes"))
    frame.update(decoded)
    return frame

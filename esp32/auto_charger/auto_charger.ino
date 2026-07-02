#include <WiFi.h>
#include <AsyncTCP.h>
#include <ESPAsyncWebServer.h>
#include "pb.h"
#include "pb_decode.h"
#include "vehicle_min.pb.h"

const char* ssid = "CrazyTown";
const char* password = "REDACTED";

AsyncWebServer server(80);
AsyncWebSocket ws("/");

static uint16_t fbVtableOffset(const uint8_t *buf, uint32_t table) {
    int32_t rel;
    memcpy(&rel, buf + table, 4);
    return table - rel;
}

static uint16_t fbFieldOffset(const uint8_t *buf, uint16_t vtable, int fieldIndex) {
    uint16_t offset;
    memcpy(&offset, buf + vtable + 4 + fieldIndex * 2, 2);
    return offset;
}

static bool fbReadVector(
    const uint8_t *buf,
    size_t len,
    uint32_t table,
    int fieldIndex,
    const uint8_t **out,
    size_t *outLen)
{
    if (table >= len) {
        return false;
    }

    uint16_t vtable = fbVtableOffset(buf, table);
    if (vtable + 4 > len) {
        return false;
    }

    uint16_t fieldOff = fbFieldOffset(buf, vtable, fieldIndex);
    if (fieldOff == 0) {
        return false;
    }

    uint32_t slot = table + fieldOff;
    if (slot + 4 > len) {
        return false;
    }

    uint32_t rel;
    memcpy(&rel, buf + slot, 4);
    uint32_t vec = slot + rel;
    if (vec + 4 > len) {
        return false;
    }

    uint32_t n;
    memcpy(&n, buf + vec, 4);
    if (n == 0 || vec + 4 + n > len) {
        return false;
    }

    *out = buf + vec + 4;
    *outLen = n;
    return true;
}

// Tesla fleet-telemetry wraps protobuf in a FlatBuffers envelope.
static bool extractTeslaPayload(const uint8_t *data, size_t len, const uint8_t **payload, size_t *payloadLen) {
    if (len < 8) {
        return false;
    }

    uint32_t root;
    memcpy(&root, data, 4);
    if (root >= len) {
        return false;
    }

    // Search for FlatbuffersStream.payload (field index 2) within the envelope.
    for (uint32_t table = root; table + 16 < len; table++) {
        const uint8_t *vec = nullptr;
        size_t vecLen = 0;
        if (!fbReadVector(data, len, table, 2, &vec, &vecLen)) {
            continue;
        }

        if (vecLen >= 2 && vec[0] == 0x0A) {
            *payload = vec;
            *payloadLen = vecLen;
            return true;
        }
    }

    return false;
}

extern "C" bool decodeDatumCallback(pb_istream_t *stream, const pb_field_t *field, void **arg);

bool decodeTelemetry(uint8_t *data, size_t len) {
    const uint8_t *payload = nullptr;
    size_t payloadLen = 0;
    if (!extractTeslaPayload(data, len, &payload, &payloadLen)) {
        Serial.println("FlatBuffers extract failed. Raw:");
        for (size_t i = 0; i < len; ++i) {
            Serial.printf("%02X ", data[i]);
        }
        Serial.println();
        return false;
    }

    pb_istream_t stream = pb_istream_from_buffer(payload, payloadLen);

    telemetry_vehicle_data_Payload msg = telemetry_vehicle_data_Payload_init_zero;
    msg.data.funcs.decode = decodeDatumCallback;

    if (!pb_decode(&stream, telemetry_vehicle_data_Payload_fields, &msg)) {
        Serial.println("Protobuf decode failed. Payload:");
        for (size_t i = 0; i < payloadLen; ++i) {
            Serial.printf("%02X ", payload[i]);
        }
        Serial.println();
        return false;
    }

    return true;
}

extern "C" bool decodeDatumCallback(pb_istream_t *stream, const pb_field_t *field, void **arg) {
    telemetry_vehicle_data_Datum datum = telemetry_vehicle_data_Datum_init_zero;

    if (!pb_decode(stream, telemetry_vehicle_data_Datum_fields, &datum)) {
        return false;
    }

    if (datum.has_value &&
        datum.key == telemetry_vehicle_data_Field_ChargePortDoorOpen &&
        datum.value.which_value == telemetry_vehicle_data_Value_boolean_value_tag) {
        bool open = datum.value.value.boolean_value;

        Serial.print("Charge port open: ");
        Serial.println(open ? "YES" : "NO");
    }

    return true;
}

void onWsEvent(
    AsyncWebSocket *server,
    AsyncWebSocketClient *client,
    AwsEventType type,
    void *arg,
    uint8_t *data,
    size_t len)
{
    if (type == WS_EVT_CONNECT) {
        Serial.printf("Client %u connected\n", client->id());
        return;
    }

    if (type == WS_EVT_DISCONNECT) {
        Serial.printf("Client %u disconnected\n", client->id());
        return;
    }

    if (type == WS_EVT_DATA) {
    AwsFrameInfo *info = (AwsFrameInfo*)arg;

    if (info->final && info->index == 0 && info->len == len) {
        decodeTelemetry(data, len);
    }
}
}

void setup() {
    Serial.begin(115200);

    WiFi.begin(ssid, password);
    Serial.print("Connecting");

    while (WiFi.status() != WL_CONNECTED) {
        delay(500);
        Serial.print(".");
    }

    Serial.println();
    Serial.print("IP: ");
    Serial.println(WiFi.localIP());

    ws.onEvent(onWsEvent);
    server.addHandler(&ws);

    server.begin();

    Serial.println("WebSocket server ready at /");
}

void loop() {}
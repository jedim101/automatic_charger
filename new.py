from cgitb import reset
import json
import requests, os
from dotenv import load_dotenv

load_dotenv()
ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")

vehicle_id = "2533993839388942"


# tokens = requests.post("https://fleet-auth.prd.vn.cloud.tesla.com/oauth2/v3/token", data={
#     # "grant_type": "refresh_token",
#     "grant_type": "client_credentials",
#     "scope": "openid vehicle_device_data",
#     "audience": "https://fleet-api.prd.na.vn.cloud.tesla.com",
#     "client_id": os.getenv("CLIENT_ID"),
#     "client_secret": os.getenv("CLIENT_SECRET"),
#     # "refresh_token": os.getenv("REFRESH_TOKEN")
# }
# ).json()

# tokens = requests.post("https://fleet-auth.prd.vn.cloud.tesla.com/oauth2/v3/token", data={
#     "grant_type": "refresh_token",
#     # "grant_type": "client_credentials",
#     # "scope": "openid vehicle_device_data",
#     # "audience": "https://fleet-api.prd.na.vn.cloud.tesla.com",
#     "client_id": os.getenv("CLIENT_ID"),
#     "client_secret": os.getenv("CLIENT_SECRET"),
#     "refresh_token": os.getenv("REFRESH_TOKEN")
# }
# ).json()


# print(tokens['access_token'])

# response = requests.post(
#     f"https://fleet-api.prd.na.vn.cloud.tesla.com/api/1/partner_accounts",
#     headers={"Authorization": f"Bearer {tokens['access_token']}", "Content-Type": "application/json"},
#     data={
#       "domain": "api.matthewglasser.org",
#     }
# )

# print(response.status_code, response.text)

vin = "7SAYGDED6TF615582"

payload = {
  "vins": [vin],
  "config": {
    "hostname": "api.matthewglasser.org",
    "port": 443,
    "ca": "-----BEGIN CERTIFICATE-----\nMIIDkDCCAzagAwIBAgIRAPJopT12WitaDh6mYOcncC4wCgYIKoZIzj0EAwIwOzELMAkGA1UEBhMCVVMxHjAcBgNVBAoTFUdvb2dsZSBUcnVzdCBTZXJ2aWNlczEMMAoGA1UEAxMDV0UxMB4XDTI2MDYyOTE2NTMxMVoXDTI2MDkyNzE3NDc1OFowHTEbMBkGA1UEAxMSbWF0dGhld2dsYXNzZXIub3JnMFkwEwYHKoZIzj0CAQYIKoZIzj0DAQcDQgAETWxyuTNyZj0q1b2Hln54syQd2NjZERFzEjyFj6Y7Cg1YOaLj2IWrVTykjDoIFuA6a/Glc7hysG1kgZVxDqIBx6OCAjcwggIzMA4GA1UdDwEB/wQEAwIHgDATBgNVHSUEDDAKBggrBgEFBQcDATAMBgNVHRMBAf8EAjAAMB0GA1UdDgQWBBRXLQDgqyu+OOX1cxZhpNN2t+XfyTAfBgNVHSMEGDAWgBSQd5I1Z8T/qMyp5nvZgHl7zJP5ODA1BggrBgEFBQcBAQQpMCcwJQYIKwYBBQUHMAKGGWh0dHA6Ly9pLnBraS5nb29nL3dlMS5jcnQwMwYDVR0RBCwwKoISbWF0dGhld2dsYXNzZXIub3JnghQqLm1hdHRoZXdnbGFzc2VyLm9yZzATBgNVHSAEDDAKMAgGBmeBDAECATA2BgNVHR8ELzAtMCugKaAnhiVodHRwOi8vYy5wa2kuZ29vZy93ZTEvdVRPcGVxdkZCbVkuY3JsMIIBAwYKKwYBBAHWeQIEAgSB9ASB8QDvAHYA2AlVO5RPev/IFhlvlE+Fq7D4/F6HVSYPFdEucrtFSxQAAAGfFIOGBwAABAMARzBFAiADbqF+zBPy7AaDEA+2IpJpfzqCUaz9x11f35dKkoERZgIhANNVeoEM57/UTWBgcKCSuEvfNJz0uqT37jAXZk/MlIP9AHUAr2eIO1ewTt2Pptl+9i6o64EKx3Fg8CReVdYML+eFhzoAAAGfFIOGtQAABAMARjBEAiAgLzzf/FaP3ne3ZuVQDqI+6H4p0F5yERzbCOc4k4tENwIgUi0nSfljCUDDt6lSdRg8I7cTPxZAhR8KCJhwITwOsFgwCgYIKoZIzj0EAwIDSAAwRQIgdSTIL2r7FAsoica98rSswXi+T99Mg1PmwRx2b9TuCsYCIQDRBRseVsGybgwD00BA3ogY1ez8JjMWZkU8W/ynJ50umA==\n-----END CERTIFICATE-----",
    "fields": {
      "ChargePortDoorOpen": { "interval_seconds": 1 },
    },
  }
}

# print(json.dumps(payload, indent=2))

# response = requests.post(
#     f"https://localhost:4443/api/1/vehicles/fleet_telemetry_config",
#     headers={"Authorization": f"Bearer {ACCESS_TOKEN}"},
#     json=payload,
#     verify=False,
#     timeout=30
# )

# print()

# print(response.status_code, response.text)




response = requests.get(
    f"https://localhost:4443/api/1/vehicles/{vin}/fleet_telemetry_errors",
    headers={"Authorization": f"Bearer {ACCESS_TOKEN}"},
    verify=False, 
    timeout=30
)

print()

print(response.status_code, response.json())
import requests, os
from dotenv import load_dotenv

load_dotenv()
ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")

vehicle_id = "2533993839388942"

tokens = requests.post("https://fleet-auth.prd.vn.cloud.tesla.com/oauth2/v3/token", data={
    "grant_type": "refresh_token",
    "client_id": os.getenv("CLIENT_ID"),
    "client_secret": os.getenv("CLIENT_SECRET"),
    "refresh_token": os.getenv("REFRESH_TOKEN")
}).json()


# print(tokens['access_token'])


url = f"https://localhost:4443/api/1/vehicles/fleet_telemetry_config"

response = requests.post(
    url,
    headers={"Authorization": f"Bearer {tokens['access_token']}"},
    json={
        "host": "api.matthewglasser.org",
        "ca": open("../vehicle-command/config/tls-cert.pem").read(),
        "public_key": open("../vehicle-command/config/public_key.pem").read(),
        "enable": True
    },
    verify=False
)

print(response.status_code, response.text)

print(response.status_code)
print(response.text)
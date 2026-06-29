import requests, os
from dotenv import load_dotenv

load_dotenv()
ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")

tokens = requests.post("https://fleet-auth.prd.vn.cloud.tesla.com/oauth2/v3/token", data={
    "grant_type": "refresh_token",
    "client_id": os.getenv("CLIENT_ID"),
    "client_secret": os.getenv("CLIENT_SECRET"),
    "refresh_token": os.getenv("REFRESH_TOKEN")
}).json()

print(tokens['access_token'])

response = requests.get(
  f"https://fleet-api.prd.na.vn.cloud.tesla.com/api/1/vehicles",
  headers={"Authorization": f"Bearer {tokens['access_token']}"}
)

print(response.json())
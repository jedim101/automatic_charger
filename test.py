import requests, urllib.parse, time, os
# from state import STATE

from dotenv import load_dotenv
load_dotenv()

CLIENT_ID = os.getenv("CLIENT_ID")

REDIRECT_URI = "https://api.matthewglasser.org/auth/callback"
SCOPES = "openid offline_access vehicle_device_data vehicle_cmds vehicle_charging_cmds"

class TeslaAPI:
  def __init__(self, client_id, client_secret, redirect_uri, scopes):
    self.client_id = client_id
    self.client_secret = client_secret
    self.redirect_uri = redirect_uri
    self.scopes = scopes
    self.tokens = {}
    # self.state = STATE

  def valid(self):
    return self.tokens and (int(time.time()) - self.tokens["obtained_at"] < self.tokens["expires_in"] - 60)

  def refresh(self):
    r = requests.post("https://fleet-auth.prd.vn.cloud.tesla.com/oauth2/v3/token", data={
      "grant_type": "refresh_token",
      "client_id": self.client_id,
      "client_secret": self.client_secret,
      "refresh_token": self.tokens["refresh_token"]
    }).json()
    r["obtained_at"] = int(time.time())
    self.tokens.update(r)

  def api_get(self, path):
    if not self.valid():
      self.refresh()
    return requests.get(
      f"https://fleet-api.prd.na.vn.cloud.tesla.com{path}",
      headers={"Authorization": f"Bearer {self.tokens['access_token']}"}
    )

  def api_post(self, path):
    if not self.valid():
      self.refresh()
    return requests.post(
      f"https://fleet-api.prd.na.vn.cloud.tesla.com{path}",
      headers={"Authorization": f"Bearer {self.tokens['access_token']}"}
    )

  def get_vehicles(self):
    resp = self.api_get("/api/1/vehicles")
    try:
      return resp.json().get('response', [])
    except Exception:
      return []

  def get_vehicle_state(self, vid):
    vehicles = self.get_vehicles()
    vehicle = next((v for v in vehicles if str(v.get('id')) == str(vid)), None)
    return vehicle.get('state') if vehicle else None

  def wake_up_vehicle(self, vid):
    return self.api_post(f"/api/1/vehicles/{vid}/wake_up")

  def get_vehicle_data(self, vid):
    return self.api_get(f"/api/1/vehicles/{vid}/vehicle_data")

tesla_api = TeslaAPI(CLIENT_ID, os.getenv("CLIENT_SECRET"), REDIRECT_URI, SCOPES)

if not tesla_api.tokens:
  url = "https://fleet-auth.prd.vn.cloud.tesla.com/oauth2/v3/authorize?" + urllib.parse.urlencode({
    "client_id": CLIENT_ID,
    "redirect_uri": REDIRECT_URI,
    "response_type": "code",
    "scope": SCOPES,
    # "state": tesla_api.state
  })
  print(url)

else:
  print(tesla_api.get_vehicles())
import base64, hashlib, os, urllib.parse

client_id = "fa39ff19-2dea-4335-8e3a-40b50e2cf483"
redirect_uri = "http://localhost:3000/callback"

# 1. Generate verifier
code_verifier = base64.urlsafe_b64encode(os.urandom(64)).rstrip(b'=').decode('utf-8')

# 2. Generate challenge
code_challenge = base64.urlsafe_b64encode(
    hashlib.sha256(code_verifier.encode()).digest()
).rstrip(b'=').decode('utf-8')

auth_url = (
    "https://auth.tesla.com/oauth2/v3/authorize?"
    + urllib.parse.urlencode({
        "client_id": client_id,
        "redirect_uri": redirect_uri,
        "response_type": "code",
        "scope": "openid offline_access vehicle_device_data vehicle_location vehicle_cmds",
        "code_challenge": code_challenge,
        "code_challenge_method": "S256"
    })
)

print(client_id)
print(auth_url)
print(code_verifier)
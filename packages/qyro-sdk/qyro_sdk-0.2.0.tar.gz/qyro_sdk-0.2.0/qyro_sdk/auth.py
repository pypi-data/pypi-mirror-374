import json
import time
import uuid
import jwt
from typing import Dict


class ApiKeyAuth:
    def __init__(self, api_key_id: str, api_key_secret: str):
        self.api_key_id = api_key_id
        self.api_key_secret = api_key_secret

    def header_value(self) -> str:
        return f"ApiKey {self.api_key_secret}"


class ClientTokenGenerator:
    def __init__(self, api_key_id: str, api_key_secret: str):
        self.api_key_id = api_key_id
        self.api_key_secret = api_key_secret

    def generate(self, context: Dict) -> str:
        subject = json.dumps(context)
        now_ts = int(time.time())
        payload = {
            "sub": subject,
            "iat": now_ts,
            "exp": now_ts + 24 * 30 * 3600,
            "type": "client",
            "iss": str(self.api_key_id),
            "aud": "qyro",
            "jti": str(uuid.uuid4()),
        }
        headers = {"kid": str(self.api_key_id)}
        token = jwt.encode(payload, key=self.api_key_secret, algorithm="HS256", headers=headers)
        return token

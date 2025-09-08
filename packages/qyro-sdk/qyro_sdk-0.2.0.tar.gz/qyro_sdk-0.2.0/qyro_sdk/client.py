import requests
from typing import Any, Dict, Optional

from qyro_sdk.exceptions import HTTPError, ConfigurationError
from qyro_sdk.models import Session, Message


class QyroClient:
    def __init__(self, base_url: str, token: str, timeout: Optional[float] = 30.0):
        if not base_url:
            raise ConfigurationError("base_url is required")
        self.base_url = base_url.rstrip("/")
        self.token = token
        self.timeout = timeout

    def _url(self, path: str) -> str:
        return f"{self.base_url}{path}"

    @staticmethod
    def _raise_for_status(resp: requests.Response):
        if not resp.ok:
            try:
                data = resp.json()
                msg = data.get("message") or data
            except Exception:
                msg = resp.text
            raise HTTPError(resp.status_code, msg, response=resp)

    def _client_headers(self) -> Dict[str, str]:
        return {"Authorization": f"Bearer {self.token}", "Content-Type": "application/json"}

    def create_session(self, assistant_id: str, context: Dict[str, Any]) -> Session:
        path = f"/client/api/v1/assistants/{assistant_id}/sessions"
        headers = self._client_headers()
        payload = {"context": context}
        resp = requests.post(self._url(path), json=payload, headers=headers, timeout=self.timeout)
        self._raise_for_status(resp)
        response = resp.json()
        return Session(id=response["id"])

    def fetch_session_messages(self, assistant_id: str, session_id: str) -> list[Message]:
        path = f"/client/api/v1/assistants/{assistant_id}/sessions/{session_id}/messages"
        headers = self._client_headers()
        resp = requests.get(self._url(path), headers=headers, timeout=self.timeout)
        self._raise_for_status(resp)
        messages = resp.json()
        result = []
        for m in messages:
            result.append(Message(id=m["id"], content=m["content"], role=m["role"]))
        return result

    def chat(self, assistant_id: str, session_id: str, message: str) -> list[Message]:
        path = f"/client/api/v1/assistants/{assistant_id}/sessions/{session_id}/chat"
        headers = self._client_headers()
        resp = requests.post(self._url(path), json={"message": message}, headers=headers, timeout=self.timeout)
        self._raise_for_status(resp)
        messages = resp.json()
        result = []
        for m in messages:
            result.append(Message(id=m["id"], content=m["content"], role=m["role"]))
        return result

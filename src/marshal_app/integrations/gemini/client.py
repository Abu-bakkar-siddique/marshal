from __future__ import annotations

import json
import os
from dataclasses import dataclass
from typing import Any
from urllib import error, request


@dataclass(slots=True, frozen=True)
class GeminiCompletion:
    text: str
    model: str | None = None


class GeminiClient:
    """Small REST client for the Gemini API."""

    def __init__(
        self,
        api_key: str,
        *,
        model: str = "gemini-2.5-flash",
        timeout: float = 60.0,
        base_url: str = "https://generativelanguage.googleapis.com/v1beta",
    ) -> None:
        self._api_key = api_key.strip()
        self._model = model.strip()
        self._timeout = timeout
        self._base_url = base_url.rstrip("/")

    @classmethod
    def from_env(cls) -> "GeminiClient | None":
        api_key = (
            os.environ.get("GEMINI_API_KEY")
            or os.environ.get("GOOGLE_API_KEY")
            or os.environ.get("MARSHAL_GEMINI_API_KEY")
        )
        if not api_key:
            return None
        model = (
            os.environ.get("MARSHAL_GEMINI_MODEL")
            or os.environ.get("GEMINI_MODEL")
            or "gemini-2.5-flash"
        )
        return cls(api_key, model=model)

    def is_configured(self) -> bool:
        return bool(self._api_key)

    def generate_json(
        self,
        *,
        system_instruction: str,
        user_input: str,
        schema_name: str,
        schema: dict[str, Any],
    ) -> dict[str, Any]:
        payload = {
            "systemInstruction": {
                "parts": [{"text": system_instruction}],
            },
            "contents": [
                {
                    "role": "user",
                    "parts": [{"text": user_input}],
                }
            ],
            "generationConfig": {
                "responseMimeType": "application/json",
                "responseJsonSchema": schema,
                "temperature": 0.2,
            },
        }
        response = self._post(f"/models/{self._model}:generateContent", payload)
        text = self._extract_text(response)
        if not text:
            raise RuntimeError("Gemini returned an empty planning response")
        return json.loads(text)

    def generate_text(self, *, system_instruction: str, user_input: str) -> GeminiCompletion:
        payload = {
            "systemInstruction": {
                "parts": [{"text": system_instruction}],
            },
            "contents": [
                {
                    "role": "user",
                    "parts": [{"text": user_input}],
                }
            ],
        }
        response = self._post(f"/models/{self._model}:generateContent", payload)
        return GeminiCompletion(text=self._extract_text(response), model=self._model)

    def _post(self, path: str, payload: dict[str, Any]) -> dict[str, Any]:
        body = json.dumps(payload).encode("utf-8")
        req = request.Request(
            url=f"{self._base_url}{path}",
            data=body,
            headers={
                "x-goog-api-key": self._api_key,
                "Content-Type": "application/json",
            },
            method="POST",
        )

        try:
            with request.urlopen(req, timeout=self._timeout) as response:
                raw_body = response.read().decode("utf-8")
        except error.HTTPError as exc:
            detail = exc.read().decode("utf-8", errors="replace")
            raise RuntimeError(f"Gemini request failed with HTTP {exc.code}: {detail}") from exc
        except error.URLError as exc:
            raise RuntimeError(f"Gemini request failed: {exc.reason}") from exc

        decoded = json.loads(raw_body)
        if decoded.get("error"):
            raise RuntimeError(f"Gemini request failed: {decoded['error']}")
        return decoded

    def _extract_text(self, response: dict[str, Any]) -> str:
        candidates = response.get("candidates", [])
        if not isinstance(candidates, list):
            return ""

        chunks: list[str] = []
        for candidate in candidates:
            if not isinstance(candidate, dict):
                continue
            content = candidate.get("content", {})
            if not isinstance(content, dict):
                continue
            parts = content.get("parts", [])
            if not isinstance(parts, list):
                continue
            for part in parts:
                if not isinstance(part, dict):
                    continue
                text = part.get("text")
                if isinstance(text, str):
                    chunks.append(text)
        return "".join(chunks).strip()

"""Lightweight Hurozo client library.

Provides an :class:`Agent` class to invoke agents via the Hurozo API.

Usage patterns:
  - Name-based: ``agent = Agent("My Agent")``  -> resolves name to UUID at runtime.
  - UUID-based: ``agent = Agent("2325125b-...", True)``  -> uses UUID directly.

Then:
  - Provide inputs: ``agent.input({"key": "value"})``
  - Run: ``agent.run()``

Configuration:
  - ``HUROZO_API_TOKEN``: Bearer token for API calls (required for name resolution and execution).
  - ``HUROZO_SERVER_URI``: Base URL for the API (default: ``https://app.hurozo.com``).
"""

from __future__ import annotations

import os
import re
from typing import Any, Dict, Optional

import requests


def _to_snake(name: str) -> str:
    """Convert a name to snake_case suitable for env vars."""
    name = re.sub(r"[^0-9a-zA-Z]+", "_", name)
    name = re.sub(r"(?<!^)(?=[A-Z])", "_", name)
    return name.strip("_").lower()


class Agent:
    """Represents an agent executable via the Hurozo API.

    Parameters:
    - identifier: display name (default) or UUID (when is_uuid=True)
    - is_uuid: set to True to skip name->UUID resolution and use the identifier directly
    """

    def __init__(self, identifier: str, is_uuid: bool = False):
        self._identifier = identifier
        self._is_uuid = is_uuid
        self.inputs: Dict[str, Any] = {}

    def input(self, mapping: Dict[str, Any]) -> "Agent":
        """Merge ``mapping`` into the agent's input dictionary."""
        self.inputs.update(mapping)
        return self

    def _resolve_uuid(self) -> str:
        """Resolve a display name to an agent UUID via /api/agents.

        Returns the identifier unchanged on failure or if already UUID mode.
        """
        if self._is_uuid:
            return self._identifier

        token = os.environ.get("HUROZO_API_TOKEN")
        if not token:
            # No token -> cannot resolve name. Fall back to given identifier.
            return self._identifier
        base_uri = os.environ.get("HUROZO_SERVER_URI", "https://app.hurozo.com").rstrip("/")
        try:
            resp = requests.get(
                f"{base_uri}/api/agents",
                headers={"Authorization": f"Bearer {token}"},
                timeout=10,
            )
            if not resp.ok:
                return self._identifier
            data = resp.json() or {}
            agents = data.get("agents", []) or []
            # Prefer exact case-sensitive match, then case-insensitive
            target: Optional[dict] = next((a for a in agents if a.get("name") == self._identifier), None)
            if not target:
                lid = self._identifier.lower()
                target = next((a for a in agents if str(a.get("name", "")).lower() == lid), None)
            return target.get("agent_uuid") if target and target.get("agent_uuid") else self._identifier
        except Exception:
            return self._identifier

    def run(self) -> Dict[str, Any]:
        """Invoke the agent via the Hurozo API using the configured token."""
        token = os.environ.get("HUROZO_API_TOKEN")
        if not token:
            raise RuntimeError("HUROZO_API_TOKEN environment variable is required")
        base_uri = os.environ.get("HUROZO_SERVER_URI", "https://app.hurozo.com").rstrip("/")
        agent_key = self._resolve_uuid()
        url = f"{base_uri}/execute/{agent_key}"
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        }
        response = requests.post(url, headers=headers, json={"inputs": self.inputs})
        response.raise_for_status()
        try:
            return response.json()
        except Exception:
            return {"status": response.status_code, "text": response.text}


__all__ = ["Agent"]

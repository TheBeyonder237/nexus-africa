"""BaaS — KYC Onboarding sessions."""

from __future__ import annotations

from typing import Any

from ..._models import CreateOnboardingSessionRequest, OnboardingSession, Party
from .._base import AsyncResource, SyncResource


class BaaSOnboardingResource(SyncResource):
    """Drive a KYC onboarding session through to an approved Party."""

    def create_session(
        self,
        *,
        nationality_code: str | None = None,
        document_type: str | None = None,
    ) -> OnboardingSession:
        """Open a new KYC onboarding session."""
        req = CreateOnboardingSessionRequest(
            nationality_code=nationality_code,
            document_type=document_type,
        )
        raw = self._post("/onboarding-sessions", req.model_dump(by_alias=True, exclude_none=True))
        return OnboardingSession.model_validate(raw)

    def upload_document(
        self, session_id: str, document: bytes, document_type: str
    ) -> dict[str, Any]:
        """Upload a KYC document to an onboarding session.

        Warning:
            This implementation is incomplete: the real endpoint expects
            ``multipart/form-data`` and the ``document`` bytes are **not yet
            sent** — only ``document_type`` is posted as JSON. Do not rely on
            it until it is reworked against the confirmed BaaS endpoint.
        """
        return self._post(
            f"/onboarding-sessions/{session_id}/documents",
            {"documentType": document_type},
        )

    def submit_session(self, session_id: str) -> OnboardingSession:
        """Submit a completed session for review."""
        raw = self._post(f"/onboarding-sessions/{session_id}/submit")
        return OnboardingSession.model_validate(raw)

    def get_session(self, session_id: str) -> OnboardingSession:
        """Retrieve an onboarding session by id."""
        raw = self._get(f"/onboarding-sessions/{session_id}")
        return OnboardingSession.model_validate(raw)

    def get_party(self, session_id: str) -> Party:
        """Retrieve the Party linked to an onboarding session."""
        raw = self._get(f"/onboarding-sessions/{session_id}/party")
        return Party.model_validate(raw)

    def list_sessions(self) -> list[OnboardingSession]:
        """List onboarding sessions for this account."""
        raw = self._get("/onboarding-sessions")
        items = raw if isinstance(raw, list) else raw.get("data", [])
        return [OnboardingSession.model_validate(s) for s in items]


class AsyncBaaSOnboardingResource(AsyncResource):
    """Async variant of :class:`BaaSOnboardingResource`."""

    async def create_session(
        self,
        *,
        nationality_code: str | None = None,
        document_type: str | None = None,
    ) -> OnboardingSession:
        req = CreateOnboardingSessionRequest(
            nationality_code=nationality_code,
            document_type=document_type,
        )
        raw = await self._post(
            "/onboarding-sessions", req.model_dump(by_alias=True, exclude_none=True)
        )
        return OnboardingSession.model_validate(raw)

    async def submit_session(self, session_id: str) -> OnboardingSession:
        raw = await self._post(f"/onboarding-sessions/{session_id}/submit")
        return OnboardingSession.model_validate(raw)

    async def get_session(self, session_id: str) -> OnboardingSession:
        raw = await self._get(f"/onboarding-sessions/{session_id}")
        return OnboardingSession.model_validate(raw)

    async def get_party(self, session_id: str) -> Party:
        raw = await self._get(f"/onboarding-sessions/{session_id}/party")
        return Party.model_validate(raw)

    async def list_sessions(self) -> list[OnboardingSession]:
        raw = await self._get("/onboarding-sessions")
        items = raw if isinstance(raw, list) else raw.get("data", [])
        return [OnboardingSession.model_validate(s) for s in items]

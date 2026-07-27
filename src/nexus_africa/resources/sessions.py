"""Sessions resource — hosted payment page."""

from __future__ import annotations

from .._models import CreateSessionRequest, DisplayInfo, Session
from ._base import AsyncResource, SyncResource


class SessionsResource(SyncResource):
    def create(
        self,
        transaction_intent_id: str,
        *,
        return_url: str | None = None,
        title: str | None = None,
        description: str | None = None,
        logo_url: str | None = None,
    ) -> Session:
        """Create a hosted payment session and obtain a redirect URL.

        Args:
            transaction_intent_id: ID of an existing Transaction Intent.
            return_url:            Where to redirect after payment.
            title:                 Displayed on the checkout page.
            description:           Displayed on the checkout page.
            logo_url:              Merchant logo URL on the checkout page.

        Returns:
            :class:`~nexus_africa.Session` with ``payment_link`` to redirect to.
        """
        display_info = None
        if any([title, description, logo_url]):
            display_info = DisplayInfo(title=title, description=description, logo_url=logo_url)

        req = CreateSessionRequest(
            transaction_intent_id=transaction_intent_id,
            return_url=return_url,
            display_info=display_info,
        )
        raw = self._post("/sessions", req.model_dump(by_alias=True, exclude_none=True))
        return Session.model_validate(raw)


class AsyncSessionsResource(AsyncResource):
    async def create(
        self,
        transaction_intent_id: str,
        *,
        return_url: str | None = None,
        title: str | None = None,
        description: str | None = None,
        logo_url: str | None = None,
    ) -> Session:
        display_info = None
        if any([title, description, logo_url]):
            display_info = DisplayInfo(title=title, description=description, logo_url=logo_url)

        req = CreateSessionRequest(
            transaction_intent_id=transaction_intent_id,
            return_url=return_url,
            display_info=display_info,
        )
        raw = await self._post("/sessions", req.model_dump(by_alias=True, exclude_none=True))
        return Session.model_validate(raw)

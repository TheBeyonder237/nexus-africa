"""BaaS resource aggregator — config, onboarding, parties, cards."""

from __future__ import annotations

from typing import TYPE_CHECKING

from .cards import AsyncBaaSCardsResource, BaaSCardsResource
from .config import AsyncBaaSConfigResource, BaaSConfigResource
from .onboarding import AsyncBaaSOnboardingResource, BaaSOnboardingResource
from .parties import AsyncBaaSPartiesResource, BaaSPartiesResource

if TYPE_CHECKING:
    from ..._client import AsyncNexusClient, NexusClient


class BaaSResource:
    """Aggregates all BaaS sub-resources under ``client.baas``."""

    def __init__(self, client: NexusClient) -> None:
        self.config = BaaSConfigResource(client)
        self.onboarding = BaaSOnboardingResource(client)
        self.parties = BaaSPartiesResource(client)
        self.cards = BaaSCardsResource(client)


class AsyncBaaSResource:
    def __init__(self, client: AsyncNexusClient) -> None:
        self.config = AsyncBaaSConfigResource(client)
        self.onboarding = AsyncBaaSOnboardingResource(client)
        self.parties = AsyncBaaSPartiesResource(client)
        self.cards = AsyncBaaSCardsResource(client)


__all__ = ["BaaSResource", "AsyncBaaSResource"]

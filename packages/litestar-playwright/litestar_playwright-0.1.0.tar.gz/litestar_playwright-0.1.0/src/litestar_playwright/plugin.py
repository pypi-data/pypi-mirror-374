"""Playwright plugin for Litestar."""
# pylint: disable=too-few-public-methods

from __future__ import annotations

import warnings
from typing import TYPE_CHECKING

from litestar.di import Provide
from litestar.plugins import InitPluginProtocol

if TYPE_CHECKING:
    from litestar.config.app import AppConfig

    from litestar_playwright.config import PlaywrightConfig


class PlaywrightPlugin(InitPluginProtocol):
    """Playwright integration for Litestar."""

    __slots__ = ("_config",)

    def __init__(self, config: PlaywrightConfig) -> None:
        """Initialize the plugin with configuration.

        Args:
            config: The Playwright configuration.
        """
        self._config = config

    @property
    def config(self) -> PlaywrightConfig:
        """Get the configuration.

        Returns:
            The configuration.
        """
        return self._config

    def on_app_init(self, app_config: AppConfig) -> AppConfig:
        """Initialize the plugin on app startup.

        Args:
            app_config: The application configuration.

        Returns:
            Updated application configuration.
        """
        dependency_keys = [
            self.config.playwright_browser_instance_state_key,
            self.config.playwright_instance_state_key,
        ]
        collisions = [key for key in dependency_keys if key in app_config.dependencies]
        if collisions:
            msg = (
                f"Dependency key collision detected: {collisions}. "
                "Existing dependencies will be overwritten."
            )
            warnings.warn(message=msg, stacklevel=2)
        app_config.dependencies.update(
            {
                self.config.playwright_browser_instance_state_key: Provide(
                    dependency=self.config.provide_playwright_browser_instance,
                    sync_to_thread=False,
                ),
                self.config.playwright_instance_state_key: Provide(
                    dependency=self.config.provide_playwright_instance,
                    sync_to_thread=False,
                ),
            },
        )

        app_config.lifespan.append(self.config.lifespan)
        return app_config

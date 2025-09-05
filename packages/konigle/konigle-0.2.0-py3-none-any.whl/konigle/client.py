"""
Main client classes for the Konigle SDK.

This module provides the primary Client and AsyncClient classes that serve
as the main entry points for interacting with the Konigle API.
"""

from typing import Optional

from .config import BASE_URL, ClientConfig
from .managers.core.media_asset import (
    AsyncDocumentManager,
    AsyncImageManager,
    AsyncVideoManager,
    DocumentManager,
    ImageManager,
    VideoManager,
)
from .session import AsyncSession, SyncSession


class Client:
    """
    Main synchronous client for Konigle API.

    This client provides access to all Konigle API resources through
    dedicated manager objects. It handles session management and
    configuration automatically.

    Example:
    ```python
    import konigle

    client = konigle.Client(api_key="your-api-key")
    products = client.products.list()
    product = client.products.get("product-id")
    ```
    """

    def __init__(
        self,
        api_key: str,
        base_url: str = BASE_URL,
        timeout: float = 30.0,
        retry_count: int = 3,
        retry_backoff: float = 0.5,
        max_connections: int = 100,
        keepalive_connections: int = 20,
        user_agent: Optional[str] = None,
        log_level: str = "WARNING",
        log_requests: bool = False,
        log_responses: bool = False,
        enable_retry: bool = True,
        **kwargs,
    ):
        """
        Initialize the Konigle client.

        Args:
            api_key: Konigle API key for authentication
            base_url: Base URL for the Konigle API
            timeout: Request timeout in seconds
            retry_count: Number of retries for failed requests
            retry_backoff: Base backoff time for exponential retry
            max_connections: Maximum number of HTTP connections in pool
            keepalive_connections: Number of connections to keep alive
            user_agent: Custom user agent string
            log_level: Logging level (DEBUG, INFO, WARNING, ERROR)
            log_requests: Whether to log HTTP requests
            log_responses: Whether to log HTTP responses
            enable_retry: Whether to enable automatic retries
            **kwargs: Additional configuration options
        """
        # Create configuration
        config_data = {
            "api_key": api_key,
            "base_url": base_url,
            "timeout": timeout,
            "retry_count": retry_count,
            "retry_backoff": retry_backoff,
            "max_connections": max_connections,
            "keepalive_connections": keepalive_connections,
            "user_agent": user_agent,
            "log_level": log_level,
            "log_requests": log_requests,
            "log_responses": log_responses,
            "enable_retry": enable_retry,
            **kwargs,
        }

        self._config = ClientConfig(**config_data)
        self._session = SyncSession(self._config)

        # Core resource managers
        self.images = ImageManager(self._session)
        self.videos = VideoManager(self._session)
        self.documents = DocumentManager(self._session)

        # TODO: Initialize other resource managers when created:

        # Website/CMS managers
        # self.pages = PageManager(self._session)
        # self.blogs = BlogManager(self._session)

        # Commerce managers
        # self.products = ProductManager(self._session)
        # self.variants = VariantManager(self._session)
        # self.customers = CustomerManager(self._session)

        # Marketing managers
        # self.emails = EmailManager(self._session)
        # self.sms = SMSManager(self._session)
        # self.campaigns = CampaignManager(self._session)

    @classmethod
    def from_env(cls) -> "Client":
        """
        Create client from environment variables.

        Environment variables should be prefixed with KONIQ_.

        Returns:
            Client instance configured from environment variables
        """
        config = ClientConfig.from_env()
        return cls(
            api_key=config.api_key,
            base_url=config.base_url,
            timeout=config.timeout,
            retry_count=config.retry_count,
            retry_backoff=config.retry_backoff,
            max_connections=config.max_connections,
            keepalive_connections=config.keepalive_connections,
            user_agent=config.user_agent,
            log_level=config.log_level,
            log_requests=config.log_requests,
            log_responses=config.log_responses,
            enable_retry=config.enable_retry,
        )

    def close(self):
        """Close the client and cleanup resources."""
        self._session.close()

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit with cleanup."""
        self.close()


class AsyncClient:
    """
    Main asynchronous client for Konigle API.

    This client provides async access to all Konigle API resources through
    dedicated async manager objects. It handles session management and
    configuration automatically.

    Example:
        async with konigle.AsyncClient(api_key="your-api-key") as client:
            products = await client.products.list()
            product = await client.products.get("product-id")
    """

    def __init__(
        self,
        api_key: str,
        base_url: str = BASE_URL,
        timeout: float = 30.0,
        retry_count: int = 3,
        retry_backoff: float = 0.5,
        max_connections: int = 100,
        keepalive_connections: int = 20,
        user_agent: Optional[str] = None,
        log_level: str = "WARNING",
        log_requests: bool = False,
        log_responses: bool = False,
        enable_retry: bool = True,
        **kwargs,
    ):
        """
        Initialize the async Konigle client.

        Args:
            api_key: Konigle API key for authentication
            base_url: Base URL for the Konigle API
            timeout: Request timeout in seconds
            retry_count: Number of retries for failed requests
            retry_backoff: Base backoff time for exponential retry
            max_connections: Maximum number of HTTP connections in pool
            keepalive_connections: Number of connections to keep alive
            user_agent: Custom user agent string
            log_level: Logging level (DEBUG, INFO, WARNING, ERROR)
            log_requests: Whether to log HTTP requests
            log_responses: Whether to log HTTP responses
            enable_retry: Whether to enable automatic retries
            **kwargs: Additional configuration options
        """
        # Create configuration
        config_data = {
            "api_key": api_key,
            "base_url": base_url,
            "timeout": timeout,
            "retry_count": retry_count,
            "retry_backoff": retry_backoff,
            "max_connections": max_connections,
            "keepalive_connections": keepalive_connections,
            "user_agent": user_agent,
            "log_level": log_level,
            "log_requests": log_requests,
            "log_responses": log_responses,
            "enable_retry": enable_retry,
            **kwargs,
        }

        self._config = ClientConfig(**config_data)
        self._session = AsyncSession(self._config)

        # Core resource managers
        self.images = AsyncImageManager(self._session)
        self.videos = AsyncVideoManager(self._session)
        self.documents = AsyncDocumentManager(self._session)

        # TODO: Initialize other async resource managers when created:

        # Website/CMS managers
        # self.pages = AsyncPageManager(self._session)
        # self.blogs = AsyncBlogManager(self._session)

        # Commerce managers
        # self.products = AsyncProductManager(self._session)
        # self.variants = AsyncVariantManager(self._session)
        # self.customers = AsyncCustomerManager(self._session)

        # Marketing managers
        # self.emails = AsyncEmailManager(self._session)
        # self.sms = AsyncSMSManager(self._session)
        # self.campaigns = AsyncCampaignManager(self._session)

    @classmethod
    def from_env(cls) -> "AsyncClient":
        """
        Create async client from environment variables.

        Environment variables should be prefixed with KONIQ_.

        Returns:
            AsyncClient instance configured from environment variables
        """
        config = ClientConfig.from_env()
        return cls(
            api_key=config.api_key,
            base_url=config.base_url,
            timeout=config.timeout,
            retry_count=config.retry_count,
            retry_backoff=config.retry_backoff,
            max_connections=config.max_connections,
            keepalive_connections=config.keepalive_connections,
            user_agent=config.user_agent,
            log_level=config.log_level,
            log_requests=config.log_requests,
            log_responses=config.log_responses,
            enable_retry=config.enable_retry,
        )

    async def aclose(self):
        """Close the async client and cleanup resources."""
        await self._session.aclose()

    async def __aenter__(self):
        """Async context manager entry."""
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit with cleanup."""
        await self.aclose()

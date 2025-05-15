"""
Base client class for dYdX v4 API interactions.
"""

import aiohttp
import logging
import ssl
import certifi
import json
from typing import Dict, Optional, Any
import asyncio
from abc import ABC, abstractmethod

class BaseClient(ABC):
    """
    Abstract base class for all API clients.
    Provides common functionality for HTTP requests, connection management, and error handling.
    """
    def __init__(self, config: Dict):
        """
        Initialize the base client.
        
        Args:
            config: Bot configuration dictionary
        """
        self.config = config
        self.session = None
        self.logger = logging.getLogger(self.__class__.__name__)
        
        # SSL Configuration
        self.ssl_context = ssl.create_default_context(cafile=certifi.where())
        if config.get('debug', {}).get('ssl_verify') is False:
            self.logger.warning("SSL verification disabled. This is not recommended for production.")
            self.ssl_context.check_hostname = False
            self.ssl_context.verify_mode = ssl.CERT_NONE
        
        # Request Configuration
        self.retry_attempts = config.get('rpc', {}).get('retry_attempts', 3)
        self.retry_delay = config.get('rpc', {}).get('retry_delay', 1)
        self.timeout = config.get('rpc', {}).get('timeout', 10)
        
        # Headers
        self.headers = {
            'Accept': 'application/json',
            'Content-Type': 'application/json',
            'User-Agent': 'dydx-v4-bot/1.0.0'
        }

    async def connect(self):
        """Establish HTTP connection."""
        if not self.session:
            timeout = aiohttp.ClientTimeout(total=self.timeout)
            connector = aiohttp.TCPConnector(
                ssl=self.ssl_context,
                force_close=True,
                enable_cleanup_closed=True
            )
            self.session = aiohttp.ClientSession(
                timeout=timeout,
                connector=connector,
                headers=self.headers
            )
            self.logger.debug(f"Connected to client")

    async def close(self):
        """Close HTTP connection."""
        if self.session:
            await self.session.close()
            self.session = None
            self.logger.debug("Connection closed")

    async def _make_request(
        self, 
        method: str, 
        url: str, 
        params: Optional[Dict] = None, 
        data: Optional[Dict] = None,
        headers: Optional[Dict] = None
    ) -> Optional[Dict]:
        """
        Make an HTTP request with retry logic.
        
        Args:
            method: HTTP method (GET, POST, etc.)
            url: Request URL
            params: URL parameters
            data: Request body data
            headers: Additional headers
            
        Returns:
            Response data or None if error
        """
        retry_count = 0
        merged_headers = {**self.headers, **(headers or {})}
        
        while retry_count < self.retry_attempts:
            try:
                if not self.session:
                    await self.connect()
                
                self.logger.debug(f"Request: {method} {url}")
                if data:
                    self.logger.debug(f"Request data: {json.dumps(data)}")
                
                kwargs = {}
                if params:
                    kwargs['params'] = params
                if data:
                    kwargs['json'] = data
                if headers:
                    kwargs['headers'] = merged_headers
                
                async with self.session.request(method, url, **kwargs) as response:
                    response_text = await response.text()
                    
                    if response.status == 200:
                        try:
                            response_data = json.loads(response_text)
                            if self.config.get('debug', {}).get('log_api_responses', False):
                                self.logger.debug(f"Response: {json.dumps(response_data)}")
                            return response_data
                        except json.JSONDecodeError:
                            self.logger.error(f"Invalid JSON response: {response_text}")
                            return None
                    else:
                        self.logger.error(
                            f"Request error: {response.status} - {response_text}"
                        )
                        return None
                        
            except aiohttp.ClientError as e:
                self.logger.error(f"HTTP client error: {e}")
            except asyncio.TimeoutError:
                self.logger.error("Request timeout")
            except Exception as e:
                self.logger.error(f"Unexpected error: {e}")
            
            retry_count += 1
            if retry_count < self.retry_attempts:
                self.logger.info(f"Retrying ({retry_count}/{self.retry_attempts})...")
                await asyncio.sleep(self.retry_delay)
                # Force reconnection
                await self.close()
        
        return None
    
    @abstractmethod
    async def get_market_data(self, market: str) -> Optional[Dict]:
        """
        Get market data for the specified market.
        
        Args:
            market: Trading pair (e.g., 'ETH-USD')
            
        Returns:
            Market data or None if error
        """
        pass

    async def __aenter__(self):
        """Support for async context manager."""
        await self.connect()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Support for async context manager."""
        await self.close()

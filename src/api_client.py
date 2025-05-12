"""
Cliente API simplificado para a dYdX v4
"""

import aiohttp
import logging
import ssl
from typing import Dict, Optional
import json
import certifi

class DydxApiClient:
    def __init__(self, config: Dict):
        """
        Inicializa o cliente API da dYdX
        
        Args:
            config: Configuração do bot contendo endpoints da API
        """
        self.config = config
        self.rest_endpoint = config['network']['endpoints']['rest']
        self.session = None
        self.logger = logging.getLogger(__name__)
        
        # Configurações SSL
        self.ssl_context = ssl.create_default_context(cafile=certifi.where())
        if config.get('debug', {}).get('ssl_verify') is False:
            self.ssl_context.check_hostname = False
            self.ssl_context.verify_mode = ssl.CERT_NONE

    async def connect(self):
        """Inicia a sessão HTTP"""
        if not self.session:
            timeout = aiohttp.ClientTimeout(total=30)
            connector = aiohttp.TCPConnector(
                ssl=self.ssl_context,
                force_close=True,
                enable_cleanup_closed=True
            )
            self.session = aiohttp.ClientSession(
                timeout=timeout,
                connector=connector,
                headers={
                    'Accept': 'application/json',
                    'Content-Type': 'application/json'
                }
            )
            self.logger.debug(f"Conectado ao endpoint: {self.rest_endpoint}")

    async def close(self):
        """Fecha a sessão HTTP"""
        if self.session:
            await self.session.close()
            self.session = None

    async def _make_request(self, method: str, url: str, **kwargs) -> Optional[Dict]:
        """
        Faz uma requisição HTTP com retry
        
        Args:
            method: Método HTTP (GET, POST, etc)
            url: URL da requisição
            **kwargs: Argumentos adicionais para a requisição
            
        Returns:
            Dict com a resposta ou None se houver erro
        """
        max_retries = 3
        retry_count = 0
        
        while retry_count < max_retries:
            try:
                if not self.session:
                    await self.connect()
                
                self.logger.debug(f"Requisitando [{method}] {url}")
                async with self.session.request(method, url, **kwargs) as response:
                    if response.status == 200:
                        data = await response.json()
                        self.logger.debug(f"Resposta da API: {data}")
                        return data
                    else:
                        self.logger.error(
                            f"Erro na requisição: {response.status} - {await response.text()}"
                        )
                        return None
                        
            except Exception as e:
                self.logger.error(f"Erro na requisição API: {e}")
                retry_count += 1
                if retry_count < max_retries:
                    self.logger.info(f"Tentando novamente ({retry_count}/{max_retries})...")
                    await self.close()  # Força reconexão
                
        return None

    async def get_market_data(self, market: str) -> Optional[Dict]:
        """
        Obtém dados do mercado via API REST
        
        Args:
            market: Par de trading (ex: 'ETH-USD')
            
        Returns:
            Dict contendo dados do mercado ou None se houver erro
        """
        url = f"{self.rest_endpoint}/perpetual/markets"
        data = await self._make_request('GET', url)
        
        if data and 'markets' in data:
            return data['markets'].get(market)
        return None

    async def get_orderbook(self, market: str) -> Optional[Dict]:
        """
        Obtém o orderbook do mercado
        
        Args:
            market: Par de trading (ex: 'ETH-USD')
            
        Returns:
            Dict contendo orderbook ou None se houver erro
        """
        url = f"{self.rest_endpoint}/perpetual/markets/{market}/orderbook"
        data = await self._make_request('GET', url)
        
        if data:
            return data.get('orderbook')
        return None

    async def get_trades(self, market: str, limit: int = 100) -> Optional[Dict]:
        """
        Obtém trades recentes do mercado
        
        Args:
            market: Par de trading (ex: 'ETH-USD')
            limit: Número máximo de trades a retornar
            
        Returns:
            Dict contendo trades ou None se houver erro
        """
        url = f"{self.rest_endpoint}/perpetual/markets/{market}/trades?limit={limit}"
        data = await self._make_request('GET', url)
        
        if data:
            return data.get('trades', [])
        return None

    async def place_order(self, payload: Dict) -> Optional[Dict]:
        """
        Envia uma ordem para a dYdX (endpoint de ordens).
        Args:
            payload: dicionário com os parâmetros da ordem
        Returns:
            Resposta da API ou None se houver erro
        """
        url = f"{self.rest_endpoint}/perpetual/orders"
        data = await self._make_request('POST', url, json=payload)
        if data:
            return data
        return None

    async def __aenter__(self):
        """Suporte para context manager assíncrono"""
        await self.connect()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Suporte para context manager assíncrono"""
        await self.close()
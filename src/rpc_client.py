"""
Cliente RPC para a dYdX v4 usando Tendermint RPC e Cosmos SDK queries
"""

import asyncio
import aiohttp
import json
import logging
import ssl
import certifi
import base64
from typing import Dict, Optional, List, Any
from datetime import datetime

class DydxRpcClient:
    def __init__(self, config: Dict):
        """
        Inicializa o cliente RPC da dYdX
        
        Args:
            config: Configuração do bot contendo endpoints RPC
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
        
        # Configurações RPC
        self.rpc_config = config.get('rpc', {})
        self.retry_attempts = self.rpc_config.get('retry_attempts', 3)
        self.retry_delay = self.rpc_config.get('retry_delay', 1)
        self.timeout = self.rpc_config.get('timeout', 10)
        
        # Cache de dados
        self._last_block = None

    async def connect(self):
        """Estabelece conexão HTTP"""
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
                headers={
                    'Accept': 'application/json',
                    'User-Agent': 'dydx-v4-bot/1.0.0'
                }
            )

    async def close(self):
        """Fecha a conexão"""
        if self.session:
            await self.session.close()
            self.session = None

    async def _rpc_request(self, method: str, params: Dict = None) -> Optional[Dict]:
        """
        Faz uma requisição RPC Tendermint
        
        Args:
            method: Método RPC
            params: Parâmetros da requisição
            
        Returns:
            Dict com a resposta ou None se houver erro
        """
        url = f"{self.rest_endpoint}/{method}"
        if params:
            # Converte parâmetros para query string
            param_strings = []
            for key, value in params.items():
                if isinstance(value, dict):
                    value = json.dumps(value)
                param_strings.append(f"{key}={value}")
            url += "?" + "&".join(param_strings)
        
        for attempt in range(self.retry_attempts):
            try:
                if not self.session:
                    await self.connect()
                
                self.logger.debug(f"RPC Request: {url}")
                async with self.session.get(url) as response:
                    if response.status == 200:
                        data = await response.json()
                        self.logger.debug(f"RPC Response: {json.dumps(data)}")
                        if 'error' in data:
                            self.logger.error(f"Erro RPC: {data['error']}")
                            return None
                        return data.get('result')
                    else:
                        self.logger.error(
                            f"Erro na requisição RPC: {response.status}"
                        )
                        
            except Exception as e:
                self.logger.error(f"Erro ao fazer requisição RPC: {e}")
                if attempt < self.retry_attempts - 1:
                    await asyncio.sleep(self.retry_delay)
                    
        return None

    async def get_latest_block(self) -> Optional[Dict]:
        """Obtém informações do último bloco"""
        return await self._rpc_request("abci_info")

    async def get_network_status(self) -> Optional[Dict]:
        """Obtém status da rede"""
        return await self._rpc_request("status")

    async def get_market_data(self, market: str) -> Optional[Dict]:
        """
        Obtém dados do mercado via Cosmos SDK query
        
        Args:
            market: Par de trading (ex: 'ETH-USD')
            
        Returns:
            Dict com dados do mercado ou None se houver erro
        """
        try:
            # Primeiro, obtém o height atual
            status = await self.get_network_status()
            if not status:
                return None
            
            height = status.get('sync_info', {}).get('latest_block_height')
            
            # Tenta diferentes caminhos de query até encontrar um que funcione
            paths = [
                "/dydxprotocol/clob/get_market",  # Novo endpoint v4
                "/dydx/markets",                   # Endpoint legado
                "/clob/markets",                   # Endpoint alternativo
                "/markets/info"                    # Endpoint genérico
            ]
            
            for path in paths:
                params = {
                    "path": path,
                    "data": base64.b64encode(market.encode()).decode(),
                    "height": height,
                    "prove": "false"
                }
                
                data = await self._rpc_request("abci_query", params)
                if data and 'response' in data and data['response'].get('code', 1) == 0:
                    value = data['response'].get('value')
                    if value:
                        try:
                            decoded = base64.b64decode(value)
                            return json.loads(decoded)
                        except Exception as decode_err:
                            self.logger.debug(f"Erro ao decodificar: {decode_err}")
                            continue
            
            # Se nenhum caminho funcionou, tenta um endpoint REST direto
            rest_url = f"{self.rest_endpoint}/cosmos/base/tendermint/v1beta1/blocks/{height}"
            async with self.session.get(rest_url) as response:
                if response.status == 200:
                    data = await response.json()
                    # Procura por dados de mercado no bloco
                    return self._extract_market_data(data, market)
                    
            return None
            
        except Exception as e:
            self.logger.error(f"Erro ao obter dados do mercado: {e}")
            return None

    def _extract_market_data(self, block_data: Dict, market: str) -> Optional[Dict]:
        """
        Extrai dados de mercado de um bloco
        
        Args:
            block_data: Dados do bloco
            market: Par de trading
            
        Returns:
            Dict com dados do mercado ou None
        """
        try:
            txs = block_data.get('block', {}).get('data', {}).get('txs', [])
            for tx in txs:
                try:
                    tx_data = base64.b64decode(tx)
                    if market.encode() in tx_data:
                        # Encontrou uma transação relacionada ao mercado
                        return {'market': market, 'raw_data': tx}
                except:
                    continue
            return None
        except Exception as e:
            self.logger.error(f"Erro ao extrair dados: {e}")
            return None

    async def get_block(self, height: Optional[int] = None) -> Optional[Dict]:
        """
        Obtém dados de um bloco específico
        
        Args:
            height: Altura do bloco (None para o último bloco)
            
        Returns:
            Dict com dados do bloco ou None se houver erro
        """
        params = {}
        if height is not None:
            params['height'] = str(height)
        
        return await self._rpc_request("block", params)

    async def __aenter__(self):
        """Suporte para context manager assíncrono"""
        await self.connect()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Suporte para context manager assíncrono"""
        await self.close()
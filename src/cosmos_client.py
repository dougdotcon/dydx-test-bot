"""
Cliente CometBFT (Tendermint) RPC para a dYdX v4
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

class DydxCosmosClient:
    def __init__(self, config: Dict):
        """
        Inicializa o cliente Cosmos para a dYdX v4
        
        Args:
            config: Configuração do bot contendo endpoints
        """
        self.config = config
        self.rest_endpoint = config['network']['endpoints']['rest'].rstrip('/')
        self.session = None
        self.logger = logging.getLogger(__name__)
        
        # Configurações SSL
        self.ssl_context = ssl.create_default_context(cafile=certifi.where())
        if config.get('debug', {}).get('ssl_verify') is False:
            self.ssl_context.check_hostname = False
            self.ssl_context.verify_mode = ssl.CERT_NONE
        
        # Configurações de retry
        self.retry_attempts = config.get('rpc', {}).get('retry_attempts', 3)
        self.retry_delay = config.get('rpc', {}).get('retry_delay', 1)
        self.timeout = config.get('rpc', {}).get('timeout', 10)

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

    async def _rpc_request(self, endpoint: str, params: Dict = None) -> Optional[Dict]:
        """
        Faz uma requisição RPC
        
        Args:
            endpoint: Endpoint da requisição
            params: Parâmetros da requisição
            
        Returns:
            Dict com resultado ou None se houver erro
        """
        try:
            url = f"{self.rest_endpoint}/{endpoint}"
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
                            self.logger.debug(f"RPC Response: {json.dumps(data, indent=2)}")
                            if 'error' in data:
                                self.logger.error(f"Erro RPC: {data['error']}")
                                return None
                            return data.get('result')
                        else:
                            text = await response.text()
                            self.logger.error(f"Erro na requisição RPC: {response.status} - {text}")
                            
                except Exception as e:
                    self.logger.error(f"Erro ao fazer requisição RPC: {e}")
                    if attempt < self.retry_attempts - 1:
                        await asyncio.sleep(self.retry_delay)
            
            return None
            
        except Exception as e:
            self.logger.error(f"Erro em _rpc_request: {e}")
            return None

    async def get_network_status(self) -> Optional[Dict]:
        """Obtém status da rede"""
        return await self._rpc_request("status")

    async def get_latest_block(self) -> Optional[Dict]:
        """Obtém informações do último bloco"""
        return await self._rpc_request("block")

    async def get_market_data(self, market: str) -> Optional[Dict]:
        """
        Obtém dados do mercado via ABCI queries
        
        Args:
            market: Par de trading (ex: 'ETH-USD')
            
        Returns:
            Dict com dados do mercado ou None se houver erro
        """
        try:
            # Primeiro obtém o block height atual
            status = await self.get_network_status()
            if not status:
                return None
            
            height = status.get('sync_info', {}).get('latest_block_height')
            
            # Na dYdX v4, os dados de mercado são armazenados em módulos específicos
            modules = [
                ("clob", "orderbook"),           # Central Limit Order Book
                ("prices", "oracle"),            # Oracle de preços
                ("perpetuals", "markets"),       # Mercados perpétuos
                ("stats", "markets"),            # Estatísticas de mercado
            ]
            
            # Função auxiliar para criar o prefixo da store
            def create_store_key(module: str, submodule: str, market_id: str) -> str:
                return f"{module}/{submodule}/{market_id}".encode()
            
            # Tenta cada módulo
            for module, submodule in modules:
                store_key = create_store_key(module, submodule, market)
                encoded_key = base64.b64encode(store_key).decode()
                
                # Query usando o store do módulo
                params = {
                    "path": f"/store/{module}/key",
                    "data": encoded_key,
                    "height": height,
                    "prove": "false"
                }
                
                self.logger.debug(f"Tentando query no módulo {module}/{submodule}")
                data = await self._rpc_request("abci_query", params)
                
                if data and data.get('response', {}).get('value'):
                    try:
                        decoded = base64.b64decode(data['response']['value'])
                        market_data = json.loads(decoded)
                        self.logger.debug(f"Dados encontrados no módulo {module}")
                        return market_data
                    except:
                        continue
            
            # Se nenhum módulo retornou dados, tenta via estado da chain
            state_path = f"/dydxprotocol/{market.lower()}/state"
            params = {
                "path": state_path,
                "height": height,
                "prove": "false"
            }
            
            self.logger.debug(f"Tentando query de estado: {state_path}")
            state_data = await self._rpc_request("abci_query", params)
            
            if state_data and state_data.get('response', {}).get('value'):
                try:
                    decoded = base64.b64decode(state_data['response']['value'])
                    return json.loads(decoded)
                except:
                    pass
            
            # Se ainda não encontrou, tenta extrair do bloco
            block = await self.get_latest_block()
            if block:
                return self._extract_market_data_from_block(block, market)
            
            return None
            
        except Exception as e:
            self.logger.error(f"Erro ao obter dados do mercado: {e}")
            return None

    def _extract_market_data_from_block(self, block_data: Dict, market: str) -> Optional[Dict]:
        """
        Extrai dados de mercado de um bloco
        
        Args:
            block_data: Dados do bloco
            market: Par de trading
            
        Returns:
            Dict com dados do mercado ou None
        """
        try:
            # Procura por transações relacionadas ao mercado
            txs = block_data.get('block', {}).get('data', {}).get('txs', [])
            market_txs = []
            market_bytes = market.encode()
            
            for tx in txs:
                try:
                    tx_data = base64.b64decode(tx)
                    if market_bytes in tx_data:
                        market_txs.append(tx_data)
                except:
                    continue
            
            if market_txs:
                # Extrai informações básicas
                block_time = block_data.get('block', {}).get('header', {}).get('time')
                height = block_data.get('block', {}).get('header', {}).get('height')
                
                # Tenta encontrar dados de preço nas transações
                for tx_data in market_txs:
                    try:
                        # Procura por padrões conhecidos nos dados
                        # Exemplo: {"type":"price_update","market":"ETH-USD","price":"2000.00"}
                        if b'"price"' in tx_data and b'"market"' in tx_data:
                            decoded = json.loads(tx_data.decode())
                            if 'price' in decoded:
                                return {
                                    'market': market,
                                    'price': decoded['price'],
                                    'last_update': block_time,
                                    'height': height
                                }
                    except:
                        continue
                
                # Se não encontrou preço, retorna dados básicos
                return {
                    'market': market,
                    'transactions': len(market_txs),
                    'last_update': block_time,
                    'height': height
                }
            
            return None
            
        except Exception as e:
            self.logger.error(f"Erro ao extrair dados do bloco: {e}")
            return None

    async def __aenter__(self):
        """Suporte para context manager assíncrono"""
        await self.connect()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Suporte para context manager assíncrono"""
        await self.close()
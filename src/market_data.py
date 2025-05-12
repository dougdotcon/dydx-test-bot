"""
Módulo responsável pela coleta e análise de dados de mercado da dYdX.
Implementa polling da API REST para dados de mercado.
"""

from typing import Dict, List, Optional
import asyncio
import logging
from datetime import datetime, timedelta
import pandas as pd
import numpy as np
from .api_client import DydxApiClient

class MarketData:
    def __init__(self, config: Dict):
        """
        Inicializa o módulo de dados de mercado.
        
        Args:
            config: Configurações do bot (do config.json)
        """
        self.config = config
        self.market = config['trading']['market']
        self.timeframe = config['trading']['timeframe']
        self.volume_lookback = config['technical']['volume_lookback']
        self.polling_interval = 5  # segundos
        
        # Cache de dados
        self.prices: List[float] = []
        self.volumes: List[float] = []
        self.timestamps: List[datetime] = []
        
        # API Client
        self.client = DydxApiClient(config)
        
        # Controle
        self.running = False
        
        # Logger
        self.logger = logging.getLogger(__name__)

    async def connect(self):
        """Inicia a conexão com a API"""
        try:
            # Inicia cliente API
            await self.client.connect()
            
            # Carrega dados iniciais
            await self._load_initial_data()
            
            self.running = True
            self.logger.info(f"Conectado à API da dYdX para {self.market}")
            
        except Exception as e:
            self.logger.error(f"Erro ao conectar: {e}")
            raise

    async def _load_initial_data(self):
        """Carrega dados históricos iniciais"""
        try:
            # Obtém trades recentes para calcular volume
            trades = await self.client.get_trades(self.market, limit=100)
            if trades:
                for trade in trades:
                    # Extrai dados do formato da dYdX v4
                    price = float(trade.get('price', 0))
                    size = float(trade.get('size', 0))
                    created_at = trade.get('createdAt', '')
                    if created_at:
                        timestamp = datetime.fromisoformat(
                            created_at.replace('Z', '+00:00')
                        )
                    else:
                        timestamp = datetime.now()
                    
                    self.prices.append(price)
                    self.volumes.append(size * price)  # Volume em USD
                    self.timestamps.append(timestamp)
                
                self.logger.info(f"Carregados {len(trades)} trades históricos")
            
        except Exception as e:
            self.logger.error(f"Erro ao carregar dados iniciais: {e}")

    async def _update_market_data(self):
        """Atualiza dados de mercado via API REST"""
        try:
            market_data = await self.client.get_market_data(self.market)
            if market_data:
                # Extrai dados do formato da dYdX v4
                price = float(market_data.get('oraclePrice', 0))
                if not price:
                    price = float(market_data.get('indexPrice', 0))
                
                # Volume é calculado a partir dos trades mais recentes
                trades = await self.client.get_trades(self.market, limit=10)
                volume = sum(
                    float(trade.get('size', 0)) * float(trade.get('price', 0))
                    for trade in (trades or [])
                )
                
                timestamp = datetime.now()

                if price > 0:
                    self.prices.append(price)
                    self.volumes.append(volume)
                    self.timestamps.append(timestamp)

                    # Mantém apenas dados dentro do período de lookback
                    cutoff = timestamp - timedelta(minutes=self.volume_lookback)
                    while self.timestamps and self.timestamps[0] < cutoff:
                        self.prices.pop(0)
                        self.volumes.pop(0)
                        self.timestamps.pop(0)

                    self.logger.debug(
                        f"Dados atualizados - Preço: {price}, Volume: {volume}"
                    )

        except Exception as e:
            self.logger.error(f"Erro ao atualizar dados de mercado: {e}")

    async def listen(self):
        """Loop principal de polling da API"""
        while self.running:
            try:
                await self._update_market_data()
                await asyncio.sleep(self.polling_interval)
            except Exception as e:
                self.logger.error(f"Erro no loop de atualização: {e}")
                await asyncio.sleep(5)  # Espera antes de tentar novamente

    def get_current_price(self) -> Optional[float]:
        """Retorna o preço atual do mercado"""
        return self.prices[-1] if self.prices else None

    def calculate_volume_anomaly(self) -> Optional[float]:
        """
        Calcula se o volume atual é anômalo comparado com a média.
        Retorna a razão entre volume atual e média dos volumes.
        """
        if not self.volumes:
            return None

        current_volume = self.volumes[-1]
        avg_volume = np.mean(self.volumes[:-1]) if len(self.volumes) > 1 else current_volume
        
        return current_volume / avg_volume if avg_volume > 0 else None

    def calculate_resistance(self) -> Optional[float]:
        """
        Calcula o nível de resistência atual baseado nas máximas recentes.
        """
        if not self.prices:
            return None

        lookback = self.config['technical']['resistance_period']
        prices_df = pd.DataFrame({
            'price': self.prices[-lookback:],
            'timestamp': self.timestamps[-lookback:]
        })
        
        # Implementação simples: usa a máxima do período como resistência
        return prices_df['price'].max()

    async def close(self):
        """Fecha as conexões"""
        self.running = False
        await self.client.close()
        self.logger.info("Conexões fechadas")

    async def __aenter__(self):
        """Suporte para context manager assíncrono"""
        await self.connect()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Suporte para context manager assíncrono"""
        await self.close()
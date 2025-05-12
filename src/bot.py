"""
Classe principal do bot de trading
"""

import asyncio
import logging
from typing import Dict, Optional
import os
import signal

from .market_data import MarketData
from .execution import Execution
from .utils import (
    setup_logging,
    load_config,
    load_env,
    validate_config
)

class TradingBot:
    def __init__(self):
        """Inicializa o bot de trading"""
        # Configuração inicial
        load_env()
        self.config = load_config()
        validate_config(self.config)
        setup_logging(os.getenv("LOG_LEVEL", "INFO"))
        
        self.logger = logging.getLogger(__name__)
        self.running = False
        self.market_data = None
        self.execution = None
        self._tasks = []
        self._shutdown_event = None

    async def start(self):
        """Inicia o bot"""
        try:
            self.logger.info("Iniciando bot de trading...")
            
            # Cria evento de shutdown
            self._shutdown_event = asyncio.Event()
            
            # Inicializa módulo de dados de mercado
            async with MarketData(self.config) as market_data:
                self.market_data = market_data
                # Instancia Execution com api_client do market_data
                self.execution = Execution(self.config, self.market_data.client)
                self.running = True
                self.logger.info("Bot iniciado com sucesso")
                
                # Inicia loop principal
                await self._main_loop()
            
        except Exception as e:
            self.logger.error(f"Erro ao iniciar bot: {e}")
            await self.stop()
            raise

    async def stop(self):
        """Para o bot"""
        self.logger.info("Parando bot...")
        self.running = False
        
        if self._shutdown_event:
            self._shutdown_event.set()
        
        # Cancela todas as tasks pendentes
        for task in self._tasks:
            if not task.done():
                task.cancel()
                try:
                    await task
                except asyncio.CancelledError:
                    pass
        
        self.logger.info("Bot parado")

    async def _main_loop(self):
        """Loop principal do bot"""
        try:
            # Inicia monitoramento de dados de mercado
            market_data_task = asyncio.create_task(
                self.market_data.listen()
            )
            self._tasks.append(market_data_task)
            
            while self.running and not self._shutdown_event.is_set():
                try:
                    # Obtém dados atuais
                    current_price = self.market_data.get_current_price()
                    volume_anomaly = self.market_data.calculate_volume_anomaly()
                    resistance = self.market_data.calculate_resistance()
                    
                    if all([current_price, volume_anomaly, resistance]):
                        # Verifica condições para breakout
                        volume_threshold = self.config['trading']['volume_factor']
                        
                        if (current_price > resistance and 
                            volume_anomaly > volume_threshold):
                            self.logger.info(
                                f"Possível breakout detectado!"
                                f"\nPreço: {current_price} > {resistance}"
                                f"\nVolume: {volume_anomaly:.2f}x acima da média"
                            )
                            # Envia ordem simulada
                            size = 0.01  # Valor fixo para simulação
                            result = await self.execution.send_order(
                                side="buy",
                                size=size,
                                price=None  # Ordem a mercado
                            )
                            self.logger.info(f"Resultado da ordem: {result}")
                        
                        self.logger.debug(
                            f"Preço: {current_price}, "
                            f"Volume/Média: {volume_anomaly:.2f}, "
                            f"Resistência: {resistance}"
                        )
                        
                    await asyncio.sleep(1)  # Evita consumo excessivo de CPU
                    
                except Exception as e:
                    self.logger.error(f"Erro no loop principal: {e}")
                    await asyncio.sleep(5)  # Espera antes de tentar novamente
            
        except asyncio.CancelledError:
            self.logger.info("Loop principal cancelado")
        except Exception as e:
            self.logger.error(f"Erro fatal no loop principal: {e}")
            raise
        finally:
            # Garante que todas as tasks sejam encerradas
            await self.stop()

def handle_shutdown(bot: TradingBot, loop: asyncio.AbstractEventLoop):
    """Handler para sinais de shutdown"""
    async def _shutdown():
        await bot.stop()
        tasks = [t for t in asyncio.all_tasks() if t is not
                asyncio.current_task()]
        for task in tasks:
            task.cancel()
        await asyncio.gather(*tasks, return_exceptions=True)
        loop.stop()
    
    loop.create_task(_shutdown())

def main():
    """Função principal para executar o bot"""
    bot = TradingBot()
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    
    # Configura handlers para sinais de shutdown
    for sig in (signal.SIGINT, signal.SIGTERM):
        loop.add_signal_handler(
            sig,
            lambda s=sig: handle_shutdown(bot, loop)
        )
    
    try:
        loop.run_until_complete(bot.start())
        loop.run_forever()
    except Exception as e:
        logging.error(f"Erro fatal: {e}")
        raise
    finally:
        loop.close()

if __name__ == "__main__":
    main()
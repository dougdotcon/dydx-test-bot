"""
Main trading bot class.
"""

import asyncio
import logging
import os
import signal
from typing import Dict, Optional, List, Any

from ..utils.config import load_env, load_config, validate_config
from ..utils.logging import setup_logging, TradeLogger
from .market_data import MarketDataService
from .execution import ExecutionService
from ..strategies.breakout_strategy import BreakoutStrategy

class TradingBot:
    """
    Main trading bot class.
    Orchestrates market data, strategy, and execution.
    """
    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize the trading bot.
        
        Args:
            config_path: Path to configuration file
        """
        # Load configuration
        load_env()
        self.config = load_config(config_path)
        validate_config(self.config)
        
        # Setup logging
        log_level = os.getenv("LOG_LEVEL", "INFO")
        log_file = os.getenv("LOG_FILE", "bot.log")
        setup_logging(log_level, log_file)
        
        # Initialize logger
        self.logger = logging.getLogger(__name__)
        self.trade_logger = TradeLogger()
        
        # Control flags
        self.running = False
        self._shutdown_event = None
        self._tasks = []
        
        # Components (initialized in start())
        self.market_data = None
        self.execution = None
        self.strategy = None
        
        self.logger.info("Trading bot initialized")
    
    async def start(self):
        """Start the trading bot."""
        try:
            self.logger.info("Starting trading bot...")
            
            # Create shutdown event
            self._shutdown_event = asyncio.Event()
            
            # Initialize market data service
            self.market_data = MarketDataService(self.config)
            await self.market_data.connect()
            
            # Initialize execution service
            self.execution = ExecutionService(self.config)
            await self.execution.connect()
            
            # Initialize strategy
            self.strategy = BreakoutStrategy(self.config)
            
            # Set running flag
            self.running = True
            self.logger.info("Trading bot started successfully")
            
            # Start main loop
            await self._main_loop()
            
        except Exception as e:
            self.logger.error(f"Error starting bot: {e}")
            await self.stop()
            raise
    
    async def stop(self):
        """Stop the trading bot."""
        self.logger.info("Stopping trading bot...")
        self.running = False
        
        if self._shutdown_event:
            self._shutdown_event.set()
        
        # Cancel all pending tasks
        for task in self._tasks:
            if not task.done():
                task.cancel()
                try:
                    await task
                except asyncio.CancelledError:
                    pass
        
        # Close services
        if self.market_data:
            await self.market_data.close()
        
        if self.execution:
            await self.execution.close()
        
        self.logger.info("Trading bot stopped")
    
    async def _main_loop(self):
        """Main trading loop."""
        try:
            # Start market data listener
            market_data_task = asyncio.create_task(
                self.market_data.listen()
            )
            self._tasks.append(market_data_task)
            
            # Main loop
            while self.running and not self._shutdown_event.is_set():
                try:
                    # Get market data for analysis
                    market_data = self.market_data.get_market_data_for_analysis()
                    
                    # Skip if not enough data
                    if not market_data['prices']:
                        self.logger.debug("Not enough market data for analysis")
                        await asyncio.sleep(1)
                        continue
                    
                    # Analyze market data
                    analysis = await self.strategy.analyze(market_data)
                    
                    # Log analysis
                    self.logger.debug(
                        f"Analysis: Price={analysis.get('current_price')}, "
                        f"Signal={analysis.get('signal')}, "
                        f"Volume={analysis.get('volume_anomaly', 0):.2f}x"
                    )
                    
                    # Check for entry signal
                    if self.strategy.should_enter(analysis):
                        self.logger.info(
                            f"Entry signal detected: {analysis.get('signal')}"
                        )
                        
                        # Log signal
                        self.trade_logger.log_signal(
                            self.config['trading']['market'],
                            analysis
                        )
                        
                        # Calculate position size (simplified for now)
                        size = 0.01  # Fixed size for testing
                        
                        # Send order
                        order_result = await self.execution.send_order(
                            side="buy",
                            size=size,
                            price=None  # Market order
                        )
                        
                        # Log order
                        self.trade_logger.log_order(
                            self.config['trading']['market'],
                            order_result
                        )
                        
                        self.logger.info(f"Order result: {order_result}")
                    
                    # Check for exit signal (if position exists)
                    position = await self.execution.get_position()
                    if position and self.strategy.should_exit(analysis, position):
                        self.logger.info("Exit signal detected")
                        
                        # Close position
                        close_result = await self.execution.close_position()
                        
                        # Log position close
                        self.trade_logger.log_trade(
                            self.config['trading']['market'],
                            close_result
                        )
                        
                        self.logger.info(f"Position closed: {close_result}")
                    
                    # Sleep to avoid excessive CPU usage
                    await asyncio.sleep(1)
                    
                except Exception as e:
                    self.logger.error(f"Error in main loop: {e}")
                    await asyncio.sleep(5)  # Wait before retrying
            
        except asyncio.CancelledError:
            self.logger.info("Main loop cancelled")
        except Exception as e:
            self.logger.error(f"Fatal error in main loop: {e}")
            raise
        finally:
            # Ensure all services are stopped
            await self.stop()

def handle_shutdown(bot: TradingBot, loop: asyncio.AbstractEventLoop):
    """
    Handle shutdown signals.
    
    Args:
        bot: Trading bot instance
        loop: Event loop
    """
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
    """Main entry point for the trading bot."""
    bot = TradingBot()
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    
    # Set up signal handlers
    for sig in (signal.SIGINT, signal.SIGTERM):
        loop.add_signal_handler(
            sig,
            lambda s=sig: handle_shutdown(bot, loop)
        )
    
    try:
        loop.run_until_complete(bot.start())
        loop.run_forever()
    except Exception as e:
        logging.error(f"Fatal error: {e}")
        raise
    finally:
        loop.close()

if __name__ == "__main__":
    main()

"""
Logging utilities for the trading bot.
"""

import logging
import os
from pathlib import Path
from typing import Optional, Dict, Any
import json
from datetime import datetime

def setup_logging(
    log_level: str = "INFO",
    log_file: Optional[str] = None,
    log_format: Optional[str] = None
) -> None:
    """
    Set up logging configuration.
    
    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Log file path (default: from environment or bot.log)
        log_format: Log format string
    """
    if log_file is None:
        log_file = os.getenv("LOG_FILE", "bot.log")
    
    if log_format is None:
        log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    # Create log directory if it doesn't exist
    log_path = Path(log_file)
    if log_path.parent != Path('.'):
        log_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Configure logging
    logging.basicConfig(
        level=getattr(logging, log_level),
        format=log_format,
        handlers=[
            logging.StreamHandler(),  # Console
            logging.FileHandler(  # File
                filename=log_file,
                encoding="utf-8"
            )
        ]
    )
    
    # Log startup information
    logger = logging.getLogger(__name__)
    logger.info(f"Logging initialized at level {log_level}")
    logger.info(f"Log file: {log_file}")

def get_logger(name: str) -> logging.Logger:
    """
    Get a logger with the specified name.
    
    Args:
        name: Logger name
    
    Returns:
        Logger instance
    """
    return logging.getLogger(name)

class TradeLogger:
    """
    Logger for trade-related events.
    Logs trades to a separate file for analysis.
    """
    def __init__(self, log_file: str = "logs/trades.log"):
        """
        Initialize trade logger.
        
        Args:
            log_file: Trade log file path
        """
        self.log_file = log_file
        self.logger = logging.getLogger("trades")
        
        # Create log directory if it doesn't exist
        log_path = Path(log_file)
        if log_path.parent != Path('.'):
            log_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Set up file handler
        handler = logging.FileHandler(log_file, encoding="utf-8")
        handler.setFormatter(logging.Formatter("%(message)s"))
        self.logger.addHandler(handler)
        self.logger.setLevel(logging.INFO)
        
        # Prevent propagation to root logger
        self.logger.propagate = False
    
    def log_signal(self, market: str, signal: Dict[str, Any]) -> None:
        """
        Log a trading signal.
        
        Args:
            market: Market symbol
            signal: Signal data
        """
        entry = {
            "type": "signal",
            "market": market,
            "timestamp": datetime.now().isoformat(),
            "data": signal
        }
        self.logger.info(json.dumps(entry))
    
    def log_order(self, market: str, order: Dict[str, Any]) -> None:
        """
        Log an order.
        
        Args:
            market: Market symbol
            order: Order data
        """
        entry = {
            "type": "order",
            "market": market,
            "timestamp": datetime.now().isoformat(),
            "data": order
        }
        self.logger.info(json.dumps(entry))
    
    def log_trade(self, market: str, trade: Dict[str, Any]) -> None:
        """
        Log a trade.
        
        Args:
            market: Market symbol
            trade: Trade data
        """
        entry = {
            "type": "trade",
            "market": market,
            "timestamp": datetime.now().isoformat(),
            "data": trade
        }
        self.logger.info(json.dumps(entry))
    
    def log_position(self, market: str, position: Dict[str, Any]) -> None:
        """
        Log a position.
        
        Args:
            market: Market symbol
            position: Position data
        """
        entry = {
            "type": "position",
            "market": market,
            "timestamp": datetime.now().isoformat(),
            "data": position
        }
        self.logger.info(json.dumps(entry))
    
    def log_pnl(self, market: str, pnl: Dict[str, Any]) -> None:
        """
        Log profit and loss.
        
        Args:
            market: Market symbol
            pnl: PnL data
        """
        entry = {
            "type": "pnl",
            "market": market,
            "timestamp": datetime.now().isoformat(),
            "data": pnl
        }
        self.logger.info(json.dumps(entry))

"""
Base strategy class for trading strategies.
"""

from abc import ABC, abstractmethod
from typing import Dict, Optional, List, Any
import logging

class BaseStrategy(ABC):
    """
    Abstract base class for all trading strategies.
    """
    def __init__(self, config: Dict):
        """
        Initialize the strategy.
        
        Args:
            config: Strategy configuration
        """
        self.config = config
        self.logger = logging.getLogger(self.__class__.__name__)
        
    @abstractmethod
    async def analyze(self, market_data: Dict) -> Dict:
        """
        Analyze market data and generate trading signals.
        
        Args:
            market_data: Market data dictionary
            
        Returns:
            Dictionary with analysis results and signals
        """
        pass
    
    @abstractmethod
    def should_enter(self, analysis: Dict) -> bool:
        """
        Determine if a position should be entered based on analysis.
        
        Args:
            analysis: Analysis results from analyze()
            
        Returns:
            True if a position should be entered, False otherwise
        """
        pass
    
    @abstractmethod
    def should_exit(self, analysis: Dict, position: Dict) -> bool:
        """
        Determine if a position should be exited based on analysis.
        
        Args:
            analysis: Analysis results from analyze()
            position: Current position information
            
        Returns:
            True if the position should be exited, False otherwise
        """
        pass
    
    @abstractmethod
    def calculate_position_size(self, analysis: Dict, account_info: Dict) -> float:
        """
        Calculate position size based on analysis and account information.
        
        Args:
            analysis: Analysis results from analyze()
            account_info: Account information
            
        Returns:
            Position size
        """
        pass
    
    @abstractmethod
    def calculate_entry_price(self, analysis: Dict) -> float:
        """
        Calculate entry price based on analysis.
        
        Args:
            analysis: Analysis results from analyze()
            
        Returns:
            Entry price
        """
        pass
    
    @abstractmethod
    def calculate_exit_targets(self, analysis: Dict, entry_price: float) -> Dict:
        """
        Calculate exit targets (stop loss, take profit) based on analysis.
        
        Args:
            analysis: Analysis results from analyze()
            entry_price: Entry price
            
        Returns:
            Dictionary with exit targets
        """
        pass

"""
Risk management module for the dYdX trading bot.
"""
import logging
from typing import Dict, Optional, Tuple
from .dydx_client import DydxClientWrapper
from . import config

logger = logging.getLogger(__name__)

class RiskManager:
    """
    Manages risk controls for trading operations.
    """

    def __init__(self, client: DydxClientWrapper,
                 max_position_size_usd: float = 1000.0,
                 max_drawdown_percent: float = 10.0,
                 max_daily_loss_usd: float = 500.0):
        """
        Initialize the risk manager.

        Args:
            client: dYdX client
            max_position_size_usd: Maximum position size in USD
            max_drawdown_percent: Maximum drawdown percentage
            max_daily_loss_usd: Maximum daily loss in USD
        """
        self.client = client
        self.max_position_size_usd = max_position_size_usd
        self.max_drawdown_percent = max_drawdown_percent
        self.max_daily_loss_usd = max_daily_loss_usd

        # Track daily P&L
        self.daily_pnl = 0.0
        self.initial_balance = 0.0

    def validate_position_size(self, position_size_usd: float, market: str) -> Tuple[bool, str]:
        """
        Validate if the position size is within risk limits.

        Args:
            position_size_usd: Requested position size in USD
            market: Market symbol

        Returns:
            Tuple[bool, str]: (is_valid, reason)
        """
        # Check against maximum position size
        if position_size_usd > self.max_position_size_usd:
            return False, f"Position size ${position_size_usd} exceeds maximum ${self.max_position_size_usd}"

        # Check available balance
        balance = self.get_available_balance()
        if balance is None:
            return False, "Unable to retrieve account balance"

        # Require at least 2x the position size in balance for margin
        required_balance = position_size_usd * 2
        if balance < required_balance:
            return False, f"Insufficient balance. Required: ${required_balance}, Available: ${balance}"

        return True, "Position size validated"

    def validate_daily_loss(self, potential_loss: float) -> Tuple[bool, str]:
        """
        Validate if the potential loss would exceed daily limits.

        Args:
            potential_loss: Potential loss amount in USD

        Returns:
            Tuple[bool, str]: (is_valid, reason)
        """
        projected_daily_loss = self.daily_pnl + potential_loss

        if abs(projected_daily_loss) > self.max_daily_loss_usd:
            return False, f"Daily loss limit would be exceeded. Current: ${self.daily_pnl}, Potential: ${projected_daily_loss}"

        return True, "Daily loss within limits"

    def validate_drawdown(self) -> Tuple[bool, str]:
        """
        Validate if current drawdown is within limits.

        Returns:
            Tuple[bool, str]: (is_valid, reason)
        """
        if self.initial_balance == 0:
            self.initial_balance = self.get_available_balance() or 0

        current_balance = self.get_available_balance()
        if current_balance is None or self.initial_balance == 0:
            return True, "Unable to calculate drawdown"

        drawdown_percent = ((self.initial_balance - current_balance) / self.initial_balance) * 100

        if drawdown_percent > self.max_drawdown_percent:
            return False, f"Drawdown {drawdown_percent:.2f}% exceeds maximum {self.max_drawdown_percent}%"

        return True, f"Drawdown {drawdown_percent:.2f}% within limits"

    def get_available_balance(self) -> Optional[float]:
        """
        Get available balance from the account.

        Returns:
            Optional[float]: Available balance in USD or None if error
        """
        try:
            # Get account info using wrapper
            account_info = self.client.get_account_info()

            if account_info and 'equity' in account_info:
                return float(account_info['equity'])
            elif account_info and 'freeCollateral' in account_info:
                return float(account_info['freeCollateral'])
            else:
                logger.warning(f"Could not determine balance from account info: {account_info}")
                return None

        except Exception as e:
            logger.error(f"Failed to get account balance: {str(e)}")
            return None

    def update_daily_pnl(self, pnl: float):
        """
        Update the daily P&L tracking.

        Args:
            pnl: Profit/Loss amount to add
        """
        self.daily_pnl += pnl
        logger.info(f"Updated daily P&L: ${self.daily_pnl:.2f}")

    def reset_daily_pnl(self):
        """
        Reset daily P&L tracking (call at start of new trading day).
        """
        self.daily_pnl = 0.0
        logger.info("Reset daily P&L tracking")

    def check_circuit_breaker(self) -> Tuple[bool, str]:
        """
        Check if circuit breaker should be triggered.

        Returns:
            Tuple[bool, str]: (should_stop, reason)
        """
        # Check daily loss limit
        if abs(self.daily_pnl) > self.max_daily_loss_usd:
            return True, f"Daily loss limit exceeded: ${self.daily_pnl:.2f}"

        # Check drawdown limit
        is_valid, reason = self.validate_drawdown()
        if not is_valid:
            return True, f"Drawdown limit exceeded: {reason}"

        return False, "All risk checks passed"

    def get_risk_summary(self) -> Dict:
        """
        Get a summary of current risk metrics.

        Returns:
            Dict: Risk summary
        """
        balance = self.get_available_balance()
        drawdown_valid, drawdown_msg = self.validate_drawdown()

        return {
            "available_balance": balance,
            "daily_pnl": self.daily_pnl,
            "max_daily_loss": self.max_daily_loss_usd,
            "max_position_size": self.max_position_size_usd,
            "max_drawdown_percent": self.max_drawdown_percent,
            "drawdown_status": drawdown_msg,
            "circuit_breaker_active": not drawdown_valid or abs(self.daily_pnl) > self.max_daily_loss_usd
        }

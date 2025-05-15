"""
Order execution and management module.
"""
import logging
import time
from typing import Dict, Optional, List

from dydx_v4_python.clients import CompositeClient
import config

logger = logging.getLogger(__name__)

class OrderManager:
    def __init__(self, client: CompositeClient, market: str = config.DEFAULT_MARKET,
                 position_size_usd: float = config.DEFAULT_POSITION_SIZE_USD,
                 simulation_mode: bool = True):
        """
        Initialize the order manager.

        Args:
            client: Initialized dYdX client
            market: Market symbol (e.g., "ETH-USD")
            position_size_usd: Position size in USD
            simulation_mode: If True, don't place actual orders
        """
        self.client = client
        self.market = market
        self.position_size_usd = position_size_usd
        self.simulation_mode = simulation_mode
        self.active_position = None

    def place_market_order(self, side: str, price: float) -> Dict:
        """
        Place a market order.

        Args:
            side: Order side ("BUY" or "SELL")
            price: Current market price for calculating size

        Returns:
            Dict: Order information
        """
        # Calculate order size based on position size in USD and current price
        size = self.position_size_usd / price

        # Round size to appropriate precision
        size = round(size, 4)  # Adjust precision as needed for the specific market

        order_info = {
            "market": self.market,
            "side": side,
            "size": size,
            "price": price,
            "type": "MARKET",
            "time_in_force": "IOC",  # Immediate or Cancel
            "post_only": False,
            "reduce_only": False
        }

        if self.simulation_mode:
            logger.info(f"SIMULATION: Would place {side} order for {size} {self.market} @ {price}")
            order_response = {
                "order_id": f"sim_{int(time.time())}",
                "status": "FILLED",
                "simulation": True,
                **order_info
            }
        else:
            try:
                # Place the order using the dYdX client
                order_response = self.client.place_order(
                    market=self.market,
                    side=side,
                    type="MARKET",
                    size=str(size),
                    price=str(price),
                    time_in_force="IOC",
                    post_only=False,
                    reduce_only=False
                )

                logger.info(f"Placed {side} order for {size} {self.market} @ {price}")

            except Exception as e:
                logger.error(f"Failed to place order: {str(e)}")
                order_response = {
                    "status": "FAILED",
                    "error": str(e),
                    **order_info
                }

        return order_response

    def open_long_position(self, entry_price: float, stop_loss: float, take_profit: float) -> Dict:
        """
        Open a long position with stop loss and take profit.

        Args:
            entry_price: Entry price
            stop_loss: Stop loss price
            take_profit: Take profit price

        Returns:
            Dict: Position information
        """
        # Place market buy order
        order_response = self.place_market_order("BUY", entry_price)

        if order_response.get("status") == "FILLED" or self.simulation_mode:
            # Create position object
            position = {
                "market": self.market,
                "side": "LONG",
                "entry_price": entry_price,
                "size": order_response.get("size", 0),
                "stop_loss": stop_loss,
                "take_profit": take_profit,
                "status": "OPEN",
                "order_id": order_response.get("order_id", ""),
                "opened_at": time.time()
            }

            self.active_position = position
            logger.info(f"Opened LONG position: {position}")

            return position
        else:
            logger.error(f"Failed to open position: {order_response}")
            return {"status": "FAILED", "error": "Order not filled"}

    def close_position(self, reason: str) -> Dict:
        """
        Close the active position.

        Args:
            reason: Reason for closing the position (e.g., "stop_loss", "take_profit")

        Returns:
            Dict: Close position information
        """
        if not self.active_position:
            logger.warning("No active position to close")
            return {"status": "FAILED", "error": "No active position"}

        current_price = self.get_current_price()

        # Place market sell order to close the position
        order_response = self.place_market_order("SELL", current_price)

        if order_response.get("status") == "FILLED" or self.simulation_mode:
            # Calculate profit/loss
            if self.active_position["side"] == "LONG":
                pnl = (current_price - self.active_position["entry_price"]) * self.active_position["size"]
            else:
                pnl = (self.active_position["entry_price"] - current_price) * self.active_position["size"]

            # Update position status
            closed_position = {
                **self.active_position,
                "status": "CLOSED",
                "exit_price": current_price,
                "exit_reason": reason,
                "pnl": pnl,
                "pnl_percent": (pnl / self.position_size_usd) * 100,
                "closed_at": time.time(),
                "duration": time.time() - self.active_position["opened_at"]
            }

            logger.info(f"Closed position due to {reason}: {closed_position}")

            # Clear active position
            self.active_position = None

            return closed_position
        else:
            logger.error(f"Failed to close position: {order_response}")
            return {"status": "FAILED", "error": "Order not filled"}

    def check_exit_conditions(self) -> Optional[str]:
        """
        Check if exit conditions (stop loss or take profit) are met.

        Returns:
            Optional[str]: Exit reason or None if no exit condition is met
        """
        if not self.active_position:
            return None

        current_price = self.get_current_price()

        if self.active_position["side"] == "LONG":
            # Check stop loss
            if current_price <= self.active_position["stop_loss"]:
                return "stop_loss"

            # Check take profit
            if current_price >= self.active_position["take_profit"]:
                return "take_profit"

        return None

    def get_current_price(self) -> float:
        """
        Get the current price for the market.

        Returns:
            float: Current price
        """
        try:
            ticker = self.client.get_ticker(market=self.market)
            return float(ticker['price'])
        except Exception as e:
            logger.error(f"Failed to get current price: {str(e)}")
            # Return a fallback price if available
            return self.active_position["entry_price"] if self.active_position else 0.0

    def get_positions(self) -> List[Dict]:
        """
        Get all open positions.

        Returns:
            List[Dict]: List of open positions
        """
        if self.simulation_mode:
            return [self.active_position] if self.active_position else []

        try:
            positions = self.client.get_positions()
            return positions
        except Exception as e:
            logger.error(f"Failed to get positions: {str(e)}")
            return []

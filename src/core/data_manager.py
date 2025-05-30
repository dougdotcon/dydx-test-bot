"""
Data persistence manager for the dYdX trading bot.
"""
import json
import os
import logging
from datetime import datetime
from typing import Dict, List, Optional
import pandas as pd

logger = logging.getLogger(__name__)

class DataManager:
    """
    Manages data persistence for trades, positions, and bot state.
    """
    
    def __init__(self, data_dir: str = None):
        """
        Initialize the data manager.
        
        Args:
            data_dir: Directory to store data files
        """
        if data_dir is None:
            # Default to data directory relative to project root
            self.data_dir = os.path.join(os.path.dirname(__file__), "..", "..", "data")
        else:
            self.data_dir = data_dir
        
        # Ensure data directory exists
        os.makedirs(self.data_dir, exist_ok=True)
        
        # File paths
        self.trades_file = os.path.join(self.data_dir, "trades.json")
        self.positions_file = os.path.join(self.data_dir, "positions.json")
        self.bot_state_file = os.path.join(self.data_dir, "bot_state.json")
        self.performance_file = os.path.join(self.data_dir, "performance.json")
    
    def save_trade(self, trade_data: Dict):
        """
        Save a completed trade to the trades file.
        
        Args:
            trade_data: Trade information dictionary
        """
        try:
            # Add timestamp if not present
            if 'timestamp' not in trade_data:
                trade_data['timestamp'] = datetime.now().isoformat()
            
            # Load existing trades
            trades = self.load_trades()
            
            # Add new trade
            trades.append(trade_data)
            
            # Save back to file
            with open(self.trades_file, 'w') as f:
                json.dump(trades, f, indent=2, default=str)
            
            logger.info(f"Saved trade: {trade_data.get('market', 'Unknown')} - {trade_data.get('side', 'Unknown')}")
            
        except Exception as e:
            logger.error(f"Failed to save trade: {str(e)}")
    
    def load_trades(self) -> List[Dict]:
        """
        Load all trades from the trades file.
        
        Returns:
            List[Dict]: List of trade records
        """
        try:
            if os.path.exists(self.trades_file):
                with open(self.trades_file, 'r') as f:
                    return json.load(f)
            return []
        except Exception as e:
            logger.error(f"Failed to load trades: {str(e)}")
            return []
    
    def save_position(self, position_data: Dict):
        """
        Save position data.
        
        Args:
            position_data: Position information dictionary
        """
        try:
            # Add timestamp if not present
            if 'timestamp' not in position_data:
                position_data['timestamp'] = datetime.now().isoformat()
            
            # Load existing positions
            positions = self.load_positions()
            
            # Add or update position
            position_id = position_data.get('order_id', f"pos_{len(positions)}")
            
            # Find existing position or add new one
            updated = False
            for i, pos in enumerate(positions):
                if pos.get('order_id') == position_id:
                    positions[i] = position_data
                    updated = True
                    break
            
            if not updated:
                positions.append(position_data)
            
            # Save back to file
            with open(self.positions_file, 'w') as f:
                json.dump(positions, f, indent=2, default=str)
            
            logger.debug(f"Saved position: {position_id}")
            
        except Exception as e:
            logger.error(f"Failed to save position: {str(e)}")
    
    def load_positions(self) -> List[Dict]:
        """
        Load all positions from the positions file.
        
        Returns:
            List[Dict]: List of position records
        """
        try:
            if os.path.exists(self.positions_file):
                with open(self.positions_file, 'r') as f:
                    return json.load(f)
            return []
        except Exception as e:
            logger.error(f"Failed to load positions: {str(e)}")
            return []
    
    def save_bot_state(self, state_data: Dict):
        """
        Save bot state information.
        
        Args:
            state_data: Bot state dictionary
        """
        try:
            state_data['timestamp'] = datetime.now().isoformat()
            
            with open(self.bot_state_file, 'w') as f:
                json.dump(state_data, f, indent=2, default=str)
            
            logger.debug("Saved bot state")
            
        except Exception as e:
            logger.error(f"Failed to save bot state: {str(e)}")
    
    def load_bot_state(self) -> Optional[Dict]:
        """
        Load bot state information.
        
        Returns:
            Optional[Dict]: Bot state or None if not found
        """
        try:
            if os.path.exists(self.bot_state_file):
                with open(self.bot_state_file, 'r') as f:
                    return json.load(f)
            return None
        except Exception as e:
            logger.error(f"Failed to load bot state: {str(e)}")
            return None
    
    def calculate_performance_metrics(self) -> Dict:
        """
        Calculate performance metrics from trade history.
        
        Returns:
            Dict: Performance metrics
        """
        trades = self.load_trades()
        
        if not trades:
            return {
                "total_trades": 0,
                "total_pnl": 0.0,
                "win_rate": 0.0,
                "avg_win": 0.0,
                "avg_loss": 0.0,
                "profit_factor": 0.0,
                "max_drawdown": 0.0
            }
        
        # Calculate basic metrics
        total_trades = len(trades)
        total_pnl = sum(trade.get('pnl', 0) for trade in trades)
        
        # Separate wins and losses
        wins = [trade for trade in trades if trade.get('pnl', 0) > 0]
        losses = [trade for trade in trades if trade.get('pnl', 0) < 0]
        
        win_rate = len(wins) / total_trades * 100 if total_trades > 0 else 0
        avg_win = sum(trade.get('pnl', 0) for trade in wins) / len(wins) if wins else 0
        avg_loss = sum(trade.get('pnl', 0) for trade in losses) / len(losses) if losses else 0
        
        # Profit factor
        gross_profit = sum(trade.get('pnl', 0) for trade in wins)
        gross_loss = abs(sum(trade.get('pnl', 0) for trade in losses))
        profit_factor = gross_profit / gross_loss if gross_loss > 0 else float('inf')
        
        # Calculate drawdown
        running_pnl = 0
        peak = 0
        max_drawdown = 0
        
        for trade in trades:
            running_pnl += trade.get('pnl', 0)
            if running_pnl > peak:
                peak = running_pnl
            drawdown = peak - running_pnl
            if drawdown > max_drawdown:
                max_drawdown = drawdown
        
        metrics = {
            "total_trades": total_trades,
            "total_pnl": total_pnl,
            "win_rate": win_rate,
            "avg_win": avg_win,
            "avg_loss": avg_loss,
            "profit_factor": profit_factor,
            "max_drawdown": max_drawdown,
            "gross_profit": gross_profit,
            "gross_loss": gross_loss,
            "winning_trades": len(wins),
            "losing_trades": len(losses)
        }
        
        # Save performance metrics
        try:
            with open(self.performance_file, 'w') as f:
                json.dump(metrics, f, indent=2, default=str)
        except Exception as e:
            logger.error(f"Failed to save performance metrics: {str(e)}")
        
        return metrics
    
    def export_trades_to_csv(self, filename: str = None) -> str:
        """
        Export trades to CSV file.
        
        Args:
            filename: Output filename (optional)
            
        Returns:
            str: Path to the exported file
        """
        if filename is None:
            filename = f"trades_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        
        filepath = os.path.join(self.data_dir, filename)
        
        try:
            trades = self.load_trades()
            if trades:
                df = pd.DataFrame(trades)
                df.to_csv(filepath, index=False)
                logger.info(f"Exported {len(trades)} trades to {filepath}")
            else:
                logger.warning("No trades to export")
            
            return filepath
            
        except Exception as e:
            logger.error(f"Failed to export trades to CSV: {str(e)}")
            return ""
    
    def cleanup_old_data(self, days_to_keep: int = 30):
        """
        Clean up old data files (keep only recent data).
        
        Args:
            days_to_keep: Number of days of data to keep
        """
        try:
            cutoff_date = datetime.now().timestamp() - (days_to_keep * 24 * 60 * 60)
            
            # Clean trades
            trades = self.load_trades()
            recent_trades = []
            for trade in trades:
                trade_time = datetime.fromisoformat(trade.get('timestamp', '1970-01-01')).timestamp()
                if trade_time > cutoff_date:
                    recent_trades.append(trade)
            
            if len(recent_trades) != len(trades):
                with open(self.trades_file, 'w') as f:
                    json.dump(recent_trades, f, indent=2, default=str)
                logger.info(f"Cleaned up trades: kept {len(recent_trades)} out of {len(trades)}")
            
        except Exception as e:
            logger.error(f"Failed to cleanup old data: {str(e)}")

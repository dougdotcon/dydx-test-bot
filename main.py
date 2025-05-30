"""
Main entry point for the dYdX trading bot.
"""
import sys
import os

# Add src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.cli.cli import cli

if __name__ == '__main__':
    cli()

#!/usr/bin/env python3
"""
Basic test to verify the bot structure and imports are working.
"""
import sys
import os

# Add src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_imports():
    """Test that all modules can be imported successfully."""
    print("Testing imports...")
    
    try:
        # Test core modules
        from src.core import config
        print("✅ config imported successfully")
        
        from src.core.auth import create_client, get_account_info
        print("✅ auth imported successfully")
        
        from src.core.market_data import MarketData
        print("✅ market_data imported successfully")
        
        from src.core.order_manager import OrderManager
        print("✅ order_manager imported successfully")
        
        from src.core.risk_manager import RiskManager
        print("✅ risk_manager imported successfully")
        
        from src.core.data_manager import DataManager
        print("✅ data_manager imported successfully")
        
        # Test strategies
        from src.strategies.strategy import BreakoutStrategy
        print("✅ strategy imported successfully")
        
        # Test CLI
        from src.cli.cli import cli
        print("✅ cli imported successfully")
        
        print("\n🎉 All imports successful!")
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

def test_config():
    """Test configuration values."""
    print("\nTesting configuration...")
    
    try:
        from src.core import config
        
        print(f"Network: {config.NETWORK}")
        print(f"Chain ID: {config.CHAIN_ID}")
        print(f"Default Market: {config.DEFAULT_MARKET}")
        print(f"Default Timeframe: {config.DEFAULT_TIMEFRAME}")
        print(f"Log File: {config.LOG_FILE}")
        
        # Check if log directory exists
        log_dir = os.path.dirname(config.LOG_FILE)
        if os.path.exists(log_dir):
            print(f"✅ Log directory exists: {log_dir}")
        else:
            print(f"⚠️ Log directory does not exist: {log_dir}")
        
        return True
        
    except Exception as e:
        print(f"❌ Configuration test failed: {e}")
        return False

def test_data_manager():
    """Test data manager functionality."""
    print("\nTesting data manager...")
    
    try:
        from src.core.data_manager import DataManager
        
        # Initialize data manager
        dm = DataManager()
        
        # Test saving a sample trade
        sample_trade = {
            "market": "ETH-USD",
            "side": "LONG",
            "entry_price": 2000.0,
            "exit_price": 2100.0,
            "size": 0.1,
            "pnl": 10.0,
            "pnl_percent": 5.0,
            "status": "CLOSED",
            "exit_reason": "take_profit"
        }
        
        dm.save_trade(sample_trade)
        print("✅ Sample trade saved")
        
        # Test loading trades
        trades = dm.load_trades()
        print(f"✅ Loaded {len(trades)} trades")
        
        # Test performance metrics
        metrics = dm.calculate_performance_metrics()
        print(f"✅ Performance metrics calculated: {metrics['total_trades']} trades")
        
        return True
        
    except Exception as e:
        print(f"❌ Data manager test failed: {e}")
        return False

def test_directory_structure():
    """Test that all required directories exist."""
    print("\nTesting directory structure...")
    
    required_dirs = [
        "src",
        "src/core",
        "src/strategies", 
        "src/utils",
        "src/cli",
        "tests",
        "docs",
        "config",
        "logs",
        "data"
    ]
    
    all_exist = True
    for dir_path in required_dirs:
        if os.path.exists(dir_path):
            print(f"✅ {dir_path}")
        else:
            print(f"❌ {dir_path} - missing")
            all_exist = False
    
    return all_exist

def main():
    """Run all tests."""
    print("🚀 Starting dYdX Trading Bot Tests\n")
    
    tests = [
        ("Directory Structure", test_directory_structure),
        ("Imports", test_imports),
        ("Configuration", test_config),
        ("Data Manager", test_data_manager)
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\n{'='*50}")
        print(f"Running {test_name} Test")
        print('='*50)
        
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} test crashed: {e}")
            results.append((test_name, False))
    
    # Summary
    print(f"\n{'='*50}")
    print("TEST SUMMARY")
    print('='*50)
    
    passed = 0
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name}: {status}")
        if result:
            passed += 1
    
    print(f"\nPassed: {passed}/{len(results)}")
    
    if passed == len(results):
        print("\n🎉 All tests passed! Bot structure is ready.")
        return 0
    else:
        print(f"\n⚠️ {len(results) - passed} test(s) failed. Please fix issues before proceeding.")
        return 1

if __name__ == "__main__":
    sys.exit(main())

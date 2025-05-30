#!/usr/bin/env python3
"""
Test script to verify the bot structure without dYdX dependencies.
"""
import sys
import os

# Add src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_basic_structure():
    """Test basic structure and imports without dYdX client."""
    print("Testing basic structure...")
    
    try:
        # Test core config
        from src.core import config
        print("✅ config imported successfully")
        
        # Test data manager (no dYdX dependency)
        from src.core.data_manager import DataManager
        print("✅ data_manager imported successfully")
        
        # Test basic functionality
        dm = DataManager()
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
        trades = dm.load_trades()
        metrics = dm.calculate_performance_metrics()
        
        print(f"✅ Data manager working: {len(trades)} trades, total P&L: ${metrics['total_pnl']:.2f}")
        
        return True
        
    except Exception as e:
        print(f"❌ Structure test failed: {e}")
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

def test_config_values():
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

def main():
    """Run all tests."""
    print("🚀 Testing dYdX Trading Bot Structure\n")
    
    tests = [
        ("Directory Structure", test_directory_structure),
        ("Basic Structure", test_basic_structure),
        ("Configuration", test_config_values)
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
        print("\n🎉 All structure tests passed! Bot organization is ready.")
        print("\n📋 NEXT STEPS:")
        print("1. Fix dYdX client imports")
        print("2. Test with actual dYdX connection")
        print("3. Run full integration tests")
        return 0
    else:
        print(f"\n⚠️ {len(results) - passed} test(s) failed. Please fix issues before proceeding.")
        return 1

if __name__ == "__main__":
    sys.exit(main())

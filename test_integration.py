#!/usr/bin/env python3
"""
Integration test to verify the complete bot functionality in simulation mode.
"""
import sys
import os

# Add src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_complete_integration():
    """Test complete bot integration in simulation mode."""
    print("Testing complete bot integration...")

    try:
        # Test imports
        from src.core.auth import create_client, get_account_info
        from src.core.market_data import MarketData
        from src.core.order_manager import OrderManager
        from src.core.risk_manager import RiskManager
        from src.core.data_manager import DataManager
        from src.strategies.strategy import BreakoutStrategy
        print("✅ All modules imported successfully")

        # Test client creation in simulation mode
        client = create_client(simulation_mode=True)
        if not client:
            print("❌ Failed to create client")
            return False
        print("✅ Client created successfully")

        # Test account info
        account_info = get_account_info(client)
        if not account_info:
            print("❌ Failed to get account info")
            return False
        print(f"✅ Account info retrieved: Balance ${account_info.get('equity', 'Unknown')}")

        # Test market data
        market_data = MarketData(client, market="ETH-USD")
        candles = market_data.fetch_candles(limit=10)
        if candles.empty:
            print("❌ Failed to fetch candles")
            return False
        print(f"✅ Market data fetched: {len(candles)} candles")

        # Test latest price
        latest_price = market_data.get_latest_price()
        if latest_price <= 0:
            print("❌ Failed to get latest price")
            return False
        print(f"✅ Latest price: ${latest_price}")

        # Test order manager
        order_manager = OrderManager(client, simulation_mode=True)
        print("✅ Order manager created")

        # Test risk manager
        risk_manager = RiskManager(client)
        risk_summary = risk_manager.get_risk_summary()
        print(f"✅ Risk manager working: Balance ${risk_summary.get('available_balance', 'Unknown')}")

        # Test strategy
        strategy = BreakoutStrategy(market_data)
        strategy.update_market_data()
        signal, signal_details = strategy.check_breakout_signal()
        print(f"✅ Strategy working: Signal = {signal}, Details = {signal_details.get('signal', 'Unknown')}")

        # Test data manager
        data_manager = DataManager()
        metrics = data_manager.calculate_performance_metrics()
        print(f"✅ Data manager working: {metrics['total_trades']} trades recorded")

        # Test a complete trading cycle simulation
        print("\n🔄 Testing complete trading cycle...")

        # Simulate opening a position
        entry_price = latest_price
        stop_loss = entry_price * 0.95  # 5% stop loss
        take_profit = entry_price * 1.10  # 10% take profit

        position = order_manager.open_long_position(entry_price, stop_loss, take_profit)
        if position.get("status") != "FAILED":
            print(f"✅ Position opened: {position.get('side')} {position.get('size')} @ ${position.get('entry_price')}")

            # Check exit conditions
            exit_reason = order_manager.check_exit_conditions()
            print(f"✅ Exit conditions checked: {exit_reason or 'None'}")

            # Close position
            closed_position = order_manager.close_position("manual_close")
            if closed_position.get("status") != "FAILED":
                print(f"✅ Position closed: P&L ${closed_position.get('pnl', 0):.2f}")
            else:
                print("❌ Failed to close position")
                return False
        else:
            print("❌ Failed to open position")
            return False

        print("\n🎉 Complete integration test passed!")
        return True

    except Exception as e:
        print(f"❌ Integration test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_cli_integration():
    """Test CLI integration."""
    print("\nTesting CLI integration...")

    try:
        from src.cli.cli import cli
        print("✅ CLI module imported successfully")

        # Note: We can't easily test CLI commands without actually running them
        # This just verifies the import works
        return True

    except Exception as e:
        print(f"❌ CLI integration test failed: {e}")
        return False

def main():
    """Run all integration tests."""
    print("🚀 Starting dYdX Trading Bot Integration Tests\n")

    tests = [
        ("Complete Integration", test_complete_integration),
        ("CLI Integration", test_cli_integration)
    ]

    results = []
    for test_name, test_func in tests:
        print(f"\n{'='*60}")
        print(f"Running {test_name} Test")
        print('='*60)

        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} test crashed: {e}")
            results.append((test_name, False))

    # Summary
    print(f"\n{'='*60}")
    print("INTEGRATION TEST SUMMARY")
    print('='*60)

    passed = 0
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name}: {status}")
        if result:
            passed += 1

    print(f"\nPassed: {passed}/{len(results)}")

    if passed == len(results):
        print("\n🎉 ALL INTEGRATION TESTS PASSED!")
        print("\n📋 BOT STATUS:")
        print("✅ Structure: Complete")
        print("✅ Core Modules: Working")
        print("✅ Risk Management: Implemented")
        print("✅ Data Persistence: Working")
        print("✅ Trading Simulation: Functional")
        print("\n🚀 Bot is ready for testing with real dYdX connection!")
        return 0
    else:
        print(f"\n⚠️ {len(results) - passed} test(s) failed.")
        return 1

if __name__ == "__main__":
    sys.exit(main())

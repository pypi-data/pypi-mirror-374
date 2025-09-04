#!/usr/bin/env python3
"""
Main test runner for xSystem.

Company: eXonware.com
Author: Eng. Muhammad AlShehri
Email: connect@exonware.com
Version: 0.0.1
Generation Date: August 31, 2025
"""

import sys
import subprocess
from pathlib import Path


def run_all_tests():
    """Run all tests (core, unit, integration, performance) in sequence."""
    
    test_categories = ['core', 'unit', 'integration', 'performance']
    results = {}
    
    print("🚀 xSystem Test Suite")
    print("=" * 50)
    
    for category in test_categories:
        print(f"\n📁 Running {category.upper()} tests...")
        print("-" * 30)
        
        runner_path = Path(__file__).parent / category / "runner.py"
        if runner_path.exists():
            try:
                result = subprocess.run([sys.executable, str(runner_path)], 
                                      capture_output=False)
                results[category] = result.returncode
                if result.returncode == 0:
                    print(f"✅ {category.upper()} tests PASSED")
                else:
                    print(f"❌ {category.upper()} tests FAILED")
            except Exception as e:
                print(f"❌ Error running {category} tests: {e}")
                results[category] = 1
        else:
            print(f"⚠️  No runner found for {category} tests")
            results[category] = 0
    
    # Summary
    print(f"\n{'='*50}")
    print("📊 TEST SUMMARY")
    print(f"{'='*50}")
    
    all_passed = True
    for category, result in results.items():
        status = "✅ PASSED" if result == 0 else "❌ FAILED"
        print(f"{category.upper():<15}: {status}")
        if result != 0:
            all_passed = False
    
    print(f"\nOverall: {'🎉 ALL TESTS PASSED' if all_passed else '💥 SOME TESTS FAILED'}")
    
    return 0 if all_passed else 1


def run_specific_category(category: str):
    """Run tests for a specific category."""
    
    runner_path = Path(__file__).parent / category / "runner.py"
    
    if not runner_path.exists():
        print(f"❌ No runner found for category: {category}")
        print(f"Available categories: core, unit, integration, performance")
        return 1
    
    print(f"🚀 Running {category.upper()} tests...")
    print("=" * 50)
    
    try:
        result = subprocess.run([sys.executable, str(runner_path)], 
                              capture_output=False)
        return result.returncode
    except Exception as e:
        print(f"❌ Error running {category} tests: {e}")
        return 1


def run_unit_category(unit_category: str):
    """Run specific unit test category."""
    
    unit_runner = Path(__file__).parent / "unit" / "runner.py"
    
    if not unit_runner.exists():
        print(f"❌ Unit test runner not found")
        return 1
    
    print(f"🚀 Running unit category: {unit_category}")
    print("=" * 50)
    
    try:
        result = subprocess.run([sys.executable, str(unit_runner), unit_category], 
                              capture_output=False)
        return result.returncode
    except Exception as e:
        print(f"❌ Error running unit category {unit_category}: {e}")
        return 1


def run_with_pytest(category: str = None, marker: str = None):
    """Run tests using pytest directly."""
    
    cmd = [sys.executable, "-m", "pytest", "tests/", "-v"]
    
    if category:
        cmd.extend([f"tests/{category}/"])
    
    if marker:
        cmd.extend(["-m", marker])
    
    print(f"🚀 Running pytest: {' '.join(cmd)}")
    print("=" * 50)
    
    try:
        result = subprocess.run(cmd, capture_output=False)
        return result.returncode
    except Exception as e:
        print(f"❌ Error running pytest: {e}")
        return 1


def show_help():
    """Show help information."""
    print("""
🚀 xSystem Test Runner

Usage:
  python runner.py [command] [options]

Commands:
  all                    Run all tests (default)
  core                   Run core tests only
  unit                   Run unit tests only
  integration            Run integration tests only
  performance            Run performance tests only
  pytest [category]      Run tests using pytest directly
  unit-category <name>   Run specific unit test category

Examples:
  python runner.py                    # Run all tests
  python runner.py core              # Run core tests only
  python runner.py pytest unit       # Run unit tests with pytest
  python runner.py pytest -m xsystem_security  # Run security tests
  python runner.py unit-category security_tests  # Run security unit tests

Markers:
  -m xsystem_core         Core functionality tests
  -m xsystem_unit         Unit tests
  -m xsystem_integration  Integration tests
  -m xsystem_security     Security tests
  -m xsystem_serialization Serialization tests
  -m xsystem_performance  Performance tests
""")


if __name__ == "__main__":
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
        
        if command == "help" or command == "--help" or command == "-h":
            show_help()
            exit_code = 0
        elif command == "pytest":
            category = sys.argv[2] if len(sys.argv) > 2 else None
            marker = None
            if len(sys.argv) > 3 and sys.argv[2] == "-m":
                marker = sys.argv[3]
                category = None
            exit_code = run_with_pytest(category, marker)
        elif command == "unit" and len(sys.argv) > 2:
            # Run specific unit category
            exit_code = run_unit_category(sys.argv[2])
        elif command in ["core", "unit", "integration", "performance"]:
            # Run specific category
            exit_code = run_specific_category(command)
        else:
            print(f"❌ Unknown command: {command}")
            show_help()
            exit_code = 1
    else:
        # Run all tests
        exit_code = run_all_tests()
    
    sys.exit(exit_code)

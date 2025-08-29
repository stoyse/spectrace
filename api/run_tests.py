#!/usr/bin/env python3
"""
Fast test runner for Spectrace API

Runs all tests quickly using mocks instead of actual LLM calls.
"""

import subprocess
import sys
import time

def main():
    """Run tests and show performance"""
    print("Running Spectrace API Tests...")
    print("=" * 50)
    
    start_time = time.time()
    
    # Run pytest with all test files
    result = subprocess.run([
        sys.executable, "-m", "pytest", 
        "tests/", 
        "-v",
        "--tb=short",
        "--color=yes"
    ], capture_output=False)
    
    end_time = time.time()
    duration = end_time - start_time
    
    print("=" * 50)
    if result.returncode == 0:
        print(f"All tests passed in {duration:.2f} seconds!")
        print("Fast & efficient - no LLM calls needed!")
    else:
        print(f"Tests failed after {duration:.2f} seconds")
        sys.exit(1)

if __name__ == "__main__":
    main()
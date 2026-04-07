#!/usr/bin/env python3
"""
Simple test runner for Copilot Real-Time Answers tests.
Run with: python run_tests.py
"""

import sys
import subprocess

if __name__ == "__main__":
    # Run pytest with the test file
    result = subprocess.run(
        [sys.executable, "-m", "pytest", "tests/test_copilot_realtime.py", "-v", "--tb=short"],
        cwd=".",
    )
    sys.exit(result.returncode)

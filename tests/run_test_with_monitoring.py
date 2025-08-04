#!/usr/bin/env python3
"""Enhanced test runner with detailed error monitoring"""

import sys
import os
import traceback
import logging
from datetime import datetime

# Configure detailed logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(f'test_run_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log'),
        logging.StreamHandler(sys.stdout)
    ]
)

# Add src to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Enable all warnings
import warnings
warnings.filterwarnings("default")

# Import the test module
try:
    from test_slack_post import test_basic_slack_post, test_full_workflow, test_with_live_data
    
    print("=" * 60)
    print("Running AI News Summarizer Tests with Full Monitoring")
    print("=" * 60)
    
    # Test 1: Basic connection
    print("\n[TEST 1] Basic Slack Connection")
    print("-" * 40)
    try:
        test_basic_slack_post()
    except Exception as e:
        print(f"ERROR in basic test: {e}")
        traceback.print_exc()
    
    # Test 2: Full workflow
    print("\n[TEST 2] Full Workflow with Sample Data")
    print("-" * 40)
    try:
        test_full_workflow()
    except Exception as e:
        print(f"ERROR in full workflow: {e}")
        traceback.print_exc()
    
    # Test 3: Live data
    print("\n[TEST 3] Live RSS Data Test")
    print("-" * 40)
    try:
        test_with_live_data()
    except Exception as e:
        print(f"ERROR in live data test: {e}")
        traceback.print_exc()
    
    print("\n" + "=" * 60)
    print("All tests completed. Check logs for details.")
    
except ImportError as e:
    print(f"Import error: {e}")
    traceback.print_exc()
except Exception as e:
    print(f"Unexpected error: {e}")
    traceback.print_exc()
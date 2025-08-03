#!/usr/bin/env python3
"""Quick digest test - sends immediately without prompts"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from test_digest_format import test_minimal_digest

if __name__ == "__main__":
    print("Sending minimal digest test...")
    test_minimal_digest()
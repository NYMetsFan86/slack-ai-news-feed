#!/usr/bin/env python3
"""Test the AI news digest locally to debug errors"""

import os
import sys
from pathlib import Path

# Add the src directory to the Python path
sys.path.insert(0, str(Path(__file__).parent))

# Set up environment variables
os.environ['ENVIRONMENT'] = 'development'

# Import after setting up the path
from src.main_digest import main_function_digest
from cloudevents.http import CloudEvent

def test_digest():
    """Test the digest function locally"""
    print("🧪 Testing AI News Digest locally...")
    
    # Create a mock cloud event
    attributes = {
        "type": "google.cloud.pubsub.topic.v1.messagePublished",
        "source": "local-test",
    }
    data = {"message": {"data": "test"}}
    
    test_event = CloudEvent(attributes, data)
    
    try:
        # Call the main function
        main_function_digest(test_event)
        print("✅ Test completed successfully!")
    except Exception as e:
        print(f"❌ Error during test: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_digest()
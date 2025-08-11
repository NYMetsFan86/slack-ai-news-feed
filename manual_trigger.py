#!/usr/bin/env python3
"""Manually trigger a digest to test the deployment"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Set required environment variables if not set
if not os.getenv('GOOGLE_CLOUD_PROJECT'):
    os.environ['GOOGLE_CLOUD_PROJECT'] = 'slack-ai-news-feed'

# Import the main function
from src.main_digest_fixed import main_function_digest

# Create a fake Pub/Sub event
fake_event = {
    'data': {},
    'attributes': {'test': 'true'}
}

# Create a fake context
class FakeContext:
    event_id = 'test-event-123'
    timestamp = '2024-01-01T00:00:00Z'
    event_type = 'google.pubsub.topic.publish'
    resource = {'name': 'projects/test/topics/test'}

print("Triggering manual digest...")
print("=" * 50)

try:
    main_function_digest(fake_event, FakeContext())
    print("\n✅ Digest triggered successfully!")
except Exception as e:
    print(f"\n❌ Error: {e}")
    import traceback
    traceback.print_exc()
#!/usr/bin/env python3
"""Clear all processed items from Firestore to allow fresh content"""

import os
from google.cloud import firestore
from dotenv import load_dotenv

load_dotenv()

# Set project ID
os.environ['GOOGLE_CLOUD_PROJECT'] = 'slack-ai-news-feed'

def clear_processed_items():
    """Clear all processed items from Firestore"""
    try:
        # Initialize Firestore client
        db = firestore.Client(project='slack-ai-news-feed')
        
        # Get reference to the collection
        collection_ref = db.collection('processed_items')
        
        # Get all documents
        docs = collection_ref.stream()
        
        # Delete each document
        count = 0
        for doc in docs:
            doc.reference.delete()
            count += 1
            print(f"Deleted: {doc.id}")
        
        print(f"\n✅ Successfully deleted {count} processed items from Firestore")
        print("The next digest will include all available content!")
        
    except Exception as e:
        print(f"❌ Error clearing Firestore: {e}")
        print("\nYou may need to clear it manually in the Google Cloud Console:")
        print("https://console.cloud.google.com/firestore/data?project=slack-ai-news-feed")

if __name__ == "__main__":
    print("Clearing Firestore processed items...")
    print("=" * 50)
    clear_processed_items()
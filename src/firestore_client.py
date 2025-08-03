from google.cloud import firestore
from google.api_core import exceptions
import logging
from typing import List, Dict, Optional
from datetime import datetime, timedelta

from .config import Config

logger = logging.getLogger(__name__)


class FirestoreClient:
    """Manage processed URLs tracking in Firestore"""

    def __init__(self) -> None:
        self.collection_name = Config.FIRESTORE_COLLECTION
        self.db = firestore.Client(project=Config.GCP_PROJECT_ID)
        self.collection = self.db.collection(self.collection_name)

    def _get_document_id(self, url: str) -> str:
        """Generate a valid Firestore document ID from URL"""
        # Firestore document IDs have restrictions, so we'll use a hash
        import hashlib
        return hashlib.sha256(url.encode()).hexdigest()[:20]

    def initialize_collection(self) -> None:
        """Initialize Firestore collection (called on first use)"""
        # Firestore creates collections automatically when documents are added
        logger.info(f"Using Firestore collection: {self.collection_name}")

    def is_url_processed(self, url: str) -> bool:
        """Check if URL has already been processed"""
        try:
            doc_id = self._get_document_id(url)
            doc_ref = self.collection.document(doc_id)
            doc = doc_ref.get()
            return bool(doc.exists)

        except exceptions.NotFound:
            return False
        except Exception as e:
            logger.error(f"Firestore error checking URL: {e}")
            return False  # Default to unprocessed on error

    def mark_url_processed(self, url: str, metadata: Optional[Dict] = None) -> bool:
        """Mark URL as processed with optional metadata"""
        try:
            doc_id = self._get_document_id(url)
            doc_data = {
                'url': url,
                'processed_at': firestore.SERVER_TIMESTAMP,
                'expire_at': datetime.utcnow() + timedelta(days=90)  # For TTL
            }

            if metadata:
                doc_data.update({
                    'title': metadata.get('title', ''),
                    'feed_name': metadata.get('feed_name', ''),
                    'feed_type': metadata.get('feed_type', ''),
                    'summary_generated': metadata.get('summary_generated', False)
                })

            self.collection.document(doc_id).set(doc_data)
            logger.info(f"Marked URL as processed: {url}")
            return True

        except Exception as e:
            logger.error(f"Error marking URL as processed: {e}")
            return False

    def get_processed_urls_count(self, hours: int = 24) -> int:
        """Get count of URLs processed in the last N hours"""
        try:
            cutoff_time = datetime.utcnow() - timedelta(hours=hours)
            query = self.collection.where('processed_at', '>=', cutoff_time)
            return len(list(query.stream()))

        except Exception as e:
            logger.error(f"Error counting processed URLs: {e}")
            return 0

    def batch_check_urls(self, urls: List[str]) -> Dict[str, bool]:
        """Check multiple URLs at once for efficiency"""
        results = {}

        # Firestore has a limit of 10 for 'in' queries
        batch_size = 10

        for i in range(0, len(urls), batch_size):
            batch_urls = urls[i:i + batch_size]
            doc_ids = [self._get_document_id(url) for url in batch_urls]

            try:
                # Get multiple documents
                docs = self.db.get_all([self.collection.document(doc_id) for doc_id in doc_ids])

                # Check which exist
                existing_ids = {doc.id for doc in docs if doc.exists}

                for url, doc_id in zip(batch_urls, doc_ids):
                    results[url] = doc_id in existing_ids

            except Exception as e:
                logger.error(f"Error in batch URL check: {e}")
                # Fall back to individual checks
                for url in batch_urls:
                    results[url] = self.is_url_processed(url)

        return results

    def cleanup_old_entries(self, days: int = 90) -> None:
        """Clean up entries older than specified days"""
        try:
            cutoff_date = datetime.utcnow() - timedelta(days=days)

            # Query for old documents
            old_docs = self.collection.where('processed_at', '<', cutoff_date).stream()

            # Delete in batches
            batch = self.db.batch()
            count = 0

            for doc in old_docs:
                batch.delete(doc.reference)
                count += 1

                # Commit every 500 documents (Firestore batch limit)
                if count % 500 == 0:
                    batch.commit()
                    batch = self.db.batch()

            # Commit remaining
            if count % 500 != 0:
                batch.commit()

            logger.info(f"Cleaned up {count} old entries")

        except Exception as e:
            logger.error(f"Error cleaning up old entries: {e}")

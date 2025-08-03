"""Main entry point for Google Cloud Functions"""

# Import the functions from src package
from src.main_digest_fixed import main_function_digest
from src.event_driven_main import event_driven_function, podcast_check_function

# Re-export them at module level for Cloud Functions
__all__ = ['main_function_digest', 'event_driven_function', 'podcast_check_function']
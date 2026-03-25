"""Supabase client - replaces SQLAlchemy direct DB connection."""
from supabase import create_client, Client
from app.core.config import settings

_supabase_client: Client | None = None


def get_supabase() -> Client:
    """Get or create the Supabase client (service role for full access)."""
    global _supabase_client
    if _supabase_client is None:
        _supabase_client = create_client(
            settings.SUPABASE_URL,
            settings.SUPABASE_SERVICE_ROLE_KEY,
        )
    return _supabase_client


# Alias used throughout the codebase
def get_db() -> Client:
    return get_supabase()

"""
Selector Cache System - Eliminates AI flakiness by persisting working selectors
Based on TestRigor and SupaTest approaches for reliable test automation
"""
import json
import hashlib
import sqlite3
import logging
from typing import Optional, Dict, Tuple
from pathlib import Path
import time

logger = logging.getLogger(__name__)

class SelectorCache:
    """
    Persistent cache for successful selectors to eliminate AI flakiness
    
    Key principles:
    1. Once a selector works, NEVER change it unless the page changes
    2. Hash command + page context for deterministic caching
    3. Validate cached selectors before using them
    4. Fall back to AI only when cached selectors fail
    """
    
    def __init__(self, cache_file: str = None):
        if cache_file is None:
            cache_file = Path.home() / ".vibeq" / "selector_cache.db"
        
        self.cache_file = Path(cache_file)
        self.cache_file.parent.mkdir(parents=True, exist_ok=True)
        
        self._init_database()
        logger.info(f"🔒 Selector cache initialized: {self.cache_file}")
    
    def _init_database(self):
        """Initialize the SQLite database for selector caching"""
        with sqlite3.connect(self.cache_file) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS selector_cache (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    command_hash TEXT UNIQUE NOT NULL,
                    command TEXT NOT NULL,
                    page_url TEXT NOT NULL,
                    page_domain TEXT NOT NULL,
                    selector TEXT NOT NULL,
                    confidence REAL NOT NULL,
                    success_count INTEGER DEFAULT 1,
                    failure_count INTEGER DEFAULT 0,
                    last_used TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_command_hash ON selector_cache(command_hash)
            """)
            
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_domain ON selector_cache(page_domain)
            """)
    
    def _create_cache_key(self, command: str, page_url: str, page_context: str = "") -> str:
        """Create a deterministic cache key from command and page context"""
        # Extract domain for better caching across similar pages
        from urllib.parse import urlparse
        domain = urlparse(page_url).netloc
        
        # Create hash from command + domain + page structure hints
        cache_input = f"{command.lower().strip()}|{domain}|{len(page_context)}"
        return hashlib.sha256(cache_input.encode()).hexdigest()[:16]
    
    def get_cached_selector(self, command: str, page_url: str, page_context: str = "") -> Optional[Tuple[str, float]]:
        """Get cached selector if available and still reliable"""
        cache_key = self._create_cache_key(command, page_url, page_context)
        
        try:
            with sqlite3.connect(self.cache_file) as conn:
                cursor = conn.execute("""
                    SELECT selector, confidence, success_count, failure_count 
                    FROM selector_cache 
                    WHERE command_hash = ? 
                    ORDER BY (success_count - failure_count) DESC, last_used DESC 
                    LIMIT 1
                """, (cache_key,))
                
                row = cursor.fetchone()
                if row:
                    selector, confidence, success_count, failure_count = row
                    
                    # Calculate reliability score
                    total_uses = success_count + failure_count
                    reliability = success_count / total_uses if total_uses > 0 else 0
                    
                    # Only use cached selector if it's been reliable (>80% success rate)
                    if reliability >= 0.8 and total_uses >= 1:
                        logger.info(f"🎯 Using cached selector: {selector} (reliability: {reliability:.1%}, uses: {total_uses})")
                        return selector, confidence
                    else:
                        logger.debug(f"🚫 Cached selector unreliable: {reliability:.1%} ({success_count}/{total_uses})")
                
        except Exception as e:
            logger.error(f"Cache lookup failed: {e}")
        
        return None
    
    def cache_successful_selector(self, command: str, page_url: str, selector: str, 
                                confidence: float, page_context: str = ""):
        """Cache a selector that worked successfully"""
        cache_key = self._create_cache_key(command, page_url, page_context)
        
        from urllib.parse import urlparse
        domain = urlparse(page_url).netloc
        
        try:
            with sqlite3.connect(self.cache_file) as conn:
                # Try to update existing record
                cursor = conn.execute("""
                    UPDATE selector_cache 
                    SET success_count = success_count + 1, last_used = CURRENT_TIMESTAMP
                    WHERE command_hash = ? AND selector = ?
                """, (cache_key, selector))
                
                if cursor.rowcount == 0:
                    # Insert new record
                    conn.execute("""
                        INSERT OR REPLACE INTO selector_cache 
                        (command_hash, command, page_url, page_domain, selector, confidence)
                        VALUES (?, ?, ?, ?, ?, ?)
                    """, (cache_key, command, page_url, domain, selector, confidence))
                    
                    logger.info(f"💾 Cached new working selector: {command} -> {selector[:50]}...")
                else:
                    logger.debug(f"📈 Updated selector success count: {selector[:50]}...")
                    
        except Exception as e:
            logger.error(f"Failed to cache selector: {e}")
            import traceback
            logger.debug(traceback.format_exc())
    
    def mark_selector_failed(self, command: str, page_url: str, selector: str, page_context: str = ""):
        """Mark a cached selector as failed (for reliability tracking)"""
        cache_key = self._create_cache_key(command, page_url, page_context)
        
        try:
            with sqlite3.connect(self.cache_file) as conn:
                conn.execute("""
                    UPDATE selector_cache 
                    SET failure_count = failure_count + 1, last_used = CURRENT_TIMESTAMP
                    WHERE command_hash = ? AND selector = ?
                """, (cache_key, selector))
                
                logger.debug(f"❌ Marked selector as failed: {selector}")
                
        except Exception as e:
            logger.error(f"Failed to mark selector as failed: {e}")
    
    def get_cache_stats(self) -> Dict:
        """Get cache statistics for monitoring"""
        try:
            with sqlite3.connect(self.cache_file) as conn:
                cursor = conn.execute("""
                    SELECT 
                        COUNT(*) as total_selectors,
                        AVG(success_count) as avg_success_count,
                        SUM(success_count) as total_successes,
                        SUM(failure_count) as total_failures,
                        COUNT(DISTINCT page_domain) as unique_domains
                    FROM selector_cache
                """)
                
                row = cursor.fetchone()
                if row:
                    total, avg_success, total_success, total_failure, domains = row
                    total_success = total_success or 0
                    total_failure = total_failure or 0
                    reliability = total_success / (total_success + total_failure) if (total_success + total_failure) > 0 else 0
                    
                    return {
                        "total_cached_selectors": total or 0,
                        "average_success_count": round(avg_success or 0, 2),
                        "total_successes": total_success,
                        "total_failures": total_failure,
                        "overall_reliability": round(reliability, 3),
                        "unique_domains": domains or 0
                    }
                    
        except Exception as e:
            logger.error(f"Failed to get cache stats: {e}")
        
        return {}
    
    def clear_unreliable_selectors(self, min_reliability: float = 0.5):
        """Clean up selectors that are consistently failing"""
        try:
            with sqlite3.connect(self.cache_file) as conn:
                cursor = conn.execute("""
                    DELETE FROM selector_cache 
                    WHERE (success_count * 1.0 / (success_count + failure_count)) < ?
                    AND (success_count + failure_count) >= 3
                """, (min_reliability,))
                
                deleted_count = cursor.rowcount
                logger.info(f"🧹 Cleaned up {deleted_count} unreliable selectors")
                
        except Exception as e:
            logger.error(f"Failed to clean cache: {e}")

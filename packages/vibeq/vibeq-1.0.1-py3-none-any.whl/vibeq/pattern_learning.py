"""
Pattern Learning Database - Learns successful automation patterns across websites
Enables VibeQ to get better with every interaction
"""
import sqlite3
import json
import logging
from typing import List, Dict, Optional, Any
from datetime import datetime
import os

logger = logging.getLogger(__name__)

class PatternLearningDB:
    """Database for learning and storing automation patterns across websites"""
    
    def __init__(self, db_path: str = None):
        if db_path is None:
            # Default to workspace db directory
            db_dir = os.path.join(os.getcwd(), 'db')
            os.makedirs(db_dir, exist_ok=True)
            db_path = os.path.join(db_dir, 'patterns.sqlite')
        
        self.db_path = db_path
        self._init_database()
    
    def _init_database(self):
        """Initialize the pattern learning database"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS website_patterns (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        domain TEXT NOT NULL,
                        site_type TEXT,
                        framework TEXT,
                        ui_library TEXT,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS successful_selectors (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        domain TEXT NOT NULL,
                        intent_verb TEXT NOT NULL,
                        intent_target TEXT NOT NULL,
                        selector TEXT NOT NULL,
                        confidence REAL NOT NULL,
                        source TEXT NOT NULL,
                        success_count INTEGER DEFAULT 1,
                        failure_count INTEGER DEFAULT 0,
                        last_success TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS element_patterns (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        domain TEXT NOT NULL,
                        element_type TEXT NOT NULL,
                        common_selectors TEXT NOT NULL,
                        naming_patterns TEXT,
                        attributes TEXT,
                        reliability_score REAL DEFAULT 0.5,
                        usage_count INTEGER DEFAULT 1,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS automation_sessions (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        domain TEXT NOT NULL,
                        session_success BOOLEAN NOT NULL,
                        commands_executed INTEGER NOT NULL,
                        commands_successful INTEGER NOT NULL,
                        total_time REAL,
                        notes TEXT,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                
                # Create indexes for performance
                conn.execute("CREATE INDEX IF NOT EXISTS idx_domain ON successful_selectors(domain)")
                conn.execute("CREATE INDEX IF NOT EXISTS idx_intent ON successful_selectors(intent_verb, intent_target)")
                conn.execute("CREATE INDEX IF NOT EXISTS idx_element_domain ON element_patterns(domain, element_type)")
                
                conn.commit()
                logger.info(f"📚 Pattern learning database initialized: {self.db_path}")
                
        except Exception as e:
            logger.error(f"Failed to initialize pattern database: {e}")
    
    def record_successful_selector(self, domain: str, intent_verb: str, intent_target: str, 
                                 selector: str, confidence: float, source: str):
        """Record a successful selector for learning"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                # Check if this exact pattern exists
                existing = conn.execute("""
                    SELECT id, success_count FROM successful_selectors 
                    WHERE domain = ? AND intent_verb = ? AND intent_target = ? AND selector = ?
                """, (domain, intent_verb, intent_target, selector)).fetchone()
                
                if existing:
                    # Update existing record
                    conn.execute("""
                        UPDATE successful_selectors 
                        SET success_count = success_count + 1, 
                            confidence = MAX(confidence, ?),
                            last_success = CURRENT_TIMESTAMP
                        WHERE id = ?
                    """, (confidence, existing[0]))
                else:
                    # Insert new record
                    conn.execute("""
                        INSERT INTO successful_selectors 
                        (domain, intent_verb, intent_target, selector, confidence, source)
                        VALUES (?, ?, ?, ?, ?, ?)
                    """, (domain, intent_verb, intent_target, selector, confidence, source))
                
                conn.commit()
                logger.debug(f"📝 Recorded successful pattern: {domain} - {selector}")
                
        except Exception as e:
            logger.error(f"Failed to record successful selector: {e}")
    
    def record_selector_failure(self, domain: str, selector: str):
        """Record a selector failure for learning"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("""
                    UPDATE successful_selectors 
                    SET failure_count = failure_count + 1
                    WHERE domain = ? AND selector = ?
                """, (domain, selector))
                conn.commit()
                
        except Exception as e:
            logger.error(f"Failed to record selector failure: {e}")
    
    def get_patterns_for_domain(self, domain: str, intent_verb: str = None, 
                               intent_target: str = None, limit: int = 10) -> List[Dict]:
        """Get learned patterns for a specific domain and intent"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                query = """
                    SELECT selector, confidence, source, success_count, failure_count
                    FROM successful_selectors 
                    WHERE domain = ?
                """
                params = [domain]
                
                if intent_verb:
                    query += " AND intent_verb = ?"
                    params.append(intent_verb)
                
                if intent_target:
                    query += " AND intent_target LIKE ?"
                    params.append(f"%{intent_target}%")
                
                query += """
                    ORDER BY 
                        (success_count * confidence) / (failure_count + 1) DESC,
                        last_success DESC
                    LIMIT ?
                """
                params.append(limit)
                
                results = conn.execute(query, params).fetchall()
                
                patterns = []
                for row in results:
                    reliability = (row[3] * row[1]) / (row[4] + 1)  # success_count * confidence / (failure_count + 1)
                    patterns.append({
                        'selector': row[0],
                        'confidence': row[1],
                        'source': row[2],
                        'success_count': row[3],
                        'failure_count': row[4],
                        'reliability': reliability
                    })
                
                return patterns
                
        except Exception as e:
            logger.error(f"Failed to get patterns for domain {domain}: {e}")
            return []
    
    def get_similar_domain_patterns(self, target_domain: str, intent_verb: str, 
                                   intent_target: str, limit: int = 5) -> List[Dict]:
        """Get patterns from similar domains that might work"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                # Find patterns from other domains with same intent
                results = conn.execute("""
                    SELECT domain, selector, confidence, success_count, failure_count
                    FROM successful_selectors 
                    WHERE domain != ? AND intent_verb = ? AND intent_target LIKE ?
                    AND success_count > failure_count
                    ORDER BY confidence DESC, success_count DESC
                    LIMIT ?
                """, (target_domain, intent_verb, f"%{intent_target}%", limit)).fetchall()
                
                patterns = []
                for row in results:
                    patterns.append({
                        'source_domain': row[0],
                        'selector': row[1],
                        'confidence': row[2] * 0.7,  # Reduce confidence for cross-domain
                        'success_count': row[3],
                        'failure_count': row[4]
                    })
                
                return patterns
                
        except Exception as e:
            logger.error(f"Failed to get similar domain patterns: {e}")
            return []
    
    def record_website_analysis(self, domain: str, site_type: str, framework: str, 
                              ui_library: str):
        """Record website analysis for pattern classification"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                # Check if domain exists
                existing = conn.execute("""
                    SELECT id FROM website_patterns WHERE domain = ?
                """, (domain,)).fetchone()
                
                if existing:
                    # Update existing
                    conn.execute("""
                        UPDATE website_patterns 
                        SET site_type = ?, framework = ?, ui_library = ?, 
                            updated_at = CURRENT_TIMESTAMP
                        WHERE domain = ?
                    """, (site_type, framework, ui_library, domain))
                else:
                    # Insert new
                    conn.execute("""
                        INSERT INTO website_patterns 
                        (domain, site_type, framework, ui_library)
                        VALUES (?, ?, ?, ?)
                    """, (domain, site_type, framework, ui_library))
                
                conn.commit()
                logger.debug(f"📊 Recorded website analysis: {domain} ({site_type}, {framework})")
                
        except Exception as e:
            logger.error(f"Failed to record website analysis: {e}")
    
    def record_automation_session(self, domain: str, success: bool, commands_executed: int,
                                commands_successful: int, total_time: float = None, 
                                notes: str = None):
        """Record an automation session for analytics"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("""
                    INSERT INTO automation_sessions 
                    (domain, session_success, commands_executed, commands_successful, 
                     total_time, notes)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (domain, success, commands_executed, commands_successful, 
                      total_time, notes))
                conn.commit()
                
        except Exception as e:
            logger.error(f"Failed to record automation session: {e}")
    
    def get_domain_statistics(self, domain: str) -> Dict[str, Any]:
        """Get statistics for a specific domain"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                # Get basic stats
                stats = conn.execute("""
                    SELECT 
                        COUNT(*) as total_sessions,
                        SUM(CASE WHEN session_success THEN 1 ELSE 0 END) as successful_sessions,
                        AVG(commands_successful * 1.0 / commands_executed) as avg_success_rate,
                        COUNT(DISTINCT substr(created_at, 1, 10)) as active_days
                    FROM automation_sessions 
                    WHERE domain = ?
                """, (domain,)).fetchone()
                
                # Get selector stats
                selector_stats = conn.execute("""
                    SELECT 
                        COUNT(*) as unique_selectors,
                        SUM(success_count) as total_successes,
                        SUM(failure_count) as total_failures,
                        AVG(confidence) as avg_confidence
                    FROM successful_selectors 
                    WHERE domain = ?
                """, (domain,)).fetchone()
                
                return {
                    'domain': domain,
                    'total_sessions': stats[0] or 0,
                    'successful_sessions': stats[1] or 0,
                    'success_rate': stats[2] or 0.0,
                    'active_days': stats[3] or 0,
                    'unique_selectors': selector_stats[0] or 0,
                    'total_successes': selector_stats[1] or 0,
                    'total_failures': selector_stats[2] or 0,
                    'avg_confidence': selector_stats[3] or 0.0
                }
                
        except Exception as e:
            logger.error(f"Failed to get domain statistics: {e}")
            return {'domain': domain, 'error': str(e)}
    
    def get_global_statistics(self) -> Dict[str, Any]:
        """Get global learning statistics"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                stats = conn.execute("""
                    SELECT 
                        COUNT(DISTINCT domain) as unique_domains,
                        COUNT(*) as total_sessions,
                        SUM(commands_successful) as total_successful_commands,
                        SUM(commands_executed) as total_commands,
                        (SELECT COUNT(*) FROM successful_selectors) as learned_selectors
                    FROM automation_sessions
                """).fetchone()
                
                return {
                    'unique_domains': stats[0] or 0,
                    'total_sessions': stats[1] or 0,
                    'total_successful_commands': stats[2] or 0,
                    'total_commands': stats[3] or 0,
                    'overall_success_rate': (stats[2] / stats[3]) if stats[3] > 0 else 0.0,
                    'learned_selectors': stats[4] or 0
                }
                
        except Exception as e:
            logger.error(f"Failed to get global statistics: {e}")
            return {'error': str(e)}
    
    def export_patterns(self, domain: str = None) -> Dict[str, Any]:
        """Export learned patterns for sharing or backup"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                query = """
                    SELECT domain, intent_verb, intent_target, selector, confidence, 
                           source, success_count, failure_count
                    FROM successful_selectors
                """
                params = []
                
                if domain:
                    query += " WHERE domain = ?"
                    params.append(domain)
                
                query += " ORDER BY domain, success_count DESC"
                
                results = conn.execute(query, params).fetchall()
                
                patterns = []
                for row in results:
                    patterns.append({
                        'domain': row[0],
                        'intent_verb': row[1],
                        'intent_target': row[2],
                        'selector': row[3],
                        'confidence': row[4],
                        'source': row[5],
                        'success_count': row[6],
                        'failure_count': row[7]
                    })
                
                return {
                    'export_date': datetime.now().isoformat(),
                    'domain_filter': domain,
                    'pattern_count': len(patterns),
                    'patterns': patterns
                }
                
        except Exception as e:
            logger.error(f"Failed to export patterns: {e}")
            return {'error': str(e)}
    
    def close(self):
        """Close database connection"""
        # SQLite connections are closed automatically with context manager
        logger.info("📚 Pattern learning database closed")


# Global instance for easy access
_pattern_db = None

def get_pattern_db(db_path: str = None) -> PatternLearningDB:
    """Get global pattern database instance"""
    global _pattern_db
    if _pattern_db is None:
        _pattern_db = PatternLearningDB(db_path)
    return _pattern_db

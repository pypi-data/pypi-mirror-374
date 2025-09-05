"""
Performance Layer - Production Performance Optimization
Optimized response times through intelligent caching and smart strategies
"""
import time
import hashlib
import logging
from typing import Optional, Dict, Any, List, Tuple
from collections import OrderedDict

logger = logging.getLogger(__name__)

class PerformanceCache:
    """LRU cache with TTL for lightning-fast pattern lookups"""
    
    def __init__(self, max_size: int = 10000, ttl_seconds: int = 3600):
        self.max_size = max_size
        self.ttl_seconds = ttl_seconds
        self.cache = OrderedDict()
        self.timestamps = {}
        self.hit_count = 0
        self.miss_count = 0
    
    def get(self, key: str) -> Optional[Any]:
        """Get cached value with TTL check"""
        if key not in self.cache:
            self.miss_count += 1
            return None
        
        # Check TTL
        if time.time() - self.timestamps[key] > self.ttl_seconds:
            del self.cache[key]
            del self.timestamps[key]
            self.miss_count += 1
            return None
        
        # Move to end (LRU)
        self.cache.move_to_end(key)
        self.hit_count += 1
        return self.cache[key]
    
    def put(self, key: str, value: Any):
        """Store value with LRU eviction"""
        if key in self.cache:
            self.cache.move_to_end(key)
        else:
            if len(self.cache) >= self.max_size:
                # Remove oldest
                oldest_key = next(iter(self.cache))
                del self.cache[oldest_key]
                del self.timestamps[oldest_key]
            
            self.cache[key] = value
        
        self.timestamps[key] = time.time()
    
    def hit_rate(self) -> float:
        """Get cache hit rate for monitoring"""
        total = self.hit_count + self.miss_count
        return self.hit_count / total if total > 0 else 0.0


class FastElementFinder:
    """Performance-first element finder with intelligent caching"""
    
    def __init__(self, browser, intelligence=None, offline_engine=None):
        self.browser = browser
        self.intelligence = intelligence
        self.offline_engine = offline_engine
        
        # Performance caches
        self.pattern_cache = PerformanceCache(max_size=5000, ttl_seconds=1800)  # 30 min
        self.success_cache = PerformanceCache(max_size=10000, ttl_seconds=3600)  # 1 hour
        self.failure_cache = PerformanceCache(max_size=2000, ttl_seconds=300)    # 5 min
        
        # Performance metrics
        self.total_requests = 0
        self.cache_hits = 0
        self.avg_response_time = 0
        
        logger.info("⚡ Fast Element Finder initialized - optimizing for best performance")
    
    def find_for_intent(self, intent) -> Optional[str]:
        """Find element with performance optimization and intelligent fallbacks"""
        start_time = time.time()
        self.total_requests += 1
        
        try:
            # STRATEGY 1: Pattern Cache (10-50ms) - Highest Priority
            cache_result = self._try_pattern_cache(intent)
            if cache_result:
                self._record_performance(time.time() - start_time, "cache_hit")
                self.cache_hits += 1
                logger.debug(f"⚡ Cache hit: {time.time() - start_time:.3f}s")
                return cache_result
            
            # STRATEGY 2: Recent Success Cache (50-100ms) 
            success_result = self._try_success_cache(intent)
            if success_result:
                self._record_performance(time.time() - start_time, "success_cache")
                logger.debug(f"⚡ Success cache: {time.time() - start_time:.3f}s")
                return success_result
            
            # STRATEGY 3: Fast Heuristics (100-200ms) - No AI calls
            if self.offline_engine:
                heuristic_result = self._try_fast_heuristics(intent)
                if heuristic_result:
                    self._record_performance(time.time() - start_time, "heuristics")
                    logger.debug(f"🧠 Heuristics: {time.time() - start_time:.3f}s")
                    # Cache successful heuristic for next time
                    self._cache_successful_pattern(intent, heuristic_result, "heuristic")
                    return heuristic_result
            
            # STRATEGY 4: Parallel AI + DOM Analysis (2-5s) - Last resort
            ai_result = self._try_parallel_ai_strategies(intent)
            if ai_result:
                self._record_performance(time.time() - start_time, "ai_success")
                logger.info(f"🤖 AI success: {time.time() - start_time:.3f}s")
                # Cache AI result for future speed
                self._cache_successful_pattern(intent, ai_result, "ai")
                return ai_result
            
            # STRATEGY 5: Failure cache to avoid repeated expensive failures
            self._cache_failure(intent)
            self._record_performance(time.time() - start_time, "failure")
            logger.warning(f"❌ All strategies failed: {time.time() - start_time:.3f}s")
            return None
            
        except Exception as e:
            self._record_performance(time.time() - start_time, "error")
            logger.error(f"Performance finder error: {e}")
            return None
    
    def _try_pattern_cache(self, intent) -> Optional[str]:
        """Try cached patterns - fastest path"""
        cache_key = self._generate_cache_key(intent)
        return self.pattern_cache.get(cache_key)
    
    def _try_success_cache(self, intent) -> Optional[str]:
        """Try recently successful selectors"""
        domain = self._get_current_domain()
        success_key = f"{domain}:{intent.verb}:{intent.target.lower()}"
        return self.success_cache.get(success_key)
    
    def _try_fast_heuristics(self, intent) -> Optional[str]:
        """Fast offline heuristics - no network calls"""
        if not self.offline_engine:
            return None
        
        # Check failure cache first to avoid expensive retries
        failure_key = self._generate_failure_key(intent)
        if self.failure_cache.get(failure_key):
            logger.debug("⚡ Skipping known failure pattern")
            return None
        
        # Try offline intelligence
        page_context = self._get_minimal_page_context()  # Faster than full context
        selector, confidence, source = self.offline_engine.find_selector(
            f"{intent.verb} {intent.target}", 
            page_context
        )
        
        if selector and confidence > 0.6:  # High confidence threshold for performance
            return selector
        
        return None
    
    def _try_parallel_ai_strategies(self, intent) -> Optional[str]:
        """Run AI and DOM analysis in parallel for speed"""
        if not self.intelligence:
            return None
        
        import concurrent.futures
        import threading
        
        results = {}
        
        def ai_strategy():
            try:
                page_context = self._get_optimized_page_context()
                command = f"{intent.verb} {intent.target}"
                selector, confidence, source = self.intelligence.find_selector(command, page_context)
                if selector and confidence > 0.4:
                    results['ai'] = selector
            except Exception as e:
                logger.debug(f"AI strategy failed: {e}")
        
        def dom_strategy():
            try:
                # Fast DOM analysis without full page scan
                selector = self._fast_dom_analysis(intent)
                if selector:
                    results['dom'] = selector
            except Exception as e:
                logger.debug(f"DOM strategy failed: {e}")
        
        # Run strategies in parallel with timeout
        with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
            futures = [
                executor.submit(ai_strategy),
                executor.submit(dom_strategy)
            ]
            
            # Wait max 10 seconds for either to complete
            concurrent.futures.wait(futures, timeout=10.0)
        
        # Return first successful result
        return results.get('ai') or results.get('dom')
    
    def _fast_dom_analysis(self, intent) -> Optional[str]:
        """Fast DOM analysis focusing on visible elements only"""
        try:
            if not self.browser.page:
                return None
            
            # Quick selector generation based on intent
            verb = intent.verb.lower()
            target = intent.target.lower()
            
            if verb == 'click':
                # Fast button/link detection
                quick_selectors = [
                    f'button:has-text("{intent.target}"):visible',
                    f'a:has-text("{intent.target}"):visible',
                    f'[role="button"]:has-text("{intent.target}"):visible'
                ]
                
                for selector in quick_selectors:
                    try:
                        if self.browser.page.locator(selector).count() > 0:
                            return selector
                    except:
                        continue
            
            elif verb == 'type':
                # Fast input detection
                quick_selectors = [
                    f'input[placeholder*="{target}" i]:visible',
                    f'input[name*="{target}" i]:visible',
                    f'input[id*="{target}" i]:visible'
                ]
                
                for selector in quick_selectors:
                    try:
                        if self.browser.page.locator(selector).count() > 0:
                            return selector
                    except:
                        continue
            
            return None
            
        except Exception as e:
            logger.debug(f"Fast DOM analysis failed: {e}")
            return None
    
    def _cache_successful_pattern(self, intent, selector: str, source: str):
        """Cache successful pattern for future speed"""
        # Cache in pattern cache
        cache_key = self._generate_cache_key(intent)
        self.pattern_cache.put(cache_key, selector)
        
        # Cache in success cache
        domain = self._get_current_domain()
        success_key = f"{domain}:{intent.verb}:{intent.target.lower()}"
        self.success_cache.put(success_key, selector)
        
        logger.debug(f"⚡ Cached successful pattern: {cache_key} -> {selector}")
    
    def _cache_failure(self, intent):
        """Cache failures to avoid expensive retries"""
        failure_key = self._generate_failure_key(intent)
        self.failure_cache.put(failure_key, True)
    
    def _generate_cache_key(self, intent) -> str:
        """Generate cache key for pattern"""
        domain = self._get_current_domain()
        page_sig = self._get_page_signature()
        content = f"{domain}:{intent.verb}:{intent.target}:{page_sig}"
        return hashlib.md5(content.encode()).hexdigest()[:16]
    
    def _generate_failure_key(self, intent) -> str:
        """Generate failure cache key"""
        domain = self._get_current_domain()
        content = f"{domain}:{intent.verb}:{intent.target}"
        return hashlib.md5(content.encode()).hexdigest()[:16]
    
    def _get_current_domain(self) -> str:
        """Get current domain quickly"""
        try:
            if self.browser.page:
                return self.browser.page.url.split('/')[2]
        except:
            pass
        return "unknown"
    
    def _get_page_signature(self) -> str:
        """Get lightweight page signature for caching"""
        try:
            if self.browser.page:
                # Quick signature based on title and URL
                title = self.browser.page.title()[:50]  # First 50 chars
                url_path = self.browser.page.url.split('/')[-1][:20]  # Last path segment
                return f"{title}:{url_path}".replace(' ', '_')
        except:
            pass
        return "default"
    
    def _get_minimal_page_context(self) -> str:
        """Get minimal page context for speed"""
        try:
            if self.browser.page:
                return f"Title: {self.browser.page.title()}\nURL: {self.browser.page.url}"
        except:
            pass
        return ""
    
    def _get_optimized_page_context(self) -> str:
        """Get optimized page context for AI - balance speed vs accuracy"""
        try:
            if not self.browser.page:
                return ""
            
            # Get key elements only - much faster than full DOM
            key_elements = []
            
            # Quickly grab visible interactive elements
            selectors = ['button:visible', 'input:visible', 'a:visible']
            for selector in selectors:
                try:
                    elements = self.browser.page.query_selector_all(selector)[:5]  # Limit to 5
                    for elem in elements:
                        try:
                            html = elem.outer_HTML()[:100]  # First 100 chars
                            key_elements.append(html)
                        except:
                            continue
                except:
                    continue
            
            context_parts = [
                f"Title: {self.browser.page.title()}",
                f"URL: {self.browser.page.url}",
                "Key Elements:",
                '\n'.join(key_elements[:10])  # Max 10 elements
            ]
            
            return '\n'.join(context_parts)
            
        except Exception as e:
            logger.debug(f"Optimized context extraction failed: {e}")
            return self._get_minimal_page_context()
    
    def _record_performance(self, duration: float, result_type: str):
        """Record performance metrics"""
        # Update rolling average
        self.avg_response_time = (self.avg_response_time + duration) / 2
        
        # Log slow operations
        if duration > 1.0:  # Slower than 1 second
            logger.warning(f"⚠️ Slow operation: {result_type} took {duration:.3f}s")
        elif duration > 0.5:  # Slower than 500ms
            logger.info(f"⚡ Acceptable: {result_type} took {duration:.3f}s")
    
    def get_performance_stats(self) -> Dict[str, Any]:
        """Get performance statistics for monitoring"""
        return {
            'total_requests': self.total_requests,
            'cache_hit_rate': self.cache_hits / self.total_requests if self.total_requests > 0 else 0,
            'avg_response_time': self.avg_response_time,
            'pattern_cache_hit_rate': self.pattern_cache.hit_rate(),
            'success_cache_hit_rate': self.success_cache.hit_rate(),
            'cache_sizes': {
                'patterns': len(self.pattern_cache.cache),
                'successes': len(self.success_cache.cache),
                'failures': len(self.failure_cache.cache)
            }
        }
    
    def clear_caches(self):
        """Clear all caches for testing/debugging"""
        self.pattern_cache = PerformanceCache(max_size=5000, ttl_seconds=1800)
        self.success_cache = PerformanceCache(max_size=10000, ttl_seconds=3600)
        self.failure_cache = PerformanceCache(max_size=2000, ttl_seconds=300)
        logger.info("🧹 All caches cleared")

class PerformanceLayer:
    """Production performance layer - wraps all performance optimizations"""
    
    def __init__(self):
        self.performance_cache = PerformanceCache()
        self.stats = {
            'total_requests': 0,
            'cache_hits': 0,
            'cache_misses': 0,
            'total_response_time': 0,
            'fastest_response': float('inf'),
            'slowest_response': 0
        }
    
    def get_performance_stats(self) -> Dict[str, Any]:
        """Get comprehensive performance statistics"""
        total_requests = max(1, self.stats['total_requests'])
        
        return {
            'total_requests': self.stats['total_requests'],
            'cache_hits': self.performance_cache.hit_count,
            'cache_misses': self.performance_cache.miss_count,
            'cache_hit_rate': (self.performance_cache.hit_count / max(1, self.performance_cache.hit_count + self.performance_cache.miss_count)) * 100,
            'avg_response_time': self.stats['total_response_time'] / total_requests,
            'fastest_response': self.stats['fastest_response'] if self.stats['fastest_response'] != float('inf') else 0,
            'slowest_response': self.stats['slowest_response']
        }
    
    def record_request(self, response_time_ms: float):
        """Record performance metrics for monitoring"""
        self.stats['total_requests'] += 1
        self.stats['total_response_time'] += response_time_ms
        self.stats['fastest_response'] = min(self.stats['fastest_response'], response_time_ms)
        self.stats['slowest_response'] = max(self.stats['slowest_response'], response_time_ms)

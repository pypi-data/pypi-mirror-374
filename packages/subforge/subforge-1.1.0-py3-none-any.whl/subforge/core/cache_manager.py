"""
SubForge Cache Manager
Intelligent caching system for analysis results and research data
"""

import hashlib
import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, Optional, Union


class CacheManager:
    """Manages caching for SubForge operations"""

    def __init__(self, cache_dir: Optional[Path] = None):
        """Initialize cache manager"""
        if cache_dir:
            self.cache_dir = Path(cache_dir)
        else:
            self.cache_dir = Path.home() / ".subforge" / "cache"

        self.cache_dir.mkdir(parents=True, exist_ok=True)

        # Cache configuration
        self.ttl_config = {
            "project_analysis": timedelta(hours=24),
            "research_results": timedelta(days=7),
            "template_selection": timedelta(hours=12),
            "workflow_results": timedelta(days=30),
            "metrics": timedelta(hours=1),
        }

        # Performance metrics
        self.stats = {"hits": 0, "misses": 0, "saves": 0, "evictions": 0}

    def _generate_key(self, namespace: str, identifier: Union[str, Dict]) -> str:
        """Generate cache key from namespace and identifier"""
        if isinstance(identifier, dict):
            identifier = json.dumps(identifier, sort_keys=True)

        content = f"{namespace}:{identifier}"
        return hashlib.sha256(content.encode()).hexdigest()

    def _get_cache_path(self, namespace: str, key: str) -> Path:
        """Get file path for cache entry"""
        namespace_dir = self.cache_dir / namespace
        namespace_dir.mkdir(exist_ok=True)
        return namespace_dir / f"{key}.json"

    def get(
        self,
        namespace: str,
        identifier: Union[str, Dict],
        max_age: Optional[timedelta] = None,
    ) -> Optional[Any]:
        """
        Retrieve item from cache

        Args:
            namespace: Cache namespace (e.g., "project_analysis")
            identifier: Unique identifier for the cached item
            max_age: Maximum age for cache validity

        Returns:
            Cached data if valid, None otherwise
        """
        key = self._generate_key(namespace, identifier)
        cache_path = self._get_cache_path(namespace, key)

        if not cache_path.exists():
            self.stats["misses"] += 1
            return None

        try:
            with open(cache_path, "r") as f:
                cache_entry = json.load(f)

            # Check if cache is expired
            cached_time = datetime.fromisoformat(cache_entry["timestamp"])
            max_age = max_age or self.ttl_config.get(namespace, timedelta(hours=24))

            if datetime.now() - cached_time > max_age:
                self.stats["misses"] += 1
                self.evict(namespace, identifier)
                return None

            self.stats["hits"] += 1
            return cache_entry["data"]

        except (json.JSONDecodeError, KeyError, ValueError):
            self.stats["misses"] += 1
            return None

    def set(
        self,
        namespace: str,
        identifier: Union[str, Dict],
        data: Any,
        ttl: Optional[timedelta] = None,
    ) -> bool:
        """
        Save item to cache

        Args:
            namespace: Cache namespace
            identifier: Unique identifier
            data: Data to cache
            ttl: Time to live for this entry

        Returns:
            True if successfully cached
        """
        key = self._generate_key(namespace, identifier)
        cache_path = self._get_cache_path(namespace, key)

        try:
            cache_entry = {
                "timestamp": datetime.now().isoformat(),
                "namespace": namespace,
                "identifier": (
                    identifier
                    if isinstance(identifier, str)
                    else json.dumps(identifier)
                ),
                "data": data,
                "ttl": str(ttl or self.ttl_config.get(namespace, timedelta(hours=24))),
            }

            with open(cache_path, "w") as f:
                json.dump(cache_entry, f, indent=2)

            self.stats["saves"] += 1
            return True

        except Exception as e:
            print(f"Cache save error: {e}")
            return False

    def evict(self, namespace: str, identifier: Union[str, Dict]) -> bool:
        """Remove item from cache"""
        key = self._generate_key(namespace, identifier)
        cache_path = self._get_cache_path(namespace, key)

        if cache_path.exists():
            cache_path.unlink()
            self.stats["evictions"] += 1
            return True

        return False

    def clear_namespace(self, namespace: str) -> int:
        """Clear all items in a namespace"""
        namespace_dir = self.cache_dir / namespace
        if not namespace_dir.exists():
            return 0

        count = 0
        for cache_file in namespace_dir.glob("*.json"):
            cache_file.unlink()
            count += 1
            self.stats["evictions"] += 1

        return count

    def clear_all(self) -> int:
        """Clear entire cache"""
        count = 0
        for namespace_dir in self.cache_dir.iterdir():
            if namespace_dir.is_dir():
                count += self.clear_namespace(namespace_dir.name)

        return count

    def cleanup_expired(self) -> int:
        """Remove all expired cache entries"""
        count = 0

        for namespace_dir in self.cache_dir.iterdir():
            if not namespace_dir.is_dir():
                continue

            namespace = namespace_dir.name
            max_age = self.ttl_config.get(namespace, timedelta(hours=24))

            for cache_file in namespace_dir.glob("*.json"):
                try:
                    with open(cache_file, "r") as f:
                        cache_entry = json.load(f)

                    cached_time = datetime.fromisoformat(cache_entry["timestamp"])

                    if datetime.now() - cached_time > max_age:
                        cache_file.unlink()
                        count += 1
                        self.stats["evictions"] += 1

                except (json.JSONDecodeError, KeyError, ValueError):
                    # Invalid cache file, remove it
                    cache_file.unlink()
                    count += 1

        return count

    def get_stats(self) -> Dict[str, Any]:
        """Get cache performance statistics"""
        total_requests = self.stats["hits"] + self.stats["misses"]
        hit_rate = (
            (self.stats["hits"] / total_requests * 100) if total_requests > 0 else 0
        )

        return {
            "hits": self.stats["hits"],
            "misses": self.stats["misses"],
            "saves": self.stats["saves"],
            "evictions": self.stats["evictions"],
            "hit_rate": f"{hit_rate:.1f}%",
            "total_requests": total_requests,
            "cache_size": self._calculate_cache_size(),
        }

    def _calculate_cache_size(self) -> str:
        """Calculate total cache size"""
        total_size = 0
        for cache_file in self.cache_dir.rglob("*.json"):
            total_size += cache_file.stat().st_size

        # Convert to human-readable format
        for unit in ["B", "KB", "MB", "GB"]:
            if total_size < 1024:
                return f"{total_size:.2f} {unit}"
            total_size /= 1024

        return f"{total_size:.2f} TB"

    def optimize(self) -> Dict[str, Any]:
        """Optimize cache by removing expired entries and analyzing usage"""
        expired_count = self.cleanup_expired()
        stats = self.get_stats()

        # Analyze cache effectiveness
        recommendations = []

        if (
            stats["hit_rate"].rstrip("%") != "0.0"
            and float(stats["hit_rate"].rstrip("%")) < 50
        ):
            recommendations.append("Low hit rate - consider increasing TTL values")

        if self.stats["evictions"] > self.stats["saves"] * 0.5:
            recommendations.append("High eviction rate - cache may be too small")

        return {
            "expired_removed": expired_count,
            "stats": stats,
            "recommendations": recommendations,
        }


class CachedAnalyzer:
    """Wrapper for ProjectAnalyzer with caching"""

    def __init__(self, analyzer, cache_manager: CacheManager):
        self.analyzer = analyzer
        self.cache = cache_manager

    async def analyze_project(self, project_path: str):
        """Analyze project with caching"""
        # Try to get from cache
        cached_result = self.cache.get("project_analysis", project_path)

        if cached_result:
            print(f"✅ Using cached analysis for {Path(project_path).name}")
            return cached_result

        # Perform analysis
        print(f"🔍 Analyzing project (not cached)...")
        result = await self.analyzer.analyze_project(project_path)

        # Cache the result
        self.cache.set("project_analysis", project_path, result.to_dict())

        return result


class CachedResearch:
    """Cached research operations"""

    def __init__(self, cache_manager: CacheManager):
        self.cache = cache_manager

    def get_cached_research(self, topic: str) -> Optional[Dict[str, Any]]:
        """Get cached research results"""
        return self.cache.get("research_results", topic, max_age=timedelta(days=7))

    def cache_research(self, topic: str, results: Dict[str, Any]):
        """Cache research results"""
        self.cache.set("research_results", topic, results, ttl=timedelta(days=7))
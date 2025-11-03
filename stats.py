#!/usr/bin/env python3
"""
Statistics tracking module for CS 1.6 Master Server.
Provides thread-safe statistics collection, rate calculation, and data aggregation.
"""

import threading
import time
from collections import defaultdict, deque
from datetime import datetime
from typing import Dict, List, Tuple, Optional


class Statistics:
    """
    Thread-safe statistics collector for master server metrics.
    """
    
    def __init__(self):
        self._lock = threading.Lock()
        
        # Core counters
        self.total_requests = 0
        self.total_packets_sent = 0
        self.total_errors = 0
        
        # Unique tracking
        self.unique_ips = set()
        self.ip_first_seen = {}  # ip -> timestamp
        self.ip_request_count = defaultdict(int)  # ip -> count
        
        # Country tracking (GeoIP)
        self.country_counts = defaultdict(int)  # country -> count
        
        # Time-based tracking
        self.start_time = time.time()
        self.last_request_time = None
        
        # Request rate tracking (rolling window of 60 seconds)
        self.request_timestamps = deque(maxlen=300)  # Store last 300 requests
        self.requests_per_second = deque(maxlen=60)  # 60 second buckets
        self._current_second = int(time.time())
        self._current_second_count = 0
        
        # Error tracking by type
        self.errors_by_type = defaultdict(int)
        
        # Historical data for charts
        self.request_history = deque(maxlen=300)  # (timestamp, count) tuples
        self._history_update_time = time.time()
    
    def record_request(self, ip: str, country: Optional[str] = None):
        """Record a player request."""
        with self._lock:
            now = time.time()
            
            # Update counters
            self.total_requests += 1
            self.last_request_time = now
            
            # Track unique IPs
            if ip not in self.unique_ips:
                self.unique_ips.add(ip)
                self.ip_first_seen[ip] = now
            
            self.ip_request_count[ip] += 1
            
            # Track country
            if country:
                self.country_counts[country] += 1
            
            # Track timestamps for rate calculation
            self.request_timestamps.append(now)
            
            # Update per-second buckets
            current_second = int(now)
            if current_second != self._current_second:
                if self._current_second_count > 0:
                    self.requests_per_second.append(self._current_second_count)
                self._current_second = current_second
                self._current_second_count = 1
            else:
                self._current_second_count += 1
    
    def record_packets_sent(self, count: int = 1):
        """Record packets sent to a client."""
        with self._lock:
            self.total_packets_sent += count
    
    def record_error(self, error_type: str = "general"):
        """Record an error occurrence."""
        with self._lock:
            self.total_errors += 1
            self.errors_by_type[error_type] += 1
    
    def get_uptime(self) -> float:
        """Get server uptime in seconds."""
        return time.time() - self.start_time
    
    def get_uptime_formatted(self) -> str:
        """Get formatted uptime string."""
        uptime = self.get_uptime()
        hours = int(uptime // 3600)
        minutes = int((uptime % 3600) // 60)
        seconds = int(uptime % 60)
        
        if hours > 0:
            return f"{hours}h {minutes}m {seconds}s"
        elif minutes > 0:
            return f"{minutes}m {seconds}s"
        else:
            return f"{seconds}s"
    
    def get_current_rps(self) -> float:
        """Get current requests per second (last 5 seconds average)."""
        with self._lock:
            now = time.time()
            # Count requests in last 5 seconds
            recent = [ts for ts in self.request_timestamps if now - ts <= 5.0]
            if len(recent) > 0:
                return len(recent) / 5.0
            return 0.0
    
    def get_average_rps(self) -> float:
        """Get average requests per second since start."""
        with self._lock:
            uptime = self.get_uptime()
            if uptime > 0:
                return self.total_requests / uptime
            return 0.0
    
    def get_unique_ip_count(self) -> int:
        """Get count of unique IPs."""
        with self._lock:
            return len(self.unique_ips)
    
    def get_top_countries(self, limit: int = 10) -> List[Tuple[str, int]]:
        """Get top N countries by request count."""
        with self._lock:
            sorted_countries = sorted(
                self.country_counts.items(),
                key=lambda x: x[1],
                reverse=True
            )
            return sorted_countries[:limit]
    
    def get_top_ips(self, limit: int = 10) -> List[Tuple[str, int]]:
        """Get top N IPs by request count."""
        with self._lock:
            sorted_ips = sorted(
                self.ip_request_count.items(),
                key=lambda x: x[1],
                reverse=True
            )
            return sorted_ips[:limit]
    
    def get_request_rate_history(self) -> List[int]:
        """Get request rate history (per-second buckets for last 60 seconds)."""
        with self._lock:
            return list(self.requests_per_second)
    
    def get_last_request_time_formatted(self) -> str:
        """Get formatted last request time."""
        with self._lock:
            if self.last_request_time is None:
                return "Never"
            dt = datetime.fromtimestamp(self.last_request_time)
            return dt.strftime("%Y-%m-%d %H:%M:%S")
    
    def get_summary(self) -> Dict:
        """Get a complete statistics summary."""
        with self._lock:
            return {
                "total_requests": self.total_requests,
                "total_packets_sent": self.total_packets_sent,
                "total_errors": self.total_errors,
                "unique_ips": len(self.unique_ips),
                "unique_countries": len(self.country_counts),
                "uptime": self.get_uptime(),
                "uptime_formatted": self.get_uptime_formatted(),
                "current_rps": self.get_current_rps(),
                "average_rps": self.get_average_rps(),
                "last_request": self.get_last_request_time_formatted(),
                "top_countries": self.get_top_countries(10),
                "top_ips": self.get_top_ips(10),
                "errors_by_type": dict(self.errors_by_type),
            }
    
    def reset(self):
        """Reset all statistics."""
        with self._lock:
            self.total_requests = 0
            self.total_packets_sent = 0
            self.total_errors = 0
            self.unique_ips.clear()
            self.ip_first_seen.clear()
            self.ip_request_count.clear()
            self.country_counts.clear()
            self.start_time = time.time()
            self.last_request_time = None
            self.request_timestamps.clear()
            self.requests_per_second.clear()
            self._current_second = int(time.time())
            self._current_second_count = 0
            self.errors_by_type.clear()
            self.request_history.clear()
            self._history_update_time = time.time()
    
    def export_to_dict(self) -> Dict:
        """Export statistics to a dictionary for saving/logging."""
        return self.get_summary()





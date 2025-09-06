#!/usr/bin/env python
"""
Advanced Memory Management System for MarcasBot

This module provides comprehensive memory management including:
- Explicit garbage collection and cleanup
- Memory monitoring and profiling
- Resource tracking and leak detection
- Automatic cleanup decorators
- Memory-efficient patterns
"""

import gc
import psutil
import os
import sys
import threading
import time
import weakref
from typing import Dict, Any, Optional, Callable, List
from functools import wraps
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)


class MemoryTracker:
    """Track memory usage and resource allocation patterns"""
    
    def __init__(self):
        self._process = psutil.Process()
        self._initial_memory = self._get_memory_usage()
        self._peak_memory = self._initial_memory
        self._memory_history: List[Dict[str, Any]] = []
        self._tracked_objects = weakref.WeakSet()
        self._lock = threading.Lock()
    
    def _get_memory_usage(self) -> Dict[str, float]:
        """Get current memory usage in MB"""
        try:
            memory_info = self._process.memory_info()
            return {
                'rss': memory_info.rss / 1024 / 1024,  # Resident Set Size
                'vms': memory_info.vms / 1024 / 1024,  # Virtual Memory Size
                'percent': self._process.memory_percent(),
                'available': psutil.virtual_memory().available / 1024 / 1024
            }
        except Exception as e:
            logger.warning(f"Error getting memory usage: {e}")
            return {'rss': 0, 'vms': 0, 'percent': 0, 'available': 0}
    
    def track_object(self, obj, name: str = None):
        """Track an object for memory monitoring"""
        try:
            self._tracked_objects.add(obj)
            if name:
                # Store reference information for debugging
                setattr(obj, '_memory_tracker_name', name)
        except Exception:
            pass  # Ignore tracking failures
    
    def snapshot(self, label: str = ""):
        """Take a memory snapshot"""
        with self._lock:
            current_memory = self._get_memory_usage()
            
            # Update peak memory
            if current_memory['rss'] > self._peak_memory['rss']:
                self._peak_memory = current_memory.copy()
            
            # Add to history
            snapshot = {
                'timestamp': datetime.now().isoformat(),
                'label': label,
                'memory': current_memory,
                'gc_objects': len(gc.get_objects()),
                'tracked_objects': len(self._tracked_objects)
            }
            self._memory_history.append(snapshot)
            
            # Keep only last 50 snapshots
            if len(self._memory_history) > 50:
                self._memory_history = self._memory_history[-50:]
            
            logger.debug(f"Memory snapshot [{label}]: RSS={current_memory['rss']:.1f}MB, "
                        f"Objects={snapshot['gc_objects']}")
            
            return snapshot
    
    def get_stats(self) -> Dict[str, Any]:
        """Get comprehensive memory statistics"""
        current = self._get_memory_usage()
        
        return {
            'current': current,
            'initial': self._initial_memory,
            'peak': self._peak_memory,
            'growth': {
                'rss_mb': current['rss'] - self._initial_memory['rss'],
                'percent': ((current['rss'] / self._initial_memory['rss']) - 1) * 100
            },
            'gc_stats': {
                'objects': len(gc.get_objects()),
                'generations': gc.get_stats(),
                'collections': gc.get_count()
            },
            'tracked_objects': len(self._tracked_objects),
            'snapshots_count': len(self._memory_history)
        }
    
    def get_memory_trend(self, minutes: int = 10) -> List[Dict[str, Any]]:
        """Get memory usage trend for the last N minutes"""
        cutoff_time = datetime.now() - timedelta(minutes=minutes)
        
        return [
            snapshot for snapshot in self._memory_history
            if datetime.fromisoformat(snapshot['timestamp']) > cutoff_time
        ]


class MemoryManager:
    """Main memory management coordinator"""
    
    def __init__(self):
        self.tracker = MemoryTracker()
        self._cleanup_callbacks: List[Callable] = []
        self._gc_enabled = True
        self._auto_gc_threshold = 100  # MB growth before triggering GC
        self._last_gc_memory = 0
    
    def register_cleanup_callback(self, callback: Callable):
        """Register a cleanup callback to be called during memory cleanup"""
        self._cleanup_callbacks.append(callback)
    
    def trigger_cleanup(self, force: bool = False):
        """Trigger comprehensive memory cleanup"""
        logger.info("Starting memory cleanup...")
        
        # Take snapshot before cleanup
        before_snapshot = self.tracker.snapshot("before_cleanup")
        
        try:
            # 1. Call registered cleanup callbacks
            for callback in self._cleanup_callbacks:
                try:
                    callback()
                except Exception as e:
                    logger.warning(f"Cleanup callback failed: {e}")
            
            # 2. Clear Python caches
            self._clear_python_caches()
            
            # 3. Force garbage collection
            if self._gc_enabled:
                self._force_garbage_collection()
            
            # 4. Clear module-level caches if available
            self._clear_module_caches()
            
            # Take snapshot after cleanup
            after_snapshot = self.tracker.snapshot("after_cleanup")
            
            # Log cleanup results
            memory_freed = before_snapshot['memory']['rss'] - after_snapshot['memory']['rss']
            objects_freed = before_snapshot['gc_objects'] - after_snapshot['gc_objects']
            
            logger.info(f"Memory cleanup completed: Freed {memory_freed:.1f}MB, "
                       f"Collected {objects_freed} objects")
            
            return {
                'memory_freed_mb': memory_freed,
                'objects_freed': objects_freed,
                'before': before_snapshot,
                'after': after_snapshot
            }
            
        except Exception as e:
            logger.error(f"Error during memory cleanup: {e}")
            return None
    
    def _clear_python_caches(self):
        """Clear various Python internal caches"""
        try:
            # Clear sys module caches
            if hasattr(sys, '_clear_type_cache'):
                sys._clear_type_cache()
            
            # Clear import caches
            if hasattr(sys, 'path_importer_cache'):
                sys.path_importer_cache.clear()
            
            # Clear regex cache
            import re
            re.purge()
            
            logger.debug("Python caches cleared")
            
        except Exception as e:
            logger.warning(f"Error clearing Python caches: {e}")
    
    def _force_garbage_collection(self):
        """Force garbage collection for all generations"""
        try:
            # Collect all generations
            collected = []
            for generation in range(3):
                count = gc.collect(generation)
                collected.append(count)
            
            total_collected = sum(collected)
            logger.debug(f"Garbage collection: {total_collected} objects collected "
                        f"(gen0: {collected[0]}, gen1: {collected[1]}, gen2: {collected[2]})")
            
            return total_collected
            
        except Exception as e:
            logger.warning(f"Error during garbage collection: {e}")
            return 0
    
    def _clear_module_caches(self):
        """Clear caches from common modules"""
        try:
            # Clear LangChain caches if available
            try:
                from langchain.cache import BaseCache
                # Clear any global caches
                pass
            except ImportError:
                pass
            
            # Clear other module caches as needed
            # Add specific cache clearing for your heavy dependencies
            
        except Exception as e:
            logger.debug(f"Error clearing module caches: {e}")
    
    def check_memory_pressure(self) -> bool:
        """Check if memory pressure is high and cleanup is needed"""
        current_memory = self.tracker._get_memory_usage()['rss']
        
        # Trigger cleanup if memory grew significantly since last GC
        if self._last_gc_memory == 0:
            self._last_gc_memory = current_memory
            return False
        
        memory_growth = current_memory - self._last_gc_memory
        if memory_growth > self._auto_gc_threshold:
            self._last_gc_memory = current_memory
            return True
        
        return False
    
    def auto_cleanup_if_needed(self):
        """Automatically cleanup if memory pressure is detected"""
        if self.check_memory_pressure():
            logger.info("High memory pressure detected, triggering cleanup")
            self.trigger_cleanup()
    
    def get_status(self) -> Dict[str, Any]:
        """Get comprehensive memory manager status"""
        return {
            'tracker_stats': self.tracker.get_stats(),
            'cleanup_callbacks': len(self._cleanup_callbacks),
            'gc_enabled': self._gc_enabled,
            'auto_gc_threshold_mb': self._auto_gc_threshold,
            'last_gc_memory_mb': self._last_gc_memory
        }


# Global memory manager instance
memory_manager = MemoryManager()


def memory_optimized(cleanup_after: bool = True, 
                    take_snapshots: bool = True,
                    auto_gc: bool = True):
    """
    Decorator for memory-optimized function execution
    
    Args:
        cleanup_after: Whether to trigger cleanup after function execution
        take_snapshots: Whether to take before/after memory snapshots
        auto_gc: Whether to check for auto cleanup needs
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            func_name = f"{func.__module__}.{func.__name__}"
            
            # Take snapshot before execution
            if take_snapshots:
                memory_manager.tracker.snapshot(f"before_{func_name}")
            
            # Auto cleanup if needed
            if auto_gc:
                memory_manager.auto_cleanup_if_needed()
            
            try:
                # Execute function
                result = func(*args, **kwargs)
                return result
                
            finally:
                # Cleanup after execution
                if cleanup_after:
                    memory_manager.trigger_cleanup()
                elif take_snapshots:
                    memory_manager.tracker.snapshot(f"after_{func_name}")
        
        return wrapper
    return decorator


def track_memory_usage(func: Callable) -> Callable:
    """Lightweight decorator to track memory usage of a function"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        func_name = f"{func.__module__}.{func.__name__}"
        
        before = memory_manager.tracker._get_memory_usage()['rss']
        
        try:
            result = func(*args, **kwargs)
            return result
        finally:
            after = memory_manager.tracker._get_memory_usage()['rss']
            memory_change = after - before
            
            if abs(memory_change) > 10:  # Log only significant changes (>10MB)
                logger.info(f"Memory usage [{func_name}]: {memory_change:+.1f}MB "
                           f"(before: {before:.1f}MB, after: {after:.1f}MB)")
    
    return wrapper


# Convenience functions
def cleanup_memory():
    """Convenience function to trigger memory cleanup"""
    return memory_manager.trigger_cleanup()


def get_memory_stats():
    """Convenience function to get memory statistics"""
    return memory_manager.get_status()


def take_memory_snapshot(label: str = ""):
    """Convenience function to take memory snapshot"""
    return memory_manager.tracker.snapshot(label)


# Setup cleanup for common heavy objects
def register_langchain_cleanup():
    """Register cleanup for LangChain objects"""
    def langchain_cleanup():
        try:
            # Clear any global LangChain state
            import gc
            
            # Find and clear LangChain objects
            langchain_objects = [
                obj for obj in gc.get_objects()
                if hasattr(obj, '__module__') and obj.__module__ and 'langchain' in obj.__module__
            ]
            
            # Clear references where safe
            for obj in langchain_objects:
                if hasattr(obj, 'clear') and callable(obj.clear):
                    try:
                        obj.clear()
                    except:
                        pass
                        
        except Exception as e:
            logger.debug(f"LangChain cleanup error: {e}")
    
    memory_manager.register_cleanup_callback(langchain_cleanup)


# Auto-register common cleanups
register_langchain_cleanup()

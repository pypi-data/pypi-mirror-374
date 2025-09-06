"""
Lightweight Session Manager for maintaining conversation memory across bot interactions.

This module provides memory-efficient session tracking without bloating the State object.
Memory is stored externally and accessed by session_id when needed.
"""

import uuid
from datetime import datetime, timedelta
from threading import Lock
from typing import Dict, List, Optional, Any
from collections import defaultdict
import logging
from .summarizer import response_summarizer, topic_extractor
try:
    from utils.logger import logger
except ImportError:
    # Fallback for direct testing
    import logging
    logger = logging.getLogger(__name__)
    logging.basicConfig(level=logging.INFO)


class SessionMemory:
    """Lightweight session memory container"""
    
    def __init__(self, session_id: str, user_id: str):
        self.session_id = session_id
        self.user_id = user_id
        self.created_at = datetime.now()
        self.last_activity = datetime.now()
        
        # Conversation context
        self.conversation_summary = ""
        self.key_topics = []
        self.recent_queries = []
        
        # Agent-specific memory (limited size)
        self.agent_memory = defaultdict(list)
        
        # Session preferences/context
        self.preferences = {}
    
    def add_query(self, query: str, full_response: str):
        """Add a query-response pair to recent history"""
        self.recent_queries.append({
            'query': query,
            'response': full_response,
            'timestamp': datetime.now().isoformat()
        })
        
        # Keep only last 5 queries to prevent memory bloat
        if len(self.recent_queries) > 5:
            self.recent_queries = self.recent_queries[-5:]
        
        self.last_activity = datetime.now()
    
    def add_agent_memory(self, agent_name: str, memory_item: Dict[str, Any]):
        """Add memory for a specific agent"""
        memory_item['timestamp'] = datetime.now().isoformat()
        self.agent_memory[agent_name].append(memory_item)
        
        # Keep only last 5 items per agent to prevent memory bloat
        if len(self.agent_memory[agent_name]) > 5:
            self.agent_memory[agent_name] = self.agent_memory[agent_name][-5:]
        
        self.last_activity = datetime.now()
    
    def get_context(self) -> str:
        """Get verbatim Q&A pairs from recent queries"""
        if not self.recent_queries:
            return ""
        
        # Include all stored Q&A pairs verbatim (up to 5)
        query_context = []
        
        for q in self.recent_queries:
            query_text = q['query']
            response_text = q.get('response', '')
            
            query_context.append(f"P: {query_text}\nR: {response_text}")
        
        return "\n\n".join(query_context)
    
    def update_summary(self, new_summary: str):
        """Update the conversation summary"""
        self.conversation_summary = new_summary
        self.last_activity = datetime.now()
    
    def auto_update_conversation_summary(self):
        """Automatically update conversation summary using NLP"""
        if len(self.recent_queries) >= 3:  # Only summarize after multiple interactions
            queries = [q['query'] for q in self.recent_queries]
            responses = [q['response_summary'] for q in self.recent_queries]
            
            try:
                new_summary = response_summarizer.summarize_conversation(queries, responses)
                if new_summary:
                    self.conversation_summary = new_summary
                    logger.debug(f"Auto-updated conversation summary: {new_summary[:50]}...")
            except Exception as e:
                logger.error(f"Error auto-updating conversation summary: {e}")
    
    def add_topic(self, topic: str):
        """Add a key topic to the session"""
        if topic not in self.key_topics:
            self.key_topics.append(topic)
            # Keep only last 5 topics
            if len(self.key_topics) > 5:
                self.key_topics = self.key_topics[-5:]


class SessionManager:
    """Lightweight session manager"""
    
    def __init__(self, session_timeout_hours: int = 4):
        """Initialize with shorter timeout to prevent memory buildup"""
        self.sessions: Dict[str, SessionMemory] = {}
        self.user_sessions: Dict[str, str] = {}  # user_id -> session_id
        self.session_timeout = timedelta(hours=session_timeout_hours)
        self._lock = Lock()
        
    def get_or_create_session(self, user_id: str, explicit_session_id: Optional[str] = None) -> str:
        """Get existing session or create new one
        
        Args:
            user_id: User identifier
            explicit_session_id: If provided, use this specific session ID (for UI consistency)
        
        Returns:
            session_id: The session ID to use
        """
        with self._lock:
            # Clean expired sessions first
            self._cleanup_expired_sessions()
            
            # If explicit session ID is provided, try to use it
            if explicit_session_id:
                if explicit_session_id in self.sessions:
                    # Session exists, update activity
                    self.sessions[explicit_session_id].last_activity = datetime.now()
                    # Update user mapping if needed
                    self.user_sessions[user_id] = explicit_session_id
                    logger.info(f"Using existing session {explicit_session_id[:8]}... for user {user_id}")
                    return explicit_session_id
                else:
                    # Session doesn't exist, create it with the explicit ID
                    self.sessions[explicit_session_id] = SessionMemory(explicit_session_id, user_id)
                    self.user_sessions[user_id] = explicit_session_id
                    logger.info(f"Created session with explicit ID {explicit_session_id[:8]}... for user {user_id}")
                    return explicit_session_id
            
            # No explicit session ID, check for existing active session
            if user_id in self.user_sessions:
                session_id = self.user_sessions[user_id]
                if session_id in self.sessions:
                    self.sessions[session_id].last_activity = datetime.now()
                    logger.info(f"Using existing session {session_id[:8]}... for user {user_id}")
                    return session_id
                else:
                    # Clean up orphaned mapping
                    del self.user_sessions[user_id]
            
            # Create new session with generated ID
            session_id = str(uuid.uuid4())
            self.sessions[session_id] = SessionMemory(session_id, user_id)
            self.user_sessions[user_id] = session_id
            
            logger.info(f"Created new session {session_id[:8]}... for user {user_id}")
            return session_id
    
    def get_session(self, session_id: str) -> Optional[SessionMemory]:
        """Get session by ID"""
        with self._lock:
            session = self.sessions.get(session_id)
            if session:
                session.last_activity = datetime.now()
            return session
    
    def get_context_for_agent(self, session_id: str, agent_name: str) -> str:
        """Get context string for an agent to include in their prompt"""
        session = self.get_session(session_id)
        if not session:
            return ""
        
        # Return the full verbatim context (up to 5 Q&A pairs)
        return session.get_context()
    
    def record_interaction(self, session_id: str, query: str, response: str, agent_name: str):
        """Record an interaction in the session - stores full response verbatim"""
        session = self.get_session(session_id)
        if not session:
            return
        
        # Add to recent queries - store full response verbatim
        session.add_query(query, response)
        
        # Simple topic extraction from query only
        potential_topics = self._extract_topics(query)
        for topic in potential_topics:
            session.add_topic(topic)
    
    def _extract_topics(self, text: str) -> List[str]:
        """Fallback topic extraction from text (used when NLP fails)"""
        # Key business terms for Delisoy
        keywords = [
            'delisoy', 'delisoya', 'ventas', 'mercado', 'consumidor', 
            'producto', 'marca', 'análisis', 'tendencias', 'margen'
        ]
        
        text_lower = text.lower()
        found_topics = [kw for kw in keywords if kw in text_lower]
        return found_topics[:3]  # Max 3 topics per query
    
    def _cleanup_expired_sessions(self):
        """Clean up expired sessions"""
        current_time = datetime.now()
        expired_sessions = []
        
        for session_id, session in self.sessions.items():
            if current_time - session.last_activity > self.session_timeout:
                expired_sessions.append(session_id)
        
        for session_id in expired_sessions:
            session = self.sessions[session_id]
            user_id = session.user_id
            
            # Remove from sessions
            del self.sessions[session_id]
            
            # Remove user mapping
            if user_id in self.user_sessions and self.user_sessions[user_id] == session_id:
                del self.user_sessions[user_id]
            
            logger.info(f"Cleaned up expired session {session_id[:8]}... for user {user_id}")
    
    def get_stats(self) -> Dict[str, Any]:
        """Get session statistics"""
        with self._lock:
            total_queries = sum(len(s.recent_queries) for s in self.sessions.values())
            total_agent_memories = sum(
                sum(len(memories) for memories in s.agent_memory.values()) 
                for s in self.sessions.values()
            )
            
            return {
                'active_sessions': len(self.sessions),
                'unique_users': len(self.user_sessions),
                'total_queries': total_queries,
                'total_agent_memories': total_agent_memories
            }


# Global session manager instance
session_manager = SessionManager()

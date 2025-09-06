from abc import ABC, abstractmethod
from typing import Any, Dict
from langgraph.types import Command
from langchain_core.messages import HumanMessage
from schemas.messages_state import State
from utils.logger import logger


class BaseNode(ABC):
    """
    Base class for all LangGraph nodes with common retry logic and routing patterns.
    Provides consistent handling of agent invocation, retry counts, and response processing.
    """

    def __init__(
        self,
        agent: Any,
        node_name: str,
        max_retries: int = 3,
        fallback_response: str = None,
        forward_all_messages: bool = False,
        keep_full_conversation: bool = True,
    ):
        self.agent = agent
        self.node_name = node_name
        self.max_retries = max_retries
        self.fallback_response = fallback_response
        # When True, forward all new messages produced by the inner agent to the outer state
        self.forward_all_messages = forward_all_messages
        # When False, only the last message is passed to the underlying agent
        self.keep_full_conversation = keep_full_conversation

    def __call__(self, state: State) -> Command:
        """
        Main entry point for the node. Handles retry logic,
        agent invocation, and response processing.
        """
        # 1. Handle retry logic
        retry_counts = self._get_retry_counts(state)
        current_retries = retry_counts.get(self.node_name, 0)

        # 2. Check if we've exceeded maximum retries
        if current_retries >= self.max_retries:
            return self._handle_max_retries_exceeded(retry_counts)

        # 3. Update retry counter
        updated_retry_counts = self._increment_retry_count(
            retry_counts, current_retries
        )

        # 4. Invoke the agent (with optional context preprocessing)
        try:
            invocation_state = self._preprocess_state(state)
            prev_messages = invocation_state.get("messages", [])
            prev_len = len(prev_messages) if prev_messages else 0
            result = self.agent.invoke(invocation_state)
            all_messages = result.get("messages", [])
            response = all_messages[-1].content if all_messages else ""
            
            # Extract any additional fields from agent result (like tabular_data)
            additional_fields = {k: v for k, v in result.items() if k not in ["messages"]}
            
            logger.info(
                f"{self._get_agent_display_name()} (attempt {current_retries + 1}): {response[:200]}..."
            )
            if additional_fields:
                logger.info(f"Additional fields from agent: {list(additional_fields.keys())}")
        except Exception as e:
            logger.error(f"Error invoking {self._get_agent_display_name()}: {e}")
            return self._handle_agent_error(retry_counts, str(e))

        # 5. If configured, forward all new messages from inner agent
        if self.forward_all_messages:
            new_messages = all_messages[prev_len:]
            if new_messages:
                logger.info(
                    f"{self._get_agent_display_name()} forwarding {len(new_messages)} inner message(s) to outer state"
                )
                return Command(
                    update={
                        "messages": new_messages,
                        "node_retry_counts": updated_retry_counts,
                    },
                    goto=self._get_continue_route(),
                )
            # If no new messages, fall back to normal processing

        # 6. Process the response and determine routing
        return self._process_response(response, updated_retry_counts, current_retries, additional_fields)

    def _get_retry_counts(self, state: State) -> Dict[str, int]:
        """Extract and initialize retry counters from state"""
        return state.get("node_retry_counts", {}).copy()

    def _increment_retry_count(
        self, retry_counts: Dict[str, int], current_retries: int
    ) -> Dict[str, int]:
        """Increment the retry count for this node"""
        updated_counts = retry_counts.copy()
        updated_counts[self.node_name] = current_retries + 1
        return updated_counts

    def _preprocess_state(self, state: State) -> State:
        """
        Optionally trim the conversation context before invoking the underlying agent.
        If keep_full_conversation is False, only pass the last message.
        """
        try:
            messages = state.get("messages", []) or []
        except Exception:
            messages = []
        if self.keep_full_conversation or not messages:
            return state
        # Keep only the last message
        last = messages[-1]
        try:
            trimmed_messages = [last]
        except Exception:
            # Fallback to ensure we always pass a message
            trimmed_messages = [HumanMessage(content=str(last))]
        trimmed = state.copy()
        trimmed["messages"] = trimmed_messages
        return trimmed

    def _reset_retry_count(self, retry_counts: Dict[str, int]) -> Dict[str, int]:
        """Reset the retry count for this node to 0"""
        reset_counts = retry_counts.copy()
        reset_counts[self.node_name] = 0
        return reset_counts

    def _handle_max_retries_exceeded(self, retry_counts: Dict[str, int]) -> Command:
        """Handle the case when maximum retries have been exceeded"""
        logger.warning(
            f"{self._get_agent_display_name()} exceeded maximum retries ({self.max_retries}). Using fallback."
        )

        fallback_response = self._get_fallback_response()
        reset_retry_counts = self._reset_retry_count(retry_counts)

        return Command(
            update={
                "messages": [
                    HumanMessage(content=fallback_response, name=self.node_name)
                ],
                "node_retry_counts": reset_retry_counts,
            },
            goto=self._get_fallback_route(),
        )

    def _handle_agent_error(
        self, retry_counts: Dict[str, int], error_message: str
    ) -> Command:
        """Handle errors during agent invocation"""
        error_response = f"Error en {self._get_agent_display_name()}: {error_message}"
        reset_retry_counts = self._reset_retry_count(retry_counts)

        return Command(
            update={
                "messages": [HumanMessage(content=error_response, name=self.node_name)],
                "node_retry_counts": reset_retry_counts,
            },
            goto=self._get_error_route(),
        )

    def _process_response(
        self, response: str, updated_retry_counts: Dict[str, int], current_retries: int, additional_fields: Dict = None
    ) -> Command:
        """Process the agent response and determine routing"""
        additional_fields = additional_fields or {}

        # Check if this is a final response
        if self._is_final_response(response):
            logger.info(f"{self._get_agent_display_name()} provided final response")
            final_retry_counts = self._reset_retry_count(updated_retry_counts)

            # Log the final response being added to state
            logger.info(
                f"[FINAL RESPONSE] {self._get_agent_display_name()} adding to state (length: {len(response)}):"
            )
            logger.info(
                f"[FINAL RESPONSE] Content: {response[:1000]}..."
                if len(response) > 1000
                else f"[FINAL RESPONSE] Content: {response}"
            )

            # Build update dict with additional fields
            update_dict = {
                "messages": [HumanMessage(content=response, name=self.node_name)],
                "node_retry_counts": final_retry_counts,
            }
            update_dict.update(additional_fields)
            
            return Command(
                update=update_dict,
                goto=self._get_success_route(),
            )
        else:
            # Continue with updated retry count
            logger.info(
                f"{self._get_agent_display_name()} continuing (retry {current_retries + 1}/{self.max_retries})"
            )

            # Log the continuing response being added to state
            logger.info(
                f"[CONTINUE RESPONSE] {self._get_agent_display_name()} adding to state (length: {len(response)}):"
            )
            logger.info(
                f"[CONTINUE RESPONSE] Content: {response[:1000]}..."
                if len(response) > 1000
                else f"[CONTINUE RESPONSE] Content: {response}"
            )

            # Build update dict with additional fields  
            update_dict = {
                "messages": [HumanMessage(content=response, name=self.node_name)],
                "node_retry_counts": updated_retry_counts,
            }
            update_dict.update(additional_fields)
            
            return Command(
                update=update_dict,
                goto=self._get_continue_route(),
            )

    # Abstract methods that subclasses must implement

    @abstractmethod
    def _get_success_route(self) -> str:
        """Return the route to take when the agent provides a final response"""
        pass

    @abstractmethod
    def _get_continue_route(self) -> str:
        """Return the route to take when the agent needs to continue processing"""
        pass

    @abstractmethod
    def _get_fallback_route(self) -> str:
        """Return the route to take when max retries are exceeded"""
        pass

    # Methods with default implementations that can be overridden

    def _get_error_route(self) -> str:
        """Return the route to take when there's an agent error (default: fallback route)"""
        return self._get_fallback_route()

    def _is_final_response(self, response: str) -> bool:
        """Check if the response indicates completion (default: check for 'RESPUESTA FINAL')"""
        return "RESPUESTA FINAL" in response

    def _get_fallback_response(self) -> str:
        """Get the fallback response when max retries are exceeded"""
        if self.fallback_response:
            return self.fallback_response
        return f"RESPUESTA FINAL: He intentado procesar la solicitud con {self._get_agent_display_name()}, pero he encontrado dificultades. Por favor, reformula tu consulta o intenta más tarde."

    def _get_agent_display_name(self) -> str:
        """Get a human-readable name for logging (default: node_name)"""
        return self.node_name.replace("_", " ").title()


class SimpleNode(BaseNode):
    """
    A simple node implementation for nodes that ALWAYS go to the same route
    regardless of response content (like synthesizer -> supervisor, text_sql -> sales_analyst).
    These nodes don't check for "RESPUESTA FINAL" - they always route the same way.
    """

    def __init__(
        self,
        agent: Any,
        node_name: str,
        target_route: str,
        max_retries: int = 3,
        fallback_response: str = None,
        forward_all_messages: bool = False,
        keep_full_conversation: bool = True,
    ):
        super().__init__(
            agent, node_name, max_retries, fallback_response, forward_all_messages, keep_full_conversation
        )
        self.target_route = target_route

    def _get_success_route(self) -> str:
        return self.target_route

    def _get_continue_route(self) -> str:
        return self.target_route

    def _get_fallback_route(self) -> str:
        return self.target_route

    def _is_final_response(self, response: str) -> bool:
        """Simple nodes don't check for final response - they always continue to target"""
        return False  # Always "continue" (which goes to target_route)


class ConditionalNode(BaseNode):
    """
    A conditional node implementation for nodes that have different routes
    for success vs. continue (like sales_node -> supervisor vs. text_sql).
    """

    def __init__(
        self,
        agent: Any,
        node_name: str,
        success_route: str,
        continue_route: str,
        fallback_route: str = None,
        max_retries: int = 3,
        fallback_response: str = None,
    ):
        super().__init__(agent, node_name, max_retries, fallback_response)
        self.success_route = success_route
        self.continue_route = continue_route
        self.fallback_route = fallback_route or success_route

    def _get_success_route(self) -> str:
        return self.success_route

    def _get_continue_route(self) -> str:
        return self.continue_route

    def _get_fallback_route(self) -> str:
        return self.fallback_route


class LoopingNode(BaseNode):
    """
    A looping node implementation for nodes that loop back to themselves
    when they don't have a final response (like market_study_node, search_node).
    These check for "RESPUESTA FINAL" and either go to supervisor or loop back to themselves.
    """

    def __init__(
        self,
        agent: Any,
        node_name: str,
        success_route: str = "supervisor",
        max_retries: int = 3,
        fallback_response: str = None,
    ):
        super().__init__(agent, node_name, max_retries, fallback_response)
        self.success_route = success_route

    def _get_success_route(self) -> str:
        return self.success_route

    def _get_continue_route(self) -> str:
        # Looping nodes go back to themselves when continuing
        return self.node_name

    def _get_fallback_route(self) -> str:
        return self.success_route

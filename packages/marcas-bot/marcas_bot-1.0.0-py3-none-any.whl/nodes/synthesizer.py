from core.base_node import SimpleNode
from agents.synthesizer import synthesizer_agent
from langgraph.types import Command
from langchain_core.messages import HumanMessage
import re


class SynthesizerNodeImpl(SimpleNode):
    """
    Synthesizer node that processes and synthesizes information from other agents.
    Adds a post-check to ensure all consolidated references are used at least once before routing to supervisor.
    """

    def __init__(self):
        super().__init__(
            agent=synthesizer_agent,
            node_name="synthesizer",
            target_route="supervisor",
            max_retries=3,  # allow one retry to fix citations
            fallback_response=(
                "He procesado la información disponible pero no pude garantizar el uso de todas las referencias. "
                "Por favor, revisa el etiquetado de referencias."
            ),
        )

    def _get_agent_display_name(self) -> str:
        """Custom display name for logging"""
        return "Sintetizador"

    def _parse_used_citations(self, text: str) -> set:
        used = set()
        if not text:
            return used
        # Matches [1], [1, 2], [3,4, 5]
        for grp in re.findall(r"\[(\d+(?:\s*,\s*\d+)*)\]", text):
            for n in grp.split(","):
                n = n.strip()
                if n.isdigit():
                    used.add(int(n))
        return used

    def _get_expected_citations(self, messages) -> set:
        expected = set()
        if not messages:
            return expected
        # Find the last consolidated references message
        for m in reversed(messages):
            name = getattr(m, "name", None)
            content = getattr(m, "content", "") or ""
            if (name == "references_collector") or content.strip().startswith(
                "REFERENCIAS CONSOLIDADAS:"
            ):
                # Lines like: - [1] "Doc.pptx"
                for num in re.findall(
                    r"^\s*-\s*\[(\d+)\]", content, flags=re.MULTILINE
                ):
                    try:
                        expected.add(int(num))
                    except ValueError:
                        continue
                break
        return expected

    def _extract_body_text(self, text: str) -> str:
        if not text:
            return ""
        # Split before the REFERENCES section (accept 'REFERENCIAS' or 'REFERENCES' with optional heading marks)
        # We only want to consider the BODY (text before the references list) for inline citations
        parts = re.split(
            r"(?im)^\s*(?:#+\s*)?(?:REFERENCIAS|REFERENCES)\s*:?.*$", text, maxsplit=1
        )
        return parts[0] if parts else text

    def _get_missing_citations_in_body(self, messages, text: str) -> set:
        expected = self._get_expected_citations(messages)
        if not expected:
            return set()
        body = self._extract_body_text(text)
        used = self._parse_used_citations(body)
        return expected - used

    def _needs_citation_retry(self, messages, text: str) -> bool:
        missing = self._get_missing_citations_in_body(messages, text)
        return len(missing) > 0

    def _count_words(self, text: str) -> int:
        """Count words in text, excluding references section"""
        if not text:
            return 0
        body = self._extract_body_text(text)
        return len(body.split())

    def _get_expected_word_count_range(self, messages) -> tuple:
        """Get expected word count range based on number of consolidated references"""
        expected_refs = self._get_expected_citations(messages)
        ref_count = len(expected_refs)

        if ref_count >= 10:
            return (1800, 2100)  # 3 to 3.5 pages
        elif ref_count >= 9:
            return (1500, 1800)  # 2 to 2.5 pages
        elif ref_count >= 7:
            return (1200, 1500)
        elif ref_count >= 5:
            return (900, 1200)
        elif ref_count >= 3:
            return (600, 900)
        elif ref_count >= 1:
            return (300, 600)
        else:
            return (10, 300)

    def _needs_length_retry(self, messages, text: str) -> bool:
        """Check if response needs retry due to insufficient length"""
        word_count = self._count_words(text)
        min_words, max_words = self._get_expected_word_count_range(messages)
        # Allow 10% tolerance below minimum threshold
        tolerance_min = min_words * 0.9
        return word_count < tolerance_min

    def __call__(self, state) -> Command:
        # Retry management (mirrors BaseNode semantics)
        retry_counts = state.get("node_retry_counts", {}).copy()
        current_retries = retry_counts.get(self.node_name, 0)

        # Exceeded retries -> fallback and route to supervisor
        if current_retries >= self.max_retries:
            fallback = (
                "RESPUESTA FINAL: No fue posible completar el etiquetado de citas conforme a lo solicitado. "
                "Por favor, solicita una revisión manual."
            )
            retry_counts[self.node_name] = 0
            return Command(
                update={
                    "messages": [HumanMessage(content=fallback, name=self.node_name)],
                    "node_retry_counts": retry_counts,
                },
                goto=self.target_route,
            )

        # Invoke synthesizer agent
        result = self.agent.invoke(state)
        all_messages = result.get("messages", [])
        response = all_messages[-1].content if all_messages else ""

        # Post-check: quality validation for citations and length
        needs_citation_fix = self._needs_citation_retry(all_messages, response)
        needs_length_fix = self._needs_length_retry(all_messages, response)

        if (
            needs_citation_fix or needs_length_fix
        ) and current_retries < self.max_retries:
            # Build comprehensive reminder message
            reminder_parts = []

            if needs_citation_fix:
                missing = sorted(
                    list(self._get_missing_citations_in_body(all_messages, response))
                )
                missing_str = ", ".join(f"[{m}]" for m in missing) if missing else ""
                reminder_parts.append(
                    f"CITAS FALTANTES: Usa TODAS las referencias de 'REFERENCIAS CONSOLIDADAS' en el cuerpo al menos una vez. "
                    f"Citas faltantes en el cuerpo: {missing_str}."
                )

            if needs_length_fix:
                word_count = self._count_words(response)
                min_words, max_words = self._get_expected_word_count_range(all_messages)
                ref_count = len(self._get_expected_citations(all_messages))
                reminder_parts.append(
                    f"LONGITUD INSUFICIENTE: Tu respuesta tiene {word_count} palabras, pero con {ref_count} referencias "
                    f"necesitas {min_words}-{max_words} palabras. Expande el análisis, agrega más detalles, "
                    f"ejemplos, y contexto para alcanzar la longitud requerida."
                )

            reminder = (
                "RECORDATORIO ESTRICTO: " + " ".join(reminder_parts) + " "
                "Reutiliza EXACTAMENTE la numeración de referencias (no renumeres) y mantén un estilo profesional en párrafos."
            )

            retry_counts[self.node_name] = current_retries + 1
            return Command(
                update={
                    "messages": [
                        HumanMessage(content=response, name=self.node_name),
                        HumanMessage(content=reminder, name="quality_guard"),
                    ],
                    "node_retry_counts": retry_counts,
                },
                goto=self.node_name,  # loop back to synthesizer
            )

        # Accept and route to supervisor
        retry_counts[self.node_name] = 0
        return Command(
            update={
                "messages": [HumanMessage(content=response, name=self.node_name)],
                "node_retry_counts": retry_counts,
            },
            goto=self.target_route,
        )


# Create the node instance - maintains the same function interface for existing code
call_synthesizer = SynthesizerNodeImpl()

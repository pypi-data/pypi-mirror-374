from typing import Dict, List
from langchain_core.messages import AIMessage
from utils.reference_extractor import ReferenceExtractor


class ReferencesCollectorAgent:
    """Collects internal document titles and external URLs from prior messages and emits a consolidated references message.
    
    IMPORTANT: To avoid leaking references from previous answers, this agent ONLY scans
    messages generated during the current turn. It explicitly ignores the initial
    HumanMessage that may contain a 'CONTEXTO PREVIO' block injected by the session manager.
    """
    
    def __init__(self):
        self.extractor = ReferenceExtractor()

    def _extract_references(self, text: str) -> Dict[str, List[str]]:
        """Extract references using the ReferenceExtractor utility."""
        return self.extractor.extract_references(text)

    def invoke(self, state: Dict) -> Dict:
        messages = state.get("messages", [])

        # Scope extraction to the CURRENT TURN only:
        # - Skip the first user message (may include CONTEXTO PREVIO + NUEVA CONSULTA)
        # - Consider only messages produced by agents in this run (index >= 1)
        candidate_messages = messages[1:] if messages else []

        all_text: List[str] = []
        for m in candidate_messages:
            content = getattr(m, "content", None)
            if isinstance(content, str):
                # Extra safeguard: if any agent message accidentally carries a context block,
                # keep only the portion after 'NUEVA CONSULTA:'
                if "NUEVA CONSULTA:" in content:
                    try:
                        content = content.split("NUEVA CONSULTA:", 1)[1]
                    except Exception:
                        # If split fails for any reason, keep original content
                        pass
                all_text.append(content)
        combined = "\n\n".join(all_text)

        refs = self._extract_references(combined)
        # Build consolidated references as a single list
        items: List[str] = []
        # Quote internal docs to match synthesizer expectations
        for d in refs["internal"]:
            if not (d.startswith('"') and d.endswith('"')):
                items.append(f'"{d}"')
            else:
                items.append(d)
        # Then add URLs
        items.extend(refs["external"])

        lines: List[str] = ["REFERENCIAS CONSOLIDADAS:"]
        if items:
            for i, it in enumerate(items, 1):
                lines.append(f"- [{i}] {it}")
        else:
            lines.append("- [Ninguna detectada]")
        lines.append("")
        lines.append(
            "Nota: El sintetizador debe USAR TODAS estas referencias en el cuerpo del texto al menos una vez con citas [n], y luego LISTARLAS al final en la sección REFERENCIAS respetando exactamente la misma numeración."
        )
        content = "\n".join(lines)
        # Tag the message so supervisor detection works
        return {
            "messages": messages
            + [AIMessage(content=content, name="references_collector")]
        }

import os
import sys
import json
import asyncio
import uuid
from fastapi import Request, HTTPException
from botbuilder.core import (
    BotFrameworkAdapter,
    ActivityHandler,
    MessageFactory,
    TurnContext,
    BotFrameworkAdapterSettings,
)
from botbuilder.schema import Activity, ActivityTypes
from botframework.connector.auth import AppCredentials

# Import project modules using proper absolute imports
try:
    from utils.logger import logger
except ImportError:
    # Fallback for when running as script - this should be avoided
    import sys
    import os

    sys.path.insert(
        0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    )
    from utils.logger import logger
from config.params import (
    MicrosoftAppId,
    MicrosoftAppPassword,
    MicrosoftAppTenantId,
)


class BotFramework:
    def __init__(self, engine):
        self.engine = engine
        self.app_id = MicrosoftAppId
        self.adapter = self._create_adapter()
        self.bot = self._create_bot()

    def _create_adapter(self):
        settings = BotFrameworkAdapterSettings(
            app_id=self.app_id,
            app_password=MicrosoftAppPassword,
            channel_auth_tenant=MicrosoftAppTenantId,
        )
        adapter = BotFrameworkAdapter(settings)

        trusted_urls = [
            "https://api.botframework.com",
            "https://botframework.azure.us",
            "https://smba.trafficmanager.net",
            "https://webchat.botframework.com",
            "https://directline.botframework.com",
            "https://soybot.azurewebsites.net",
        ]

        for url in trusted_urls:
            try:
                AppCredentials.trust_service_url(url)
            except Exception as e:
                logger.warning(f"Failed to trust URL {url}: {e}")

        async def on_error(context, error):
            logger.error(f"Bot adapter error: {type(error).__name__}: {error}")
            await context.send_activity(
                MessageFactory.text("I encountered an error. Please try again.")
            )

        adapter.on_turn_error = on_error
        return adapter

    def _create_bot(self):
        class MarcasBot(ActivityHandler):
            def __init__(self, engine):
                self.engine = engine
                # Track conversations we've greeted to avoid duplicate welcomes
                self.welcomed_conversations = set()

            def _normalize_text(self, turn_context: TurnContext) -> str:
                """Normalize incoming text for robust command detection.
                - Remove @mentions (e.g., <at>MarcasBot</at>)
                - Lowercase, strip whitespace
                """
                text = turn_context.activity.text or ""
                # Remove explicit mention text if present in entities
                try:
                    entities = getattr(turn_context.activity, "entities", []) or []
                    for ent in entities:
                        if getattr(ent, "type", "").lower() == "mention":
                            mention_text = None
                            if isinstance(ent, dict):
                                mention_text = ent.get("text")
                            else:
                                mention_text = getattr(ent, "text", None)
                            if mention_text:
                                text = text.replace(mention_text, "")
                except Exception:
                    pass
                # Remove <at>...</at> markup if any
                try:
                    import re as _re

                    text = _re.sub(
                        r"<\s*at\s*>.*?<\s*/\s*at\s*>", "", text, flags=_re.IGNORECASE
                    )
                except Exception:
                    pass
                return text.strip().lower()

            async def on_message_activity(self, turn_context: TurnContext):
                user_message = self._normalize_text(turn_context)

                # Handle specific commands (allow simple variants like "help please")
                base_commands = {
                    "hello",
                    "hola",
                    "hi",
                    "help",
                    "ayuda",
                    "ejemplos",
                    "ejemplo",
                }
                if user_message in base_commands or any(
                    user_message.startswith(cmd + " ") for cmd in base_commands
                ):
                    # Use the first token as the command keyword
                    command = user_message.split()[0]
                    await self.handle_command(turn_context, command)
                    return

                await turn_context.send_activity(
                    MessageFactory.text(
                        "Procesando su consulta. Un momento, por favor."
                    )
                )
                asyncio.create_task(self.process_query_async(turn_context))

            async def process_query_async(self, turn_context: TurnContext):
                try:
                    user_message = turn_context.activity.text
                    user_id = turn_context.activity.from_property.id
                    session_id = turn_context.activity.conversation.id

                    result = self.engine.process_query(
                        user_message, user_name=user_id, session_id=session_id
                    )
                    response_text = self.extract_response(result)
                except Exception as e:
                    logger.error(f"Error processing bot message: {e}")
                    response_text = "Lo siento, ocurrió un error."

                await turn_context.send_activity(MessageFactory.text(response_text))

            def extract_response(self, result):
                if result and result.get("error"):
                    return "Lo siento, he encontrado un problema técnico."
                if result and "messages" in result:
                    synthesizer_messages = [
                        msg
                        for msg in result["messages"]
                        if (hasattr(msg, "name") and msg.name == "synthesizer")
                        or (isinstance(msg, dict) and msg.get("name") == "synthesizer")
                    ]
                    if synthesizer_messages:
                        content = (
                            synthesizer_messages[-1].content
                            if hasattr(synthesizer_messages[-1], "content")
                            else synthesizer_messages[-1].get("content")
                        )
                        return content
                    else:
                        content = (
                            result["messages"][-1].content
                            if hasattr(result["messages"][-1], "content")
                            else result["messages"][-1].get("content")
                        )
                        return content
                return "Lo siento, no pude procesar tu consulta."

            async def handle_command(self, turn_context: TurnContext, command: str):
                """Handle specific bot commands"""
                if command in ["hello", "hola", "hi"]:
                    response = "¡Hola! Soy MarcasBot, tu asistente IA en construcción de marcas con capacidades en investigación de mercado, analisis de ventas, y mas. ¿En qué puedo ayudarte hoy?"
                elif command in ["help", "ayuda"]:
                    response = """Como un asistente en construcción de marcas. Puedo ayudarte con:

- Investigación y estudios de mercado
- Insights y tendencias de ventas
- Búsqueda y análisis de información online

Comandos disponibles:
- **Hola**: Saludo
- **Ayuda**: Ver esta ayuda
- **Ejemplos**: Ver ejemplos de preguntas

Simplemente escríbeme tu consulta para comenzar."""
                elif command in ["ejemplo", "ejemplos"]:
                    response = """
                    Ejemplos de preguntas que le puedes hacer a Marcas Bot:
                    - Cuál debería ser el posicionamiento de la marca Delisoy, tomando en cuenta su equity de marca en el mercado centroamericano, y los beneficios percibidos por sus consumidores?
                    - Haz un analisis comprehensivo de venta mes a mes del 2020 en adelante.
                    - Definir la competencia a través de determinar los otros productos que resuelven las necesidades que Delisoy está resolviendo.
                    - Ejecuta un resumen cronológico de la evolución de la marca Delisoy a lo largo de su participación en el mercado Centroamiricano.
                    """

                else:
                    response = "¡Hola! ¿En qué puedo ayudarte?"

                await turn_context.send_activity(MessageFactory.text(response))

            async def on_members_added_activity(
                self, members_added, turn_context: TurnContext
            ):
                # Send a single welcome only when the BOT is added to a Team/Group conversation
                conversation = turn_context.activity.conversation
                conversation_id = getattr(conversation, "id", None)

                is_team_context = getattr(conversation, "conversation_type", None) in [
                    "channel",
                    "groupChat",
                ]
                bot_id = (
                    turn_context.activity.recipient.id
                    if hasattr(turn_context.activity, "recipient")
                    else None
                )
                bot_added = any(getattr(m, "id", None) == bot_id for m in members_added)

                if (
                    is_team_context
                    and bot_added
                    and conversation_id
                    and conversation_id not in self.welcomed_conversations
                ):
                    welcome_message = (
                        "¡Hola! Soy MarcasBot, tu asistente experto en análisis de mercado y construcción de marcas. "
                        "Estoy aquí para ayudar a todo el equipo con investigación de mercado, análisis de ventas y estrategias de branding. "
                        "Mencióname (@MarcasBot) en este canal o escríbeme por 1:1 para comenzar."
                    )
                    await turn_context.send_activity(
                        MessageFactory.text(welcome_message)
                    )
                    self.welcomed_conversations.add(conversation_id)
                # For 1:1 chats, do not auto-greet here (on_members_added). The user can say "hi" or "help".

        return MarcasBot(self.engine)

    async def messages_handler(self, request: Request):
        if not self.adapter or not self.bot:
            raise HTTPException(
                status_code=503,
                detail="Bot Framework components not available",
            )

        # Generate a request ID for correlation and log basic request info
        request_id = str(uuid.uuid4())
        method = request.method
        path = request.url.path
        has_auth = "Authorization" in request.headers

        try:
            body_bytes = await request.body()
            body_str = body_bytes.decode("utf-8") if body_bytes else ""
            activity_dict = json.loads(body_str) if body_str else {}
            activity = Activity().deserialize(activity_dict)
            channel_id = getattr(activity, "channel_id", None)
            activity_id = getattr(activity, "id", None)
        except Exception as e:
            logger.error(
                f"[messages_handler] req_id={request_id} failed to parse activity: {type(e).__name__}: {e}"
            )
            raise HTTPException(status_code=400, detail="Invalid activity payload")

        logger.info(
            f"[messages_handler] req_id={request_id} method={method} path={path} auth_present={has_auth} channel_id={channel_id} activity_id={activity_id}"
        )

        # Local/dev mode bypass for Emulator (no auth header required)
        if os.getenv("ENV") == "local":
            await self.adapter.process_activity(activity, "", self.bot.on_turn)
            return {"status": "ok", "req_id": request_id}

        auth_header = request.headers.get("Authorization", "")
        if not auth_header or not auth_header.startswith("Bearer "):
            logger.warning(
                f"[messages_handler] req_id={request_id} missing or invalid Authorization header"
            )
            raise HTTPException(status_code=401, detail="Unauthorized")

        # Rely on Bot Framework SDK to validate token, signature, audience, issuer, tenant, etc.
        await self.adapter.process_activity(activity, auth_header, self.bot.on_turn)
        return {"status": "ok", "req_id": request_id}

    def options_messages_handler(self):
        return {"status": "ok", "methods": ["POST", "OPTIONS"]}

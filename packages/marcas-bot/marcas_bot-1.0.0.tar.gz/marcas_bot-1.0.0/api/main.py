from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from api.marcas_engine import marcas_engine
from api.research_engine import research_engine
from api.sales_engine import sales_engine
from api.market_study_engine import market_study_engine
from api.search_engine import search_engine
from utils.logger import logger
from utils.memory_manager import memory_manager, get_memory_stats, cleanup_memory, take_memory_snapshot
from schemas.api_query_request import QueryRequest
from api.bot_framework import BotFramework
import os
import gc


# Import the MarcasBot engine - must happen AFTER MLflow configuration

app = FastAPI(
    title="Marcas Bot API",
    description="API para interactuar con Marcas Bot, experto en las marcas CSSA.",
    version="1.0.3",
)


@app.on_event("startup")
async def startup_event():
    """Initialize memory management on startup"""
    logger.info("Starting MarcasBot API with memory optimization...")
    
    # Take initial memory snapshot
    take_memory_snapshot("app_startup")
    
    # Set environment variables for memory optimization
    os.environ.setdefault("PYTHONUNBUFFERED", "1")
    os.environ.setdefault("PYTHONDONTWRITEBYTECODE", "1")
    os.environ.setdefault("MALLOC_ARENA_MAX", "2")
    
    # Configure garbage collection
    gc.set_threshold(700, 10, 10)  # More aggressive GC
    gc.enable()
    
    # Initial cleanup
    cleanup_memory()
    
    logger.info("Memory management initialized successfully")


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    logger.info("Shutting down MarcasBot API...")
    
    # Final memory cleanup
    cleanup_memory()
    
    # Take final memory snapshot
    take_memory_snapshot("app_shutdown")
    
    logger.info("Shutdown completed")


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for Bot Framework
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],  # Include OPTIONS for Bot Framework
    allow_headers=["*"],  # Allow all headers for now
)


@app.get("/")
async def read_root():
    return {"status": "ok", "message": "MarcasBot API is running"}


@app.get("/privacy")
async def privacy_policy():
    """Privacy policy for MarcasBot Teams app"""
    return {
        "title": "Política de Privacidad - MarcasBot",
        "company": "CSSA TI",
        "effective_date": "2025-08-27",
        "policy": {
            "data_collection": {
                "description": "MarcasBot recopila únicamente los datos necesarios para proporcionar servicios de análisis de mercado y construcción de marcas.",
                "collected_data": [
                    "Mensajes y consultas enviados al bot",
                    "Identificadores de usuario de Microsoft Teams",
                    "Metadatos de conversación (fecha, hora)",
                ],
            },
            "data_use": {
                "description": "Los datos se utilizan exclusivamente para:",
                "purposes": [
                    "Proporcionar respuestas y análisis solicitados",
                    "Mejorar la precisión de las respuestas del bot",
                    "Mantener el contexto de conversación durante las sesiones",
                ],
            },
            "data_storage": {
                "description": "Los datos se almacenan de forma segura y se eliminan automáticamente después del período de retención establecido.",
                "retention": "Los datos de conversación se mantienen por un máximo de 30 días.",
            },
            "data_sharing": {
                "description": "CSSA TI no comparte datos personales con terceros, excepto cuando sea requerido por ley."
            },
            "user_rights": {
                "description": "Los usuarios tienen derecho a:",
                "rights": [
                    "Solicitar acceso a sus datos personales",
                    "Solicitar la corrección de datos inexactos",
                    "Solicitar la eliminación de sus datos",
                ],
            },
            "contact": {
                "email": "privacy@cssa.com",
                "description": "Para consultas sobre privacidad, contacte al equipo de CSSA TI.",
            },
        },
    }


@app.get("/terms")
async def terms_of_use():
    """Terms of use for MarcasBot Teams app"""
    return {
        "title": "Términos de Uso - MarcasBot",
        "company": "CSSA TI",
        "effective_date": "2025-08-27",
        "terms": {
            "service_description": {
                "description": "MarcasBot es un asistente de inteligencia artificial especializado en análisis de mercado, investigación y construcción de marcas para CSSA."
            },
            "acceptable_use": {
                "description": "Los usuarios se comprometen a:",
                "obligations": [
                    "Usar el servicio únicamente para fines comerciales legítimos",
                    "No intentar acceder a datos o sistemas no autorizados",
                    "No usar el servicio para actividades ilegales o dañinas",
                    "Respetar los derechos de propiedad intelectual",
                ],
            },
            "service_availability": {
                "description": "CSSA TI se esfuerza por mantener el servicio disponible, pero no garantiza disponibilidad continua.",
                "disclaimer": "El servicio se proporciona 'tal como está' sin garantías expresas o implícitas.",
            },
            "intellectual_property": {
                "description": "Todo el contenido y tecnología de MarcasBot es propiedad de CSSA TI y está protegido por derechos de autor."
            },
            "limitation_of_liability": {
                "description": "CSSA TI no será responsable por daños indirectos, incidentales o consecuentes que resulten del uso del servicio."
            },
            "modifications": {
                "description": "CSSA TI se reserva el derecho de modificar estos términos en cualquier momento. Los cambios serán efectivos inmediatamente tras su publicación."
            },
            "termination": {
                "description": "CSSA TI puede suspender o terminar el acceso al servicio en caso de violación de estos términos."
            },
            "governing_law": {
                "description": "Estos términos se rigen por las leyes aplicables en el territorio donde opera CSSA."
            },
            "contact": {
                "email": "legal@cssa.com",
                "description": "Para consultas legales, contacte al equipo legal de CSSA TI.",
            },
        },
    }


@app.get("/api/version")
async def get_version():
    """Get API version and deployment info"""
    import datetime

    return {
        "version": "1.0.2",
        "deployment_time": f"{datetime.datetime.now().isoformat()}",
    }


@app.post("/api/query")
async def process_query(request: QueryRequest):
    """
    Process a user query through the MarcasBot engine

    Returns the result of MarcasBot's analysis.
    """
    try:
        logger.info(f"Received query: {request.query} from user_id: {request.user_id}")

        # Use the user_id as the user_name if provided, otherwise use "user"
        user_name = request.user_id if request.user_id else "user"

        # Process the query through the MarcasBot engine with user name and session
        result = marcas_engine.process_query(
            request.query, user_name=user_name, session_id=request.session_id
        )

        logger.info(f"Engine result: {result}")
        return result
    except Exception as e:
        logger.error(f"Error processing query: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/health")
async def health_check():
    """
    Check if the MarcasBot API is healthy and the engine is properly initialized
    """
    try:
        # Check if the engine is properly initialized
        if marcas_engine.bot_runner:
            return {"status": "healthy", "engine": "initialized"}
        else:
            return {"status": "degraded", "engine": "not initialized"}
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return {"status": "unhealthy", "error": str(e)}


@app.get("/api/memory")
async def memory_status():
    """
    Get comprehensive memory usage statistics
    """
    try:
        stats = get_memory_stats()
        return {
            "status": "success",
            "memory_stats": stats
        }
    except Exception as e:
        logger.error(f"Error getting memory stats: {e}")
        return {"status": "error", "error": str(e)}


@app.post("/api/memory/cleanup")
async def trigger_memory_cleanup():
    """
    Manually trigger memory cleanup and garbage collection
    """
    try:
        logger.info("Manual memory cleanup triggered via API")
        cleanup_result = cleanup_memory()
        
        if cleanup_result:
            return {
                "status": "success",
                "message": "Memory cleanup completed",
                "cleanup_result": cleanup_result
            }
        else:
            return {
                "status": "warning",
                "message": "Memory cleanup completed but no detailed results available"
            }
    except Exception as e:
        logger.error(f"Error during manual memory cleanup: {e}")
        return {"status": "error", "error": str(e)}


# ===== AZURE BOT ENDPOINTS ======

# Initialize Bot Framework with the research engine (marcas engine is too heavy...)
bot_framework = BotFramework(marcas_engine)


@app.post("/api/messages")
async def messages(request: Request):
    return await bot_framework.messages_handler(request)


@app.options("/api/messages")
async def options_messages():
    return bot_framework.options_messages_handler()


# ===== RESEARCH ENGINE ENDPOINTS =====


@app.post("/api/research/query")
async def process_research_query(request: QueryRequest):
    """
    Process a user query through the MarcasBot engine

    Returns the result of MarcasBot's analysis.
    """
    try:
        logger.info(f"Received query: {request.query} from user_id: {request.user_id}")

        # Use the user_id as the user_name if provided, otherwise use "user"
        user_name = request.user_id if request.user_id else "user"

        # Process the query through the MarcasBot engine with user name and session
        result = research_engine.process_query(
            request.query, user_name=user_name, session_id=request.session_id
        )

        logger.info(f"Engine result: {result}")
        return result
    except Exception as e:
        logger.error(f"Error processing query: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ===== SALES ENGINE ENDPOINTS =====


@app.post("/api/sales/query")
async def process_sales_query(request: QueryRequest):
    """
    Process a sales-specific query through the SalesBot engine

    This endpoint is optimized for sales analysis and provides focused
    sales insights without the broader research team coordination.
    """
    try:
        logger.info(
            f"Received sales query: {request.query} from user_id: {request.user_id}"
        )

        # Use the user_id as the user_name if provided, otherwise use "user"
        user_name = request.user_id if request.user_id else "user"

        # Process the query through the Sales Engine with session management
        result = sales_engine.process_query(
            request.query, user_name=user_name, session_id=request.session_id
        )

        logger.info(f"Sales engine result: {result}")
        return result
    except Exception as e:
        logger.error(f"Error processing sales query: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ===== MARKET STUDY ENGINE ENDPOINTS =====


@app.post("/api/market-study/query")
async def process_market_study_query(request: QueryRequest):
    """
    Process a market study-specific query through the MarketStudyBot engine

    This endpoint is optimized for qualitative market research analysis
    and provides insights based on market studies conducted between 2004-2024.
    """
    try:
        logger.info(
            f"Received market study query: {request.query} from user_id: {request.user_id}"
        )

        # Use the user_id as the user_name if provided, otherwise use "user"
        user_name = request.user_id if request.user_id else "user"

        # Process the query through the Market Study Engine with session management
        result = market_study_engine.process_query(
            request.query, user_name=user_name, session_id=request.session_id
        )

        logger.info(f"Market study engine result: {result}")
        return result
    except Exception as e:
        logger.error(f"Error processing market study query: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ===== SEARCH ENGINE ENDPOINTS =====


@app.post("/api/search/query")
async def process_search_query(request: QueryRequest):
    """
    Process a general-purpose search query through the SearchEngine
    """
    try:
        logger.info(
            f"Received search query: {request.query} from user_id: {request.user_id}"
        )

        # Use the user_id as the user_name if provided, otherwise use "user"
        user_name = request.user_id if request.user_id else "user"

        # Process the query through the Search Engine with session management
        result = search_engine.process_query(
            request.query, user_name=user_name, session_id=request.session_id
        )

        logger.info(f"Search engine result: {result}")
        return result
    except Exception as e:
        logger.error(f"Error processing search query: {e}")
        raise HTTPException(status_code=500, detail=str(e))

import os

DELISOY_SELL_IN_GENIE_SPACE_ID = os.getenv("DELISOY_SELL_IN_GENIE_SPACE_ID")
DATABRICKS_TOKEN = os.getenv("DATABRICKS_TOKEN")
DATABRICKS_HOST = os.getenv("DATABRICKS_HOST")
DATABRICKS_WAREHOUSE_ID = os.getenv("DATABRICKS_WAREHOUSE_ID")
MARKET_STUDY_RAG_TABLE = os.getenv("MARKET_STUDY_RAG_TABLE")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
MICROSOFT_ACCESS_TOKEN = os.getenv("MICROSOFT_ACCESS_TOKEN")
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")

if os.getenv("ENV") == "local":
    MicrosoftAppId = ""
    MicrosoftAppPassword = ""
    MicrosoftAppTenantId = ""
else:
    MicrosoftAppId = os.getenv("MicrosoftAppId")
    MicrosoftAppPassword = os.getenv("MicrosoftAppPassword")
    MicrosoftAppTenantId = os.getenv("MicrosoftAppTenantId")

MICROSOFT_APP_ID = MicrosoftAppId
MICROSOFT_APP_PASSWORD = MicrosoftAppPassword
MICROSOFT_APP_TENANT_ID = MicrosoftAppTenantId

import os
import logging
from dotenv import load_dotenv
import databases
import sqlalchemy

# Load environment variables from .env file
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# Load the DATABASE_URL from environment variables

# Explicitly load the .env file from the current project directory
ENV_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../.env")
load_dotenv(dotenv_path=ENV_PATH)

DATABASE_URL = os.getenv("DATABASE_URI")

if not DATABASE_URL:
    logger.error("DATABASE_URI not found in environment variables.")
    raise ValueError("DATABASE_URI not found in environment variables. Ensure it is set in the .env file.")

# Initialize the database connection and metadata
try:
    database = databases.Database(DATABASE_URL)
    metadata = sqlalchemy.MetaData()
    logger.info("Database connection initialized successfully.")
except Exception as e:
    logger.error("Failed to initialize database connection: %s", e)
    raise

# Helper function to initialize database
async def connect_to_database():
    """
    Connects to the database when the application starts.
    """
    try:
        await database.connect()
        logger.info("Successfully connected to the database.")
    except Exception as e:
        logger.error("Error connecting to the database: %s", e)
        raise

# Helper function to disconnect database
async def disconnect_from_database():
    """
    Disconnects from the database when the application shuts down.
    """
    try:
        await database.disconnect()
        logger.info("Successfully disconnected from the database.")
    except Exception as e:
        logger.error("Error disconnecting from the database: %s", e)
        raise

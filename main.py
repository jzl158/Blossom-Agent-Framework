import logging
import os
from flask import Flask, jsonify
from utils.framework import Framework
from utils.agent_manager import AgentManager
from data.models import init_db
from llm.llm_interface import LLMInterface

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET")

# Initialize components
framework = Framework()
agent_manager = AgentManager()
llm_interface = LLMInterface()

@app.route('/')
def index():
    """Root endpoint providing API documentation"""
    logger.info("Root endpoint accessed")
    return jsonify({
        "message": "Welcome to the Skylark Multiagent Framework API",
        "version": "1.0.0",
        "endpoints": {
            "/": "API documentation",
            "/health": "Health check endpoint",
            "/stats": "System statistics and metrics"
        }
    })

@app.route('/health')
def health_check():
    """Health check endpoint"""
    logger.info("Health check endpoint accessed")
    return jsonify({"status": "healthy"})

@app.route('/stats')
def get_stats():
    """Get system statistics"""
    logger.info("Stats endpoint accessed")
    try:
        stats = framework.get_stats()
        return jsonify(stats)
    except Exception as e:
        logger.error(f"Error getting stats: {e}")
        return jsonify({"error": str(e)}), 500

async def initialize_system():
    """Initialize all system components"""
    try:
        logger.info("Starting system initialization...")
        init_db()
        await framework.initialize()
        await agent_manager.initialize()
        logger.info("System initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize system: {e}")
        raise

# Initialize the system at startup
import asyncio
try:
    asyncio.run(initialize_system())
    logger.info("System initialization completed")
except Exception as e:
    logger.error(f"System initialization failed: {e}")
    raise

if __name__ == "__main__":
    # Run the Flask development server
    app.run(host="0.0.0.0", port=5000, debug=True)
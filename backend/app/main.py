from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import logging
from contextlib import asynccontextmanager

from app.config import settings
from app.models.database import engine, Base, get_db
from app.models.models import Portfolio, BotConfig
from app.services.portfolio_service import portfolio_service
from app.routers import portfolio, stocks, bot, trades, logs, alpha_vantage
from sqlalchemy.orm import Session

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("Starting StockBot API...")
    
    # Create database tables
    Base.metadata.create_all(bind=engine)
    logger.info("Database tables created")
    
    # Initialize portfolio and bot config
    db = next(get_db())
    try:
        # Initialize portfolio if it doesn't exist
        portfolio_service.initialize_portfolio(db)
        
        # Initialize bot config if it doesn't exist
        bot_config = db.query(BotConfig).first()
        if not bot_config:
            bot_config = BotConfig(
                max_daily_trades=settings.default_max_daily_trades,
                risk_tolerance=settings.default_risk_tolerance
            )
            db.add(bot_config)
            db.commit()
            logger.info("Bot configuration initialized")
        
    except Exception as e:
        logger.error(f"Error during startup: {str(e)}")
    finally:
        db.close()
    
    yield
    
    # Shutdown
    logger.info("Shutting down StockBot API...")

# Create FastAPI app
app = FastAPI(
    title="StockBot API",
    description="AI-powered stock trading bot with virtual money",
    version="1.0.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(portfolio.router, prefix="/api/portfolio", tags=["portfolio"])
app.include_router(stocks.router, prefix="/api/stocks", tags=["stocks"])
app.include_router(bot.router, prefix="/api/bot", tags=["bot"])
app.include_router(trades.router, prefix="/api/trades", tags=["trades"])
app.include_router(logs.router, prefix="/api/logs", tags=["logs"])
app.include_router(alpha_vantage.router, prefix="/api/alpha-vantage", tags=["alpha-vantage"])

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "StockBot API",
        "version": "1.0.0",
        "status": "running"
    }

@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": "2024-01-01T00:00:00Z"
    }

@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler"""
    logger.error(f"Global exception: {str(exc)}")
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "error": "Internal server error",
            "details": str(exc) if settings.debug else "An error occurred"
        }
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.debug
    )
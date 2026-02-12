from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
import logging

from app.models.database import get_db
from app.models.schemas import (
    PortfolioResponse, PortfolioSummary, HoldingResponse,
    TradingStats, APIResponse, PortfolioHistoryResponse,
    PortfolioChartData, PortfolioSnapshotResponse
)
from app.services.portfolio_service import portfolio_service

logger = logging.getLogger(__name__)
router = APIRouter()

@router.get("/", response_model=PortfolioResponse)
async def get_portfolio(db: Session = Depends(get_db)):
    """Get current portfolio information"""
    try:
        portfolio = portfolio_service.get_portfolio(db)
        if not portfolio:
            raise HTTPException(status_code=404, detail="Portfolio not found")
        
        return PortfolioResponse.from_orm(portfolio)
    except Exception as e:
        logger.error(f"Error getting portfolio: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/summary", response_model=PortfolioSummary)
async def get_portfolio_summary(db: Session = Depends(get_db)):
    """Get comprehensive portfolio summary with returns and statistics"""
    try:
        # Check if portfolio exists, create if not
        portfolio = portfolio_service.get_portfolio(db)
        if not portfolio:
            portfolio = portfolio_service.initialize_portfolio(db)
        
        summary = await portfolio_service.get_portfolio_summary(db)
        if not summary:
            raise HTTPException(status_code=404, detail="Portfolio not found")
        
        return summary
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting portfolio summary: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@router.get("/holdings", response_model=List[HoldingResponse])
async def get_holdings(db: Session = Depends(get_db)):
    """Get all current stock holdings"""
    try:
        holdings = await portfolio_service.get_holdings(db)
        return holdings
    except Exception as e:
        logger.error(f"Error getting holdings: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/stats", response_model=TradingStats)
async def get_trading_stats(db: Session = Depends(get_db)):
    """Get trading statistics and performance metrics"""
    try:
        stats = portfolio_service.get_trading_stats(db)
        if not stats:
            raise HTTPException(status_code=404, detail="No trading data found")
        
        return stats
    except Exception as e:
        logger.error(f"Error getting trading stats: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.post("/initialize", response_model=APIResponse)
async def initialize_portfolio(db: Session = Depends(get_db)):
    """Initialize portfolio with starting balance (for testing)"""
    try:
        portfolio = portfolio_service.initialize_portfolio(db)
        return APIResponse(
            success=True,
            message=f"Portfolio initialized with ${portfolio.cash_balance}",
            data={"portfolio_id": portfolio.id, "balance": portfolio.cash_balance}
        )
    except Exception as e:
        logger.error(f"Error initializing portfolio: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/history", response_model=PortfolioHistoryResponse)
async def get_portfolio_history(
    days: int = 7,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """Get portfolio historical snapshots for charting"""
    try:
        history = portfolio_service.get_portfolio_history(db, days=days, limit=limit)
        return history
    except Exception as e:
        logger.error(f"Error getting portfolio history: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/chart-data", response_model=PortfolioChartData)
async def get_portfolio_chart_data(
    days: int = 7,
    db: Session = Depends(get_db)
):
    """Get portfolio data formatted for Plotly charts"""
    try:
        chart_data = portfolio_service.get_portfolio_chart_data(db, days=days)
        return chart_data
    except Exception as e:
        logger.error(f"Error getting portfolio chart data: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.post("/snapshot", response_model=APIResponse)
async def create_portfolio_snapshot(db: Session = Depends(get_db)):
    """Manually create a portfolio snapshot (for testing)"""
    try:
        snapshot = await portfolio_service.create_portfolio_snapshot(db)
        return APIResponse(
            success=True,
            message="Portfolio snapshot created successfully",
            data={"snapshot_id": snapshot.id, "timestamp": snapshot.timestamp.isoformat()}
        )
    except Exception as e:
        logger.error(f"Error creating portfolio snapshot: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")
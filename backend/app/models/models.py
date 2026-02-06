from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, Text, Enum
from sqlalchemy.sql import func
from datetime import datetime
import enum
from .database import Base

class TradeAction(enum.Enum):
    BUY = "BUY"
    SELL = "SELL"

class RiskTolerance(enum.Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"

class Portfolio(Base):
    __tablename__ = "portfolio"
    
    id = Column(Integer, primary_key=True, index=True)
    cash_balance = Column(Float, nullable=False, default=20.00)
    total_value = Column(Float, nullable=False, default=20.00)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

class Holdings(Base):
    __tablename__ = "holdings"
    
    id = Column(Integer, primary_key=True, index=True)
    symbol = Column(String(10), nullable=False, index=True)
    quantity = Column(Integer, nullable=False)
    average_cost = Column(Float, nullable=False)
    current_price = Column(Float, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

class Trades(Base):
    __tablename__ = "trades"
    
    id = Column(Integer, primary_key=True, index=True)
    symbol = Column(String(10), nullable=False, index=True)
    action = Column(Enum(TradeAction), nullable=False)
    quantity = Column(Integer, nullable=False)
    price = Column(Float, nullable=False)
    total_amount = Column(Float, nullable=False)
    ai_reasoning = Column(Text, nullable=True)
    executed_at = Column(DateTime(timezone=True), server_default=func.now())

class BotConfig(Base):
    __tablename__ = "bot_config"
    
    id = Column(Integer, primary_key=True, index=True)
    max_daily_trades = Column(Integer, nullable=False, default=5)
    max_position_size = Column(Float, nullable=False, default=0.20)  # 20% of portfolio
    risk_tolerance = Column(Enum(RiskTolerance), nullable=False, default=RiskTolerance.MEDIUM)
    trading_hours_start = Column(String(5), nullable=False, default="09:30")  # HH:MM format
    trading_hours_end = Column(String(5), nullable=False, default="16:00")    # HH:MM format
    is_active = Column(Boolean, nullable=False, default=False)
    stop_loss_percentage = Column(Float, nullable=False, default=-0.10)  # -10%
    take_profit_percentage = Column(Float, nullable=False, default=0.15)  # +15%
    min_cash_reserve = Column(Float, nullable=False, default=5.00)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

class MarketData(Base):
    __tablename__ = "market_data"
    
    id = Column(Integer, primary_key=True, index=True)
    symbol = Column(String(10), nullable=False, index=True)
    price = Column(Float, nullable=False)
    volume = Column(Integer, nullable=True)
    change_percent = Column(Float, nullable=True)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())

class TradingLog(Base):
    __tablename__ = "trading_log"
    
    id = Column(Integer, primary_key=True, index=True)
    level = Column(String(10), nullable=False)  # INFO, WARNING, ERROR
    message = Column(Text, nullable=False)
    symbol = Column(String(10), nullable=True)
    trade_id = Column(Integer, nullable=True)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())

class ActivityLog(Base):
    __tablename__ = "activity_log"
    
    id = Column(Integer, primary_key=True, index=True)
    action = Column(String(50), nullable=False)  # BOT_STARTED, BOT_STOPPED, MARKET_CHECK, etc.
    details = Column(Text, nullable=False)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
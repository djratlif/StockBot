import yfinance as yf
import pandas as pd
from typing import Dict, List, Optional
from datetime import datetime, timedelta
import logging
from app.models.schemas import StockInfo, MarketDataResponse
from app.models.models import MarketData
from sqlalchemy.orm import Session
from app.services.alpha_vantage_service import alpha_vantage_service

logger = logging.getLogger(__name__)

class StockService:
    def __init__(self):
        self.cache = {}
        self.cache_duration = timedelta(minutes=1)  # Cache for 1 minute
        self.use_alpha_vantage = True  # Primary data source
    
    def get_stock_info(self, symbol: str) -> Optional[StockInfo]:
        """Get comprehensive stock information with Alpha Vantage primary, Yahoo Finance fallback"""
        try:
            # Check cache first
            cache_key = f"{symbol}_info"
            if self._is_cached(cache_key):
                return self.cache[cache_key]["data"]
            
            # Try Alpha Vantage first
            if self.use_alpha_vantage:
                try:
                    stock_info = alpha_vantage_service.get_stock_info(symbol)
                    if stock_info:
                        logger.info(f"Successfully fetched {symbol} data from Alpha Vantage")
                        self._cache_data(cache_key, stock_info)
                        return stock_info
                except Exception as e:
                    logger.warning(f"Alpha Vantage failed for {symbol}: {str(e)}, falling back to Yahoo Finance")
            
            # Fallback to Yahoo Finance
            logger.info(f"Using Yahoo Finance fallback for {symbol}")
            ticker = yf.Ticker(symbol)
            info = ticker.info
            hist = ticker.history(period="1d")
            
            if hist.empty:
                logger.warning(f"No data found for symbol: {symbol}")
                return None
            
            current_price = hist['Close'].iloc[-1]
            previous_close = info.get('previousClose', current_price)
            change_percent = ((current_price - previous_close) / previous_close) * 100 if previous_close else 0
            
            stock_info = StockInfo(
                symbol=symbol.upper(),
                current_price=float(current_price),
                change_percent=float(change_percent),
                volume=int(hist['Volume'].iloc[-1]) if not hist['Volume'].empty else 0,
                market_cap=info.get('marketCap'),
                pe_ratio=info.get('trailingPE'),
                week_52_high=info.get('fiftyTwoWeekHigh'),
                week_52_low=info.get('fiftyTwoWeekLow')
            )
            
            # Cache the result
            self._cache_data(cache_key, stock_info)
            return stock_info
            
        except Exception as e:
            logger.error(f"Error fetching stock info for {symbol}: {str(e)}")
            return None
    
    def get_current_price(self, symbol: str) -> Optional[float]:
        """Get current stock price with Alpha Vantage primary, Yahoo Finance fallback"""
        try:
            # Check cache first
            cache_key = f"{symbol}_price"
            if self._is_cached(cache_key):
                return self.cache[cache_key]["data"]
            
            # Try Alpha Vantage first
            if self.use_alpha_vantage:
                try:
                    current_price = alpha_vantage_service.get_current_price(symbol)
                    if current_price:
                        logger.info(f"Successfully fetched {symbol} price from Alpha Vantage: ${current_price}")
                        self._cache_data(cache_key, current_price)
                        return current_price
                except Exception as e:
                    logger.warning(f"Alpha Vantage price fetch failed for {symbol}: {str(e)}, falling back to Yahoo Finance")
            
            # Fallback to Yahoo Finance
            logger.info(f"Using Yahoo Finance fallback for {symbol} price")
            ticker = yf.Ticker(symbol)
            hist = ticker.history(period="1d")
            
            if hist.empty:
                return None
            
            current_price = float(hist['Close'].iloc[-1])
            
            # Cache the result
            self._cache_data(cache_key, current_price)
            return current_price
            
        except Exception as e:
            logger.error(f"Error fetching price for {symbol}: {str(e)}")
            return None
    
    def get_historical_data(self, symbol: str, period: str = "1mo") -> Optional[pd.DataFrame]:
        """Get historical stock data"""
        try:
            ticker = yf.Ticker(symbol)
            hist = ticker.history(period=period)
            return hist if not hist.empty else None
        except Exception as e:
            logger.error(f"Error fetching historical data for {symbol}: {str(e)}")
            return None
    
    def get_trending_stocks(self) -> List[str]:
        """Get list of trending stock symbols"""
        # For now, return a curated list of popular stocks
        # In production, this could be enhanced with actual trending data
        return [
            "AAPL", "GOOGL", "MSFT", "AMZN", "TSLA",
            "META", "NVDA", "NFLX", "AMD", "INTC",
            "SPY", "QQQ", "IWM", "DIA", "VTI"
        ]
    
    def validate_symbol(self, symbol: str) -> bool:
        """Validate if a stock symbol exists"""
        try:
            ticker = yf.Ticker(symbol)
            info = ticker.info
            return 'symbol' in info or 'shortName' in info
        except:
            return False
    
    def get_market_status(self) -> Dict[str, bool]:
        """Check if market is currently open"""
        try:
            # Get current time in EST
            from datetime import datetime
            import pytz
            
            est = pytz.timezone('US/Eastern')
            now = datetime.now(est)
            
            # Market hours: 9:30 AM - 4:00 PM EST, Monday-Friday
            is_weekday = now.weekday() < 5  # Monday = 0, Friday = 4
            market_open = now.time() >= datetime.strptime("09:30", "%H:%M").time()
            market_close = now.time() <= datetime.strptime("16:00", "%H:%M").time()
            
            is_market_open = is_weekday and market_open and market_close
            
            return {
                "is_open": is_market_open,
                "is_weekday": is_weekday,
                "current_time": now.strftime("%H:%M:%S EST"),
                "next_open": self._get_next_market_open(now)
            }
        except Exception as e:
            logger.error(f"Error checking market status: {str(e)}")
            return {"is_open": False, "error": str(e)}
    
    def save_market_data(self, db: Session, symbol: str, price: float, 
                        volume: Optional[int] = None, change_percent: Optional[float] = None):
        """Save market data to database"""
        try:
            market_data = MarketData(
                symbol=symbol.upper(),
                price=price,
                volume=volume,
                change_percent=change_percent
            )
            db.add(market_data)
            db.commit()
            db.refresh(market_data)
            return market_data
        except Exception as e:
            logger.error(f"Error saving market data: {str(e)}")
            db.rollback()
            return None
    
    def _is_cached(self, key: str) -> bool:
        """Check if data is cached and still valid"""
        if key not in self.cache:
            return False
        
        cached_time = self.cache[key]["timestamp"]
        return datetime.now() - cached_time < self.cache_duration
    
    def _cache_data(self, key: str, data):
        """Cache data with timestamp"""
        self.cache[key] = {
            "data": data,
            "timestamp": datetime.now()
        }
    
    def _get_next_market_open(self, current_time) -> str:
        """Calculate next market open time"""
        try:
            # Simple logic - can be enhanced for holidays
            if current_time.weekday() >= 5:  # Weekend
                days_until_monday = 7 - current_time.weekday()
                next_open = current_time + timedelta(days=days_until_monday)
                next_open = next_open.replace(hour=9, minute=30, second=0, microsecond=0)
            else:  # Weekday
                if current_time.time() > datetime.strptime("16:00", "%H:%M").time():
                    # After market close, next day
                    next_open = current_time + timedelta(days=1)
                    next_open = next_open.replace(hour=9, minute=30, second=0, microsecond=0)
                else:
                    # Before market open today
                    next_open = current_time.replace(hour=9, minute=30, second=0, microsecond=0)
            
            return next_open.strftime("%Y-%m-%d %H:%M:%S EST")
        except:
            return "Unknown"

# Global instance
stock_service = StockService()
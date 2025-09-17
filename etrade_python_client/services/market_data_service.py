"""Market data service using Yahoo Finance for real-time data and news."""

import asyncio
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from decimal import Decimal

import yfinance as yf
import pandas as pd
from sqlalchemy.ext.asyncio import AsyncSession

from ..database.models import MarketSentiment
from ..utils.config_manager import ConfigManager

logger = logging.getLogger(__name__)


class MarketDataService:
    """Service for fetching market data and news from Yahoo Finance."""
    
    def __init__(self):
        self.config_manager = ConfigManager()
    
    async def get_real_time_quote(self, symbol: str) -> Dict[str, Any]:
        """
        Get real-time quote data for a symbol.
        
        Args:
            symbol: Stock symbol (e.g., 'AAPL')
            
        Returns:
            Dictionary containing current quote data
        """
        try:
            # Run yfinance in thread to avoid blocking
            ticker = await asyncio.to_thread(yf.Ticker, symbol)
            info = await asyncio.to_thread(lambda: ticker.info)
            
            # Extract key quote data
            quote_data = {
                'symbol': symbol,
                'current_price': info.get('currentPrice', 0.0),
                'previous_close': info.get('previousClose', 0.0),
                'day_high': info.get('dayHigh', 0.0),
                'day_low': info.get('dayLow', 0.0),
                'volume': info.get('volume', 0),
                'market_cap': info.get('marketCap', 0),
                'pe_ratio': info.get('forwardPE', 0.0),
                'timestamp': datetime.now(),
                'change': 0.0,
                'change_percent': 0.0
            }
            
            # Calculate price change
            current = quote_data['current_price']
            previous = quote_data['previous_close']
            
            if previous and previous > 0:
                quote_data['change'] = current - previous
                quote_data['change_percent'] = (quote_data['change'] / previous) * 100
            
            logger.info(f"📈 Quote for {symbol}: ${current:.2f} ({quote_data['change_percent']:+.2f}%)")
            return quote_data
            
        except Exception as e:
            logger.error(f"❌ Failed to get quote for {symbol}: {e}")
            return {
                'symbol': symbol,
                'error': str(e),
                'timestamp': datetime.now()
            }
    
    async def get_historical_data(
        self,
        symbol: str,
        period: str = "1mo",
        interval: str = "1d"
    ) -> Dict[str, Any]:
        """
        Get historical price data for technical analysis.
        
        Args:
            symbol: Stock symbol
            period: Data period (1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, ytd, max)
            interval: Data interval (1m, 2m, 5m, 15m, 30m, 60m, 90m, 1h, 1d, 5d, 1wk, 1mo, 3mo)
            
        Returns:
            Dictionary containing historical data and technical indicators
        """
        try:
            ticker = await asyncio.to_thread(yf.Ticker, symbol)
            hist = await asyncio.to_thread(
                lambda: ticker.history(period=period, interval=interval)
            )
            
            if hist.empty:
                return {'symbol': symbol, 'error': 'No historical data available'}
            
            # Calculate technical indicators
            technical_data = await self._calculate_technical_indicators(hist)
            
            # Convert to serializable format
            historical_data = {
                'symbol': symbol,
                'period': period,
                'interval': interval,
                'data_points': len(hist),
                'latest_close': float(hist['Close'].iloc[-1]),
                'latest_volume': int(hist['Volume'].iloc[-1]),
                'high_52w': float(hist['High'].max()),
                'low_52w': float(hist['Low'].min()),
                'avg_volume': int(hist['Volume'].mean()),
                'technical_indicators': technical_data,
                'timestamp': datetime.now()
            }
            
            logger.info(f"📊 Historical data for {symbol}: {len(hist)} data points")
            return historical_data
            
        except Exception as e:
            logger.error(f"❌ Failed to get historical data for {symbol}: {e}")
            return {
                'symbol': symbol,
                'error': str(e),
                'timestamp': datetime.now()
            }
    
    async def _calculate_technical_indicators(self, hist: pd.DataFrame) -> Dict[str, float]:
        """Calculate basic technical indicators from historical data."""
        try:
            indicators = {}
            
            # Simple Moving Averages
            if len(hist) >= 20:
                indicators['sma_20'] = float(hist['Close'].rolling(window=20).mean().iloc[-1])
            if len(hist) >= 50:
                indicators['sma_50'] = float(hist['Close'].rolling(window=50).mean().iloc[-1])
            
            # Relative Strength Index (RSI)
            if len(hist) >= 14:
                delta = hist['Close'].diff()
                gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
                loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
                rs = gain / loss
                rsi = 100 - (100 / (1 + rs))
                indicators['rsi'] = float(rsi.iloc[-1])
            
            # Bollinger Bands
            if len(hist) >= 20:
                sma_20 = hist['Close'].rolling(window=20).mean()
                std_20 = hist['Close'].rolling(window=20).std()
                indicators['bb_upper'] = float((sma_20 + (std_20 * 2)).iloc[-1])
                indicators['bb_lower'] = float((sma_20 - (std_20 * 2)).iloc[-1])
                indicators['bb_width'] = indicators['bb_upper'] - indicators['bb_lower']
            
            # Price position within recent range
            if len(hist) >= 5:
                recent_high = hist['High'].tail(5).max()
                recent_low = hist['Low'].tail(5).min()
                current_price = hist['Close'].iloc[-1]
                
                if recent_high != recent_low:
                    indicators['price_position'] = float(
                        (current_price - recent_low) / (recent_high - recent_low)
                    )
            
            return indicators
            
        except Exception as e:
            logger.error(f"❌ Failed to calculate technical indicators: {e}")
            return {}
    
    async def get_news_headlines(self, symbol: str, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get recent news headlines for a symbol.
        
        Args:
            symbol: Stock symbol
            limit: Maximum number of headlines to return
            
        Returns:
            List of news headline dictionaries
        """
        try:
            ticker = await asyncio.to_thread(yf.Ticker, symbol)
            news = await asyncio.to_thread(lambda: ticker.news)
            
            if not news:
                return []
            
            # Process and clean news data
            headlines = []
            for item in news[:limit]:
                headline = {
                    'title': item.get('title', ''),
                    'summary': item.get('summary', ''),
                    'publisher': item.get('publisher', ''),
                    'publish_time': datetime.fromtimestamp(
                        item.get('providerPublishTime', 0)
                    ) if item.get('providerPublishTime') else datetime.now(),
                    'url': item.get('link', ''),
                    'symbol': symbol
                }
                headlines.append(headline)
            
            logger.info(f"📰 Found {len(headlines)} news headlines for {symbol}")
            return headlines
            
        except Exception as e:
            logger.error(f"❌ Failed to get news for {symbol}: {e}")
            return []
    
    async def analyze_market_sentiment_batch(
        self,
        symbols: List[str],
        db: AsyncSession
    ) -> Dict[str, float]:
        """
        Analyze market sentiment for multiple symbols and store in database.
        
        Args:
            symbols: List of stock symbols to analyze
            db: Database session
            
        Returns:
            Dictionary mapping symbols to sentiment scores
        """
        sentiment_results = {}
        
        for symbol in symbols:
            try:
                # Get news headlines
                headlines = await self.get_news_headlines(symbol, limit=5)
                
                if not headlines:
                    sentiment_results[symbol] = 0.0
                    continue
                
                # Simple sentiment analysis based on keywords
                sentiment_score = await self._analyze_news_sentiment(headlines)
                sentiment_results[symbol] = sentiment_score
                
                # Store in database
                news_summary = '; '.join([h['title'] for h in headlines[:3]])
                
                market_sentiment = MarketSentiment(
                    symbol=symbol,
                    sentiment_score=sentiment_score,
                    news_summary=news_summary,
                    source_count=len(headlines)
                )
                
                db.add(market_sentiment)
                
                logger.info(f"📊 Sentiment for {symbol}: {sentiment_score:.2f}")
                
            except Exception as e:
                logger.error(f"❌ Failed sentiment analysis for {symbol}: {e}")
                sentiment_results[symbol] = 0.0
        
        await db.commit()
        return sentiment_results
    
    async def _analyze_news_sentiment(self, headlines: List[Dict[str, Any]]) -> float:
        """
        Perform simple keyword-based sentiment analysis on news headlines.
        
        This is a basic implementation. In production, you might use:
        - More sophisticated NLP models
        - External sentiment analysis APIs
        - Pre-trained financial sentiment models
        """
        positive_keywords = [
            'beats', 'exceeds', 'strong', 'growth', 'rise', 'gain', 'up',
            'bull', 'positive', 'outperform', 'upgrade', 'buy', 'bullish',
            'rally', 'surge', 'jump', 'soar', 'boost', 'optimistic'
        ]
        
        negative_keywords = [
            'misses', 'falls', 'decline', 'drop', 'down', 'bear', 'negative',
            'underperform', 'downgrade', 'sell', 'bearish', 'crash', 'plunge',
            'tumble', 'slump', 'concern', 'worry', 'risk', 'pessimistic'
        ]
        
        total_score = 0.0
        total_weight = 0.0
        
        for headline in headlines:
            text = (headline.get('title', '') + ' ' + headline.get('summary', '')).lower()
            
            positive_count = sum(1 for keyword in positive_keywords if keyword in text)
            negative_count = sum(1 for keyword in negative_keywords if keyword in text)
            
            # Weight recent news more heavily
            age_hours = (datetime.now() - headline.get('publish_time', datetime.now())).total_seconds() / 3600
            weight = max(0.1, 1.0 - (age_hours / 72))  # Decay over 3 days
            
            if positive_count + negative_count > 0:
                headline_sentiment = (positive_count - negative_count) / (positive_count + negative_count)
                total_score += headline_sentiment * weight
                total_weight += weight
        
        if total_weight > 0:
            final_sentiment = total_score / total_weight
        else:
            final_sentiment = 0.0
        
        # Clamp to [-1, 1] range
        return max(-1.0, min(1.0, final_sentiment))
    
    async def get_market_overview(self) -> Dict[str, Any]:
        """
        Get overall market overview with major indices.
        
        Returns:
            Dictionary containing market overview data
        """
        indices = {
            'S&P 500': '^GSPC',
            'Dow Jones': '^DJI',
            'NASDAQ': '^IXIC',
            'Russell 2000': '^RUT',
            'VIX': '^VIX'
        }
        
        market_data = {}
        
        for name, symbol in indices.items():
            try:
                quote = await self.get_real_time_quote(symbol)
                market_data[name] = {
                    'price': quote.get('current_price', 0.0),
                    'change': quote.get('change', 0.0),
                    'change_percent': quote.get('change_percent', 0.0)
                }
            except Exception as e:
                logger.error(f"❌ Failed to get data for {name}: {e}")
                market_data[name] = {'error': str(e)}
        
        market_data['timestamp'] = datetime.now()
        return market_data
    
    async def get_watchlist_data(self, symbols: List[str]) -> List[Dict[str, Any]]:
        """
        Get comprehensive data for a list of symbols (watchlist) using a single batch request.
        """
        if not symbols:
            return []

        try:
            # Use yf.Tickers for batch requests
            tickers = await asyncio.to_thread(yf.Tickers, ' '.join(symbols))
            
            # Fetch historical data for all tickers at once
            hist_df = await asyncio.to_thread(tickers.history, period="1mo", interval="1d")
            
            watchlist_data = []
            for symbol in symbols:
                try:
                    ticker_info = tickers.tickers[symbol].info
                    
                    # Process quote data
                    quote_data = {
                        'symbol': symbol,
                        'current_price': ticker_info.get('currentPrice', 0.0),
                        'previous_close': ticker_info.get('previousClose', 0.0),
                        'day_high': ticker_info.get('dayHigh', 0.0),
                        'day_low': ticker_info.get('dayLow', 0.0),
                        'volume': ticker_info.get('volume', 0),
                        'market_cap': ticker_info.get('marketCap', 0),
                        'pe_ratio': ticker_info.get('forwardPE', 0.0),
                        'timestamp': datetime.now(),
                        'change': 0.0,
                        'change_percent': 0.0
                    }
                    current = quote_data['current_price']
                    previous = quote_data['previous_close']
                    if previous and previous > 0:
                        quote_data['change'] = current - previous
                        quote_data['change_percent'] = (quote_data['change'] / previous) * 100

                    # Process historical data and technical indicators
                    hist_symbol_df = hist_df.xs(symbol, level=1, axis=1)
                    technical_data = await self._calculate_technical_indicators(hist_symbol_df)
                    
                    historical_data = {
                        'symbol': symbol,
                        'period': '1mo',
                        'interval': '1d',
                        'data_points': len(hist_symbol_df),
                        'latest_close': float(hist_symbol_df['Close'].iloc[-1]),
                        'latest_volume': int(hist_symbol_df['Volume'].iloc[-1]),
                        'high_52w': float(hist_symbol_df['High'].max()),
                        'low_52w': float(hist_symbol_df['Low'].min()),
                        'avg_volume': int(hist_symbol_df['Volume'].mean()),
                        'technical_indicators': technical_data,
                        'timestamp': datetime.now()
                    }

                    watchlist_data.append({
                        'symbol': symbol,
                        'quote': quote_data,
                        'historical': historical_data,
                        'timestamp': datetime.now()
                    })

                except Exception as e:
                    logger.error(f"❌ Failed to process data for {symbol} in batch: {e}")
                    watchlist_data.append({
                        'symbol': symbol,
                        'error': f"Failed to process data: {e}",
                        'timestamp': datetime.now()
                    })

            return watchlist_data

        except Exception as e:
            logger.error(f"❌ Failed to get watchlist data in batch: {e}")
            return [{'symbol': s, 'error': str(e), 'timestamp': datetime.now()} for s in symbols]
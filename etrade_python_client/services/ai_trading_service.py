"""AI Trading Service using Google Gemini for analysis and decision making."""

import json
import asyncio
import logging
from typing import Dict, List, Optional, Tuple
from datetime import datetime
from decimal import Decimal

import google.generativeai as genai
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from ..database.models import AIDecision, MarketSentiment, UserPreferences, DecisionType
from ..utils.config_manager import ConfigManager

logger = logging.getLogger(__name__)


class AITradingService:
    """AI Trading service using Google Gemini for intelligent trading decisions."""
    
    def __init__(self):
        self.config_manager = ConfigManager()
        self.model = None
        self._initialize_gemini()
    
    def _initialize_gemini(self):
        """Initialize Google Gemini AI model."""
        try:
            api_key = self.config_manager.get_gemini_api_key()
            if api_key == "your_gemini_api_key":
                logger.warning("⚠️ Gemini API key not configured. AI features will be limited.")
                return
            
            genai.configure(api_key=api_key)
            self.model = genai.GenerativeModel('gemini-1.5-flash')
            logger.info("✅ Gemini AI model initialized successfully")
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize Gemini: {e}")
            self.model = None
    
    async def analyze_market_sentiment(
        self,
        symbol: str,
        market_data: Dict,
        news_summaries: List[str]
    ) -> Tuple[float, str]:
        """
        Analyze market sentiment for a given symbol.
        
        Args:
            symbol: Stock symbol (e.g., 'AAPL')
            market_data: Current market data for the symbol
            news_summaries: List of recent news summaries
            
        Returns:
            Tuple of (sentiment_score, analysis_summary)
        """
        if not self.model:
            logger.warning("Gemini model not available, using fallback sentiment analysis")
            return await self._fallback_sentiment_analysis(symbol, market_data, news_summaries)
        
        try:
            # Prepare prompt for sentiment analysis
            prompt = f"""
            Analyze the market sentiment for {symbol} based on the following data:
            
            Market Data:
            {json.dumps(market_data, indent=2, default=str)}
            
            Recent News:
            {chr(10).join(news_summaries[:5])}  # Limit to 5 news items
            
            Please provide:
            1. A sentiment score between -1.0 (very negative) and 1.0 (very positive)
            2. A brief analysis summary explaining the sentiment
            
            Format your response as JSON:
            {{
                "sentiment_score": 0.0,
                "summary": "Analysis summary here"
            }}
            """
            
            response = await asyncio.to_thread(
                self.model.generate_content, prompt
            )
            
            # Parse AI response
            result = json.loads(response.text.strip())
            sentiment_score = float(result.get('sentiment_score', 0.0))
            summary = result.get('summary', 'No analysis available')
            
            # Clamp sentiment score to valid range
            sentiment_score = max(-1.0, min(1.0, sentiment_score))
            
            logger.info(f"📊 Sentiment analysis for {symbol}: {sentiment_score}")
            return sentiment_score, summary
            
        except Exception as e:
            logger.error(f"❌ Gemini sentiment analysis failed: {e}")
            return await self._fallback_sentiment_analysis(symbol, market_data, news_summaries)
    
    async def generate_trading_decision(
        self,
        symbol: str,
        portfolio_data: Dict,
        market_data: Dict,
        sentiment_data: Dict,
        user_preferences: UserPreferences
    ) -> Optional[AIDecision]:
        """
        Generate an AI trading decision based on comprehensive analysis.
        
        Args:
            symbol: Stock symbol to analyze
            portfolio_data: Current portfolio information
            market_data: Real-time market data
            sentiment_data: Market sentiment analysis
            user_preferences: User trading preferences
            
        Returns:
            AIDecision object or None if no decision recommended
        """
        if not self.model:
            logger.warning("Gemini model not available, using fallback decision logic")
            return await self._fallback_trading_decision(
                symbol, portfolio_data, market_data, sentiment_data, user_preferences
            )
        
        try:
            # Prepare comprehensive prompt
            prompt = f"""
            You are an expert AI trading advisor. Analyze the following data for {symbol} and provide a trading recommendation:
            
            Portfolio Data:
            {json.dumps(portfolio_data, indent=2, default=str)}
            
            Market Data:
            {json.dumps(market_data, indent=2, default=str)}
            
            Sentiment Analysis:
            {json.dumps(sentiment_data, indent=2, default=str)}
            
            User Preferences:
            - Risk Tolerance: {user_preferences.risk_tolerance.value}
            - Max Trade Amount: ${user_preferences.max_trade_amount}
            - Auto Trading: {user_preferences.auto_trading_enabled}
            
            Consider:
            1. Technical indicators from market data
            2. Market sentiment and news impact
            3. Portfolio diversification
            4. Risk management based on user preferences
            5. Current market conditions
            
            Provide a recommendation in JSON format:
            {{
                "decision": "BUY|SELL|HOLD",
                "confidence": 0.85,
                "rationale": "Detailed explanation of the decision",
                "price_target": 150.00,
                "risk_assessment": "LOW|MEDIUM|HIGH"
            }}
            
            Only recommend BUY/SELL if confidence > 0.7 and the decision aligns with user risk tolerance.
            """
            
            response = await asyncio.to_thread(
                self.model.generate_content, prompt
            )
            
            # Parse AI decision
            result = json.loads(response.text.strip())
            
            decision_type_str = result.get('decision', 'HOLD').upper()
            confidence = float(result.get('confidence', 0.0))
            rationale = result.get('rationale', 'No rationale provided')
            price_target = result.get('price_target')
            risk_assessment = result.get('risk_assessment', 'MEDIUM')
            
            # Validate decision type
            try:
                decision_type = DecisionType(decision_type_str)
            except ValueError:
                logger.warning(f"Invalid decision type '{decision_type_str}', defaulting to HOLD")
                decision_type = DecisionType.HOLD
            
            # Apply confidence and risk filters
            confidence_threshold = self.config_manager.get_ai_confidence_threshold()
            
            if confidence < confidence_threshold:
                logger.info(f"Decision confidence {confidence} below threshold {confidence_threshold}")
                decision_type = DecisionType.HOLD
                rationale += f" (Confidence below threshold: {confidence})"
            
            # Create AI decision record
            ai_decision = AIDecision(
                symbol=symbol,
                decision_type=decision_type,
                confidence_score=confidence,
                rationale=rationale,
                price_target=Decimal(str(price_target)) if price_target else None
            )
            
            logger.info(f"🤖 AI Decision for {symbol}: {decision_type.value} (confidence: {confidence})")
            return ai_decision
            
        except Exception as e:
            logger.error(f"❌ Gemini trading decision failed: {e}")
            return await self._fallback_trading_decision(
                symbol, portfolio_data, market_data, sentiment_data, user_preferences
            )
    
    async def _fallback_sentiment_analysis(
        self,
        symbol: str,
        market_data: Dict,
        news_summaries: List[str]
    ) -> Tuple[float, str]:
        """Fallback sentiment analysis when Gemini is unavailable."""
        # Simple rule-based sentiment analysis
        sentiment_score = 0.0
        
        # Analyze price movement
        if 'change_percent' in market_data:
            change_pct = float(market_data.get('change_percent', 0))
            sentiment_score += change_pct / 100.0  # Convert percentage to decimal
        
        # Basic news sentiment (count positive/negative keywords)
        positive_words = ['up', 'gain', 'rise', 'bull', 'positive', 'strong', 'growth']
        negative_words = ['down', 'fall', 'drop', 'bear', 'negative', 'weak', 'decline']
        
        news_text = ' '.join(news_summaries).lower()
        positive_count = sum(1 for word in positive_words if word in news_text)
        negative_count = sum(1 for word in negative_words if word in news_text)
        
        if positive_count + negative_count > 0:
            news_sentiment = (positive_count - negative_count) / (positive_count + negative_count)
            sentiment_score += news_sentiment * 0.3  # Weight news sentiment
        
        # Clamp to valid range
        sentiment_score = max(-1.0, min(1.0, sentiment_score))
        
        summary = f"Fallback analysis: {positive_count} positive, {negative_count} negative signals"
        
        return sentiment_score, summary
    
    async def _fallback_trading_decision(
        self,
        symbol: str,
        portfolio_data: Dict,
        market_data: Dict,
        sentiment_data: Dict,
        user_preferences: UserPreferences
    ) -> Optional[AIDecision]:
        """Fallback trading decision logic when Gemini is unavailable."""
        
        # Simple rule-based decision making
        decision_type = DecisionType.HOLD
        confidence = 0.5
        rationale = "Fallback analysis: "
        
        # Analyze sentiment
        sentiment_score = sentiment_data.get('sentiment_score', 0.0)
        
        # Basic decision logic
        if sentiment_score > 0.3:
            decision_type = DecisionType.BUY
            confidence = 0.6
            rationale += f"Positive sentiment ({sentiment_score:.2f})"
        elif sentiment_score < -0.3:
            decision_type = DecisionType.SELL
            confidence = 0.6
            rationale += f"Negative sentiment ({sentiment_score:.2f})"
        else:
            rationale += f"Neutral sentiment ({sentiment_score:.2f}), holding position"
        
        # Apply confidence threshold
        confidence_threshold = self.config_manager.get_ai_confidence_threshold()
        if confidence < confidence_threshold:
            decision_type = DecisionType.HOLD
            rationale += f" (Below confidence threshold)"
        
        return AIDecision(
            symbol=symbol,
            decision_type=decision_type,
            confidence_score=confidence,
            rationale=rationale
        )
    
    async def learn_from_feedback(
        self,
        decision: AIDecision,
        actual_outcome: Optional[Decimal] = None
    ):
        """
        Learn from user feedback and actual outcomes to improve future decisions.
        
        This would typically update AI learning parameters, but for now we'll
        log the feedback for future ML model training.
        """
        feedback_data = {
            'decision_id': decision.decision_id,
            'symbol': decision.symbol,
            'decision_type': decision.decision_type.value,
            'confidence': decision.confidence_score,
            'user_feedback': decision.user_feedback.value if decision.user_feedback else None,
            'actual_outcome': float(actual_outcome) if actual_outcome else None,
            'timestamp': datetime.now().isoformat()
        }
        
        logger.info(f"📚 Learning from feedback: {feedback_data}")
        
        # In a full implementation, this would:
        # 1. Update ML model parameters
        # 2. Adjust confidence thresholds
        # 3. Update decision-making weights
        # For now, we just log the feedback
        
        return feedback_data
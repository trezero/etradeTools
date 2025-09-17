"""Notification service for email and Slack alerts."""

import smtplib
import ssl
import logging
from datetime import datetime
from typing import Dict, List, Optional, Any
import asyncio

try:
    from slack_sdk import WebClient
    from slack_sdk.errors import SlackApiError
    SLACK_AVAILABLE = True
except ImportError:
    SLACK_AVAILABLE = False

from ..database.models import AIDecision, PortfolioAnalytics, DecisionType
from ..utils.config_manager import ConfigManager

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class NotificationService:
    """Service for sending email and Slack notifications."""
    
    def __init__(self):
        self.config_manager = ConfigManager()
        self.smtp_server = None
        self.slack_client = None
        self._initialize_services()
    
    def _initialize_services(self):
        """Initialize email and Slack services."""
        # Initialize SMTP
        try:
            smtp_host = self.config_manager.config.get('NOTIFICATIONS', 'smtp_host', fallback='')
            smtp_port = self.config_manager.config.getint('NOTIFICATIONS', 'smtp_port', fallback=587)
            smtp_username = self.config_manager.config.get('NOTIFICATIONS', 'smtp_username', fallback='')
            smtp_password = self.config_manager.config.get('NOTIFICATIONS', 'smtp_password', fallback='')
            
            if smtp_host and smtp_username and smtp_password:
                self.smtp_config = {
                    'host': smtp_host,
                    'port': smtp_port,
                    'username': smtp_username,
                    'password': smtp_password,
                    'use_tls': self.config_manager.config.getboolean('NOTIFICATIONS', 'smtp_use_tls', fallback=True)
                }
                logger.info("📧 Email service initialized")
            else:
                self.smtp_config = None
                logger.info("📧 Email service not configured")
                
        except Exception as e:
            logger.error(f"❌ Failed to initialize email service: {e}")
            self.smtp_config = None
        
        # Initialize Slack
        try:
            if SLACK_AVAILABLE:
                slack_token = self.config_manager.config.get('NOTIFICATIONS', 'slack_bot_token', fallback='')
                slack_channel = self.config_manager.config.get('NOTIFICATIONS', 'slack_channel', fallback='')
                
                if slack_token and slack_channel:
                    self.slack_client = WebClient(token=slack_token)
                    self.slack_channel = slack_channel
                    logger.info("📱 Slack service initialized")
                else:
                    self.slack_client = None
                    logger.info("📱 Slack service not configured")
            else:
                logger.warning("📱 Slack SDK not available - install slack_sdk package")
                self.slack_client = None
                
        except Exception as e:
            logger.error(f"❌ Failed to initialize Slack service: {e}")
            self.slack_client = None
    
    async def send_trading_alert(
        self, 
        decision: AIDecision, 
        market_data: Dict[str, Any],
        recipients: Optional[List[str]] = None
    ) -> Dict[str, bool]:
        """
        Send trading alert notification.
        
        Args:
            decision: AI trading decision
            market_data: Current market data
            recipients: List of email recipients (optional)
            
        Returns:
            Dict with success status for each service
        """
        try:
            subject = f"🤖 AI Trading Alert: {decision.decision_type.value} {decision.symbol}"
            
            # Format decision details
            current_price = market_data.get('current_price', 0)
            change_percent = market_data.get('change_percent', 0)
            volume = market_data.get('volume', 0)
            
            # Create message content
            message_content = self._format_trading_alert(
                decision, current_price, change_percent, volume
            )
            
            results = {}
            
            # Send email notification
            if self.smtp_config and recipients:
                email_result = await self._send_email(
                    subject=subject,
                    content=message_content,
                    recipients=recipients,
                    is_html=True
                )
                results['email'] = email_result
            else:
                results['email'] = False
                logger.info("📧 Email notification skipped (not configured or no recipients)")
            
            # Send Slack notification
            if self.slack_client:
                slack_result = await self._send_slack_message(
                    message=self._format_slack_trading_alert(decision, current_price, change_percent),
                    channel=self.slack_channel
                )
                results['slack'] = slack_result
            else:
                results['slack'] = False
                logger.info("📱 Slack notification skipped (not configured)")
            
            return results
            
        except Exception as e:
            logger.error(f"❌ Failed to send trading alert: {e}")
            return {'email': False, 'slack': False}
    
    async def send_system_alert(
        self, 
        title: str, 
        message: str, 
        severity: str = 'info',
        recipients: Optional[List[str]] = None
    ) -> Dict[str, bool]:
        """
        Send system alert notification.
        
        Args:
            title: Alert title
            message: Alert message
            severity: Alert severity (info, warning, error)
            recipients: List of email recipients (optional)
            
        Returns:
            Dict with success status for each service
        """
        try:
            # Add emoji based on severity
            emoji_map = {
                'info': '💡',
                'warning': '⚠️',
                'error': '🚨',
                'success': '✅'
            }
            emoji = emoji_map.get(severity, '📢')
            
            subject = f"{emoji} Trading System Alert: {title}"
            
            results = {}
            
            # Send email notification
            if self.smtp_config and recipients:
                email_content = self._format_system_alert_email(title, message, severity)
                email_result = await self._send_email(
                    subject=subject,
                    content=email_content,
                    recipients=recipients,
                    is_html=True
                )
                results['email'] = email_result
            else:
                results['email'] = False
            
            # Send Slack notification
            if self.slack_client:
                slack_message = f"{emoji} *{title}*\n{message}"
                slack_result = await self._send_slack_message(
                    message=slack_message,
                    channel=self.slack_channel
                )
                results['slack'] = slack_result
            else:
                results['slack'] = False
            
            return results
            
        except Exception as e:
            logger.error(f"❌ Failed to send system alert: {e}")
            return {'email': False, 'slack': False}
    
    async def send_portfolio_summary(
        self, 
        analytics: PortfolioAnalytics,
        recipients: Optional[List[str]] = None
    ) -> Dict[str, bool]:
        """
        Send portfolio summary notification.
        
        Args:
            analytics: Portfolio analytics data
            recipients: List of email recipients (optional)
            
        Returns:
            Dict with success status for each service
        """
        try:
            subject = f"📊 Daily Portfolio Summary - {analytics.timestamp.strftime('%Y-%m-%d')}"
            
            results = {}
            
            # Send email notification
            if self.smtp_config and recipients:
                email_content = self._format_portfolio_summary_email(analytics)
                email_result = await self._send_email(
                    subject=subject,
                    content=email_content,
                    recipients=recipients,
                    is_html=True
                )
                results['email'] = email_result
            else:
                results['email'] = False
            
            # Send Slack notification
            if self.slack_client:
                slack_message = self._format_slack_portfolio_summary(analytics)
                slack_result = await self._send_slack_message(
                    message=slack_message,
                    channel=self.slack_channel
                )
                results['slack'] = slack_result
            else:
                results['slack'] = False
            
            return results
            
        except Exception as e:
            logger.error(f"❌ Failed to send portfolio summary: {e}")
            return {'email': False, 'slack': False}
    
    async def _send_email(
        self, 
        subject: str, 
        content: str, 
        recipients: List[str],
        is_html: bool = False
    ) -> bool:
        """Send email notification."""
        if not self.smtp_config:
            return False
            
        try:
            # Send email
            await asyncio.to_thread(self._send_smtp_email, content, subject, recipients)
            
            logger.info(f"📧 Email sent successfully to {len(recipients)} recipients")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to send email: {e}")
            return False
    
    def _send_smtp_email(self, msg_content: str, subject: str, recipients: List[str]):
        """Send SMTP email (synchronous)."""
        context = ssl.create_default_context()
        
        with smtplib.SMTP(self.smtp_config['host'], self.smtp_config['port']) as server:
            if self.smtp_config['use_tls']:
                server.starttls(context=context)
            
            server.login(self.smtp_config['username'], self.smtp_config['password'])
            
            # Create email message manually
            message = f"""Subject: {subject}
From: {self.smtp_config['username']}
To: {', '.join(recipients)}
Content-Type: text/html; charset=utf-8

{msg_content}"""
            
            server.sendmail(self.smtp_config['username'], recipients, message.encode('utf-8'))
    
    async def _send_slack_message(self, message: str, channel: str) -> bool:
        """Send Slack message."""
        if not self.slack_client:
            return False
            
        try:
            # Send message using Slack SDK
            response = await asyncio.to_thread(
                self.slack_client.chat_postMessage,
                channel=channel,
                text=message,
                mrkdwn=True
            )
            
            if response['ok']:
                logger.info(f"📱 Slack message sent successfully to {channel}")
                return True
            else:
                logger.error(f"❌ Slack API error: {response.get('error', 'Unknown error')}")
                return False
                
        except SlackApiError as e:
            logger.error(f"❌ Slack API error: {e.response['error']}")
            return False
        except Exception as e:
            logger.error(f"❌ Failed to send Slack message: {e}")
            return False
    
    def _format_trading_alert(
        self, 
        decision: AIDecision, 
        current_price: float, 
        change_percent: float, 
        volume: int
    ) -> str:
        """Format trading alert email content."""
        decision_color = {
            DecisionType.BUY: '#4caf50',
            DecisionType.SELL: '#f44336',
            DecisionType.HOLD: '#ff9800'
        }.get(decision.decision_type, '#9e9e9e')
        
        price_color = '#4caf50' if change_percent > 0 else '#f44336'
        change_sign = '+' if change_percent >= 0 else ''
        
        return f"""
        <html>
        <body style="font-family: Arial, sans-serif; color: #333;">
            <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                <h2 style="color: #1976d2; margin-bottom: 20px;">🤖 AI Trading Alert</h2>
                
                <div style="background: #f5f5f5; padding: 15px; border-radius: 8px; margin-bottom: 20px;">
                    <h3 style="margin: 0 0 10px 0;">{decision.symbol}</h3>
                    <div style="display: flex; align-items: center; gap: 10px;">
                        <span style="font-size: 24px; font-weight: bold;">${current_price:.2f}</span>
                        <span style="color: {price_color}; font-weight: bold;">
                            {change_sign}{change_percent:.2f}%
                        </span>
                    </div>
                    <div style="margin-top: 5px; color: #666;">
                        Volume: {volume:,}
                    </div>
                </div>
                
                <div style="background: {decision_color}; color: white; padding: 15px; border-radius: 8px; margin-bottom: 20px;">
                    <h3 style="margin: 0 0 10px 0;">AI Decision: {decision.decision_type.value}</h3>
                    <div style="opacity: 0.9;">
                        Confidence: {decision.confidence_score:.1%}
                    </div>
                    {f'<div style="opacity: 0.9;">Price Target: ${decision.price_target:.2f}</div>' if decision.price_target else ''}
                </div>
                
                <div style="background: white; border: 1px solid #ddd; padding: 15px; border-radius: 8px;">
                    <h4 style="margin: 0 0 10px 0; color: #333;">Rationale:</h4>
                    <p style="margin: 0; line-height: 1.5;">{decision.rationale}</p>
                </div>
                
                <div style="margin-top: 20px; padding-top: 15px; border-top: 1px solid #ddd; color: #666; font-size: 12px;">
                    Generated at: {decision.created_at.strftime('%Y-%m-%d %H:%M:%S UTC')}<br>
                    Decision ID: {decision.decision_id}
                </div>
            </div>
        </body>
        </html>
        """
    
    def _format_slack_trading_alert(
        self, 
        decision: AIDecision, 
        current_price: float, 
        change_percent: float
    ) -> str:
        """Format Slack trading alert message."""
        decision_emoji = {
            DecisionType.BUY: '🟢',
            DecisionType.SELL: '🔴',
            DecisionType.HOLD: '🟡'
        }.get(decision.decision_type, '⚪')
        
        change_emoji = '📈' if change_percent > 0 else '📉'
        change_sign = '+' if change_percent >= 0 else ''
        
        message = f"""🤖 *AI Trading Alert*

{decision_emoji} *{decision.decision_type.value} {decision.symbol}*

💰 Current Price: ${current_price:.2f} ({change_emoji} {change_sign}{change_percent:.2f}%)
🎯 Confidence: {decision.confidence_score:.1%}"""

        if decision.price_target:
            message += f"\n🎯 Price Target: ${decision.price_target:.2f}"
        
        message += f"\n\n📝 *Rationale:*\n{decision.rationale}"
        
        return message
    
    def _format_system_alert_email(self, title: str, message: str, severity: str) -> str:
        """Format system alert email content."""
        severity_colors = {
            'info': '#2196f3',
            'warning': '#ff9800',
            'error': '#f44336',
            'success': '#4caf50'
        }
        color = severity_colors.get(severity, '#9e9e9e')
        
        return f"""
        <html>
        <body style="font-family: Arial, sans-serif; color: #333;">
            <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                <div style="background: {color}; color: white; padding: 15px; border-radius: 8px; margin-bottom: 20px;">
                    <h2 style="margin: 0;">{title}</h2>
                    <div style="opacity: 0.9; margin-top: 5px;">Severity: {severity.upper()}</div>
                </div>
                
                <div style="background: white; border: 1px solid #ddd; padding: 15px; border-radius: 8px;">
                    <p style="margin: 0; line-height: 1.5;">{message}</p>
                </div>
                
                <div style="margin-top: 20px; padding-top: 15px; border-top: 1px solid #ddd; color: #666; font-size: 12px;">
                    Generated at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}
                </div>
            </div>
        </body>
        </html>
        """
    
    def _format_portfolio_summary_email(self, analytics: PortfolioAnalytics) -> str:
        """Format portfolio summary email content."""
        total_color = '#4caf50' if analytics.total_gain_loss >= 0 else '#f44336'
        daily_color = '#4caf50' if analytics.daily_gain_loss >= 0 else '#f44336'
        
        return f"""
        <html>
        <body style="font-family: Arial, sans-serif; color: #333;">
            <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                <h2 style="color: #1976d2; margin-bottom: 20px;">📊 Portfolio Summary</h2>
                
                <div style="background: #f5f5f5; padding: 15px; border-radius: 8px; margin-bottom: 20px;">
                    <h3 style="margin: 0 0 15px 0;">Portfolio Value</h3>
                    <div style="font-size: 28px; font-weight: bold; margin-bottom: 10px;">
                        ${analytics.total_value:.2f}
                    </div>
                    <div style="display: flex; justify-content: space-between;">
                        <span>Cash: ${analytics.cash_balance:.2f}</span>
                        <span>Positions: ${analytics.total_value - analytics.cash_balance:.2f}</span>
                    </div>
                </div>
                
                <div style="display: flex; gap: 15px; margin-bottom: 20px;">
                    <div style="flex: 1; background: white; border: 1px solid #ddd; padding: 15px; border-radius: 8px;">
                        <h4 style="margin: 0 0 10px 0;">Total P&L</h4>
                        <div style="font-size: 20px; font-weight: bold; color: {total_color};">
                            ${analytics.total_gain_loss:.2f}
                        </div>
                        <div style="color: {total_color};">
                            {analytics.total_gain_loss_percent:.2f}%
                        </div>
                    </div>
                    
                    <div style="flex: 1; background: white; border: 1px solid #ddd; padding: 15px; border-radius: 8px;">
                        <h4 style="margin: 0 0 10px 0;">Daily P&L</h4>
                        <div style="font-size: 20px; font-weight: bold; color: {daily_color};">
                            ${analytics.daily_gain_loss:.2f}
                        </div>
                        <div style="color: {daily_color};">
                            {analytics.daily_gain_loss_percent:.2f}%
                        </div>
                    </div>
                </div>
                
                <div style="background: white; border: 1px solid #ddd; padding: 15px; border-radius: 8px;">
                    <h4 style="margin: 0 0 10px 0;">Risk Metrics</h4>
                    <div style="display: flex; justify-content: space-between; margin-bottom: 5px;">
                        <span>Risk Score:</span>
                        <span>{analytics.risk_score:.2f}</span>
                    </div>
                    <div style="display: flex; justify-content: space-between; margin-bottom: 5px;">
                        <span>Diversification Score:</span>
                        <span>{analytics.diversification_score:.2f}</span>
                    </div>
                    <div style="display: flex; justify-content: space-between;">
                        <span>Beta:</span>
                        <span>{analytics.beta:.2f}</span>
                    </div>
                </div>
                
                <div style="margin-top: 20px; padding-top: 15px; border-top: 1px solid #ddd; color: #666; font-size: 12px;">
                    Generated at: {analytics.timestamp.strftime('%Y-%m-%d %H:%M:%S UTC')}
                </div>
            </div>
        </body>
        </html>
        """
    
    def _format_slack_portfolio_summary(self, analytics: PortfolioAnalytics) -> str:
        """Format Slack portfolio summary message."""
        total_emoji = '📈' if analytics.total_gain_loss >= 0 else '📉'
        daily_emoji = '📈' if analytics.daily_gain_loss >= 0 else '📉'
        
        return f"""📊 *Portfolio Summary* - {analytics.timestamp.strftime('%Y-%m-%d')}

💰 *Portfolio Value:* ${analytics.total_value:,.2f}
💵 Cash: ${analytics.cash_balance:,.2f} | 📈 Positions: ${analytics.total_value - analytics.cash_balance:,.2f}

{total_emoji} *Total P&L:* ${analytics.total_gain_loss:,.2f} ({analytics.total_gain_loss_percent:+.2f}%)
{daily_emoji} *Daily P&L:* ${analytics.daily_gain_loss:,.2f} ({analytics.daily_gain_loss_percent:+.2f}%)

📊 *Risk Metrics:*
• Risk Score: {analytics.risk_score:.2f}
• Diversification: {analytics.diversification_score:.2f}
• Beta: {analytics.beta:.2f}"""


# Global instance
notification_service = NotificationService()
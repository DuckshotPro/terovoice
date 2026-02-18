"""
Analytics service for tracking events and generating insights.
"""

from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine, func
from backend_setup.db.models import AnalyticsEvent, User, OnboardingState, Call
import os
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import logging

logger = logging.getLogger(__name__)

# Database setup
DATABASE_URL = os.getenv('DATABASE_URL', 'postgresql://user:password@localhost/tero_voice')
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class AnalyticsService:
    """Service for logging events and generating analytics."""

    def log_event(self, user_id: Optional[str], event_type: str, event_data: Dict, session_id: Optional[str] = None):
        """Log an analytics event."""
        try:
            session = SessionLocal()

            event = AnalyticsEvent(
                user_id=user_id,
                event_type=event_type,
                event_data=event_data,
                session_id=session_id or str(uuid.uuid4()),
                metadata={}
            )

            session.add(event)
            session.commit()
            session.close()

            logger.info(f"Analytics event logged: {event_type} for user {user_id}")
            return True

        except Exception as e:
            logger.error(f"Failed to log analytics event: {str(e)}")
            return False

    def get_onboarding_funnel(self, start_date: Optional[datetime] = None, end_date: Optional[datetime] = None) -> Dict:
        """Get onboarding conversion funnel data."""
        try:
            session = SessionLocal()

            if not start_date:
                start_date = datetime.utcnow() - timedelta(days=30)
            if not end_date:
                end_date = datetime.utcnow()

            # Get step completion counts
            step_counts = {}
            for step in range(1, 8):
                count = session.query(OnboardingState).filter(
                    OnboardingState.created_at >= start_date,
                    OnboardingState.created_at <= end_date,
                    OnboardingState.completed_steps.contains([step])
                ).count()
                step_counts[f'step_{step}'] = count

            # Get total users who started onboarding
            total_started = session.query(OnboardingState).filter(
                OnboardingState.created_at >= start_date,
                OnboardingState.created_at <= end_date
            ).count()

            # Calculate conversion rates
            conversion_rates = {}
            for step in range(1, 8):
                if total_started > 0:
                    conversion_rates[f'step_{step}'] = (step_counts[f'step_{step}'] / total_started) * 100
                else:
                    conversion_rates[f'step_{step}'] = 0

            session.close()

            return {
                'total_started': total_started,
                'step_counts': step_counts,
                'conversion_rates': conversion_rates,
                'period': {
                    'start': start_date.isoformat(),
                    'end': end_date.isoformat()
                }
            }

        except Exception as e:
            logger.error(f"Failed to get onboarding funnel: {str(e)}")
            return {}

    def get_customer_metrics(self, start_date: Optional[datetime] = None, end_date: Optional[datetime] = None) -> Dict:
        """Get customer metrics and KPIs."""
        try:
            session = SessionLocal()

            if not start_date:
                start_date = datetime.utcnow() - timedelta(days=30)
            if not end_date:
                end_date = datetime.utcnow()

            # Total customers
            total_customers = session.query(User).filter(
                User.created_at >= start_date,
                User.created_at <= end_date
            ).count()

            # Active customers (completed onboarding)
            active_customers = session.query(User).join(OnboardingState).filter(
                User.created_at >= start_date,
                User.created_at <= end_date,
                OnboardingState.progress == 100
            ).count()

            # Customers by industry
            industry_counts = session.query(
                OnboardingState.industry,
                func.count(OnboardingState.id)
            ).filter(
                OnboardingState.created_at >= start_date,
                OnboardingState.created_at <= end_date,
                OnboardingState.industry.isnot(None)
            ).group_by(OnboardingState.industry).all()

            # Average time to complete onboarding
            completed_onboarding = session.query(OnboardingState).filter(
                OnboardingState.created_at >= start_date,
                OnboardingState.created_at <= end_date,
                OnboardingState.progress == 100
            ).all()

            avg_completion_time = 0
            if completed_onboarding:
                total_time = sum([
                    (state.updated_at - state.created_at).total_seconds() / 3600  # Convert to hours
                    for state in completed_onboarding
                ])
                avg_completion_time = total_time / len(completed_onboarding)

            session.close()

            return {
                'total_customers': total_customers,
                'active_customers': active_customers,
                'activation_rate': (active_customers / total_customers * 100) if total_customers > 0 else 0,
                'industry_breakdown': dict(industry_counts),
                'avg_completion_time_hours': round(avg_completion_time, 2),
                'period': {
                    'start': start_date.isoformat(),
                    'end': end_date.isoformat()
                }
            }

        except Exception as e:
            logger.error(f"Failed to get customer metrics: {str(e)}")
            return {}

    def get_demo_metrics(self, start_date: Optional[datetime] = None, end_date: Optional[datetime] = None) -> Dict:
        """Get interactive demo performance metrics."""
        try:
            session = SessionLocal()

            if not start_date:
                start_date = datetime.utcnow() - timedelta(days=30)
            if not end_date:
                end_date = datetime.utcnow()

            # Demo completion rate
            total_reached_demo = session.query(OnboardingState).filter(
                OnboardingState.created_at >= start_date,
                OnboardingState.created_at <= end_date,
                OnboardingState.current_step >= 5
            ).count()

            completed_demo = session.query(OnboardingState).filter(
                OnboardingState.created_at >= start_date,
                OnboardingState.created_at <= end_date,
                OnboardingState.demo_completed == True
            ).count()

            demo_completion_rate = (completed_demo / total_reached_demo * 100) if total_reached_demo > 0 else 0

            # Average demo duration (from analytics events)
            demo_events = session.query(AnalyticsEvent).filter(
                AnalyticsEvent.timestamp >= start_date,
                AnalyticsEvent.timestamp <= end_date,
                AnalyticsEvent.event_type.in_(['demo_started', 'demo_completed'])
            ).all()

            # Group by session to calculate durations
            demo_sessions = {}
            for event in demo_events:
                session_id = event.session_id
                if session_id not in demo_sessions:
                    demo_sessions[session_id] = {}
                demo_sessions[session_id][event.event_type] = event.timestamp

            durations = []
            for session_id, events in demo_sessions.items():
                if 'demo_started' in events and 'demo_completed' in events:
                    duration = (events['demo_completed'] - events['demo_started']).total_seconds() / 60  # Minutes
                    durations.append(duration)

            avg_demo_duration = sum(durations) / len(durations) if durations else 0

            session.close()

            return {
                'total_reached_demo': total_reached_demo,
                'completed_demo': completed_demo,
                'demo_completion_rate': round(demo_completion_rate, 2),
                'avg_demo_duration_minutes': round(avg_demo_duration, 2),
                'total_demo_sessions': len(demo_sessions),
                'period': {
                    'start': start_date.isoformat(),
                    'end': end_date.isoformat()
                }
            }

        except Exception as e:
            logger.error(f"Failed to get demo metrics: {str(e)}")
            return {}

    def get_user_journey(self, user_id: str) -> Dict:
        """Get detailed journey for a specific user."""
        try:
            session = SessionLocal()

            # Get user info
            user = session.query(User).filter(User.id == user_id).first()
            if not user:
                return {}

            # Get onboarding state
            onboarding = session.query(OnboardingState).filter(
                OnboardingState.user_id == user_id
            ).first()

            # Get all analytics events for this user
            events = session.query(AnalyticsEvent).filter(
                AnalyticsEvent.user_id == user_id
            ).order_by(AnalyticsEvent.timestamp).all()

            # Get call history
            calls = session.query(Call).join(User).filter(
                User.id == user_id
            ).order_by(Call.created_at.desc()).limit(10).all()

            session.close()

            return {
                'user': {
                    'id': str(user.id),
                    'email': user.email,
                    'name': user.name,
                    'created_at': user.created_at.isoformat(),
                    'is_active': user.is_active
                },
                'onboarding': {
                    'current_step': onboarding.current_step if onboarding else 0,
                    'progress': onboarding.progress if onboarding else 0,
                    'completed_steps': onboarding.completed_steps if onboarding else [],
                    'demo_completed': onboarding.demo_completed if onboarding else False,
                    'industry': onboarding.industry if onboarding else None
                },
                'events': [
                    {
                        'type': event.event_type,
                        'timestamp': event.timestamp.isoformat(),
                        'data': event.event_data
                    }
                    for event in events
                ],
                'recent_calls': [
                    {
                        'id': str(call.id),
                        'duration': call.duration_seconds,
                        'success': call.success,
                        'sentiment': call.sentiment,
                        'created_at': call.created_at.isoformat()
                    }
                    for call in calls
                ]
            }

        except Exception as e:
            logger.error(f"Failed to get user journey: {str(e)}")
            return {}
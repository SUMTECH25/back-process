"""
라우트 패키지 초기화
"""

from .auth import auth_bp
from .records import records_bp
from .rewards import rewards_bp
from .reports import reports_bp
from .audio import audio_bp

__all__ = ['auth_bp', 'records_bp', 'rewards_bp', 'reports_bp', 'audio_bp']
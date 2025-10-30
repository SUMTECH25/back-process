"""
Flask 애플리케이션 초기화 및 실행 스크립트
"""

import os
import sys
import logging
from datetime import datetime

# 현재 디렉토리를 Python 경로에 추가
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import app, db
from utils.database import init_database, create_sample_data, get_database_stats
from services.audio_stress_service import initialize_audio_models

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('app.log'),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)

def setup_application():
    """애플리케이션 초기 설정"""
    try:
        logger.info("Setting up application...")
        
        # 필요한 디렉토리 생성
        directories = ['logs', 'reports', 'reports/pdf', 'reports/images', 'backups', 'uploads', 'uploads/audio']
        for directory in directories:
            os.makedirs(directory, exist_ok=True)
        
        # 데이터베이스 초기화
        with app.app_context():
            init_database()
            logger.info("Database initialized successfully")
        
        # 오디오 모델 초기화 (백그라운드에서)
        logger.info("Initializing audio models in background...")
        try:
            initialize_audio_models()
            logger.info("Audio models initialized successfully")
        except Exception as e:
            logger.warning(f"Audio model initialization failed: {str(e)}")
            logger.warning("Audio analysis features will be disabled")
        
        logger.info("Application setup completed")
        
    except Exception as e:
        logger.error(f"Error setting up application: {str(e)}")
        sys.exit(1)

def create_sample_user():
    """샘플 사용자 생성 (개발용)"""
    try:
        if os.getenv('FLASK_ENV') == 'development':
            with app.app_context():
                user_id = create_sample_data()
                logger.info(f"Sample user created with ID: {user_id}")
                return user_id
        else:
            logger.info("Skipping sample data creation in production mode")
            return None
            
    except Exception as e:
        logger.error(f"Error creating sample user: {str(e)}")
        return None

def print_database_stats():
    """데이터베이스 통계 출력"""
    try:
        with app.app_context():
            stats = get_database_stats()
            
            print("\n" + "="*50)
            print("📊 DATABASE STATISTICS")
            print("="*50)
            print(f"Users: {stats.get('users_count', 0)}")
            print(f"Daily Records: {stats.get('records_count', 0)}")
            print(f"Milestones: {stats.get('milestones_count', 0)}")
            print(f"Active Users: {stats.get('active_users', 0)}")
            print(f"Records (Last 7 days): {stats.get('records_last_7_days', 0)}")
            print(f"Unclaimed Rewards: {stats.get('unclaimed_rewards', 0)}")
            
            if 'most_active_user' in stats:
                most_active = stats['most_active_user']
                print(f"Most Active User: {most_active['username']} ({most_active['record_count']} records)")
            
            print("="*50)
            
    except Exception as e:
        logger.error(f"Error getting database stats: {str(e)}")

def print_api_endpoints():
    """API 엔드포인트 목록 출력"""
    print("\n" + "="*50)
    print("🚀 API ENDPOINTS")
    print("="*50)
    
    endpoints = [
        ("POST", "/api/auth/register", "사용자 회원가입"),
        ("POST", "/api/auth/login", "사용자 로그인"),
        ("GET", "/api/auth/profile", "프로필 조회"),
        ("PUT", "/api/auth/profile", "프로필 업데이트"),
        ("", "", ""),
        ("POST", "/api/records/", "일일 기록 생성"),
        ("GET", "/api/records/", "기록 목록 조회"),
        ("GET", "/api/records/today", "오늘의 기록 조회"),
        ("GET", "/api/records/{id}", "특정 기록 조회"),
        ("PUT", "/api/records/{id}", "기록 업데이트"),
        ("", "", ""),
        ("POST", "/api/rewards/check", "마일스톤 확인"),
        ("GET", "/api/rewards/milestones", "마일스톤 목록"),
        ("POST", "/api/rewards/milestones/{id}/claim", "보상 수령"),
        ("GET", "/api/rewards/progress", "진행 상황"),
        ("GET", "/api/rewards/next-milestone", "다음 마일스톤"),
        ("", "", ""),
        ("GET", "/api/reports/analysis/{type}", "분석 리포트 (3/7/30일)"),
        ("GET", "/api/reports/pdf/{milestone_id}", "PDF 리포트 다운로드"),
        ("GET", "/api/reports/summary", "요약 리포트"),
        ("GET", "/api/reports/insights", "개인화된 인사이트"),
        ("", "", ""),
        ("POST", "/api/audio/analyze", "오디오 스트레스 분석 (파일 저장)"),
        ("POST", "/api/audio/analyze-direct", "오디오 스트레스 분석 (임시)"),
        ("GET", "/api/audio/formats", "지원 오디오 형식"),
        ("GET", "/api/audio/records/{id}/audio", "기록의 오디오 분석"),
        ("GET", "/api/audio/recent-analyses", "최근 오디오 분석"),
        ("GET", "/api/audio/stats", "오디오 분석 통계"),
        ("GET", "/api/audio/policy", "분석 정책 정보"),
        ("", "", ""),
        ("GET", "/", "API 상태 확인"),
        ("GET", "/health", "헬스 체크"),
    ]
    
    for method, endpoint, description in endpoints:
        if method:
            print(f"{method:6} {endpoint:35} - {description}")
        else:
            print()
    
    print("="*50)

def main():
    """메인 실행 함수"""
    print("\n🌟 3-7-30 보상 시스템 백엔드 시작")
    print(f"⏰ 시작 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 애플리케이션 설정
    setup_application()
    
    # 개발 모드에서 샘플 데이터 생성
    if os.getenv('FLASK_ENV') == 'development':
        create_sample_user()
    
    # 통계 출력
    print_database_stats()
    
    # API 엔드포인트 출력
    print_api_endpoints()
    
    # 서버 정보 출력
    host = os.getenv('HOST', '0.0.0.0')
    port = int(os.getenv('PORT', 5000))
    
    print(f"\n🔗 서버 주소: http://{host}:{port}")
    print(f"📚 API 문서: http://{host}:{port}/")
    print(f"❤️  헬스 체크: http://{host}:{port}/health")
    print("\n🎯 테스트 계정:")
    print("   username: testuser")
    print("   password: password123")
    print("\n" + "="*50)
    print("Press Ctrl+C to stop the server")
    print("="*50 + "\n")
    
    # Flask 서버 실행
    try:
        app.run(
            host=host,
            port=port,
            debug=os.getenv('FLASK_DEBUG', 'False').lower() == 'true'
        )
    except KeyboardInterrupt:
        print("\n\n👋 서버를 종료합니다...")
        logger.info("Server shutdown requested")
    except Exception as e:
        logger.error(f"Server error: {str(e)}")
        sys.exit(1)

if __name__ == '__main__':
    main()
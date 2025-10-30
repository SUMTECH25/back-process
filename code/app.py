"""
3-7-30 보상 시스템 Flask 애플리케이션
일일 상태 기록 및 보상 시스템의 핵심 로직을 구현
"""

from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from flask_cors import CORS
from datetime import datetime, timedelta, timezone
import os
from dotenv import load_dotenv

# 환경 변수 로드
load_dotenv()

# Flask 앱 초기화
app = Flask(__name__)

# 설정
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///career_stress.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY', 'jwt-secret-change-in-production')
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(days=7)

# 확장 기능 초기화
db = SQLAlchemy(app)
migrate = Migrate(app, db)
bcrypt = Bcrypt(app)
jwt = JWTManager(app)
CORS(app)

# 순환 import 방지를 위해 함수 내에서 import하고 블루프린트 등록
def register_blueprints():
    """블루프린트 등록"""
    from routes.auth import auth_bp
    from routes.records import records_bp
    from routes.rewards import rewards_bp
    from routes.reports import reports_bp
    from routes.audio import audio_bp
    
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(records_bp, url_prefix='/api/records')
    app.register_blueprint(rewards_bp, url_prefix='/api/rewards')
    app.register_blueprint(reports_bp, url_prefix='/api/reports')
    app.register_blueprint(audio_bp, url_prefix='/api/audio')

# 블루프린트 등록 실행
register_blueprints()

@app.route('/')
def index():
    """API 상태 확인"""
    return jsonify({
        "message": "3-7-30 보상 시스템 API",
        "version": "1.0.0",
        "status": "running"
    })

@app.route('/health')
def health_check():
    """헬스 체크 엔드포인트"""
    return jsonify({
        "status": "healthy",
        "timestamp": datetime.now(timezone.utc).isoformat()
    })

if __name__ == '__main__':
    # 데이터베이스 테이블 생성
    with app.app_context():
        db.create_all()
    
    # 개발 서버 실행
    app.run(debug=True, host='0.0.0.0', port=5000)
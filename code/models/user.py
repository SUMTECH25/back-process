"""
사용자 모델
"""

from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from app import db

class User(db.Model):
    """사용자 정보"""
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    
    # 사용자 프로필
    name = db.Column(db.String(100), nullable=True)
    occupation = db.Column(db.String(100), nullable=True)  # 직업
    stress_level = db.Column(db.Integer, default=5)  # 1-10 스케일
    
    # 시스템 필드
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)
    
    # 관계
    daily_records = db.relationship('DailyRecord', backref='user', lazy=True, 
                                   cascade='all, delete-orphan')
    milestones = db.relationship('Milestone', backref='user', lazy=True,
                                cascade='all, delete-orphan')
    
    def set_password(self, password):
        """비밀번호 해시 설정"""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """비밀번호 확인"""
        return check_password_hash(self.password_hash, password)
    
    def get_current_streak(self):
        """현재 연속 기록 일수 계산"""
        from models.daily_record import DailyRecord
        from datetime import timedelta
        
        records = DailyRecord.query.filter_by(user_id=self.id).order_by(
            DailyRecord.record_date.desc()
        ).all()
        
        if not records:
            return 0
        
        streak = 0
        current_date = datetime.utcnow().date()
        
        for record in records:
            if record.record_date == current_date or record.record_date == current_date - timedelta(days=streak):
                streak += 1
                current_date = record.record_date
            else:
                break
        
        return streak
    
    def to_dict(self):
        """사용자 정보를 딕셔너리로 반환"""
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'name': self.name,
            'occupation': self.occupation,
            'stress_level': self.stress_level,
            'created_at': self.created_at.isoformat(),
            'current_streak': self.get_current_streak()
        }
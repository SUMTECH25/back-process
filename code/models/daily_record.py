"""
일일 기록 모델
"""

from datetime import datetime, date
from app import db

class DailyRecord(db.Model):
    """일일 상태 기록"""
    __tablename__ = 'daily_records'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    record_date = db.Column(db.Date, nullable=False)
    
    # 기본 상태 정보
    stress_level = db.Column(db.Integer, nullable=False)  # 1-10 스케일
    mood = db.Column(db.String(20), nullable=False)  # happy, sad, angry, anxious, etc.
    energy_level = db.Column(db.Integer, nullable=False)  # 1-10 스케일
    
    # 업무 관련
    work_satisfaction = db.Column(db.Integer, nullable=True)  # 1-10 스케일
    work_load = db.Column(db.Integer, nullable=True)  # 1-10 스케일
    work_hours = db.Column(db.Float, nullable=True)  # 근무 시간
    sleep_hours = db.Column(db.Float, nullable=True)  # 수면 시간
    
    # 프론트엔드 추가 요구 필드들
    fatigue = db.Column(db.Integer, nullable=True)  # 피로도 0-10 (프론트엔드 주요 필드)
    emotions = db.Column(db.JSON, nullable=True)  # ["지침", "짜증"] 같은 감정 배열
    worked_during_lunch = db.Column(db.Boolean, default=False)  # 점심시간 근무 여부
    after_hours_contacts_count = db.Column(db.Integer, nullable=True)  # 퇴근 후 연락 횟수
    unpaid_prep_hours = db.Column(db.Float, nullable=True)  # 무급 준비 시간
    had_drinking_or_overtime = db.Column(db.Boolean, default=False)  # 술자리/야근 여부
    heard_hustle_praise = db.Column(db.Boolean, default=False)  # 야근 칭찬 들었는지
    none_of_above = db.Column(db.Boolean, default=False)  # 해당사항 없음
    
    # 한 문장 읽기 (스트레스 분석용)
    daily_sentence = db.Column(db.Text, nullable=True)
    sentence_analysis = db.Column(db.JSON, nullable=True)  # NLP 분석 결과
    
    # 오디오 스트레스 분석
    audio_file_path = db.Column(db.String(255), nullable=True)  # 오디오 파일 경로
    audio_analysis = db.Column(db.JSON, nullable=True)  # 오디오 분석 결과
    
    # 추가 메모
    notes = db.Column(db.Text, nullable=True)
    
    # 시스템 필드
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 고유 제약조건 (한 사용자당 하루에 하나의 기록만)
    __table_args__ = (
        db.UniqueConstraint('user_id', 'record_date', name='unique_user_date'),
    )
    
    def to_dict(self):
        """기록을 딕셔너리로 반환 (프론트엔드 호환)"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'date': self.record_date.isoformat() if self.record_date else None,  # 🔥 프론트엔드가 기대하는 'date' 필드
            'stress_level': self.stress_level or 0,
            'mood': self.mood or 'normal',
            'energy_level': self.energy_level or 0,
            'work_satisfaction': self.work_satisfaction or 0,
            'work_load': self.work_load or 0,
            'work_hours': self.work_hours or 0.0,
            'sleep_hours': self.sleep_hours or 0.0,
            'fatigue': self.fatigue or 0,
            'emotions': self.emotions or [],
            'worked_during_lunch': self.worked_during_lunch or False,
            'after_hours_contacts_count': self.after_hours_contacts_count or 0,
            'unpaid_prep_hours': self.unpaid_prep_hours or 0.0,
            'had_drinking_or_overtime': self.had_drinking_or_overtime or False,
            'heard_hustle_praise': self.heard_hustle_praise or False,
            'none_of_above': self.none_of_above or False,
            'daily_sentence': self.daily_sentence or '',
            'sentence_analysis': self.sentence_analysis,
            'audio_file_path': self.audio_file_path,
            'audio_analysis': self.audio_analysis,
            'notes': self.notes or '',
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            # 호환성을 위해 기존 필드명도 유지
            'record_date': self.record_date.isoformat() if self.record_date else None
        }
    
    @staticmethod
    def get_user_records(user_id, start_date=None, end_date=None):
        """사용자의 기록을 날짜 범위로 조회"""
        query = DailyRecord.query.filter_by(user_id=user_id)
        
        if start_date:
            query = query.filter(DailyRecord.record_date >= start_date)
        if end_date:
            query = query.filter(DailyRecord.record_date <= end_date)
        
        return query.order_by(DailyRecord.record_date.desc()).all()
    
    @staticmethod
    def get_streak_count(user_id):
        """연속 기록 일수 계산"""
        from datetime import timedelta
        
        records = DailyRecord.query.filter_by(user_id=user_id).order_by(
            DailyRecord.record_date.desc()
        ).all()
        
        if not records:
            return 0
        
        streak = 0
        current_date = date.today()
        
        for record in records:
            expected_date = current_date if streak == 0 else current_date - timedelta(days=streak)
            if record.record_date == expected_date:
                streak += 1
            else:
                break
        
        return streak
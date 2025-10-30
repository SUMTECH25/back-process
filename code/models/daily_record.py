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
        """기록을 딕셔너리로 반환"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'record_date': self.record_date.isoformat(),
            'stress_level': self.stress_level,
            'mood': self.mood,
            'energy_level': self.energy_level,
            'work_satisfaction': self.work_satisfaction,
            'work_load': self.work_load,
            'daily_sentence': self.daily_sentence,
            'sentence_analysis': self.sentence_analysis,
            'audio_file_path': self.audio_file_path,
            'audio_analysis': self.audio_analysis,
            'notes': self.notes,
            'created_at': self.created_at.isoformat()
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
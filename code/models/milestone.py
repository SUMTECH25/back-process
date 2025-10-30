"""
마일스톤 모델
"""

from datetime import datetime
from app import db

class Milestone(db.Model):
    """보상 마일스톤 (3일, 7일, 30일)"""
    __tablename__ = 'milestones'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # 마일스톤 정보
    milestone_type = db.Column(db.String(10), nullable=False)  # '3', '7', '30'
    streak_count = db.Column(db.Integer, nullable=False)  # 달성 시점의 연속 일수
    achieved_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # 보상 정보
    reward_type = db.Column(db.String(20), nullable=False)  # 'report', 'analysis', 'prediction'
    reward_data = db.Column(db.JSON, nullable=True)  # 보상 데이터 (분석 결과, 리포트 등)
    is_claimed = db.Column(db.Boolean, default=False)  # 보상 수령 여부
    
    # PDF 리포트 (30일 전용)
    pdf_path = db.Column(db.String(255), nullable=True)  # PDF 파일 경로
    
    # 시스템 필드
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        """마일스톤을 딕셔너리로 반환"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'milestone_type': self.milestone_type,
            'streak_count': self.streak_count,
            'achieved_at': self.achieved_at.isoformat(),
            'reward_type': self.reward_type,
            'reward_data': self.reward_data,
            'is_claimed': self.is_claimed,
            'pdf_path': self.pdf_path,
            'created_at': self.created_at.isoformat()
        }
    
    @staticmethod
    def get_user_milestones(user_id, milestone_type=None):
        """사용자의 마일스톤 조회"""
        query = Milestone.query.filter_by(user_id=user_id)
        
        if milestone_type:
            query = query.filter_by(milestone_type=milestone_type)
        
        return query.order_by(Milestone.achieved_at.desc()).all()
    
    @staticmethod
    def create_milestone(user_id, milestone_type, streak_count, reward_data=None):
        """새 마일스톤 생성"""
        # 보상 타입 결정
        reward_types = {
            '3': 'analysis',      # 3일: 기본 분석
            '7': 'prediction',    # 7일: 한계점 예측
            '30': 'report'        # 30일: 종합 리포트 + PDF
        }
        
        milestone = Milestone(
            user_id=user_id,
            milestone_type=milestone_type,
            streak_count=streak_count,
            reward_type=reward_types.get(milestone_type, 'analysis'),
            reward_data=reward_data or {}
        )
        
        db.session.add(milestone)
        db.session.commit()
        
        return milestone
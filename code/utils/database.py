"""
데이터베이스 초기화 및 관리 유틸리티
"""

from app import app, db
from models.user import User
from models.daily_record import DailyRecord
from models.milestone import Milestone
from datetime import datetime, date, timedelta
import logging
import os

logger = logging.getLogger(__name__)

def init_database():
    """데이터베이스 테이블 생성"""
    try:
        with app.app_context():
            db.create_all()
            logger.info("Database tables created successfully")
    except Exception as e:
        logger.error(f"Error creating database tables: {str(e)}")
        raise e

def create_sample_data():
    """샘플 데이터 생성 (개발/테스트용)"""
    try:
        with app.app_context():
            # 샘플 사용자 생성
            if not User.query.filter_by(username='testuser').first():
                user = User(
                    username='testuser',
                    email='test@example.com',
                    name='테스트 사용자',
                    occupation='개발자',
                    stress_level=5
                )
                user.set_password('password123')
                db.session.add(user)
                db.session.commit()
                
                # 최근 30일간의 샘플 기록 생성
                import random
                today = date.today()
                
                for i in range(30):
                    record_date = today - timedelta(days=i)
                    
                    # 랜덤하지만 현실적인 데이터 생성
                    base_stress = 5 + random.randint(-2, 3)
                    base_energy = 6 + random.randint(-3, 2)
                    
                    moods = ['happy', 'neutral', 'stressed', 'tired', 'anxious', 'excited']
                    mood = random.choice(moods)
                    
                    sample_sentences = [
                        "오늘은 정말 바쁜 하루였다.",
                        "새로운 프로젝트가 시작되어 설렌다.",
                        "업무량이 너무 많아서 스트레스가 심하다.",
                        "팀원들과 협업이 잘 되어서 만족스럽다.",
                        "데드라인이 촉박해서 걱정된다.",
                        "오늘은 비교적 평온한 하루였다.",
                        "새로운 기술을 배워서 뿌듯하다.",
                        "회의가 너무 많아서 피곤하다."
                    ]
                    
                    record = DailyRecord(
                        user_id=user.id,
                        record_date=record_date,
                        stress_level=max(1, min(10, base_stress)),
                        mood=mood,
                        energy_level=max(1, min(10, base_energy)),
                        work_satisfaction=random.randint(4, 9),
                        work_load=random.randint(3, 8),
                        daily_sentence=random.choice(sample_sentences),
                        notes=f"Day {i+1} sample record"
                    )
                    
                    db.session.add(record)
                
                db.session.commit()
                logger.info(f"Sample data created for user: {user.username}")
                
                return user.id
            else:
                logger.info("Sample user already exists")
                return User.query.filter_by(username='testuser').first().id
                
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error creating sample data: {str(e)}")
        raise e

def reset_database():
    """데이터베이스 초기화 (주의: 모든 데이터 삭제)"""
    try:
        with app.app_context():
            db.drop_all()
            db.create_all()
            logger.info("Database reset successfully")
    except Exception as e:
        logger.error(f"Error resetting database: {str(e)}")
        raise e

def backup_database():
    """데이터베이스 백업 (SQLite 기준)"""
    try:
        import shutil
        import os
        from datetime import datetime
        
        db_path = app.config['SQLALCHEMY_DATABASE_URI'].replace('sqlite:///', '')
        backup_dir = os.path.join(os.getcwd(), 'backups')
        os.makedirs(backup_dir, exist_ok=True)
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_path = os.path.join(backup_dir, f'backup_{timestamp}.db')
        
        shutil.copy2(db_path, backup_path)
        logger.info(f"Database backed up to: {backup_path}")
        
        return backup_path
        
    except Exception as e:
        logger.error(f"Error backing up database: {str(e)}")
        raise e

def get_database_stats():
    """데이터베이스 통계 정보"""
    try:
        with app.app_context():
            stats = {
                'users_count': User.query.count(),
                'records_count': DailyRecord.query.count(),
                'milestones_count': Milestone.query.count(),
                'active_users': User.query.filter_by(is_active=True).count(),
                'records_last_7_days': DailyRecord.query.filter(
                    DailyRecord.record_date >= date.today() - timedelta(days=7)
                ).count(),
                'unclaimed_rewards': Milestone.query.filter_by(is_claimed=False).count()
            }
            
            # 가장 활발한 사용자
            most_active_user = db.session.query(
                User.username, 
                db.func.count(DailyRecord.id).label('record_count')
            ).join(DailyRecord).group_by(User.id).order_by(
                db.func.count(DailyRecord.id).desc()
            ).first()
            
            if most_active_user:
                stats['most_active_user'] = {
                    'username': most_active_user.username,
                    'record_count': most_active_user.record_count
                }
            
            return stats
            
    except Exception as e:
        logger.error(f"Error getting database stats: {str(e)}")
        return {'error': str(e)}

def cleanup_old_data(days_to_keep=365):
    """오래된 데이터 정리"""
    try:
        with app.app_context():
            cutoff_date = date.today() - timedelta(days=days_to_keep)
            
            # 오래된 기록 삭제
            old_records = DailyRecord.query.filter(
                DailyRecord.record_date < cutoff_date
            ).all()
            
            for record in old_records:
                db.session.delete(record)
            
            # 관련된 오래된 마일스톤도 삭제
            old_milestones = Milestone.query.filter(
                Milestone.achieved_at < datetime.combine(cutoff_date, datetime.min.time())
            ).all()
            
            for milestone in old_milestones:
                # PDF 파일도 삭제
                if milestone.pdf_path and os.path.exists(milestone.pdf_path):
                    os.remove(milestone.pdf_path)
                db.session.delete(milestone)
            
            db.session.commit()
            
            logger.info(f"Cleaned up {len(old_records)} old records and {len(old_milestones)} old milestones")
            
            return {
                'deleted_records': len(old_records),
                'deleted_milestones': len(old_milestones),
                'cutoff_date': cutoff_date.isoformat()
            }
            
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error cleaning up old data: {str(e)}")
        raise e
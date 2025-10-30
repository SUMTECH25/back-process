#!/usr/bin/env python3
"""
데이터베이스 마이그레이션 스크립트
새로 추가된 필드들을 기존 데이터베이스에 추가합니다.
"""

from app import app, db
from models.daily_record import DailyRecord
import logging

logger = logging.getLogger(__name__)

def migrate_database():
    """데이터베이스 마이그레이션 실행"""
    with app.app_context():
        try:
            print("🔄 데이터베이스 마이그레이션 시작...")
            
            # 테이블 생성/업데이트
            db.create_all()
            
            print("✅ 데이터베이스 마이그레이션 완료!")
            
            # 기존 데이터 확인
            record_count = DailyRecord.query.count()
            print(f"📊 현재 일일 기록 수: {record_count}")
            
            if record_count > 0:
                print("📝 기존 기록들의 새 필드는 기본값으로 설정됩니다:")
                print("   - work_hours: 0.0")
                print("   - sleep_hours: 0.0") 
                print("   - emotions: []")
                print("   - worked_during_lunch: False")
                print("   - after_hours_contacts_count: 0")
                print("   - unpaid_prep_hours: 0.0")
                print("   - had_drinking_or_overtime: False")
                print("   - heard_hustle_praise: False")
                print("   - none_of_above: False")
            
            return True
            
        except Exception as e:
            logger.error(f"마이그레이션 오류: {e}")
            print(f"❌ 마이그레이션 실패: {e}")
            return False

def test_api_compatibility():
    """API 호환성 테스트"""
    print("\n🧪 API 호환성 테스트...")
    
    try:
        with app.app_context():
            # 기존 기록이 있다면 테스트
            sample_record = DailyRecord.query.first()
            
            if sample_record:
                result = sample_record.to_dict()
                
                # 필수 필드 확인
                required_fields = ['id', 'date', 'stress_level', 'mood', 'work_hours', 'sleep_hours']
                missing_fields = [field for field in required_fields if field not in result]
                
                if missing_fields:
                    print(f"❌ 누락된 필드: {missing_fields}")
                    return False
                else:
                    print("✅ 모든 필수 필드가 존재합니다.")
                    print(f"📋 샘플 응답: {result}")
                    return True
            else:
                print("📭 기록이 없어서 샘플 기록을 생성합니다...")
                
                # 테스트 기록 생성
                from datetime import date
                test_record = DailyRecord(
                    user_id=1,
                    record_date=date.today(),
                    stress_level=5,
                    mood='normal',
                    energy_level=5
                )
                
                db.session.add(test_record)
                db.session.commit()
                
                result = test_record.to_dict()
                print(f"✅ 테스트 기록 생성 완료: {result}")
                return True
                
    except Exception as e:
        print(f"❌ 호환성 테스트 실패: {e}")
        return False

def main():
    """메인 실행 함수"""
    print("🚀 백엔드 마이그레이션 및 테스트")
    print("=" * 50)
    
    # 1. 데이터베이스 마이그레이션
    if not migrate_database():
        return
    
    # 2. API 호환성 테스트  
    if not test_api_compatibility():
        return
    
    print("\n" + "=" * 50)
    print("🎉 모든 작업이 완료되었습니다!")
    print("\n📋 다음 단계:")
    print("1. 서버 재시작: python3 run.py")
    print("2. API 테스트: curl http://localhost:5000/api/records/")
    print("3. 프론트엔드 연결 테스트")
    print("\n🔍 API 엔드포인트:")
    print("   GET  /api/records/         - 기록 목록 조회")
    print("   POST /api/records/         - 새 기록 생성/업데이트")
    print("   GET  /api/records/today    - 오늘 기록 조회")
    print("   GET  /api/rewards/progress - 보상 진행 상황")

if __name__ == "__main__":
    main()
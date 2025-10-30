"""
일일 기록 관련 라우트
"""

from flask import Blueprint, request, jsonify
# JWT 인증 비활성화됨
# from flask_jwt_extended import jwt_required, get_jwt_identity

# 기본 테스트 사용자 ID (인증 비활성화용)
DEFAULT_USER_ID = 1
from datetime import datetime, date, timedelta
from models.user import User
from models.daily_record import DailyRecord
from services.nlp_service import analyze_sentence
from services.audio_stress_service import analyze_audio_stress_from_data
from app import db
import logging

logger = logging.getLogger(__name__)

records_bp = Blueprint('records', __name__)

def calculate_stress_from_fatigue(fatigue):
    """피로도(0-10) → stress_level(1-10) 변환"""
    if fatigue is None:
        return 5
    return max(1, min(10, int(fatigue * 0.9 + 1)))

def calculate_energy_from_fatigue(fatigue):
    """피로도 → 에너지 레벨 변환 (피로도가 높으면 에너지는 낮음)"""
    if fatigue is None:
        return 5
    return max(1, min(10, int((10 - fatigue) * 0.8 + 1)))

def calculate_streak(user_id):
    """연속 기록 일수 계산"""
    records = DailyRecord.query.filter_by(user_id=user_id)\
        .order_by(DailyRecord.record_date.desc())\
        .all()
    
    if not records:
        return 0
    
    today = date.today()
    current_date = today
    streak = 0
    
    for record in records:
        if record.record_date == current_date or \
           (streak == 0 and record.record_date == current_date - timedelta(days=1)):
            streak += 1
            current_date = record.record_date - timedelta(days=1)
        elif record.record_date < current_date:
            break
    
    return streak

@records_bp.route('/', methods=['POST'])
# @jwt_required()  # 인증 비활성화
def create_record():
    """일일 기록 생성 - 프론트엔드 호환"""
    try:
        user_id = DEFAULT_USER_ID  # 고정된 테스트 사용자 ID
        data = request.get_json()
        
        # 날짜 처리 (프론트엔드는 'date' 필드 사용)
        record_date = data.get('date', data.get('record_date', date.today().isoformat()))
        if isinstance(record_date, str):
            record_date = datetime.strptime(record_date, '%Y-%m-%d').date()
        
        # 중복 기록 확인 (있으면 업데이트, 없으면 새로 생성)
        existing_record = DailyRecord.query.filter_by(
            user_id=user_id, 
            record_date=record_date
        ).first()
        
        # 한 문장 분석 (있는 경우) - 참고용으로만 저장, 스트레스 레벨에는 영향 없음
        sentence_analysis = None
        if data.get('daily_sentence'):
            sentence_analysis = analyze_sentence(data['daily_sentence'])
        
        # 오디오 분석 (multipart/form-data로 오디오 파일이 있는 경우)
        # 오디오 분석만 스트레스 레벨 판독에 사용
        audio_analysis = None
        audio_file_path = None
        if 'audio_file' in request.files:
            try:
                audio_file = request.files['audio_file']
                if audio_file and audio_file.filename:
                    # 오디오 데이터에서 직접 분석
                    audio_data = audio_file.read()
                    audio_analysis = analyze_audio_stress_from_data(audio_data, audio_file.filename)
                    
                    # 오디오 분석 결과만으로 스트레스 레벨 설정
                    if audio_analysis and 'stress_level' in audio_analysis and not audio_analysis.get('error'):
                        # 오디오 분석 결과를 우선적으로 사용
                        data['stress_level'] = audio_analysis['stress_level']
                        logger.info(f"Stress level updated from audio analysis: {audio_analysis['stress_level']}")
            except Exception as e:
                logger.warning(f"Audio analysis failed during record creation: {str(e)}")
                # 오디오 분석 실패해도 기록 생성은 계속 진행
        
        # 프론트엔드 필드 매핑 (camelCase → snake_case)
        def get_field_value(camel_case, snake_case, default=None):
            """camelCase와 snake_case 둘 다 지원"""
            return data.get(camel_case, data.get(snake_case, default))
        
        # 필드 값 추출 (프론트엔드 호환)
        work_hours = get_field_value('workHours', 'work_hours')
        fatigue = get_field_value('fatigue', 'fatigue')  # 피로도
        emotions = get_field_value('emotions', 'emotions', [])
        worked_during_lunch = get_field_value('workedDuringLunch', 'worked_during_lunch', False)
        after_hours_contacts_count = get_field_value('afterHoursContactsCount', 'after_hours_contacts_count')
        unpaid_prep_hours = get_field_value('unpaidPrepHours', 'unpaid_prep_hours')
        had_drinking_or_overtime = get_field_value('hadDrinkingOrOvertime', 'had_drinking_or_overtime', False)
        heard_hustle_praise = get_field_value('heardHustlePraise', 'heard_hustle_praise', False)
        none_of_above = get_field_value('noneOfAbove', 'none_of_above', False)
        
        # 피로도에서 스트레스 레벨 자동 계산 (프론트엔드 우선 지원)
        stress_level = data.get('stress_level')
        if not stress_level and fatigue is not None:
            stress_level = calculate_stress_from_fatigue(fatigue)
        elif not stress_level:
            stress_level = 5  # 기본값
        
        # 피로도에서 기타 필드 자동 계산
        mood = data.get('mood') or (emotions[0] if emotions else 'normal')
        energy_level = data.get('energy_level') or calculate_energy_from_fatigue(fatigue) if fatigue else 5
        
        if existing_record:
            # 기존 기록 업데이트
            existing_record.stress_level = stress_level
            existing_record.mood = mood
            existing_record.energy_level = energy_level
            existing_record.work_satisfaction = data.get('work_satisfaction')
            existing_record.work_load = data.get('work_load')
            existing_record.work_hours = work_hours
            existing_record.sleep_hours = data.get('sleep_hours')
            existing_record.fatigue = fatigue
            existing_record.emotions = emotions
            existing_record.worked_during_lunch = worked_during_lunch
            existing_record.after_hours_contacts_count = after_hours_contacts_count
            existing_record.unpaid_prep_hours = unpaid_prep_hours
            existing_record.had_drinking_or_overtime = had_drinking_or_overtime
            existing_record.heard_hustle_praise = heard_hustle_praise
            existing_record.none_of_above = none_of_above
            existing_record.daily_sentence = data.get('daily_sentence')
            existing_record.sentence_analysis = sentence_analysis
            existing_record.audio_file_path = audio_file_path
            existing_record.audio_analysis = audio_analysis
            existing_record.notes = data.get('notes')
            existing_record.updated_at = datetime.utcnow()
            
            record = existing_record
            message = 'Record updated successfully'
        else:
            # 새 기록 생성 (프론트엔드 요구 필드 포함)
            record = DailyRecord(
                user_id=user_id,
                record_date=record_date,
                stress_level=stress_level,
                mood=mood,
                energy_level=energy_level,
                work_satisfaction=data.get('work_satisfaction'),
                work_load=data.get('work_load'),
                work_hours=work_hours,
                sleep_hours=data.get('sleep_hours'),
                fatigue=fatigue,
                emotions=emotions,
                worked_during_lunch=worked_during_lunch,
                after_hours_contacts_count=after_hours_contacts_count,
                unpaid_prep_hours=unpaid_prep_hours,
                had_drinking_or_overtime=had_drinking_or_overtime,
                heard_hustle_praise=heard_hustle_praise,
                none_of_above=none_of_above,
                daily_sentence=data.get('daily_sentence'),
                sentence_analysis=sentence_analysis,
                audio_file_path=audio_file_path,
                audio_analysis=audio_analysis,
                notes=data.get('notes')
            )
            db.session.add(record)
            message = 'Record created successfully'
        
        db.session.commit()
        
        # 연속 기록 일수 확인 (마일스톤 체크용)
        streak_count = DailyRecord.get_streak_count(user_id)
        
        return jsonify({
            'message': message,
            'record': record.to_dict(),
            'streak_count': streak_count,
            'analysis_info': {
                'has_audio_analysis': bool(audio_analysis),
                'has_text_analysis': bool(sentence_analysis),
                'stress_level_source': 'audio_analysis' if audio_analysis else 'user_input',
                'note': 'Audio analysis takes priority for stress level determination'
            }
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@records_bp.route('/', methods=['GET'])
# @jwt_required()  # 인증 비활성화
def get_records():
    """사용자의 기록 목록 조회"""
    try:
        user_id = DEFAULT_USER_ID  # 고정된 테스트 사용자 ID
        
        # 쿼리 파라미터
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        limit = request.args.get('limit', 30, type=int)
        
        # 날짜 파싱
        start_date_obj = None
        end_date_obj = None
        
        if start_date:
            start_date_obj = datetime.strptime(start_date, '%Y-%m-%d').date()
        if end_date:
            end_date_obj = datetime.strptime(end_date, '%Y-%m-%d').date()
        
        # 기록 조회
        records = DailyRecord.get_user_records(user_id, start_date_obj, end_date_obj)
        records = records[:limit]  # 제한
        
        # 통계 정보
        streak_count = DailyRecord.get_streak_count(user_id)
        total_records = DailyRecord.query.filter_by(user_id=user_id).count()
        
        return jsonify({
            'records': [record.to_dict() for record in records],
            'stats': {
                'total_count': total_records,  # 프론트엔드 기대 필드명
                'current_streak': streak_count,
                'records_count': len(records)
            }
        }), 200
        
    except Exception as e:
        # 에러 발생 시에도 올바른 형식으로 반환
        return jsonify({
            'error': str(e),
            'records': [],
            'stats': {
                'total_count': 0,
                'current_streak': 0,
                'records_count': 0
            }
        }), 500

@records_bp.route('/<int:record_id>', methods=['GET'])
# @jwt_required()  # 인증 비활성화
def get_record(record_id):
    """특정 기록 조회"""
    try:
        user_id = DEFAULT_USER_ID  # 고정된 테스트 사용자 ID
        
        record = DailyRecord.query.filter_by(
            id=record_id, 
            user_id=user_id
        ).first()
        
        if not record:
            return jsonify({'error': 'Record not found'}), 404
        
        return jsonify({
            'record': record.to_dict()
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@records_bp.route('/<int:record_id>', methods=['PUT'])
# @jwt_required()  # 인증 비활성화
def update_record(record_id):
    """기록 업데이트"""
    try:
        user_id = DEFAULT_USER_ID  # 고정된 테스트 사용자 ID
        
        record = DailyRecord.query.filter_by(
            id=record_id, 
            user_id=user_id
        ).first()
        
        if not record:
            return jsonify({'error': 'Record not found'}), 404
        
        data = request.get_json()
        
        # 업데이트 가능한 필드
        updatable_fields = [
            'stress_level', 'mood', 'energy_level', 
            'work_satisfaction', 'work_load', 'daily_sentence', 'notes'
        ]
        
        for field in updatable_fields:
            if field in data:
                setattr(record, field, data[field])
        
        # 한 문장이 변경된 경우 재분석
        if 'daily_sentence' in data and data['daily_sentence']:
            record.sentence_analysis = analyze_sentence(data['daily_sentence'])
        
        db.session.commit()
        
        return jsonify({
            'message': 'Record updated successfully',
            'record': record.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@records_bp.route('/today', methods=['GET'])
# @jwt_required()  # 인증 비활성화
def get_today_record():
    """오늘의 기록 조회"""
    try:
        user_id = DEFAULT_USER_ID  # 고정된 테스트 사용자 ID
        today = date.today()
        
        record = DailyRecord.query.filter_by(
            user_id=user_id,
            record_date=today
        ).first()
        
        if not record:
            return jsonify({'record': None}), 200
        
        return jsonify({
            'record': record.to_dict()
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
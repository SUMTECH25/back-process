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

@records_bp.route('/', methods=['POST'])
# @jwt_required()  # 인증 비활성화
def create_record():
    """일일 기록 생성"""
    try:
        user_id = DEFAULT_USER_ID  # 고정된 테스트 사용자 ID
        data = request.get_json()
        
        # 필수 필드 검증
        required_fields = ['stress_level', 'mood', 'energy_level']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'{field} is required'}), 400
        
        # 오늘 날짜
        today = date.today()
        record_date = datetime.strptime(data.get('record_date', today.isoformat()), '%Y-%m-%d').date()
        
        # 중복 기록 확인
        existing_record = DailyRecord.query.filter_by(
            user_id=user_id, 
            record_date=record_date
        ).first()
        
        if existing_record:
            return jsonify({'error': 'Record for this date already exists'}), 400
        
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
        
        # 새 기록 생성
        record = DailyRecord(
            user_id=user_id,
            record_date=record_date,
            stress_level=data['stress_level'],
            mood=data['mood'],
            energy_level=data['energy_level'],
            work_satisfaction=data.get('work_satisfaction'),
            work_load=data.get('work_load'),
            daily_sentence=data.get('daily_sentence'),
            sentence_analysis=sentence_analysis,
            audio_file_path=audio_file_path,
            audio_analysis=audio_analysis,
            notes=data.get('notes')
        )
        
        db.session.add(record)
        db.session.commit()
        
        # 연속 기록 일수 확인 (마일스톤 체크용)
        streak_count = DailyRecord.get_streak_count(user_id)
        
        return jsonify({
            'message': 'Record created successfully',
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
                'total_records': total_records,
                'current_streak': streak_count,
                'records_count': len(records)
            }
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

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
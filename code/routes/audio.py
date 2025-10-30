"""
오디오 스트레스 분석 관련 라우트
"""

import os
from flask import Blueprint, request, jsonify, current_app
# JWT 인증 비활성화됨
# from flask_jwt_extended import jwt_required, get_jwt_identity

# 기본 테스트 사용자 ID (인증 비활성화용)
DEFAULT_USER_ID = 1
from werkzeug.utils import secure_filename
from datetime import datetime, date
from models.user import User
from models.daily_record import DailyRecord
from services.audio_stress_service import (
    analyze_audio_stress, 
    analyze_audio_stress_from_data,
    validate_audio_input,
    get_supported_audio_formats
)
from app import db
import logging

logger = logging.getLogger(__name__)

audio_bp = Blueprint('audio', __name__)

# 허용되는 파일 확장자
ALLOWED_EXTENSIONS = {'.wav', '.mp3', '.flac', '.m4a', '.ogg'}
MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB

def allowed_file(filename):
    """허용되는 파일 형식인지 확인"""
    return '.' in filename and \
           os.path.splitext(filename)[1].lower() in ALLOWED_EXTENSIONS

def ensure_upload_dir():
    """업로드 디렉토리 확인 및 생성"""
    upload_dir = os.path.join(os.getcwd(), 'uploads', 'audio')
    os.makedirs(upload_dir, exist_ok=True)
    return upload_dir

@audio_bp.route('/analyze', methods=['POST'])
# @jwt_required()  # 인증 비활성화
def analyze_audio():
    """오디오 파일 업로드 및 스트레스 분석"""
    try:
        user_id = DEFAULT_USER_ID  # 고정된 테스트 사용자 ID
        
        # 파일 업로드 확인
        if 'audio_file' not in request.files:
            return jsonify({'error': 'No audio file provided'}), 400
        
        file = request.files['audio_file']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        # 파일 형식 확인
        if not allowed_file(file.filename):
            return jsonify({
                'error': 'Invalid file format',
                'supported_formats': list(ALLOWED_EXTENSIONS)
            }), 400
        
        # 파일 크기 확인
        file.seek(0, os.SEEK_END)
        file_size = file.tell()
        file.seek(0)  # 파일 포인터 리셋
        
        if file_size > MAX_FILE_SIZE:
            return jsonify({
                'error': f'File too large. Maximum size: {MAX_FILE_SIZE // (1024*1024)}MB'
            }), 400
        
        # 업로드 디렉토리 준비
        upload_dir = ensure_upload_dir()
        
        # 안전한 파일명 생성
        original_filename = secure_filename(file.filename)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"{user_id}_{timestamp}_{original_filename}"
        file_path = os.path.join(upload_dir, filename)
        
        # 파일 저장
        file.save(file_path)
        logger.info(f"Audio file saved: {file_path}")
        
        # 스트레스 분석 수행
        analysis_result = analyze_audio_stress(file_path)
        
        if 'error' in analysis_result:
            # 분석 실패 시 파일 삭제
            if os.path.exists(file_path):
                os.remove(file_path)
            return jsonify({
                'error': 'Audio analysis failed',
                'details': analysis_result['error']
            }), 500
        
        # 요청 파라미터에서 추가 정보 가져오기
        record_date_str = request.form.get('record_date')
        save_to_record = request.form.get('save_to_record', 'false').lower() == 'true'
        
        # 일일 기록에 저장하는 경우
        if save_to_record:
            try:
                # 날짜 처리
                if record_date_str:
                    record_date = datetime.strptime(record_date_str, '%Y-%m-%d').date()
                else:
                    record_date = date.today()
                
                # 해당 날짜의 기록 찾기 또는 생성
                record = DailyRecord.query.filter_by(
                    user_id=user_id,
                    record_date=record_date
                ).first()
                
                if record:
                    # 기존 기록 업데이트
                    record.audio_file_path = file_path
                    record.audio_analysis = analysis_result
                    
                    # 오디오 분석 결과로만 스트레스 레벨 업데이트
                    # (오디오가 있으면 항상 오디오 분석 결과를 우선 사용)
                    update_stress_level = request.form.get('update_stress_level', 'true').lower() == 'true'
                    if update_stress_level:
                        record.stress_level = analysis_result['stress_level']
                        logger.info(f"Updated stress level from audio analysis: {analysis_result['stress_level']}")
                    
                    db.session.commit()
                    logger.info(f"Updated existing record {record.id} with audio analysis")
                else:
                    # 새 기록 생성 (오디오 분석 결과만)
                    record = DailyRecord(
                        user_id=user_id,
                        record_date=record_date,
                        stress_level=analysis_result['stress_level'],
                        mood='neutral',  # 기본값
                        energy_level=5,  # 기본값
                        audio_file_path=file_path,
                        audio_analysis=analysis_result,
                        notes='Audio-only record created from stress analysis'
                    )
                    
                    db.session.add(record)
                    db.session.commit()
                    logger.info(f"Created new record {record.id} with audio analysis")
                
                return jsonify({
                    'message': 'Audio analysis completed and saved to daily record',
                    'analysis_result': analysis_result,
                    'record_id': record.id,
                    'file_path': file_path,
                    'original_filename': original_filename
                }), 200
                
            except Exception as e:
                # 기록 저장 실패 시에도 분석 결과는 반환
                logger.error(f"Error saving audio analysis to record: {str(e)}")
                return jsonify({
                    'message': 'Audio analysis completed but failed to save to record',
                    'analysis_result': analysis_result,
                    'file_path': file_path,
                    'original_filename': original_filename,
                    'warning': str(e)
                }), 200
        
        # 분석 결과만 반환
        return jsonify({
            'message': 'Audio analysis completed',
            'analysis_result': analysis_result,
            'file_path': file_path,
            'original_filename': original_filename
        }), 200
        
    except Exception as e:
        logger.error(f"Error in audio analysis: {str(e)}")
        return jsonify({'error': str(e)}), 500

@audio_bp.route('/analyze-direct', methods=['POST'])
# @jwt_required()  # 인증 비활성화
def analyze_audio_direct():
    """오디오 데이터를 직접 받아서 분석 (파일 저장 안함)"""
    try:
        user_id = DEFAULT_USER_ID  # 고정된 테스트 사용자 ID
        
        # 파일 업로드 확인
        if 'audio_file' not in request.files:
            return jsonify({'error': 'No audio file provided'}), 400
        
        file = request.files['audio_file']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        # 파일 형식 확인
        if not allowed_file(file.filename):
            return jsonify({
                'error': 'Invalid file format',
                'supported_formats': list(ALLOWED_EXTENSIONS)
            }), 400
        
        # 파일 데이터 읽기
        audio_data = file.read()
        
        # 파일 크기 확인
        if len(audio_data) > MAX_FILE_SIZE:
            return jsonify({
                'error': f'File too large. Maximum size: {MAX_FILE_SIZE // (1024*1024)}MB'
            }), 400
        
        # 스트레스 분석 수행 (임시 파일 사용)
        analysis_result = analyze_audio_stress_from_data(audio_data, file.filename)
        
        if 'error' in analysis_result:
            return jsonify({
                'error': 'Audio analysis failed',
                'details': analysis_result['error']
            }), 500
        
        return jsonify({
            'message': 'Audio analysis completed (no file saved)',
            'analysis_result': analysis_result,
            'original_filename': file.filename
        }), 200
        
    except Exception as e:
        logger.error(f"Error in direct audio analysis: {str(e)}")
        return jsonify({'error': str(e)}), 500

@audio_bp.route('/formats', methods=['GET'])
def get_supported_formats():
    """지원되는 오디오 형식 목록"""
    return jsonify({
        'supported_formats': get_supported_audio_formats(),
        'max_file_size_mb': MAX_FILE_SIZE // (1024 * 1024),
        'description': 'Supported audio formats for stress analysis'
    }), 200

@audio_bp.route('/records/<int:record_id>/audio', methods=['GET'])
# @jwt_required()  # 인증 비활성화
def get_record_audio_analysis(record_id):
    """특정 기록의 오디오 분석 결과 조회"""
    try:
        user_id = DEFAULT_USER_ID  # 고정된 테스트 사용자 ID
        
        record = DailyRecord.query.filter_by(
            id=record_id,
            user_id=user_id
        ).first()
        
        if not record:
            return jsonify({'error': 'Record not found'}), 404
        
        if not record.audio_analysis:
            return jsonify({'error': 'No audio analysis found for this record'}), 404
        
        return jsonify({
            'record_id': record_id,
            'record_date': record.record_date.isoformat(),
            'audio_analysis': record.audio_analysis,
            'audio_file_exists': bool(record.audio_file_path and os.path.exists(record.audio_file_path))
        }), 200
        
    except Exception as e:
        logger.error(f"Error retrieving audio analysis: {str(e)}")
        return jsonify({'error': str(e)}), 500

@audio_bp.route('/recent-analyses', methods=['GET'])
# @jwt_required()  # 인증 비활성화
def get_recent_audio_analyses():
    """최근 오디오 분석 결과들 조회"""
    try:
        user_id = DEFAULT_USER_ID  # 고정된 테스트 사용자 ID
        limit = request.args.get('limit', 10, type=int)
        
        # 오디오 분석이 있는 기록들만 조회
        records = DailyRecord.query.filter(
            DailyRecord.user_id == user_id,
            DailyRecord.audio_analysis.isnot(None)
        ).order_by(DailyRecord.record_date.desc()).limit(limit).all()
        
        analyses = []
        for record in records:
            analyses.append({
                'record_id': record.id,
                'record_date': record.record_date.isoformat(),
                'stress_level': record.stress_level,
                'audio_analysis': record.audio_analysis,
                'created_at': record.created_at.isoformat()
            })
        
        return jsonify({
            'recent_analyses': analyses,
            'count': len(analyses)
        }), 200
        
    except Exception as e:
        logger.error(f"Error retrieving recent audio analyses: {str(e)}")
        return jsonify({'error': str(e)}), 500

@audio_bp.route('/stats', methods=['GET'])
# @jwt_required()  # 인증 비활성화
def get_audio_analysis_stats():
    """사용자의 오디오 분석 통계"""
    try:
        user_id = DEFAULT_USER_ID  # 고정된 테스트 사용자 ID
        
        # 오디오 분석이 있는 기록 수
        total_audio_records = DailyRecord.query.filter(
            DailyRecord.user_id == user_id,
            DailyRecord.audio_analysis.isnot(None)
        ).count()
        
        # 전체 기록 수
        total_records = DailyRecord.query.filter_by(user_id=user_id).count()
        
        if total_audio_records == 0:
            return jsonify({
                'message': 'No audio analyses found',
                'total_audio_records': 0,
                'total_records': total_records,
                'audio_usage_rate': 0,
                'recommendation': 'Consider using voice recording for more accurate stress analysis'
            }), 200
        
        # 최근 30일 오디오 분석 기록
        from datetime import timedelta
        thirty_days_ago = date.today() - timedelta(days=30)
        
        recent_records = DailyRecord.query.filter(
            DailyRecord.user_id == user_id,
            DailyRecord.audio_analysis.isnot(None),
            DailyRecord.record_date >= thirty_days_ago
        ).all()
        
        # 스트레스 분포 계산
        stress_distribution = {'low': 0, 'medium': 0, 'high': 0}
        total_confidence = 0
        
        for record in recent_records:
            if record.audio_analysis and 'stress_level' in record.audio_analysis:
                stress_level = record.audio_analysis['stress_level']
                if stress_level <= 3:
                    stress_distribution['low'] += 1
                elif stress_level <= 7:
                    stress_distribution['medium'] += 1
                else:
                    stress_distribution['high'] += 1
                
                confidence = record.audio_analysis.get('confidence', 0)
                total_confidence += confidence
        
        avg_confidence = total_confidence / len(recent_records) if recent_records else 0
        audio_usage_rate = (total_audio_records / total_records * 100) if total_records > 0 else 0
        
        return jsonify({
            'total_audio_records': total_audio_records,
            'total_records': total_records,
            'audio_usage_rate': round(audio_usage_rate, 1),
            'recent_30_days': len(recent_records),
            'stress_distribution': stress_distribution,
            'average_confidence': round(avg_confidence, 2),
            'analysis_period': {
                'start_date': thirty_days_ago.isoformat(),
                'end_date': date.today().isoformat()
            },
            'note': 'Audio analysis is prioritized for stress level determination'
        }), 200
        
    except Exception as e:
        logger.error(f"Error getting audio analysis stats: {str(e)}")
        return jsonify({'error': str(e)}), 500

@audio_bp.route('/policy', methods=['GET'])
def get_analysis_policy():
    """스트레스 분석 정책 정보"""
    return jsonify({
        'analysis_priority': {
            'primary': 'audio_voice_analysis',
            'secondary': 'user_manual_input',
            'reference_only': 'text_nlp_analysis'
        },
        'policy_description': {
            'ko': '음성 분석이 있을 경우 음성 분석 결과를 우선적으로 사용하며, 텍스트 NLP 분석은 참고용으로만 활용됩니다.',
            'en': 'When audio analysis is available, it takes priority for stress level determination. Text NLP analysis is used for reference only.'
        },
        'supported_audio_formats': ['.wav', '.mp3', '.flac', '.m4a', '.ogg'],
        'model_info': {
            'audio_model': 'forwarder1121/voice-based-stress-recognition',
            'embedding_model': 'facebook/wav2vec2-base',
            'text_model': 'keyword_based_analysis (reference only)'
        }
    }), 200
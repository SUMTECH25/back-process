"""
리포트 생성 관련 라우트
"""

from flask import Blueprint, request, jsonify, send_file
# JWT 인증 비활성화됨
# from flask_jwt_extended import jwt_required, get_jwt_identity

# 기본 테스트 사용자 ID (인증 비활성화용)
DEFAULT_USER_ID = 1
from datetime import datetime, date, timedelta
from models.user import User
from models.daily_record import DailyRecord
from models.milestone import Milestone
from services.report_service import generate_analysis_report, generate_pdf_report
from app import db
import os

reports_bp = Blueprint('reports', __name__)

@reports_bp.route('/analysis/<milestone_type>', methods=['GET'])
# @jwt_required()  # 인증 비활성화
def get_analysis_report(milestone_type):
    """분석 리포트 조회 (3일, 7일, 30일)"""
    try:
        user_id = DEFAULT_USER_ID  # 고정된 테스트 사용자 ID
        
        if milestone_type not in ['3', '7', '30']:
            return jsonify({'error': 'Invalid milestone type'}), 400
        
        # 해당 마일스톤이 달성되었는지 확인
        milestone = Milestone.query.filter_by(
            user_id=user_id,
            milestone_type=milestone_type
        ).order_by(Milestone.achieved_at.desc()).first()
        
        if not milestone:
            return jsonify({'error': 'Milestone not achieved yet'}), 400
        
        # 리포트 데이터가 없으면 생성
        if not milestone.reward_data:
            days = int(milestone_type)
            end_date = date.today()
            start_date = end_date - timedelta(days=days-1)
            
            milestone.reward_data = generate_analysis_report(user_id, start_date, end_date, milestone_type)
            db.session.commit()
        
        return jsonify({
            'milestone_type': milestone_type,
            'achieved_at': milestone.achieved_at.isoformat(),
            'report_data': milestone.reward_data
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@reports_bp.route('/pdf/<int:milestone_id>', methods=['GET'])
# @jwt_required()  # 인증 비활성화
def get_pdf_report(milestone_id):
    """PDF 리포트 다운로드 (30일 전용)"""
    try:
        user_id = DEFAULT_USER_ID  # 고정된 테스트 사용자 ID
        
        milestone = Milestone.query.filter_by(
            id=milestone_id,
            user_id=user_id,
            milestone_type='30'
        ).first()
        
        if not milestone:
            return jsonify({'error': 'Milestone not found or not 30-day milestone'}), 404
        
        # PDF가 없으면 생성
        if not milestone.pdf_path or not os.path.exists(milestone.pdf_path):
            pdf_path = generate_pdf_report(user_id, milestone.reward_data)
            milestone.pdf_path = pdf_path
            db.session.commit()
        
        return send_file(
            milestone.pdf_path,
            as_attachment=True,
            download_name=f'30day_report_{user_id}_{milestone.id}.pdf',
            mimetype='application/pdf'
        )
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@reports_bp.route('/summary', methods=['GET'])
# @jwt_required()  # 인증 비활성화
def get_summary():
    """전체 요약 리포트"""
    try:
        user_id = DEFAULT_USER_ID  # 고정된 테스트 사용자 ID
        
        # 쿼리 파라미터
        days = request.args.get('days', 30, type=int)
        
        # 날짜 범위
        end_date = date.today()
        start_date = end_date - timedelta(days=days-1)
        
        # 기간 내 기록 조회
        records = DailyRecord.get_user_records(user_id, start_date, end_date)
        
        if not records:
            return jsonify({
                'message': 'No records found for the specified period',
                'period': {
                    'start_date': start_date.isoformat(),
                    'end_date': end_date.isoformat(),
                    'days': days
                }
            }), 200
        
        # 기본 통계
        total_records = len(records)
        avg_stress = sum(r.stress_level for r in records) / total_records
        avg_energy = sum(r.energy_level for r in records) / total_records
        
        # 기분 분포
        mood_counts = {}
        for record in records:
            mood_counts[record.mood] = mood_counts.get(record.mood, 0) + 1
        
        # 스트레스 트렌드 (최근 7일)
        recent_records = records[:7] if len(records) >= 7 else records
        stress_trend = [r.stress_level for r in reversed(recent_records)]
        
        # 업무 관련 통계 (데이터가 있는 경우)
        work_records = [r for r in records if r.work_satisfaction is not None]
        work_stats = None
        if work_records:
            avg_satisfaction = sum(r.work_satisfaction for r in work_records) / len(work_records)
            avg_workload = sum(r.work_load for r in work_records) / len(work_records) if work_records[0].work_load else None
            work_stats = {
                'average_satisfaction': round(avg_satisfaction, 2),
                'average_workload': round(avg_workload, 2) if avg_workload else None,
                'records_with_work_data': len(work_records)
            }
        
        return jsonify({
            'period': {
                'start_date': start_date.isoformat(),
                'end_date': end_date.isoformat(),
                'days': days
            },
            'summary': {
                'total_records': total_records,
                'average_stress_level': round(avg_stress, 2),
                'average_energy_level': round(avg_energy, 2),
                'mood_distribution': mood_counts,
                'stress_trend': stress_trend,
                'work_stats': work_stats
            }
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@reports_bp.route('/insights', methods=['GET'])
# @jwt_required()  # 인증 비활성화
def get_insights():
    """개인화된 인사이트 제공"""
    try:
        user_id = DEFAULT_USER_ID  # 고정된 테스트 사용자 ID
        
        # 최근 30일 데이터
        end_date = date.today()
        start_date = end_date - timedelta(days=29)
        records = DailyRecord.get_user_records(user_id, start_date, end_date)
        
        insights = []
        
        if len(records) >= 7:
            # 스트레스 패턴 분석
            stress_levels = [r.stress_level for r in records]
            avg_stress = sum(stress_levels) / len(stress_levels)
            
            if avg_stress > 7:
                insights.append({
                    'type': 'warning',
                    'title': '높은 스트레스 수준 감지',
                    'message': f'최근 {len(records)}일간 평균 스트레스 수준이 {avg_stress:.1f}입니다. 스트레스 관리 방법을 찾아보세요.',
                    'priority': 'high'
                })
            elif avg_stress < 4:
                insights.append({
                    'type': 'positive',
                    'title': '안정적인 스트레스 관리',
                    'message': f'최근 {len(records)}일간 스트레스 수준을 잘 관리하고 계시네요! (평균: {avg_stress:.1f})',
                    'priority': 'medium'
                })
            
            # 에너지 레벨 분석
            energy_levels = [r.energy_level for r in records]
            avg_energy = sum(energy_levels) / len(energy_levels)
            
            if avg_energy < 4:
                insights.append({
                    'type': 'info',
                    'title': '에너지 수준 개선 필요',
                    'message': f'평균 에너지 수준이 {avg_energy:.1f}입니다. 충분한 휴식과 운동을 고려해보세요.',
                    'priority': 'medium'
                })
            
            # 연속 기록 격려
            streak = DailyRecord.get_streak_count(user_id)
            if streak >= 7:
                insights.append({
                    'type': 'achievement',
                    'title': f'{streak}일 연속 기록 달성!',
                    'message': '꾸준한 기록 습관이 형성되고 있습니다. 계속 이어가세요!',
                    'priority': 'high'
                })
        
        return jsonify({
            'insights': insights,
            'data_period': {
                'start_date': start_date.isoformat(),
                'end_date': end_date.isoformat(),
                'records_count': len(records)
            }
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
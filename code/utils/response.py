"""
응답 형식화 유틸리티
"""

from datetime import datetime, date, timezone
from typing import Dict, Any, List, Optional, Union
from flask import jsonify

def success_response(data: Any = None, message: str = "Success", status_code: int = 200) -> tuple:
    """성공 응답 형식화"""
    response_data = {
        'success': True,
        'message': message,
        'timestamp': datetime.now(timezone.utc).isoformat(),
        'data': data
    }
    
    return jsonify(response_data), status_code

def error_response(message: str, status_code: int = 400, error_code: str = None, details: Any = None) -> tuple:
    """에러 응답 형식화"""
    response_data = {
        'success': False,
        'message': message,
        'timestamp': datetime.now(timezone.utc).isoformat(),
        'error': {
            'code': error_code or f'ERROR_{status_code}',
            'details': details
        }
    }
    
    return jsonify(response_data), status_code

def validation_error_response(errors: List[str], status_code: int = 400) -> tuple:
    """유효성 검사 에러 응답"""
    return error_response(
        message="Validation failed",
        status_code=status_code,
        error_code="VALIDATION_ERROR",
        details={'validation_errors': errors}
    )

def paginated_response(items: List[Any], page: int, per_page: int, total: int, message: str = "Success") -> tuple:
    """페이지네이션된 응답"""
    total_pages = (total + per_page - 1) // per_page  # 올림 계산
    
    data = {
        'items': items,
        'pagination': {
            'page': page,
            'per_page': per_page,
            'total': total,
            'total_pages': total_pages,
            'has_next': page < total_pages,
            'has_prev': page > 1,
            'next_page': page + 1 if page < total_pages else None,
            'prev_page': page - 1 if page > 1 else None
        }
    }
    
    return success_response(data, message)

def milestone_achievement_response(milestone: Any, is_new: bool = True) -> tuple:
    """마일스톤 달성 응답"""
    message = "새로운 마일스톤을 달성했습니다!" if is_new else "마일스톤 정보"
    
    data = {
        'milestone': milestone.to_dict() if hasattr(milestone, 'to_dict') else milestone,
        'achievement': {
            'is_new': is_new,
            'reward_available': True,
            'celebration_message': f"{milestone.milestone_type}일 연속 기록 달성을 축하합니다!"
        }
    }
    
    return success_response(data, message, 201 if is_new else 200)

def analysis_report_response(report_data: Dict, report_type: str) -> tuple:
    """분석 리포트 응답"""
    insights_count = len(report_data.get('insights', []))
    
    data = {
        'report': report_data,
        'meta': {
            'report_type': report_type,
            'insights_count': insights_count,
            'generated_at': report_data.get('generated_at', datetime.now(timezone.utc).isoformat()),
            'data_quality': get_data_quality_score(report_data)
        }
    }
    
    return success_response(data, f"{report_type}일 분석 리포트가 생성되었습니다.")

def get_data_quality_score(report_data: Dict) -> str:
    """데이터 품질 점수 계산"""
    total_records = report_data.get('period', {}).get('duration_days', 0)
    expected_records = int(report_data.get('report_type', '0').split('일')[0])
    
    if total_records >= expected_records:
        return 'high'
    elif total_records >= expected_records * 0.7:
        return 'medium'
    else:
        return 'low'

def streak_info_response(current_streak: int, user_data: Dict = None) -> tuple:
    """연속 기록 정보 응답"""
    # 다음 마일스톤 계산
    milestones = [3, 7, 30]
    next_milestone = None
    days_to_next = 0
    
    for milestone in milestones:
        if current_streak < milestone:
            next_milestone = milestone
            days_to_next = milestone - current_streak
            break
    
    # 진행률 계산
    if next_milestone:
        progress_percentage = (current_streak / next_milestone) * 100
    else:
        progress_percentage = 100
    
    data = {
        'current_streak': current_streak,
        'next_milestone': next_milestone,
        'days_to_next_milestone': days_to_next,
        'progress_percentage': round(progress_percentage, 1),
        'encouragement_message': get_encouragement_message(current_streak),
        'streak_status': get_streak_status(current_streak)
    }
    
    if user_data:
        data['user'] = user_data
    
    return success_response(data, "연속 기록 정보")

def get_encouragement_message(streak: int) -> str:
    """연속 기록에 따른 격려 메시지"""
    if streak == 0:
        return "오늘부터 새로운 시작입니다! 첫 기록을 남겨보세요."
    elif streak == 1:
        return "좋은 시작입니다! 내일도 계속해보세요."
    elif streak < 3:
        return f"{streak}일째 기록 중입니다. 3일 마일스톤까지 조금만 더!"
    elif streak == 3:
        return "🎉 3일 연속 달성! 첫 마일스톤을 완성했습니다."
    elif streak < 7:
        return f"{streak}일째 훌륭합니다! 7일 마일스톤을 향해 가고 있어요."
    elif streak == 7:
        return "🎉 일주일 연속 달성! 정말 대단합니다."
    elif streak < 30:
        return f"{streak}일째 연속 기록 중! 30일 마일스톤까지 {30-streak}일 남았어요."
    elif streak == 30:
        return "🎉 30일 연속 달성! 놀라운 성취입니다!"
    else:
        return f"🔥 {streak}일 연속! 이미 모든 마일스톤을 달성한 챔피언입니다!"

def get_streak_status(streak: int) -> str:
    """연속 기록 상태"""
    if streak == 0:
        return "새로운 시작"
    elif streak < 3:
        return "초기 단계"
    elif streak < 7:
        return "기초 형성"
    elif streak < 30:
        return "습관 형성 중"
    else:
        return "마스터 레벨"

def health_check_response() -> tuple:
    """헬스 체크 응답"""
    data = {
        'status': 'healthy',
        'version': '1.0.0',
        'timestamp': datetime.now(timezone.utc).isoformat(),
        'services': {
            'database': 'connected',
            'nlp_service': 'available',
            'pdf_service': 'available'
        }
    }
    
    return success_response(data, "서비스가 정상적으로 운영 중입니다.")

def statistics_response(stats: Dict) -> tuple:
    """통계 정보 응답"""
    # 통계 요약 생성
    summary = {
        'total_entries': stats.get('total_records', 0),
        'average_stress': round(stats.get('average_stress_level', 0), 1),
        'average_energy': round(stats.get('average_energy_level', 0), 1),
        'data_quality': 'high' if stats.get('total_records', 0) > 20 else 'medium' if stats.get('total_records', 0) > 5 else 'low'
    }
    
    data = {
        'statistics': stats,
        'summary': summary,
        'insights': generate_quick_insights(stats)
    }
    
    return success_response(data, "통계 정보")

def generate_quick_insights(stats: Dict) -> List[str]:
    """통계 기반 빠른 인사이트 생성"""
    insights = []
    
    avg_stress = stats.get('average_stress_level', 5)
    avg_energy = stats.get('average_energy_level', 5)
    total_records = stats.get('total_records', 0)
    
    if avg_stress > 7:
        insights.append("평균 스트레스 수준이 높습니다. 스트레스 관리가 필요해 보입니다.")
    elif avg_stress < 4:
        insights.append("스트레스 수준이 양호합니다. 좋은 상태를 유지하고 계시네요!")
    
    if avg_energy < 4:
        insights.append("평균 에너지 수준이 낮습니다. 휴식과 회복이 필요할 수 있습니다.")
    elif avg_energy > 7:
        insights.append("에너지 수준이 높습니다. 활기찬 상태를 잘 유지하고 계십니다!")
    
    if total_records > 30:
        insights.append("꾸준한 기록 습관이 형성되었습니다. 훌륭합니다!")
    elif total_records > 7:
        insights.append("기록 습관이 형성되고 있습니다. 계속 이어가세요!")
    
    return insights

def format_datetime(dt: Union[datetime, date, str]) -> str:
    """날짜/시간 형식화"""
    if isinstance(dt, str):
        return dt
    elif isinstance(dt, datetime):
        return dt.isoformat()
    elif isinstance(dt, date):
        return dt.isoformat()
    else:
        return str(dt)

def clean_response_data(data: Any) -> Any:
    """응답 데이터 정리 (None 값 제거, 날짜 형식화 등)"""
    if isinstance(data, dict):
        return {k: clean_response_data(v) for k, v in data.items() if v is not None}
    elif isinstance(data, list):
        return [clean_response_data(item) for item in data]
    elif isinstance(data, (datetime, date)):
        return format_datetime(data)
    else:
        return data
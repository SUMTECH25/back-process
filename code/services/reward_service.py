"""
보상 시스템 서비스
"""

from datetime import datetime, date, timedelta
from typing import List, Dict, Optional
from models.user import User
from models.daily_record import DailyRecord
from models.milestone import Milestone
from app import db
import logging

logger = logging.getLogger(__name__)

def check_and_create_milestones(user_id: int, current_streak: int) -> List[Milestone]:
    """
    현재 연속 기록을 바탕으로 새로운 마일스톤 생성
    
    Args:
        user_id: 사용자 ID
        current_streak: 현재 연속 기록 일수
    
    Returns:
        새로 생성된 마일스톤 리스트
    """
    new_milestones = []
    milestone_targets = [3, 7, 30]
    
    try:
        for target in milestone_targets:
            if current_streak >= target:
                # 해당 마일스톤이 이미 존재하는지 확인
                existing_milestone = Milestone.query.filter_by(
                    user_id=user_id,
                    milestone_type=str(target),
                    streak_count=current_streak
                ).first()
                
                if not existing_milestone:
                    # 보상 데이터 생성
                    reward_data = generate_reward_data(user_id, str(target))
                    
                    # 새 마일스톤 생성
                    milestone = Milestone.create_milestone(
                        user_id=user_id,
                        milestone_type=str(target),
                        streak_count=current_streak,
                        reward_data=reward_data
                    )
                    
                    new_milestones.append(milestone)
                    logger.info(f"Created new milestone: {target} days for user {user_id}")
        
        return new_milestones
        
    except Exception as e:
        logger.error(f"Error creating milestones for user {user_id}: {str(e)}")
        db.session.rollback()
        return []

def generate_reward_data(user_id: int, milestone_type: str) -> Dict:
    """
    마일스톤 타입에 따른 보상 데이터 생성
    
    Args:
        user_id: 사용자 ID
        milestone_type: '3', '7', '30'
    
    Returns:
        보상 데이터 딕셔너리
    """
    try:
        if milestone_type == '3':
            return generate_3day_analysis(user_id)
        elif milestone_type == '7':
            return generate_7day_prediction(user_id)
        elif milestone_type == '30':
            return generate_30day_report(user_id)
        else:
            return {'error': 'Invalid milestone type'}
            
    except Exception as e:
        logger.error(f"Error generating reward data: {str(e)}")
        return {'error': str(e)}

def generate_3day_analysis(user_id: int) -> Dict:
    """3일 기본 분석 리포트"""
    try:
        # 최근 3일 데이터
        end_date = date.today()
        start_date = end_date - timedelta(days=2)
        
        records = DailyRecord.get_user_records(user_id, start_date, end_date)
        
        if len(records) < 3:
            return {
                'message': '3일 연속 기록이 부족합니다.',
                'records_count': len(records)
            }
        
        # 기본 통계
        stress_levels = [r.stress_level for r in records]
        energy_levels = [r.energy_level for r in records]
        moods = [r.mood for r in records]
        
        avg_stress = sum(stress_levels) / len(stress_levels)
        avg_energy = sum(energy_levels) / len(energy_levels)
        
        # 가장 흔한 기분
        from collections import Counter
        mood_counter = Counter(moods)
        dominant_mood = mood_counter.most_common(1)[0][0]
        
        # 기본 인사이트
        insights = []
        if avg_stress > 7:
            insights.append("높은 스트레스 수준이 관찰됩니다. 휴식이 필요해 보입니다.")
        elif avg_stress < 4:
            insights.append("스트레스 수준이 양호합니다. 좋은 상태를 유지하고 계시네요!")
        
        if avg_energy < 4:
            insights.append("에너지 수준이 낮습니다. 충분한 수면과 영양 섭취를 고려해보세요.")
        elif avg_energy > 7:
            insights.append("에너지 수준이 높습니다. 활기찬 하루를 보내고 계시네요!")
        
        return {
            'milestone_type': '3일 분석',
            'period': {
                'start_date': start_date.isoformat(),
                'end_date': end_date.isoformat()
            },
            'statistics': {
                'average_stress_level': round(avg_stress, 1),
                'average_energy_level': round(avg_energy, 1),
                'dominant_mood': dominant_mood,
                'total_records': len(records)
            },
            'daily_breakdown': [
                {
                    'date': r.record_date.isoformat(),
                    'stress_level': r.stress_level,
                    'energy_level': r.energy_level,
                    'mood': r.mood
                } for r in reversed(records)
            ],
            'insights': insights,
            'generated_at': datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error generating 3-day analysis: {str(e)}")
        return {'error': str(e)}

def generate_7day_prediction(user_id: int) -> Dict:
    """7일 한계점 예측 리포트"""
    try:
        # 최근 7일 데이터
        end_date = date.today()
        start_date = end_date - timedelta(days=6)
        
        records = DailyRecord.get_user_records(user_id, start_date, end_date)
        
        if len(records) < 7:
            return {
                'message': '7일 연속 기록이 부족합니다.',
                'records_count': len(records)
            }
        
        # 트렌드 분석
        stress_levels = [r.stress_level for r in reversed(records)]  # 시간순으로 정렬
        energy_levels = [r.energy_level for r in reversed(records)]
        
        # 간단한 선형 트렌드 계산
        def calculate_trend(values):
            n = len(values)
            x_sum = sum(range(n))
            y_sum = sum(values)
            xy_sum = sum(i * values[i] for i in range(n))
            x2_sum = sum(i * i for i in range(n))
            
            slope = (n * xy_sum - x_sum * y_sum) / (n * x2_sum - x_sum * x_sum)
            return slope
        
        stress_trend = calculate_trend(stress_levels)
        energy_trend = calculate_trend(energy_levels)
        
        # 예측 및 권장사항
        predictions = []
        recommendations = []
        
        if stress_trend > 0.3:
            predictions.append("스트레스 수준이 상승 추세입니다.")
            recommendations.append("스트레스 관리 기법 (명상, 운동 등)을 시도해보세요.")
        elif stress_trend < -0.3:
            predictions.append("스트레스 수준이 개선되고 있습니다.")
            recommendations.append("현재의 좋은 습관을 계속 유지하세요.")
        
        if energy_trend < -0.3:
            predictions.append("에너지 수준이 감소하고 있습니다.")
            recommendations.append("충분한 휴식과 규칙적인 수면 패턴을 고려해보세요.")
        
        # 위험 예측
        current_avg_stress = sum(stress_levels[-3:]) / 3  # 최근 3일 평균
        risk_level = "low"
        
        if current_avg_stress > 8:
            risk_level = "high"
        elif current_avg_stress > 6:
            risk_level = "medium"
        
        return {
            'milestone_type': '7일 예측 분석',
            'period': {
                'start_date': start_date.isoformat(),
                'end_date': end_date.isoformat()
            },
            'trend_analysis': {
                'stress_trend': round(stress_trend, 3),
                'energy_trend': round(energy_trend, 3),
                'stress_direction': 'increasing' if stress_trend > 0 else 'decreasing' if stress_trend < 0 else 'stable',
                'energy_direction': 'increasing' if energy_trend > 0 else 'decreasing' if energy_trend < 0 else 'stable'
            },
            'predictions': predictions,
            'recommendations': recommendations,
            'risk_assessment': {
                'level': risk_level,
                'current_avg_stress': round(current_avg_stress, 1)
            },
            'weekly_pattern': {
                'stress_levels': stress_levels,
                'energy_levels': energy_levels,
                'dates': [r.record_date.isoformat() for r in reversed(records)]
            },
            'generated_at': datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error generating 7-day prediction: {str(e)}")
        return {'error': str(e)}

def generate_30day_report(user_id: int) -> Dict:
    """30일 종합 리포트"""
    try:
        # 최근 30일 데이터
        end_date = date.today()
        start_date = end_date - timedelta(days=29)
        
        records = DailyRecord.get_user_records(user_id, start_date, end_date)
        user = User.query.get(user_id)
        
        if len(records) < 30:
            return {
                'message': '30일 연속 기록이 부족합니다.',
                'records_count': len(records)
            }
        
        # 종합 통계
        stress_levels = [r.stress_level for r in records]
        energy_levels = [r.energy_level for r in records]
        moods = [r.mood for r in records]
        
        # 기본 통계
        stats = {
            'avg_stress': sum(stress_levels) / len(stress_levels),
            'avg_energy': sum(energy_levels) / len(energy_levels),
            'max_stress': max(stress_levels),
            'min_stress': min(stress_levels),
            'stress_variance': calculate_variance(stress_levels)
        }
        
        # 주간별 분석
        weekly_analysis = analyze_weekly_patterns(records)
        
        # 기분 패턴
        from collections import Counter
        mood_distribution = Counter(moods)
        
        # 오디오 분석 우선, 텍스트 분석은 참고용
        audio_records = [r for r in records if r.audio_analysis]
        text_records = [r for r in records if r.daily_sentence and r.sentence_analysis]
        
        # 오디오 분석 통계 (우선)
        audio_analysis = None
        if audio_records:
            audio_stress_levels = []
            audio_confidences = []
            stressed_count = 0
            
            for record in audio_records:
                if 'stress_level' in record.audio_analysis:
                    audio_stress_levels.append(record.audio_analysis['stress_level'])
                    audio_confidences.append(record.audio_analysis.get('confidence', 0))
                    if record.audio_analysis.get('is_stressed', False):
                        stressed_count += 1
            
            if audio_stress_levels:
                audio_analysis = {
                    'total_audio_records': len(audio_records),
                    'average_audio_stress': sum(audio_stress_levels) / len(audio_stress_levels),
                    'average_confidence': sum(audio_confidences) / len(audio_confidences) if audio_confidences else 0,
                    'stressed_days_ratio': stressed_count / len(audio_records),
                    'analysis_method': 'voice_based_primary'
                }
        
        # 텍스트 분석 (참고용)
        text_emotion_analysis = None
        if text_records:
            from services.nlp_service import extract_emotion_patterns
            sentences = [r.daily_sentence for r in text_records]
            text_emotion_analysis = extract_emotion_patterns(sentences)
            if text_emotion_analysis:
                text_emotion_analysis['analysis_method'] = 'text_based_reference'
        
        # 개인화된 인사이트
        insights = generate_personalized_insights(records, user)
        
        return {
            'milestone_type': '30일 종합 리포트',
            'user_profile': {
                'name': user.name,
                'occupation': user.occupation,
                'baseline_stress': user.stress_level
            },
            'period': {
                'start_date': start_date.isoformat(),
                'end_date': end_date.isoformat(),
                'total_days': len(records)
            },
            'overall_statistics': {
                'average_stress_level': round(stats['avg_stress'], 1),
                'average_energy_level': round(stats['avg_energy'], 1),
                'stress_range': f"{stats['min_stress']} - {stats['max_stress']}",
                'stress_consistency': 'high' if stats['stress_variance'] < 2 else 'medium' if stats['stress_variance'] < 4 else 'low',
                'mood_distribution': dict(mood_distribution)
            },
            'weekly_patterns': weekly_analysis,
            'audio_analysis': audio_analysis,
            'text_emotion_analysis': text_emotion_analysis,
            'personalized_insights': insights,
            'achievements': {
                'consecutive_days': len(records),
                'milestone_reached': '30일 연속 기록 달성',
                'completion_rate': '100%'
            },
            'generated_at': datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error generating 30-day report: {str(e)}")
        return {'error': str(e)}

def calculate_variance(values):
    """분산 계산"""
    mean = sum(values) / len(values)
    return sum((x - mean) ** 2 for x in values) / len(values)

def analyze_weekly_patterns(records):
    """주간별 패턴 분석"""
    weeks = []
    for i in range(0, len(records), 7):
        week_records = records[i:i+7]
        if len(week_records) >= 5:  # 최소 5일 이상
            week_stress = sum(r.stress_level for r in week_records) / len(week_records)
            week_energy = sum(r.energy_level for r in week_records) / len(week_records)
            
            weeks.append({
                'week_number': len(weeks) + 1,
                'avg_stress': round(week_stress, 1),
                'avg_energy': round(week_energy, 1),
                'days_recorded': len(week_records)
            })
    
    return weeks

def generate_personalized_insights(records, user):
    """개인화된 인사이트 생성 (오디오 분석 우선)"""
    insights = []
    
    # 오디오 분석이 있는 기록과 없는 기록 구분
    audio_records = [r for r in records if r.audio_analysis and 'stress_level' in r.audio_analysis]
    all_stress_levels = [r.stress_level for r in records]
    avg_stress = sum(all_stress_levels) / len(all_stress_levels)
    
    # 오디오 분석 기반 인사이트 (우선)
    if audio_records:
        audio_stress_levels = [r.audio_analysis['stress_level'] for r in audio_records]
        avg_audio_stress = sum(audio_stress_levels) / len(audio_stress_levels)
        audio_confidences = [r.audio_analysis.get('confidence', 0) for r in audio_records]
        avg_confidence = sum(audio_confidences) / len(audio_confidences)
        
        insights.append({
            'type': 'info',
            'message': f'음성 분석 기반 평균 스트레스: {avg_audio_stress:.1f}/10 (신뢰도: {avg_confidence:.1f}%)'
        })
        
        if avg_confidence > 80:
            insights.append({
                'type': 'positive',
                'message': '음성 분석 신뢰도가 높습니다. 정확한 스트레스 측정이 이루어지고 있어요.'
            })
        
        # 음성 기반 스트레스 수준 평가
        if avg_audio_stress > 7:
            insights.append({
                'type': 'concern',
                'message': '음성 분석 결과 높은 스트레스 수준이 감지됩니다. 휴식과 스트레스 관리가 필요해 보입니다.'
            })
        elif avg_audio_stress < 4:
            insights.append({
                'type': 'positive',
                'message': '음성 분석 결과 안정적인 스트레스 상태를 보여주고 있습니다.'
            })
    
    # 사용자 기준선과 비교 (전체 평균 기준)
    if user.stress_level:
        if avg_stress > user.stress_level + 2:
            insights.append({
                'type': 'concern',
                'message': f'평소보다 스트레스 수준이 높습니다. (기준: {user.stress_level}, 실제: {avg_stress:.1f})'
            })
        elif avg_stress < user.stress_level - 1:
            insights.append({
                'type': 'positive',
                'message': f'평소보다 스트레스 관리를 잘하고 계시네요!'
            })
    
    # 직업별 맞춤 조언
    if user.occupation:
        occupation_insights = get_occupation_specific_insights(user.occupation, avg_stress)
        insights.extend(occupation_insights)
    
    # 패턴 기반 조언
    high_stress_days = sum(1 for level in all_stress_levels if level >= 8)
    if high_stress_days > 10:
        insights.append({
            'type': 'advice',
            'message': f'30일 중 {high_stress_days}일이 높은 스트레스 상태였습니다. 정기적인 스트레스 해소 활동을 권장합니다.'
        })
    
    # 오디오 분석 사용 권장
    if len(audio_records) < len(records) * 0.3:  # 30% 미만만 오디오 분석 사용
        insights.append({
            'type': 'recommendation',
            'message': '더 정확한 스트레스 분석을 위해 음성 녹음 기능을 더 자주 사용해보세요.'
        })
    
    return insights

def get_occupation_specific_insights(occupation, avg_stress):
    """직업별 맞춤 인사이트"""
    insights = []
    
    occupation_lower = occupation.lower()
    
    if any(word in occupation_lower for word in ['개발자', 'developer', '프로그래머']):
        if avg_stress > 6:
            insights.append({
                'type': 'advice',
                'message': '개발자 특성상 장시간 집중이 필요한 업무입니다. 정기적인 휴식과 눈 운동을 권장합니다.'
            })
    elif any(word in occupation_lower for word in ['의사', 'doctor', '간호사', 'nurse']):
        insights.append({
            'type': 'advice',
            'message': '의료진은 높은 책임감으로 인한 스트레스가 클 수 있습니다. 자기 관리에도 신경 써주세요.'
        })
    elif any(word in occupation_lower for word in ['교사', 'teacher', '강사']):
        insights.append({
            'type': 'advice',
            'message': '교육자는 타인을 위한 에너지 소모가 큽니다. 개인 시간 확보가 중요합니다.'
        })
    
    return insights
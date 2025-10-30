"""
보상 시스템 관련 라우트
"""

from flask import Blueprint, request, jsonify
# JWT 인증 비활성화됨
# from flask_jwt_extended import jwt_required, get_jwt_identity

# 기본 테스트 사용자 ID (인증 비활성화용)
DEFAULT_USER_ID = 1
from datetime import datetime, date
from models.user import User
from models.daily_record import DailyRecord
from models.milestone import Milestone
from services.reward_service import check_and_create_milestones, generate_reward_data
from app import db

rewards_bp = Blueprint('rewards', __name__)

@rewards_bp.route('/check', methods=['POST'])
# @jwt_required()  # 인증 비활성화
def check_milestones():
    """마일스톤 달성 여부 확인 및 보상 생성"""
    try:
        user_id = DEFAULT_USER_ID  # 고정된 테스트 사용자 ID
        
        # 현재 연속 기록 일수
        streak_count = DailyRecord.get_streak_count(user_id)
        
        # 마일스톤 확인 및 생성
        new_milestones = check_and_create_milestones(user_id, streak_count)
        
        return jsonify({
            'current_streak': streak_count,
            'new_milestones': [milestone.to_dict() for milestone in new_milestones],
            'milestone_achieved': len(new_milestones) > 0
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@rewards_bp.route('/milestones', methods=['GET'])
# @jwt_required()  # 인증 비활성화
def get_milestones():
    """사용자의 마일스톤 목록 조회"""
    try:
        user_id = DEFAULT_USER_ID  # 고정된 테스트 사용자 ID
        
        # 쿼리 파라미터
        milestone_type = request.args.get('type')  # '3', '7', '30'
        
        milestones = Milestone.get_user_milestones(user_id, milestone_type)
        
        return jsonify({
            'milestones': [milestone.to_dict() for milestone in milestones]
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@rewards_bp.route('/milestones/<int:milestone_id>/claim', methods=['POST'])
# @jwt_required()  # 인증 비활성화
def claim_reward(milestone_id):
    """보상 수령"""
    try:
        user_id = DEFAULT_USER_ID  # 고정된 테스트 사용자 ID
        
        milestone = Milestone.query.filter_by(
            id=milestone_id,
            user_id=user_id
        ).first()
        
        if not milestone:
            return jsonify({'error': 'Milestone not found'}), 404
        
        if milestone.is_claimed:
            return jsonify({'error': 'Reward already claimed'}), 400
        
        # 보상 데이터 생성 (아직 없는 경우)
        if not milestone.reward_data:
            milestone.reward_data = generate_reward_data(user_id, milestone.milestone_type)
        
        # 보상 수령 처리
        milestone.is_claimed = True
        db.session.commit()
        
        return jsonify({
            'message': 'Reward claimed successfully',
            'milestone': milestone.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@rewards_bp.route('/progress', methods=['GET'])
# @jwt_required()  # 인증 비활성화
def get_progress():
    """보상 진행 상황 조회"""
    try:
        user_id = DEFAULT_USER_ID  # 고정된 테스트 사용자 ID
        
        # 현재 연속 기록
        streak_count = DailyRecord.get_streak_count(user_id)
        
        # 각 마일스톤별 진행 상황
        milestones_info = []
        for milestone_type in ['3', '7', '30']:
            target = int(milestone_type)
            achieved = streak_count >= target
            
            # 가장 최근 달성한 마일스톤
            latest_milestone = Milestone.query.filter_by(
                user_id=user_id,
                milestone_type=milestone_type
            ).order_by(Milestone.achieved_at.desc()).first()
            
            milestones_info.append({
                'type': milestone_type,
                'target': target,
                'current_progress': min(streak_count, target),
                'achieved': achieved,
                'progress_percentage': min(100, (streak_count / target) * 100),
                'latest_achievement': latest_milestone.to_dict() if latest_milestone else None
            })
        
        # 전체 통계
        total_milestones = Milestone.query.filter_by(user_id=user_id).count()
        claimed_rewards = Milestone.query.filter_by(user_id=user_id, is_claimed=True).count()
        
        return jsonify({
            'current_streak': streak_count,
            'milestones': milestones_info,
            'stats': {
                'total_milestones_achieved': total_milestones,
                'rewards_claimed': claimed_rewards,
                'unclaimed_rewards': total_milestones - claimed_rewards
            }
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@rewards_bp.route('/next-milestone', methods=['GET'])
# @jwt_required()  # 인증 비활성화
def get_next_milestone():
    """다음 마일스톤 정보"""
    try:
        user_id = DEFAULT_USER_ID  # 고정된 테스트 사용자 ID
        streak_count = DailyRecord.get_streak_count(user_id)
        
        # 다음 마일스톤 찾기
        milestones = [3, 7, 30]
        next_milestone = None
        
        for milestone in milestones:
            if streak_count < milestone:
                next_milestone = milestone
                break
        
        if next_milestone:
            days_remaining = next_milestone - streak_count
            return jsonify({
                'next_milestone': next_milestone,
                'days_remaining': days_remaining,
                'current_streak': streak_count,
                'progress_percentage': (streak_count / next_milestone) * 100
            }), 200
        else:
            return jsonify({
                'message': 'All milestones completed!',
                'current_streak': streak_count
            }), 200
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500
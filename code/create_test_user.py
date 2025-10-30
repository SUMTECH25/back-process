#!/usr/bin/env python3
"""
테스트 사용자 생성 스크립트 (인증 비활성화 모드용)
"""

from app import app, db
from models.user import User

def create_test_user():
    """기본 테스트 사용자 생성"""
    with app.app_context():
        # 기존 사용자 확인
        existing_user = User.query.filter_by(username='testuser').first()
        if existing_user:
            print(f"✅ Test user already exists: {existing_user.username} (ID: {existing_user.id})")
            return existing_user
        
        # 새 테스트 사용자 생성
        test_user = User(
            username='testuser',
            email='test@example.com',
            password='password123'  # User 모델에서 자동으로 해시됨
        )
        
        db.session.add(test_user)
        db.session.commit()
        
        print(f"✅ Test user created: {test_user.username} (ID: {test_user.id})")
        print("🔓 Authentication is disabled - all APIs can be used without login")
        return test_user

if __name__ == "__main__":
    create_test_user()
#!/usr/bin/env python3
"""
인증 비활성화 테스트 스크립트
로그인 없이 모든 API를 테스트합니다.
"""

import requests
import json
import os
from datetime import datetime, date

# API 설정
API_BASE_URL = "http://localhost:5000"
HEADERS = {'Content-Type': 'application/json'}

def test_no_auth_apis():
    """인증 없이 API 테스트"""
    print("🔓 인증 비활성화 모드 API 테스트")
    print("=" * 60)
    
    # 1. 헬스 체크 (원래부터 인증 불필요)
    print("\n1️⃣ Health Check")
    try:
        response = requests.get(f"{API_BASE_URL}/health")
        if response.status_code == 200:
            print("✅ Health check passed")
        else:
            print(f"❌ Health check failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Health check error: {e}")
    
    # 2. 일일 기록 생성 (인증 비활성화됨)
    print("\n2️⃣ Create Daily Record (No Auth)")
    record_data = {
        "stress_level": 7,
        "mood": "stressed",
        "energy_level": 4,
        "work_satisfaction": 6,
        "work_load": 9,
        "daily_sentence": "오늘은 정말 바빴다. 회의가 너무 많았고 스트레스를 많이 받았다.",
        "notes": "인증 비활성화 테스트"
    }
    
    try:
        response = requests.post(
            f"{API_BASE_URL}/api/records/",
            headers=HEADERS,
            data=json.dumps(record_data)
        )
        if response.status_code == 201:
            result = response.json()
            record_id = result['record']['id']
            print(f"✅ Daily record created (ID: {record_id})")
            print(f"   Stress level: {result['record']['stress_level']}")
            print(f"   Has text analysis: {result['analysis_info']['has_text_analysis']}")
        else:
            print(f"❌ Record creation failed: {response.status_code}")
            print(response.text)
    except Exception as e:
        print(f"❌ Record creation error: {e}")
    
    # 3. 기록 목록 조회 (인증 비활성화됨)
    print("\n3️⃣ Get Records List (No Auth)")
    try:
        response = requests.get(f"{API_BASE_URL}/api/records/")
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Records retrieved: {len(result['records'])} records")
            print(f"   Current streak: {result['stats']['current_streak']} days")
        else:
            print(f"❌ Records retrieval failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Records retrieval error: {e}")
    
    # 4. 오디오 분석 (인증 비활성화됨)
    print("\n4️⃣ Audio Analysis (No Auth)")
    audio_file_path = "../data/scratch/test.wav"
    
    if os.path.exists(audio_file_path):
        try:
            files = {'audio_file': open(audio_file_path, 'rb')}
            response = requests.post(
                f"{API_BASE_URL}/api/audio/analyze-direct",
                files=files
            )
            files['audio_file'].close()
            
            if response.status_code == 200:
                result = response.json()
                analysis = result['analysis_result']
                print(f"✅ Audio analysis completed")
                print(f"   Stress level: {analysis['stress_level']}/10")
                print(f"   Stressed probability: {analysis['stressed_probability']:.1f}%")
            else:
                print(f"❌ Audio analysis failed: {response.status_code}")
                print(response.text)
        except Exception as e:
            print(f"❌ Audio analysis error: {e}")
    else:
        print(f"⚠️  Audio file not found: {audio_file_path}")
    
    # 5. 리포트 생성 (인증 비활성화됨)
    print("\n5️⃣ Generate Report (No Auth)")
    try:
        response = requests.get(f"{API_BASE_URL}/api/reports/7-day")
        if response.status_code == 200:
            result = response.json()
            print("✅ 7-day report generated")
            if 'data' in result and 'report' in result['data']:
                report = result['data']['report']
                print(f"   Records analyzed: {len(report.get('daily_summaries', []))}")
        else:
            print(f"❌ Report generation failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Report generation error: {e}")
    
    # 6. 보상 시스템 (인증 비활성화됨)
    print("\n6️⃣ Rewards System (No Auth)")
    try:
        response = requests.get(f"{API_BASE_URL}/api/rewards/")
        if response.status_code == 200:
            result = response.json()
            print("✅ Rewards retrieved")
            if 'rewards' in result:
                print(f"   Available rewards: {len(result['rewards'])}")
        else:
            print(f"❌ Rewards retrieval failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Rewards retrieval error: {e}")
    
    # 7. 프로필 조회 (인증 비활성화됨)
    print("\n7️⃣ Get Profile (No Auth)")
    try:
        response = requests.get(f"{API_BASE_URL}/api/auth/profile")
        if response.status_code == 200:
            result = response.json()
            print("✅ Profile retrieved")
            if 'user' in result:
                user = result['user']
                print(f"   Username: {user.get('username')}")
                print(f"   Total records: {user.get('total_records', 0)}")
        else:
            print(f"❌ Profile retrieval failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Profile retrieval error: {e}")
    
    print("\n" + "=" * 60)
    print("🎉 인증 비활성화 테스트 완료!")
    print("📝 모든 API가 로그인 없이 사용 가능합니다.")

if __name__ == "__main__":
    test_no_auth_apis()
"""
오디오 스트레스 분석 예제 스크립트
사용자가 제공한 스크립트를 기반으로 API와 통합된 버전
"""

import os
import sys
import requests
import json
from datetime import datetime

# API 설정
API_BASE_URL = "http://localhost:5000"
HEADERS = {'Content-Type': 'application/json'}

def test_audio_analysis_with_api(audio_file_path, access_token):
    """API를 통한 오디오 스트레스 분석 테스트"""
    
    print(f"🎵 Testing audio analysis via API...")
    print(f"Audio file: {audio_file_path}")
    
    if not os.path.exists(audio_file_path):
        print(f"❌ Audio file not found: {audio_file_path}")
        return None
    
    # 오디오 파일 업로드 및 분석
    files = {'audio_file': open(audio_file_path, 'rb')}
    headers = {'Authorization': f'Bearer {access_token}'}
    
    # 일일 기록에 저장하지 않고 분석만 수행
    try:
        response = requests.post(
            f"{API_BASE_URL}/api/audio/analyze-direct",
            headers=headers,
            files=files
        )
        
        if response.status_code == 200:
            result = response.json()
            analysis = result['analysis_result']
            
            print("\n" + "="*60)
            print("📊 API 오디오 스트레스 분석 결과:")
            print("="*60)
            print(f"Original filename: {result['original_filename']}")
            print(f"Not stressed: {analysis['not_stressed_probability']:.1f}%")
            print(f"Stressed    : {analysis['stressed_probability']:.1f}%")
            print(f"Stress level: {analysis['stress_level']}/10")
            print(f"Is stressed : {'Yes' if analysis['is_stressed'] else 'No'}")
            print(f"Confidence  : {analysis['confidence']:.1f}%")
            print(f"Model used  : {analysis['model_used']}")
            print(f"Analyzed at : {analysis['analysis_timestamp']}")
            print("="*60)
            
            return analysis
        else:
            print(f"❌ API request failed: {response.status_code}")
            print(response.text)
            return None
            
    except Exception as e:
        print(f"❌ API error: {str(e)}")
        return None
    finally:
        files['audio_file'].close()

def test_audio_analysis_direct(audio_file_path):
    """직접 분석 (원본 코드 기반)"""
    print(f"🔬 Testing direct audio analysis...")
    
    try:
        # 순환 import를 피하기 위해 직접 임포트
        import sys
        import os
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'services'))
        
        # 오디오 분석 서비스만 직접 임포트
        from audio_stress_service import analyze_audio_stress
        
        result = analyze_audio_stress(audio_file_path)
        
        print("\n" + "="*60)
        print("📊 직접 오디오 스트레스 분석 결과:")
        print("="*60)
        print(f"Not stressed: {result['not_stressed_probability']:.1f}%")
        print(f"Stressed    : {result['stressed_probability']:.1f}%")
        print(f"Stress level: {result['stress_level']}/10")
        print(f"Is stressed : {'Yes' if result['is_stressed'] else 'No'}")
        print(f"Confidence  : {result['confidence']:.1f}%")
        print("="*60)
        
        return result
        
    except Exception as e:
        print(f"❌ Direct analysis error: {str(e)}")
        print("⚠️  Direct analysis is only available when running from server environment")
        return None

def create_daily_record_with_audio(audio_file_path, access_token):
    """오디오 파일과 함께 일일 기록 생성"""
    print(f"📝 Creating daily record with audio analysis...")
    
    if not os.path.exists(audio_file_path):
        print(f"❌ Audio file not found: {audio_file_path}")
        return None
    
    # multipart/form-data로 데이터와 파일 전송
    files = {'audio_file': open(audio_file_path, 'rb')}
    data = {
        'stress_level': 6,
        'mood': 'anxious',
        'energy_level': 4,
        'work_satisfaction': 7,
        'work_load': 8,
        'daily_sentence': 'API를 통한 오디오 분석 테스트 중입니다.',
        'notes': 'Audio analysis integration test',
        'save_to_record': 'true',
        'update_stress_level': 'true'  # 오디오 분석 결과로 스트레스 레벨 보정
    }
    
    headers = {'Authorization': f'Bearer {access_token}'}
    
    try:
        response = requests.post(
            f"{API_BASE_URL}/api/audio/analyze",
            headers=headers,
            files=files,
            data=data
        )
        
        if response.status_code == 200:
            result = response.json()
            analysis = result['analysis_result']
            
            print("✅ Daily record with audio analysis created successfully!")
            print(f"   Record ID: {result['record_id']}")
            print(f"   Audio stress level: {analysis['stress_level']}/10")
            print(f"   Stressed probability: {analysis['stressed_probability']:.1f}%")
            
            return result
        else:
            print(f"❌ Record creation failed: {response.status_code}")
            print(response.text)
            return None
            
    except Exception as e:
        print(f"❌ Record creation error: {str(e)}")
        return None
    finally:
        files['audio_file'].close()

def login_and_get_token():
    """API 로그인하여 토큰 획득"""
    print("🔐 Logging in to get access token...")
    
    login_data = {
        "username": "testuser",
        "password": "password123"
    }
    
    try:
        response = requests.post(
            f"{API_BASE_URL}/api/auth/login",
            headers=HEADERS,
            data=json.dumps(login_data)
        )
        
        if response.status_code == 200:
            data = response.json()
            access_token = data['access_token']
            print(f"✅ Login successful: {data['user']['username']}")
            return access_token
        else:
            print(f"❌ Login failed: {response.status_code}")
            return None
            
    except Exception as e:
        print(f"❌ Login error: {str(e)}")
        return None

def check_server_status():
    """서버 상태 확인"""
    print("🔍 Checking server status...")
    try:
        response = requests.get(f"{API_BASE_URL}/health")
        if response.status_code == 200:
            print("✅ Server is running")
            return True
        else:
            print(f"❌ Server health check failed: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to server. Is it running?")
        return False

def main():
    """메인 실행 함수"""
    print("🎵 3-7-30 보상 시스템 오디오 스트레스 분석 테스트")
    print("=" * 60)
    
    # 오디오 파일 경로 설정
    audio_file_path = "../data/scratch/test.wav"
    
    # 서버 상태 확인
    if not check_server_status():
        print("서버를 먼저 실행해주세요: python run.py")
        return
    
    # API 로그인
    access_token = login_and_get_token()
    if not access_token:
        print("로그인에 실패했습니다.")
        return
    
    print(f"\n📁 오디오 파일 경로: {audio_file_path}")
    
    # 파일 존재 확인
    if not os.path.exists(audio_file_path):
        print(f"⚠️  오디오 파일을 찾을 수 없습니다: {audio_file_path}")
        print("실제 오디오 파일 경로로 변경하거나 샘플 파일을 준비해주세요.")
        
        # 지원되는 형식 확인
        try:
            response = requests.get(f"{API_BASE_URL}/api/audio/formats")
            if response.status_code == 200:
                formats = response.json()
                print(f"지원되는 형식: {', '.join(formats['supported_formats'])}")
                print(f"최대 파일 크기: {formats['max_file_size_mb']}MB")
        except:
            pass
        
        return
    
    # 분석 정책 확인
    print("\n🔍 분석 정책 확인...")
    try:
        response = requests.get(f"{API_BASE_URL}/api/audio/policy")
        if response.status_code == 200:
            policy = response.json()
            print(f"✅ 분석 우선순위: {policy['analysis_priority']['primary']}")
            print(f"   {policy['policy_description']['ko']}")
        else:
            print("⚠️  정책 정보를 가져올 수 없습니다.")
    except:
        pass
    
    print("\n" + "="*60)
    print("테스트 시나리오 (🎵 오디오 우선 정책):")
    print("1. API를 통한 오디오 분석 (파일 저장 안함)")
    print("2. 오디오와 함께 일일 기록 생성 (오디오가 스트레스 레벨 결정)")
    print("3. 직접 분석 (개발용)")
    print("4. 텍스트 NLP는 참고용으로만 사용")
    print("="*60)
    
    # 1. API를 통한 오디오 분석
    print("\n🧪 Test 1: API Audio Analysis")
    api_result = test_audio_analysis_with_api(audio_file_path, access_token)
    
    # 2. 일일 기록과 함께 오디오 분석
    print("\n🧪 Test 2: Daily Record with Audio")
    record_result = create_daily_record_with_audio(audio_file_path, access_token)
    
    # 3. 직접 분석 (서버 환경에서만 가능)
    print("\n🧪 Test 3: Direct Analysis")
    try:
        sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
        direct_result = test_audio_analysis_direct(audio_file_path)
    except Exception as e:
        print(f"⚠️  Direct analysis not available: {str(e)}")
        direct_result = None
    
    # 결과 비교
    print("\n" + "="*60)
    print("📊 결과 요약")
    print("="*60)
    
    if api_result:
        print(f"API Analysis      : {api_result['stress_level']}/10 ({api_result['stressed_probability']:.1f}% stressed)")
    
    if record_result:
        analysis = record_result['analysis_result']
        print(f"Record Analysis   : {analysis['stress_level']}/10 ({analysis['stressed_probability']:.1f}% stressed)")
        print(f"Record ID         : {record_result['record_id']}")
    
    if direct_result:
        print(f"Direct Analysis   : {direct_result['stress_level']}/10 ({direct_result['stressed_probability']:.1f}% stressed)")
    
    print("\n✨ 오디오 스트레스 분석 테스트 완료!")

if __name__ == "__main__":
    main()
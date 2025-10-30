"""
API 테스트 스크립트
Flask 애플리케이션의 주요 엔드포인트를 테스트합니다.
"""

import requests
import json
import time
from datetime import datetime, date, timedelta

# 서버 설정
BASE_URL = "http://localhost:5000"
HEADERS = {'Content-Type': 'application/json'}

class APITester:
    def __init__(self, base_url=BASE_URL):
        self.base_url = base_url
        self.access_token = None
        self.user_id = None
        
    def test_health_check(self):
        """헬스 체크 테스트"""
        print("🔍 Testing health check...")
        try:
            response = requests.get(f"{self.base_url}/health")
            if response.status_code == 200:
                print("✅ Health check passed")
                return True
            else:
                print(f"❌ Health check failed: {response.status_code}")
                return False
        except requests.exceptions.ConnectionError:
            print("❌ Cannot connect to server. Is it running?")
            return False
    
    def test_user_registration(self):
        """사용자 등록 테스트"""
        print("👤 Testing user registration...")
        
        # 테스트용 사용자 데이터
        user_data = {
            "username": f"testuser_{int(time.time())}",
            "email": f"test_{int(time.time())}@example.com",
            "password": "password123",
            "name": "테스트 사용자",
            "occupation": "개발자",
            "stress_level": 5
        }
        
        try:
            response = requests.post(
                f"{self.base_url}/api/auth/register",
                headers=HEADERS,
                data=json.dumps(user_data)
            )
            
            if response.status_code == 201:
                data = response.json()
                self.access_token = data['access_token']
                self.user_id = data['user']['id']
                print(f"✅ User registered successfully: {data['user']['username']}")
                return True
            else:
                print(f"❌ Registration failed: {response.status_code}")
                print(response.text)
                return False
                
        except Exception as e:
            print(f"❌ Registration error: {str(e)}")
            return False
    
    def test_user_login(self):
        """사용자 로그인 테스트 (기존 testuser 사용)"""
        print("🔐 Testing user login...")
        
        login_data = {
            "username": "testuser",
            "password": "password123"
        }
        
        try:
            response = requests.post(
                f"{self.base_url}/api/auth/login",
                headers=HEADERS,
                data=json.dumps(login_data)
            )
            
            if response.status_code == 200:
                data = response.json()
                self.access_token = data['access_token']
                self.user_id = data['user']['id']
                print(f"✅ Login successful: {data['user']['username']}")
                return True
            else:
                print(f"❌ Login failed: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Login error: {str(e)}")
            return False
    
    def test_daily_record_creation(self):
        """일일 기록 생성 테스트"""
        print("📝 Testing daily record creation...")
        
        if not self.access_token:
            print("❌ No access token available")
            return False
        
        auth_headers = {
            **HEADERS,
            'Authorization': f'Bearer {self.access_token}'
        }
        
        record_data = {
            "stress_level": 6,
            "mood": "stressed",
            "energy_level": 4,
            "work_satisfaction": 7,
            "work_load": 8,
            "daily_sentence": "API 테스트를 위한 샘플 기록입니다.",
            "notes": "자동 테스트로 생성된 기록"
        }
        
        try:
            response = requests.post(
                f"{self.base_url}/api/records/",
                headers=auth_headers,
                data=json.dumps(record_data)
            )
            
            if response.status_code == 201:
                data = response.json()
                print(f"✅ Daily record created successfully")
                print(f"   Streak count: {data['streak_count']}")
                return True
            else:
                print(f"❌ Record creation failed: {response.status_code}")
                print(response.text)
                return False
                
        except Exception as e:
            print(f"❌ Record creation error: {str(e)}")
            return False
    
    def test_records_list(self):
        """기록 목록 조회 테스트"""
        print("📋 Testing records list...")
        
        if not self.access_token:
            print("❌ No access token available")
            return False
        
        auth_headers = {
            **HEADERS,
            'Authorization': f'Bearer {self.access_token}'
        }
        
        try:
            response = requests.get(
                f"{self.base_url}/api/records/",
                headers=auth_headers
            )
            
            if response.status_code == 200:
                data = response.json()
                records_count = len(data['records'])
                print(f"✅ Records retrieved successfully: {records_count} records")
                print(f"   Current streak: {data['stats']['current_streak']}")
                return True
            else:
                print(f"❌ Records retrieval failed: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Records retrieval error: {str(e)}")
            return False
    
    def test_milestone_check(self):
        """마일스톤 확인 테스트"""
        print("🏆 Testing milestone check...")
        
        if not self.access_token:
            print("❌ No access token available")
            return False
        
        auth_headers = {
            **HEADERS,
            'Authorization': f'Bearer {self.access_token}'
        }
        
        try:
            response = requests.post(
                f"{self.base_url}/api/rewards/check",
                headers=auth_headers
            )
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Milestone check successful")
                print(f"   Current streak: {data['current_streak']}")
                print(f"   New milestones: {len(data['new_milestones'])}")
                return True
            else:
                print(f"❌ Milestone check failed: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Milestone check error: {str(e)}")
            return False
    
    def test_rewards_progress(self):
        """보상 진행 상황 테스트"""
        print("📊 Testing rewards progress...")
        
        if not self.access_token:
            print("❌ No access token available")
            return False
        
        auth_headers = {
            **HEADERS,
            'Authorization': f'Bearer {self.access_token}'
        }
        
        try:
            response = requests.get(
                f"{self.base_url}/api/rewards/progress",
                headers=auth_headers
            )
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Rewards progress retrieved successfully")
                print(f"   Current streak: {data['current_streak']}")
                print(f"   Total milestones achieved: {data['stats']['total_milestones_achieved']}")
                return True
            else:
                print(f"❌ Rewards progress failed: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Rewards progress error: {str(e)}")
            return False
    
    def test_summary_report(self):
        """요약 리포트 테스트"""
        print("📈 Testing summary report...")
        
        if not self.access_token:
            print("❌ No access token available")
            return False
        
        auth_headers = {
            **HEADERS,
            'Authorization': f'Bearer {self.access_token}'
        }
        
        try:
            response = requests.get(
                f"{self.base_url}/api/reports/summary?days=7",
                headers=auth_headers
            )
            
            if response.status_code == 200:
                data = response.json()
                if 'summary' in data:
                    summary = data['summary']
                    print(f"✅ Summary report generated successfully")
                    print(f"   Total records: {summary['total_records']}")
                    print(f"   Average stress: {summary['average_stress_level']}")
                    print(f"   Average energy: {summary['average_energy_level']}")
                else:
                    print(f"✅ Summary report response (no data for period)")
                return True
            else:
                print(f"❌ Summary report failed: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Summary report error: {str(e)}")
            return False
    
    def test_audio_formats(self):
        """오디오 형식 지원 테스트"""
        print("🎵 Testing audio formats...")
        
        try:
            response = requests.get(f"{self.base_url}/api/audio/formats")
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Audio formats retrieved successfully")
                print(f"   Supported formats: {', '.join(data['supported_formats'])}")
                print(f"   Max file size: {data['max_file_size_mb']}MB")
                return True
            else:
                print(f"❌ Audio formats failed: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Audio formats error: {str(e)}")
            return False
    
    def test_audio_stats(self):
        """오디오 분석 통계 테스트"""
        print("📊 Testing audio analysis stats...")
        
        if not self.access_token:
            print("❌ No access token available")
            return False
        
        auth_headers = {
            **HEADERS,
            'Authorization': f'Bearer {self.access_token}'
        }
        
        try:
            response = requests.get(
                f"{self.base_url}/api/audio/stats",
                headers=auth_headers
            )
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Audio stats retrieved successfully")
                if 'total_audio_records' in data:
                    print(f"   Total audio records: {data['total_audio_records']}")
                    if data['total_audio_records'] > 0:
                        print(f"   Recent 30 days: {data['recent_30_days']}")
                        print(f"   Average confidence: {data['average_confidence']}%")
                else:
                    print(f"   No audio records found")
                return True
            else:
                print(f"❌ Audio stats failed: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Audio stats error: {str(e)}")
            return False
    
    def run_all_tests(self):
        """모든 테스트 실행"""
        print("🚀 Starting API Tests")
        print("=" * 50)
        
        results = []
        
        # 헬스 체크
        results.append(('Health Check', self.test_health_check()))
        
        # 사용자 로그인 (기존 testuser 사용)
        results.append(('User Login', self.test_user_login()))
        
        # 일일 기록 생성
        results.append(('Daily Record Creation', self.test_daily_record_creation()))
        
        # 기록 목록 조회
        results.append(('Records List', self.test_records_list()))
        
        # 마일스톤 확인
        results.append(('Milestone Check', self.test_milestone_check()))
        
        # 보상 진행 상황
        results.append(('Rewards Progress', self.test_rewards_progress()))
        
        # 요약 리포트
        results.append(('Summary Report', self.test_summary_report()))
        
        # 오디오 관련 테스트
        results.append(('Audio Formats', self.test_audio_formats()))
        results.append(('Audio Stats', self.test_audio_stats()))
        
        # 결과 출력
        print("\n" + "=" * 50)
        print("📋 Test Results")
        print("=" * 50)
        
        passed = 0
        failed = 0
        
        for test_name, result in results:
            status = "✅ PASS" if result else "❌ FAIL"
            print(f"{test_name:25} {status}")
            if result:
                passed += 1
            else:
                failed += 1
        
        print("=" * 50)
        print(f"Total: {len(results)}, Passed: {passed}, Failed: {failed}")
        
        if failed == 0:
            print("🎉 All tests passed!")
        else:
            print(f"⚠️  {failed} test(s) failed")
        
        return failed == 0

def main():
    """메인 실행 함수"""
    print("🧪 3-7-30 보상 시스템 API 테스트")
    print("=" * 50)
    
    tester = APITester()
    success = tester.run_all_tests()
    
    if success:
        print("\n✨ API 테스트가 성공적으로 완료되었습니다!")
    else:
        print("\n💥 일부 테스트가 실패했습니다. 로그를 확인해주세요.")
    
    return success

if __name__ == '__main__':
    main()
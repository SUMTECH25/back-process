#!/usr/bin/env python3
"""
프론트엔드 개발용 음성 파일 API 테스트 스크립트
실제 프론트엔드에서 사용할 API 호출 방법을 시뮬레이션합니다.
"""

import requests
import json
import os
from datetime import datetime
import base64

# API 설정
API_BASE_URL = "http://localhost:5000"

class VoiceAPIClient:
    """음성 API 클라이언트 (프론트엔드 시뮬레이션)"""
    
    def __init__(self, base_url=API_BASE_URL):
        self.base_url = base_url
        
    def upload_voice_for_analysis(self, audio_file_path, save_to_record=False, record_data=None):
        """
        음성 파일 업로드 및 분석
        
        Args:
            audio_file_path: 음성 파일 경로
            save_to_record: 일일 기록으로 저장할지 여부
            record_data: 기록 데이터 (save_to_record=True일 때 필요)
        
        Returns:
            분석 결과
        """
        
        if not os.path.exists(audio_file_path):
            return {"error": f"Audio file not found: {audio_file_path}"}
        
        try:
            # 파일 읽기
            with open(audio_file_path, 'rb') as audio_file:
                files = {'audio_file': audio_file}
                
                if save_to_record and record_data:
                    # 일일 기록과 함께 저장
                    response = requests.post(
                        f"{self.base_url}/api/audio/analyze",
                        files=files,
                        data=record_data
                    )
                    endpoint = "/api/audio/analyze"
                else:
                    # 분석만 수행 (저장 안함)
                    response = requests.post(
                        f"{self.base_url}/api/audio/analyze-direct",
                        files=files
                    )
                    endpoint = "/api/audio/analyze-direct"
                
                print(f"🎵 API 호출: {endpoint}")
                print(f"📁 파일: {os.path.basename(audio_file_path)}")
                
                if response.status_code == 200:
                    result = response.json()
                    print("✅ 업로드 및 분석 성공!")
                    return result
                else:
                    error_msg = f"API 오류: {response.status_code}"
                    try:
                        error_detail = response.json()
                        error_msg += f" - {error_detail}"
                    except:
                        error_msg += f" - {response.text}"
                    print(f"❌ {error_msg}")
                    return {"error": error_msg}
                    
        except Exception as e:
            error_msg = f"업로드 오류: {str(e)}"
            print(f"❌ {error_msg}")
            return {"error": error_msg}
    
    def upload_voice_as_base64(self, audio_file_path):
        """
        Base64로 인코딩된 음성 데이터 전송 (웹 브라우저에서 녹음한 경우)
        실제로는 multipart/form-data를 사용하지만, 참고용으로 구현
        """
        if not os.path.exists(audio_file_path):
            return {"error": f"Audio file not found: {audio_file_path}"}
        
        try:
            # 파일을 Base64로 인코딩
            with open(audio_file_path, 'rb') as audio_file:
                encoded_audio = base64.b64encode(audio_file.read()).decode('utf-8')
            
            # JSON으로 전송 (예제용 - 실제로는 multipart를 권장)
            data = {
                "audio_data": encoded_audio,
                "filename": os.path.basename(audio_file_path),
                "format": "base64"
            }
            
            print("⚠️  주의: 이 방법은 예제용입니다. multipart/form-data 사용을 권장합니다.")
            return {"message": "Base64 인코딩 완료", "size": len(encoded_audio)}
            
        except Exception as e:
            return {"error": f"Base64 인코딩 오류: {str(e)}"}
    
    def get_supported_formats(self):
        """지원되는 오디오 형식 조회"""
        try:
            response = requests.get(f"{self.base_url}/api/audio/formats")
            if response.status_code == 200:
                return response.json()
            else:
                return {"error": f"API 오류: {response.status_code}"}
        except Exception as e:
            return {"error": f"오류: {str(e)}"}
    
    def get_analysis_policy(self):
        """분석 정책 정보 조회"""
        try:
            response = requests.get(f"{self.base_url}/api/audio/policy")
            if response.status_code == 200:
                return response.json()
            else:
                return {"error": f"API 오류: {response.status_code}"}
        except Exception as e:
            return {"error": f"오류: {str(e)}"}
    
    def create_record_with_voice(self, audio_file_path, record_data):
        """음성과 함게 일일 기록 생성"""
        return self.upload_voice_for_analysis(
            audio_file_path, 
            save_to_record=True, 
            record_data=record_data
        )

def demo_frontend_simulation():
    """프론트엔드 시뮬레이션 데모"""
    
    print("🎤 프론트엔드 음성 API 시뮬레이션")
    print("=" * 60)
    
    client = VoiceAPIClient()
    
    # 테스트 오디오 파일
    test_audio = "../data/scratch/test.wav"
    
    if not os.path.exists(test_audio):
        print(f"⚠️  테스트 오디오 파일이 없습니다: {test_audio}")
        print("실제 오디오 파일 경로를 사용해주세요.")
        return
    
    # 1. 지원 형식 확인
    print("\n1️⃣ 지원되는 오디오 형식 확인")
    formats = client.get_supported_formats()
    if 'supported_formats' in formats:
        print(f"✅ 지원 형식: {', '.join(formats['supported_formats'])}")
        print(f"📏 최대 크기: {formats.get('max_file_size_mb', 'N/A')}MB")
    
    # 2. 분석 정책 확인
    print("\n2️⃣ 분석 정책 확인")
    policy = client.get_analysis_policy()
    if 'policy_description' in policy:
        print(f"✅ 정책: {policy['policy_description'].get('ko', 'N/A')}")
    
    # 3. 음성 분석만 수행 (저장 안함)
    print("\n3️⃣ 음성 분석만 수행 (저장 안함)")
    analysis_result = client.upload_voice_for_analysis(test_audio, save_to_record=False)
    
    if 'analysis_result' in analysis_result:
        analysis = analysis_result['analysis_result']
        print(f"📊 스트레스 레벨: {analysis.get('stress_level', 'N/A')}/10")
        print(f"📈 스트레스 확률: {analysis.get('stressed_probability', 'N/A')}%")
        print(f"🎯 신뢰도: {analysis.get('confidence', 'N/A')}%")
        print(f"🔬 모델: {analysis.get('model_used', 'N/A')}")
    
    # 4. 음성과 함께 일일 기록 생성
    print("\n4️⃣ 음성과 함께 일일 기록 생성")
    record_data = {
        'stress_level': 6,  # 초기값 (음성 분석으로 보정됨)
        'mood': 'anxious',
        'energy_level': 4,
        'work_satisfaction': 7,
        'work_load': 8,
        'daily_sentence': '프론트엔드 테스트 중입니다.',
        'notes': 'Voice API 테스트',
        'save_to_record': 'true',
        'update_stress_level': 'true'
    }
    
    record_result = client.create_record_with_voice(test_audio, record_data)
    
    if 'record' in record_result:
        record = record_result['record']
        print(f"✅ 기록 생성 성공! ID: {record.get('id')}")
        print(f"📊 최종 스트레스 레벨: {record.get('stress_level')}/10")
        
        if 'analysis_info' in record_result:
            info = record_result['analysis_info']
            print(f"🎵 음성 분석: {info.get('has_audio_analysis')}")
            print(f"📝 텍스트 분석: {info.get('has_text_analysis')}")
            print(f"🎯 스트레스 레벨 출처: {info.get('stress_level_source')}")
    
    # 5. Base64 인코딩 예제 (참고용)
    print("\n5️⃣ Base64 인코딩 예제 (참고용)")
    base64_result = client.upload_voice_as_base64(test_audio)
    if 'size' in base64_result:
        print(f"📦 Base64 크기: {base64_result['size']} 문자")
        print("⚠️  실제로는 multipart/form-data 사용을 권장합니다.")
    
    print("\n" + "=" * 60)
    print("🎉 프론트엔드 시뮬레이션 완료!")

def generate_javascript_example():
    """JavaScript/프론트엔드 예제 코드 생성"""
    
    js_code = '''
// 프론트엔드 JavaScript 예제 코드

class VoiceAPI {
    constructor(baseURL = 'http://localhost:5000') {
        this.baseURL = baseURL;
    }
    
    // 1. 파일 업로드로 음성 분석
    async analyzeVoiceFile(audioFile, saveToRecord = false, recordData = null) {
        const formData = new FormData();
        formData.append('audio_file', audioFile);
        
        // 일일 기록 데이터가 있으면 추가
        if (saveToRecord && recordData) {
            Object.keys(recordData).forEach(key => {
                formData.append(key, recordData[key]);
            });
        }
        
        const endpoint = saveToRecord ? '/api/audio/analyze' : '/api/audio/analyze-direct';
        
        try {
            const response = await fetch(`${this.baseURL}${endpoint}`, {
                method: 'POST',
                body: formData
            });
            
            if (response.ok) {
                return await response.json();
            } else {
                throw new Error(`API 오류: ${response.status}`);
            }
        } catch (error) {
            console.error('음성 분석 오류:', error);
            throw error;
        }
    }
    
    // 2. 웹 브라우저에서 녹음한 음성 분석
    async analyzeRecordedVoice(audioBlob, saveToRecord = false, recordData = null) {
        // Blob을 File 객체로 변환
        const audioFile = new File([audioBlob], 'recorded_voice.wav', {
            type: 'audio/wav'
        });
        
        return this.analyzeVoiceFile(audioFile, saveToRecord, recordData);
    }
    
    // 3. 지원되는 오디오 형식 확인
    async getSupportedFormats() {
        try {
            const response = await fetch(`${this.baseURL}/api/audio/formats`);
            return await response.json();
        } catch (error) {
            console.error('형식 조회 오류:', error);
            throw error;
        }
    }
}

// 사용 예제
const voiceAPI = new VoiceAPI();

// 파일 입력으로 음성 업로드
document.getElementById('audioFileInput').addEventListener('change', async (event) => {
    const file = event.target.files[0];
    if (file) {
        try {
            // 분석만 수행
            const result = await voiceAPI.analyzeVoiceFile(file, false);
            console.log('음성 분석 결과:', result);
            
            // UI 업데이트
            if (result.analysis_result) {
                const analysis = result.analysis_result;
                document.getElementById('stressLevel').textContent = analysis.stress_level;
                document.getElementById('stressProbability').textContent = 
                    `${analysis.stressed_probability}%`;
            }
        } catch (error) {
            alert('음성 분석 중 오류가 발생했습니다: ' + error.message);
        }
    }
});

// 녹음 버튼으로 음성 녹음 및 분석
let mediaRecorder;
let recordedChunks = [];

document.getElementById('recordButton').addEventListener('click', async () => {
    if (!mediaRecorder || mediaRecorder.state === 'inactive') {
        // 녹음 시작
        try {
            const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
            mediaRecorder = new MediaRecorder(stream);
            
            mediaRecorder.ondataavailable = (event) => {
                if (event.data.size > 0) {
                    recordedChunks.push(event.data);
                }
            };
            
            mediaRecorder.onstop = async () => {
                const audioBlob = new Blob(recordedChunks, { type: 'audio/wav' });
                recordedChunks = [];
                
                try {
                    // 녹음된 음성 분석
                    const result = await voiceAPI.analyzeRecordedVoice(audioBlob, false);
                    console.log('녹음된 음성 분석 결과:', result);
                } catch (error) {
                    alert('음성 분석 중 오류가 발생했습니다: ' + error.message);
                }
            };
            
            mediaRecorder.start();
            document.getElementById('recordButton').textContent = '녹음 중지';
        } catch (error) {
            alert('마이크 접근 권한이 필요합니다: ' + error.message);
        }
    } else {
        // 녹음 중지
        mediaRecorder.stop();
        document.getElementById('recordButton').textContent = '녹음 시작';
    }
});

// 일일 기록과 함께 음성 저장
async function saveRecordWithVoice(audioFile) {
    const recordData = {
        stress_level: 5,  // 초기값
        mood: 'normal',
        energy_level: 5,
        daily_sentence: '오늘의 한마디...',
        notes: '음성과 함께 저장된 기록',
        save_to_record: 'true',
        update_stress_level: 'true'  // 음성 분석으로 스트레스 레벨 보정
    };
    
    try {
        const result = await voiceAPI.analyzeVoiceFile(audioFile, true, recordData);
        console.log('기록 저장 결과:', result);
        
        if (result.record) {
            alert(`기록이 저장되었습니다! (ID: ${result.record.id})`);
        }
    } catch (error) {
        alert('기록 저장 중 오류가 발생했습니다: ' + error.message);
    }
}
'''
    
    # JavaScript 코드를 파일로 저장
    js_file_path = "/home/probius/nvidia-workbench/back-process/code/frontend_voice_api_example.js"
    with open(js_file_path, 'w', encoding='utf-8') as f:
        f.write(js_code)
    
    print(f"📁 JavaScript 예제 코드가 생성되었습니다: {js_file_path}")

def generate_html_example():
    """HTML 예제 페이지 생성"""
    
    html_code = '''<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>음성 스트레스 분석 API 테스트</title>
    <style>
        body { font-family: Arial, sans-serif; max-width: 800px; margin: 0 auto; padding: 20px; }
        .container { background: #f5f5f5; padding: 20px; border-radius: 10px; margin: 10px 0; }
        .result { background: #e8f5e8; padding: 15px; border-radius: 5px; margin: 10px 0; }
        .error { background: #f5e8e8; padding: 15px; border-radius: 5px; margin: 10px 0; }
        button { padding: 10px 20px; margin: 5px; cursor: pointer; }
        input[type="file"] { margin: 10px 0; }
        .stats { display: flex; justify-content: space-around; }
        .stat { text-align: center; padding: 10px; background: white; border-radius: 5px; }
    </style>
</head>
<body>
    <h1>🎤 음성 스트레스 분석 API 테스트</h1>
    
    <div class="container">
        <h2>1. 음성 파일 업로드 분석</h2>
        <input type="file" id="audioFileInput" accept="audio/*">
        <button onclick="analyzeUploadedFile()">분석하기</button>
        <div id="uploadResult"></div>
    </div>
    
    <div class="container">
        <h2>2. 음성 녹음 및 분석</h2>
        <button id="recordButton" onclick="toggleRecording()">녹음 시작</button>
        <div id="recordingStatus"></div>
        <div id="recordResult"></div>
    </div>
    
    <div class="container">
        <h2>3. 분석 결과</h2>
        <div class="stats">
            <div class="stat">
                <h3>스트레스 레벨</h3>
                <div id="stressLevel">-</div>
            </div>
            <div class="stat">
                <h3>스트레스 확률</h3>
                <div id="stressProbability">-</div>
            </div>
            <div class="stat">
                <h3>신뢰도</h3>
                <div id="confidence">-</div>
            </div>
        </div>
    </div>
    
    <div class="container">
        <h2>4. 일일 기록으로 저장</h2>
        <button onclick="saveAsRecord()" id="saveRecordBtn" disabled>기록으로 저장</button>
        <div id="saveResult"></div>
    </div>

    <script src="frontend_voice_api_example.js"></script>
    <script>
        let lastAnalyzedFile = null;
        let lastAnalyzedBlob = null;
        let mediaRecorder = null;
        let recordedChunks = [];
        
        // 업로드된 파일 분석
        async function analyzeUploadedFile() {
            const fileInput = document.getElementById('audioFileInput');
            const file = fileInput.files[0];
            
            if (!file) {
                alert('음성 파일을 선택해주세요.');
                return;
            }
            
            try {
                showLoading('uploadResult', '분석 중...');
                const voiceAPI = new VoiceAPI();
                const result = await voiceAPI.analyzeVoiceFile(file, false);
                
                lastAnalyzedFile = file;
                displayResult(result, 'uploadResult');
                document.getElementById('saveRecordBtn').disabled = false;
                
            } catch (error) {
                showError('uploadResult', '분석 중 오류가 발생했습니다: ' + error.message);
            }
        }
        
        // 녹음 토글
        async function toggleRecording() {
            const button = document.getElementById('recordButton');
            const status = document.getElementById('recordingStatus');
            
            if (!mediaRecorder || mediaRecorder.state === 'inactive') {
                try {
                    const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
                    mediaRecorder = new MediaRecorder(stream);
                    recordedChunks = [];
                    
                    mediaRecorder.ondataavailable = (event) => {
                        if (event.data.size > 0) {
                            recordedChunks.push(event.data);
                        }
                    };
                    
                    mediaRecorder.onstop = async () => {
                        const audioBlob = new Blob(recordedChunks, { type: 'audio/wav' });
                        await analyzeRecordedVoice(audioBlob);
                    };
                    
                    mediaRecorder.start();
                    button.textContent = '녹음 중지';
                    status.innerHTML = '<div class="result">🔴 녹음 중...</div>';
                    
                } catch (error) {
                    showError('recordingStatus', '마이크 접근 권한이 필요합니다: ' + error.message);
                }
            } else {
                mediaRecorder.stop();
                button.textContent = '녹음 시작';
                status.innerHTML = '';
            }
        }
        
        // 녹음된 음성 분석
        async function analyzeRecordedVoice(audioBlob) {
            try {
                showLoading('recordResult', '녹음된 음성 분석 중...');
                const voiceAPI = new VoiceAPI();
                const result = await voiceAPI.analyzeRecordedVoice(audioBlob, false);
                
                lastAnalyzedBlob = audioBlob;
                displayResult(result, 'recordResult');
                document.getElementById('saveRecordBtn').disabled = false;
                
            } catch (error) {
                showError('recordResult', '분석 중 오류가 발생했습니다: ' + error.message);
            }
        }
        
        // 기록으로 저장
        async function saveAsRecord() {
            const recordData = {
                stress_level: 5,
                mood: 'normal',
                energy_level: 5,
                daily_sentence: '음성 API 테스트 기록입니다.',
                notes: 'HTML 테스트 페이지에서 생성',
                save_to_record: 'true',
                update_stress_level: 'true'
            };
            
            try {
                showLoading('saveResult', '기록 저장 중...');
                const voiceAPI = new VoiceAPI();
                let result;
                
                if (lastAnalyzedFile) {
                    result = await voiceAPI.analyzeVoiceFile(lastAnalyzedFile, true, recordData);
                } else if (lastAnalyzedBlob) {
                    result = await voiceAPI.analyzeRecordedVoice(lastAnalyzedBlob, true, recordData);
                } else {
                    throw new Error('저장할 음성 데이터가 없습니다.');
                }
                
                if (result.record) {
                    document.getElementById('saveResult').innerHTML = 
                        `<div class="result">✅ 기록이 저장되었습니다! (ID: ${result.record.id})</div>`;
                }
                
            } catch (error) {
                showError('saveResult', '저장 중 오류가 발생했습니다: ' + error.message);
            }
        }
        
        // 결과 표시
        function displayResult(result, containerId) {
            if (result.analysis_result) {
                const analysis = result.analysis_result;
                
                document.getElementById('stressLevel').textContent = analysis.stress_level + '/10';
                document.getElementById('stressProbability').textContent = analysis.stressed_probability + '%';
                document.getElementById('confidence').textContent = analysis.confidence + '%';
                
                document.getElementById(containerId).innerHTML = `
                    <div class="result">
                        <h4>✅ 분석 완료</h4>
                        <p><strong>스트레스 레벨:</strong> ${analysis.stress_level}/10</p>
                        <p><strong>스트레스 확률:</strong> ${analysis.stressed_probability}%</p>
                        <p><strong>비스트레스 확률:</strong> ${analysis.not_stressed_probability}%</p>
                        <p><strong>신뢰도:</strong> ${analysis.confidence}%</p>
                        <p><strong>모델:</strong> ${analysis.model_used}</p>
                        <p><strong>분석 시간:</strong> ${new Date(analysis.analysis_timestamp).toLocaleString()}</p>
                    </div>
                `;
            } else {
                showError(containerId, '분석 결과를 받을 수 없습니다.');
            }
        }
        
        function showLoading(containerId, message) {
            document.getElementById(containerId).innerHTML = `<div class="result">${message}</div>`;
        }
        
        function showError(containerId, message) {
            document.getElementById(containerId).innerHTML = `<div class="error">${message}</div>`;
        }
    </script>
</body>
</html>'''
    
    # HTML 파일 저장
    html_file_path = "/home/probius/nvidia-workbench/back-process/code/voice_api_test.html"
    with open(html_file_path, 'w', encoding='utf-8') as f:
        f.write(html_code)
    
    print(f"📁 HTML 테스트 페이지가 생성되었습니다: {html_file_path}")
    print(f"🌐 브라우저에서 file://{html_file_path} 로 접속하여 테스트하세요.")

if __name__ == "__main__":
    print("🎤 프론트엔드 음성 API 도구")
    print("=" * 60)
    
    # 1. 프론트엔드 시뮬레이션 실행
    demo_frontend_simulation()
    
    # 2. JavaScript 예제 코드 생성
    print("\n📝 JavaScript 예제 코드 생성...")
    generate_javascript_example()
    
    # 3. HTML 테스트 페이지 생성
    print("\n🌐 HTML 테스트 페이지 생성...")
    generate_html_example()
    
    print("\n" + "=" * 60)
    print("🎉 프론트엔드 개발 도구 준비 완료!")
    print("\n📋 다음 단계:")
    print("1. 서버 실행: python3 run.py")
    print("2. 브라우저에서 voice_api_test.html 열기")
    print("3. JavaScript 코드를 프론트엔드 프로젝트에 복사")
    print("4. API 엔드포인트를 실제 서버 주소로 변경")
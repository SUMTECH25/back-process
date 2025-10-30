
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

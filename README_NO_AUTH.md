# 인증 비활성화 브랜치 (disable-auth)

이 브랜치에서는 JWT 인증이 비활성화되어 있어 모든 API를 로그인 없이 사용할 수 있습니다.

## 🔓 변경 사항

### 인증 시스템 비활성화
- 모든 `@jwt_required()` 데코레이터가 주석 처리됨
- `get_jwt_identity()` 호출이 고정된 테스트 사용자 ID (1)로 교체됨
- 로그인 없이 모든 API 엔드포인트 사용 가능

### 수정된 파일들
- `routes/audio.py` - 오디오 분석 API
- `routes/records.py` - 일일 기록 API  
- `routes/reports.py` - 리포트 생성 API
- `routes/rewards.py` - 보상 시스템 API
- `routes/auth.py` - 프로필 API (로그인/등록은 유지)

## 🚀 사용 방법

### 1. 서버 실행
```bash
cd code
python3 run.py
```

### 2. 테스트 사용자 생성 (최초 1회)
```bash
python3 create_test_user.py
```

### 3. 인증 없이 API 테스트
```bash
python3 test_no_auth.py
```

### 4. 오디오 분석 테스트 (인증 없음)
```bash
python3 test_audio_analysis.py
```

## 📡 API 사용 예제

### 일일 기록 생성 (로그인 불필요)
```bash
curl -X POST http://localhost:5000/api/records/ \
  -H "Content-Type: application/json" \
  -d '{
    "stress_level": 7,
    "mood": "stressed", 
    "energy_level": 4,
    "daily_sentence": "오늘은 정말 바빴다."
  }'
```

### 오디오 분석 (로그인 불필요)
```bash
curl -X POST http://localhost:5000/api/audio/analyze-direct \
  -F "audio_file=@test.wav"
```

### 기록 목록 조회 (로그인 불필요)
```bash
curl http://localhost:5000/api/records/
```

### 7일 리포트 생성 (로그인 불필요)  
```bash
curl http://localhost:5000/api/reports/7-day
```

## ⚠️ 주의사항

- **개발/테스트 전용**: 이 브랜치는 개발 및 테스트 목적으로만 사용하세요
- **보안 없음**: 모든 데이터가 user_id=1로 고정되어 저장됩니다
- **프로덕션 부적합**: 실제 서비스에서는 인증이 활성화된 main 브랜치를 사용하세요

## 🔄 원래 브랜치로 돌아가기

인증이 필요한 정상 버전으로 돌아가려면:
```bash
git checkout main
```

## 🧪 테스트 시나리오

1. **기본 API 테스트**: `test_no_auth.py` 실행
2. **오디오 분석**: `test_audio_analysis.py` 실행  
3. **직접 API 호출**: curl 명령어 사용
4. **프론트엔드 연동**: 토큰 없이 API 호출 가능

이 브랜치를 통해 인증 과정 없이 빠르게 API 기능을 테스트할 수 있습니다.
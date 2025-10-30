#!/usr/bin/env python3
"""
완전히 독립적인 오디오 스트레스 분석 테스트
사용자 제공 코드를 직접 구현
"""

import os
import sys

# 오디오 스트레스 분석 함수들을 직접 구현
def audio_to_w2v_embedding(audio_path, target_sr=16000):
    """오디오 파일을 Wav2Vec2 임베딩(512차원)으로 변환"""
    import librosa
    from transformers import Wav2Vec2Processor, Wav2Vec2Model
    import torch
    
    # 오디오 로드
    audio, sr = librosa.load(audio_path, sr=target_sr)
    
    # Wav2Vec2 모델 로드
    processor = Wav2Vec2Processor.from_pretrained("facebook/wav2vec2-base")
    w2v_model = Wav2Vec2Model.from_pretrained("facebook/wav2vec2-base")
    w2v_model.eval()
    
    # 오디오 전처리 및 임베딩 추출
    inputs = processor(audio, sampling_rate=target_sr, return_tensors="pt", padding=True)
    
    with torch.no_grad():
        outputs = w2v_model(**inputs)
        hidden_states = outputs.last_hidden_state  # (1, time_steps, 768)
        embedding_768 = hidden_states.mean(dim=1)  # 시간축 평균: (1, 768)
        embedding_512 = embedding_768[:, :512]     # 512차원으로 축소
    
    return embedding_512

def analyze_stress_from_audio_standalone(audio_path):
    """오디오 파일에서 스트레스 분석 (완전 독립 버전)"""
    from huggingface_hub import hf_hub_download
    import importlib.util
    from transformers import AutoConfig, AutoModelForAudioClassification
    import torch
    import torch.nn.functional as F
    
    repo = "forwarder1121/voice-based-stress-recognition"
    
    print("1) 스트레스 분석 모델 로딩 중...")
    # 커스텀 models.py 다운로드 및 로드
    code_path = hf_hub_download(repo_id=repo, filename="models.py")
    spec = importlib.util.spec_from_file_location("models", code_path)
    models = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(models)
    
    # Config 및 모델 로드
    cfg = AutoConfig.from_pretrained(repo, trust_remote_code=True)
    model = AutoModelForAudioClassification.from_pretrained(
        repo,
        trust_remote_code=True,
        torch_dtype="auto"
    )
    model.eval()
    
    print("2) 오디오 파일을 W2V 임베딩으로 변환 중...")
    # 오디오를 W2V 임베딩으로 변환
    x_w2v = audio_to_w2v_embedding(audio_path)
    
    # 모델과 같은 dtype으로 변환
    x_w2v = x_w2v.to(dtype=next(model.parameters()).dtype)
    
    print("3) 스트레스 분석 수행 중...")
    # 추론
    with torch.no_grad():
        outputs = model(x_w2v)
        probs = torch.nn.functional.softmax(outputs.logits, dim=-1)
    
    # 결과 출력
    not_stressed_prob = probs[0, 0].item() * 100
    stressed_prob = probs[0, 1].item() * 100
    
    print("\n" + "="*50)
    print(f"📊 스트레스 분석 결과:")
    print(f"   Not stressed: {not_stressed_prob:.1f}%")
    print(f"   Stressed    : {stressed_prob:.1f}%")
    print("="*50)
    
    return {
        "not_stressed": not_stressed_prob,
        "stressed": stressed_prob
    }

def main():
    """메인 테스트 함수"""
    print("🎵 완전 독립적인 오디오 스트레스 분석 테스트")
    print("=" * 60)
    
    # 오디오 파일 경로
    audio_path = "../data/scratch/test.wav"
    
    # 파일 존재 확인
    if not os.path.exists(audio_path):
        print(f"❌ 오디오 파일을 찾을 수 없습니다: {audio_path}")
        return
    
    try:
        print(f"🎵 오디오 파일: {audio_path}")
        print(f"📁 파일 크기: {os.path.getsize(audio_path)} bytes")
        print()
        
        # 스트레스 분석 실행
        result = analyze_stress_from_audio_standalone(audio_path)
        
        # 결과를 1-10 스케일로 변환
        stressed_prob = result['stressed']
        if stressed_prob <= 10:
            stress_level = 1
        elif stressed_prob <= 20:
            stress_level = 2
        elif stressed_prob <= 30:
            stress_level = 3
        elif stressed_prob <= 40:
            stress_level = 4
        elif stressed_prob <= 50:
            stress_level = 5
        elif stressed_prob <= 60:
            stress_level = 6
        elif stressed_prob <= 70:
            stress_level = 7
        elif stressed_prob <= 80:
            stress_level = 8
        elif stressed_prob <= 90:
            stress_level = 9
        else:
            stress_level = 10
        
        print(f"\n🎯 최종 결과:")
        print(f"   스트레스 레벨: {stress_level}/10")
        print(f"   스트레스 상태: {'높음' if stressed_prob > 50 else '낮음'}")
        print(f"   신뢰도: {max(result['not_stressed'], result['stressed']):.1f}%")
        
        print("\n✅ 실제 Hugging Face 모델을 사용한 분석 성공!")
        
    except Exception as e:
        print(f"❌ 오류 발생: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
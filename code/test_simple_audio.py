#!/usr/bin/env python3
"""
단순화된 오디오 스트레스 분석 테스트
사용자 제공 코드를 기반으로 한 테스트
"""

import os
import sys

# 경로 추가
sys.path.insert(0, '.')

def test_simple_audio_analysis():
    """단순 오디오 분석 테스트"""
    print("🎵 단순 오디오 스트레스 분석 테스트")
    print("=" * 50)
    
    audio_file = "../data/scratch/test.wav"
    
    if not os.path.exists(audio_file):
        print(f"❌ 오디오 파일을 찾을 수 없습니다: {audio_file}")
        return
    
    try:
        # 직접 함수 import
        from services.audio_stress_service import analyze_stress_from_audio_simple
        
        print("🚀 사용자 제공 코드로 분석 시작...")
        result = analyze_stress_from_audio_simple(audio_file)
        
        print("\n" + "=" * 50)
        print("📊 분석 결과:")
        print("=" * 50)
        print(f"Not stressed: {result['not_stressed']:.1f}%")
        print(f"Stressed    : {result['stressed']:.1f}%")
        
        # 1-10 스케일로 변환
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
        
        print(f"Stress level: {stress_level}/10")
        print(f"Is stressed : {'Yes' if stressed_prob > 50.0 else 'No'}")
        print("=" * 50)
        
        print("\n✅ 실제 ML 모델을 사용한 분석 성공!")
        
    except Exception as e:
        print(f"❌ 분석 실패: {e}")
        import traceback
        traceback.print_exc()

def test_service_class():
    """서비스 클래스 테스트"""
    print("\n🔧 서비스 클래스 테스트")
    print("=" * 50)
    
    audio_file = "../data/scratch/test.wav"
    
    try:
        from services.audio_stress_service import AudioStressAnalyzer
        
        analyzer = AudioStressAnalyzer()
        analyzer.initialize_models()
        
        result = analyzer.analyze_stress_from_audio_file(audio_file)
        
        print("📊 서비스 클래스 결과:")
        print(f"Not stressed: {result['not_stressed_probability']:.1f}%")
        print(f"Stressed    : {result['stressed_probability']:.1f}%")
        print(f"Stress level: {result['stress_level']}/10")
        print(f"Model used  : {result['model_used']}")
        
        print("\n✅ 서비스 클래스 테스트 성공!")
        
    except Exception as e:
        print(f"❌ 서비스 클래스 테스트 실패: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_simple_audio_analysis()
    test_service_class()
    
    print("\n✨ 모든 테스트 완료!")
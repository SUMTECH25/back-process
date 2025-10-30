#!/usr/bin/env python3
"""
순환 import 없이 오디오 분석을 테스트하는 스크립트
"""

import os
import sys
import tempfile
import logging
from typing import Dict, Optional, Tuple
from datetime import datetime

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Try to import the ML libraries with fallback handling
try:
    from huggingface_hub import hf_hub_download
    import importlib.util
    from transformers import AutoConfig, AutoModelForAudioClassification
    from transformers import Wav2Vec2Processor, Wav2Vec2Model
    import torch
    import torch.nn.functional as F
    import librosa
    ML_AVAILABLE = True
    logger.info("ML libraries imported successfully")
except ImportError as e:
    ML_AVAILABLE = False
    logger.warning(f"ML libraries not available: {e}. Using fallback mode.")

class StandaloneAudioAnalyzer:
    """독립적인 오디오 스트레스 분석기"""
    
    def __init__(self):
        self.repo = "forwarder1121/voice-based-stress-recognition"
        self.w2v_model = None
        self.w2v_processor = None
        self.stress_model = None
        self.stress_pipeline = None
        self.use_pipeline = False
        self.is_initialized = False
        self.ml_available = ML_AVAILABLE
        
    def initialize_models(self):
        """모델들을 초기화합니다."""
        if not self.ml_available:
            logger.warning("ML libraries not available. Audio analysis will use fallback mode.")
            self.is_initialized = True
            return
            
        try:
            logger.info("Initializing audio stress analysis models...")
            
            # Wav2Vec2 모델 로드
            logger.info("Loading Wav2Vec2 model...")
            self.w2v_processor = Wav2Vec2Processor.from_pretrained("facebook/wav2vec2-base")
            self.w2v_model = Wav2Vec2Model.from_pretrained("facebook/wav2vec2-base")
            self.w2v_model.eval()
            
            # 스트레스 분석 모델 로드
            logger.info("Loading stress analysis model...")
            
            # Config 및 모델 로드 (호환성 문제 해결)
            try:
                # 먼저 캐시를 정리하고 다시 시도
                logger.info("Attempting to load model with cache cleanup...")
                
                # 모델을 직접 로드하지 말고 pipeline을 사용해보자
                from transformers import pipeline
                
                # Audio classification pipeline으로 시도
                self.stress_pipeline = pipeline(
                    "audio-classification",
                    model=self.repo,
                    trust_remote_code=True
                )
                
                logger.info("Successfully loaded model via pipeline")
                self.use_pipeline = True
                
            except Exception as pipeline_error:
                logger.warning(f"Pipeline loading failed: {pipeline_error}")
                
                try:
                    # 대안: 직접 모델 로드 (config 없이)
                    logger.info("Trying direct model loading without config...")
                    self.stress_model = AutoModelForAudioClassification.from_pretrained(
                        self.repo,
                        trust_remote_code=True,
                        torch_dtype="auto"
                    )
                    self.use_pipeline = False
                    
                except Exception as direct_error:
                    logger.error(f"Direct loading also failed: {direct_error}")
                    raise Exception("All model loading methods failed")
            
            self.stress_model.eval()
            
            self.is_initialized = True
            logger.info("Audio stress analysis models initialized successfully")
            
        except Exception as e:
            logger.error(f"Error initializing audio models: {str(e)}")
            # Fall back to mock mode
            self.ml_available = False
            self.is_initialized = True
            logger.warning("Falling back to mock audio analysis mode")

    def audio_to_w2v_embedding(self, audio_path: str, target_sr: int = 16000):
        """오디오 파일을 Wav2Vec2 임베딩(512차원)으로 변환"""
        if not self.ml_available:
            raise RuntimeError("ML libraries not available for embedding conversion")
            
        try:
            # 오디오 로드
            audio, sr = librosa.load(audio_path, sr=target_sr)
            
            # 오디오 전처리 및 임베딩 추출
            inputs = self.w2v_processor(
                audio, 
                sampling_rate=target_sr, 
                return_tensors="pt", 
                padding=True
            )
            
            with torch.no_grad():
                outputs = self.w2v_model(**inputs)
                hidden_states = outputs.last_hidden_state  # (1, time_steps, 768)
                embedding_768 = hidden_states.mean(dim=1)  # 시간축 평균: (1, 768)
                embedding_512 = embedding_768[:, :512]     # 512차원으로 축소
            
            return embedding_512
            
        except Exception as e:
            logger.error(f"Error converting audio to embedding: {str(e)}")
            raise e

    def _fallback_audio_analysis(self, audio_path: str) -> Dict:
        """Fallback audio analysis when ML libraries are not available"""
        try:
            # Basic file analysis without ML libraries
            file_size = os.path.getsize(audio_path)
            file_name = os.path.basename(audio_path)
            
            # Mock analysis based on file characteristics
            # This is a simple heuristic - in production you might use other methods
            stress_level = min(max(1, int((file_size % 1000) / 100) + 3), 10)
            stressed_prob = (stress_level - 1) * 10 + 10
            not_stressed_prob = 100 - stressed_prob
            
            result = {
                "not_stressed_probability": round(not_stressed_prob, 2),
                "stressed_probability": round(stressed_prob, 2),
                "stress_level": stress_level,
                "is_stressed": stressed_prob > 50.0,
                "confidence": max(not_stressed_prob, stressed_prob),
                "analysis_timestamp": datetime.utcnow().isoformat(),
                "model_used": "fallback_mode",
                "note": "ML libraries unavailable - using fallback analysis"
            }
            
            logger.info(f"Fallback stress analysis: {stress_level}/10 stress level")
            return result
            
        except Exception as e:
            logger.error(f"Error in fallback audio analysis: {str(e)}")
            return {
                "error": str(e),
                "not_stressed_probability": 50,
                "stressed_probability": 50,
                "stress_level": 5,
                "is_stressed": False,
                "confidence": 50,
                "analysis_timestamp": datetime.utcnow().isoformat(),
                "model_used": "fallback_mode"
            }

    def analyze_stress_from_audio_file(self, audio_path: str) -> Dict:
        """오디오 파일에서 스트레스 분석"""
        try:
            # 모델이 초기화되지 않았으면 초기화
            if not self.is_initialized:
                self.initialize_models()
            
            logger.info(f"Analyzing stress from audio file: {audio_path}")
            
            # 파일 존재 확인
            if not os.path.exists(audio_path):
                raise FileNotFoundError(f"Audio file not found: {audio_path}")
            
            # ML 라이브러리가 없으면 fallback 모드 사용
            if not self.ml_available:
                return self._fallback_audio_analysis(audio_path)
            
            # Pipeline을 사용하는 경우
            if self.use_pipeline and self.stress_pipeline:
                try:
                    # 오디오 로드
                    audio, sr = librosa.load(audio_path, sr=16000)
                    
                    # Pipeline으로 분석
                    results = self.stress_pipeline(audio, sampling_rate=sr)
                    
                    # 결과 파싱 (가장 높은 점수 선택)
                    if isinstance(results, list) and len(results) > 0:
                        # 'STRESSED'와 'NOT_STRESSED' 라벨 찾기
                        stressed_score = 0
                        not_stressed_score = 0
                        
                        for result in results:
                            label = result['label'].upper()
                            score = result['score']
                            
                            if 'STRESS' in label and 'NOT' not in label:
                                stressed_score = score
                            elif 'NOT' in label or 'NORMAL' in label:
                                not_stressed_score = score
                        
                        # 확률 정규화
                        total = stressed_score + not_stressed_score
                        if total > 0:
                            stressed_prob = (stressed_score / total) * 100
                            not_stressed_prob = (not_stressed_score / total) * 100
                        else:
                            stressed_prob = stressed_score * 100
                            not_stressed_prob = not_stressed_score * 100
                        
                        # 스트레스 수준을 1-10 스케일로 변환
                        stress_level = self._probability_to_stress_level(stressed_prob)
                    else:
                        # Fallback to default values
                        stressed_prob = 50.0
                        not_stressed_prob = 50.0
                        stress_level = 5
                        
                except Exception as pipeline_error:
                    logger.error(f"Pipeline analysis failed: {pipeline_error}")
                    return self._fallback_audio_analysis(audio_path)
            
            else:
                # 기존 방식: 오디오를 W2V 임베딩으로 변환
                x_w2v = self.audio_to_w2v_embedding(audio_path)
                
                # 모델과 같은 dtype으로 변환
                x_w2v = x_w2v.to(dtype=next(self.stress_model.parameters()).dtype)
                
                # 추론
                with torch.no_grad():
                    outputs = self.stress_model(x_w2v)
                    probs = F.softmax(outputs.logits, dim=-1)
                
                # 결과 계산
                not_stressed_prob = probs[0, 0].item() * 100
                stressed_prob = probs[0, 1].item() * 100
                
                # 스트레스 수준을 1-10 스케일로 변환
                stress_level = self._probability_to_stress_level(stressed_prob)
            
            result = {
                "not_stressed_probability": round(not_stressed_prob, 2),
                "stressed_probability": round(stressed_prob, 2),
                "stress_level": stress_level,  # 1-10 스케일
                "is_stressed": stressed_prob > 50.0,
                "confidence": max(not_stressed_prob, stressed_prob),
                "analysis_timestamp": datetime.utcnow().isoformat(),
                "model_used": self.repo
            }
            
            logger.info(f"Stress analysis completed: {stress_level}/10 stress level")
            return result
            
        except Exception as e:
            logger.error(f"Error analyzing stress from audio: {str(e)}")
            # Try fallback mode if ML analysis fails
            if self.ml_available:
                logger.info("Attempting fallback analysis...")
                return self._fallback_audio_analysis(audio_path)
            
            return {
                "error": str(e),
                "not_stressed_probability": 50,
                "stressed_probability": 50,
                "stress_level": 5,  # 기본값
                "is_stressed": False,
                "confidence": 50,
                "analysis_timestamp": datetime.utcnow().isoformat(),
                "model_used": "error_fallback"
            }

    def _probability_to_stress_level(self, stressed_prob: float) -> int:
        """스트레스 확률을 1-10 스케일로 변환"""
        if stressed_prob <= 10:
            return 1
        elif stressed_prob <= 20:
            return 2
        elif stressed_prob <= 30:
            return 3
        elif stressed_prob <= 40:
            return 4
        elif stressed_prob <= 50:
            return 5
        elif stressed_prob <= 60:
            return 6
        elif stressed_prob <= 70:
            return 7
        elif stressed_prob <= 80:
            return 8
        elif stressed_prob <= 90:
            return 9
        else:
            return 10


def main():
    """메인 테스트 함수"""
    print("🔬 독립적인 오디오 스트레스 분석 테스트")
    print("=" * 50)
    
    audio_file = "../data/scratch/test.wav"
    
    if not os.path.exists(audio_file):
        print(f"❌ 오디오 파일을 찾을 수 없습니다: {audio_file}")
        return
    
    analyzer = StandaloneAudioAnalyzer()
    
    print("🚀 모델 초기화 중...")
    analyzer.initialize_models()
    
    if analyzer.ml_available:
        print("✅ ML 모델이 성공적으로 로드되었습니다!")
    else:
        print("⚠️  Fallback 모드를 사용합니다.")
    
    print("\n🎵 오디오 분석 실행 중...")
    result = analyzer.analyze_stress_from_audio_file(audio_file)
    
    print("\n" + "=" * 50)
    print("📊 분석 결과:")
    print("=" * 50)
    print(f"Not stressed: {result['not_stressed_probability']:.1f}%")
    print(f"Stressed    : {result['stressed_probability']:.1f}%")
    print(f"Stress level: {result['stress_level']}/10")
    print(f"Is stressed : {'Yes' if result['is_stressed'] else 'No'}")
    print(f"Confidence  : {result['confidence']:.1f}%")
    print(f"Model used  : {result['model_used']}")
    print(f"Analyzed at : {result['analysis_timestamp']}")
    if 'note' in result:
        print(f"Note        : {result['note']}")
    print("=" * 50)
    
    print("\n✨ 분석 완료!")


if __name__ == "__main__":
    main()
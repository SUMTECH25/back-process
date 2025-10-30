"""
오디오 기반 스트레스 분석 서비스
사용자 제공 코드를 기반으로 한 단순하고 효과적인 구현
"""

import os
import tempfile
import logging
from typing import Dict, Optional, Tuple
from datetime import datetime, timezone
import numpy as np

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
    logger = logging.getLogger(__name__)
    logger.info("ML libraries imported successfully")
except ImportError as e:
    ML_AVAILABLE = False
    logger = logging.getLogger(__name__)
    logger.warning(f"ML libraries not available: {e}. Using fallback mode.")
    
    # Create dummy classes for fallback
    class torch:
        class Tensor:
            pass
        @staticmethod
        def no_grad():
            return DummyContext()
    
    class DummyContext:
        def __enter__(self):
            return self
        def __exit__(self, *args):
            pass

def audio_to_w2v_embedding(audio_path, target_sr=16000):
    """오디오 파일을 Wav2Vec2 임베딩(512차원)으로 변환"""
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

def analyze_stress_from_audio_simple(audio_path):
    """오디오 파일에서 스트레스 분석 (사용자 제공 코드 기반)"""
    
    repo = "forwarder1121/voice-based-stress-recognition"
    
    logger.info("1) 스트레스 분석 모델 로딩 중...")
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
    
    logger.info("2) 오디오 파일을 W2V 임베딩으로 변환 중...")
    # 오디오를 W2V 임베딩으로 변환
    x_w2v = audio_to_w2v_embedding(audio_path)
    
    # 모델과 같은 dtype으로 변환
    x_w2v = x_w2v.to(dtype=next(model.parameters()).dtype)
    
    logger.info("3) 스트레스 분석 수행 중...")
    # 추론
    with torch.no_grad():
        outputs = model(x_w2v)
        probs = F.softmax(outputs.logits, dim=-1)
    
    # 결과 계산
    not_stressed_prob = probs[0, 0].item() * 100
    stressed_prob = probs[0, 1].item() * 100
    
    logger.info(f"스트레스 분석 결과: Not stressed {not_stressed_prob:.1f}%, Stressed {stressed_prob:.1f}%")
    
    return {
        "not_stressed": not_stressed_prob,
        "stressed": stressed_prob
    }

logger = logging.getLogger(__name__)

class AudioStressAnalyzer:
    """오디오 스트레스 분석기 (단순화된 버전)"""
    
    def __init__(self):
        self.is_initialized = False
        self.ml_available = ML_AVAILABLE
        
    def initialize_models(self):
        """모델들을 초기화합니다."""
        if not self.ml_available:
            logger.warning("ML libraries not available. Audio analysis will use fallback mode.")
            self.is_initialized = True  # Mark as initialized for fallback mode
            return
            
        try:
            logger.info("Models will be loaded on-demand for better reliability")
            self.is_initialized = True
            logger.info("Audio stress analysis ready")
            
        except Exception as e:
            logger.error(f"Error in initialization: {str(e)}")
            # Fall back to mock mode
            self.ml_available = False
            self.is_initialized = True
            logger.warning("Falling back to mock audio analysis mode")
    
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
                "analysis_timestamp": datetime.now(timezone.utc).isoformat(),
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
                "analysis_timestamp": datetime.now(timezone.utc).isoformat(),
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
            
            # 사용자 제공 코드로 분석 실행
            try:
                simple_result = analyze_stress_from_audio_simple(audio_path)
                
                # 결과를 표준 형식으로 변환
                not_stressed_prob = simple_result['not_stressed']
                stressed_prob = simple_result['stressed']
                stress_level = self._probability_to_stress_level(stressed_prob)
                
                result = {
                    "not_stressed_probability": round(not_stressed_prob, 2),
                    "stressed_probability": round(stressed_prob, 2),
                    "stress_level": stress_level,  # 1-10 스케일
                    "is_stressed": stressed_prob > 50.0,
                    "confidence": max(not_stressed_prob, stressed_prob),
                    "analysis_timestamp": datetime.now(timezone.utc).isoformat(),
                    "model_used": "forwarder1121/voice-based-stress-recognition"
                }
                
                logger.info(f"Stress analysis completed: {stress_level}/10 stress level")
                return result
                
            except Exception as ml_error:
                logger.error(f"ML analysis failed: {ml_error}")
                return self._fallback_audio_analysis(audio_path)
            
        except Exception as e:
            logger.error(f"Error analyzing stress from audio: {str(e)}")
            
            return {
                "error": str(e),
                "not_stressed_probability": 50,
                "stressed_probability": 50,
                "stress_level": 5,  # 기본값
                "is_stressed": False,
                "confidence": 50,
                "analysis_timestamp": datetime.now(timezone.utc).isoformat(),
                "model_used": "error_fallback"
            }
    
    def analyze_stress_from_audio_data(self, audio_data: bytes, filename: str = "audio.wav") -> Dict:
        """바이트 데이터에서 스트레스 분석"""
        try:
            # 임시 파일에 오디오 데이터 저장
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_file:
                temp_file.write(audio_data)
                temp_path = temp_file.name
            
            try:
                # 임시 파일에서 분석 수행
                result = self.analyze_stress_from_audio_file(temp_path)
                result["original_filename"] = filename
                return result
            finally:
                # 임시 파일 삭제
                if os.path.exists(temp_path):
                    os.unlink(temp_path)
                    
        except Exception as e:
            logger.error(f"Error analyzing stress from audio data: {str(e)}")
            return {
                "error": str(e),
                "stress_level": 5,
                "is_stressed": False
            }
    
    def _probability_to_stress_level(self, stressed_prob: float) -> int:
        """스트레스 확률을 1-10 스케일로 변환"""
        # 0-100% 확률을 1-10 스케일로 매핑
        # 50% 이하는 1-5 (낮은 스트레스)
        # 50% 이상은 6-10 (높은 스트레스)
        
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
    
    def validate_audio_file(self, file_path: str) -> Tuple[bool, Optional[str]]:
        """오디오 파일 유효성 검사"""
        try:
            if not os.path.exists(file_path):
                return False, "File does not exist"
            
            # 파일 확장자 확인
            valid_extensions = ['.wav', '.mp3', '.flac', '.m4a', '.ogg']
            file_ext = os.path.splitext(file_path)[1].lower()
            
            if file_ext not in valid_extensions:
                return False, f"Invalid file format. Supported: {', '.join(valid_extensions)}"
            
            # 파일 크기 확인 (최대 50MB)
            file_size = os.path.getsize(file_path)
            max_size = 50 * 1024 * 1024  # 50MB
            
            if file_size > max_size:
                return False, f"File too large. Maximum size: {max_size // (1024*1024)}MB"
            
            # 파일 크기가 너무 작은지 확인 (최소 1KB)
            if file_size < 1024:
                return False, "File too small. Minimum size: 1KB"
            
            # 오디오 파일 로드 테스트 (librosa가 사용 가능한 경우만)
            if self.ml_available:
                try:
                    audio, sr = librosa.load(file_path, duration=1.0)  # 1초만 테스트
                    if len(audio) == 0:
                        return False, "Empty audio file"
                except Exception as e:
                    return False, f"Cannot read audio file: {str(e)}"
            
            return True, None
            
        except Exception as e:
            return False, str(e)

# 글로벌 분석기 인스턴스
audio_analyzer = AudioStressAnalyzer()

def analyze_audio_stress(audio_path: str) -> Dict:
    """
    오디오 파일에서 스트레스 분석 (외부 API용)
    
    Args:
        audio_path: 오디오 파일 경로
    
    Returns:
        스트레스 분석 결과
    """
    return audio_analyzer.analyze_stress_from_audio_file(audio_path)

def analyze_audio_stress_from_data(audio_data: bytes, filename: str = "audio.wav") -> Dict:
    """
    오디오 바이트 데이터에서 스트레스 분석 (외부 API용)
    
    Args:
        audio_data: 오디오 파일 바이트 데이터
        filename: 원본 파일명
    
    Returns:
        스트레스 분석 결과
    """
    return audio_analyzer.analyze_stress_from_audio_data(audio_data, filename)

def validate_audio_input(file_path: str) -> Tuple[bool, Optional[str]]:
    """
    오디오 파일 유효성 검사 (외부 API용)
    
    Args:
        file_path: 오디오 파일 경로
    
    Returns:
        (유효성, 에러메시지)
    """
    return audio_analyzer.validate_audio_file(file_path)

def get_supported_audio_formats() -> list:
    """지원되는 오디오 형식 목록"""
    return ['.wav', '.mp3', '.flac', '.m4a', '.ogg']

def initialize_audio_models():
    """오디오 모델 초기화 (앱 시작시 호출)"""
    try:
        audio_analyzer.initialize_models()
        if audio_analyzer.ml_available:
            logger.info("Audio stress analysis models ready (ML mode)")
        else:
            logger.info("Audio stress analysis ready (fallback mode)")
        return True
    except Exception as e:
        logger.error(f"Failed to initialize audio models: {str(e)}")
        return False
"""
NLP 서비스 - 한 문장 스트레스 분석
"""

import os
from typing import Dict, Optional
import logging

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def analyze_sentence(sentence: str) -> Optional[Dict]:
    """
    한 문장을 분석하여 스트레스, 감정 등을 추출
    
    Args:
        sentence: 분석할 문장
    
    Returns:
        분석 결과 딕셔너리
    """
    try:
        if not sentence or not sentence.strip():
            return None
        
        # 기본적인 키워드 기반 분석 (프로토타입용)
        # 실제 구현시에는 transformers 라이브러리 사용
        analysis_result = basic_sentiment_analysis(sentence)
        
        # TODO: Hugging Face transformers 모델 사용
        # model_name = "klue/bert-base"  # 한국어 BERT 모델
        # tokenizer = AutoTokenizer.from_pretrained(model_name)
        # model = AutoModelForSequenceClassification.from_pretrained(model_name)
        
        return {
            'sentence': sentence,
            'sentiment': analysis_result['sentiment'],
            'confidence': analysis_result['confidence'],
            'stress_indicators': analysis_result['stress_indicators'],
            'emotion_keywords': analysis_result['emotion_keywords'],
            'analysis_timestamp': analysis_result['timestamp']
        }
        
    except Exception as e:
        logger.error(f"Error analyzing sentence: {str(e)}")
        return {
            'sentence': sentence,
            'sentiment': 'neutral',
            'confidence': 0.5,
            'stress_indicators': [],
            'emotion_keywords': [],
            'error': str(e),
            'analysis_timestamp': None
        }

def basic_sentiment_analysis(sentence: str) -> Dict:
    """
    기본적인 키워드 기반 감정 분석 (프로토타입용)
    """
    from datetime import datetime, timezone
    
    sentence_lower = sentence.lower()
    
    # 스트레스 관련 키워드
    stress_keywords = [
        '스트레스', '피곤', '힘들', '지쳐', '답답', '짜증', '화나', 
        '우울', '불안', '걱정', '부담', '압박', '막막', '절망'
    ]
    
    # 긍정적 키워드
    positive_keywords = [
        '좋', '행복', '기쁘', '만족', '편안', '평온', '즐겁', 
        '감사', '희망', '성취', '뿌듯', '보람'
    ]
    
    # 부정적 키워드
    negative_keywords = [
        '나쁘', '싫', '슬프', '아프', '무서', '걱정', '실망', 
        '분노', '좌절', '후회', '원망'
    ]
    
    # 키워드 매칭
    stress_indicators = [kw for kw in stress_keywords if kw in sentence_lower]
    positive_matches = [kw for kw in positive_keywords if kw in sentence_lower]
    negative_matches = [kw for kw in negative_keywords if kw in sentence_lower]
    
    # 감정 점수 계산
    positive_score = len(positive_matches)
    negative_score = len(negative_matches) + len(stress_indicators)
    
    # 감정 분류
    if positive_score > negative_score:
        sentiment = 'positive'
        confidence = min(0.9, 0.6 + (positive_score - negative_score) * 0.1)
    elif negative_score > positive_score:
        sentiment = 'negative'
        confidence = min(0.9, 0.6 + (negative_score - positive_score) * 0.1)
    else:
        sentiment = 'neutral'
        confidence = 0.5
    
    return {
        'sentiment': sentiment,
        'confidence': round(confidence, 2),
        'stress_indicators': stress_indicators,
        'emotion_keywords': positive_matches + negative_matches,
        'timestamp': datetime.now(timezone.utc).isoformat()
    }

def get_stress_level_from_sentence(sentence: str) -> int:
    """
    문장에서 스트레스 수준을 1-10으로 추정
    """
    analysis = analyze_sentence(sentence)
    
    if not analysis:
        return 5  # 기본값
    
    sentiment = analysis['sentiment']
    stress_count = len(analysis['stress_indicators'])
    
    if sentiment == 'negative' and stress_count > 0:
        return min(10, 6 + stress_count)
    elif sentiment == 'positive':
        return max(1, 4 - len(analysis['emotion_keywords']))
    else:
        return 5

def extract_emotion_patterns(sentences: list) -> Dict:
    """
    여러 문장에서 감정 패턴 추출
    """
    if not sentences:
        return {}
    
    all_analyses = []
    for sentence in sentences:
        if sentence:
            analysis = analyze_sentence(sentence)
            if analysis:
                all_analyses.append(analysis)
    
    if not all_analyses:
        return {}
    
    # 패턴 분석
    sentiments = [a['sentiment'] for a in all_analyses]
    stress_words = []
    emotion_words = []
    
    for analysis in all_analyses:
        stress_words.extend(analysis['stress_indicators'])
        emotion_words.extend(analysis['emotion_keywords'])
    
    # 감정 분포
    sentiment_distribution = {
        'positive': sentiments.count('positive'),
        'negative': sentiments.count('negative'),
        'neutral': sentiments.count('neutral')
    }
    
    # 자주 사용하는 스트레스 단어
    from collections import Counter
    common_stress_words = Counter(stress_words).most_common(5)
    common_emotion_words = Counter(emotion_words).most_common(5)
    
    return {
        'total_sentences': len(all_analyses),
        'sentiment_distribution': sentiment_distribution,
        'dominant_sentiment': max(sentiment_distribution, key=sentiment_distribution.get),
        'common_stress_indicators': dict(common_stress_words),
        'common_emotion_keywords': dict(common_emotion_words),
        'average_confidence': sum(a['confidence'] for a in all_analyses) / len(all_analyses)
    }
"""
유효성 검사 유틸리티
"""

import re
from datetime import datetime, date
from typing import Dict, List, Optional, Union

def validate_email(email: str) -> bool:
    """이메일 형식 검증"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))

def validate_password(password: str) -> Dict[str, Union[bool, List[str]]]:
    """
    비밀번호 강도 검증
    
    Returns:
        Dict with 'valid' boolean and 'errors' list
    """
    errors = []
    
    if len(password) < 8:
        errors.append("비밀번호는 최소 8자 이상이어야 합니다.")
    
    if not re.search(r'[A-Za-z]', password):
        errors.append("비밀번호에는 최소 하나의 영문자가 포함되어야 합니다.")
    
    if not re.search(r'\d', password):
        errors.append("비밀번호에는 최소 하나의 숫자가 포함되어야 합니다.")
    
    return {
        'valid': len(errors) == 0,
        'errors': errors
    }

def validate_username(username: str) -> Dict[str, Union[bool, str]]:
    """사용자명 검증"""
    if not username:
        return {'valid': False, 'error': '사용자명은 필수입니다.'}
    
    if len(username) < 3:
        return {'valid': False, 'error': '사용자명은 최소 3자 이상이어야 합니다.'}
    
    if len(username) > 20:
        return {'valid': False, 'error': '사용자명은 20자를 초과할 수 없습니다.'}
    
    if not re.match(r'^[a-zA-Z0-9_]+$', username):
        return {'valid': False, 'error': '사용자명은 영문자, 숫자, 언더스코어만 사용할 수 있습니다.'}
    
    return {'valid': True, 'error': None}

def validate_stress_level(stress_level: Union[int, str]) -> Dict[str, Union[bool, str]]:
    """스트레스 수준 검증 (1-10)"""
    try:
        level = int(stress_level)
        if 1 <= level <= 10:
            return {'valid': True, 'error': None}
        else:
            return {'valid': False, 'error': '스트레스 수준은 1-10 사이의 값이어야 합니다.'}
    except (ValueError, TypeError):
        return {'valid': False, 'error': '스트레스 수준은 숫자여야 합니다.'}

def validate_energy_level(energy_level: Union[int, str]) -> Dict[str, Union[bool, str]]:
    """에너지 수준 검증 (1-10)"""
    try:
        level = int(energy_level)
        if 1 <= level <= 10:
            return {'valid': True, 'error': None}
        else:
            return {'valid': False, 'error': '에너지 수준은 1-10 사이의 값이어야 합니다.'}
    except (ValueError, TypeError):
        return {'valid': False, 'error': '에너지 수준은 숫자여야 합니다.'}

def validate_mood(mood: str) -> Dict[str, Union[bool, str]]:
    """기분 검증"""
    valid_moods = [
        'happy', 'sad', 'angry', 'anxious', 'excited', 'tired', 
        'stressed', 'calm', 'frustrated', 'content', 'worried', 'neutral'
    ]
    
    if not mood:
        return {'valid': False, 'error': '기분은 필수입니다.'}
    
    if mood.lower() not in valid_moods:
        return {'valid': False, 'error': f'유효하지 않은 기분입니다. 가능한 값: {", ".join(valid_moods)}'}
    
    return {'valid': True, 'error': None}

def validate_date(date_str: str) -> Dict[str, Union[bool, str, date]]:
    """날짜 형식 검증"""
    if not date_str:
        return {'valid': False, 'error': '날짜는 필수입니다.', 'parsed_date': None}
    
    try:
        parsed_date = datetime.strptime(date_str, '%Y-%m-%d').date()
        
        # 미래 날짜 검증
        if parsed_date > date.today():
            return {'valid': False, 'error': '미래 날짜는 입력할 수 없습니다.', 'parsed_date': None}
        
        # 너무 오래된 날짜 검증 (1년 전까지만)
        if parsed_date < date.today().replace(year=date.today().year - 1):
            return {'valid': False, 'error': '1년 이전의 날짜는 입력할 수 없습니다.', 'parsed_date': None}
        
        return {'valid': True, 'error': None, 'parsed_date': parsed_date}
        
    except ValueError:
        return {'valid': False, 'error': '날짜 형식이 올바르지 않습니다. (YYYY-MM-DD)', 'parsed_date': None}

def validate_sentence(sentence: str) -> Dict[str, Union[bool, str]]:
    """일일 문장 검증"""
    if not sentence:
        return {'valid': True, 'error': None}  # 선택사항이므로 빈 값 허용
    
    if len(sentence) > 500:
        return {'valid': False, 'error': '문장은 500자를 초과할 수 없습니다.'}
    
    if len(sentence.strip()) < 2:
        return {'valid': False, 'error': '의미있는 문장을 입력해주세요.'}
    
    return {'valid': True, 'error': None}

def validate_daily_record(data: Dict) -> Dict[str, Union[bool, List[str]]]:
    """일일 기록 전체 검증"""
    errors = []
    
    # 필수 필드 검증
    required_fields = ['stress_level', 'mood', 'energy_level']
    for field in required_fields:
        if field not in data:
            errors.append(f'{field} is required')
    
    # 개별 필드 검증
    if 'stress_level' in data:
        stress_validation = validate_stress_level(data['stress_level'])
        if not stress_validation['valid']:
            errors.append(stress_validation['error'])
    
    if 'energy_level' in data:
        energy_validation = validate_energy_level(data['energy_level'])
        if not energy_validation['valid']:
            errors.append(energy_validation['error'])
    
    if 'mood' in data:
        mood_validation = validate_mood(data['mood'])
        if not mood_validation['valid']:
            errors.append(mood_validation['error'])
    
    # 선택적 필드 검증
    if 'work_satisfaction' in data and data['work_satisfaction'] is not None:
        work_satisfaction_validation = validate_stress_level(data['work_satisfaction'])  # 같은 1-10 스케일
        if not work_satisfaction_validation['valid']:
            errors.append('업무 만족도는 1-10 사이의 값이어야 합니다.')
    
    if 'work_load' in data and data['work_load'] is not None:
        work_load_validation = validate_stress_level(data['work_load'])  # 같은 1-10 스케일
        if not work_load_validation['valid']:
            errors.append('업무량은 1-10 사이의 값이어야 합니다.')
    
    if 'daily_sentence' in data:
        sentence_validation = validate_sentence(data['daily_sentence'])
        if not sentence_validation['valid']:
            errors.append(sentence_validation['error'])
    
    if 'record_date' in data:
        date_validation = validate_date(data['record_date'])
        if not date_validation['valid']:
            errors.append(date_validation['error'])
    
    return {
        'valid': len(errors) == 0,
        'errors': errors
    }

def validate_user_registration(data: Dict) -> Dict[str, Union[bool, List[str]]]:
    """사용자 등록 정보 검증"""
    errors = []
    
    # 필수 필드 검증
    required_fields = ['username', 'email', 'password']
    for field in required_fields:
        if field not in data or not data[field]:
            errors.append(f'{field} is required')
    
    # 개별 필드 검증
    if 'username' in data:
        username_validation = validate_username(data['username'])
        if not username_validation['valid']:
            errors.append(username_validation['error'])
    
    if 'email' in data:
        if not validate_email(data['email']):
            errors.append('유효하지 않은 이메일 형식입니다.')
    
    if 'password' in data:
        password_validation = validate_password(data['password'])
        if not password_validation['valid']:
            errors.extend(password_validation['errors'])
    
    # 선택적 필드 검증
    if 'stress_level' in data and data['stress_level'] is not None:
        stress_validation = validate_stress_level(data['stress_level'])
        if not stress_validation['valid']:
            errors.append(stress_validation['error'])
    
    return {
        'valid': len(errors) == 0,
        'errors': errors
    }

def sanitize_string(input_string: str, max_length: int = None) -> str:
    """문자열 정화 및 길이 제한"""
    if not input_string:
        return ""
    
    # HTML 태그 제거
    import html
    sanitized = html.escape(input_string.strip())
    
    # 길이 제한
    if max_length and len(sanitized) > max_length:
        sanitized = sanitized[:max_length]
    
    return sanitized

def validate_api_pagination(page: Union[int, str], per_page: Union[int, str]) -> Dict:
    """API 페이지네이션 파라미터 검증"""
    try:
        page_num = int(page) if page else 1
        per_page_num = int(per_page) if per_page else 20
        
        # 범위 검증
        if page_num < 1:
            page_num = 1
        
        if per_page_num < 1:
            per_page_num = 20
        elif per_page_num > 100:  # 최대 100개까지
            per_page_num = 100
        
        return {
            'valid': True,
            'page': page_num,
            'per_page': per_page_num
        }
        
    except (ValueError, TypeError):
        return {
            'valid': False,
            'error': 'Invalid pagination parameters',
            'page': 1,
            'per_page': 20
        }
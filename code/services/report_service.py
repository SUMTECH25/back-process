"""
리포트 생성 서비스 (분석 및 PDF)
"""

import os
from datetime import datetime, date, timedelta
from typing import Dict, List, Optional
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import pandas as pd
import numpy as np
from models.user import User
from models.daily_record import DailyRecord
from services.reward_service import generate_30day_report
import logging

logger = logging.getLogger(__name__)

def generate_analysis_report(user_id: int, start_date: date, end_date: date, report_type: str) -> Dict:
    """
    분석 리포트 생성
    
    Args:
        user_id: 사용자 ID
        start_date: 시작 날짜
        end_date: 종료 날짜  
        report_type: '3', '7', '30'
    
    Returns:
        리포트 데이터
    """
    try:
        records = DailyRecord.get_user_records(user_id, start_date, end_date)
        
        if not records:
            return {
                'error': 'No records found for the specified period',
                'period': {
                    'start_date': start_date.isoformat(),
                    'end_date': end_date.isoformat()
                }
            }
        
        # 기본 통계
        stress_levels = [r.stress_level for r in records]
        energy_levels = [r.energy_level for r in records]
        moods = [r.mood for r in records]
        
        # pandas를 사용한 고급 분석
        df = pd.DataFrame({
            'date': [r.record_date for r in records],
            'stress_level': stress_levels,
            'energy_level': energy_levels,
            'mood': moods
        })
        
        # 기본 통계
        basic_stats = {
            'total_records': len(records),
            'avg_stress_level': df['stress_level'].mean(),
            'avg_energy_level': df['energy_level'].mean(),
            'stress_std': df['stress_level'].std(),
            'energy_std': df['energy_level'].std(),
            'stress_trend': calculate_trend(stress_levels),
            'energy_trend': calculate_trend(energy_levels)
        }
        
        # 기분 분포
        mood_distribution = df['mood'].value_counts().to_dict()
        
        # 상관관계 분석
        stress_energy_correlation = df['stress_level'].corr(df['energy_level'])
        
        # 주간 패턴 (7일 이상인 경우)
        weekly_pattern = None
        if len(records) >= 7:
            df['weekday'] = pd.to_datetime(df['date']).dt.day_name()
            weekly_pattern = df.groupby('weekday')[['stress_level', 'energy_level']].mean().to_dict()
        
        # 리포트 타입별 특화 분석
        specialized_analysis = {}
        if report_type == '7':
            specialized_analysis = analyze_7day_patterns(df)
        elif report_type == '30':
            specialized_analysis = analyze_30day_patterns(df)
        
        return {
            'report_type': f'{report_type}일 분석 리포트',
            'period': {
                'start_date': start_date.isoformat(),
                'end_date': end_date.isoformat(),
                'duration_days': len(records)
            },
            'basic_statistics': {
                'total_records': basic_stats['total_records'],
                'average_stress_level': round(basic_stats['avg_stress_level'], 2),
                'average_energy_level': round(basic_stats['avg_energy_level'], 2),
                'stress_variability': round(basic_stats['stress_std'], 2),
                'energy_variability': round(basic_stats['energy_std'], 2)
            },
            'trends': {
                'stress_trend': 'increasing' if basic_stats['stress_trend'] > 0.1 else 'decreasing' if basic_stats['stress_trend'] < -0.1 else 'stable',
                'energy_trend': 'increasing' if basic_stats['energy_trend'] > 0.1 else 'decreasing' if basic_stats['energy_trend'] < -0.1 else 'stable',
                'stress_energy_correlation': round(stress_energy_correlation, 3)
            },
            'mood_analysis': {
                'distribution': mood_distribution,
                'dominant_mood': max(mood_distribution, key=mood_distribution.get),
                'mood_variety': len(mood_distribution)
            },
            'weekly_pattern': weekly_pattern,
            'specialized_analysis': specialized_analysis,
            'generated_at': datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error generating analysis report: {str(e)}")
        return {'error': str(e)}

def calculate_trend(values: List[float]) -> float:
    """선형 트렌드 계산"""
    if len(values) < 2:
        return 0
    
    x = np.arange(len(values))
    y = np.array(values)
    
    # 선형 회귀 계수 계산
    slope = np.polyfit(x, y, 1)[0]
    return slope

def analyze_7day_patterns(df: pd.DataFrame) -> Dict:
    """7일 패턴 특화 분석"""
    try:
        # 스트레스 피크 분석
        high_stress_days = df[df['stress_level'] >= 8]
        
        # 에너지 저점 분석
        low_energy_days = df[df['energy_level'] <= 3]
        
        # 회복 패턴 분석
        recovery_days = df[df['stress_level'] <= 4]
        
        return {
            'high_stress_frequency': len(high_stress_days) / len(df),
            'low_energy_frequency': len(low_energy_days) / len(df),
            'recovery_frequency': len(recovery_days) / len(df),
            'stress_peaks': high_stress_days['date'].dt.strftime('%Y-%m-%d').tolist() if not high_stress_days.empty else [],
            'energy_lows': low_energy_days['date'].dt.strftime('%Y-%m-%d').tolist() if not low_energy_days.empty else [],
            'recommendations': generate_7day_recommendations(df)
        }
        
    except Exception as e:
        logger.error(f"Error analyzing 7-day patterns: {str(e)}")
        return {'error': str(e)}

def analyze_30day_patterns(df: pd.DataFrame) -> Dict:
    """30일 패턴 특화 분석"""
    try:
        # 주간별 분석
        df['week'] = (pd.to_datetime(df['date']) - pd.to_datetime(df['date']).min()).dt.days // 7 + 1
        weekly_stats = df.groupby('week')[['stress_level', 'energy_level']].agg(['mean', 'std']).round(2)
        
        # 장기 트렌드
        long_term_trend = {
            'stress_improvement': df['stress_level'].iloc[-7:].mean() < df['stress_level'].iloc[:7].mean(),
            'energy_improvement': df['energy_level'].iloc[-7:].mean() > df['energy_level'].iloc[:7].mean(),
            'consistency_improvement': df['stress_level'].iloc[-7:].std() < df['stress_level'].iloc[:7].std()
        }
        
        # 이상치 탐지
        stress_q75, stress_q25 = df['stress_level'].quantile([0.75, 0.25])
        stress_iqr = stress_q75 - stress_q25
        stress_outliers = df[
            (df['stress_level'] < (stress_q25 - 1.5 * stress_iqr)) | 
            (df['stress_level'] > (stress_q75 + 1.5 * stress_iqr))
        ]
        
        return {
            'weekly_breakdown': weekly_stats.to_dict(),
            'long_term_trends': long_term_trend,
            'outlier_days': stress_outliers['date'].dt.strftime('%Y-%m-%d').tolist() if not stress_outliers.empty else [],
            'stability_score': calculate_stability_score(df),
            'recommendations': generate_30day_recommendations(df, long_term_trend)
        }
        
    except Exception as e:
        logger.error(f"Error analyzing 30-day patterns: {str(e)}")
        return {'error': str(e)}

def calculate_stability_score(df: pd.DataFrame) -> float:
    """안정성 점수 계산 (0-100)"""
    stress_cv = df['stress_level'].std() / df['stress_level'].mean()  # 변동계수
    energy_cv = df['energy_level'].std() / df['energy_level'].mean()
    
    # 낮은 변동계수일수록 높은 점수
    stability = 100 - min(100, (stress_cv + energy_cv) * 50)
    return round(max(0, stability), 1)

def generate_7day_recommendations(df: pd.DataFrame) -> List[str]:
    """7일 분석 기반 권장사항"""
    recommendations = []
    
    avg_stress = df['stress_level'].mean()
    avg_energy = df['energy_level'].mean()
    
    if avg_stress > 7:
        recommendations.append("높은 스트레스 수준이 지속되고 있습니다. 스트레스 관리 기법을 도입해보세요.")
    
    if avg_energy < 4:
        recommendations.append("에너지 수준이 낮습니다. 수면 패턴과 영양 상태를 점검해보세요.")
    
    if df['stress_level'].std() > 2:
        recommendations.append("스트레스 수준의 변동이 큽니다. 일정한 루틴 만들기를 권장합니다.")
    
    # 주간 패턴 기반 권장사항
    if 'weekday' in df.columns:
        weekday_stress = df.groupby('weekday')['stress_level'].mean()
        high_stress_day = weekday_stress.idxmax()
        recommendations.append(f"{high_stress_day}에 스트레스가 높은 경향이 있습니다. 해당 요일의 일정을 조정해보세요.")
    
    return recommendations

def generate_30day_recommendations(df: pd.DataFrame, trends: Dict) -> List[str]:
    """30일 분석 기반 권장사항"""
    recommendations = []
    
    if not trends['stress_improvement']:
        recommendations.append("스트레스 수준이 개선되지 않고 있습니다. 전문가 상담을 고려해보세요.")
    else:
        recommendations.append("스트레스 관리가 향상되고 있습니다. 현재 방법을 지속하세요.")
    
    if not trends['energy_improvement']:
        recommendations.append("에너지 수준 개선이 필요합니다. 생활 습관 전반을 점검해보세요.")
    
    if trends['consistency_improvement']:
        recommendations.append("감정 상태가 안정화되고 있습니다. 좋은 추세입니다.")
    
    return recommendations

def generate_pdf_report(user_id: int, report_data: Dict) -> str:
    """
    PDF 리포트 생성
    
    Args:
        user_id: 사용자 ID
        report_data: 리포트 데이터
    
    Returns:
        생성된 PDF 파일 경로
    """
    try:
        # PDF 파일 경로 설정
        pdf_dir = os.path.join(os.getcwd(), 'reports', 'pdf')
        os.makedirs(pdf_dir, exist_ok=True)
        
        filename = f'30day_report_{user_id}_{datetime.now().strftime("%Y%m%d_%H%M%S")}.pdf'
        pdf_path = os.path.join(pdf_dir, filename)
        
        # PDF 문서 생성
        doc = SimpleDocTemplate(pdf_path, pagesize=A4)
        styles = getSampleStyleSheet()
        story = []
        
        # 제목
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            spaceAfter=30,
            alignment=1  # 중앙 정렬
        )
        story.append(Paragraph("30일 스트레스 관리 종합 리포트", title_style))
        story.append(Spacer(1, 12))
        
        # 사용자 정보
        if 'user_profile' in report_data:
            profile = report_data['user_profile']
            story.append(Paragraph(f"<b>이름:</b> {profile.get('name', 'Unknown')}", styles['Normal']))
            story.append(Paragraph(f"<b>직업:</b> {profile.get('occupation', 'Unknown')}", styles['Normal']))
            story.append(Spacer(1, 12))
        
        # 기간 정보
        if 'period' in report_data:
            period = report_data['period']
            story.append(Paragraph(f"<b>분석 기간:</b> {period['start_date']} ~ {period['end_date']}", styles['Normal']))
            story.append(Paragraph(f"<b>총 기록 일수:</b> {period['total_days']}일", styles['Normal']))
            story.append(Spacer(1, 20))
        
        # 전체 통계
        if 'overall_statistics' in report_data:
            story.append(Paragraph("전체 통계", styles['Heading2']))
            stats = report_data['overall_statistics']
            
            stats_data = [
                ['항목', '값'],
                ['평균 스트레스 수준', f"{stats['average_stress_level']}/10"],
                ['평균 에너지 수준', f"{stats['average_energy_level']}/10"],
                ['스트레스 범위', stats['stress_range']],
                ['일관성', stats['stress_consistency']]
            ]
            
            stats_table = Table(stats_data)
            stats_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 14),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            
            story.append(stats_table)
            story.append(Spacer(1, 20))
        
        # 개인화된 인사이트
        if 'personalized_insights' in report_data:
            story.append(Paragraph("개인화된 인사이트", styles['Heading2']))
            
            for insight in report_data['personalized_insights']:
                insight_text = f"• {insight['message']}"
                story.append(Paragraph(insight_text, styles['Normal']))
            
            story.append(Spacer(1, 20))
        
        # 감정 분석 (있는 경우)
        if 'emotion_analysis' in report_data and report_data['emotion_analysis']:
            story.append(Paragraph("감정 분석", styles['Heading2']))
            emotion = report_data['emotion_analysis']
            
            story.append(Paragraph(f"<b>총 분석된 문장:</b> {emotion['total_sentences']}개", styles['Normal']))
            story.append(Paragraph(f"<b>주요 감정:</b> {emotion['dominant_sentiment']}", styles['Normal']))
            
            if emotion['common_stress_indicators']:
                story.append(Paragraph("<b>자주 언급된 스트레스 지표:</b>", styles['Normal']))
                for word, count in emotion['common_stress_indicators'].items():
                    story.append(Paragraph(f"  • {word}: {count}회", styles['Normal']))
            
            story.append(Spacer(1, 20))
        
        # 주간 패턴
        if 'weekly_patterns' in report_data:
            story.append(Paragraph("주간별 패턴", styles['Heading2']))
            
            weekly_data = [['주차', '평균 스트레스', '평균 에너지', '기록 일수']]
            for week in report_data['weekly_patterns']:
                weekly_data.append([
                    f"{week['week_number']}주차",
                    str(week['avg_stress']),
                    str(week['avg_energy']),
                    f"{week['days_recorded']}일"
                ])
            
            weekly_table = Table(weekly_data)
            weekly_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 12),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            
            story.append(weekly_table)
            story.append(Spacer(1, 20))
        
        # 달성 성과
        if 'achievements' in report_data:
            story.append(Paragraph("달성 성과", styles['Heading2']))
            achievements = report_data['achievements']
            
            story.append(Paragraph(f"🎉 {achievements['milestone_reached']}", styles['Normal']))
            story.append(Paragraph(f"📊 기록 완료율: {achievements['completion_rate']}", styles['Normal']))
            story.append(Paragraph(f"🔥 연속 기록: {achievements['consecutive_days']}일", styles['Normal']))
        
        # PDF 빌드
        doc.build(story)
        
        logger.info(f"PDF report generated: {pdf_path}")
        return pdf_path
        
    except Exception as e:
        logger.error(f"Error generating PDF report: {str(e)}")
        raise e

def create_chart_image(data: List[float], title: str, filename: str) -> str:
    """
    차트 이미지 생성 (matplotlib 사용)
    
    Args:
        data: 차트 데이터
        title: 차트 제목
        filename: 저장할 파일명
    
    Returns:
        이미지 파일 경로
    """
    try:
        import matplotlib.pyplot as plt
        import matplotlib.dates as mdates
        
        plt.figure(figsize=(10, 6))
        plt.plot(data, marker='o', linewidth=2, markersize=6)
        plt.title(title, fontsize=16, fontweight='bold')
        plt.xlabel('일수', fontsize=12)
        plt.ylabel('수준', fontsize=12)
        plt.grid(True, alpha=0.3)
        plt.tight_layout()
        
        # 이미지 저장
        img_dir = os.path.join(os.getcwd(), 'reports', 'images')
        os.makedirs(img_dir, exist_ok=True)
        
        img_path = os.path.join(img_dir, filename)
        plt.savefig(img_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        return img_path
        
    except Exception as e:
        logger.error(f"Error creating chart image: {str(e)}")
        return None
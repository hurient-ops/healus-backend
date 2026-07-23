import sys
import os
import json
from openai import OpenAI

# Add parent directory to path to import models and core
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.database import SessionLocal
from models import models

def test_lm_studio_inference():
    db = SessionLocal()
    try:
        # 1. Fetch user and their data
        test_email = "testuser@healus.com"
        user = db.query(models.User).filter(models.User.email == test_email).first()
        
        if not user:
            print("[ERROR] User not found. Please run generate_mock_data.py first.")
            return

        logs = db.query(models.PumpLog).filter(models.PumpLog.user_id == user.id).order_by(models.PumpLog.created_at.asc()).all()
        
        if not logs:
            print("[ERROR] No logs found for user. Please run generate_mock_data.py first.")
            return

        # 2. Format data for prompt
        print(f"[INFO] Extracted {len(logs)} days of data for {user.name} ({user.email}).")
        
        # Summarize data by weekday vs weekend to keep prompt concise
        weekday_eat = []
        weekend_eat = []
        
        for log in logs:
            is_weekend = log.created_at.weekday() >= 5
            if is_weekend:
                weekend_eat.append(log.eat_total)
            else:
                weekday_eat.append(log.eat_total)
                
        avg_weekday = sum(weekday_eat) / len(weekday_eat) if weekday_eat else 0
        avg_weekend = sum(weekend_eat) / len(weekend_eat) if weekend_eat else 0

        # Raw data snapshot of last 5 days
        recent_logs_text = "\n".join([
            f"- {log.month}/{log.day}: 기초(Basal): {log.base_total}U, 식사(Bolus): {log.eat_total}U (아침:{log.morning_total}, 점심:{log.afternoon_total}, 저녁:{log.evening_total}, 추가:{log.append_total})"
            for log in logs[-5:]
        ])

        prompt = f"""
당신은 당뇨병 환자의 인슐린 펌프 데이터를 분석하여 맞춤형 식습관 및 주입량 조언을 제공하는 전문 AI 주치의입니다.

[환자 데이터 요약 - 최근 30일]
- 평일 평균 식사 주입량(Bolus): {avg_weekday:.1f}U
- 주말 평균 식사 주입량(Bolus): {avg_weekend:.1f}U

[최근 5일 상세 데이터]
{recent_logs_text}

[요청 사항]
위 데이터를 바탕으로 환자의 주말과 평일 식습관 차이를 분석하고, 기저 주입량(Basal) 및 식사 주입량(Bolus) 관리에 대한 구체적인 조언을 정확히 3줄로 요약해서 제공해주세요. (전문적이고 친절한 한국어로 답변할 것)
"""

        print("\n[INFO] Sending Prompt to LM Studio...")
        print("-" * 50)
        print(prompt)
        print("-" * 50)

        # 3. Call LM Studio Local API (OpenAI Compatible)
        # Assuming LM Studio is running on default port 1234
        client = OpenAI(base_url="http://localhost:1234/v1", api_key="lm-studio")
        
        response = client.chat.completions.create(
            model="llama-3.1-storm-8b", # Updated to match exact LM Studio identifier
            messages=[
                {"role": "system", "content": "You are a helpful, professional medical AI assistant."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=500
        )

        print("\n[AI INSIGHT REPORT]")
        print("=" * 50)
        print(response.choices[0].message.content)
        print("=" * 50)

    except Exception as e:
        print(f"[ERROR] Error during AI inference: {e}")
        print("\n[TIP] Check if LM Studio server is running on http://localhost:1234")
    finally:
        db.close()

if __name__ == "__main__":
    test_lm_studio_inference()

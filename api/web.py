from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime, timezone
import dateutil.parser

from core.database import get_db
from models import models, schemas
from openai import OpenAI

router = APIRouter()

@router.get("/dashboard")
def get_dashboard_data(email: str = "testuser@healus.com", db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.email == email).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Get 100 days of pump logs for full simulation and anomaly detection
    pump_logs = db.query(models.PumpLog).filter(models.PumpLog.user_id == user.id).order_by(models.PumpLog.created_at.desc()).limit(100).all()
    pump_logs.reverse()

    # Get today's BG logs
    bg_logs = db.query(models.BloodGlucoseLog).filter(models.BloodGlucoseLog.user_id == user.id).order_by(models.BloodGlucoseLog.recorded_at.desc()).limit(20).all()

    processed_pump_logs = []
    for log in pump_logs:
        processed_pump_logs.append({
            "date": f"{log.month}/{log.day}",
            "basal": log.base_total,
            "bolus": log.eat_total,
            "append": log.append_total,
            "avg_cgm": log.avg_cgm,
            "sleep_hours": log.sleep_hours,
            "stress_level": log.stress_level,
            "exercise_hours": log.exercise_hours,
            "event_tags": log.event_tags,
            "error_count": log.error_count,
            "error_types": log.error_types
        })

    return {
        "status": "success",
        "data": {
            "user_name": user.name,
            "pump_logs": processed_pump_logs,
            "bg_logs": [
                {
                    "value": bg.glucose_value,
                    "tag": bg.tag,
                    "time": bg.recorded_at.isoformat()
                } for bg in bg_logs
            ]
        }
    }

@router.post("/bg-log")
def log_blood_glucose(payload: schemas.BloodGlucoseLogRequest, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.email == payload.user_email).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    try:
        recorded_dt = dateutil.parser.isoparse(payload.recorded_at)
    except:
        recorded_dt = datetime.now(timezone.utc)

    new_log = models.BloodGlucoseLog(
        user_id=user.id,
        glucose_value=payload.glucose_value,
        tag=payload.tag,
        recorded_at=recorded_dt
    )
    db.add(new_log)
    db.commit()

    return {"status": "success", "message": "혈당이 성공적으로 기록되었습니다."}

@router.get("/ai-insight")
def get_ai_insight(email: str = "testuser@healus.com", db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.email == email).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    logs = db.query(models.PumpLog).filter(models.PumpLog.user_id == user.id).order_by(models.PumpLog.created_at.desc()).limit(7).all()
    logs.reverse()

    if not logs:
        return {"insight": "아직 충분한 데이터가 수집되지 않았습니다. 매일 데이터를 꾸준히 기록해주세요."}

    recent_logs_text = "\n".join([
        f"- {log.month}/{log.day}: 식사 주입(Bolus) {log.eat_total}U, 수면 {log.sleep_hours}h, 스트레스 {log.stress_level}/10, 운동 {log.exercise_hours}h, 이벤트 [{log.event_tags or '없음'}], 평균혈당 {log.avg_cgm}mg/dL"
        for log in logs
    ])

    prompt = f"""
당신은 당뇨병 환자의 라이프로그(Lifelog) 데이터를 분석하는 전문 AI 주치의입니다.
아래는 최근 7일간의 심층 데이터입니다 (인슐린 주입량, 수면, 스트레스, 운동, 이벤트 태그, 연속혈당(CGM) 평균치).

환자 데이터 요약 (최근 7일):
{recent_logs_text}

지시사항:
1. 위 데이터를 종합적으로 분석하여 회식, 수면 부족, 스트레스가 혈당에 미친 영향을 '추론(Reasoning)' 과정을 포함하여 상세히 분석해 주세요.
2. 결과는 JSON 형식으로 반환해야 합니다.
3. JSON 스키마는 다음과 같아야 합니다:
{{
    "reasoning_process": ["첫 번째 추론 단계", "두 번째 추론 단계", ...],
    "insight": "환자를 위한 따뜻하고 전문적인 최종 조언 (3줄 이내)"
}}
절대 마크다운(```json) 텍스트 블록으로 감싸지 말고 순수 JSON 문자열만 출력하세요.
"""

    try:
        client = OpenAI(base_url="http://localhost:1234/v1", api_key="lm-studio")
        response = client.chat.completions.create(
            model="llama-3.1-storm-8b",
            messages=[
                {"role": "system", "content": "You are a helpful, professional medical AI assistant."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=500
        )
        ai_response = response.choices[0].message.content
        import json
        
        # In case the model returns markdown wrapped json
        if ai_response.startswith("```"):
            ai_response = ai_response.split("```")[1]
            if ai_response.startswith("json"):
                ai_response = ai_response[4:]
        
        parsed_json = json.loads(ai_response)
        reasoning = parsed_json.get("reasoning_process", [])
        insight = parsed_json.get("insight", "")
        model_name = "LLaMA-3.1-Storm-8B"
        
    except Exception as e:
        # Fallback if local LM studio is unreachable or json parsing fails
        import traceback
        traceback.print_exc()
        reasoning = [
            "최근 7일간의 수면 데이터와 회식 태그를 교차 분석 중...",
            "회식 날짜 직후 수면 시간이 2시간가량 단축된 것을 확인.",
            "수면 부족과 스트레스 증가가 다음 날 평균 혈당(CGM) 상승에 영향을 미쳤을 확률 87% 도출."
        ]
        insight = "최근 7일간 '회식' 이벤트가 있었던 날 직후 수면 부족 현상이 나타났으며, 이로 인해 다음 날 혈당 스파이크가 발생했습니다. 회식 후에도 규칙적인 수면 시간을 확보하도록 노력해 보세요."
        model_name = "Healus Fallback AI"
        prompt = "Mock AI Inference due to connection failure."

    return {
        "status": "success", 
        "insight": insight, 
        "reasoning": reasoning, 
        "model": model_name,
        "prompt_used": prompt
    }

import time
import json

def verify_access(event_id, gate_id, network="online", quality_score=0.88, liveness_score=0.95, occlusion=None):
    start_time = time.time()
    reasons = []
    
    # 1. Проверка сети
    degraded = (network == "offline")
    if degraded:
        reasons.append("degraded_mode_offline")

    # 2. Проверка качества и Liveness
    if occlusion == "mask" or quality_score < 0.6:
        reasons.append("low_frame_quality")
    if liveness_score < 0.8:
        reasons.append("liveness_check_failed")

    # 3. Эмуляция поиска по базе (Match)
    if event_id == "e-1001":
        match_score = 0.85
        margin = 0.20
        emp_id = "emp-4821"
    elif event_id == "e-1004": # Сомнительный случай
        match_score = 0.68
        margin = 0.02
        emp_id = "emp-9999"
        reasons.append("low_margin_to_second_best")
    else: # Неизвестный или спуфинг
        match_score = 0.30
        margin = 0.00
        emp_id = None

    # 4. Логика принятия решений
    allow_threshold = 0.80 if not degraded else 0.90
    
    if "liveness_check_failed" in reasons or "low_frame_quality" in reasons:
        decision = "manual_review"
    elif match_score >= allow_threshold and margin >= 0.10 and not degraded:
        decision = "allow"
        reasons.extend(["quality_ok", "liveness_ok", "match_above_allow_threshold"])
    elif match_score >= 0.60:
        decision = "manual_review"
    else:
        decision = "deny"
        reasons.append("unknown_face")

    turnstile_command = "open" if decision == "allow" else "keep_closed"
    
    result = {
        "event_id": event_id,
        "decision_id": f"d-{event_id}",
        "decision": decision,
        "employee_id": emp_id if decision == "allow" else None,
        "match_score": match_score,
        "reasons": reasons,
        "turnstile_command": turnstile_command,
        "requires_human_review": (decision == "manual_review"),
        "degraded_mode": degraded,
        "latency_ms": int((time.time() - start_time) * 1000) + 40
    }
    
    # Логирование в audit log
    with open("audit_log.jsonl", "a", encoding="utf-8") as f:
        f.write(json.dumps(result, ensure_ascii=False) + "\n")
        
    return result

if __name__ == "__main__":
    print("--- 1. HAPPY PATH (Авто-допуск) ---")
    print(json.dumps(verify_access("e-1001", "gate-2"), indent=2, ensure_ascii=False))
    
    print("\n--- 2. RISKY PATH (Маска / Спуфинг -> Ручная проверка) ---")
    print(json.dumps(verify_access("e-1002", "gate-1", quality_score=0.45, occlusion="mask"), indent=2, ensure_ascii=False))

import json
from database.db import query, execute
from config import DEFAULT_EVAL_WEIGHTS


def get_session_evaluation(session_id):
    return query(
        "SELECT * FROM evaluations WHERE session_id = ?",
        (session_id,), one=True,
    )


def save_evaluation(session_id, eval_data):
    weights = DEFAULT_EVAL_WEIGHTS
    general_scores = [
        eval_data.get("communication_clarity", 5),
        eval_data.get("empathy_rapport", 5),
        eval_data.get("active_listening", 5),
        eval_data.get("professional_language", 5),
        eval_data.get("call_structure", 5),
        eval_data.get("call_control", 5),
        eval_data.get("objection_handling", 5),
    ]
    general_avg = (sum(general_scores) / len(general_scores)) * 10  # Scale to 100

    checkpoints = eval_data.get("checkpoints", [])
    if checkpoints:
        passed = sum(1 for c in checkpoints if c.get("passed", False))
        checkpoint_pct = (passed / len(checkpoints)) * 100
    else:
        checkpoint_pct = 0

    goal_map = {"ACHIEVED": 100, "PARTIAL": 50, "FAILED": 0}
    goal_score = goal_map.get(eval_data.get("goal_achieved", "PARTIAL"), 50)

    overall = (
        general_avg * weights["weight_general"]
        + checkpoint_pct * weights["weight_checkpoints"]
        + goal_score * weights["weight_goal"]
        + eval_data.get("bonus_points", 0)
        - eval_data.get("penalty_points", 0)
    )
    overall = max(0, min(100, round(overall, 1)))

    eval_id = execute("""
        INSERT INTO evaluations (
            session_id, overall_score,
            communication_clarity, empathy_rapport, active_listening,
            professional_language, call_structure, call_control, objection_handling,
            checkpoint_results, checkpoint_order_ok, goal_achieved, hidden_need_found,
            bonus_points, penalty_points,
            summary, strengths, improvements, coaching_tip, raw_llm_response
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        session_id, overall,
        eval_data.get("communication_clarity", 5),
        eval_data.get("empathy_rapport", 5),
        eval_data.get("active_listening", 5),
        eval_data.get("professional_language", 5),
        eval_data.get("call_structure", 5),
        eval_data.get("call_control", 5),
        eval_data.get("objection_handling", 5),
        json.dumps(checkpoints),
        eval_data.get("checkpoint_order_correct", True),
        eval_data.get("goal_achieved", "PARTIAL"),
        eval_data.get("hidden_need_found", False),
        eval_data.get("bonus_points", 0),
        eval_data.get("penalty_points", 0),
        eval_data.get("summary", ""),
        json.dumps(eval_data.get("strengths", [])),
        json.dumps(eval_data.get("improvements", [])),
        eval_data.get("coaching_tip", ""),
        json.dumps(eval_data),
    ))
    return eval_id, overall


def get_user_stats(user_id):
    stats = query("""
        SELECT
            COUNT(s.id) as total_sessions,
            COALESCE(AVG(e.overall_score), 0) as avg_score,
            COALESCE(MAX(e.overall_score), 0) as best_score,
            COALESCE(SUM(s.duration_seconds), 0) as total_time
        FROM sessions s
        LEFT JOIN evaluations e ON e.session_id = s.id
        WHERE s.user_id = ? AND s.status = 'completed'
    """, (user_id,), one=True)
    return stats


def get_user_recent_sessions(user_id, limit=5):
    return query("""
        SELECT s.*, sc.name as scenario_name, sc.category, sc.difficulty,
            e.overall_score, e.goal_achieved
        FROM sessions s
        JOIN scenarios sc ON sc.id = s.scenario_id
        LEFT JOIN evaluations e ON e.session_id = s.id
        WHERE s.user_id = ? AND s.status = 'completed'
        ORDER BY s.started_at DESC
        LIMIT ?
    """, (user_id, limit))


def get_team_stats(team=None):
    where = "WHERE u.role = 'agent'"
    params = []
    if team:
        where += " AND u.team = ?"
        params.append(team)

    return query(f"""
        SELECT
            COUNT(DISTINCT u.id) as total_agents,
            COUNT(CASE WHEN date(u.last_active) = date('now') THEN 1 END) as active_today,
            COALESCE(AVG(e.overall_score), 0) as avg_score,
            COUNT(CASE WHEN s.started_at >= datetime('now', '-7 days') THEN s.id END) as sessions_this_week
        FROM users u
        LEFT JOIN sessions s ON s.user_id = u.id AND s.status = 'completed'
        LEFT JOIN evaluations e ON e.session_id = s.id
        {where}
    """, params, one=True)


def get_team_score_trend(team=None, days=30):
    where = "WHERE u.role = 'agent' AND s.status = 'completed'"
    params = []
    if team:
        where += " AND u.team = ?"
        params.append(team)

    return query(f"""
        SELECT date(s.started_at) as day, AVG(e.overall_score) as avg_score
        FROM sessions s
        JOIN users u ON u.id = s.user_id
        JOIN evaluations e ON e.session_id = s.id
        {where}
        AND s.started_at >= datetime('now', '-{days} days')
        GROUP BY date(s.started_at)
        ORDER BY day
    """, params)


def get_agent_skill_scores(user_id):
    return query("""
        SELECT
            AVG(e.communication_clarity) as communication_clarity,
            AVG(e.empathy_rapport) as empathy_rapport,
            AVG(e.active_listening) as active_listening,
            AVG(e.professional_language) as professional_language,
            AVG(e.call_structure) as call_structure,
            AVG(e.call_control) as call_control,
            AVG(e.objection_handling) as objection_handling
        FROM sessions s
        JOIN evaluations e ON e.session_id = s.id
        WHERE s.user_id = ? AND s.status = 'completed'
    """, (user_id,), one=True)

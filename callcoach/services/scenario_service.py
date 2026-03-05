import json
from database.db import query, execute


def get_all_scenarios(active_only=True):
    sql = "SELECT * FROM scenarios"
    if active_only:
        sql += " WHERE is_active = 1"
    sql += " ORDER BY category, difficulty"
    return query(sql)


def get_scenario(scenario_id):
    return query("SELECT * FROM scenarios WHERE id = ?", (scenario_id,), one=True)


def get_scenario_checkpoints(scenario_id):
    return query(
        "SELECT * FROM checkpoints WHERE scenario_id = ? ORDER BY order_index",
        (scenario_id,),
    )


def get_scenarios_by_category(category):
    return query(
        "SELECT * FROM scenarios WHERE category = ? AND is_active = 1 ORDER BY difficulty",
        (category,),
    )


def get_user_best_score(user_id, scenario_id):
    result = query("""
        SELECT MAX(e.overall_score) as best_score
        FROM sessions s
        JOIN evaluations e ON e.session_id = s.id
        WHERE s.user_id = ? AND s.scenario_id = ? AND s.status = 'completed'
    """, (user_id, scenario_id), one=True)
    return result["best_score"] if result else None


def get_user_scenario_attempts(user_id, scenario_id):
    result = query("""
        SELECT COUNT(*) as cnt
        FROM sessions
        WHERE user_id = ? AND scenario_id = ? AND status = 'completed'
    """, (user_id, scenario_id), one=True)
    return result["cnt"] if result else 0


def get_scenario_stats(scenario_id):
    return query("""
        SELECT
            COUNT(s.id) as total_attempts,
            AVG(e.overall_score) as avg_score,
            MAX(e.overall_score) as best_score
        FROM sessions s
        LEFT JOIN evaluations e ON e.session_id = s.id
        WHERE s.scenario_id = ? AND s.status = 'completed'
    """, (scenario_id,), one=True)

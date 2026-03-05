import json
from datetime import datetime
from database.db import query, execute
from config import (
    LEVEL_THRESHOLDS, LEVEL_NAMES,
    XP_BASE_CALL, XP_PER_POINT_ABOVE_70, XP_PERFECT_BONUS,
    XP_FIRST_SCENARIO, XP_DAILY_STREAK,
)


def calculate_level(xp):
    level = 1
    for lvl, threshold in sorted(LEVEL_THRESHOLDS.items()):
        if xp >= threshold:
            level = lvl
    return level


def get_level_name(level):
    return LEVEL_NAMES.get(level, "Unknown")


def get_xp_to_next_level(xp, current_level):
    next_level = current_level + 1
    if next_level > 10:
        return 0
    return LEVEL_THRESHOLDS.get(next_level, 25000) - xp


def get_xp_progress_pct(xp, current_level):
    current_threshold = LEVEL_THRESHOLDS.get(current_level, 0)
    next_level = current_level + 1
    if next_level > 10:
        return 100
    next_threshold = LEVEL_THRESHOLDS.get(next_level, 25000)
    range_total = next_threshold - current_threshold
    if range_total <= 0:
        return 100
    progress = xp - current_threshold
    return min(100, int((progress / range_total) * 100))


def calculate_xp_for_session(user_id, session_id, overall_score, scenario_id):
    xp_total = 0
    reasons = []

    # Base XP
    xp_total += XP_BASE_CALL
    reasons.append(f"Dokončený hovor: +{XP_BASE_CALL} XP")

    # Score bonus
    if overall_score > 70:
        bonus = int(overall_score - 70) * XP_PER_POINT_ABOVE_70
        xp_total += bonus
        reasons.append(f"Bonus za skóre ({overall_score:.0f}%): +{bonus} XP")

    # Perfect score
    if overall_score >= 99.5:
        xp_total += XP_PERFECT_BONUS
        reasons.append(f"Perfektné skóre: +{XP_PERFECT_BONUS} XP")

    # First time scenario
    prev_attempts = query("""
        SELECT COUNT(*) as cnt FROM sessions
        WHERE user_id = ? AND scenario_id = ? AND status = 'completed' AND id != ?
    """, (user_id, scenario_id, session_id), one=True)
    if prev_attempts and prev_attempts["cnt"] == 0:
        xp_total += XP_FIRST_SCENARIO
        reasons.append(f"Prvé dokončenie scenára: +{XP_FIRST_SCENARIO} XP")

    return xp_total, reasons


def award_xp(user_id, session_id, xp_amount, reason):
    execute(
        "INSERT INTO xp_log (user_id, session_id, xp_earned, reason) VALUES (?, ?, ?, ?)",
        (user_id, session_id, xp_amount, reason),
    )
    execute("UPDATE users SET xp = xp + ? WHERE id = ?", (xp_amount, user_id))
    user = query("SELECT xp FROM users WHERE id = ?", (user_id,), one=True)
    new_level = calculate_level(user["xp"])
    execute("UPDATE users SET level = ? WHERE id = ?", (new_level, user_id))
    return new_level


def get_user_achievements(user_id):
    return query("""
        SELECT a.*, ua.earned_at
        FROM achievements a
        LEFT JOIN user_achievements ua ON ua.achievement_id = a.id AND ua.user_id = ?
        ORDER BY ua.earned_at DESC NULLS LAST, a.id
    """, (user_id,))


def get_earned_achievements(user_id):
    return query("""
        SELECT a.*, ua.earned_at
        FROM user_achievements ua
        JOIN achievements a ON a.id = ua.achievement_id
        WHERE ua.user_id = ?
        ORDER BY ua.earned_at DESC
    """, (user_id,))


def check_and_award_achievements(user_id):
    earned = get_earned_achievements(user_id)
    earned_ids = {a["id"] for a in earned}
    all_achievements = query("SELECT * FROM achievements")
    newly_earned = []

    for achievement in all_achievements:
        if achievement["id"] in earned_ids:
            continue

        if _check_achievement_condition(user_id, achievement):
            execute(
                "INSERT OR IGNORE INTO user_achievements (user_id, achievement_id) VALUES (?, ?)",
                (user_id, achievement["id"]),
            )
            newly_earned.append(achievement)

    return newly_earned


def _check_achievement_condition(user_id, achievement):
    ctype = achievement["condition_type"]
    cvalue = achievement["condition_value"]

    if ctype == "first_call":
        result = query(
            "SELECT COUNT(*) as cnt FROM sessions WHERE user_id = ? AND status = 'completed'",
            (user_id,), one=True,
        )
        return result and result["cnt"] >= 1

    if ctype == "perfect_score":
        result = query("""
            SELECT MAX(e.overall_score) as best
            FROM sessions s JOIN evaluations e ON e.session_id = s.id
            WHERE s.user_id = ? AND s.status = 'completed'
        """, (user_id,), one=True)
        return result and result["best"] and result["best"] >= float(cvalue)

    if ctype == "streak":
        user = query("SELECT streak_days FROM users WHERE id = ?", (user_id,), one=True)
        return user and user["streak_days"] >= int(cvalue)

    if ctype == "daily_calls":
        result = query("""
            SELECT COUNT(*) as cnt FROM sessions
            WHERE user_id = ? AND status = 'completed' AND date(started_at) = date('now')
        """, (user_id,), one=True)
        return result and result["cnt"] >= int(cvalue)

    return False


def get_leaderboard(team=None, period="all"):
    where_clauses = ["u.role = 'agent'"]
    params = []

    if team:
        where_clauses.append("u.team = ?")
        params.append(team)

    if period == "week":
        where_clauses.append("s.started_at >= datetime('now', '-7 days')")
    elif period == "month":
        where_clauses.append("s.started_at >= datetime('now', '-30 days')")

    where = " AND ".join(where_clauses)

    return query(f"""
        SELECT u.id, u.name, u.level, u.xp, u.streak_days,
            COUNT(s.id) as session_count,
            COALESCE(AVG(e.overall_score), 0) as avg_score
        FROM users u
        LEFT JOIN sessions s ON s.user_id = u.id AND s.status = 'completed'
        LEFT JOIN evaluations e ON e.session_id = s.id
        WHERE {where}
        GROUP BY u.id
        ORDER BY avg_score DESC, u.xp DESC
    """, params)

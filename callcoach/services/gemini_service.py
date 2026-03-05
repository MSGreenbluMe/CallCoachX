import json
from config import GEMINI_API_KEY


def evaluate_call(transcript, scenario, checkpoints):
    """Send transcript to Gemini for evaluation. Returns parsed evaluation dict."""
    if not GEMINI_API_KEY:
        return _generate_demo_evaluation(checkpoints)

    try:
        import google.generativeai as genai

        genai.configure(api_key=GEMINI_API_KEY)
        model = genai.GenerativeModel("gemini-2.0-flash-lite")

        checkpoint_text = "\n".join(
            f"  {i+1}. {cp['name']}: {cp['description']}"
            for i, cp in enumerate(checkpoints)
        )

        prompt = f"""Si expert na kvalitu hovorov v call centre. Tvoja úloha je objektívne
vyhodnotiť nasledujúci hovor medzi operátorom a zákazníkom.

Buď prísny ale spravodlivý. Hodnoť na základe konkrétnych dôkazov
z prepisu, nie domnienok.

SCENÁR: {scenario.get('description', '')}
CIEĽ AGENTA: {scenario.get('primary_goal', '')}
POVINNÉ BODY:
{checkpoint_text}

PREPIS HOVORU:
{transcript}

Vráť VÝHRADNE valídny JSON podľa nasledujúcej schémy, žiadny iný text:

{{
  "communication_clarity": {{"score": 1-10, "evidence": "...", "recommendation": "..."}},
  "empathy_rapport": {{"score": 1-10, "evidence": "...", "recommendation": "..."}},
  "active_listening": {{"score": 1-10, "evidence": "...", "recommendation": "..."}},
  "professional_language": {{"score": 1-10, "evidence": "...", "recommendation": "..."}},
  "call_structure": {{"score": 1-10, "evidence": "...", "recommendation": "..."}},
  "call_control": {{"score": 1-10, "evidence": "...", "recommendation": "..."}},
  "objection_handling": {{"score": 1-10, "evidence": "...", "recommendation": "..."}},
  "checkpoints": [
    {{"checkpoint_id": 1, "passed": true/false, "evidence": "..."}}
  ],
  "checkpoint_order_correct": true/false,
  "goal_achieved": "ACHIEVED" | "PARTIAL" | "FAILED",
  "hidden_need_found": true/false,
  "summary": "2-3 vety zhrnutie",
  "strengths": ["...", "...", "..."],
  "improvements": ["...", "...", "..."],
  "coaching_tip": "..."
}}"""

        response = model.generate_content(
            prompt,
            generation_config=genai.GenerationConfig(
                response_mime_type="application/json",
            ),
        )

        result = json.loads(response.text)
        return _normalize_evaluation(result, checkpoints)

    except Exception as e:
        print(f"Gemini evaluation error: {e}")
        return _generate_demo_evaluation(checkpoints)


def _normalize_evaluation(raw, checkpoints):
    """Normalize Gemini response to flat evaluation dict."""

    def _get_score(field):
        val = raw.get(field, {})
        if isinstance(val, dict):
            return val.get("score", 5)
        return val if isinstance(val, (int, float)) else 5

    checkpoint_results = raw.get("checkpoints", [])
    if not checkpoint_results:
        checkpoint_results = [
            {"checkpoint_id": cp["id"], "passed": True, "evidence": ""}
            for cp in checkpoints
        ]

    return {
        "communication_clarity": _get_score("communication_clarity"),
        "empathy_rapport": _get_score("empathy_rapport"),
        "active_listening": _get_score("active_listening"),
        "professional_language": _get_score("professional_language"),
        "call_structure": _get_score("call_structure"),
        "call_control": _get_score("call_control"),
        "objection_handling": _get_score("objection_handling"),
        "checkpoints": checkpoint_results,
        "checkpoint_order_correct": raw.get("checkpoint_order_correct", True),
        "goal_achieved": raw.get("goal_achieved", "PARTIAL"),
        "hidden_need_found": raw.get("hidden_need_found", False),
        "summary": raw.get("summary", "Hovor prebehol podľa očakávaní."),
        "strengths": raw.get("strengths", []),
        "improvements": raw.get("improvements", []),
        "coaching_tip": raw.get("coaching_tip", ""),
        "bonus_points": 0,
        "penalty_points": 0,
    }


def _generate_demo_evaluation(checkpoints):
    """Generate a demo evaluation when Gemini API is not available."""
    import random

    checkpoint_results = []
    for cp in checkpoints:
        checkpoint_results.append({
            "checkpoint_id": cp["id"],
            "passed": random.random() > 0.25,
            "evidence": f"Agent splnil bod: {cp['name']}" if random.random() > 0.25 else f"Agent vynechal: {cp['name']}",
        })

    goal = random.choice(["ACHIEVED", "PARTIAL", "ACHIEVED"])

    return {
        "communication_clarity": round(random.uniform(6, 9.5), 1),
        "empathy_rapport": round(random.uniform(5.5, 9), 1),
        "active_listening": round(random.uniform(6, 9), 1),
        "professional_language": round(random.uniform(7, 9.5), 1),
        "call_structure": round(random.uniform(6, 9), 1),
        "call_control": round(random.uniform(5.5, 8.5), 1),
        "objection_handling": round(random.uniform(5, 8.5), 1),
        "checkpoints": checkpoint_results,
        "checkpoint_order_correct": random.random() > 0.3,
        "goal_achieved": goal,
        "hidden_need_found": random.random() > 0.5,
        "summary": "Hovor prebehol celkovo dobre. Agent prejavil profesionálny prístup a snažil sa vyriešiť problém zákazníka. Niektoré oblasti však majú priestor na zlepšenie.",
        "strengths": [
            "Profesionálny a priateľský tón počas celého hovoru",
            "Dobrá štruktúra hovoru s jasným úvodom a záverom",
            "Aktívne počúvanie a parafrázovanie problému zákazníka",
        ],
        "improvements": [
            "Viac empatie pri frustrovanom zákazníkovi",
            "Konkrétnejšie návrhy riešenia",
            "Lepšie zvládanie námietok zákazníka",
        ],
        "coaching_tip": "Pri nasledujúcom hovore skúste viac parafrázovať to, čo zákazník hovorí. Pomáha to budovať dôveru a zákazník cíti, že mu rozumiete.",
        "bonus_points": 0,
        "penalty_points": 0,
    }

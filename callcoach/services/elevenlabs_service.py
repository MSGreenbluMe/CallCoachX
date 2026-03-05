import requests
import json
from config import ELEVENLABS_API_KEY


ELEVENLABS_BASE_URL = "https://api.elevenlabs.io/v1"


def create_agent(scenario):
    """Create an ElevenLabs Conversational AI agent for a scenario."""
    if not ELEVENLABS_API_KEY:
        return None

    headers = {
        "xi-api-key": ELEVENLABS_API_KEY,
        "Content-Type": "application/json",
    }

    payload = {
        "name": f"CallCoach - {scenario['name']}",
        "conversation_config": {
            "agent": {
                "prompt": {
                    "prompt": scenario.get("system_prompt", ""),
                    "temperature": scenario.get("temperature", 0.7),
                },
                "first_message": scenario.get("first_message", ""),
                "language": scenario.get("language", "cs"),
            },
            "tts": {
                "voice_id": scenario.get("voice_id", ""),
            },
        },
    }

    try:
        resp = requests.post(
            f"{ELEVENLABS_BASE_URL}/convai/agents/create",
            headers=headers,
            json=payload,
            timeout=30,
        )
        resp.raise_for_status()
        return resp.json().get("agent_id")
    except Exception as e:
        print(f"ElevenLabs agent creation error: {e}")
        return None


def get_signed_url(agent_id):
    """Get a signed URL to start a conversation with an agent."""
    if not ELEVENLABS_API_KEY:
        return None

    headers = {"xi-api-key": ELEVENLABS_API_KEY}

    try:
        resp = requests.get(
            f"{ELEVENLABS_BASE_URL}/convai/conversation/get_signed_url",
            headers=headers,
            params={"agent_id": agent_id},
            timeout=15,
        )
        resp.raise_for_status()
        return resp.json().get("signed_url")
    except Exception as e:
        print(f"ElevenLabs signed URL error: {e}")
        return None


def get_conversation_transcript(conversation_id):
    """Retrieve the transcript after a conversation ends."""
    if not ELEVENLABS_API_KEY:
        return None

    headers = {"xi-api-key": ELEVENLABS_API_KEY}

    try:
        resp = requests.get(
            f"{ELEVENLABS_BASE_URL}/convai/conversations/{conversation_id}",
            headers=headers,
            timeout=15,
        )
        resp.raise_for_status()
        data = resp.json()
        return data.get("transcript", [])
    except Exception as e:
        print(f"ElevenLabs transcript error: {e}")
        return None


def generate_system_prompt(scenario):
    """Generate the customer persona system prompt from scenario data."""
    mood_descriptions = {
        "CALM": "Si pokojný/á a vecný/á.",
        "FRUSTRATED": "Si frustrovaný/á a potrebuješ rýchle riešenie.",
        "ANGRY": "Si nahnevaný/á a chceš okamžité riešenie. Zvyšuješ hlas.",
        "CONFUSED": "Si zmätený/á a nerozumieš čo sa deje. Potrebuješ trpezlivé vysvetlenie.",
        "IMPATIENT": "Si netrpezlivý/á, nemáš čas a chceš to vyriešiť čo najrýchlejšie.",
        "FRIENDLY": "Si priateľský/á a ochotný/á spolupracovať.",
    }

    mood_desc = mood_descriptions.get(scenario.get("persona_mood", "CALM"), "")

    prompt = f"""Si zákazník menom {scenario.get('persona_name', 'Zákazník')}.

TVOJ PRÍBEH: {scenario.get('persona_background', '')}

TVOJA NÁLADA: {mood_desc}
TVOJA TRPEZLIVOSŤ: {scenario.get('persona_patience', 5)}/10

TVOJ KOMUNIKAČNÝ ŠTÝL: {scenario.get('persona_comm_style', '')}

TVOJA SKRYTÁ POTREBA: {scenario.get('persona_hidden_need', '')}

PRAVIDLÁ:
- Správaj sa ako skutočný zákazník, nie ako AI
- Reaguj emocionálne podľa svojej nálady
- Ak agent prejaví empatiu, tvoja nálada sa môže zlepšiť
- Ak agent ignoruje tvoje pocity alebo je neosobný, tvoja nálada sa zhorší
- Ak tvoja trpezlivosť klesne na 0, žiadaj vedúceho alebo zaves
- Nikdy neprezraď svoju skrytú potrebu priamo — agent ju musí odhaliť otázkami
- Odpovedaj v jazyku {scenario.get('language', 'cs')}
- Hovor prirodzene, s prípadnými "hm", pauzami, prerušeniami

KONTEXT HOVORU: {scenario.get('description', '')}"""

    return prompt

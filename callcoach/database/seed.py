import json
from database.db import get_connection, query


def seed_achievements():
    existing = query("SELECT COUNT(*) as cnt FROM achievements")
    if existing[0]["cnt"] > 0:
        return

    achievements = [
        ("Prvý hovor", "Dokončiť prvý tréningový hovor", "🎯", "first_call", "1", "milestone"),
        ("Perfekcionista", "Získať 100% na ľubovoľnom scenári", "⭐", "perfect_score", "100", "skill"),
        ("Streak Master", "5 po sebe idúcich dní tréning", "🔥", "streak", "5", "consistency"),
        ("Empat roka", "Priemer empatie > 9.0 (min 10 hovorov)", "💚", "avg_empathy", "9.0", "skill"),
        ("Speed Demon", "Dokončiť scenár pod 50% odhadovaného času s >80%", "⚡", "speed_quality", "50", "skill"),
        ("Polyglot", "Dokončiť scenáre v 3 rôznych jazykoch", "🌍", "languages", "3", "milestone"),
        ("Kategória komplet", "Dokončiť všetky scenáre v jednej kategórii", "🏆", "category_complete", "1", "milestone"),
        ("Záchranár", "Zmeniť ANGRY zákazníka na spokojného", "🛟", "angry_rescue", "1", "skill"),
        ("Sales Shark", "5x úspešný upsell", "🦈", "upsell_count", "5", "skill"),
        ("Iron Man", "10 hovorov v jednom dni", "💪", "daily_calls", "10", "consistency"),
        ("Comeback Kid", "Po neúspešnom hovore hneď úspešný na tom istom scenári", "🔄", "comeback", "1", "skill"),
    ]

    conn = get_connection()
    cursor = conn.cursor()
    cursor.executemany(
        "INSERT INTO achievements (name, description, icon, condition_type, condition_value, category) VALUES (?,?,?,?,?,?)",
        achievements,
    )
    conn.commit()
    conn.close()


def seed_scenarios():
    existing = query("SELECT COUNT(*) as cnt FROM scenarios")
    if existing[0]["cnt"] > 0:
        return

    conn = get_connection()
    cursor = conn.cursor()

    # Scenario 1: Reklamácia — E-shop
    cursor.execute("""
        INSERT INTO scenarios (name, description, category, difficulty, language, estimated_duration_min, max_duration_min,
            persona_name, persona_background, persona_mood, persona_patience, persona_comm_style, persona_hidden_need,
            primary_goal, success_definition, fail_conditions, first_message, temperature,
            evaluation_weights, is_active)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        "Reklamácia poškodeného tovaru",
        "Zákazníčka Jana Nováková volá ohľadom reklamácie práčky, ktorú si kúpila pred 14 dňami. Práčka nefunguje správne — odstreďovanie nepracuje. Je frustrovaná, pretože sa na práčku spoliehala.",
        "COMPLAINTS", 2, "cs", 8, 15,
        "Jana Nováková",
        "45 rokov, učiteľka na základnej škole. Kúpila si práčku Samsung pred 14 dňami v e-shope. Odstreďovanie nefunguje, prádlo je po praní úplne mokré. Už volala raz, ale nikto sa neozval.",
        "FRUSTRATED", 5,
        "Hovorí pomerne rýchlo, občas sa opakuje. Keď je frustrovaná, zvýši hlas. Chce jasné odpovede, nemá rada vyhýbavé reči.",
        "V skutočnosti nechce čakať na opravu — chce rýchle riešenie, ideálne výmenu za novší model alebo vrátenie peňazí.",
        "Vyriešiť reklamáciu a ponúknuť výmenu za vyšší model",
        "Zákazníčka súhlasí s výmenou alebo vrátením a je spokojná s riešením",
        "Zákazníčka žiada vedúceho alebo zavesí nahnevaná",
        "Dobrý deň, volám ohľadom reklamácie. Pred dvoma týždňami som si u vás kúpila práčku a vôbec nefunguje to odstreďovanie!",
        0.7,
        json.dumps({"weight_general": 0.35, "weight_checkpoints": 0.35, "weight_goal": 0.30}),
        1,
    ))
    scenario1_id = cursor.lastrowid

    checkpoints_1 = [
        (scenario1_id, "Pozdrav a predstavenie sa", "Agent sa profesionálne pozdraví a predstaví", 1, 1, "Hľadaj pozdrav a predstavenie sa menom/firmou"),
        (scenario1_id, "Overenie identity zákazníka", "Agent overí meno a číslo objednávky", 2, 1, "Hľadaj otázku na meno, email alebo číslo objednávky"),
        (scenario1_id, "Aktívne vypočutie problému", "Agent nechá zákazníčku vysvetliť problém bez prerušovania", 3, 1, "Hľadaj trpezlivé počúvanie, parafrázovanie problému"),
        (scenario1_id, "Empatické vyjadrenie porozumenia", "Agent prejaví empatiu a pochopenie frustrácie", 4, 1, "Hľadaj vyjadrenie pochopenia, ospravedlnenie za problémy"),
        (scenario1_id, "Zistenie detailov problému", "Agent sa opýta na konkrétne detaily (model, kedy sa to stalo)", 5, 0, "Hľadaj diagnostické otázky o probléme"),
        (scenario1_id, "Navrhnutie riešenia", "Agent ponúkne konkrétne riešenie (výmena, vrátenie)", 6, 1, "Hľadaj ponuku riešenia — výmena, oprava, vrátenie peňazí"),
        (scenario1_id, "Potvrdenie súhlasu zákazníka", "Agent sa uistí, že zákazníčka súhlasí s navrhnutým riešením", 7, 1, "Hľadaj overenie súhlasu zákazníčky"),
        (scenario1_id, "Zhrnutie dohodnutých krokov", "Agent zhrnie čo sa dohodlo a aké budú ďalšie kroky", 8, 1, "Hľadaj zhrnutie dohodnutých krokov, termíny"),
        (scenario1_id, "Profesionálne rozlúčenie", "Agent sa profesionálne rozlúči", 9, 1, "Hľadaj rozlúčenie a poďakovanie"),
    ]

    # Scenario 2: Retencia — Telko
    cursor.execute("""
        INSERT INTO scenarios (name, description, category, difficulty, language, estimated_duration_min, max_duration_min,
            persona_name, persona_background, persona_mood, persona_patience, persona_comm_style, persona_hidden_need,
            primary_goal, success_definition, fail_conditions, first_message, temperature,
            evaluation_weights, is_active)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        "Retencia — zákazník chce odísť",
        "Martin Horák, 32-ročný programátor, volá že chce zrušiť svoju zmluvu u telekomunikačného operátora. Našiel lacnejšiu ponuku u konkurencie. Je pokojný, ale rozhodnutý.",
        "RETENTION", 4, "cs", 10, 15,
        "Martin Horák",
        "32 rokov, programátor. Zákazník už 3 roky. Má tarif za 599 Kč/mesiac (neobmedzené volania, 5 GB dát). Konkurencia mu ponúkla to isté za 399 Kč + 10 GB dát.",
        "CALM", 7,
        "Hovorí vecne a stručne. Má rád fakty a čísla. Nemá rád emotívne presviedčanie. Rozhoduje sa racionálne.",
        "Nechce naozaj rušiť zmluvu — chce lepšiu cenu a hlavne rýchlejší internet pre prácu z domu.",
        "Udržať zákazníka ponukou lepšieho tarifu",
        "Zákazník súhlasí s novým tarifom a zostáva",
        "Zákazník trvá na zrušení a žiada poslanie výpovedného formulára",
        "Dobrý deň, volám protože chcem zrušiť svoju zmluvu. Našiel som si lepšiu ponuku inde.",
        0.7,
        json.dumps({"weight_general": 0.35, "weight_checkpoints": 0.35, "weight_goal": 0.30}),
        1,
    ))
    scenario2_id = cursor.lastrowid

    checkpoints_2 = [
        (scenario2_id, "Pozdrav a predstavenie", "Agent sa profesionálne pozdraví", 1, 1, "Hľadaj pozdrav a predstavenie"),
        (scenario2_id, "Overenie identity", "Agent overí totožnosť zákazníka", 2, 1, "Hľadaj overenie mena, čísla zmluvy"),
        (scenario2_id, "Zistenie dôvodu odchodu", "Agent sa spýta prečo chce odísť", 3, 1, "Hľadaj otázku na dôvod zrušenia"),
        (scenario2_id, "Empatia a pochopenie", "Agent prejaví pochopenie rozhodnutia", 4, 1, "Hľadaj vyjadrenie pochopenia, nie presviedčanie"),
        (scenario2_id, "Protiponuka", "Agent ponúkne lepší tarif", 5, 1, "Hľadaj konkrétnu ponuku lepšieho tarifu"),
        (scenario2_id, "Zvládnutie námietok", "Agent reaguje na námietky zákazníka", 6, 0, "Hľadaj reakcie na odpor alebo porovnanie s konkurenciou"),
        (scenario2_id, "Dohodnutie podmienok", "Agent dohodne konkrétne podmienky nového tarifu", 7, 1, "Hľadaj dohodnutie ceny, podmienok, termínu"),
        (scenario2_id, "Zhrnutie a ďalšie kroky", "Agent zhrnie dohodnuté", 8, 1, "Hľadaj zhrnutie dohody"),
        (scenario2_id, "Rozlúčenie", "Profesionálne rozlúčenie", 9, 1, "Hľadaj rozlúčenie"),
    ]

    # Scenario 3: Tech Support
    cursor.execute("""
        INSERT INTO scenarios (name, description, category, difficulty, language, estimated_duration_min, max_duration_min,
            persona_name, persona_background, persona_mood, persona_patience, persona_comm_style, persona_hidden_need,
            primary_goal, success_definition, fail_conditions, first_message, temperature,
            evaluation_weights, is_active)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        "Tech Support — problém s prihlásením",
        "Eva Malá, 58-ročná účtovníčka, nedokáže sa prihlásiť do firemnej aplikácie. Je zmätená a nervózna, pretože potrebuje urobiť mesačnú uzávierku do zajtra.",
        "TECH_SUPPORT", 3, "cs", 7, 12,
        "Eva Malá",
        "58 rokov, účtovníčka v malej firme. Používa firemný software na účtovníctvo. Včera jej vypršalo heslo a systém ju nepustí ďalej. Zajtra je deadline na mesačnú uzávierku.",
        "CONFUSED", 6,
        "Hovorí pomaly, často sa pýta či rozumie správne. Používa neodborné výrazy pre technické veci. Potrebuje všetko vysvetliť krok za krokom.",
        "Má strach z technológií a bojí sa, že niečo pokazí. Potrebuje trpezlivé vysvetlenie a uistenie, že to zvládne.",
        "Vyriešiť problém s prihlásením a naučiť zákazníčku postup na reset hesla",
        "Zákazníčka sa úspešne prihlási a vie si v budúcnosti resetovať heslo sama",
        "Zákazníčka je úplne stratená a žiada aby sa niekto pripojil na jej počítač",
        "Dobrý deň, ja neviem čo sa deje, ale nemôžem sa dostať do toho nášho programu. Píše mi to niečo o hesle...",
        0.7,
        json.dumps({"weight_general": 0.35, "weight_checkpoints": 0.35, "weight_goal": 0.30}),
        1,
    ))
    scenario3_id = cursor.lastrowid

    checkpoints_3 = [
        (scenario3_id, "Pozdrav a upokojenie", "Agent sa pozdraví a uistí zákazníčku, že jej pomôže", 1, 1, "Hľadaj pozdrav a upokojujúce vyjadrenie"),
        (scenario3_id, "Overenie identity", "Agent overí meno a prístup zákazníčky", 2, 1, "Hľadaj overenie identity"),
        (scenario3_id, "Pochopenie problému", "Agent sa spýta čo presne vidí na obrazovke", 3, 1, "Hľadaj otázky na to čo zákazníčka vidí"),
        (scenario3_id, "Upokojenie a empatia", "Agent uistí zákazníčku že problém sa dá vyriešiť", 4, 1, "Hľadaj upokojenie, uistenie že to nie je vážne"),
        (scenario3_id, "Krokový návod na reset hesla", "Agent krok za krokom vysvetlí postup", 5, 1, "Hľadaj postupné inštrukcie, číslovanie krokov"),
        (scenario3_id, "Overenie funkčnosti", "Agent overí že nové heslo funguje", 6, 1, "Hľadaj overenie či sa zákazníčka prihlásila"),
        (scenario3_id, "Zhrnutie postupu", "Agent zhrnie postup pre budúcnosť", 7, 1, "Hľadaj zhrnutie ako si resetovať heslo v budúcnosti"),
        (scenario3_id, "Rozlúčenie", "Profesionálne rozlúčenie s ponukou ďalšej pomoci", 8, 1, "Hľadaj rozlúčenie"),
    ]

    cursor.executemany(
        "INSERT INTO checkpoints (scenario_id, name, description, order_index, is_order_strict, detection_hint) VALUES (?,?,?,?,?,?)",
        checkpoints_1 + checkpoints_2 + checkpoints_3,
    )

    conn.commit()
    conn.close()


def seed_demo_users():
    existing = query("SELECT COUNT(*) as cnt FROM users")
    if existing[0]["cnt"] > 0:
        return

    conn = get_connection()
    cursor = conn.cursor()

    users = [
        ("Michal Kováč", "michal@demo.cz", "agent", "Team Alpha", 1450, 4, 5),
        ("Petra Svobodová", "petra@demo.cz", "agent", "Team Alpha", 2800, 5, 3),
        ("Tomáš Novák", "tomas@demo.cz", "agent", "Team Alpha", 850, 3, 1),
        ("Jana Marková", "jana@demo.cz", "agent", "Team Beta", 3500, 6, 7),
        ("Martin Dvořák", "martin@demo.cz", "agent", "Team Beta", 600, 3, 0),
        ("Eva Černá", "eva@demo.cz", "agent", "Team Beta", 1100, 4, 2),
        ("Alex Jensen", "alex@demo.cz", "manager", "Team Alpha", 0, 1, 0),
        ("Admin User", "admin@demo.cz", "admin", None, 0, 1, 0),
    ]

    cursor.executemany(
        "INSERT INTO users (name, email, role, team, xp, level, streak_days) VALUES (?,?,?,?,?,?,?)",
        users,
    )
    conn.commit()
    conn.close()


def seed_demo_sessions():
    """Create demo sessions with evaluations for dashboard data."""
    existing = query("SELECT COUNT(*) as cnt FROM sessions")
    if existing[0]["cnt"] > 0:
        return

    import random
    from datetime import datetime, timedelta

    conn = get_connection()
    cursor = conn.cursor()

    agents = query("SELECT id FROM users WHERE role = 'agent'")
    scenarios = query("SELECT id, difficulty FROM scenarios")

    if not agents or not scenarios:
        conn.close()
        return

    now = datetime.now()

    for agent in agents:
        num_sessions = random.randint(5, 15)
        for i in range(num_sessions):
            scenario = random.choice(scenarios)
            days_ago = random.randint(0, 30)
            started = now - timedelta(days=days_ago, hours=random.randint(0, 8))
            duration = random.randint(180, 600)
            ended = started + timedelta(seconds=duration)

            cursor.execute("""
                INSERT INTO sessions (user_id, scenario_id, started_at, ended_at, duration_seconds, status)
                VALUES (?, ?, ?, ?, ?, 'completed')
            """, (agent["id"], scenario["id"], started.isoformat(), ended.isoformat(), duration))
            session_id = cursor.lastrowid

            base_score = random.uniform(55, 95)
            scores = {
                "communication_clarity": min(10, max(1, base_score / 10 + random.uniform(-1.5, 1.5))),
                "empathy_rapport": min(10, max(1, base_score / 10 + random.uniform(-1.5, 1.5))),
                "active_listening": min(10, max(1, base_score / 10 + random.uniform(-1.5, 1.5))),
                "professional_language": min(10, max(1, base_score / 10 + random.uniform(-1.5, 1.5))),
                "call_structure": min(10, max(1, base_score / 10 + random.uniform(-1.5, 1.5))),
                "call_control": min(10, max(1, base_score / 10 + random.uniform(-1.5, 1.5))),
                "objection_handling": min(10, max(1, base_score / 10 + random.uniform(-1.5, 1.5))),
            }

            overall = round(base_score + random.uniform(-5, 5), 1)
            goal = random.choice(["ACHIEVED", "PARTIAL", "FAILED"])
            if overall > 80:
                goal = "ACHIEVED"
            elif overall < 50:
                goal = "FAILED"

            strengths = json.dumps(["Dobrá komunikácia", "Empatický prístup", "Jasná štruktúra"])
            improvements = json.dumps(["Lepšie zvládanie námietok", "Viac diagnostických otázok"])

            cursor.execute("""
                INSERT INTO evaluations (session_id, overall_score,
                    communication_clarity, empathy_rapport, active_listening,
                    professional_language, call_structure, call_control, objection_handling,
                    goal_achieved, summary, strengths, improvements, coaching_tip, evaluated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                session_id, overall,
                round(scores["communication_clarity"], 1),
                round(scores["empathy_rapport"], 1),
                round(scores["active_listening"], 1),
                round(scores["professional_language"], 1),
                round(scores["call_structure"], 1),
                round(scores["call_control"], 1),
                round(scores["objection_handling"], 1),
                goal,
                "Hovor prebehol celkovo dobre, agent prejavil profesionálny prístup.",
                strengths, improvements,
                "Skúste viac parafrázovať to, čo zákazník hovorí, aby cítil, že mu rozumiete.",
                ended.isoformat(),
            ))

    conn.commit()
    conn.close()


def run_all_seeds():
    seed_demo_users()
    seed_achievements()
    seed_scenarios()
    seed_demo_sessions()

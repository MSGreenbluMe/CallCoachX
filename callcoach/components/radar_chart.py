import plotly.graph_objects as go


SKILL_LABELS = {
    "communication_clarity": "Komunikácia",
    "empathy_rapport": "Empatia",
    "active_listening": "Aktívne počúvanie",
    "professional_language": "Profesionálny jazyk",
    "call_structure": "Štruktúra hovoru",
    "call_control": "Riadenie hovoru",
    "objection_handling": "Zvládanie námietok",
}


def create_radar_chart(scores, title="Prehľad zručností", height=400):
    categories = list(SKILL_LABELS.values())
    values = [
        scores.get(k, 5) for k in SKILL_LABELS.keys()
    ]
    # Close the polygon
    categories.append(categories[0])
    values.append(values[0])

    fig = go.Figure()

    fig.add_trace(go.Scatterpolar(
        r=values,
        theta=categories,
        fill="toself",
        fillcolor="rgba(19, 127, 236, 0.15)",
        line=dict(color="#137fec", width=2),
        marker=dict(size=6, color="#137fec"),
        name="Skóre",
    ))

    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 10],
                tickvals=[2, 4, 6, 8, 10],
                ticktext=["2", "4", "6", "8", "10"],
                gridcolor="#e5e7eb",
                linecolor="#e5e7eb",
            ),
            angularaxis=dict(
                gridcolor="#e5e7eb",
                linecolor="#e5e7eb",
            ),
            bgcolor="white",
        ),
        showlegend=False,
        title=dict(text=title, font=dict(size=16, color="#1e293b")),
        height=height,
        margin=dict(l=60, r=60, t=60, b=40),
        paper_bgcolor="white",
        font=dict(family="Inter, sans-serif"),
    )

    return fig


def create_comparison_radar(scores1, scores2, label1="Agent", label2="Tímový priemer", height=400):
    categories = list(SKILL_LABELS.values())
    values1 = [scores1.get(k, 5) for k in SKILL_LABELS.keys()]
    values2 = [scores2.get(k, 5) for k in SKILL_LABELS.keys()]

    categories.append(categories[0])
    values1.append(values1[0])
    values2.append(values2[0])

    fig = go.Figure()

    fig.add_trace(go.Scatterpolar(
        r=values1,
        theta=categories,
        fill="toself",
        fillcolor="rgba(19, 127, 236, 0.15)",
        line=dict(color="#137fec", width=2),
        name=label1,
    ))

    fig.add_trace(go.Scatterpolar(
        r=values2,
        theta=categories,
        fill="toself",
        fillcolor="rgba(139, 92, 246, 0.1)",
        line=dict(color="#8b5cf6", width=2, dash="dash"),
        name=label2,
    ))

    fig.update_layout(
        polar=dict(
            radialaxis=dict(visible=True, range=[0, 10], gridcolor="#e5e7eb"),
            angularaxis=dict(gridcolor="#e5e7eb"),
            bgcolor="white",
        ),
        showlegend=True,
        legend=dict(orientation="h", y=-0.1),
        height=height,
        margin=dict(l=60, r=60, t=40, b=60),
        paper_bgcolor="white",
        font=dict(family="Inter, sans-serif"),
    )

    return fig

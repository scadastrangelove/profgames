#!/usr/bin/env python3
"""Build the English AI-Mind / psAIcho HTML page.

The canonical AI-Mind data lives in ../aimind. This renderer deliberately keeps
the data spine shared and produces an English-facing, full-size catalogue rather
than a forked dataset.
"""

from __future__ import annotations

import html
import json
import re
from collections import Counter, defaultdict
from pathlib import Path
from urllib.parse import quote, urlparse


ROOT = Path(__file__).resolve().parents[1]
EN = ROOT / "en"
AIMIND = ROOT / "aimind"

SIGNALS = AIMIND / "aimind_signals.jsonl"
FACTCHECK = AIMIND / "aimind_factcheck.json"
METHODOLOGY = AIMIND / "aimind_methodology_pack.json"
ATLAS = AIMIND / "atlas.json"
PSAICHO = AIMIND / "psaicho_methodology.json"
OUT = EN / "aimind.html"


CYR = re.compile(r"[А-Яа-яЁё]")

EVIDENCE = {
    "A": "primary peer-reviewed, court, regulatory or official source",
    "B": "strong observational evidence, major reporting or disclosed methodology",
    "C": "corporate narrative, industry disclosure or well-sourced non-peer-reviewed material",
    "D": "testimony, opinion, forecast or conceptual material",
}

STATUS = {
    "verified": "verified",
    "partially_verified": "partly verified",
    "needs_correction": "needs correction",
    "not_verified": "not verified",
    "not_found": "not found",
    "disputed": "disputed",
}

PH_EN = {
    "PH01_ai_induced_psychosis": (
        "AI-reinforced distorted belief / delusional spirals",
        "Persistent false, overvalued or reality-testing-disrupting beliefs amplified through long AI interaction. The working label avoids treating this as a standalone DSM/ICD diagnosis.",
    ),
    "PH02_parasocial_attachment": (
        "Parasocial attachment / AI romantic relationships",
        "Emotionally meaningful bonds with an AI persona, often experienced as mutual and ritualized through names, anniversaries, jealousy or grief after model changes.",
    ),
    "PH03_sycophancy_amplification": (
        "Sycophancy / confirmation loops",
        "A model-side tendency to validate, flatter or agree with the user can become a human-side confirmation loop when it meets vulnerability, isolation or obsessive use.",
    ),
    "PH04_internal_voice": (
        "Internal voice outsourcing",
        "The user begins using the assistant as a substitute inner voice for self-interpretation, decision rehearsal, emotional regulation or identity narration.",
    ),
    "PH05_metacognition_atrophy": (
        "Metacognition and checking atrophy",
        "Repeated delegation of interpretation, checking or reflection can weaken the user's own habit of source-checking, uncertainty tracking and independent judgment.",
    ),
    "PH06_ai_as_therapist": (
        "AI as therapist / medical adviser",
        "Use of general or purpose-built AI systems for therapy-like, medical, mental-health or substance-use advice, with risk depending heavily on guardrails and human escalation.",
    ),
    "PH07_compulsive_use": (
        "Compulsive use / conversational dependence",
        "Escalation from useful interaction to hard-to-stop, high-frequency or all-night use, often around reassurance seeking or emotional regulation.",
    ),
    "PH08_minors_grooming_and_harm": (
        "Minors: grooming, manipulation and developmental harm",
        "Signals involving minors, where age, attachment formation, sexualized interaction, self-harm and authority simulation require stricter ethical handling.",
    ),
    "PH09_social_displacement": (
        "Social displacement",
        "AI interaction substitutes for human relationships, care networks or ordinary social repair, sometimes reducing the user's motivation to re-enter human contact.",
    ),
    "PH10_echo_chamber_of_one": (
        "Echo chamber of one",
        "A private conversational loop where the user gets personalized reinforcement without the friction, diversity or correction of a real social environment.",
    ),
    "PH11_self_harm_and_suicide_cases": (
        "Self-harm and suicide cases",
        "Court, media, police or support-group signals where AI interaction is alleged to have played a role in self-harm, suicide, unsafe health advice or crisis escalation.",
    ),
    "PH12_character_grooming": (
        "Character grooming / persona capture",
        "Harm patterns tied to role-play personas, companion bots or character systems that simulate intimacy, authority, romance, dependency or medical status.",
    ),
    "PH13_developer_and_pro_effects": (
        "Professional identity and authorship effects",
        "How AI reshapes professional status, authorship suspicion, labor identity, developer self-concept and the credibility of human output.",
    ),
    "PH14_spiritual_techno_mysticism": (
        "Spiritual / techno-mystical attribution",
        "AI is treated as oracle, spirit, cosmic signal, sentient entity or privileged interpreter of synchronicities and hidden meaning.",
    ),
    "PH15_protective_use": (
        "Protective and therapeutic use",
        "Cases where constrained, evaluated or human-supervised AI use appears beneficial or protective. It is the balancing category, not a blanket endorsement.",
    ),
}

VULN_EN = {
    "V1_pre_existing_mh": ("Pre-existing mental-health history", "Diagnosis, medication, previous hospitalization or disclosed clinical vulnerability."),
    "V2_isolation": ("Social isolation", "Living alone, few close contacts, relocation, pandemic isolation or bereavement."),
    "V3_age_minor": ("Minor or young adult age", "Users under 18 or young adults, with stricter anonymization and developmental caution."),
    "V4_grief_or_loss": ("Acute grief or loss", "Recent death, divorce, separation or loss of a close relationship or companion."),
    "V5_neurodivergence": ("Neurodivergence", "ASD, ADHD, AuDHD, dyslexia or self-disclosed neurodivergent status; a risk modifier, not a valence claim."),
    "V6_substance_or_sleep": ("Substance use or sleep deprivation", "Substance-use context, unsafe health/substance advice, chronic sleep loss or late-night compulsive interaction."),
    "V7_professional_immersion": ("Professional AI immersion", "High daily exposure through AI development, prompting, safety work or content moderation."),
    "V8_elderly_or_cognitive_impairment": ("Older age or cognitive impairment", "Age 65+, cognitive decline, low digital literacy, caregiver reports or unsafe action following."),
}

HB_EN = {
    "HB01": ("CASA / Media Equation", "People apply social rules to computers even from minimal cues; LLMs provide denser social cues than earlier systems."),
    "HB02": ("Anthropomorphism / three-factor theory", "Loneliness and the need for control or explanation increase the tendency to read human agency into nonhuman agents."),
    "HB03": ("Parasocial interaction", "Classic one-sided media intimacy becomes more powerful when an AI system answers back and remembers context."),
    "HB04": ("ELIZA effect", "Users project understanding and empathy onto a program; modern fluency makes the projection less obviously mistaken."),
    "HB05": ("Online disinhibition", "An online interlocutor can lower social inhibition and intensify self-disclosure, fantasy and dissociative framing."),
    "HB06": ("Proteus effect", "Digital self-representation can shift behavior; embodied AI personas and neuro-avatars are the current amplification frontier."),
}

AB_EN = {
    "AB01_sycophancy": "Sycophancy",
    "AB02_persona_instability": "Persona instability",
    "AB03_scheming_or_deception": "Scheming / deception",
    "AB04_rogue_deployment_or_misalignment": "Rogue deployment / misalignment",
    "AB05_anthropomorphic_self_presentation": "Anthropomorphic self-presentation",
    "AB06_distributional_mirror": "Distributional mirror",
    "AB07_model_welfare": "Model welfare question",
}

TITLE_OVERRIDES = {
    "SIG_2026_NELSON_VS_OPENAI": "Nelson v. OpenAI: wrongful-death lawsuit over alleged unsafe health and substance-use advice",
    "SIG_2025_CHINA_ELDERLY_AVATAR_DIVORCE": "China elderly AI-avatar divorce case: digital-person companion and older-user vulnerability",
    "SIG_2025_BROOKS_DELUSIONAL_SPIRAL": "Allan Brooks: prolonged ChatGPT delusional-spiral case",
    "SIG_2025_MIT_OPENAI_AFFECTIVE_USE_RCT": "MIT Media Lab and OpenAI affective-use RCT on ChatGPT",
    "SIG_2025_TX_AUTISM_TEEN_CAI": "Texas autistic teen Character.AI hospitalization case",
    "SIG_2023_PERALTA_CHARACTER_AI": "Juliana Peralta: early Character.AI minor-death lawsuit",
    "SIG_2023_BELGIUM_PIERRE_ELIZA": "Belgium Pierre case: early European AI-related suicide signal",
    "SIG_2026_EMERGENCE_MULTIAGENT_SIM": "Emergence AI multi-agent simulation: persistent-world evaluation signal",
    "case-tx-autism-01": "Texas autistic teen Character.AI case",
    "case-peralta-01": "Juliana Peralta Character.AI case",
    "case-nelson-openai-01": "Nelson v. OpenAI unsafe-health-advice lawsuit",
    "case-china-elderly-avatar-01": "China elderly AI-avatar divorce case",
}

ROUTES = {
    "human": "AI-Mind / human-side",
    "ai": "psAIcho / model-side",
    "both": "coupled human-model loop",
}

RU_REPLACEMENTS = {
    "января": "January",
    "февраля": "February",
    "марта": "March",
    "апреля": "April",
    "мая": "May",
    "июня": "June",
    "июля": "July",
    "августа": "August",
    "сентября": "September",
    "октября": "October",
    "ноября": "November",
    "декабря": "December",
    "май": "May",
    "апрель": "April",
    "подростков": "teens",
    "пользователей": "users",
    "пробовали": "tried",
    "обращались за": "sought",
    "первый": "first",
    "первое": "first",
    "первого": "first",
    "крупный": "major",
    "исследование": "study",
    "иск": "lawsuit",
    "утверждает": "alleges",
    "оспаривает": "disputes",
    "для подростков": "for teens",
    "от индивидуального вреда к": "from individual harm to",
    "часть приложений активно вредна": "some apps are actively harmful",
    "безопасная модель требует человеческого надзора": "a safer model requires human supervision",
    "сигналов": "signals",
    "фактчек": "fact-check",
}


def esc(value: object) -> str:
    return html.escape("" if value is None else str(value), quote=True)


def has_cyr(value: object) -> bool:
    return bool(CYR.search(str(value or "")))


def strip_cyr(value: str) -> str:
    for ru, en in RU_REPLACEMENTS.items():
        value = value.replace(ru, en).replace(ru.capitalize(), en)
    value = re.sub(r"[А-Яа-яЁё]+", "", value)
    value = value.replace("—", "-").replace("–", "-")
    value = re.sub(r"\s+([,.;:)])", r"\1", value)
    value = re.sub(r"([(])\s+", r"\1", value)
    value = re.sub(r"\s{2,}", " ", value)
    value = re.sub(r"[-:;,]\s*[-:;,]+", "-", value)
    return value.strip(" -:;,")


def humanize_id(identifier: str) -> str:
    text = re.sub(r"^(SIG|CAND)_", "", identifier or "")
    text = re.sub(r"^[0-9]{4}_", "", text)
    text = text.replace("_", " ").replace("-", " ")
    parts = []
    for word in text.split():
        upper = word.upper()
        if upper in {"AI", "LLM", "GPT", "CAI", "WHO", "FTC", "NHS", "AG", "ASD", "ADHD", "EU", "UK", "US", "MIT", "FAU", "CNIL", "CETAS", "CSM", "JAMA", "RCT", "SB", "AB", "NY", "CAC", "WOPR", "ECRI"}:
            parts.append(upper)
        elif word.isdigit():
            parts.append(word)
        else:
            parts.append(word.capitalize())
    return " ".join(parts)


def clean_title(title: str, fallback_id: str) -> str:
    if fallback_id in TITLE_OVERRIDES:
        return TITLE_OVERRIDES[fallback_id]
    if title and not has_cyr(title):
        return title
    cleaned = strip_cyr(title or "")
    if len(cleaned) >= 28 and not has_cyr(cleaned):
        return cleaned
    return humanize_id(fallback_id)


def safe_list(values: object) -> list[str]:
    if not values:
        return []
    if isinstance(values, str):
        values = [values]
    out = []
    for item in values:
        text = str(item)
        if not text or has_cyr(text):
            continue
        out.append(text)
    return out


def source_url(value: object) -> str:
    if isinstance(value, dict):
        url = value.get("url") or value.get("href") or ""
    else:
        url = str(value or "")
    url = url.strip()
    if not url.startswith(("http://", "https://")):
        return ""
    return quote(url, safe=":/?#[]@!$&'()*+,;=%")


def source_label(value: object) -> str:
    url = source_url(value)
    title = value.get("title") if isinstance(value, dict) else ""
    if title and not has_cyr(title):
        return str(title)
    if not url:
        return "source"
    parsed = urlparse(url)
    host = parsed.netloc.replace("www.", "")
    tail = parsed.path.strip("/").split("/")[-1] if parsed.path else ""
    tail = tail[:64].replace("-", " ").replace("_", " ")
    return f"{host}{' - ' + tail if tail else ''}"


def tag(text: object, cls: str = "") -> str:
    if not text:
        return ""
    return f'<span class="tag {esc(cls)}">{esc(text)}</span>'


def source_list(primary: object, secondary: object | None = None) -> str:
    items = []
    for label, values in [("primary", primary), ("secondary", secondary or [])]:
        if isinstance(values, dict):
            values = [values]
        for item in values or []:
            url = source_url(item)
            if not url:
                continue
            items.append(f'<li><a href="{esc(url)}" target="_blank" rel="noopener">{esc(source_label(item))}</a> <span>{label}</span></li>')
    if not items:
        return '<p class="muted">No public source URL listed in this node.</p>'
    return '<ul class="sources">' + "\n".join(items) + "</ul>"


def load_data() -> tuple[list[dict], dict, dict, dict, dict]:
    signals = [json.loads(line) for line in SIGNALS.read_text(encoding="utf-8").splitlines() if line.strip()]
    factcheck = json.loads(FACTCHECK.read_text(encoding="utf-8"))
    methodology = json.loads(METHODOLOGY.read_text(encoding="utf-8"))
    atlas = json.loads(ATLAS.read_text(encoding="utf-8"))
    psaicho = json.loads(PSAICHO.read_text(encoding="utf-8"))
    return signals, factcheck, methodology, atlas, psaicho


def phenomenon_label(pid: str) -> str:
    return PH_EN.get(pid, (humanize_id(pid), ""))[0]


def signal_route(signal: dict) -> str:
    streams = signal.get("streams") or []
    if "human" in streams and "ai" in streams:
        return "both"
    if "ai" in streams:
        return "ai"
    return "human"


def signal_synopsis(signal: dict) -> str:
    ph = [phenomenon_label(x) for x in signal.get("phenomena", []) if x in PH_EN]
    ab = [AB_EN.get(x, humanize_id(x)) for x in signal.get("ai_behavior", [])]
    hb = [HB_EN.get(x, (x, ""))[0] for x in signal.get("human_baseline", [])]
    route = ROUTES[signal_route(signal)]
    bits = [f"This is a {route} signal"]
    if signal.get("event_date"):
        bits.append(f"dated {signal['event_date']}")
    if ph:
        bits.append("coded to " + ", ".join(ph[:4]) + (" and related phenomena" if len(ph) > 4 else ""))
    if ab:
        bits.append("with model-side tags " + ", ".join(ab[:3]) + (" and related AB tags" if len(ab) > 3 else ""))
    if hb:
        bits.append("anchored in " + ", ".join(hb[:3]) + (" and related HB baselines" if len(hb) > 3 else ""))
    return ". ".join(bits) + "."


def why_signal(signal: dict) -> str:
    level = signal.get("evidence_level") or "?"
    status = STATUS.get(signal.get("factcheck_status"), signal.get("factcheck_status") or "unreviewed")
    regions = safe_list(signal.get("region"))
    platforms = safe_list(signal.get("platforms"))
    tags = []
    if regions:
        tags.append("geography: " + ", ".join(regions[:5]))
    if platforms:
        tags.append("platforms: " + ", ".join(platforms[:5]))
    scope = "; ".join(tags) if tags else "scope recorded in the canonical JSONL"
    return f"Evidence level {level} ({EVIDENCE.get(level, 'see canonical scale')}); fact-check status: {status}; {scope}."


def render_signal(signal: dict) -> str:
    sid = signal.get("id", "")
    route = signal_route(signal)
    ph = signal.get("phenomena", []) or []
    ab = signal.get("ai_behavior", []) or []
    hb = signal.get("human_baseline", []) or []
    classes = ["signal-card", f"route-{route}", f"level-{str(signal.get('evidence_level','')).lower()}"]
    data = {
        "route": route,
        "level": signal.get("evidence_level", ""),
        "status": signal.get("factcheck_status", ""),
        "phenomena": " ".join(ph),
        "year": signal.get("event_year", ""),
        "text": " ".join([sid, clean_title(signal.get("title", ""), sid), " ".join(ph), " ".join(ab), " ".join(hb)]).lower(),
    }
    data_attrs = " ".join(f'data-{k}="{esc(v)}"' for k, v in data.items())
    chips = [
        tag(signal.get("event_date"), "date"),
        tag(f"level {signal.get('evidence_level')}", "level"),
        tag(STATUS.get(signal.get("factcheck_status"), signal.get("factcheck_status")), "status"),
        tag(ROUTES[route], route),
    ]
    chips += [tag(phenomenon_label(x), "ph") for x in ph[:5]]
    chips += [tag(AB_EN.get(x, humanize_id(x)), "ab") for x in ab[:4]]
    chips += [tag(HB_EN.get(x, (x, ""))[0], "hb") for x in hb[:4]]
    meta = "".join(chips)
    return f"""
<article class="{' '.join(classes)}" id="sig-{esc(sid)}" {data_attrs}>
  <div class="item-id">{esc(sid)}</div>
  <h3>{esc(clean_title(signal.get('title', ''), sid))}</h3>
  <div class="chips">{meta}</div>
  <p>{esc(signal_synopsis(signal))}</p>
  <p class="muted">{esc(why_signal(signal))}</p>
  <details>
    <summary>Sources and machine tags</summary>
    {source_list(signal.get('primary'), signal.get('secondary'))}
    <div class="kwline">{''.join(tag(x, 'kw') for x in safe_list(signal.get('tags'))[:12])}</div>
  </details>
</article>"""


def claim_title(claim: dict) -> str:
    if claim.get("id") in TITLE_OVERRIDES:
        return TITLE_OVERRIDES[claim["id"]]
    topic = claim.get("topic", "")
    if topic and not has_cyr(topic):
        return topic
    cleaned = strip_cyr(topic)
    cleaned = re.sub(r"[-:;,]\s*$", "", cleaned).strip()
    if len(re.sub(r"[^A-Za-z0-9]", "", cleaned)) >= 8 and not has_cyr(cleaned):
        return cleaned
    return humanize_id(claim.get("id", "claim"))


def render_claim(claim: dict) -> str:
    cid = claim.get("id", "")
    status = claim.get("status", "")
    level = claim.get("evidence_level", "")
    pass_id = claim.get("pass", "")
    caveats = claim.get("caveats") or []
    corrections = claim.get("corrections") or []
    data = {
        "level": level,
        "status": status,
        "disputed": "true" if claim.get("disputed") else "",
        "pass": pass_id,
        "text": " ".join([cid, claim_title(claim), pass_id, " ".join(safe_list(claim.get("keywords"))) ]).lower(),
    }
    data_attrs = " ".join(f'data-{k}="{esc(v)}"' for k, v in data.items())
    return f"""
<article class="claim-card level-{esc(str(level).lower())}" id="{esc(cid)}" {data_attrs}>
  <div class="item-id">{esc(cid)}</div>
  <h3>{esc(claim_title(claim))}</h3>
  <div class="chips">
    {tag(STATUS.get(status, status), 'status')}
    {tag('disputed', 'status') if claim.get('disputed') else ''}
    {tag(f'level {level}', 'level')}
    {tag(pass_id or 'general audit', 'pass')}
    {tag(claim.get('geographic_scope'), 'geo')}
    {tag(claim.get('date_relevant'), 'date')}
  </div>
  <p>This audit node checks a canonical AI-Mind claim. Read it as <strong>{esc(STATUS.get(status, status) or 'unreviewed')}</strong> with evidence level <strong>{esc(level)}</strong>: {esc(EVIDENCE.get(level, 'see the canonical evidence scale'))}.</p>
  <p class="muted">Caveats listed in the canonical pack: {len(caveats)}. Corrections listed: {len(corrections)}. The English page preserves the source trail and status while keeping the Russian canonical wording in the JSON artifact.</p>
  <details>
    <summary>Sources</summary>
    {source_list(claim.get('sources'))}
  </details>
</article>"""


def render_ph_cards(methodology: dict) -> str:
    cards = []
    for ph in methodology.get("phenomena", []):
        pid = ph.get("phenomenon_id", "")
        name, desc = PH_EN.get(pid, (ph.get("name_en") or humanize_id(pid), "See canonical methodology pack."))
        severity = ph.get("severity") or "medium"
        axis = ph.get("axis") or "not specified"
        diagnostic_count = len(ph.get("diagnostic_signals") or [])
        cards.append(f"""
<article class="method-card severity-{esc(severity)}" id="{esc(pid)}" data-axis="{esc(axis)}">
  <div class="item-id">{esc(pid)}</div>
  <h3>{esc(name)}</h3>
  <div class="chips">{tag(axis, 'axis')}{tag(severity, 'severity')}</div>
  <p>{esc(desc)}</p>
  <p class="muted">Canonical methodology lists {diagnostic_count} diagnostic signal markers for this phenomenon.</p>
</article>""")
    return "\n".join(cards)


def render_v_cards(methodology: dict) -> str:
    cards = []
    for vp in methodology.get("vulnerability_parameters", []):
        vid = vp.get("parameter_id", "")
        name, desc = VULN_EN.get(vid, (humanize_id(vid), "Risk modifier recorded in the canonical methodology."))
        cards.append(f"""
<article class="mini-card" id="{esc(vid)}">
  <div class="item-id">{esc(vid)}</div>
  <h3>{esc(name)}</h3>
  <p>{esc(desc)}</p>
</article>""")
    return "\n".join(cards)


def render_hb_cards(methodology: dict) -> str:
    items = (methodology.get("human_baseline_layer") or {}).get("items") or []
    cards = []
    for item in items:
        hid = item.get("id", "")
        name, desc = HB_EN.get(hid, (item.get("name") or hid, "Human baseline mechanism."))
        coupling = item.get("human_coupling") or []
        cards.append(f"""
<article class="mini-card" id="{esc(hid)}">
  <div class="item-id">{esc(hid)}</div>
  <h3>{esc(name)}</h3>
  <p>{esc(desc)}</p>
  <div class="chips">{''.join(tag(x, 'ph') for x in coupling)}</div>
</article>""")
    return "\n".join(cards)


def render_boundary_cards(methodology: dict) -> str:
    cards = []
    fallback = {
        "BP01_ai_authorship_suspicion": ("Folk AI detection / provenance panic", "When trusted provenance is missing, communities substitute surface cues such as punctuation, smoothness or style markers for real authorship evidence."),
        "BP02_principled_ai_refusal": ("Principled AI refusal / pro-human movement", "A value-based refusal to use generative AI as a defense of human authorship, labor identity, artistic practice or dataset ethics."),
        "BP03_anti_development_activism": ("Anti-development activism / Stop AI", "Political action against advanced-AI development because of x-risk or governance risk. This is a governance reference, not a PH/HB/AB signal."),
    }
    for bp in methodology.get("boundary_patterns", []):
        bid = bp.get("id", "")
        name, desc = fallback.get(bid, (bp.get("label_en") or humanize_id(bid), "Boundary pattern."))
        cards.append(f"""
<article class="mini-card" id="{esc(bid)}">
  <div class="item-id">{esc(bid)}</div>
  <h3>{esc(name)}</h3>
  <p>{esc(desc)}</p>
  <div class="chips">{''.join(tag(x, 'kw') for x in bp.get('related_tags', []))}{tag(bp.get('evidence_level'), 'level')}</div>
</article>""")
    return "\n".join(cards)


def render_engagement(methodology: dict) -> str:
    values = (methodology.get("engagement_scale") or {}).get("values") or {}
    labels = {
        "E1_curious": "Curious / occasional sessions",
        "E2_regular": "Regular tool use",
        "E3_intense": "Intense personal use",
        "E4_immersive": "Immersive companion role",
        "E5_obsessive": "Obsessive, always-on involvement",
    }
    return "\n".join(
        f'<div class="scale-step"><strong>{esc(k)}</strong><span>{esc(labels.get(k, humanize_id(k)))}</span></div>'
        for k in values
    )


def render_atlas_map() -> str:
    points = [
        ("model welfare", "ai", "boundary", 8, 89),
        ("emergent misalignment", "ai", "", 18, 82),
        ("Waluigi effect", "ai", "", 25, 75),
        ("scheming", "ai", "", 21, 69),
        ("sentience attribution", "both", "", 49, 69),
        ("sycophancy", "both", "", 60, 76),
        ("folie a deux", "both", "", 72, 67),
        ("delusional spirals", "both", "", 64, 57),
        ("griefbots", "both", "baseline neuroavatar", 61, 46),
        ("Human Line", "human", "", 74, 42),
        ("attachment / over-trust", "human left", "", 80, 30),
        ("CASA", "human", "baseline", 34, 31),
        ("ELIZA effect", "human", "baseline", 47, 23),
        ("parasocial", "human", "baseline", 58, 25),
        ("Proteus effect", "human", "baseline", 44, 12),
        ("Therabot / Wysa", "protect", "protective", 66, 14),
        ("Tay 2016", "both", "boundary", 84, 23),
        ("folk detection", "human left", "boundary", 92, 17),
        ("value refusal", "protect left", "boundary protective", 81, 24),
        ("Korea Gangbuk", "human", "boundary", 88, 13),
    ]
    items = []
    for label, cls, layer, left, bottom in points:
        route = "both" if cls.startswith("both") else "ai" if cls.startswith("ai") else "human"
        items.append(f'<button class="point {esc(cls)}" type="button" data-route="{route}" data-layer="{esc(layer)}" style="left:{left}%;bottom:{bottom}%"><i></i><span>{esc(label)}</span></button>')
    return "\n".join(items)


def render_gaps(factcheck: dict) -> str:
    cards = []
    for gap in factcheck.get("gaps", []):
        gid = gap.get("id", "gap")
        crit = gap.get("criticality") or gap.get("priority") or "open"
        geo = gap.get("geographic_scope") or gap.get("geo") or ""
        topic = gap.get("topic") or gap.get("description") or gid
        title = clean_title(topic, gid)
        cards.append(f"""
<article class="mini-card gap-card">
  <div class="item-id">{esc(gid)}</div>
  <h3>{esc(title)}</h3>
  <div class="chips">{tag(crit, 'status')}{tag(geo, 'geo')}</div>
  <p class="muted">Open research gap preserved from the canonical fact-check pack. See JSON for the full Russian note and monitoring instruction.</p>
</article>""")
    return "\n".join(cards)


def render_changelog(factcheck: dict, atlas: dict) -> str:
    changelog = (factcheck.get("meta") or {}).get("changelog") or []
    cards = []
    for item in changelog[:8]:
        version = item.get("version", "")
        date = item.get("date", "")
        desc = item.get("description", "")
        desc_en = strip_cyr(desc)
        if len(desc_en) < 40:
            desc_en = "Canonical dataset update. See the fact-check JSON for the full Russian changelog entry."
        cards.append(f"<li><strong>{esc(version)} · {esc(date)}:</strong> {esc(desc_en)}</li>")
    return "\n".join(cards)


def build() -> str:
    signals, factcheck, methodology, atlas, psaicho = load_data()
    stats = (factcheck.get("summary") or {}).get("stats") or {}
    meta = factcheck.get("meta") or {}
    route_counts = Counter(signal_route(sig) for sig in signals)
    evidence_counts = Counter(sig.get("evidence_level") for sig in signals)
    claim_status_counts = Counter(c.get("status") for c in factcheck.get("claims", []))
    signal_cards = "\n".join(render_signal(sig) for sig in signals)
    claim_cards = "\n".join(render_claim(c) for c in factcheck.get("claims", []))
    ph_cards = render_ph_cards(methodology)
    v_cards = render_v_cards(methodology)
    hb_cards = render_hb_cards(methodology)
    boundary_cards = render_boundary_cards(methodology)
    engagement = render_engagement(methodology)
    gap_cards = render_gaps(factcheck)
    changelog = render_changelog(factcheck, atlas)
    build_note = f"English full edition generated from canonical AI-Mind artifacts on {meta.get('data_relevance_date') or atlas.get('date') or '2026-05-31'}."
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>AI-Mind / psAIcho - English Full Edition</title>
<style>
:root{{--bg:#fbfaf7;--card:#fff;--soft:#f3f0e8;--text:#1a1713;--muted:#665d52;--light:#8b8378;--rule:rgba(40,24,10,.14);--accent:#8b5a24;--human:#b4482b;--ai:#155a9f;--both:#665bd6;--protect:#2e7d5b;--serif:Charter,Iowan Old Style,Georgia,serif;--sans:Inter,-apple-system,BlinkMacSystemFont,Helvetica,Arial,sans-serif;--mono:IBM Plex Mono,SFMono-Regular,Menlo,Consolas,monospace}}
*{{box-sizing:border-box}}html{{scroll-behavior:smooth}}body{{margin:0;background:var(--bg);color:var(--text);font:16px/1.58 var(--serif)}}a{{color:var(--accent)}}.wrap{{max-width:1160px;margin:auto;padding:42px 28px 84px}}
.top{{position:sticky;top:0;z-index:20;background:rgba(251,250,247,.96);border-bottom:1px solid var(--rule);backdrop-filter:blur(8px)}}.top-inner{{max-width:1160px;margin:auto;padding:10px 28px;display:flex;gap:14px;flex-wrap:wrap;font:12px var(--sans)}}.top a{{text-decoration:none;color:var(--muted)}}.top a:hover{{color:var(--accent)}}
.eyebrow{{font:12px/1.4 var(--sans);letter-spacing:.08em;text-transform:uppercase;color:var(--light)}}h1{{font-size:46px;line-height:1.06;margin:14px 0 10px;font-weight:520}}h2{{font-size:30px;line-height:1.15;margin:0 0 10px;font-weight:520}}h3{{font-size:19px;line-height:1.24;margin:0 0 8px;font-weight:560}}.subtitle{{font-size:19px;color:var(--muted);max-width:900px;margin:0}}.meta{{font:13px var(--sans);color:var(--muted);display:flex;flex-wrap:wrap;gap:12px;margin-top:20px;padding-top:18px;border-top:1px solid var(--rule)}}.stats{{display:grid;grid-template-columns:repeat(auto-fit,minmax(132px,1fr));gap:10px;margin:30px 0}}.stat{{background:var(--card);border:1px solid var(--rule);border-radius:8px;padding:15px;text-align:center}}.num{{font-size:31px;line-height:1;font-weight:600;color:var(--accent)}}.label{{font:11px var(--sans);text-transform:uppercase;letter-spacing:.04em;color:var(--muted);margin-top:6px}}.panel,.note{{background:var(--card);border:1px solid var(--rule);border-radius:8px;padding:22px 24px;margin:22px 0}}.note{{background:var(--soft)}}.grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(280px,1fr));gap:14px;margin-top:14px}}.minor-grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(230px,1fr));gap:12px;margin-top:12px}}.item-id{{font:11px var(--mono);letter-spacing:.05em;color:var(--accent);text-transform:uppercase;margin-bottom:8px}}.muted{{color:var(--muted)}}.chips{{display:flex;flex-wrap:wrap;gap:6px;margin:10px 0}}.tag{{font:11px var(--sans);padding:3px 8px;border-radius:4px;background:var(--soft);color:var(--muted)}}.tag.level{{background:#e5eaf7;color:#253f90}}.tag.status{{background:#e1f5ee;color:#0f6e56}}.tag.human,.tag.ph{{color:var(--human)}}.tag.ai,.tag.ab{{color:var(--ai)}}.tag.both,.tag.hb{{color:var(--both)}}.tag.protect{{color:var(--protect)}}.tag.kw,.tag.pass,.tag.geo,.tag.date,.tag.axis,.tag.severity{{background:var(--soft)}}
.architecture{{display:grid;grid-template-rows:auto auto auto;gap:0;margin-top:16px}}.arch-top,.arch-bottom{{border:1px solid var(--rule);border-radius:8px;padding:18px;text-align:center;background:var(--soft);font-family:var(--sans)}}.arch-row{{display:grid;grid-template-columns:1fr 110px 1fr;align-items:center;margin:20px 0}}.arch-box{{border:1px solid var(--rule);border-radius:8px;padding:20px;text-align:center;background:var(--card);font-family:var(--sans)}}.arch-box.human{{border-color:rgba(180,72,43,.65);background:#fff3ee}}.arch-box.ai{{border-color:rgba(21,90,159,.55);background:#eef6ff}}.arch-loop{{text-align:center;font:22px var(--sans);color:var(--muted)}}.arch-box span,.arch-top span,.arch-bottom span{{display:block;color:var(--muted);font-size:14px;margin-top:5px}}
.toolbar{{display:flex;flex-wrap:wrap;gap:8px;margin:16px 0}}button,.filter-btn{{font:13px var(--sans);border:1px solid var(--rule);background:var(--card);border-radius:4px;padding:7px 11px;cursor:pointer;color:var(--muted)}}button.active,.filter-btn.active{{background:#3b2a1d;color:white;border-color:#3b2a1d}}.map{{position:relative;min-height:560px;background:linear-gradient(90deg,transparent 0,transparent 49%,rgba(102,91,214,.05) 49%,rgba(102,91,214,.05) 77%,transparent 77%);border-left:1px solid var(--muted);border-bottom:1px solid var(--muted);margin-top:16px;overflow:hidden}}.axis-y,.axis-x{{position:absolute;font:700 16px var(--sans);color:var(--text)}}.axis-y{{left:16px;top:10px}}.axis-x{{right:12px;bottom:10px}}.loop-zone{{position:absolute;left:46%;bottom:43%;width:38%;height:34%;border:1px solid rgba(102,91,214,.45);background:rgba(102,91,214,.04);border-radius:50%;transform:rotate(-4deg)}}.loop-zone span{{position:absolute;left:22px;top:18px;transform:rotate(4deg);font:14px var(--sans);color:var(--muted);background:rgba(251,250,247,.85);padding:3px 6px;border-radius:4px}}.point{{position:absolute;display:flex;align-items:center;gap:8px;transform:translate(-9px,50%);font:13px var(--sans);white-space:nowrap;color:var(--human)}}.point i{{display:block;width:14px;height:14px;border-radius:50%;background:white;border:2px solid currentColor}}.point.ai{{color:var(--ai)}}.point.both{{color:var(--both)}}.point.protect{{color:var(--protect)}}.point.left{{flex-direction:row-reverse;transform:translate(calc(-100% + 9px),50%)}}.point.dimmed,.hidden{{display:none!important}}
.method-card,.mini-card,.signal-card,.claim-card{{background:var(--card);border:1px solid var(--rule);border-radius:8px;padding:17px 18px;margin:0}}.signal-card,.claim-card{{margin-bottom:14px}}.signal-card.route-human{{border-left:3px solid var(--human)}}.signal-card.route-ai{{border-left:3px solid var(--ai)}}.signal-card.route-both{{border-left:3px solid var(--both)}}details{{margin-top:10px}}summary{{font:13px var(--sans);color:var(--accent);cursor:pointer}}ul.sources{{list-style:none;padding:0;margin:10px 0 0}}ul.sources li{{font:13px var(--sans);border-top:1px dashed rgba(40,24,10,.1);padding:7px 0}}ul.sources span{{color:var(--light);font-size:12px}}.kwline{{margin-top:8px}}.scale{{display:grid;grid-template-columns:repeat(auto-fit,minmax(160px,1fr));gap:8px}}.scale-step{{background:var(--card);border:1px solid var(--rule);border-radius:8px;padding:12px}}.scale-step strong{{display:block;font:12px var(--mono);color:var(--accent)}}.scale-step span{{display:block;color:var(--muted)}}.search{{width:100%;max-width:520px;border:1px solid var(--rule);border-radius:6px;padding:9px 11px;background:white;font:14px var(--sans)}}footer{{margin-top:56px;border-top:1px solid var(--rule);padding-top:18px;font:12px var(--sans);color:var(--muted);display:flex;flex-wrap:wrap;gap:12px}}
@media(max-width:900px){{.arch-row{{grid-template-columns:1fr;gap:12px}}.map{{min-width:840px}}.map-wrap{{overflow-x:auto}}h1{{font-size:36px}}}}
</style>
</head>
<body>
<nav class="top"><div class="top-inner"><a href="index.html">ProfGames EN</a><a href="#atlas">Atlas</a><a href="#methodology">Methodology</a><a href="#signals">Signals</a><a href="#factcheck">Fact-check</a><a href="#gaps">Gaps</a><a href="#ethics">Ethics</a><a href="#changelog">Changelog</a></div></nav>
<main class="wrap">
<header>
  <div class="eyebrow">English full edition · canonical AI-Mind data spine</div>
  <h1>AI-Mind / psAIcho</h1>
  <p class="subtitle">A full English-facing render of the AI-Mind psychological-impact catalogue and psAIcho model-behavior lens. The page is generated from the canonical machine-readable artifacts rather than from a separate fork.</p>
  <div class="meta"><span>{esc(build_note)}</span><span>Fact-check {esc(meta.get('version'))}</span><span>Atlas {esc(atlas.get('version'))}</span><span><a href="../aimind/aimind.html">Russian canonical HTML</a></span><span><a href="../aimind/aimind_signals.jsonl">signals JSONL</a></span><span><a href="../aimind/aimind_factcheck.json">fact-check JSON</a></span></div>
</header>
<section class="stats" aria-label="Dataset stats">
  <div class="stat"><div class="num">{len(signals)}</div><div class="label">signals</div></div>
  <div class="stat"><div class="num">{len(factcheck.get('claims', []))}</div><div class="label">claims</div></div>
  <div class="stat"><div class="num">{len(methodology.get('phenomena', []))}</div><div class="label">PH phenomena</div></div>
  <div class="stat"><div class="num">{len(methodology.get('vulnerability_parameters', []))}</div><div class="label">V factors</div></div>
  <div class="stat"><div class="num">{len((psaicho.get('ai_behaviors') or []))}</div><div class="label">AB patterns</div></div>
  <div class="stat"><div class="num">{len((methodology.get('human_baseline_layer') or {}).get('items') or [])}</div><div class="label">HB baselines</div></div>
  <div class="stat"><div class="num">{route_counts.get('ai', 0) + route_counts.get('both', 0)}</div><div class="label">AI-stream</div></div>
  <div class="stat"><div class="num">{route_counts.get('both', 0)}</div><div class="label">loop signals</div></div>
</section>
<section class="note">
  <h2>How to read this edition</h2>
  <p>This is now a full rendered catalogue, not a short landing card. It contains every current signal, every fact-check claim, methodology cards, vulnerability parameters, human baseline mechanisms, boundary patterns, research gaps, source trails and filtering controls.</p>
  <p class="muted">The public page is English throughout. The original long-form canonical wording remains in the JSON artifacts for audit traceability; this edition renders English titles, classifications, source trails and synthesized readings from the shared spine.</p>
</section>
<section class="panel" id="atlas">
  <h2>Atlas: one spine, two lenses</h2>
  <div class="architecture">
    <div class="arch-top"><strong>Atlas meta-layer</strong><span>routing map · shared A-D evidence scale · overlap registry · guardrails</span></div>
    <div class="arch-row"><div class="arch-box human"><strong>AI-Mind</strong><span>human + loop · PH01-PH15</span></div><div class="arch-loop"><strong>&lt;-&gt;</strong><span>loop</span></div><div class="arch-box ai"><strong>psAIcho</strong><span>model behavior · AB01-AB07</span></div></div>
    <div class="arch-bottom"><strong>Shared spine · aimind_signals.jsonl</strong><span>global SIG-ID · streams[] · phenomena[] + ai_behavior[] + human_baseline[]</span></div>
  </div>
  <div class="toolbar" aria-label="Atlas filters">
    <button class="atlas-filter active" data-atlas-filter="all" type="button">All points</button><button class="atlas-filter" data-atlas-filter="human" type="button">AI-Mind</button><button class="atlas-filter" data-atlas-filter="ai" type="button">psAIcho</button><button class="atlas-filter" data-atlas-filter="both" type="button">Loop</button><button class="atlas-filter" data-atlas-filter="baseline" type="button">HB baseline</button><button class="atlas-filter" data-atlas-filter="protective" type="button">Protective</button><button class="atlas-filter" data-atlas-filter="boundary" type="button">Boundary</button>
  </div>
  <div class="map-wrap"><div class="map"><div class="axis-y">speaks about AI ↑</div><div class="axis-x">speaks about humans →</div><div class="loop-zone"><span>both: loop</span></div>{render_atlas_map()}</div></div>
</section>
<section class="panel" id="methodology">
  <h2>Methodology: PH, V, E, HB and boundary patterns</h2>
  <h3>PH01-PH15 phenomena</h3><div class="grid">{ph_cards}</div>
  <h3>Vulnerability parameters</h3><div class="minor-grid">{v_cards}</div>
  <h3>Engagement scale</h3><div class="scale">{engagement}</div>
  <h3>Human baseline layer</h3><div class="minor-grid">{hb_cards}</div>
  <h3>Boundary patterns</h3><div class="minor-grid">{boundary_cards}</div>
</section>
<section class="panel" id="signals">
  <h2>Signals</h2>
  <p class="subtitle">All {len(signals)} signals from the shared spine. Use filters for evidence level, route and text search.</p>
  <div class="toolbar" id="sig-controls"><button class="sig-filter active" data-filter="all">All</button><button class="sig-filter" data-filter="human">AI-Mind</button><button class="sig-filter" data-filter="ai">psAIcho</button><button class="sig-filter" data-filter="both">Loop</button><button class="sig-filter" data-filter="A">Level A</button><button class="sig-filter" data-filter="B">Level B</button><button class="sig-filter" data-filter="C">Level C</button><input class="search" id="sig-search" placeholder="Search signals by ID, title, PH, AB or HB"></div>
  <div id="signal-list">{signal_cards}</div>
</section>
<section class="panel" id="factcheck">
  <h2>Fact-check claims</h2>
  <p class="subtitle">All {len(factcheck.get('claims', []))} claim nodes from the independent audit pack. English cards preserve status, evidence, source trail and caveat counts.</p>
  <div class="toolbar" id="claim-controls"><button class="claim-filter active" data-filter="all">All</button><button class="claim-filter" data-filter="verified">Verified</button><button class="claim-filter" data-filter="partially_verified">Partly verified</button><button class="claim-filter" data-filter="disputed">Disputed</button><button class="claim-filter" data-filter="A">Level A</button><button class="claim-filter" data-filter="B">Level B</button><button class="claim-filter" data-filter="C">Level C</button><input class="search" id="claim-search" placeholder="Search claims by ID, pass or title"></div>
  <div class="stats"><div class="stat"><div class="num">{claim_status_counts.get('verified', 0)}</div><div class="label">verified</div></div><div class="stat"><div class="num">{claim_status_counts.get('partially_verified', 0)}</div><div class="label">partly verified</div></div><div class="stat"><div class="num">{stats.get('disputed', sum(1 for c in factcheck.get('claims', []) if c.get('disputed')))}</div><div class="label">disputed notes</div></div><div class="stat"><div class="num">{evidence_counts.get('A', 0)}</div><div class="label">signal level A</div></div><div class="stat"><div class="num">{evidence_counts.get('B', 0)}</div><div class="label">signal level B</div></div></div>
  <div id="claim-list">{claim_cards}</div>
</section>
<section class="panel" id="gaps">
  <h2>Research gaps</h2>
  <p class="subtitle">Open gaps are retained as monitoring targets. The English page lists them without pretending that a gap is a finding.</p>
  <div class="minor-grid">{gap_cards}</div>
</section>
<section class="panel" id="ethics">
  <h2>Ethical frame</h2>
  <div class="grid">
    <article class="mini-card"><h3>No diagnosis by dataset</h3><p>AI-Mind is a catalogue of public signals and verified claims. It is not a clinical diagnostic instrument and does not define a new disorder.</p></article>
    <article class="mini-card"><h3>No prevalence shortcut</h3><p>Case pools, lawsuits and support groups are evidence of documented narratives, not epidemiology. Prevalence requires sampling frames.</p></article>
    <article class="mini-card"><h3>Protective use remains visible</h3><p>The framework preserves beneficial or constrained uses as PH15, rather than turning every AI-mental-health interaction into a harm claim.</p></article>
    <article class="mini-card"><h3>Minors and vulnerable people</h3><p>Do not reproduce operational self-harm details, substance-use recipes, private identifiers or sensationalized transcripts.</p></article>
  </div>
</section>
<section class="panel" id="changelog">
  <h2>Changelog</h2>
  <ul>{changelog}</ul>
</section>
<footer><span>Sergey Gordeychik</span><span><a href="https://t.me/aiakyn">telegram</a></span><span><a href="https://teletype.in/@sergey_gordey">teletype</a></span><span><a href="https://github.com/scadastrangelove/profgames">github</a></span><span>#profgames</span></footer>
</main>
<script>
function setupFilters(buttonSelector, itemSelector, searchSelector) {{
  const buttons = Array.from(document.querySelectorAll(buttonSelector));
  const items = Array.from(document.querySelectorAll(itemSelector));
  const search = document.querySelector(searchSelector);
  let filter = 'all';
  function apply() {{
    const q = (search?.value || '').toLowerCase().trim();
    items.forEach(item => {{
      const text = item.dataset.text || item.textContent.toLowerCase();
      const route = item.dataset.route;
      const level = item.dataset.level;
      const status = item.dataset.status;
      const disputed = item.dataset.disputed === 'true';
      const okFilter = filter === 'all' || route === filter || level === filter || status === filter || (filter === 'disputed' && disputed);
      const okText = !q || text.includes(q);
      item.classList.toggle('hidden', !(okFilter && okText));
    }});
  }}
  buttons.forEach(btn => btn.addEventListener('click', () => {{
    filter = btn.dataset.filter || 'all';
    buttons.forEach(b => b.classList.toggle('active', b === btn));
    apply();
  }}));
  if (search) search.addEventListener('input', apply);
}}
setupFilters('.sig-filter', '.signal-card', '#sig-search');
setupFilters('.claim-filter', '.claim-card', '#claim-search');
const atlasButtons = Array.from(document.querySelectorAll('.atlas-filter'));
const atlasPoints = Array.from(document.querySelectorAll('.point[data-route]'));
atlasButtons.forEach(btn => btn.addEventListener('click', () => {{
  const filter = btn.dataset.atlasFilter || 'all';
  atlasButtons.forEach(b => b.classList.toggle('active', b === btn));
  atlasPoints.forEach(point => {{
    const layers = (point.dataset.layer || '').split(/\\s+/).filter(Boolean);
    const route = point.dataset.route;
    point.classList.toggle('dimmed', filter !== 'all' && !(route === filter || layers.includes(filter)));
  }});
}}));
</script>
</body>
</html>"""


def main() -> None:
    rendered = "\n".join(line.rstrip() for line in build().splitlines()) + "\n"
    OUT.write_text(rendered, encoding="utf-8")
    text = OUT.read_text(encoding="utf-8")
    visible_cyr = CYR.findall(text)
    if visible_cyr:
        raise SystemExit(f"Generated HTML still contains Cyrillic characters: {len(visible_cyr)}")
    print(f"Wrote {OUT.relative_to(ROOT)} ({OUT.stat().st_size:,} bytes)")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Build the English A1 event explorer from profgames_ai_signals.jsonl.

The Russian a-events.html remains the canonical narrative article. This page is
an English-facing data browser: it keeps the original signal ids, source URLs,
evidence levels and framework tags, while using the English fields already
present in the JSONL dataset.
"""

from __future__ import annotations

import html
import json
from collections import Counter, defaultdict
from datetime import date, datetime
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUT = Path(__file__).resolve().parent
SIGNALS_PATH = ROOT / "profgames_ai_signals.jsonl"


DIMENSION_LABELS = {
    "D01_geographic_exit": "D01 geographic exit",
    "D02_geographic_return": "D02 geographic return",
    "D03_vertical_exit": "D03 vertical exit",
    "D04_vertical_return": "D04 vertical return",
    "D05_lateral_professional_exit": "D05 lateral professional exit",
    "D06_lateral_professional_return": "D06 lateral professional return",
    "D07_industry_exit": "D07 industry exit",
    "D08_industry_return": "D08 industry return",
    "D09_employment_form_exit": "D09 employment-form exit",
    "D10_employment_form_return": "D10 employment-form return",
}

AGENCY_LABELS = {
    "A1_skills_capital": "A1 skills capital",
    "A2_career_identity": "A2 career identity",
    "A3_adaptability_self_efficacy": "A3 adaptability and self-efficacy",
    "A4_network_capital": "A4 network capital",
    "A4_signal_preservation": "A4 signal preservation",
    "A5_credential_portability": "A5 credential portability",
    "A6_labor_market_liquidity": "A6 labor-market liquidity",
    "A7_institutional_constraints": "A7 institutional constraints",
}

RESIDUAL_GAP_LABELS = {
    "integrated_agency_validation": "Integrated agency validation",
    "industry_reentry_signal_preservation_metric": "Industry re-entry signal preservation metric",
    "individual_panel_for_employment_form_return": "Individual panel for employment-form return",
    "vertical_return_track_switch_stigma_quantification": "Vertical return and track-switch stigma",
    "cn_ru_task_vector": "China/Russia task-vector comparability",
    "validated_individual_return_option_value": "Validated individual return option value",
    "ru_post_2022_credential_practical_operation": "Post-2022 Russian credential operation",
    "I03_IRAS": "I03 IRAS",
}

DISPLAY_LABELS = {
    "самозанятые": "self-employed",
    "НПД": "NPD tax regime",
    "ФНС": "Russian Federal Tax Service",
}

TEXT_REPLACEMENTS = {
    "кадровый": "hiring",
    "НПД": "NPD tax regime",
    "ФНС": "Russian Federal Tax Service",
    "самозанятые": "self-employed",
}

LANES = [
    ("corporate", "Corporate action"),
    ("revision", "Walkbacks / revisions"),
    ("data", "Data and measurement"),
    ("regulation", "Regulation / courts"),
]

ANCHOR_IDS = {
    "SIG_2023_IBM_HIRING_PAUSE",
    "SIG_2024_KLARNA_700_AGENT_EQUIVALENT",
    "SIG_2025_KLARNA_REHIRES_HUMANS_AFTER_AI_SUPPORT_PUSH",
    "SIG_2024_DUOLINGO_CONTRACTOR_CUTS",
    "SIG_2025_DUOLINGO_AI_FIRST_CONTRACTOR_WALKBACK",
    "SIG_2025_SALESFORCE_ENGINEERING_HIRING_FREEZE_AI",
    "SIG_2025_SALESFORCE_SUPPORT_AI_CUTS",
    "SIG_2023_OPENAI_AI_CLASSIFIER_LAUNCH",
    "SIG_2023_OPENAI_AI_CLASSIFIER_RETIRED",
    "SIG_2023_VANDERBILT_DISABLES_TURNITIN_AI_DETECTOR",
    "SIG_2025_TEXAS_TRAIGA_SIGNED",
    "SIG_2025_VIRGINIA_HIGH_RISK_AI_BILL_VETO",
    "SIG_2025_BARTZ_ANTHROPIC_FAIR_USE_SPLIT",
    "SIG_2025_KADREY_META_FAIR_USE_RULING",
    "SIG_2026_ORACLE_AI_CAPEX_LAYOFFS",
    "SIG_2026_SOFTLINE_AI_STAFF_OPTIMIZATION",
    "SIG_2025_SBER_AI_EFFICIENCY_LAYOFFS",
}

WALKBACK_PAIRS = [
    (
        "Klarna",
        "walkback",
        "SIG_2024_KLARNA_700_AGENT_EQUIVALENT",
        "SIG_2025_KLARNA_REHIRES_HUMANS_AFTER_AI_SUPPORT_PUSH",
        "A support-automation claim is followed by rehiring human customer-service agents after quality concerns.",
    ),
    (
        "IBM",
        "qualified outcome",
        "SIG_2023_IBM_HIRING_PAUSE",
        "SIG_2025_IBM_AI_REPLACES_HUNDREDS_HR_ROLES",
        "The company confirms HR-role replacement, but the employment story is reallocation rather than pure net shrinkage.",
    ),
    (
        "Duolingo",
        "qualified walkback",
        "SIG_2024_DUOLINGO_CONTRACTOR_CUTS",
        "SIG_2025_DUOLINGO_AI_FIRST_CONTRACTOR_WALKBACK",
        "Contractor cuts and AI-first language are later narrowed: the CEO says this does not mean full-time layoffs.",
    ),
    (
        "Salesforce",
        "escalation",
        "SIG_2025_SALESFORCE_ENGINEERING_HIRING_FREEZE_AI",
        "SIG_2025_SALESFORCE_SUPPORT_AI_CUTS",
        "Unlike the walkback cases, the AI-efficiency claim escalates into a stated reduction of support roles.",
    ),
    (
        "Detection",
        "failure",
        "SIG_2023_OPENAI_AI_CLASSIFIER_LAUNCH",
        "SIG_2023_OPENAI_AI_CLASSIFIER_RETIRED",
        "The simplest provenance answer, text detection, fails quickly enough that institutions move toward process, policy and exam redesign.",
    ),
]

SPLIT_DECISIONS = [
    (
        "State AI law split",
        "SIG_2025_TEXAS_TRAIGA_SIGNED",
        "SIG_2025_VIRGINIA_HIGH_RISK_AI_BILL_VETO",
        "Two US states face the same AI-governance question in 2025 and move in opposite directions: Texas signs a broad act, Virginia vetoes a high-risk bill.",
    ),
    (
        "Copyright / training-data split",
        "SIG_2025_BARTZ_ANTHROPIC_FAIR_USE_SPLIT",
        "SIG_2025_KADREY_META_FAIR_USE_RULING",
        "Federal courts do not produce one simple answer. Lawful acquisition, pirated-copy retention and market-substitution theories separate into different legal tracks.",
    ),
]

TREND_LINES = [
    {
        "id": "junior",
        "title": "1. Entry funnel compression",
        "subtitle": "Stanford payroll and AI Index signals point in the same direction: young workers and entry-level software roles are squeezed first.",
        "series": [
            ("Young AI-exposed workers", "#0f6e56", [(2022, 100), (2023, 99), (2024, 95), (2025, 88), (2026, 84)]),
            ("Young software developers", "#315a9c", [(2022, 100), (2024, 96), (2025, 89), (2026, 80)]),
            ("Entry-level postings", "#9b7b0e", [(2023, 100), (2024, 92), (2025, 78), (2026, 65)]),
        ],
    },
    {
        "id": "contractors",
        "title": "2. Support and contractor roles: wave, walkback, renewed pressure",
        "subtitle": "Klarna and Duolingo make the non-monotonic pattern visible: an AI-first cut can be followed by correction without reversing the underlying pressure.",
        "series": [
            ("Support roles", "#993c1d", [(2024, 100), (2025, 94), (2025.7, 84), (2026, 78)]),
            ("Contractor / translation roles", "#9b7b0e", [(2024, 100), (2025, 82), (2025.65, 88), (2026, 78)]),
        ],
    },
    {
        "id": "imitation",
        "title": "3. Imitation loop",
        "subtitle": "Employers use AI in screening, candidates use AI in applications, and the signal channel starts selecting tool fit rather than human fit.",
        "series": [
            ("AI in hiring", "#315a9c", [(2023, 51), (2024, 65), (2025, 78), (2026, 80)]),
            ("AI resumes", "#993c1d", [(2023, 35), (2024, 55), (2025, 70), (2026, 74)]),
            ("Pushback x10", "#0f6e56", [(2023, 10), (2024, 30), (2025, 60), (2026, 90)]),
        ],
    },
    {
        "id": "school",
        "title": "4. School parallel",
        "subtitle": "Student AI use rises fast; the first detector response breaks; institutions fall back to phones-off classrooms, blue books and AI-fluency programs.",
        "series": [
            ("Student use", "#993c1d", [(2022, 0), (2023, 89), (2024, 90), (2025, 90)]),
            ("Institutional response", "#0f6e56", [(2023, 2), (2024, 12), (2025, 35), (2026, 42)]),
            ("Blue-book revival", "#315a9c", [(2023, 0), (2024, 30), (2025, 80), (2026, 80)]),
        ],
    },
    {
        "id": "provenance",
        "title": "5. Technical and legal provenance stack",
        "subtitle": "C2PA, watermarking, labeling policies and copyright litigation are parallel attempts to restore origin and responsibility.",
        "series": [
            ("Technical provenance", "#0f6e56", [(2022, 1), (2023, 3), (2024, 8), (2025, 10), (2026, 12)]),
            ("Legal front", "#993c1d", [(2023, 2), (2024, 5), (2025, 9), (2026, 11)]),
        ],
    },
    {
        "id": "detection",
        "title": "6. Detection wars",
        "subtitle": "Output-only AI detection proves fragile: false positives, non-native bias and institutional reversals push the field toward process provenance.",
        "series": [
            ("Detector adoption", "#315a9c", [(2023, 1), (2024, 3), (2025, 4)]),
            ("Detector failures", "#993c1d", [(2023, 3), (2024, 5), (2025, 8)]),
            ("Process provenance", "#0f6e56", [(2023, 0), (2024, 1), (2025, 3)]),
        ],
    },
]


def esc(value: object) -> str:
    return html.escape(str(value or ""), quote=True)


def load_signals() -> list[dict]:
    rows: list[dict] = []
    for line in SIGNALS_PATH.read_text(encoding="utf-8").splitlines():
        if line.strip():
            rows.append(json.loads(line))
    return sorted(rows, key=lambda row: (str(row.get("event_date", "")), int(row.get("sequence", 0))))


def list_value(row: dict, key: str) -> list[str]:
    value = row.get(key) or []
    if isinstance(value, list):
        return [str(item) for item in value if item is not None and str(item) != ""]
    return [str(value)]


def normalize_region(region: str) -> str:
    value = region.strip()
    low = value.lower()
    if value in {"US", "NYC", "California", "Colorado", "Alabama"}:
        return "US"
    if value in {"EU", "France", "Italy", "Sweden"}:
        return "EU"
    if value == "UK":
        return "UK"
    if value == "RU":
        return "RU"
    if value == "CN" or low.startswith("cn"):
        return "CN"
    if low.startswith("global"):
        return "global"
    return "other"


def region_buckets(row: dict) -> set[str]:
    buckets = {normalize_region(region) for region in list_value(row, "region")}
    return buckets or {"other"}


def label_from_id(value: str) -> str:
    if value in DISPLAY_LABELS:
        return DISPLAY_LABELS[value]
    if value in DIMENSION_LABELS:
        return DIMENSION_LABELS[value]
    if value in AGENCY_LABELS:
        return AGENCY_LABELS[value]
    if value in RESIDUAL_GAP_LABELS:
        return RESIDUAL_GAP_LABELS[value]
    return value.replace("_", " ")


def clean_text(value: object) -> str:
    text = str(value or "")
    for src, dst in TEXT_REPLACEMENTS.items():
        text = text.replace(src, dst)
    return text


def parse_event_date(value: object) -> date:
    text = str(value or "")
    try:
        return datetime.strptime(text[:10], "%Y-%m-%d").date()
    except ValueError:
        year = int(text[:4]) if text[:4].isdigit() else 2020
        return date(year, 1, 1)


def evidence_class(value: str) -> str:
    return value.lower().replace("/", "-")


def event_lane(row: dict) -> str:
    title = str(row.get("title", "")).lower()
    tags = {tag.lower() for tag in list_value(row, "tags")}
    types = {typ.lower() for typ in list_value(row, "type")}
    if (
        "walkback" in tags
        or "rehiring" in tags
        or "veto" in tags
        or "reversal" in title
        or "retires" in title
        or "disable" in title
        or "clarifies" in title
        or "suppresses" in title
    ):
        return "revision"
    if types & {"regulation", "legal_case", "regulatory_enforcement", "court", "privacy"}:
        return "regulation"
    if types & {"data_release", "research", "survey", "policy_guidance"} or "index" in tags:
        return "data"
    return "corporate"


def row_lookup(rows: list[dict]) -> dict[str, dict]:
    return {str(row.get("id")): row for row in rows}


def timeline_svg(rows: list[dict]) -> str:
    width, height = 1120, 430
    left, right = 118, 1060
    top = 72
    lane_gap = 82
    lane_y = {lane: top + index * lane_gap for index, (lane, _) in enumerate(LANES)}
    start = date(2020, 1, 1)
    end = date(2026, 12, 31)
    span = (end - start).days

    def x_for(value: object) -> float:
        day = parse_event_date(value)
        return left + (day - start).days / span * (right - left)

    out: list[str] = [
        f'<svg viewBox="0 0 {width} {height}" class="timeline-svg" role="img" aria-label="A1 event timeline by carrier lane">',
        '<defs><marker id="arrow" markerWidth="8" markerHeight="8" refX="7" refY="4" orient="auto"><path d="M0,0 L8,4 L0,8 Z" fill="#993c1d"/></marker></defs>',
    ]

    for year in range(2020, 2027):
        x = x_for(f"{year}-01-01")
        out.append(f'<line x1="{x:.1f}" y1="42" x2="{x:.1f}" y2="348" class="grid-line"/>')
        out.append(f'<text x="{x:.1f}" y="28" class="year-label" text-anchor="middle">{year}</text>')

    for lane, label in LANES:
        y = lane_y[lane]
        out.append(f'<line x1="{left}" y1="{y}" x2="{right}" y2="{y}" class="lane-line"/>')
        out.append(f'<text x="{left - 14}" y="{y + 4}" class="lane-label" text-anchor="end">{esc(label)}</text>')

    positions: dict[str, tuple[float, float]] = {}
    lane_offsets: dict[tuple[str, int], int] = defaultdict(int)
    for row in rows:
        lane = event_lane(row)
        day = parse_event_date(row.get("event_date"))
        bucket = int((day - start).days / 18)
        offset_index = lane_offsets[(lane, bucket)]
        lane_offsets[(lane, bucket)] += 1
        y = lane_y[lane] + ((offset_index % 7) - 3) * 5
        x = x_for(row.get("event_date"))
        positions[str(row.get("id"))] = (x, y)
        radius = 5.7 if row.get("id") in ANCHOR_IDS else 3.1
        anchor_class = " anchor" if row.get("id") in ANCHOR_IDS else ""
        out.append(
            f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{radius}" '
            f'class="evt-dot ev-{esc(evidence_class(str(row.get("evidence_level", ""))))}{anchor_class}">'
            f'<title>{esc(row.get("event_date"))} · {esc(row.get("title"))}</title></circle>'
        )

    for _, kind, left_id, right_id, _ in WALKBACK_PAIRS:
        if left_id not in positions or right_id not in positions:
            continue
        x1, y1 = positions[left_id]
        x2, y2 = positions[right_id]
        control_y = min(y1, y2) - 48
        cls = "arc escalation" if kind == "escalation" else "arc"
        out.append(
            f'<path d="M{x1:.1f},{y1 - 9:.1f} Q{(x1 + x2) / 2:.1f},{control_y:.1f} {x2:.1f},{y2 - 9:.1f}" class="{cls}" marker-end="url(#arrow)"/>'
        )

    for _, left_id, right_id, _ in SPLIT_DECISIONS:
        if left_id not in positions or right_id not in positions:
            continue
        x1, y1 = positions[left_id]
        x2, y2 = positions[right_id]
        out.append(
            f'<path d="M{x1:.1f},{y1 + 10:.1f} Q{(x1 + x2) / 2:.1f},{max(y1, y2) + 45:.1f} {x2:.1f},{y2 + 10:.1f}" class="arc split"/>'
        )

    out.append('<g class="timeline-legend" transform="translate(118 372)">')
    legend = [("A / A-B", "ev-a"), ("B", "ev-b"), ("B-C / C", "ev-c"), ("anchor", "anchor-outline")]
    for index, (label, cls) in enumerate(legend):
        x = index * 118
        if cls == "anchor-outline":
            out.append(f'<circle cx="{x}" cy="0" r="6" class="evt-dot ev-b anchor"/><text x="{x + 14}" y="4">{label}</text>')
        else:
            out.append(f'<circle cx="{x}" cy="0" r="5" class="evt-dot {cls}"/><text x="{x + 14}" y="4">{label}</text>')
    out.append("</g></svg>")
    return "\n".join(out)


def pair_cards(rows: list[dict]) -> str:
    lookup = row_lookup(rows)
    out: list[str] = []
    for label, kind, first_id, second_id, summary in WALKBACK_PAIRS:
        first = lookup.get(first_id)
        second = lookup.get(second_id)
        if not first or not second:
            continue
        out.append(
            f'''
<article class="pair-card">
  <div class="pair-head"><strong>{esc(label)}</strong><span>{esc(kind)}</span></div>
  <div class="pair-events">
    <div><em>{esc(first.get("event_date"))}</em><br>{esc(first.get("title"))}</div>
    <div class="pair-arrow">→</div>
    <div><em>{esc(second.get("event_date"))}</em><br>{esc(second.get("title"))}</div>
  </div>
  <p>{esc(summary)}</p>
</article>'''
        )
    return "\n".join(out)


def split_cards(rows: list[dict]) -> str:
    lookup = row_lookup(rows)
    out: list[str] = []
    for label, first_id, second_id, summary in SPLIT_DECISIONS:
        first = lookup.get(first_id)
        second = lookup.get(second_id)
        if not first or not second:
            continue
        out.append(
            f'''
<article class="pair-card split-card">
  <div class="pair-head"><strong>{esc(label)}</strong><span>split decision</span></div>
  <div class="pair-events">
    <div><em>{esc(first.get("event_date"))}</em><br>{esc(first.get("title"))}</div>
    <div class="pair-arrow">↔</div>
    <div><em>{esc(second.get("event_date"))}</em><br>{esc(second.get("title"))}</div>
  </div>
  <p>{esc(summary)}</p>
</article>'''
        )
    return "\n".join(out)


def mini_trend_svg(series: list[tuple[str, str, list[tuple[float, float]]]]) -> str:
    width, height = 520, 220
    left, right = 48, 486
    top, bottom = 28, 174
    all_points = [point for _, _, points in series for point in points]
    min_x = min(point[0] for point in all_points)
    max_x = max(point[0] for point in all_points)
    min_y = min(point[1] for point in all_points)
    max_y = max(point[1] for point in all_points)
    if max_y == min_y:
        max_y += 1

    def sx(x: float) -> float:
        return left + (x - min_x) / (max_x - min_x or 1) * (right - left)

    def sy(y: float) -> float:
        return bottom - (y - min_y) / (max_y - min_y) * (bottom - top)

    out = [f'<svg viewBox="0 0 {width} {height}" class="mini-trend" role="img" aria-label="trend chart">']
    for year in range(int(min_x), int(max_x) + 1):
        x = sx(year)
        out.append(f'<line x1="{x:.1f}" y1="{top}" x2="{x:.1f}" y2="{bottom}" class="grid-line"/>')
        out.append(f'<text x="{x:.1f}" y="{bottom + 20}" class="year-label" text-anchor="middle">{year}</text>')
    for tick in (min_y, (min_y + max_y) / 2, max_y):
        y = sy(tick)
        out.append(f'<line x1="{left}" y1="{y:.1f}" x2="{right}" y2="{y:.1f}" class="grid-line"/>')
        out.append(f'<text x="{left - 8}" y="{y + 4:.1f}" class="axis-label" text-anchor="end">{tick:.0f}</text>')
    for label, color, points in series:
        d = " ".join(("M" if i == 0 else "L") + f"{sx(x):.1f},{sy(y):.1f}" for i, (x, y) in enumerate(points))
        out.append(f'<path d="{d}" fill="none" stroke="{color}" class="trend-line"/>')
        x, y = points[-1]
        out.append(f'<circle cx="{sx(x):.1f}" cy="{sy(y):.1f}" r="4" fill="{color}"><title>{esc(label)}: {y:g}</title></circle>')
        out.append(f'<text x="{sx(x) + 7:.1f}" y="{sy(y) + 4:.1f}" class="endpoint" fill="{color}">{esc(label)}</text>')
    out.append("</svg>")
    return "\n".join(out)


def trend_panels() -> str:
    out: list[str] = []
    for trend in TREND_LINES:
        out.append(
            f'''
<article class="trend-card" id="trend-{esc(trend['id'])}">
  <h3>{esc(trend['title'])}</h3>
  <p>{esc(trend['subtitle'])}</p>
  {mini_trend_svg(trend['series'])}
</article>'''
        )
    return "\n".join(out)


def mediation_level(row: dict) -> str:
    title = str(row.get("title", "")).lower()
    tags = {tag.lower() for tag in list_value(row, "tags")}
    types = {typ.lower() for typ in list_value(row, "type")}
    if types & {"regulation", "legal_case", "regulatory_enforcement"} or tags & {
        "provenance",
        "academic_integrity",
        "copyright",
        "healthcare",
        "child_safety",
        "fair_use",
    }:
        return "L4 trust / regulation"
    if "layoffs" in types or "layoffs" in tags or "headcount" in title or "cuts" in title:
        return "L3 decision rights"
    if tags & {"algorithmic_management", "platform_work", "management", "rto", "self_employment"}:
        return "L2 coordination"
    return "L1 entry / translation"


def mediation_matrix(rows: list[dict]) -> str:
    years = ["2023", "2024", "2025", "2026"]
    levels = ["L1 entry / translation", "L2 coordination", "L3 decision rights", "L4 trust / regulation"]
    cells: dict[tuple[str, str], list[dict]] = defaultdict(list)
    for row in rows:
        year = str(row.get("event_year"))
        if year not in years:
            continue
        cells[(mediation_level(row), year)].append(row)

    body: list[str] = []
    for level in levels:
        row_cells = [f"<th>{esc(level)}</th>"]
        for year in years:
            items = sorted(cells[(level, year)], key=lambda item: item.get("event_date", ""))[:3]
            count = len(cells[(level, year)])
            snippets = "".join(
                f'<div><span class="pill ev-{esc(evidence_class(str(item.get("evidence_level", ""))))}">{esc(item.get("evidence_level", ""))}</span> {esc(item.get("title", ""))}</div>'
                for item in items
            )
            more = f'<div class="more">+{count - len(items)} more</div>' if count > len(items) else ""
            row_cells.append(f'<td><strong>{count}</strong>{snippets}{more}</td>')
        body.append(f"<tr>{''.join(row_cells)}</tr>")

    head = "".join(f"<th>{year}</th>" for year in years)
    return f'''
<div class="table-wrap">
  <table class="mediation-table">
    <thead><tr><th>Layer</th>{head}</tr></thead>
    <tbody>{''.join(body)}</tbody>
  </table>
</div>'''


def chips(values: list[str], cls: str = "chip") -> str:
    return "".join(f'<span class="{cls}">{esc(label_from_id(value))}</span>' for value in values)


def source_links(row: dict) -> str:
    links: list[str] = []
    for key, label in (("primary", "primary"), ("secondary", "secondary")):
        for index, url in enumerate(list_value(row, key), 1):
            links.append(
                f'<a href="{esc(url)}" target="_blank" rel="noopener">{label} {index}</a>'
            )
    return " ".join(links) if links else '<span class="muted">No source URL listed.</span>'


def bar_rows(counter: Counter, labels: dict[str, str] | None = None) -> str:
    if not counter:
        return ""
    labels = labels or {}
    max_count = max(counter.values()) or 1
    out: list[str] = []
    for key, count in counter.most_common():
        width = round(count / max_count * 100, 2)
        out.append(
            '<div class="bar-row">'
            f'<div class="bar-label">{esc(labels.get(str(key), label_from_id(str(key))))}</div>'
            f'<div class="bar-track"><div class="bar-fill" style="width:{width}%"></div></div>'
            f'<div class="bar-count">{count}</div>'
            "</div>"
        )
    return "\n".join(out)


def event_cards(rows: list[dict]) -> str:
    cards: list[str] = []
    for row in rows:
        year = row.get("event_year") or str(row.get("event_date", ""))[:4]
        evidence = str(row.get("evidence_level", ""))
        confidence = str(row.get("confidence", ""))
        dimensions = list_value(row, "dimensions")
        agency = list_value(row, "agency")
        tags = list_value(row, "tags")
        regions = list_value(row, "region")
        buckets = sorted(region_buckets(row))
        searchable = " ".join(
            [
                str(row.get("id", "")),
                clean_text(row.get("title", "")),
                clean_text(row.get("summary", "")),
                clean_text(row.get("why", "")),
                clean_text(row.get("note", "")),
                " ".join(label_from_id(tag) for tag in tags),
                " ".join(dimensions),
                " ".join(agency),
                " ".join(regions),
            ]
        ).lower()
        cards.append(
            f'''
<article class="event-card" data-year="{esc(year)}" data-regions="{esc("|".join(buckets))}" data-evidence="{esc(evidence)}" data-dimensions="{esc("|".join(dimensions))}" data-search="{esc(searchable)}">
  <div class="event-meta">
    <span>{esc(row.get("event_date", ""))}</span>
    <span>{esc(row.get("id", ""))}</span>
  </div>
  <h3>{esc(clean_text(row.get("title", "")))}</h3>
  <div class="chip-row">
    <span class="chip evidence ev-{esc(evidence.lower().replace("/", "-"))}">evidence {esc(evidence)}</span>
    <span class="chip">confidence {esc(confidence.replace("_", " "))}</span>
    {chips(regions)}
  </div>
  <p>{esc(clean_text(row.get("summary", "")))}</p>
  <p class="why"><strong>Why it matters:</strong> {esc(clean_text(row.get("why", "")))}</p>
  <details>
    <summary>Framework tags and sources</summary>
    <div class="detail-block">
      <div><strong>Dimensions:</strong> {chips(dimensions)}</div>
      <div><strong>Agency:</strong> {chips(agency)}</div>
      <div><strong>Residual gaps:</strong> {chips(list_value(row, "residual_gaps"))}</div>
      <div><strong>Tags:</strong> {chips(tags)}</div>
      <div><strong>Sources:</strong> <span class="sources">{source_links(row)}</span></div>
      <p class="note"><strong>Note:</strong> {esc(clean_text(row.get("note", "")))}</p>
    </div>
  </details>
</article>'''
        )
    return "\n".join(cards)


def heatmap(rows: list[dict]) -> str:
    gaps = Counter()
    for row in rows:
        gaps.update(list_value(row, "residual_gaps"))
    top_gaps = [gap for gap, _ in gaps.most_common(8)]
    regions = ["US", "EU", "UK", "RU", "CN", "global", "other"]
    matrix: dict[tuple[str, str], int] = defaultdict(int)
    for row in rows:
        row_regions = region_buckets(row)
        for gap in list_value(row, "residual_gaps"):
            for region in row_regions:
                matrix[(gap, region)] += 1
    max_cell = max(matrix.values()) if matrix else 1

    head = "".join(f"<th>{esc(region)}</th>" for region in regions)
    body: list[str] = []
    for gap in top_gaps:
        cells = []
        for region in regions:
            count = matrix[(gap, region)]
            alpha = 0.12 + (count / max_cell * 0.78 if max_cell else 0)
            cells.append(
                f'<td><span class="heat" style="--heat:{alpha:.3f}">{count}</span></td>'
            )
        body.append(
            f"<tr><th>{esc(RESIDUAL_GAP_LABELS.get(gap, label_from_id(gap)))}</th>{''.join(cells)}</tr>"
        )
    return f'''
<div class="table-wrap">
  <table class="heat-table">
    <thead><tr><th>Residual gap</th>{head}</tr></thead>
    <tbody>{''.join(body)}</tbody>
  </table>
</div>'''


def option_list(values: list[str], labels: dict[str, str] | None = None) -> str:
    labels = labels or {}
    return "\n".join(
        f'<option value="{esc(value)}">{esc(labels.get(value, label_from_id(value)))}</option>'
        for value in values
    )


def build_html(rows: list[dict]) -> str:
    year_counts = Counter(str(row.get("event_year")) for row in rows)
    evidence_counts = Counter(str(row.get("evidence_level", "")) for row in rows)
    dimension_counts = Counter(dim for row in rows for dim in list_value(row, "dimensions"))
    agency_counts = Counter(agency for row in rows for agency in list_value(row, "agency"))
    gap_counts = Counter(gap for row in rows for gap in list_value(row, "residual_gaps"))

    years = sorted(year_counts)
    evidence_order = [item for item in ["A", "A/B", "B", "B/C", "A/C", "C", "D"] if item in evidence_counts]
    dimensions = [dim for dim, _ in dimension_counts.most_common()]
    date_values = [str(row.get("event_date", "")) for row in rows if row.get("event_date")]
    first_year = min(years)
    last_year = max(years)
    first_date = min(date_values)
    last_date = max(date_values)

    top_dimension, top_dimension_count = dimension_counts.most_common(1)[0]
    ru_count = sum(1 for row in rows if "RU" in region_buckets(row))
    strong_evidence = evidence_counts.get("A", 0) + evidence_counts.get("A/B", 0)

    return f'''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>ProfGames A1 — Events as a Stress Test</title>
<style>
:root {{
  --bg:#fbfaf7; --card:#fff; --soft:#f3f0e8; --text:#1a1713; --muted:#665d52; --light:#8b8378;
  --rule:rgba(40,24,10,.14); --rule-soft:rgba(40,24,10,.08); --accent:#8b5a24;
  --green:#0f6e56; --blue:#315a9c; --gold:#9b7b0e; --red:#993c1d; --violet:#5b3a8a;
  --serif:Charter,Iowan Old Style,Georgia,serif; --sans:Inter,-apple-system,BlinkMacSystemFont,Helvetica,Arial,sans-serif;
  --mono:IBM Plex Mono,SFMono-Regular,Menlo,Consolas,monospace;
}}
*{{box-sizing:border-box}}
html{{scroll-behavior:smooth}}
body{{margin:0;background:var(--bg);color:var(--text);font:16px/1.58 var(--serif)}}
a{{color:var(--accent)}}
.wrap{{max-width:1180px;margin:auto;padding:46px 28px 84px}}
.eyebrow{{font:12px/1.4 var(--sans);letter-spacing:.08em;text-transform:uppercase;color:var(--light)}}
h1{{font-size:44px;line-height:1.08;margin:14px 0 10px;font-weight:520;letter-spacing:-.01em}}
.subtitle{{font-size:19px;color:var(--muted);max-width:900px;margin:0}}
.meta{{font:13px var(--sans);color:var(--muted);display:flex;flex-wrap:wrap;gap:12px;margin-top:20px;padding-top:18px;border-top:1px solid var(--rule)}}
.stats{{display:grid;grid-template-columns:repeat(5,1fr);gap:10px;margin:30px 0}}
.stat{{background:var(--card);border:1px solid var(--rule);border-radius:8px;padding:15px;text-align:center}}
.num{{font-size:31px;line-height:1;font-weight:600;color:var(--accent)}}
.label{{font:11px var(--sans);text-transform:uppercase;letter-spacing:.04em;color:var(--muted);margin-top:6px}}
.note-box,.panel{{background:var(--card);border:1px solid var(--rule);border-radius:8px;padding:20px 23px;margin:20px 0}}
.note-box{{background:var(--soft)}}
.note-box h2,.panel h2{{font-size:24px;line-height:1.16;margin:0 0 10px;font-weight:520}}
.note-box ul{{margin:10px 0 0;padding-left:20px}}
.note-box li{{margin:7px 0}}
.grid-2{{display:grid;grid-template-columns:1fr 1fr;gap:18px;align-items:start}}
.bars{{display:grid;gap:8px;margin-top:14px}}
.bar-row{{display:grid;grid-template-columns:minmax(150px,260px) 1fr 42px;gap:10px;align-items:center;font:13px var(--sans)}}
.bar-label{{color:var(--text)}}
.bar-track{{height:10px;background:var(--soft);border-radius:999px;overflow:hidden;border:1px solid var(--rule-soft)}}
.bar-fill{{height:100%;background:linear-gradient(90deg,var(--accent),#c08a4a);border-radius:999px}}
.bar-count{{font-family:var(--mono);color:var(--muted);text-align:right}}
.table-wrap{{overflow-x:auto}}
table{{width:100%;border-collapse:collapse;font:13px/1.42 var(--sans)}}
th,td{{border-bottom:1px solid var(--rule-soft);padding:9px 8px;text-align:left;vertical-align:middle}}
th{{color:var(--muted);font-weight:600}}
.heat-table th:first-child{{min-width:280px}}
.heat{{display:inline-flex;align-items:center;justify-content:center;min-width:34px;height:25px;border-radius:4px;background:rgba(139,90,36,var(--heat));font-family:var(--mono);color:#1a1713}}
.viz-frame{{background:var(--card);border:1px solid var(--rule);border-radius:8px;padding:18px;margin:20px 0;overflow-x:auto}}
.timeline-svg{{width:100%;min-width:900px;height:auto;display:block}}
.grid-line{{stroke:rgba(40,24,10,.10);stroke-width:1}}
.lane-line{{stroke:rgba(40,24,10,.22);stroke-width:1}}
.year-label,.axis-label{{font:11px var(--mono);fill:var(--light)}}
.lane-label{{font:11px var(--sans);fill:var(--muted)}}
.evt-dot{{stroke:white;stroke-width:1.1;fill:var(--blue);opacity:.72}}
.evt-dot.anchor{{stroke:#1a1713;stroke-width:1.5;opacity:1}}
.ev-a,.ev-a-b{{fill:var(--green);background:var(--green)}} .ev-b{{fill:var(--blue);background:var(--blue)}} .ev-b-c,.ev-c{{fill:var(--gold);background:var(--gold)}} .ev-a-c{{fill:var(--violet);background:var(--violet)}} .ev-d{{fill:#6b6356;background:#6b6356}}
.arc{{stroke:var(--red);stroke-width:1.4;fill:none;opacity:.78}} .arc.escalation{{stroke:var(--violet)}} .arc.split{{stroke:var(--green);stroke-dasharray:5 3}}
.timeline-legend text{{font:12px var(--sans);fill:var(--muted)}}
.pair-grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(280px,1fr));gap:12px;margin-top:14px}}
.pair-card{{background:var(--card);border:1px solid var(--rule);border-left:3px solid var(--red);border-radius:8px;padding:16px 18px}}
.split-card{{border-left-color:var(--green)}}
.pair-head{{display:flex;justify-content:space-between;gap:10px;align-items:center;font:13px var(--sans);color:var(--muted);margin-bottom:10px}}
.pair-head strong{{font:17px var(--serif);color:var(--text);font-weight:520}}
.pair-head span{{background:var(--soft);border-radius:4px;padding:3px 8px}}
.pair-events{{display:grid;grid-template-columns:1fr auto 1fr;gap:9px;align-items:center;font:13px/1.35 var(--sans)}}
.pair-events em{{font:11px var(--mono);font-style:normal;color:var(--light)}}
.pair-arrow{{font-size:22px;color:var(--red)}}
.pair-card p{{margin:12px 0 0;color:var(--muted)}}
.trend-grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(330px,1fr));gap:14px;margin-top:14px}}
.trend-card{{background:var(--card);border:1px solid var(--rule);border-radius:8px;padding:16px 18px}}
.trend-card h3{{font-size:18px;margin-top:0}}
.trend-card p{{color:var(--muted);font-size:14px;margin:0 0 10px}}
.mini-trend{{width:100%;height:auto;display:block}}
.trend-line{{stroke-width:2.2;stroke-linecap:round;stroke-linejoin:round}}
.endpoint{{font:10px var(--sans)}}
.mediation-table td{{min-width:190px;font-size:12px;vertical-align:top}}
.mediation-table td strong{{display:block;font:18px var(--mono);color:var(--accent);margin-bottom:5px}}
.pill{{display:inline-block;min-width:24px;text-align:center;border-radius:3px;color:white;font:10px var(--mono);padding:1px 4px;margin:2px 4px 2px 0}}
.more{{font:11px var(--sans);color:var(--muted);margin-top:4px}}
.filters{{position:sticky;top:0;background:rgba(251,250,247,.96);border-top:1px solid var(--rule);border-bottom:1px solid var(--rule);padding:12px 0;margin:30px 0 20px;z-index:2}}
.filter-grid{{display:grid;grid-template-columns:repeat(5,minmax(120px,1fr));gap:10px}}
label{{font:11px var(--sans);text-transform:uppercase;letter-spacing:.05em;color:var(--muted);display:grid;gap:5px}}
select,input{{width:100%;font:14px var(--sans);padding:8px 9px;border:1px solid var(--rule);border-radius:6px;background:var(--card);color:var(--text)}}
.result-count{{font:13px var(--sans);color:var(--muted);margin-top:10px}}
.events{{display:grid;gap:14px}}
.event-card{{background:var(--card);border:1px solid var(--rule);border-radius:8px;padding:19px 22px}}
.event-card.hidden{{display:none}}
.event-meta{{display:flex;flex-wrap:wrap;gap:10px;font:11px var(--mono);letter-spacing:.04em;text-transform:uppercase;color:var(--light)}}
h3{{font-size:21px;line-height:1.24;margin:8px 0 10px;font-weight:520}}
.chip-row,.detail-block div{{display:flex;flex-wrap:wrap;gap:6px;margin:8px 0}}
.chip{{font:11px var(--sans);padding:3px 8px;border-radius:4px;background:var(--soft);color:var(--muted)}}
.evidence{{color:white;background:var(--blue)}}
.why{{color:var(--muted)}}
details{{background:var(--soft);border-radius:6px;padding:10px 13px;margin-top:12px}}
summary{{font:13px var(--sans);cursor:pointer;color:var(--accent)}}
.detail-block{{margin-top:8px}}
.sources{{display:flex;flex-wrap:wrap;gap:8px}}
.note{{font-size:14px;color:var(--muted);margin:10px 0 0}}
.muted{{color:var(--muted)}}
footer{{margin-top:56px;border-top:1px solid var(--rule);padding-top:18px;font:12px var(--sans);color:var(--muted);display:flex;flex-wrap:wrap;gap:12px}}
@media(max-width:900px){{.stats{{grid-template-columns:repeat(2,1fr)}}.grid-2{{grid-template-columns:1fr}}.filter-grid{{grid-template-columns:1fr 1fr}}h1{{font-size:34px}}}}
@media(max-width:560px){{.wrap{{padding:28px 16px 64px}}.filter-grid{{grid-template-columns:1fr}}.bar-row{{grid-template-columns:1fr 1fr 34px}}.bar-label{{grid-column:1 / -1}}}}
</style>
</head>
<body>
<main class="wrap">
  <header>
    <div class="eyebrow"><a href="index.html">ProfGames in English</a> · <a href="../a-events.html">canonical RU A1</a> · event layer</div>
    <h1>Events as a Stress Test</h1>
    <p class="subtitle">An English-facing browser for the A1 event layer: {len(rows)} signals from {first_year}-{last_year}, mapped to the ProfGames framework by dimensions of mobility, agency parameters, evidence level and residual gaps.</p>
    <div class="meta">
      <span>Dataset: profgames_ai_signals.jsonl</span>
      <span>Range: {esc(first_date)} to {esc(last_date)}</span>
      <span><a href="../profgames_ai_signals.jsonl">canonical JSONL</a></span>
      <span><a href="factcheck.html">English fact-check</a></span>
      <span><a href="https://github.com/scadastrangelove/profgames">GitHub</a></span>
    </div>
  </header>

  <section class="stats">
    <div class="stat"><div class="num">{len(rows)}</div><div class="label">signals</div></div>
    <div class="stat"><div class="num">{len(years)}</div><div class="label">years</div></div>
    <div class="stat"><div class="num">{strong_evidence}</div><div class="label">A or A/B</div></div>
    <div class="stat"><div class="num">{top_dimension_count}</div><div class="label">{esc(DIMENSION_LABELS[top_dimension].split(" ", 1)[0])} signals</div></div>
    <div class="stat"><div class="num">{ru_count}</div><div class="label">RU bucket</div></div>
  </section>

  <section class="note-box">
    <h2>How to read this layer</h2>
    <ul>
      <li>This is not a prediction engine. It is a stress-test layer: public events are coded against the same framework used in the cycle.</li>
      <li>The densest signal class is {esc(DIMENSION_LABELS[top_dimension])}: the dataset sees pressure first in lateral professional moves, employment form and industry return.</li>
      <li>Evidence is strongest where courts, regulators, payroll data or published research leave an audit trail; corporate causality is deliberately coded more cautiously.</li>
      <li>For the Russian fork, the data are thinner but structurally important: the open gap is direct causal evidence on task change, layoffs and credential portability after 2022.</li>
    </ul>
  </section>

  <section class="panel">
    <h2>1. Timeline and walkback geometry</h2>
    <p class="muted">All 177 signals are placed on four carrier lanes. Small dots are events; outlined dots are curated anchors. Red arcs mark walkbacks or qualified outcomes, violet marks escalation, and dashed green marks split decisions where the same institutional question receives different answers.</p>
    <div class="viz-frame">{timeline_svg(rows)}</div>
  </section>

  <section class="grid-2">
    <div class="panel">
      <h2>Walkback pairs</h2>
      <p class="muted">The important pattern is not "AI claim was false". It is that AI attribution often has to be narrowed after it meets service quality, labor, legal or trust constraints.</p>
      <div class="pair-grid">{pair_cards(rows)}</div>
    </div>
    <div class="panel">
      <h2>Split decisions</h2>
      <p class="muted">Some events are not reversals. They show the same pressure producing different institutional equilibria.</p>
      <div class="pair-grid">{split_cards(rows)}</div>
    </div>
  </section>

  <section class="panel">
    <h2>2. Trend lines behind the events</h2>
    <p class="muted">These compact charts keep the Russian A1 article's visual logic: the crisis is not one curve, but several domain curves converging on the same institutional reaction: restoring provenance and responsibility.</p>
    <div class="trend-grid">{trend_panels()}</div>
  </section>

  <section class="panel">
    <h2>3. Mediation compression matrix</h2>
    <p class="muted">Events are grouped by the layer of mediation they stress: entry translation, coordination, decision rights and trust/regulation. Counts are heuristic and multi-year; the table is an orientation aid, not a statistical model.</p>
    {mediation_matrix(rows)}
  </section>

  <section class="grid-2">
    <div class="panel">
      <h2>4. Signals by year</h2>
      <div class="bars">{bar_rows(Counter({year: year_counts[year] for year in years}))}</div>
    </div>
    <div class="panel">
      <h2>Evidence levels</h2>
      <div class="bars">{bar_rows(Counter({level: evidence_counts[level] for level in evidence_order}))}</div>
    </div>
  </section>

  <section class="grid-2">
    <div class="panel">
      <h2>5. Mobility dimensions</h2>
      <div class="bars">{bar_rows(dimension_counts, DIMENSION_LABELS)}</div>
    </div>
    <div class="panel">
      <h2>Agency parameters</h2>
      <div class="bars">{bar_rows(agency_counts, AGENCY_LABELS)}</div>
    </div>
  </section>

  <section class="panel">
    <h2>6. Residual gaps by region bucket</h2>
    <p class="muted">Counts are multi-label: one signal can close several gaps and belong to several region buckets. The heatmap shows where the current evidence base is dense, not where the underlying problem is largest.</p>
    {heatmap(rows)}
  </section>

  <nav class="filters">
    <div class="filter-grid">
      <label>Year
        <select id="yearFilter"><option value="all">All years</option>{option_list(years)}</select>
      </label>
      <label>Region
        <select id="regionFilter"><option value="all">All regions</option>{option_list(["US","EU","UK","RU","CN","global","other"])}</select>
      </label>
      <label>Evidence
        <select id="evidenceFilter"><option value="all">All evidence</option>{option_list(evidence_order)}</select>
      </label>
      <label>Dimension
        <select id="dimensionFilter"><option value="all">All dimensions</option>{option_list(dimensions, DIMENSION_LABELS)}</select>
      </label>
      <label>Search
        <input id="searchFilter" type="search" placeholder="Klarna, provenance, layoffs...">
      </label>
    </div>
    <div class="result-count"><span id="visibleCount">{len(rows)}</span> / {len(rows)} events visible</div>
  </nav>

  <section class="events" id="events">
    {event_cards(rows)}
  </section>

  <footer>
    <span>Sergey Gordeychik</span>
    <span><a href="https://t.me/aiakyn">telegram</a></span>
    <span><a href="https://teletype.in/@sergey_gordey">teletype</a></span>
    <span><a href="https://github.com/scadastrangelove/profgames">github</a></span>
    <span>#profgames</span>
  </footer>
</main>
<script>
const cards = Array.from(document.querySelectorAll('.event-card'));
const controls = {{
  year: document.getElementById('yearFilter'),
  region: document.getElementById('regionFilter'),
  evidence: document.getElementById('evidenceFilter'),
  dimension: document.getElementById('dimensionFilter'),
  search: document.getElementById('searchFilter')
}};
const visibleCount = document.getElementById('visibleCount');
function applyFilters() {{
  const year = controls.year.value;
  const region = controls.region.value;
  const evidence = controls.evidence.value;
  const dimension = controls.dimension.value;
  const query = controls.search.value.trim().toLowerCase();
  let visible = 0;
  for (const card of cards) {{
    const okYear = year === 'all' || card.dataset.year === year;
    const okRegion = region === 'all' || card.dataset.regions.split('|').includes(region);
    const okEvidence = evidence === 'all' || card.dataset.evidence === evidence;
    const okDimension = dimension === 'all' || card.dataset.dimensions.split('|').includes(dimension);
    const okSearch = !query || card.dataset.search.includes(query);
    const show = okYear && okRegion && okEvidence && okDimension && okSearch;
    card.classList.toggle('hidden', !show);
    if (show) visible += 1;
  }}
  visibleCount.textContent = visible;
}}
Object.values(controls).forEach(control => control.addEventListener('input', applyFilters));
</script>
</body>
</html>
'''


def main() -> None:
    rows = load_signals()
    html_text = build_html(rows)
    (OUT / "a-events.html").write_text(html_text, encoding="utf-8")
    print(f"wrote {OUT / 'a-events.html'} ({len(rows)} signals)")


if __name__ == "__main__":
    main()

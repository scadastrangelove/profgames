#!/usr/bin/env python3
"""Build the first English public layer for the ProfGames fact-check pack.

The root factcheck.json stays canonical. This script emits an English-facing
audit pack with stable ids, evidence levels, statuses, source URLs and concise
English claim summaries, while preserving the original Russian text for audit.
"""

from __future__ import annotations

import html
import json
from collections import Counter, defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUT = Path(__file__).resolve().parent


CLAIMS_EN: dict[str, tuple[str, str]] = {
    "ru-01": (
        "Russian Government Decree No. 1949: IT firms and university training",
        "Large accredited Russian IT firms are required to sign university agreements and channel up to about 3% of tax-benefit savings into IT education; the exact numeric thresholds need cautious wording.",
    ),
    "ru-02": (
        "Russian IT accreditation requirements",
        "Accreditation uses a 30% IT-revenue threshold, OKVED 62/63 activity codes and wage requirements; the 70% threshold applies to tax-benefit eligibility, not accreditation itself.",
    ),
    "ru-03": (
        "Russian IT tax and social-contribution benefits in 2026",
        "The verified baseline is a 5% profit-tax rate through 2030, a two-tier social-contribution regime around the RUB 2.979m base, and a 6% IT mortgage with a RUB 9m base limit; the claimed 3% profit tax needs correction.",
    ),
    "ru-04": (
        "Registry of accredited Russian IT companies",
        "The public count is roughly 18,000-20,000 accredited companies around 2024-2025, with annual checks affecting the exact number.",
    ),
    "ru-05": (
        "Russian IT labor market, 2025",
        "Russian IT vacancies fell by roughly a quarter to a third in 2025, the hh index reached 16.1 in Q3, entry-level roles weakened sharply, while AI/ML, security and senior specialties stayed comparatively expensive.",
    ),
    "ru-06": (
        "Russian IT emigration, 2022-2024",
        "Public estimates support an order-of-magnitude figure of about 80,000-100,000 net IT emigrants after 2022; precise official MVD/Rosstat totals are not publicly available.",
    ),
    "ru-07": (
        "OutRush wave 4 on Russian emigration and return",
        "OutRush wave 4 (n=8,600, July-November 2024) reports 8% returnees, another 5% planning return, and 54% considering return under political change; the sample is educated/IT-skewed and not random.",
    ),
    "ru-08": (
        "RANEPA brain-drain monitoring",
        "Secondary reporting attributes an approximate 10% returnee figure to RANEPA monitoring, broadly consistent with OutRush, but the direct public primary source was not located.",
    ),
    "ru-09": (
        "Russia's 2026-2030 migration-policy concept",
        "The 2026-2030 concept confirms a more selective migration stance, including language about carriers of traditional values; 2025 citizenship and compatriot-return figures show a sharp decline from earlier peaks.",
    ),
    "ru-10": (
        "The 850,000-person controlled-persons registry",
        "The 850,000 figure belongs to Russia's migration-enforcement registry for foreigners with terminated grounds of stay; it must not be used as an IT-sector cage indicator.",
    ),
    "ru-11": (
        "School 21 by Sber",
        "School 21 is a free peer-to-peer Sber training program with 16+ Russian campuses; its 100% employment claim is a corporate narrative without independent public verification.",
    ),
    "ru-12": (
        "Yandex SourceCraft AI agents",
        "Yandex B2B Tech reports a 50% quarterly increase in SourceCraft AI-agent use and 60% of developers using agent mode; these are corporate self-disclosed figures.",
    ),
    "ru-13": (
        "Rosatom / Greenatom digital staffing and 1C:ERP migration",
        "Rosatom/Greenatom publicly supports large-scale 1C deployment figures; broader digital-staffing targets such as 25k to 55k require primary press-release verification.",
    ),
    "ru-14": (
        "Top Russian government IT suppliers in 2024",
        "CNews Analytics reports about RUB 199bn revenue for the top 20 IT suppliers to the Russian public sector in 2024; treat as a secondary analytics source.",
    ),
    "ru-15": (
        "Liga Digital Economy and Program Product revenues",
        "Industry rankings place Liga Digital Economy and Program Product around RUB 11-12bn revenue in 2024; primary company financial statements need separate verification.",
    ),
    "ru-16": (
        "Russian Ministry of Digital Development Plan 2030",
        "The ministerial 2030 target is 700,000 new developers, with 2024 intake and student figures used as projections and capacity indicators, not measured outcomes.",
    ),
    "ru-17": (
        "Russian vacancies offering training or reskilling",
        "hh.ru/Forbes reporting indicates a growing share of vacancies open to candidates without experience and with training/reskilling offers, consistent with a shortage market.",
    ),
    "ru-18": (
        "Russian IT market segmentation",
        "The big-tech / state / midmarket / startup split is a useful analytical estimate but lacks a public methodological source from ARPP, RUSSOFT or HSE ISSEK.",
    ),
    "ai-19": (
        "Stanford HAI AI Index 2026: core figures",
        "AI Index 2026 robustly supports rapid GenAI adoption, broad organizational use, productivity gains in support/coding/marketing, US private-investment dominance and falling net AI-researcher inflow into the US.",
    ),
    "ai-20": (
        "Anthropic Labour Market Impacts, March 2026",
        "Anthropic finds that higher observed AI exposure is associated with lower BLS 2024-2034 employment projections, especially for programming, customer-service and data-entry work; it is observational, not causal.",
    ),
    "ai-21": (
        "Anthropic Economic Index: geographic concentration",
        "Anthropic's Economic Index shows concentrated Claude use by US state and a large computer-and-mathematical occupation share in both Claude.ai and API traffic.",
    ),
    "ai-22": (
        "Stanford Digital Economy Lab: Canaries in the Coal Mine",
        "ADP payroll microdata support a 13-16% relative employment decline for workers aged 22-25 in highly AI-exposed occupations, with young software developers down about 20% from the 2022 peak.",
    ),
    "reg-23": (
        "Teaching Council Ireland: processing times and routes",
        "The corrected Teaching Council Ireland baseline is up to 12 weeks for overseas-qualified teachers, 6 weeks for Ireland-qualified teachers, and Routes 1/2 as standard overseas routes; Route 4 is special-education specific.",
    ),
    "reg-24": (
        "GPhC OSPAP UK",
        "OSPAP applications fell from 909 in 2022 to 302 in 2023, while oversubscribed courses and a coming one-year track show the translator pathway itself becoming a bottleneck.",
    ),
    "reg-25": (
        "German Skilled Immigration Act: three phases",
        "Germany's 2023-2024 reform lowered Blue Card thresholds, introduced recognition partnerships and launched the Opportunity Card, including an IT route based on experience without a degree.",
    ),
    "reg-26": (
        "UK apprenticeships",
        "UK apprenticeship starts fell from the 2015/16 peak of 509,400 to 354,000 in 2024/25, with under-19 starts only about 21%; the policy frame shifted toward the Growth and Skills Levy and Skills England.",
    ),
    "reg-27": (
        "China Young Thousand Talents",
        "Science 2023 evidence shows Young Thousand Talents returnees publishing 27% more papers and 144% more last-author papers than matched overseas peers.",
    ),
    "reg-28": (
        "Chinese returnees, 1978-2024",
        "Chinese official statistics support a massive long-run returnee channel: more than 7 million students went abroad and more than 5 million returned by 2024.",
    ),
    "corp-29a": (
        "IBM Apprenticeship and SkillsBuild",
        "IBM's apprenticeship and SkillsBuild programs are real, but the specific '$250k investment in new collar' figure was not verified and should be removed or sourced separately.",
    ),
    "corp-29b": (
        "JPMorgan AI programs",
        "JPMorgan's AI upskilling and internal deployment claims should be treated as corporate narrative unless tied to specific filings or audited program metrics.",
    ),
    "corp-29c": (
        "Big Four UK graduate cuts",
        "Evidence supports reduced graduate hiring or changed intake patterns at major professional-services firms, but AI causality should be framed carefully and not overstated.",
    ),
    "corp-29d": (
        "Salesforce / Benioff",
        "Salesforce is a strong corporate narrative case for AI-linked efficiency and support-staff reduction, but the evidence remains management self-disclosure.",
    ),
    "corp-29e": (
        "Klarna",
        "Klarna is a strong corporate narrative case: AI assistant performance and headcount/productivity claims are public, but they remain company-reported rather than independent labor statistics.",
    ),
    "corp-29f": (
        "Amazon's October 2025 layoffs",
        "Amazon's roughly 14,000 layoff announcement should not be coded as AI-driven: Jassy explicitly framed the main rationale as culture and organizational layering.",
    ),
    "corp-29g": (
        "Microsoft 2025 layoffs",
        "Microsoft's 2025 layoff figures are real corporate restructuring signals, but direct AI-replacement causality remains weaker than media framing suggests.",
    ),
    "corp-29h": (
        "Bloomberry / Live Data Technologies jobs analysis",
        "The Bloomberry analysis is useful for role-level exposure and orchestration patterns, but it should be treated as private-sector labor analytics rather than an official series.",
    ),
    "corp-29i": (
        "PwC AI Jobs Barometer 2025",
        "PwC's AI Jobs Barometer supports wage/productivity differences between AI-exposed and less exposed jobs, but it is an analytical report rather than administrative evidence.",
    ),
    "corp-29j": (
        "WEF Future of Jobs 2025",
        "WEF's Future of Jobs survey is a broad employer-expectations source for skill shifts and role disruption, not a measured employment outcome.",
    ),
    "corp-29k": (
        "MIT NANDA: '95% of AI pilots fail'",
        "MIT NANDA is useful for the enterprise-adoption failure narrative, but the exact '95%' headline must be tied to its study scope and not universalized.",
    ),
    "corp-29l": (
        "Anthropic CEO Dario Amodei opinion",
        "Amodei's warnings are important executive opinion and forecast material, not evidence that the forecast has already occurred.",
    ),
    "reg-30": (
        "UAE National AI Strategy 2031",
        "The UAE case is anchored in National AI Strategy 2031, MBZUAI and Stargate UAE; specific corporate-retention claims remain corporate narrative unless independently verified.",
    ),
    "b-ire-01": (
        "Teaching Council Ireland Timebound Provision",
        "The October 2025 revised regulations let overseas-qualified teachers complete induction in Ireland through the Timebound Provision until 31 December 2027.",
    ),
    "b-ire-02": (
        "AI cheating in UK universities, 2023-2026",
        "UK higher education shows a sharp rise in AI-related academic misconduct, very high student AI use, renewed interest in in-class written exams, weak teacher training and limited policy effectiveness.",
    ),
    "b-ire-03": (
        "Teaching Council Ireland registration routes",
        "Teaching Council Ireland has five registration routes; the corrected route for overseas-qualified general teachers is Route 1 or 2, not Route 4.",
    ),
    "b-ger-01": (
        "EU AI Act implementation timeline",
        "The EU AI Act enters application in phases from February 2025 through August 2026, with obligations distributed across providers, deployers, importers and distributors.",
    ),
    "b-ger-02": (
        "AI Liability Directive withdrawal",
        "The European Commission withdrew the AI Liability Directive in early 2025, leaving AI harm mainly to product-liability law, the AI Act and national tort law.",
    ),
    "b-ger-03": (
        "German Product Liability Act draft, September 2025",
        "Germany's September 2025 ProdHaftG-E draft implements the updated EU Product Liability Directive and matters for AI-driven product failures and supply-chain risk allocation.",
    ),
    "b-ger-04": (
        "German court 6 O 151/23 on AI output responsibility",
        "A German court held a business-information service operator directly responsible for false AI-generated content because the company made the AI output its own.",
    ),
    "b-ger-05": (
        "Ingenieur: protected title versus regulated profession",
        "In Germany, Ingenieur is a protected title in some federal states but not a regulated profession in the immigration sense; recognition is needed to use the title, not to work in an engineering role.",
    ),
    "b-ind-01": (
        "PLAB to UKMLA transition",
        "From 2024-2025, the GMC replaced PLAB with UKMLA as a common assessment for UK-trained and international medical graduates, alongside EPIC's replacement by MyIntealth.",
    ),
    "b-ind-02": (
        "UK Medical Training (Prioritisation) Act",
        "The 5 March 2026 Act gives UK-trained graduates priority in Foundation Programme and specialty training places, while preserving equal access for some already-registered NHS-working IMGs.",
    ),
    "b-ind-03": (
        "UK medical-training competition ratios",
        "UK medical training faces very high competition: 2025 data show 91,999 applications for 12,833 specialty posts, with 2026 already above 47,000 applicants.",
    ),
    "b-chn-01": (
        "AI-generated biomedical papers: China concentration",
        "The Pangram 2025/2026 analysis finds much higher AI-flagged biomedical text shares in Chinese and South Korean institutional papers than in US-affiliated papers.",
    ),
    "b-chn-02": (
        "AI-related retractions: Chinese first authors",
        "A Frontiers systematic review reports China accounting for 72.2% of first authors among AI-related retracted papers, with shorter time-to-retraction in China and India.",
    ),
    "b-chn-03": (
        "Saveetha University extreme retraction case",
        "Saveetha University is a cross-country illustration of extreme paper-mill behavior, with dozens of retractions and questionable-authorship findings.",
    ),
    "b-rus-it-01": (
        "Russia's 152-FZ amendment on personal-data collection",
        "Federal Law No. 23-FZ changed Article 18(5) of 152-FZ from 1 July 2025: it restricts primary collection of Russian citizens' personal data through foreign databases, but is not a full ban on cross-border transfer.",
    ),
    "b-rus-it-02": (
        "GitHub sanctions and Russian developers",
        "GitHub remains available for free public personal use in non-sanctioned Russian regions, but paid/corporate accounts linked to sanctioned entities can be blocked under US trade-control rules.",
    ),
    "b-rus-it-03": (
        "Workslop in IT: Stack Overflow, Sonar, DORA and St. Louis Fed",
        "Multiple 2025-2026 sources show high AI-tool adoption but low trust, weak verification, more instability or defects, and a gap between individual time savings and aggregate productivity gains.",
    ),
    "b-rus-it-04": (
        "Workslop as a tragedy of the commons",
        "A qualitative 2026 arXiv analysis frames AI slop in software development as a tragedy of the commons: individual speed gains externalize review, maintenance and quality costs.",
    ),
    "b-rus-it-05": (
        "Global tech-layoff frame for 2026",
        "RationalFX early-2026 layoff figures are useful as a global frame for tech layoffs and AI/automation attribution, but they are not official labor statistics.",
    ),
    "b-rus-it-06": (
        "Softline AI-linked staff optimization",
        "Softline is the strongest local Russian Oracle analogue: about 800 fewer employees from Q3 2025 to Q1 2026, AI-linked efficiency language, and Q1 2026 turnover up 5% YoY.",
    ),
    "b-rus-it-07": (
        "Sber AI-assisted efficiency cuts",
        "Sber provides a rare public allocator case: Gref described AI-assisted identification of inefficient employees, while Putin reframed the issue as management responsibility.",
    ),
    "b-rus-it-08": (
        "Positive Technologies quiet restructuring",
        "Positive Technologies is useful as a quiet-restructuring case, not an AI-causality case: employee and union-linked reports described sizable layoffs without confirmed AI replacement.",
    ),
    "b-rus-it-09": (
        "Russian IT junior squeeze",
        "Russian IT moved toward an employer market in 2025-2026, with fewer vacancies, more resumes per vacancy and stronger competition for entry-level developers from both experienced candidates and AI-enabled workflows.",
    ),
    "b-rus-it-10": (
        "Russian IT wage polarization and shortage-with-layoffs paradox",
        "Russian IT can cut staff while still having shortages: mass and entry-level roles are squeezed, while AI/ML, cybersecurity, DevOps/SRE and senior profiles remain expensive.",
    ),
}


GAPS_EN = {
    "gap-01": ("Direct RANEPA brain-drain primary source", "Only secondary links via Meduza were located for the roughly 10% returnee figure."),
    "gap-02": ("Russian IT market segment structure", "No public 2025-2026 ARPP/RUSSOFT/HSE ISSEK source gives the required big-tech / state / midmarket / startup revenue split."),
    "gap-03": ("Exact numeric thresholds for Decree No. 1949", "The relevant 2026 by-laws were not yet consolidated in public legal systems at the fact-check date."),
    "gap-04": ("CNews analytics figures", "Some CNews Analytics values are behind paid/closed access; mark as secondary source only."),
    "gap-05": ("Avito Jobs AI-vacancy doubling", "Corporate analytics without a public primary methodology note."),
    "gap-06": ("Greenatom digital-employment targets", "Specific 25k / 55k staff numbers lack located public Rosatom/Greenatom primary releases."),
    "gap-07": ("Direct causal AI payroll evidence for Russia", "Russia lacks a public Brynjolfsson-Chandar-Chen-style payroll microdata study."),
    "gap-08": ("Bloomberry / Live Data Technologies analogue for Russia", "No open Russian vacancy dataset breaks PM/BA/coordinator/HRBP dynamics into tactical vs accountable roles."),
    "gap-09": ("Workslop in Russian corporate context", "No BetterUp-style Russian corporate study was located."),
    "gap-10": ("Long-term effects of the junior squeeze", "The 7-10 year horizon central to the cycle is not yet observable; current Stanford evidence covers 2022-2025."),
    "gap-11": ("UAE long-term spillover", "Long-run expat-model sustainability and MBZUAI graduate-retention data are still speculative or unavailable."),
    "gap-12": ("Effect of Russian Decree No. 1949", "First outcomes will only appear in 2026-2027, and methodology for counting the education share is contested."),
    "gap-13": ("Tactical versus accountable orchestrators", "The split is conceptually strong but not yet operationalized in comparable data."),
    "gap-14": ("Cross-country junior:middle:senior comparison", "No unified methodology exists across PwC, BLS, hh.ru and China MOE-type sources."),
    "gap-15": ("DeepSeek/Moonshot/Zhipu hiring microdata", "Qualitative stories exist, but panel-level hiring data do not."),
    "gap-16": ("Ireland-specific AI-cheating data", "UK studies provide context; Ireland-specific surveys were not found."),
    "gap-17": ("GitHub paid-subscriber blocking specifics", "Only secondary sourcing was located for full blocking of paid Russian subscribers in 2025."),
    "gap-18": ("Subsequent applications of 6 O 151/23", "The precedent is confirmed; later applications are not tracked here."),
    "gap-19": ("Independent School 21 / Innopolis employment verification", "Employment claims are company PR data without third-party evaluation."),
    "gap-20": ("Russian IT relocation figures, 2024-2026", "Post-2022 official figures remain partial; later precise relocation numbers are not public."),
}


PASS_LABELS = {
    "russia": "Russian IT sector",
    "ai_research": "AI research and labor evidence",
    "regulators_corporate": "Regulators and corporate cases",
    "b-ireland": "Biography B1: Irish teacher",
    "b-germany": "Biography B2: German engineer",
    "b-india-uk": "Biography B3: Indian doctor in the UK",
    "b-china": "Biography B4: Chinese returnee scientist",
    "b-russia-it": "Biography B5: Russian IT specialist",
}

PASS_ORDER = [
    "ai_research",
    "regulators_corporate",
    "b-ireland",
    "b-germany",
    "b-india-uk",
    "b-china",
    "russia",
    "b-russia-it",
]


def norm_status(status: str) -> str:
    return status.replace("_", " ")


def build_json() -> dict:
    source = json.loads((ROOT / "factcheck.json").read_text(encoding="utf-8"))
    claims = []
    for claim in source["claims"]:
        title, summary = CLAIMS_EN[claim["id"]]
        claims.append(
            {
                "id": claim["id"],
                "pass": claim["pass"],
                "pass_label": PASS_LABELS.get(claim["pass"], claim["pass"]),
                "title": title,
                "claim_summary": summary,
                "status": claim["status"],
                "evidence_level": claim["evidence_level"],
                "geographic_scope": claim.get("geographic_scope"),
                "date_relevant": claim.get("date_relevant"),
                "source_urls": [s.get("url") for s in claim.get("sources", []) if s.get("url")],
                "sources": claim.get("sources", []),
                "keywords": claim.get("keywords", []),
                "original_ru": {
                    "topic": claim.get("topic"),
                    "claim": claim.get("claim"),
                    "caveats": claim.get("caveats", []),
                    "corrections": claim.get("corrections", []),
                    "recommended_phrasing": claim.get("recommended_phrasing", ""),
                },
            }
        )
    pass_rank = {pass_id: index for index, pass_id in enumerate(PASS_ORDER)}
    claims.sort(key=lambda claim: (pass_rank.get(claim["pass"], 999), claim["id"]))

    gaps = []
    for gap in source.get("gaps", []):
        title, missing = GAPS_EN.get(gap["id"], (gap.get("topic", gap["id"]), gap.get("missing") or gap.get("note", "")))
        gaps.append(
            {
                "id": gap["id"],
                "title": title,
                "missing": missing,
                "geographic_scope": gap.get("geographic_scope"),
                "criticality": gap.get("criticality") or gap.get("priority"),
                "original_ru": gap,
            }
        )

    return {
        "meta": {
            "title": "ProfGames — English Fact-Check Audit Layer",
            "language": "en",
            "source_language": "ru",
            "version": "0.1-en",
            "created": "2026-05-27",
            "canonical_pack": "../factcheck.json",
            "canonical_version": source["meta"]["version"],
            "fact_check_date": source["meta"]["fact_check_date"],
            "data_relevance_date": source["meta"]["data_relevance_date"],
            "translation_status": "Concise English audit summaries; original Russian claim text is preserved in original_ru for canonical wording.",
            "evidence_levels": source["meta"]["evidence_levels"],
            "status_values": source["meta"]["status_values"],
        },
        "summary": {
            "stats": source["summary"]["stats"],
            "approximate_pass_rate": source["summary"]["approximate_pass_rate"],
            "key_findings": [
                "The pack contains 65 audited claims with stable IDs, source URLs, status labels and A/B/C/D evidence levels.",
                "The strongest evidence comes from administrative sources, official regulators, payroll/labor microdata and major published research packs.",
                "For English readers, the general entry point is AI research, regulators, corporate cases and the international biography claims; Russia is kept as a later, separate fork.",
                "The biographical sections show how provenance translators work through registries, licenses, chambers, state programs and network traces.",
                "Russian-specific conclusions should be framed as a segmented-market problem: large anchor employers and the state can fund training, while entry-level roles and independent intermediaries are exposed.",
                "The most important unresolved Russian gap is direct causal payroll evidence on AI effects, comparable to the Stanford/ADP evidence for the US.",
            ],
        },
        "claims": claims,
        "gaps": gaps,
    }


def render_html(pack: dict) -> str:
    stats = pack["summary"]["stats"]
    status_counts = Counter(c["status"] for c in pack["claims"])
    pass_groups: dict[str, list[dict]] = defaultdict(list)
    for claim in pack["claims"]:
        pass_groups[claim["pass"]].append(claim)

    def esc(value: object) -> str:
        return html.escape("" if value is None else str(value))

    def status_class(status: str) -> str:
        return status.replace("_", "-")

    cards = []
    ordered_passes = [pass_id for pass_id in PASS_ORDER if pass_id in pass_groups]
    ordered_passes.extend(pass_id for pass_id in pass_groups if pass_id not in ordered_passes)

    for pass_id in ordered_passes:
        items = pass_groups[pass_id]
        cards.append(f'<section class="pass-section" id="{esc(pass_id)}">')
        cards.append(f"<h2>{esc(items[0]['pass_label'])}</h2>")
        for c in items:
            source_links = " ".join(
                f'<a href="{esc(url)}" target="_blank" rel="noopener">source {i}</a>'
                for i, url in enumerate(c["source_urls"], 1)
            )
            original = c["original_ru"]
            cards.append(
                f"""
<article class="claim" data-status="{esc(c['status'])}" data-level="{esc(c['evidence_level'])}" data-pass="{esc(c['pass'])}">
  <div class="claim-head">
    <div class="claim-id">{esc(c['id'])}</div>
    <h3>{esc(c['title'])}</h3>
    <div class="tags">
      <span class="tag status {status_class(c['status'])}">{esc(norm_status(c['status']))}</span>
      <span class="tag level level-{esc(c['evidence_level']).lower()}">evidence {esc(c['evidence_level'])}</span>
      <span class="tag">{esc(c.get('geographic_scope') or 'global')}</span>
    </div>
  </div>
  <p class="claim-summary">{esc(c['claim_summary'])}</p>
  <div class="sources">{source_links or '<span class="muted">No source URL listed</span>'}</div>
  <details>
    <summary>Original Russian canonical wording</summary>
    <p><strong>Topic:</strong> {esc(original.get('topic'))}</p>
    <p><strong>Claim:</strong> {esc(original.get('claim'))}</p>
    <p><strong>Recommended wording:</strong> {esc(original.get('recommended_phrasing'))}</p>
  </details>
</article>
"""
            )
        cards.append("</section>")

    gaps = []
    for gap in pack["gaps"]:
        gaps.append(
            f"""
<article class="gap">
  <div class="claim-id">{esc(gap['id'])} · {esc(gap.get('criticality') or '')}</div>
  <h3>{esc(gap['title'])}</h3>
  <p>{esc(gap['missing'])}</p>
</article>
"""
        )

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{esc(pack['meta']['title'])}</title>
<style>
:root {{
  --bg:#fbfaf7; --card:#fff; --soft:#f3f0e8; --text:#1a1713; --muted:#6c6257;
  --rule:rgba(40,24,10,.14); --accent:#8b5a24; --green:#0f6e56; --blue:#315a9c; --gold:#9b7b0e; --red:#993c1d;
  --serif: Charter, Iowan Old Style, Georgia, serif; --sans: Inter, -apple-system, BlinkMacSystemFont, Helvetica, Arial, sans-serif;
  --mono: IBM Plex Mono, SFMono-Regular, Menlo, Consolas, monospace;
}}
*{{box-sizing:border-box}} body{{margin:0;background:var(--bg);color:var(--text);font:16px/1.58 var(--serif)}}
.wrap{{max-width:1080px;margin:auto;padding:46px 28px 80px}} a{{color:var(--accent)}} .eyebrow{{font:12px/1.4 var(--sans);letter-spacing:.08em;text-transform:uppercase;color:var(--muted)}}
h1{{font-size:42px;line-height:1.08;margin:14px 0 10px;font-weight:520}} .subtitle{{font-size:19px;color:var(--muted);max-width:860px}}
.meta{{font:13px var(--sans);color:var(--muted);display:flex;flex-wrap:wrap;gap:12px;margin-top:20px;padding-top:18px;border-top:1px solid var(--rule)}}
.stats{{display:grid;grid-template-columns:repeat(5,1fr);gap:10px;margin:30px 0}} .stat{{background:var(--card);border:1px solid var(--rule);border-radius:8px;padding:15px;text-align:center}}
.num{{font-size:31px;line-height:1;font-weight:600}} .label{{font:11px var(--sans);text-transform:uppercase;color:var(--muted);margin-top:6px}}
.note,.findings{{background:var(--soft);border-radius:8px;padding:18px 22px;margin:22px 0}} .findings li{{margin:6px 0}}
.filters{{position:sticky;top:0;background:rgba(251,250,247,.96);border-bottom:1px solid var(--rule);padding:12px 0;margin:26px 0;z-index:2}}
button{{font:12px var(--sans);padding:6px 10px;margin:3px;border:1px solid var(--rule);background:var(--card);border-radius:4px;cursor:pointer}} button.active{{background:#3b2a1d;color:white}}
.pass-section{{margin:46px 0}} .pass-section>h2{{font-size:28px;border-bottom:1px solid var(--rule);padding-bottom:8px}}
.claim,.gap{{background:var(--card);border:1px solid var(--rule);border-radius:8px;padding:20px 23px;margin:16px 0}} .claim.hidden{{display:none}}
.claim-id{{font:11px var(--mono);letter-spacing:.05em;color:var(--muted);text-transform:uppercase}} h3{{font-size:21px;line-height:1.24;margin:7px 0 10px}}
.tags{{display:flex;flex-wrap:wrap;gap:6px}} .tag{{font:11px var(--sans);padding:3px 8px;border-radius:4px;background:var(--soft);color:var(--muted)}}
.status.verified{{background:#e1f5ee;color:var(--green)}} .status.partially-verified{{background:#faeeda;color:var(--gold)}} .status.needs-correction{{background:#faece7;color:var(--red)}} .status.not-verified{{background:#ece9e0;color:var(--muted)}}
.level-a{{background:var(--green);color:white}} .level-b{{background:var(--blue);color:white}} .level-c{{background:var(--gold);color:white}} .level-d{{background:#6b6356;color:white}}
.claim-summary{{font-size:17px;margin:14px 0}} .sources{{font:13px var(--sans);display:flex;flex-wrap:wrap;gap:9px;margin:10px 0 12px}} details{{background:var(--soft);border-radius:6px;padding:10px 13px;margin-top:12px}}
summary{{font:13px var(--sans);cursor:pointer;color:var(--accent)}} details p{{font-size:14px;color:var(--muted)}} .muted{{color:var(--muted)}} footer{{margin-top:56px;border-top:1px solid var(--rule);padding-top:18px;font:12px var(--sans);color:var(--muted)}}
@media(max-width:760px){{.wrap{{padding:28px 16px}} h1{{font-size:32px}} .stats{{grid-template-columns:repeat(2,1fr)}}}}
</style>
</head>
<body>
<main class="wrap">
<header>
  <div class="eyebrow"><a href="../index.html">ProfGames</a> · English starter layer · fact-check audit</div>
  <h1>ProfGames — Fact-Check Audit Layer</h1>
  <p class="subtitle">A first English-facing layer over the canonical Russian fact-check pack: stable claim ids, evidence levels, source URLs, concise English summaries and original Russian wording for audit.</p>
  <div class="meta">
    <span>English layer: {esc(pack['meta']['version'])}</span>
    <span>Canonical pack: v{esc(pack['meta']['canonical_version'])}</span>
    <span>Fact-check date: {esc(pack['meta']['fact_check_date'])}</span>
    <span>Data relevance: {esc(pack['meta']['data_relevance_date'])}</span>
    <span><a href="factcheck.json">JSON</a></span>
    <span><a href="../factcheck.json">canonical RU JSON</a></span>
    <span><a href="https://github.com/scadastrangelove/profgames">GitHub</a></span>
  </div>
</header>
<section class="stats">
  <div class="stat"><div class="num">{stats['total_claims']}</div><div class="label">claims</div></div>
  <div class="stat"><div class="num">{status_counts['verified']}</div><div class="label">verified</div></div>
  <div class="stat"><div class="num">{status_counts['partially_verified']}</div><div class="label">partial</div></div>
  <div class="stat"><div class="num">{status_counts['needs_correction']}</div><div class="label">corrections</div></div>
  <div class="stat"><div class="num">{esc(pack['summary']['approximate_pass_rate'])}</div><div class="label">pass rate</div></div>
</section>
<section class="findings">
  <h2>What this layer is for</h2>
  <ul>{"".join(f"<li>{esc(x)}</li>" for x in pack['summary']['key_findings'])}</ul>
</section>
<nav class="filters">
  <button class="active" data-filter="all">All</button>
  <button data-filter="verified">Verified</button>
  <button data-filter="partially_verified">Partially verified</button>
  <button data-filter="needs_correction">Needs correction</button>
  <button data-filter="not_verified">Not verified</button>
</nav>
{"".join(cards)}
<section class="pass-section" id="gaps"><h2>Known Evidence Gaps</h2>{"".join(gaps)}</section>
<footer>
  ProfGames by Sergey Gordeychik · <a href="https://t.me/aiakyn">t.me/aiakyn</a> · <a href="https://teletype.in/@sergey_gordey">teletype</a> · #profgames
</footer>
</main>
<script>
const buttons = document.querySelectorAll('button[data-filter]');
buttons.forEach(btn => btn.addEventListener('click', () => {{
  buttons.forEach(b => b.classList.remove('active'));
  btn.classList.add('active');
  const f = btn.dataset.filter;
  document.querySelectorAll('.claim').forEach(card => {{
    card.classList.toggle('hidden', f !== 'all' && card.dataset.status !== f);
  }});
}}));
</script>
</body>
</html>
"""


def main() -> None:
    pack = build_json()
    (OUT / "factcheck.json").write_text(json.dumps(pack, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (OUT / "factcheck.html").write_text(render_html(pack), encoding="utf-8")


if __name__ == "__main__":
    main()

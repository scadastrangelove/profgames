#!/usr/bin/env python3
"""Pinned v0.52 -> v0.53: institutional scientific access and cyber comparison."""
import argparse
import copy
import hashlib
import json
from pathlib import Path

from migrate_frontier_pacing import add_source, event_record, pair
from migrate_stack_refresh import refresh
from migrate_v031_agent_behavior import attach_edge_links, uniq

ROOT = Path(__file__).resolve().parents[1]
PACKET = ROOT / 'review/scientific-access-2026-11-07'
DATE, VERSION = '2026-11-07', '0.53'
BASE_HASH = {
    'ru': 'b60b1edf1b0a11787cc937d468001d1dd67c5294d707c947a24547849cf955c4',
    'en': 'cb730ec2014607c0fc7f0e8a53c175095618e1120564a09ad4798f5ae16bfe67',
}
PACKAGE = json.loads((PACKET / 'candidates.json').read_text())
RECORDS, SOURCES = PACKAGE['events'], PACKAGE['sources']
ACCESS = 'ARC_QUIET_ACCESS_CONTROL'
KNOW = 'ARC_KNOWLEDGE_PRODUCTION_VALIDATION'
QUIET = 'CLM_013_QUIET_ACCESS_CONTROL'
OBSERVE = 'CLM_PROVIDER_OBSERVABILITY_ACCESS_GATE'
BIO = 'SIG_2026_ANTHROPIC_BIOLOGY_DUAL_USE_ACCESS_DISCLOSURE'
ROSALIND = 'SIG_2026_OPENAI_ROSALIND6_RESEARCH_ACCESS'
CVP = 'SIG_2026_ANTHROPIC_CVP_TIERED_CAPABILITY_ACCESS'
DNA = 'SIG_2026_DNA_SYNTHESIS_SCREENING_OPEN_LETTER'
MONITOR = 'SIG_2025_OPENAI_BIOLOGY_MONITORING_VETTED_ACCESS'
TEXT_UPDATES = {
    ACCESS: ('thesis',
        'Проверка клиентов, уровни допуска, телеметрия и отзыв доступа действуют в кибербезопасности и биологических исследованиях. Поставщики определяют доступную помощь и условия её использования; наблюдаемость ограничена размещённым сервисом. Военные кейсы и научные исследования различаются по цели, основаниям блокировки и установленным последствиям.',
        'Customer verification, access tiers, telemetry and revocation operate in cybersecurity and biological research. Providers determine available assistance and its conditions; visibility is bounded by the hosted service. Military cases and scientific research differ in purpose, grounds for blocking and established consequences.'),
    KNOW: ('thesis',
        'ИИ расширяет поиск, моделирование и повторное чтение архивов. Генерация кандидата, независимая проверка и применение требуют разных ресурсов. В биологии поставщик проверяет учреждение и определяет доступный режим помощи; открытые данные и локальные модели дают иные условия доступа.',
        'AI expands search, modelling and archive reanalysis. Candidate generation, independent validation and deployment require different resources. In biology, the provider vets institutions and determines available assistance; open data and local models offer different access conditions.'),
    QUIET: ('claim',
        'Контроль проявляется через проверку клиентов, уровни допуска, журналы запросов и отзыв аккаунтов. Киберпрограммы и GPT-Rosalind показывают институциональный отбор; биологические кейсы Anthropic добавляют наблюдение научных процессов и блокировку по правилам платформы. Величина влияния на научную производительность не измерена.',
        'Control operates through customer verification, access tiers, request logs and account revocation. Cyber programmes and GPT-Rosalind demonstrate institutional selection; Anthropic\'s biological cases add research-workflow observation and platform-policy enforcement. The effect on scientific productivity is not quantified.'),
    OBSERVE: ('claim',
        'Телеметрия размещённой модели даёт поставщику видимость части пользовательских процессов, включая научную работу. Контроль аккаунтов и конфигураций позволяет ограничить помощь или прекратить доступ. Раскрытия Anthropic показывают обе функции; полнота наблюдения, нейтральность решений и злонамеренность заблокированных учёных не установлены.',
        'Hosted-model telemetry gives the provider visibility into parts of user workflows, including scientific work. Account and configuration control can limit assistance or terminate access. Anthropic\'s disclosures show both functions; complete visibility, neutral decisions and malicious intent by banned scientists are not established.'),
}


def migrate(doc):
    if doc['meta']['version'] != '0.52':
        raise ValueError('Expected reviewed v0.52; repeated migration rejected')
    old = copy.deepcopy(doc)
    lang = doc['language']
    events = {e['id']: e for e in doc['events']}
    arcs = {a['id']: a for a in doc['arcs']}
    checks = {c['id']: c for c in doc['claimChecks']}
    sources = copy.deepcopy(SOURCES)
    for s in sources.values():
        s.update(checked_at=DATE, verification_method='source_content_reviewed; no_independent_replication')
    for candidate in RECORDS:
        if candidate['id'] in events:
            raise ValueError('Duplicate event: ' + candidate['id'])
        raw = dict(candidate, date_status='source_backed', actor_types=['company'],
            contexts=candidate['contexts'], method='primary_document_review_with_attribution',
            stack_layers=candidate['layers'], structures=['security', 'knowledge', 'production'],
            research_questions=[], confidence='B', status='proposal_not_enacted' if candidate['id'] == DNA else 'verified_as_reported',
            domains=[candidate['domain']] if candidate['domain'] else [],
            roles=['AI_ROLE_DEFENSIVE_TOOL'] if candidate['domain'] else [],
            primary_domain=candidate['domain'], delegation='not_applicable',
            safe_ru=candidate['summary_ru'], safe_en=candidate['summary_en'])
        e = event_record(raw, lang, sources, doc)
        e.update(story_primary_arc_id=candidate['arcs'][0], story_secondary_arc_ids=candidate['arcs'][1:],
            geographic_scopes=candidate['geographic_scopes'], research_updates=['scientific-access-2026-11-07'],
            actor_jurisdictions=[], geographic_scope_basis='proposed_regulatory_jurisdiction' if candidate['id'] == DNA else
                'provider_jurisdiction_not_unnamed_researcher_location',
            governance_scale='provider_access_policy' if candidate['id'] != DNA else 'US_legislative_proposal',
            behavioral_status=[], research_provenance=copy.deepcopy(candidate),
            classification_review=dict(date=DATE, source_content_checked=True, independent_source_reverification=False,
                                       independent_replication=False))
        if not candidate['domain']:
            e.update(research_track='science', research_evidence_kind='provider_access_policy_or_report',
                     research_review_status='source_reviewed_not_independently_replicated')
        for field in ['notes', 'corroboration_needed', 'claim_challenged']:
            pair(e, field, '', '', lang)
        pair(e, 'scope', candidate['title_ru'], candidate['title_en'], lang)
        pair(e, 'mechanism', candidate['mechanism_ru'], candidate['mechanism_en'], lang)
        pair(e, 'editorial_rationale', candidate['mechanism_ru'], candidate['mechanism_en'], lang)
        if candidate['id'] == BIO:
            e['targets_named'] = False
            e['malicious_intent_established'] = False
            e['weapon_creation_established'] = False
        if candidate['id'] == ROSALIND:
            e['current_state'] = dict(observed_at=DATE, source_url=sources['rosalind_access']['url'])
            pair(e['current_state'], 'title', 'Уровни исследовательского доступа', 'Research access tiers', lang)
            pair(e['current_state'], 'summary', candidate['current_state_ru'], candidate['current_state_en'], lang)
            pair(e['current_state'], 'date_note', candidate['date_note_ru'], candidate['date_note_en'], lang)
        doc['events'].append(e)
        events[e['id']] = e

    edges = []
    signatures = {(e['source'], e['target'], e['relation'], e.get('arc_id')) for e in doc['edges']}
    def edge(source, target, relation, arc, ru, en, target_kind='evidence', relationship='editorial_relationship'):
        signature = (source, target, relation, arc)
        if signature in signatures:
            raise ValueError('Duplicate edge: ' + repr(signature))
        signatures.add(signature)
        item = dict(id=f'EDGE_V053_SCIENCE_ACCESS_{len(edges)+1:03d}', kind='edge', source=source, target=target,
            source_kind='evidence', target_kind=target_kind, relation=relation, arc_id=arc,
            arc_family_id=arcs[arc]['family_id'], strength='moderate', evidence_level='B',
            visual_lane='model_weights', is_auto=False, style='dashed', relationship_class=relationship)
        pair(item, 'summary', ru, en, lang)
        edges.append(item)
    for candidate in RECORDS:
        eid = candidate['id']
        for aid in candidate['arcs']:
            edge(eid, aid, 'part_of_arc', aid,
                'Тематическая принадлежность: условия доступа к научным или кибервозможностям.',
                'Thematic membership: conditions of access to scientific or cyber capabilities.', 'arc', 'thematic')
            arcs[aid]['key_nodes'] = uniq(arcs[aid]['key_nodes'] + [eid])
        for related in candidate['related']:
            if related not in events:
                raise ValueError('Missing related event: ' + related)
            edge(eid, related, 'context_for', candidate['arcs'][0],
                'Сопоставление режимов доступа и наблюдаемости; причинная связь между событиями не заявляется.',
                'Comparison of access and observability regimes; no causal link between the events is claimed.')
    for eid in [MONITOR, BIO, CVP, ROSALIND]:
        edge(eid, QUIET, 'supports_with_scope', ACCESS,
            'Документирует проверку пользователей или контроль платформенного доступа; влияние на темп науки не измерено.',
            'Documents user verification or platform access control; effects on scientific pace are unmeasured.', 'claim_check', 'evidence_support')
        checks[QUIET]['supporting_evidence'] = uniq(checks[QUIET]['supporting_evidence'] + [eid])
        for s in events[eid]['sources']:
            add_source(checks[QUIET], s)
    edge(BIO, OBSERVE, 'supports_with_scope', ACCESS,
        'Поставщик описывает наблюдение исследований и отзыв доступа; злонамеренность учёных не установлена.',
        'The provider describes research observation and access revocation; malicious scientific intent is not established.', 'claim_check', 'evidence_support')
    checks[OBSERVE]['supporting_evidence'] = uniq(checks[OBSERVE]['supporting_evidence'] + [BIO])
    for s in events[BIO]['sources']:
        add_source(checks[OBSERVE], s)
    doc['edges'].extend(edges)
    attach_edge_links(doc, {e['id'] for e in edges})
    for aid in {a for r in RECORDS for a in r['arcs']}:
        a = arcs[aid]
        ordered = iter(sorted((n for n in a['key_nodes'] if n in events), key=lambda n: (events[n]['date'], n)))
        a['key_nodes'] = [next(ordered) if n in events else n for n in a['key_nodes']]
        dates = [events[n]['date'] for n in a['key_nodes'] if n in events]
        a.update(start_date=min([a['start_date']] + dates), end_date=max([a['end_date']] + dates))
    for node_id, (field, ru, en) in TEXT_UPDATES.items():
        node = (arcs if node_id in arcs else checks)[node_id]
        node.setdefault('editorial_history', []).append(dict(as_of=DATE, release='0.52', field=field,
            text=node[field], text_ru=node.get(field+'_ru'), text_en=node.get(field+'_en')))
        pair(node, field, ru, en, lang)
    # Keep the narrow claim about source visibility separate from access to scientific capability.
    doc['meta'].update(version=VERSION, updated_at=DATE)
    doc['meta']['changelog'].insert(0, dict(version=VERSION, date=DATE, added_evidence=len(RECORDS),
        updated_evidence=0, added_story_edges=len(edges), added_claims=0, added_story_arcs=0,
        description='Biological research access, provider observability, synthesis-screening proposal and cyber access tiers.'))
    doc['presentation'].update(editorial_version=VERSION, release_notes=[dict(
        title='Научные возможности и допуск' if lang == 'ru' else 'Scientific capability and access',
        text='Пять новых карточек: биологические исследования, проверка учреждений, синтез ДНК и кибердопуск. Предложения и наблюдаемые действия разделены.' if lang == 'ru' else
             'Five records cover biological research, institutional verification, DNA synthesis and cyber access. Proposals and observed actions remain distinct.')])
    doc['migrationAudit'].update(version=VERSION, v053_base_sha256=BASE_HASH[lang],
        v053_added_event_ids=[r['id'] for r in RECORDS], v053_added_edge_ids=[e['id'] for e in edges],
        v053_updated_text_ids=list(TEXT_UPDATES))
    doc['researchAudit']['scientific_access'] = dict(date=DATE, packet='review/scientific-access-2026-11-07/candidates.json',
        dedup=copy.deepcopy(PACKAGE['dedup']), excluded_claims=PACKAGE['excluded_claims'],
        full_registry_reverified=False, independent_replication=False)
    refresh(doc)
    assert all(e in doc['edges'] for e in old['edges'])
    assert {(s['id'], s['url']) for s in old['sourceIndex']} <= {(s['id'], s['url']) for s in doc['sourceIndex']}
    return doc


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--input', type=Path, default=ROOT)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    results, audit = {}, dict(version=VERSION, date=DATE, languages={})
    for lang in ['ru', 'en']:
        raw = (args.input / f'ai_power_storygraph_{lang}.json').read_bytes()
        if hashlib.sha256(raw).hexdigest() != BASE_HASH[lang]:
            raise ValueError('Unreviewed baseline: ' + lang)
        d = migrate(json.loads(raw))
        results[lang] = json.dumps(d, ensure_ascii=False, indent=2) + '\n'
        audit['languages'][lang] = dict(base_sha256=BASE_HASH[lang],
            counts={k: len(d[k]) for k in ['events', 'claims', 'claimChecks', 'arcs', 'edges', 'sourceIndex']})
    args.output.mkdir(parents=True, exist_ok=True)
    for lang, body in results.items():
        (args.output / f'ai_power_storygraph_{lang}.json').write_text(body)
    (PACKET / 'migration-audit.json').write_text(json.dumps(audit, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps(audit, indent=2))


if __name__ == '__main__':
    main()

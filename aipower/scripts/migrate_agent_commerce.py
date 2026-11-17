#!/usr/bin/env python3
"""Deterministic v0.58 -> v0.59 banking and agent-commerce integration."""
import argparse
import copy
import gzip
import hashlib
import json

from agent_commerce_packet import ROOT, PACKET, DATE, RECORDS, SOURCES, FIN, ADOPT, ACCESS, DATA, COG, OLD_AMAZON, COURT
from migrate_astra_underperformance import journal_document
from migrate_audit_repair import check_document, date_bounds, field_changes, write_documents
from migrate_frontier_pacing import event_record, pair, add_source
from migrate_stack_refresh import refresh
from migrate_v031_agent_behavior import attach_edge_links, uniq
from validate import references

VERSION = '0.59'
CLAIM = 'CLM_013_QUIET_ACCESS_CONTROL'
LEGAL_EDGES = {'EDGE_AMAZON_PERPLEXITY_QUIET_ACCESS', 'EDGE_AMAZON_PERPLEXITY_CLM013'}


def read_baseline(lang):
    manifest = json.loads((PACKET / 'baseline-manifest.json').read_text())
    raw = gzip.decompress((PACKET / manifest[lang]['path']).read_bytes())
    assert hashlib.sha256(raw).hexdigest() == manifest[lang]['sha256']
    return json.loads(raw)


def remember(item):
    item.setdefault('editorial_history', []).append(dict(as_of=DATE, release='0.58',
        fields={k: copy.deepcopy(v) for k, v in item.items() if k != 'editorial_history'}))


def migrate(before):
    assert before['meta']['version'] == '0.58'
    doc, lang = copy.deepcopy(before), before['language']
    events = {e['id']: e for e in doc['events']}
    arcs = {a['id']: a for a in doc['arcs']}
    added_edges = []
    for record in RECORDS:
        assert record['id'] not in events
        assert set(record['arcs']) <= arcs.keys()
        raw = dict(record)
        raw.update(date_basis=record.get('date_basis', 'primary_publication_date'),
            date_status='source_backed', confidence='A' if record['id'] == COURT else 'B',
            status='verified_as_reported', stack_layers=record['layers'],
            structures=['finance', 'production', 'knowledge'], research_questions=[], numbers={},
            contexts=['controlled_simulation'] if record['id'].endswith('CONTEXT_TESTBED') else
                     ['production'] if record['artifact'] == 'deployment' else
                     ['ecosystem_measurement'] if record['artifact'] == 'survey' else ['governance_document'],
            method='primary_source_review', domains=record.get('domains', []), roles=record.get('roles', []),
            primary_domain=next(iter(record.get('domains', [])), None), priority=2,
            force=record.get('force', 'not_applicable'), stage=record.get('stage', 'published'),
            delegation=record.get('delegation', 'not_applicable'),
            safe_ru=record['summary_ru'], safe_en=record['summary_en'])
        item = event_record(raw, lang, SOURCES, doc)
        item.update(date_precision='day', story_primary_arc_id=record['arcs'][0],
            story_secondary_arc_ids=record['arcs'][1:], route_eligible_arc_ids=record['arcs'], context_arc_ids=[],
            research_updates=[PACKET.name], geographic_scopes=record.get('geographic_scopes', []),
            actor_jurisdictions=[], geographic_scope_basis='source_scope_not_actor_nationality',
            governance_scale='not_applicable' if raw['force'] == 'not_applicable' else 'as_specified_in_source',
            behavioral_status=[], classification_review=dict(date=DATE, source_account_reviewed=True,
                independent_replication=False, all_underlying_metrics_reaudited=False),
            research_evidence_kind=record['evidence_kind'],
            research_review_status='source_reviewed_not_independently_replicated',
            research_provenance=dict(packet=str(PACKET.relative_to(ROOT))),
            event_or_forecast='event', cyber_access_principal=raw['delegation'] in ('observed', 'evaluated'))
        for field in ('notes', 'corroboration_needed', 'claim_challenged', 'role_basis'):
            pair(item, field, '', '', lang)
        for field in ('mechanism', 'editorial_rationale'):
            pair(item, field, record['mechanism_ru'], record['mechanism_en'], lang)
        pair(item, 'scope', record['title_ru'], record['title_en'], lang)
        if record['id'].endswith('CONTEXT_TESTBED'):
            pair(item, 'role_basis', 'Защищаемая система: платёжный агент в контролируемом испытании.',
                 'Protected system: a payment agent in a controlled evaluation.', lang)
        doc['events'].append(item)
        events[item['id']] = item

    old = events[OLD_AMAZON]
    remember(old)
    pair(old, 'title', 'Мартовский запрет Comet по иску Amazon, отменённый в апелляции',
         'Amazon\'s March Comet injunction, subsequently vacated on appeal', lang)
    ru = ('9 марта 2026 года окружной суд предварительно запретил спорный доступ Comet к Amazon, '
          'разделив разрешение пользователя и разрешение платформы. 18 марта исполнение было приостановлено. '
          '4 августа Девятый округ отменил запрет и вернул дело: на рассмотренных фактах доступ осуществлял пользователь при помощи инструмента.')
    en = ('On 9 March 2026 the district court preliminarily enjoined the disputed Comet access to Amazon, '
          'distinguishing user permission from platform authorization. Enforcement was stayed on 18 March. '
          'On 4 August the Ninth Circuit vacated the injunction and remanded: on the facts before it, the user accessed Amazon through a tool.')
    for field in ('summary', 'claim_supported', 'safe_wording'):
        pair(old, field, ru, en, lang)
    court_record = next(r for r in RECORDS if r['id'] == COURT)
    for field in ('caveat', 'claim_challenged', 'notes'):
        pair(old, field, court_record['caveat_ru'], court_record['caveat_en'], lang)
    pair(old, 'corroboration_needed', '', '', lang)
    # Retain the separate historical legal qualifications in both language fields.
    pair(old, 'caveats', [court_record['caveat_ru'],
        'Дело гражданское: это не уголовное преследование и не решение о правосубъектности или умысле ИИ-агента.',
        'Amazon показала расходы на реагирование свыше $5 000, что имело значение для гражданского CFAA-требования в мартовском приказе; это не универсальный порог любого несанкционированного доступа.',
        'Политика DOJ отдельно требует знания человеком фактов, делавших доступ неавторизованным, и предписывает не предъявлять обвинение за отвечающее условиям добросовестное исследование безопасности.'],
        [court_record['caveat_en'],
        'The case is civil, not a prosecution or a ruling on AI personhood or intent.',
        'Amazon presented response costs above $5,000, relevant to the civil CFAA claim in the March order; this is not a universal threshold for every unauthorized-access offense.',
        'DOJ policy separately requires human knowledge of the facts making access unauthorized and directs prosecutors to decline qualifying good-faith security research.'], lang)
    old.update(status='verified_historical_order_vacated_on_appeal', status_update_date='2026-08-04',
               current_legal_status='preliminary_injunction_vacated_and_remanded',
               research_updates=uniq(old.get('research_updates', []) + [PACKET.name]))
    old['numbers']['vacatur_date'] = '2026-08-04'
    pair(old, 'legal_update', court_record['summary_ru'], court_record['summary_en'], lang)
    add_source(old, SOURCES['COURT'])
    for edge in doc['edges']:
        if edge['id'] in LEGAL_EDGES:
            remember(edge)
            pair(edge, 'summary',
                'Исторический пример спорного контроля доступа: мартовский предварительный запрет отменён 4 августа. Не действующее подтверждение права платформы запрещать любой пользовательский агент.',
                'Historical evidence of contested access control: the March preliminary injunction was vacated on 4 August. Not a current endorsement of a platform right to prohibit every user agent.', lang)

    signatures = {(e['source'], e['target'], e['relation'], e.get('arc_id')) for e in doc['edges']}
    def link(source, target, aid, relation='part_of_arc', target_kind='arc',
             ru='Тематическая принадлежность; не самостоятельное доказательство тезиса.',
             en='Thematic membership, not independent proof of a thesis.'):
        signature = (source, target, relation, aid)
        assert signature not in signatures
        signatures.add(signature)
        edge = dict(id=f'EDGE_V059_{len(added_edges)+1:03d}', kind='edge', source=source, target=target,
            source_kind='evidence', target_kind=target_kind, relation=relation, arc_id=aid,
            arc_family_id=arcs[aid]['family_id'], strength='moderate', evidence_level='B',
            visual_lane='finance_rent' if aid == FIN else events[source]['stack_layer'][0],
            is_auto=False, style='dashed', relationship_class='thematic' if relation == 'part_of_arc' else 'editorial_relationship')
        pair(edge, 'summary', ru, en, lang)
        added_edges.append(edge)
    for record in RECORDS:
        for aid in record['arcs']:
            link(record['id'], aid, aid)
            arcs[aid]['key_nodes'] = uniq(arcs[aid]['key_nodes'] + [record['id']])
    link(COURT, OLD_AMAZON, ACCESS, 'updates', 'evidence',
         'Августовская отмена обновляет мартовский запрет, сохраняя обе даты.',
         'The August vacatur updates the March injunction without replacing either date.')
    link(COURT, CLAIM, ACCESS, 'qualifies', 'claim_check',
         'Уточняет пределы платформенного контроля: на этих фактах суд не поддержал запрет доступа по CFAA/CDAFA.',
         'Qualifies platform control: on these facts the court did not uphold the access restriction under CFAA/CDAFA.')
    link('SIG_2026_BOE_FCA_AGENTS_PROVIDER_CONCENTRATION', 'SIG_2024_BOE_FINANCE_AI_THIRD_PARTY_CONCENTRATION', FIN,
         'updates', 'evidence', 'Новый опрос того же регулятора; изменённые определения ограничивают сравнение.',
         'A new survey by the same regulator; changed definitions limit comparability.')
    link('SIG_2025_JPMORGAN_PLAID_PRICED_DATA_ACCESS', 'SIG_2026_JPMORGAN_EXTERNAL_AGENTS_SMARTCASH', FIN,
         'context_for', 'evidence', 'Предыстория договорного доступа к данным; не доказательство причинной связи с агентной политикой.',
         'Background on contractual data access, not evidence that it caused the agent policy.')

    check = next(c for c in doc['claimChecks'] if c['id'] == CLAIM)
    check['qualifying_evidence'] = uniq(check.get('qualifying_evidence', []) + [COURT])
    for language in ('ru', 'en'):
        check.setdefault('caveats_' + language, []).append(court_record['caveat_' + language])
    check['caveats'] = copy.deepcopy(check['caveats_' + lang])
    add_source(check, SOURCES['COURT'])
    arc = arcs[FIN]
    remember(arc)
    pair(arc, 'title', 'Финансы: клиентский доступ, платёжные полномочия и устойчивость',
         'Finance: customer access, payment authority and resilience', lang)
    pair(arc, 'thesis',
         'Агенты могут менять выбор финансового посредника и скорость движения средств. Банки развивают собственные интерфейсы, договариваются о цене доступа к данным и устанавливают условия допуска внешних агентов. Платёжные сети проверяют участников и полномочия; регуляторы изучают общих поставщиков, ошибки, ликвидность и восстановление.',
         'Agents can change the choice of financial intermediary and the speed of fund movement. Banks develop their own interfaces, negotiate data-access pricing and set conditions for outside agents. Payment networks vet participants and authority; regulators examine shared suppliers, errors, liquidity and recovery.', lang)
    pair(arc, 'safe_wording',
         'Различать банковские условия доступа, пилотные платежи и сценарии рисков. Возможность ускорить перевод средств ещё не означает наблюдаемого оттока депозитов.',
         'Distinguish bank access conditions, pilot payments and risk scenarios. The ability to accelerate transfers does not establish observed deposit outflows.', lang)
    pair(arc, 'counterpoints', [
        'Документ RBI в этой арке представлен проектом, а не доказательством фактического внедрения банковского аварийного отключения.',
        'В группе европейских надзорных материалов именно письмо ЕЦБ содержит конкретный запрос на представление планов в указанной сфере.',
        'Оценки EBA, ESRB, европейских надзорных органов и FSB сами по себе не создают новой общей юридической обязанности.',
        'Пилот, заявление руководства и сценарий бегства вкладчиков имеют разный доказательный статус. Защита депозитной базы не установлена как единственная причина ограничений доступа.'], [
        'The RBI document in this arc is a draft, not evidence that banks have implemented an emergency kill switch.',
        'Within the European supervisory materials, the ECB letter is the concrete request for submission of plans within its stated scope.',
        'EBA, ESRB, the European Supervisory Authorities and FSB assessments do not by themselves create a new general legal duty.',
        'A pilot, an executive statement and a bank-run scenario have different evidential status. Protection of the deposit base is not established as the sole reason for access restrictions.'], lang)

    doc['edges'].extend(added_edges)
    attach_edge_links(doc, {e['id'] for e in added_edges})
    qualifying_edges = [e for e in added_edges if e['source'] == COURT and e['target'] == CLAIM]
    check.setdefault('evidence_relations', []).append(dict(event_id=COURT,
        relations=uniq(e['relation'] for e in qualifying_edges),
        edge_ids=[e['id'] for e in qualifying_edges], basis='manual_edges',
        legacy_fields=['qualifying_evidence']))
    for arc in doc['arcs']:
        nodes = [n for n in arc['key_nodes'] if n in events]
        ordered = iter(sorted(nodes, key=lambda n: (events[n]['date'], n)))
        arc['key_nodes'] = [next(ordered) if n in events else n for n in arc['key_nodes']]
        bounds = [date_bounds(events[n]['date']) for n in nodes]
        if bounds:
            arc['start_date'] = min([arc['start_date']] + [b[0] for b in bounds])
            arc['end_date'] = max([arc['end_date']] + [b[1] for b in bounds])
    doc['meta'].update(version=VERSION, updated_at=DATE)
    doc['meta']['changelog'].insert(0, dict(version=VERSION, date=DATE, added_evidence=len(RECORDS),
        updated_evidence=1, added_claims=0, added_story_arcs=0, added_story_edges=len(added_edges),
        description='Agent banking and commerce: access pricing, payment pilots, platform ranking, bounded security testing and an appellate correction.'))
    doc['presentation'].update(editorial_version=VERSION, release_notes=[dict(
        title='Банки, агенты и право доступа' if lang == 'ru' else 'Banks, agents and access rights',
        text='Условия доступа, платёжные пилоты, финансовые сценарии и судебные пределы контроля.' if lang == 'ru' else
             'Access conditions, payment pilots, financial scenarios and judicial limits on control.')])
    refresh(doc)
    doc['connectivity']['last_recomputed'] = DATE
    doc['auditRepair']['presentation_counts'].update(
        events=sum(not e.get('presentation_hidden') for e in doc['events']), stored_events=len(doc['events']))
    doc['migrationAudit']['v059_agent_commerce'] = dict(date=DATE, added_event_ids=[r['id'] for r in RECORDS],
        updated_event_ids=[OLD_AMAZON], updated_edge_ids=sorted(LEGAL_EDGES), updated_arc_ids=[FIN],
        updated_claim_check_ids=[CLAIM], added_edge_ids=[e['id'] for e in added_edges],
        added_source_urls=sorted({s['url'] for s in doc['sourceIndex']} - {s['url'] for s in before['sourceIndex']}))
    doc['referenceIntegrity'] = references(doc)
    check_document(doc)
    assert all(e in doc['edges'] for e in before['edges'] if e['id'] not in LEGAL_EDGES)
    return doc


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--apply', action='store_true')
    args = parser.parse_args()
    paths = {lang: ROOT / f'ai_power_storygraph_{lang}.json' for lang in ('ru', 'en')}
    raw = {lang: p.read_bytes() for lang, p in paths.items()}
    manifest_path = PACKET / 'baseline-manifest.json'
    before = {lang: read_baseline(lang) if manifest_path.exists() else json.loads(raw[lang]) for lang in paths}
    after = {lang: migrate(before[lang]) for lang in paths}
    for lang in paths:
        if json.loads(raw[lang]) not in (before[lang], after[lang]):
            raise ValueError('Unreviewed concurrent changes: ' + lang)
    report = dict(version=VERSION, languages={lang: dict(
        counts={key: len(after[lang][key]) for key in ('events', 'claims', 'arcs', 'edges', 'sourceIndex')},
        changes=field_changes(journal_document(before[lang]), journal_document(after[lang]))) for lang in paths})
    if args.apply:
        PACKET.mkdir(parents=True, exist_ok=True)
        if not manifest_path.exists():
            manifest = {}
            for lang in paths:
                name = f'baseline-{lang}.json.gz'
                (PACKET / name).write_bytes(gzip.compress(raw[lang], mtime=0))
                manifest[lang] = dict(path=name, sha256=hashlib.sha256(raw[lang]).hexdigest())
            manifest_path.write_text(json.dumps(manifest, indent=2)+'\n')
        (PACKET / 'migration-audit.json').write_text(json.dumps(report, ensure_ascii=False, indent=2)+'\n')
        (PACKET / 'reviewed-records.json').write_text(json.dumps(dict(events=RECORDS, sources=SOURCES), ensure_ascii=False, indent=2)+'\n')
        write_documents(ROOT, raw, after)
    print(json.dumps(dict(applied=args.apply, counts={lang: report['languages'][lang]['counts'] for lang in paths})))


if __name__ == '__main__':
    main()

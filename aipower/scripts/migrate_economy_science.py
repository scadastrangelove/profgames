#!/usr/bin/env python3
"""Reviewable, idempotent v0.57 -> v0.58 integration of economy and science evidence."""
import argparse
import copy
import gzip
import hashlib
import json

from economy_science_packet import ROOT, PACKET, DATE, CAP, CLOUD, WORK, KNOW, PACE, package
from migrate_astra_underperformance import journal_document
from migrate_audit_repair import check_document, date_bounds, field_changes, write_documents
from migrate_frontier_pacing import event_record, pair, add_source, arc_families
from migrate_stack_refresh import refresh
from migrate_v031_agent_behavior import attach_edge_links, uniq
from validate import references

VERSION = '0.58'


def read_baseline(lang):
    manifest = json.loads((PACKET / 'baseline-manifest.json').read_text())
    raw = gzip.decompress((PACKET / manifest[lang]['path']).read_bytes())
    assert hashlib.sha256(raw).hexdigest() == manifest[lang]['sha256']
    return json.loads(raw)


def migrate(before, bundle):
    assert before['meta']['version'] == '0.57'
    doc, lang = copy.deepcopy(before), before['language']
    events = {e['id']: e for e in doc['events']}
    arcs = {a['id']: a for a in doc['arcs']}
    added, updated, edges = [], [], []
    for record in bundle['events']:
        assert record['id'] not in events
        assert set(record['arcs']) <= arcs.keys()
        raw = dict(record, date_status='source_backed', confidence='B', status='verified_as_reported',
            stack_layers=record['layers'], structures=['knowledge', 'production'] if KNOW in record['arcs'] else ['finance', 'production'],
            research_questions=[], numbers={}, domains=[], roles=[], primary_domain=None, priority=2,
            safe_ru=record['summary_ru'], safe_en=record['summary_en'],
            contexts=['governance_document'] if record.get('artifact') == 'government_order' else ['ecosystem_measurement'],
            method='primary_source_review', force=record.get('force', 'not_applicable'), stage='published',
            delegation='not_applicable')
        raw['artifact'] = record.get('artifact_override', record['artifact'])
        event = event_record(raw, lang, bundle['sources'], doc)
        event.update(date_precision='month' if len(record['date']) == 7 else 'day',
            story_primary_arc_id=record['arcs'][0], story_secondary_arc_ids=record['arcs'][1:],
            route_eligible_arc_ids=record['arcs'], context_arc_ids=[],
            research_updates=[PACKET.name], geographic_scopes=record.get('geographic_scopes', []),
            actor_jurisdictions=[], geographic_scope_basis='study_or_event_scope_not_actor_nationality',
            governance_scale='not_applicable' if raw['force'] == 'not_applicable' else 'as_specified_in_source',
            behavioral_status=[], classification_review=dict(date=DATE, source_account_reviewed=True,
                independent_replication=False, all_underlying_metrics_reaudited=False),
            research_evidence_kind=record['evidence_kind'],
            research_review_status='source_reviewed_not_independently_replicated',
            research_provenance=dict(packet=str(PACKET.relative_to(ROOT)), input_ids=record.get('input_ids', [])),
            observation_period=record.get('observation_period'),
            event_or_forecast=record.get('event_or_forecast', 'event'))
        for optional in ('outcome_stage', 'source_access_note'):
            if optional in record:
                event['research_'+optional] = record[optional]
        for field in ('notes', 'corroboration_needed', 'claim_challenged', 'role_basis'):
            pair(event, field, '', '', lang)
        for field in ('mechanism', 'editorial_rationale'):
            pair(event, field, record['mechanism_ru'], record['mechanism_en'], lang)
        pair(event, 'scope', record['title_ru'], record['title_en'], lang)
        doc['events'].append(event)
        events[event['id']] = event
        added.append(event['id'])

    supplied = {e['id']: e for e in bundle['input']['events']}
    for decision in bundle['decisions']:
        event = events[decision['target_id']]
        event.setdefault('research_package_records', []).append(decision['input_id'])
        if decision['decision'] != 'enrich_existing':
            continue
        original = supplied[decision['input_id']]
        # Keep earlier claims and historical observations; add provenance without redating.
        for source in original['sources']:
            add_source(event, dict(name=source.get('publisher') or event['source_name'],
                title=source['title'], url=source['url'], date=source.get('source_date', ''),
                type=event['source_type'], primary_or_secondary=source['primary_or_secondary'],
                checked_at=DATE, verification_method='duplicate_report_matched_to_existing_evidence'))
        event['research_updates'] = uniq(event.get('research_updates', []) + [PACKET.name])
        updated.append(event['id'])

    coreweave = events['SIG_2025_COREWEAVE_OPENAI_11_9B_CAPACITY']
    coreweave.setdefault('editorial_history', []).append(dict(as_of=DATE, release='0.57',
        fields={k: coreweave.get(k) for k in ('summary', 'summary_ru', 'summary_en')}))
    pair(coreweave, 'summary',
        '10 марта 2025 года CoreWeave объявила соглашение о предоставлении инфраструктуры OpenAI на сумму до $11,9 млрд. В рамках сделки OpenAI также должна была получить акции CoreWeave на $350 млн. Клиент становится акционером поставщика; потолок договора не равен признанной выручке.',
        'On 10 March 2025 CoreWeave announced an infrastructure agreement with OpenAI worth up to $11.9 billion. OpenAI would also receive $350 million of CoreWeave equity. The customer becomes a supplier shareholder; the contract ceiling is not recognized revenue.', lang)
    coreweave['research_updates'] = uniq(coreweave.get('research_updates', []) + [PACKET.name])
    updated.append(coreweave['id'])

    # A malformed encoded NBSP is a URL defect, not a new independent source.
    iea = events['SIG_2025_IEA_ENERGY_LOCAL_NOT_GLOBAL']
    for source in iea.get('sources', []):
        source['url'] = source['url'].replace('%C2%A0', '').rstrip('\u00a0')
    iea['url'] = iea['url'].replace('%C2%A0', '').rstrip('\u00a0')
    updated.append(iea['id'])

    signatures = {(e['source'], e['target'], e['relation'], e.get('arc_id')) for e in doc['edges']}

    def edge(source, target, arc, relation='part_of_arc', ru='Тематическая принадлежность, не самостоятельное подтверждение тезиса.', en='Thematic membership, not independent proof of the thesis.', target_kind='arc'):
        signature = (source, target, relation, arc)
        assert signature not in signatures
        signatures.add(signature)
        item = dict(id=f'EDGE_V058_{len(edges)+1:03d}', kind='edge', source=source, target=target,
            source_kind='evidence' if source in events else 'claim', target_kind=target_kind,
            relation=relation, arc_id=arc, arc_family_id=arcs[arc]['family_id'],
            strength='moderate', evidence_level='B', visual_lane='decision_support_cognition' if arc == KNOW else 'finance_rent',
            is_auto=False, style='dashed', relationship_class='thematic' if relation == 'part_of_arc' else 'editorial_relationship')
        pair(item, 'summary', ru, en, lang)
        edges.append(item)

    for record in bundle['events']:
        for aid in record['arcs']:
            edge(record['id'], aid, aid)
            arcs[aid]['key_nodes'] = uniq(arcs[aid]['key_nodes'] + [record['id']])

    targets = {d['input_id']: d['target_id'] for d in bundle['decisions']}
    def econ(index):
        return targets[bundle['input']['events'][index]['id']]

    relations = [
        (econ(20), 'SIG_2026_COREWEAVE_Q2_CASH_CAPEX_DEBT', CAP, 'updates',
         'Новый отчётный квартал той же компании; не независимая репликация.', 'A new reporting quarter from the same company, not independent replication.'),
        (econ(32), 'SIG_2024_KLARNA_WORKLOAD_EQUIVALENT', WORK, 'updates',
         'Годовой отчёт уточняет масштаб поддержки и сохранение человеческого канала.', 'The annual report updates support scale and the continued human channel.'),
        (econ(2), 'SIG_2026_BIS_CIRCULAR_AI_FINANCE', CAP, 'refines',
         'От связей инвестор-поставщик к структурам долга и распределению риска.', 'Extends investor-supplier links to debt structures and risk distribution.'),
        (econ(39), 'SIG_2025_IEA_ENERGY_LOCAL_NOT_GLOBAL', 'ARC_ENERGY_GRID_POLITICS', 'updates',
         'Обновлённые оценки и прогноз того же института.', 'Updated estimates and projections from the same institution.'),
        ('SIG_2026_AI_FUTURES_TIMELINE_REVISION', 'SIG_2026_METR_ANTHROPIC_RD_ACCELERATION', KNOW, 'context_for',
         'Прогноз использует оценку METR; два текста не являются двумя независимыми измерениями.', 'The forecast uses METR\'s assessment; the two texts are not independent measurements.'),
        ('SIG_2026_ANTHROPIC_EXPECTED_RD_THRESHOLD', 'SIG_2026_METR_ANTHROPIC_RD_ACCELERATION', KNOW, 'qualifies',
         'Порог политики опирается также на ожидания; его нельзя подменять измерением текущей модели.', 'The policy threshold also relies on expectations; it is not a current-model measurement.'),
    ]
    for source, target, aid, relation, ru, en in relations:
        edge(source, target, aid, relation, ru, en, 'evidence')

    arc_updates = {
        CAP: (
            'Финансирование стека связывает инвестиции, закупки вычислений, аренду и гарантии. Рост продаж и полезные результаты сосуществуют с долгосрочными обязательствами. Условия договора определяют, кто получает доход и кто несёт риск недозагрузки.',
            'Stack financing links investment, compute purchases, leases and guarantees. Growing sales and useful outcomes coexist with long-term commitments. Contract terms allocate revenue and the risk of unused capacity.',
            ['Выручка, годовой темп продаж, обязательства и оценка компании имеют разные знаменатели.', 'Прибыль поставщика оборудования не устанавливает окупаемость его покупателя.', 'Связанное финансирование не означает фиктивность продаж. Географическая прозрачность раскрытий неодинакова.'],
            ['Revenue, annualized sales pace, commitments and company valuation have different denominators.', 'Equipment-supplier profit does not establish the buyer\'s investment return.', 'Linked financing does not establish fictitious sales. Disclosure transparency differs across jurisdictions.']),
        KNOW: (
            'ИИ расширяет поиск, моделирование, чтение архивов и автоматизацию экспериментов. Результат зависит от данных, приборов, доступа к моделям и проверки новизны. Лаборатории также используют ИИ для разработки следующих моделей, а часть доказательств ускорения оставляют закрытой.',
            'AI expands search, modelling, archive analysis and experimental automation. Outcomes depend on data, instruments, model access and novelty checks. Labs also use AI to develop subsequent models while keeping some acceleration evidence confidential.',
            ['Различать генерацию кандидата, лабораторную проверку и общественный эффект.', 'Повторное обнаружение не является новым открытием; автоматизация задач не равна замене научной команды.', 'Внешняя оценка с доступом к закрытым данным может быть недоступна для публичного воспроизведения.'],
            ['Separate candidate generation, laboratory validation and societal outcomes.', 'Rediscovery is not a new discovery; task automation is not replacement of a research team.', 'External assessment with access to confidential data may not be publicly reproducible.'])}
    for aid, (ru, en, cru, cen) in arc_updates.items():
        arc = arcs[aid]
        arc.setdefault('editorial_history', []).append(dict(as_of=DATE, release='0.57',
            fields={k: copy.deepcopy(arc.get(k)) for k in ('thesis', 'thesis_ru', 'thesis_en', 'counterpoints', 'counterpoints_ru', 'counterpoints_en')}))
        pair(arc, 'thesis', ru, en, lang)
        pair(arc, 'counterpoints', cru, cen, lang)

    claims = [
        ('CLM_ECON_USE_VALUE_AND_RETURN', [econ(23), econ(32), econ(34)], [econ(28), econ(31), econ(25)], [CAP, WORK, CLOUD],
         'Полезный результат, доход поставщика и окупаемость вложений измеряются раздельно',
         'Useful outcomes, supplier revenue and investment returns require separate measurements',
         'Платящие клиенты, экономия в отдельных процессах и удешевление вычислений сосуществуют с неполными данными о затратах покупателей и возврате инфраструктурного капитала.',
         'Paying customers, savings in particular workflows and cheaper computation coexist with incomplete evidence about customer costs and infrastructure capital returns.'),
        ('CLM_ECON_SHARED_FINANCING_EXPOSURE', [econ(0), econ(1), econ(2), econ(3), econ(12)], [econ(9), econ(4)], [CAP, CLOUD],
         'Финансирование и закупки могут связывать нескольких участников с одним будущим потоком денег',
         'Financing and procurement can expose several parties to the same future cash flows',
         'Инвестиции, гарантии и заказы создают общие риски между поставщиками и покупателями. Это установленный механизм взаимозависимости, а не оценка доли фиктивных продаж или даты кризиса.',
         'Investments, guarantees and purchase commitments create shared exposures between suppliers and buyers. This establishes interdependence, not the share of fictitious sales or the date of a crisis.'),
        ('CLM_RESEARCH_ACCELERATION_VALIDATION_ACCESS', ['SIG_2026_CHALMERS_AGENT_BIOLOGY_VALIDATION', 'SIG_2026_SJTU_AUTODNA_LABORATORY', 'SIG_2026_METR_ANTHROPIC_RD_ACCELERATION'], ['SIG_2026_MAYA_AGENT_REDISCOVERY_CORRECTION', 'SIG_2026_ANTHROPIC_EXPECTED_RD_THRESHOLD'], [KNOW, PACE],
         'Ускорение исследований усиливает значение доступа к данным и независимой проверки',
         'Faster research increases the importance of data access and independent validation',
         'Агентные системы уже участвуют в проверяемых лабораторных процессах и ускорении R&D. Новизна результата, автономность и доступность доказательств требуют отдельной проверки.',
         'Agentic systems already contribute to validated laboratory workflows and faster R&D. Novelty, autonomy and access to supporting evidence require distinct checks.'),
    ]
    for cid, supporting, qualifying, aids, tru, ten, cru, cen in claims:
        claim = dict(id=cid, kind='claim', status='partially_verified', confidence='B', evidence_level='B',
            supporting_evidence=uniq(supporting), qualifying_evidence=uniq(qualifying),
            arcIds=aids, arcFamilyIds=arc_families(doc, aids), edgeIds=[], relationTypes=[], sources=[],
            date_relevant='2023-2026', interpretation_type='editorial_synthesis',
            stack_layer=['decision_support_cognition', 'data_telemetry', 'model_weights'] if KNOW in aids else ['finance_rent', 'cloud_inference', 'decision_support_cognition'],
            strange_structure=['knowledge', 'production'] if KNOW in aids else ['finance', 'production'], geography=[])
        for field, ru, en in [('title', tru, ten), ('claim', cru, cen), ('safe_wording', cru, cen), ('recommended_phrasing', cru, cen)]:
            pair(claim, field, ru, en, lang)
        pair(claim, 'caveats', ['Тематический корпус; доли событий не являются статистикой всей отрасли.'],
             ['A thematic corpus; event shares are not statistics for the whole industry.'], lang)
        for eid in uniq(supporting + qualifying):
            for source in events[eid]['sources']:
                add_source(claim, source)
            aid = events[eid]['story_primary_arc_id']
            edge(eid, cid, aid, 'supports_with_scope' if eid in supporting else 'qualifies',
                 'Поддержка или уточнение в пределах описанной выборки и метода.',
                 'Support or qualification within the stated sample and method.', 'claim')
        for aid in aids:
            edge(cid, aid, aid, 'supports_arc', cru, cen)
        doc['claims'].append(claim)

    doc['edges'].extend(edges)
    attach_edge_links(doc, {e['id'] for e in edges})
    for arc in doc['arcs']:
        event_nodes = [n for n in arc['key_nodes'] if n in events]
        ordered = iter(sorted(event_nodes, key=lambda n: (events[n]['date'], n)))
        arc['key_nodes'] = [next(ordered) if n in events else n for n in arc['key_nodes']]
        bounds = [date_bounds(events[n]['date']) for n in event_nodes]
        if bounds:
            arc['start_date'] = min([arc['start_date']] + [b[0] for b in bounds])
            arc['end_date'] = max([arc['end_date']] + [b[1] for b in bounds])
    doc['meta'].update(version=VERSION, updated_at=DATE)
    doc['meta']['changelog'].insert(0, dict(version=VERSION, date=DATE, added_evidence=len(added),
        updated_evidence=len(set(updated)), added_claims=len(claims), added_story_arcs=0,
        added_story_edges=len(edges), description='Reviewed economy disclosures, scientific validation and R&D acceleration; novelty correction and explicit deduplication.'))
    doc['presentation'].update(editorial_version=VERSION, release_notes=[dict(
        title='Экономика и производство знаний' if lang == 'ru' else 'Economics and knowledge production',
        text='Спрос, обязательства, стоимость вычислений и проверка результатов исследований.' if lang == 'ru' else
             'Demand, commitments, compute costs and validation of research results.')])
    refresh(doc)
    doc['connectivity']['last_recomputed'] = DATE
    doc['auditRepair']['presentation_counts']['events'] = sum(not e.get('presentation_hidden') for e in doc['events'])
    doc['auditRepair']['presentation_counts']['stored_events'] = len(doc['events'])
    doc['migrationAudit']['v058_economy_science'] = dict(date=DATE, added_event_ids=added,
        updated_event_ids=sorted(set(updated)), added_claim_ids=[c[0] for c in claims],
        added_edge_ids=[e['id'] for e in edges], decisions=bundle['decisions'],
        input_packet='review/economy-science-2026-11-15/input-economy-ru.json',
        added_source_urls=sorted({s['url'] for s in doc['sourceIndex']} - {s['url'] for s in before['sourceIndex']}))
    doc['referenceIntegrity'] = references(doc)
    check_document(doc)
    assert all(e in doc['edges'] for e in before['edges'])
    return doc


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--apply', action='store_true')
    args = parser.parse_args()
    paths = {lang: ROOT / f'ai_power_storygraph_{lang}.json' for lang in ('ru', 'en')}
    raw = {lang: path.read_bytes() for lang, path in paths.items()}
    manifest_path = PACKET / 'baseline-manifest.json'
    before = {lang: read_baseline(lang) if manifest_path.exists() else json.loads(raw[lang]) for lang in paths}
    bundle = package()
    after = {lang: migrate(before[lang], bundle) for lang in paths}
    for lang in paths:
        if json.loads(raw[lang]) not in (before[lang], after[lang]):
            raise ValueError('Unreviewed concurrent changes: ' + lang)
    report = dict(version=VERSION, languages={lang: dict(counts={key: len(after[lang][key]) for key in ('events', 'claims', 'arcs', 'edges', 'sourceIndex')},
        changes=field_changes(journal_document(before[lang]), journal_document(after[lang]))) for lang in paths})
    if args.apply:
        if not manifest_path.exists():
            manifest = {}
            for lang in paths:
                name = f'baseline-{lang}.json.gz'
                (PACKET / name).write_bytes(gzip.compress(raw[lang], mtime=0))
                manifest[lang] = dict(path=name, sha256=hashlib.sha256(raw[lang]).hexdigest())
            manifest_path.write_text(json.dumps(manifest, indent=2)+'\n')
        (PACKET / 'migration-audit.json').write_text(json.dumps(report, ensure_ascii=False, indent=2)+'\n')
        (PACKET / 'decisions.json').write_text(json.dumps(bundle['decisions'], ensure_ascii=False, indent=2)+'\n')
        write_documents(ROOT, raw, after)
    print(json.dumps(dict(applied=args.apply, counts={lang: report['languages'][lang]['counts'] for lang in paths})))


if __name__ == '__main__':
    main()

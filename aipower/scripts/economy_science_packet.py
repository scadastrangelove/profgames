"""Reviewed editorial mapping; the supplied research pack remains an immutable input."""
import copy
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PACKET = ROOT / 'review/economy-science-2026-11-15'
DATE = '2026-11-15'
CAP = 'ARC_CAPITAL_MIX_PUBLIC_PRIVATE'
CLOUD = 'ARC_CLOUD_CAPACITY_VENDOR_LOCKIN'
ENERGY = 'ARC_ENERGY_GRID_POLITICS'
WORK = 'ARC_WORK_COMPETENCE_DISTRIBUTION'
ADOPT = 'ARC_CORPORATE_DECISION_SUPPORT_ADOPTION'
KNOW = 'ARC_KNOWLEDGE_PRODUCTION_VALIDATION'
PACE = 'ARC_FRONTIER_PACING_AND_SOVEREIGN_CONTROL'

# One disclosure can contain several observations without becoming several events.
GROUPS = [
([2], 'BIS', [CAP, CLOUD], 'BIS: debt and guarantees distribute infrastructure risk',
 'BIS describes special-purpose vehicles, leases and corporate guarantees financing AI infrastructure. Five hyperscalers issued $222 billion of bonds through 22 September 2026. Observed bond-market spillovers on AI-financing news days were small and short-lived.',
 'Gross issuance is neither net debt growth nor exclusively AI spending. The report maps exposures, not a realized systemic crisis.'),
([3], 'IMF', [CAP, CLOUD], 'IMF: investments and sales depend on the same counterparties',
 'Fourteen disclosed transactions since 2023 link about $300 billion of equity, $650 billion of debt and $1.4 trillion of future revenue commitments. Distress at an investee could impair both the investment and the investor\'s expected sales.',
 'Different financial categories and a selected sample; these amounts must not be added as market size or realized spending.'),
([4,5], 'Federal Reserve', [CAP], 'Federal Reserve: elevated valuations and AI-related risk concerns',
 'The November stability report describes elevated equity valuations despite higher expected earnings. In a separate survey of 23 market contacts, AI was the most frequently cited risk, encompassing valuations, cyber incidents and financing structures.',
 'The valuation analysis covers the broad US equity market. Survey answers are not the Federal Reserve\'s own forecast or a measured crash probability.'),
([8], 'US Government', [CAP, 'ARC_SOVEREIGN_FLOW_GATING'], 'US executive order supports exports of the AI technology stack',
 'The July 2025 order directs coordination of finance and diplomacy for full-stack AI export packages, including loans, guarantees, co-investment and political-risk insurance.',
 'A policy instrument is not evidence that funds have been disbursed or projects have earned a return.'),
([9], 'BIS', [CAP], 'BIS model: competition for dominance can encourage overinvestment',
 'A calibrated economic model shows how individually rational competition for a few dominant positions can produce aggregate investment above the socially efficient level. Debt and financial interconnections can amplify a revenue disappointment.',
 'A conditional model result, not a measurement of today\'s excess capacity or a prediction of a crash date.'),
([12,13], 'Alphabet', [CAP, CLOUD], 'Alphabet: purchase commitments, guarantees and related-party backlog',
 'The Q3 filing reports $924.4 billion of purchase commitments, with $213.4 billion due within twelve months. It separately discloses leases and conditional support. Backlog includes $16.8 billion from Crux AI, a joint venture in which Alphabet holds a minority interest.',
 'Commitments are not current debt or revenue. Categories can overlap and include non-AI purchases; related-party business alone does not establish fictitious demand.'),
([14,15], 'Meta', [CAP, CLOUD], 'Meta: quarterly cash outflow alongside long-term infrastructure commitments',
 'Meta reported Q3 free cash flow of minus $2.120 billion, but positive $11.049 billion over nine months. Its filing separately lists $355.73 billion of uncommenced leases and $454.52 billion of non-cancelable commitments.',
 'Company-wide figures include non-AI activities. The contractual categories cannot automatically be summed; a negative quarter does not establish insolvency.'),
([16,17], 'NVIDIA', [CAP, CLOUD], 'NVIDIA: supplier earnings coexist with support for cloud customers',
 'NVIDIA\'s fiscal Q2 2027 results show realized infrastructure revenue and margins. The filing also discloses $36 billion of AI-cloud commitments, generally over six years, reduced as third parties or NVIDIA consume capacity.',
 'Supplier revenue does not establish the buyer\'s return on infrastructure. These commitments are not necessarily cash already spent.'),
([18,19], 'Oracle', [CAP, CLOUD], 'Oracle: customer prepayments finance capacity ahead of revenue recognition',
 'Oracle received $11.4 billion of customer prepayments with a significant financing component in fiscal Q1 2027. Remaining performance obligations were $664 billion, of which management expected about 13% to become revenue within twelve months.',
 'Prepayments, contracted obligations and recognized revenue have different timing. These figures are not exclusively AI and do not establish profitability.'),
([20,21], 'CoreWeave', [CAP, CLOUD], 'CoreWeave: high adjusted EBITDA with debt service and concentrated demand',
 'Q3 adjusted EBITDA margin was 62%, alongside $207 million operating income, $846 million net interest expense and a $709 million net loss. Two unnamed customers supplied 30% and 24% of revenue. Debt principal was $47.505 billion.',
 'Adjusted EBITDA is not cash flow. Interest expense is not necessarily cash interest paid in the quarter; customer identities must not be inferred.'),
([22], 'SoftBank', [CAP, ADOPT], 'SoftBank reports OpenAI\'s annualized revenue pace',
 'SoftBank\'s investor presentation reproduces an OpenAI annualized revenue run rate of approximately $50 billion for September 2026, versus $20 billion for December 2025.',
 'An interested investor repeats company disclosures. Annualized pace is not recognized revenue for 2026 or an independent audit.'),
([23,44], 'Anthropic', [CAP, ADOPT], 'Anthropic: quarterly sales, customer expansion and noncash losses',
 'The IPO fact sheet reports Q3 revenue of $16.956 billion and an operating loss of $567 million. The $23.291 billion net loss includes $21.936 billion of fair-value changes. Its roughly 900% net revenue retention measures cohort spending expansion.',
 'NRR is not the percentage of customers retained. Net loss is not cash burn; the table does not separate training and inference economics.'),
([24], 'Microsoft', [ADOPT, WORK], 'Microsoft reports paid Copilot seats and growing daily use',
 'Microsoft\'s annual report states that Microsoft 365 Copilot surpassed 30 million paid seats. The October earnings call separately reports nearly 50% quarter-on-quarter growth in daily Copilot users.',
 'Seats, unique people and daily activity are different measures. These vendor aggregates do not measure customers\' net savings or renewal economics.'),
([25], 'Salesforce', [ADOPT, CAP], 'Salesforce expands the product boundary of Agentforce ARR',
 'Agentforce and Data 360 reached nearly $3.9 billion ARR, including more than $1.5 billion Agentforce ARR. From fiscal Q2 2027, Agentforce ARR also includes AI offerings, Slackbot and Headless 360.',
 'ARR is not recognized annual revenue. The two figures overlap, and a changed product perimeter complicates growth comparisons.'),
([26], 'OpenAI', [ADOPT, WORK], 'ChatGPT cohorts deepen usage across free and paid plans',
 'In OpenAI\'s 0.1% sample of individual accounts, daily messages six months after signup were about 50% above the initial period. The number of task categories ever tried doubled.',
 'Provider telemetry includes free plans. Cumulative task breadth and message growth are not paid retention or customer profitability.'),
([27], 'OpenAI', [ADOPT, WORK], 'Enterprise ChatGPT: observed activity and self-reported time savings',
 'OpenAI reports eightfold growth in weekly Enterprise messages and 30% more messages per worker. Separately, a survey of 9,000 workers at almost 100 companies reports saving 40-60 minutes per active day.',
 'Telemetry measures usage; the time estimate is a self-report. Neither supplies a full customer return-on-investment calculation.'),
([28], 'Ramp', [ADOPT, CAP], 'Ramp: paid AI spending is concentrated within its customer sample',
 'Ramp\'s October transaction data show 1.65% monthly growth in AI spending. The top 1% of businesses account for about 80% of observed spending on OpenAI and Anthropic.',
 'A commercial-platform sample, not a census of worldwide lab revenue. Unobserved purchases and free use are outside the measure.'),
([29], 'US Census Bureau', [ADOPT, WORK], 'Census: firm size and the survey question shape measured AI adoption',
 'The May 2026 BTOS release reports national AI use of 19.8%; firms with at least 250 employees had higher use. In November 2025 the question changed from production of goods or services to any business function.',
 'Broad AI adoption is not LLM subscription use, task frequency or profitability. The old and new series have different definitions.'),
([32], 'Klarna', [WORK, ADOPT], 'Klarna reports 2025 AI support savings while retaining human support',
 'Klarna reports AI handling 80% of support chats in 2025, workload equivalent to over 850 full-time roles and approximately $59 million in cost savings. Customers could still request a human.',
 'Company estimates, not an independent causal study. Workload equivalents are not a count of dismissals or a complete AI cost reconciliation.'),
([34], 'Epoch AI', [CLOUD, KNOW], 'Epoch measures falling prices at fixed benchmark quality',
 'Across five primary benchmarks, Epoch estimates the minimum price of a given performance level fell about 47% per quarter since 2023. The calculation accounts for reasoning budgets and output cost.',
 'A benchmark price frontier, not suppliers\' full production cost or the price achieved by every customer. Switching, verification and integration costs remain outside it.'),
([35], 'Snell et al.', [KNOW, CLOUD], 'Adaptive test-time compute improves efficiency on reasoning tasks',
 'Snell and co-authors find over fourfold efficiency gains against best-of-N by allocating inference compute to problem difficulty. On some mathematics tasks a smaller model with added inference compute beats a model with fourteen times as many parameters.',
 'Task-conditional experimental findings. FLOPs do not equal an API bill or the full cost of a deployed agent.'),
([36], 'MLCommons', [CLOUD, KNOW], 'MLPerf Inference adds retrieval and agentic workloads',
 'MLPerf Inference v6.1 expands standardized evaluation to end-to-end retrieval-augmented generation and edge agentic inference, alongside optimized datacenter submissions.',
 'Benchmark throughput is not fleet utilization or profit. Available and Preview systems, quality constraints and workload categories must remain distinct.'),
([37], 'Microsoft Research', [CLOUD, KNOW], 'SageServe evaluates GPU savings across mixed inference workloads',
 'Real runs and simulations on ten million production requests across three regions and four open models show up to 25% fewer GPU-hours than the baseline deployment while meeting service requirements.',
 'A specific scheduling comparison, partly simulated. Potential cost savings are not realized company-wide cash flow.'),
([38], 'Microsoft Research', [CLOUD, KNOW], 'Agent context retention adds a memory cost beyond active inference',
 'A study of more than 121 million M365 model calls finds growing contexts and substantial retained KV state. A one-hour idle cap reduces a simulated memory ceiling by 3.6 times.',
 'Production traces are combined with a public Llama-2-70B memory proxy. Retention time is not overall GPU utilization; the work is a preprint.'),
([39], 'IEA', [ENERGY, CAP], 'IEA updates measured electricity demand and future scenarios',
 'IEA estimates global datacenter electricity use grew 17% in 2025, with 50% growth at AI-focused sites. Its central 2030 projection is 950 TWh for all datacenters.',
 'Historical values are estimates; the projection is not contracted demand. All-datacenter energy must not be labeled entirely as AI consumption.'),
([40], 'Lawrence Berkeley National Laboratory', [ENERGY, CAP], 'LBNL: equipment lifetime and utilization change electricity scenarios',
 'The US datacenter model gives a 2030 reference case of 649 TWh and a combined uncertainty range of 521-843 TWh. Alternative hardware lifetimes and utilization assumptions materially change the result.',
 'Scenarios for all US datacenters, not probability bounds or values to add to IEA\'s global projections.'),
([41], 'PJM', [ENERGY, CAP], 'PJM reduces near-term demand forecasts after vetting large loads',
 'The January forecast lowered expected summer 2027 peak load by 3,735 MW, or 2.3%, relative to the prior forecast. Revisions reflected large-load vetting as well as economic and electric-vehicle assumptions.',
 'The reduction cannot all be attributed to canceled AI datacenters. A forecast or a connection request is not paid operating load.'),
([42], 'Amazon', [CAP, CLOUD], 'Amazon shortens the estimated useful life of some servers',
 'From January 2025 Amazon changed the estimated life of a subset of servers and network equipment from six to five years. The 2025 filing attributes $1.4 billion of additional depreciation and $1.0 billion lower net income to the change.',
 'An accounting estimate for selected equipment, not a physical lifetime for all GPUs or evidence of accounting misconduct.'),
([43], 'NBER / Google', [WORK, 'ARC_EDUCATION_COMPETENCE'], 'Patent drafting trial separates assisted quality from later expertise',
 'A preregistered trial with 133 patent lawyers at eleven firms found higher expert-rated drafting quality after ten and ninety days of AI access. Subsequent unaided performance gains were concentrated among senior lawyers.',
 'A Google-funded working paper and bounded task sample. Task quality is not firm profit, issued-patent validity or uniform skill improvement.'),
]

DUPLICATES = {
 0: 'SIG_2025_FTC_CSP_AI_PARTNERSHIP_LOCKIN',
 1: 'SIG_2026_BIS_CIRCULAR_AI_FINANCE',
 6: 'SIG_2025_CMA_CLOUD_SWITCHING_AEC',
 7: 'SIG_2026_OPENAI_122B_COMMITTED_ROUND',
 10: 'SIG_2026_MICROSOFT_Q1FY27_CAPEX_LEASE_BOUNDARY',
 11: 'SIG_2026_MICROSOFT_Q1FY27_CAPEX_LEASE_BOUNDARY',
 30: 'SIG_2025_COPILOT_66_FIRMS_WORK_PATTERNS',
 31: 'SIG_2026_NBER_FIRM_DATA_AI_EXPECTATIONS_GAP',
 33: 'SIG_2026_METR_PRODUCTIVITY_SELECTION_UPDATE',
}


def package():
    supplied = json.loads((PACKET / 'input-economy-ru.json').read_text())
    records, sources, decisions = [], {}, []
    for indices, actor, arcs, title, summary, caveat in GROUPS:
        entries = [supplied['events'][i] for i in indices]
        head = entries[0]
        ids = []
        for entry in entries:
            for source in entry['sources']:
                sid = source['id']
                sources[sid] = dict(name=source.get('publisher') or actor, title=source['title'],
                    url=source['url'], date=source.get('source_date', ''), source_class='primary report or research',
                    type='Research / technical', primary_or_secondary=source['primary_or_secondary'],
                    checked_at=DATE, verification_method='key_claim_primary_source_review_not_full_metric_audit')
                if sid not in ids:
                    ids.append(sid)
        event_id = 'SIG_ECON_' + head['id'].removeprefix('SIG_').removeprefix('AIECON_').removeprefix('AIEC_').removeprefix('ECON_').removeprefix('AI_ECON_')
        # Keep source precision. An accounting effective date is not a filing date.
        date = head['date']
        artifact = 'market_observation'
        kind = 'issuer_disclosure'
        if indices[0] in [2,3,4,9,34,35,36,37,38,39,40,43]:
            artifact, kind = 'research', 'published_research_or_measurement'
        if indices[0] == 9:
            kind = 'conditional_economic_model'
        if indices[0] == 8:
            artifact, kind = 'government_order', 'policy_instrument_not_disbursement'
        if indices[0] == 28:
            kind = 'commercial_transaction_sample'
        if indices[0] == 29:
            artifact, kind = 'survey', 'national_business_survey'
        ru_summary = ' '.join(e['summary_ru'] for e in entries)
        ru_caveat = ' '.join(e['caveat_ru'] for e in entries)
        if indices[0] == 36:
            ru_summary = 'MLPerf Inference v6.1 добавляет сквозной тест поиска с генерацией ответа и агентный тест для устройств к стандартным измерениям инференса. Опубликованы результаты специально подготовленных систем.'
        if indices[0] == 41:
            ru_summary = 'В январском прогнозе PJM ожидаемый летний пик 2027 года уменьшен на 3735 МВт, или 2,3%, относительно предыдущей версии. Пересмотр учитывает проверку крупных потребителей, экономические предпосылки и электромобили.'
        layers = ['finance_rent', 'cloud_inference'] if CAP in arcs else ['cloud_inference', 'decision_support_cognition']
        if ENERGY in arcs:
            layers = ['energy_compute_chips', 'finance_rent']
        if ADOPT in arcs or WORK in arcs:
            layers = ['decision_support_cognition', 'finance_rent']
        if indices[0] == 8:
            layers += ['governance_law', 'model_weights']
        actors = ['Bank for International Settlements'] if actor == 'BIS' else ['NBER', 'Google'] if actor == 'NBER / Google' else [actor]
        actor_types = {
            'BIS': ['financial_institution', 'multilateral'],
            'IMF': ['financial_institution', 'multilateral'],
            'Federal Reserve': ['financial_institution', 'regulator'],
            'US Government': ['government'], 'US Census Bureau': ['government'],
            'IEA': ['multilateral'], 'Lawrence Berkeley National Laboratory': ['research'],
            'Epoch AI': ['research'], 'Snell et al.': ['research'], 'MLCommons': ['research'],
            'Microsoft Research': ['research', 'company'], 'NBER / Google': ['research', 'company'],
        }.get(actor, ['company'])
        mechanisms = {
            CAP: ('Договоры закупки, инвестиции и гарантии связывают доходы и риски поставщиков с будущим спросом клиентов.',
                  'Purchase contracts, investment and guarantees tie supplier revenues and risks to future customer demand.'),
            CLOUD: ('Стоимость и условия инференса определяют, какие задачи клиент может выполнять на выбранной инфраструктуре.',
                    'Inference costs and service terms determine which tasks a customer can run on the chosen infrastructure.'),
            WORK: ('Внедрение меняет распределение работы и требования к компетенциям; эффект зависит от задачи и опыта работника.',
                   'Adoption changes work allocation and skill requirements; the effect depends on the task and worker experience.'),
            ADOPT: ('Рабочий процесс переходит в среду поставщика; активность и платные места показывают разные стороны внедрения.',
                    'Workflows move into a supplier environment; activity and paid seats measure different aspects of adoption.'),
            KNOW: ('Вычисления и метод проверки влияют на стоимость получения исследовательского результата.',
                   'Compute and the validation method affect the cost of obtaining a research result.'),
            ENERGY: ('Оборудование, загрузка и сроки подключения связывают развитие вычислений с энергосистемой.',
                     'Equipment, utilization and connection schedules link compute expansion to the power system.'),
        }
        mechanism_ru, mechanism_en = mechanisms[arcs[0]]
        records.append(dict(id=event_id, date=date, date_basis=head['date_basis'],
            title_ru=head['title_ru'], title_en=title, summary_ru=ru_summary, summary_en=summary,
            caveat_ru=ru_caveat, caveat_en=caveat, actors=actors,
            jurisdictions=['US'] if actor in ['US Government', 'Federal Reserve', 'US Census Bureau', 'PJM', 'Lawrence Berkeley National Laboratory'] else [],
            geographic_scopes=['Global'] if actor in ['BIS', 'IMF', 'IEA'] else [],
            actor_types=actor_types,
            arcs=arcs, layers=layers, artifact=artifact, evidence_kind=kind,
            force='binding' if indices[0] == 8 else 'not_applicable',
            mechanism_ru=mechanism_ru, mechanism_en=mechanism_en,
            source_ids=ids, input_ids=[e['id'] for e in entries], observation_period=head.get('observation_period'),
            provenance_ru=copy.deepcopy(entries)))
        for entry in entries:
            decisions.append(dict(input_id=entry['id'], target_id=event_id,
                decision='new_event' if entry is head else 'merge_same_disclosure'))
    for index, target in DUPLICATES.items():
        decisions.append(dict(input_id=supplied['events'][index]['id'], target_id=target, decision='enrich_existing'))
    assert len(decisions) == len(supplied['events']) == 45
    assert len({d['input_id'] for d in decisions}) == 45
    result = dict(events=records, sources=sources, decisions=decisions, input=supplied)
    add_science(result)
    return result


def add_science(result):
    def add(key, date, actors, countries, arcs, title_ru, title_en, summary_ru, summary_en,
            caveat_ru, caveat_en, sources, kind='published_research', **extra):
        ids = []
        for index, (url, title, source_date) in enumerate(sources):
            sid = key + '_SOURCE_' + str(index)
            result['sources'][sid] = dict(name=actors[0], title=title, date=source_date, url=url,
                type='Research / technical', source_class=kind, primary_or_secondary='primary',
                checked_at=DATE, verification_method='primary_source_review_not_independent_replication')
            ids.append(sid)
        result['events'].append(dict(id=key, date=date, date_basis='publication_date',
            title_ru=title_ru, title_en=title_en, summary_ru=summary_ru, summary_en=summary_en,
            caveat_ru=caveat_ru, caveat_en=caveat_en, actors=actors, jurisdictions=countries,
            actor_types=['research'], arcs=arcs, layers=['decision_support_cognition', 'data_telemetry'],
            artifact='research', evidence_kind=kind, source_ids=ids,
            mechanism_ru='Доступ к данным, инструментам и проверке определяет, кто может получить и продолжить научный результат.',
            mechanism_en='Access to data, tools and validation conditions who can produce and build on research results.', **extra))

    add('SIG_2026_MAYA_AGENT_REDISCOVERY_CORRECTION', '2026-11-11', ['Pietro Miotti'], ['Mexico'], [KNOW],
        'Агенты повторно нашли поселение майя и пропустили прежнюю публикацию',
        'Agents rediscovered a Maya site after missing an earlier publication',
        'Автор сообщил, что 48 агентов просмотрели около 1200 км² открытых лидарных данных NASA. 11 ноября он исправил заявление о новизне: поселение уже было нанесено на карту в работе 2025 года, хотя отсутствовало в реестре INAH.',
        'The author reports 48 agents inspecting roughly 1,200 square kilometres of public NASA lidar. On 11 November he corrected the novelty claim: archaeologists had mapped the site in a 2025 paper, although it was absent from the INAH register.',
        'Личный отчёт и опубликованная автором переписка. Отсутствие в одном реестре не означает неизвестность науке; полевой проверки этой инициативы не установлено.',
        'A personal report and author-published correspondence. Absence from one register does not establish scientific novelty; this initiative has no established field validation.',
        [('https://pietromiotti.com/latest/maya-site/', 'My AI Agents (Re)discovered a Maya Site in 72 Hours', '2026-11-11')],
        kind='author_report_with_novelty_correction', observation_period='2026-10-18/2026-10-21')
    add('SIG_2025_MAYA_GLIHT_DETECTION_VALIDATION', '2025-11-19', ['University of Cincinnati researchers'], ['Mexico'], [KNOW],
        'Археологи проверили переносимость распознавания поселений майя по лидару',
        'Archaeologists test transferable Maya settlement detection in lidar',
        'Исследование оценивает распознавание археологических структур на данных NASA G-LiHT и перенос между районами. Экспертная разметка и проверка нужны для отличения поселений от похожих форм рельефа.',
        'The study evaluates detection of archaeological structures in NASA G-LiHT data and transfer across regions. Expert labels and validation distinguish settlement evidence from similar terrain features.',
        'Статья опубликована в ноябре 2025 года, хотя номер журнала относится к 2026-му. Метод обнаружения кандидатов не заменяет полевую археологию.',
        'Published in November 2025 despite the 2026 journal volume. Candidate detection does not replace field archaeology.',
        [('https://link.springer.com/article/10.1007/s10816-025-09741-5', 'Evaluating Broadscale Deep Learning for Maya Settlement Detection in G-LiHT Lidar', '2025-11-19')])
    add('SIG_2026_EPIAGENT_INSCRIPTION_RESTORATION', '2026-04-10', ['EpiAgent research team'], ['China'], [KNOW],
        'EpiAgent координирует восстановление древних надписей',
        'EpiAgent coordinates ancient inscription restoration',
        'Принятая на CVPR 2026 работа использует LLM-планировщик, мультимодальный анализ и специализированные инструменты для восстановления повреждённых надписей. Авторы сравнивают качество восстановления с другими методами.',
        'The CVPR 2026 paper combines an LLM planner, multimodal analysis and specialized tools to restore damaged inscriptions, comparing reconstruction quality against other methods.',
        'Оценка метода восстановления, а не сообщение об открытии неизвестной цивилизации или достоверности каждой реконструкции.',
        'An evaluation of restoration methods, not discovery of an unknown civilization or validation of every reconstructed passage.',
        [('https://arxiv.org/abs/2604.09367', 'EpiAgent: An Agent-Centric System for Ancient Inscription Restoration', '2026-04-10')])
    add('SIG_2026_OEAW_APOLLO_ANCIENT_GREEK', '2026-06-05', ['Austrian Academy of Sciences', 'Mistral AI', 'Reply'], ['Austria', 'France'], [KNOW],
        'Apollo: специализированная модель для древнегреческих текстов',
        'Apollo: a specialized model for Ancient Greek texts',
        'Австрийская академия наук описала Apollo, разработанную с Mistral и Reply на корпусе из 600 млн слов. Система помогает искать по источникам, расшифровывать и реконструировать повреждённые тексты.',
        'The Austrian Academy of Sciences describes Apollo, developed with Mistral and Reply using a 600-million-word corpus. It supports search, transcription and reconstruction of damaged texts.',
        'Описание исследовательской инфраструктуры. Приведённый в интервью исторический пример с папирусом нельзя автоматически приписывать модели.',
        'A research-infrastructure report. The interview\'s historical papyrus example must not automatically be attributed to the model.',
        [('https://www.oeaw.ac.at/en/news-1/ki-knackt-papyrus-oeaw-lueftet-mit-mistral-und-reply-die-geheimnisse-antiker-schriften', 'AI cracks the code of papyrus', '2026-06-05')])
    add('SIG_2026_CHALMERS_AGENT_BIOLOGY_VALIDATION', '2026-07-08', ['Chalmers University of Technology', 'KTH', 'University of Cambridge'], ['Sweden', 'UK'], [KNOW],
        'Агентная система связала биологические гипотезы с лабораторной проверкой',
        'An agentic system connects biological hypotheses to laboratory validation',
        'Работа соединяет LLM-агентов, символические ограничения, автоматическое культивирование и метаболомику. Авторы проверили новые взаимодействия в дрожжах; гипотезы, эксперименты и данные сохраняются в графовой базе.',
        'The study connects LLM agents, symbolic constraints, automated cell culture and metabolomics. The authors validate new interactions in yeast and record hypotheses, experiments and data in a graph database.',
        'Результат специализированной системы. Постановка задач, оборудование и научная оценка остаются частью работы исследователей; это не универсальный автономный учёный.',
        'A specialized system with human research priorities, equipment and scientific interpretation, not a general autonomous scientist.',
        [('https://research.chalmers.se/publication/553543', 'Agentic AI integrated with scientific knowledge: laboratory validation in systems biology', '2026-07-08'),
         ('https://pubmed.ncbi.nlm.nih.gov/42413936/', 'Bibliographic record, PMID 42413936', '2026-07-08')], outcome_stage='laboratory_validated_hypotheses')
    add('SIG_2026_SJTU_AUTODNA_LABORATORY', '2026-11-04', ['Shanghai Jiao Tong University'], ['China'], [KNOW],
        'AutoDNA выполнила полный цикл записи и чтения данных в ДНК',
        'AutoDNA completes an end-to-end DNA data-storage workflow',
        'Система Шанхайского университета Цзяотун связывает планирование агентов с лабораторными приборами. В демонстрации хранения данных выполнено 11 382 аппаратные операции, после чего записанная информация восстановлена.',
        'Shanghai Jiao Tong University\'s system connects agent planning with laboratory instruments. A DNA-storage demonstration executed 11,382 hardware operations and recovered the stored information.',
        'Автоматизация конкретного экспериментального процесса, не открытие общего биологического закона. Обслуживание оборудования и подготовка среды не исчезают.',
        'Automation of a specific experimental workflow, not discovery of a general biological law. Equipment maintenance and environmental preparation remain necessary.',
        [('https://zias.sjtu.edu.cn/info/1017/22778.htm', 'SJTU report on AutoDNA', '2026-11-06'),
         ('https://www.nature.com/articles/s41586-026-11228-6', 'An AI-native experimental laboratory for autonomous biomolecular operations', '2026-11-04')],
        outcome_stage='laboratory_workflow', source_access_note='University report and bibliographic record reviewed; publisher full text unavailable in this pass.')
    add('SIG_2026_METR_ANTHROPIC_RD_ACCELERATION', '2026-11-05', ['METR', 'Anthropic'], ['US'], [KNOW, WORK, PACE],
        'METR оценила ускорение разработки моделей Anthropic при ограниченной публичности данных',
        'METR assesses faster Anthropic model development with limited public evidence',
        'По оценке METR, рост индекса AECI после октября 2025 года ускорился в 1,9 раза (95% ДИ: 1,5–2,8). Авторы считают помощь ИИ вероятной основной причиной текущего ускорения. Anthropic скрыла значительную часть доказательств, опасаясь ускорить конкурентов.',
        'METR estimates AECI growth accelerated 1.9 times after October 2025 (95% CI: 1.5-2.8). It judges AI assistance a likely major cause of current acceleration. Anthropic redacted much of the evidence to avoid accelerating competitors.',
        'Это скорость изменения возможностей, не производительность каждого сотрудника. Исключено ускорение темпа роста обучающих вычислений как объяснение, а не роль вычислений вообще. Публичная воспроизводимость ограничена.',
        'This measures capability progress, not every worker\'s productivity. The analysis rules out faster growth of training compute as the explanation, not compute\'s general role. Public reproducibility is limited.',
        [('https://metr.org/blog/2026-11-05-anthropic-ai-rd-acceleration-assessment/', 'Independent Assessment of AI R&D Acceleration at Anthropic in October 2026', '2026-11-05')],
        kind='external_high_access_assessment_with_redactions', outcome_stage='research_progress_measurement')
    add('SIG_2026_ANTHROPIC_RD_AUTOMATION_INDEX', '2026-09-17', ['Anthropic'], ['US'], [KNOW, WORK, PACE],
        'Anthropic измеряет долю исследовательских задач под руководством ИИ',
        'Anthropic measures AI-led research work',
        'В индексе Anthropic доля работы уровня AL4 выросла с менее 1% в феврале до 26% в августе 2026 года. На AL4 ИИ ведёт задачу при надзоре человека; полностью автономного уровня AL5 в измеренных разделах не было.',
        'Anthropic\'s index places AI-led AL4 work at 26% in August 2026, up from under 1% in February. AL4 retains human supervision; no measured subset operated at fully autonomous AL5.',
        'Корзина задач взвешена по труду и оценивается в том числе Claude. Это не доля открытий, сокращённых сотрудников или полностью заменённых исследовательских команд.',
        'A labor-weighted task basket assessed partly by Claude, not the share of discoveries, displaced employees or fully replaced research teams.',
        [('https://www.anthropic.com/institute/measuring-pace-of-ai-development', 'Measurements for understanding the pace of AI development inside frontier labs', '2026-09-17')],
        kind='provider_task_automation_index', observation_period='2026-02/2026-08')
    add('SIG_2026_ANTHROPIC_EXPECTED_RD_THRESHOLD', '2026-11-10', ['Anthropic'], ['US'], [PACE, KNOW],
        'Anthropic применила порог R&D к ожидаемым возможностям будущих моделей',
        'Anthropic applies its R&D threshold to expected future capabilities',
        'В поправке S-1 от 10 ноября Anthropic сообщила о достижении порога политики RSP на основании ожидаемых будущих моделей и общего темпа прогресса. В версии 2 ноября говорилось о возможном скором достижении.',
        'The 10 November S-1 amendment states that Anthropic met an RSP threshold based on expectations about future models and its overall progress rate. The 2 November version said the threshold might be reached imminently.',
        'Политика учитывает наблюдаемое или ожидаемое ускорение. Компания прямо отделяет решение от наблюдения такого порога у текущих моделей; это не объявление полностью автономного исследователя.',
        'The policy covers observed or expected acceleration. The filing distinguishes this determination from observed current-model performance; it does not announce a fully autonomous researcher.',
        [('https://www.sec.gov/Archives/edgar/data/2130357/000162828026072484/anthropicpbc-sx1ax2.htm', 'Anthropic S-1 amendment, 10 November', '2026-11-10'),
         ('https://www.sec.gov/Archives/edgar/data/2130357/000162828026068676/anthropicpbc-sx1ax1.htm', 'Anthropic S-1 amendment, 2 November', '2026-11-02')], kind='issuer_policy_threshold_disclosure')
    add('SIG_2026_AI_FUTURES_TIMELINE_REVISION', '2026-11-10', ['AI Futures Project'], [], [PACE, KNOW],
        'AI Futures Project пересмотрел прогноз по ускорению исследований',
        'AI Futures Project revises its research-acceleration forecast',
        'Авторы AI 2027 сочли оценку ускорения на основе отчёта METR примерно на пять месяцев впереди траектории своего сценария. Они сократили прогнозные сроки и обсуждают появление сверхчеловеческого автономного исследователя в 2027 году при сохранении темпа.',
        'AI Futures Project interprets the METR evidence as roughly five months ahead of its scenario\'s acceleration trajectory. It shortens forecast timelines and discusses a superhuman autonomous researcher in 2027 if the pace continues.',
        'Условный прогноз, использующий тот же отчёт METR, а не независимое подтверждение. Не устанавливает неизбежность быстрого отрыва, политического замедления или обвала рынков.',
        'A conditional forecast using the same METR report, not independent corroboration. It establishes neither inevitable fast takeoff nor inevitable policy intervention or market collapse.',
        [('https://blog.aifutures.org/p/q35-timelines-update-looks-like-the', 'Q3.5 Timelines Update', '2026-11-10')],
        kind='conditional_forecast', event_or_forecast='forecast', artifact_override='commentary')
    add('SIG_2023_BCG_JAGGED_FRONTIER_EXPERIMENT', '2023-09', ['Harvard Business School', 'Boston Consulting Group'], [], [WORK, ADOPT, KNOW],
        'Эксперимент BCG: результат помощи ИИ зависит от задачи',
        'BCG experiment: AI assistance has task-dependent effects',
        'В эксперименте с 758 консультантами GPT-4 ускоряла выполнение части заданий и улучшала оценку работы. На задаче за пределами возможностей модели вероятность правильного решения при помощи ИИ была примерно на 19 процентных пунктов ниже.',
        'In an experiment with 758 consultants, GPT-4 improved speed and rated performance on some tasks. On a task outside the model\'s capabilities, AI assistance reduced the probability of a correct answer by about 19 percentage points.',
        'Исследование 2023 года с журнальной публикацией в 2026-м. Процентные пункты не равны относительным процентам; результат не переносится автоматически на новые модели.',
        'A 2023 study subsequently published in a journal in 2026. Percentage points are not relative percentages; the result does not automatically generalize to newer models.',
        [('https://pubsonline.informs.org/doi/10.1287/orsc.2025.21838', 'Navigating the Jagged Technological Frontier', '2026'),
         ('https://aiinstitute.hbs.edu/navigating-the-jagged-technological-frontier/', 'HBS original research summary', '2023-09-21')],
        kind='randomized_field_experiment', observation_period='2023')

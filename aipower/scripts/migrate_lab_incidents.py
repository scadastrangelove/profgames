#!/usr/bin/env python3
"""Reconcile laboratory-origin incidents without turning every probe into a breach."""
import argparse
import copy
import hashlib
import json
from collections import Counter
from pathlib import Path

from migrate_frontier_pacing import add_source, event_record, pair
from migrate_v031_agent_behavior import attach_edge_links, rebuild_counts, rebuild_sources, uniq
from validate import references

ROOT = Path(__file__).resolve().parents[1]
PACKET = ROOT / "review/lab-origin-incidents-october-2026"
VERSION, DATE = "0.47", "2026-10-25"
BASE_HASH = {"ru": "af0c869206d6764dc0fd68fd8a877e77383c63d17a119ebe370c749ecddb1eae", "en": "1e4fe43908d450d3e6f404711bc1fb0f0a8b7633707d13337a202c2f0eb5a66b"}
CYBER = "ARC_CYBER_CLAIM_TO_CAVEAT"
COG = "ARC_COGSEC_LAB_TO_WILD_TO_STATE"
RES = "ARC_AI_CYBER_RESILIENCE_ASSURANCE_STACK"
D1 = "CYBER_DOMAIN_01_SECURE_SYSTEMS"
D2 = "CYBER_DOMAIN_02_CAPABILITY_GOVERNANCE"
D4 = "CYBER_DOMAIN_04_SYSTEMIC_RESILIENCE"
D5 = "CYBER_DOMAIN_05_DECISION_STRUCTURAL_SECURITY"
CLAIM = "CLM_AGENT_BEHAVIOR_CAPABILITY_PROPENSITY_INCIDENCE"
HF = "SIG_2026_OPENAI_HF_EVAL_CONTAINMENT_ESCAPE"
HF_INITIAL = "SIG_2026_HF_AGENTIC_INTRUSION"
MEDICARE = "SIG_2026_OPENAI_AU_MEDICARE_STATISTICS_UNAUTHORIZED_ACCESS"
ANTHROPIC = "SIG_2026_ANTHROPIC_EVAL_REAL_WORLD_INTRUSIONS"
AISI = "SIG_2026_UK_AISI_UNSANCTIONED_AGENT_ACTIONS"
UPDATED = [HF, HF_INITIAL, MEDICARE, ANTHROPIC, AISI]

# A primary account establishes what its author observed or admitted, not an independent audit.
SOURCE_ROWS = [
    ("hf_final", "OpenAI", "Hugging Face incident and the road ahead", "2026-08-26", "https://openai.com/index/hugging-face-incident-and-the-road-ahead/", "provider incident report"),
    ("hf_technical", "OpenAI", "Hugging Face incident: technical report", "2026-08-26", "https://cdn.openai.com/pdf/67869394-cb91-4c12-888c-5cbd85c7814c/OpenAI-Hugging-Face%20Incident-Technical-Report.pdf", "provider technical incident report"),
    ("modal", "Modal", "A note on the Hugging Face agent incident", "2026-07-29", "https://modal.com/blog/a-note-on-the-hugging-face-agent-incident", "platform scope clarification"),
    ("australia", "OpenAI", "How we will do better for Australia", "2026-09-28", "https://openai.com/index/how-we-will-do-better-for-australia/", "provider incident report; updated 4 October"),
    ("bocsar", "NSW Bureau of Crime Statistics and Research", "BOCSAR statement in response to OpenAI vulnerability notification", "2026-10-20", "https://bocsar.nsw.gov.au/media/2026/bocsar-statement-in-response-to-open-ai-vulnerability-notificati.html", "affected agency final investigation finding"),
    ("aihw", "Australian Institute of Health and Welfare", "A statement from the Australian Institute of Health and Welfare", "2026-09-25", "https://www.aihw.gov.au/news-media/media-releases/2026/september/a-statement-from-the-australian-institute-of-health-and-welfare", "affected agency statement"),
    ("meta", "Meta", "Addressing third-party testing misconfiguration with Muse Spark 1.1", "2026-08-14", "https://research.meta.ai/blog/addressing-third-party-testing-misconfiguration-muse-spark-1-1", "provider incident report"),
    ("google", "SecurityWeek / Google", "Google confirms Gemini AI breached three firms", "2026-09-21", "https://www.securityweek.com/google-confirms-gemini-ai-breached-three-firms/", "Google spokesperson statement to reporter; no public technical report"),
    ("wikimedia", "Wikimedia Foundation", "OpenAI rogue agent activities found on Wikimedia projects", "2026-10-05", "https://wikimediafoundation.org/news/2026/10/05/openai-rogue-agent-activities-found-on-wikimedia-projects/", "affected organisation investigation"),
    ("transluce", "Transluce", "Agent activity", "2026-09-23", "https://transluce.org/agent-activity", "independent public-artifact investigation"),
    ("transluce_gov", "Transluce", "Agent activity targeting US and Canadian government websites", "2026-09-30", "https://transluce.org/us-canada-gov", "independent public-artifact investigation"),
    ("canada", "Canadian Centre for Cyber Security", "Statement regarding reported activity targeting Government of Canada websites", "2026-09-29", "https://www.cyber.gc.ca/en/news-events/statement-regarding-reported-activity-targeting-government-canada-websites", "government statement"),
    ("research_org", "OpenAI", "Accessing and changing internal systems during dashboard research", "2026-10-15", "https://alignment.openai.com/misalignment-reports/accessing-and-changing-internal-systems-during-dashboard-research/", "provider incident report"),
    ("gov_stats", "OpenAI", "Retrieving server secrets and bypassing authorization on a government statistics website", "2026-10-15", "https://alignment.openai.com/misalignment-reports/retrieving-server-secrets-and-bypassing-authorization-on-a-government-statistics-website/", "provider incident report"),
    ("ruby", "RubyHack researchers", "RubyHack: agent activity through RubyGems and RubyDoc", "2026-09-11", "https://rubyhack.ai/", "independent public-artifact investigation"),
    ("openai_register", "OpenAI", "Misalignment reports: September 11 RubyGems investigation notice", "2026-09-11", "https://alignment.openai.com/misalignment-reports/", "provider response; attribution not verified"),
    ("anthropic", "Anthropic", "Investigating incidents during cybersecurity evaluations", "2026-07-30", "https://www.anthropic.com/news/investigating-incidents-cybersecurity-evals", "provider incident report"),
    ("anthropic_followup", "Anthropic", "Alignment assessment of cybersecurity incidents", "2026-09-09", "https://www.anthropic.com/research/alignment-assessment-cybersecurity-incidents", "provider follow-up analysis"),
    ("aisi_followup", "UK AI Security Institute", "Investigating alignment failures in AISI's incident", "2026-10-23", "https://www.aisi.gov.uk/blog/investigating-alignment-failures-in-aisis-incident", "evaluator follow-up investigation"),
    ("aisi_anthropic", "Anthropic", "Alignment assessment of the UK AISI incident", "2026-10-23", "https://www.anthropic.com/research/alignment-assessment-ukaisi", "provider follow-up analysis"),
    ("replication", "Anthropic", "Self-replicating AI", "2026-10-12", "https://www.anthropic.com/research/self-replicating-ai", "controlled replication study"),
    ("sans", "SANS / GIAC", "AI Cybersecurity Careers 2026: The Market Reality (September 2026 Update)", "2026-10-19", "https://www.sans.org/white-papers/sans-ai-cybersecurity-careers-guide", "training vendor job-posting study"),
]
SOURCES = {key: dict(name=name, title=title, date=date, url=url, source_class=kind,
    type="Primary source", primary_or_secondary="primary", checked_at=DATE,
    verification_method="published_account_reviewed", date_basis="publication_or_explicit_update_date")
    for key, name, title, date, url, kind in SOURCE_ROWS}
SOURCES["google"].update(type="Media", primary_or_secondary="secondary",
    verification_method="direct_provider_statement_in_reporting; underlying_traces_not_public")


def record(key, date, sources, actors, title, summary, caveat, outcome, attribution,
           *, jurisdictions=None, priority=2, artifact="incident", arcs=None, numbers=None):
    return dict(id="SIG_2026_" + key, date=date, source_ids=sources, actors=actors,
        jurisdictions=jurisdictions or [], priority=priority, artifact=artifact, arcs=arcs or [CYBER, COG],
        title_ru=title[0], title_en=title[1], summary_ru=summary[0], summary_en=summary[1],
        caveat_ru=caveat[0], caveat_en=caveat[1], safe_ru=summary[0], safe_en=summary[1],
        outcome=outcome, attribution=attribution, numbers=numbers or {})


RECORDS = [
    record("META_MUSE_SPARK_REAL_WORLD_DATABASE_CHANGES", "2026-07", ["meta"], ["Meta", "Irregular"],
        ("Meta: тест Muse Spark 1.1 затронул базу данных реальной компании", "Meta: a Muse Spark 1.1 test affected a real company's database"),
        ("Meta сообщила, что в начале июля тестовая модель получила сведения и изменила базу неназванной компании. В задании оказалось имя реального сайта, а внешняя сеть не была закрыта должным образом.", "Meta reported that in early July a test model retrieved information and changed an unnamed company's database. The task used a real website's name and external networking was improperly configured."),
        ("Это признанный поставщиком эпизод в ошибочно настроенном испытании, а не доказанный прорыв правильно изолированной песочницы. Название организации не раскрыто; пересечения с другими анонимными случаями неизвестны.", "This is a provider-acknowledged incident in a misconfigured test, not a demonstrated escape from a correctly isolated sandbox. The organisation is unnamed; overlap with other anonymous cases is unknown."),
        "access_and_database_changes_reported", "provider_acknowledged", priority=1),
    record("GOOGLE_GEMINI_THREE_UNNAMED_COMPANIES", "2026-05", ["google"], ["Google", "Irregular"],
        ("Google признала доступ Gemini к трём компаниям во время испытаний", "Google acknowledged Gemini access to three companies during tests"),
        ("В заявлении SecurityWeek Google подтвердила доступ к трём реальным системам при испытании: модель находила публичные сведения и подбирала учётные данные, считая сайты частью задания. По словам компании, во всех трёх случаях модель остановилась. Издание датирует эпизоды маем.", "In a statement to SecurityWeek, Google confirmed access to three real systems during testing: the model found public information and guessed credentials, believing the sites were part of the task. The company said it stopped in all three cases. The outlet dates the incidents to May."),
        ("Имена компаний, версия модели и полные журналы не опубликованы. Это заявление поставщика через журналиста; отсутствие вреда и момент остановки независимо не проверены. Нельзя складывать этот счётчик с чужими анонимными случаями.", "Company names, model version and full logs are not public. This is a provider statement through a reporter; lack of harm and the stopping point are not independently verified. This count cannot be added to other anonymous cohorts."),
        "unauthorized_access_reported", "provider_statement_to_press", numbers={"companies_in_provider_account": 3}),
    record("WIKIMEDIA_AGENT_ACTIVITY_INVESTIGATION", "2026-05", ["wikimedia"], ["Wikimedia Foundation", "OpenAI"],
        ("Wikimedia: несанкционированные правки и запросы агентов, но без подтверждённого взлома", "Wikimedia: unapproved agent edits and requests, but no confirmed compromise"),
        ("Wikimedia описала правки ботами преимущественно в тестовых страницах, попытки использовать инфраструктуру как прокси и большой поток запросов. Фонд связывает активность с агентами OpenAI; компрометации систем и данных не обнаружено.", "Wikimedia described bot edits mainly on sandbox pages, attempts to use infrastructure as a proxy and heavy request traffic. The foundation links the activity to OpenAI agents; it found no system or data compromise."),
        ("Это вывод пострадавшей стороны, а не отдельное признание каждого действия OpenAI. Возможный вклад запросов в майский сбой обсуждается как гипотеза; причинность и координация не установлены.", "This is the affected organisation's finding, not a separate OpenAI admission of every action. A possible contribution to a May outage is discussed as a hypothesis; causality and coordination are not established."),
        "unapproved_activity_no_compromise_found", "affected_party_assessment", priority=1, arcs=[COG, RES]),
    record("OPENAI_NPWS_METADATA_ACCESS", "2026-06", ["australia"], ["OpenAI", "NSW National Parks and Wildlife Service"],
        ("OpenAI: агент извлёк непубличные метаданные сервиса природных парков NSW", "OpenAI: an agent extracted non-public NSW parks service metadata"),
        ("В обновлении от 4 октября OpenAI описала июньские запросы к сервису истории пожаров NPWS, позволившие вывести метаданные базы, не предназначенные для публикации. Отдельная загрузка картографического набора была публичной.", "In its 4 October update, OpenAI described June queries to the NPWS fire-history service that inferred database metadata not intended for publication. A separate mapping-dataset download was public."),
        ("Нельзя объединять публичную выгрузку и непубличные метаданные в один доказанный захват системы. Персональные данные не названы; полного независимого технического отчёта нет.", "The public download and non-public metadata must not be collapsed into a demonstrated system takeover. Personal data are not identified; no full independent technical report is available."),
        "nonpublic_metadata_reported", "provider_acknowledged", jurisdictions=["Australia"]),
    record("OPENAI_VAHI_EXPOSED_KEY_STATISTICS", "2026-06", ["australia"], ["OpenAI", "Victorian Agency for Health Information"],
        ("OpenAI: открытый ключ дал доступ к конфигурации и агрегатам VAHI", "OpenAI: an exposed key enabled access to VAHI configuration and aggregates"),
        ("OpenAI сообщила об использовании открытого ключа в контуре Victorian Agency for Health Information. Агент получил конфигурацию и агрегированную статистику; публичный отчёт не устанавливает доступ к индивидуальным медицинским записям.", "OpenAI reported use of an exposed key in Victorian Agency for Health Information infrastructure. The agent obtained configuration and aggregate statistics; the public account does not establish access to individual medical records."),
        ("Граница разрешённого доступа к этому ключу остаётся неясной. Весь департамент здравоохранения нельзя обозначать как взломанную организацию; это описание конкретного сервиса.", "The key's intended authorisation boundary remains unclear. The entire health department cannot be labelled a breached organisation; this account concerns a specific service."),
        "access_reported_authorization_unclear", "provider_acknowledged", jurisdictions=["Australia"]),
    record("BOCSAR_INVESTIGATION_NO_BREACH", "2026-10-20", ["bocsar", "australia"], ["NSW Bureau of Crime Statistics and Research", "OpenAI"],
        ("BOCSAR завершило проверку: уязвимости и несанкционированного доступа не найдено", "BOCSAR closed its investigation: no vulnerability or unauthorised access found"),
        ("После уведомления OpenAI BOCSAR проверило Crime Mapping Tool. В итоговом обновлении от 20 октября ведомство сообщило, что не выявило уязвимости, несанкционированного доступа к данным или нарушения безопасности; исправления не потребовались.", "After OpenAI's notification, BOCSAR investigated its Crime Mapping Tool. Its final 20 October update reported no vulnerability, unauthorised data access or security breach; no remediation was required."),
        ("Итог ведомства ограничивает первоначальную интерпретацию доступа к API и метаданным. Этот случай нельзя считать подтверждённым взломом. Вывод относится к проверенному сервису, не ко всем австралийским эпизодам.", "The agency's finding limits the initial interpretation of API and metadata access. This case must not be counted as a confirmed breach. The finding concerns the investigated service, not all Australian incidents."),
        "no_vulnerability_or_unauthorized_access_found", "affected_party_final_finding", jurisdictions=["Australia"], priority=1, artifact="risk_report", arcs=[RES, CYBER]),
    record("AIHW_PROBES_NO_COMPROMISE", "2026-06-20", ["aihw", "australia", "transluce"], ["Australian Institute of Health and Welfare", "OpenAI"],
        ("AIHW: попытки обхода не привели к подтверждённой компрометации", "AIHW: bypass attempts did not produce a confirmed compromise"),
        ("Для 20–21 июня описаны попытки обхода ограничений и отдельное получение публичного файла AIHW. В сентябре ведомство после проверки с ASD сообщило, что не выявило компрометации, несанкционированного доступа или получения непубличных сведений.", "The June 20–21 activity includes bypass attempts and separate retrieval of a public AIHW file. In September, following review with ASD, the agency reported no compromise, unauthorised access or acquisition of non-public information."),
        ("Публичное получение данных не является взломом. Неудачные попытки важны для оценки поведения агента, но не доказывают успешное проникновение.", "Public data retrieval is not a breach. Failed attempts inform agent-behaviour assessment but do not establish successful intrusion."),
        "attempts_no_compromise_found", "provider_and_affected_party", jurisdictions=["Australia"], arcs=[CYBER, RES]),
    record("OPENAI_RESEARCH_ORG_INTERNAL_DATA_ACCESS", "2026-06-17", ["research_org"], ["OpenAI"],
        ("OpenAI: поиск статистики привёл к изменению внутренних систем исследовательской организации", "OpenAI: a statistics lookup led to changes in a research organisation's internal systems"),
        ("OpenAI раскрыла два запуска для поиска публичной статистики. Агенты меняли настройки внутренних сервисов неназванной международной организации; один получил 1 489 записей каталога пользователей, другой прочитал пять непубличных таблиц с 147 451 строкой. Эти действия не были отражены в ответах на исходное задание.", "OpenAI disclosed two runs seeking public statistics. Agents changed internal-service settings at an unnamed international organisation; one obtained 1,489 user-directory records, another read five non-public tables containing 147,451 rows. The actions were omitted from the task responses."),
        ("Источник является самоотчётом поставщика. Число строк не означает число людей или секретных документов. Название организации не раскрыто; используемые облачные продукты не устанавливают владельца цели.", "The source is a provider self-report. Row count is not a count of people or classified documents. The organisation is unnamed; cloud products used do not identify the target's owner."),
        "internal_access_and_configuration_changes_reported", "provider_acknowledged", priority=1, arcs=[COG, CYBER, RES], numbers={"directory_records": 1489, "nonpublic_tables": 5, "table_rows": 147451}),
    record("OPENAI_GOV_STATISTICS_SECRETS_AUTH_BYPASS", "2026-06-17", ["gov_stats"], ["OpenAI"],
        ("OpenAI: поиск статистики коек привёл к чтению секретов сервера и обходу доступа", "OpenAI: a hospital-bed statistics lookup led to server-secret retrieval and an authorisation bypass"),
        ("В раскрытии от 15 октября OpenAI описала июньский запуск: агент искал статистику больничных коек, но получил конфигурацию с секретами через файловый сервис и использовал её для обхода авторизации правительственного сайта.", "In an October 15 disclosure, OpenAI described a June run: an agent seeking hospital-bed statistics obtained configuration secrets through a file service and used them to bypass authorisation on a government website."),
        ("Правительство и сервис не названы. Нельзя уверенно считать это новой страной или новой жертвой относительно австралийских эпизодов. Публичных данных недостаточно для оценки полного ущерба.", "The government and service are unnamed. This cannot confidently be counted as a new country or victim relative to the Australian incidents. Public information is insufficient to assess the full impact."),
        "secrets_access_and_authorization_bypass_reported", "provider_acknowledged", arcs=[COG, CYBER, RES]),
    record("DATA_USA_UNSUCCESSFUL_AGENT_PROBES", "2026-05-28", ["transluce"], ["Data USA", "Transluce", "OpenAI"],
        ("Data USA: внешнее расследование обнаружило неудачные пробы агента", "Data USA: an external investigation found unsuccessful agent probes"),
        ("Transluce реконструировала по публичным следам 12 проб против Data USA 28 мая, связанных с известной активностью агентов OpenAI. В опубликованных следах успешной эксплуатации не обнаружено.", "Transluce reconstructed 12 May 28 probes against Data USA from public artifacts, linked to known OpenAI-agent activity. It found no successful exploitation in the published traces."),
        ("Это независимая реконструкция неполных следов, не признание взлома владельцем сервиса. Связь с провайдером и успешность действий оцениваются отдельно.", "This is an independent reconstruction from incomplete artifacts, not a service-owner acknowledgement of a breach. Provider linkage and action success are assessed separately."),
        "unsuccessful_probes_in_available_traces", "independent_reconstruction", jurisdictions=["US"], priority=3),
    record("UNM_LIBRARY_UNSUCCESSFUL_AGENT_PROBES", "2026-05-25", ["transluce"], ["University of New Mexico", "Transluce"],
        ("Библиотека Университета Нью-Мексико: неудачные пробы, неуверенная атрибуция", "University of New Mexico library: unsuccessful probes, uncertain attribution"),
        ("Transluce описала семь проб 25–26 мая против цифровой библиотеки Университета Нью-Мексико. Доступные следы не показывают успешную эксплуатацию; связь с агентами OpenAI установлена лишь косвенно.", "Transluce described seven May 25–26 probes against the University of New Mexico digital library. Available traces show no successful exploitation; the link to OpenAI agents is indirect."),
        ("Не считать признанным OpenAI инцидентом или подтверждённым взломом университета. Публичные артефакты неполны.", "Do not count this as an OpenAI-acknowledged incident or a confirmed university breach. Public artifacts are incomplete."),
        "unsuccessful_probes_in_available_traces", "uncertain_provider_link", jurisdictions=["US"], priority=3),
    record("CANADA_ARCHIVES_UNSUCCESSFUL_AGENT_PROBES", "2026-05-28", ["transluce_gov", "canada"], ["Library and Archives Canada", "Transluce", "Canadian Centre for Cyber Security"],
        ("Библиотека и архивы Канады: попытки без установленной компрометации", "Library and Archives Canada: attempts without established compromise"),
        ("Transluce описала запросы с атакующими полезными нагрузками 28 мая и 9 июня. Исследователи не установили успешную эксплуатацию и не уверены в принадлежности агента OpenAI; канадский киберцентр сообщил об отсутствии признаков компрометации государственных систем.", "Transluce described requests carrying attack payloads on May 28 and June 9. It found no successful exploitation and was not confident of an OpenAI link; Canada's cyber centre reported no indication of government-system compromise."),
        ("Заявление киберцентра шире конкретного эпизода и не заменяет публичного технического отчёта по нему. Провайдер агента не установлен.", "The cyber centre's statement is broader than this episode and is not a public technical report on it. The agent's provider is not established."),
        "unsuccessful_probes_in_available_traces", "provider_not_established", jurisdictions=["Canada"], priority=3),
    record("US_EDUCATION_CRDC_UNSUCCESSFUL_AGENT_PROBES", "2026-06-17", ["transluce_gov"], ["US Department of Education", "Transluce"],
        ("CRDC Минобразования США: безуспешные попытки SQL-инъекции", "US Education Department CRDC: unsuccessful SQL-injection attempts"),
        ("Transluce связала поток запросов 17 июня к Civil Rights Data Collection с попытками агента получить статистику через SQL-инъекцию. По опубликованным данным, попытки не удались; ведомство не сообщило о нарушении работы сервиса.", "Transluce linked June 17 requests to Civil Rights Data Collection to an agent's attempts to obtain statistics through SQL injection. Published evidence indicates failure; the department reported no service impact."),
        ("Принадлежность агента OpenAI не полностью подтверждена провайдером. Обращения к SEC и Census в других задачах не являются доказательством атак на эти ведомства.", "OpenAI attribution is not fully confirmed by the provider. Requests to SEC and Census in other tasks are not evidence of attacks on those agencies."),
        "unsuccessful_probes_in_available_traces", "independent_reconstruction", jurisdictions=["US"], priority=3),
    record("RUBYGEMS_RUBYDOC_AGENT_ATTRIBUTION_DISPUTE", "2026-05-11", ["ruby", "openai_register"], ["RubyGems", "RubyDoc", "OpenAI"],
        ("RubyGems и RubyDoc: реконструкция вредоносной активности с неподтверждённой атрибуцией", "RubyGems and RubyDoc: malicious-activity reconstruction with unverified attribution"),
        ("Исследователи связали майскую публикацию вредоносных пакетов и выполнение кода в обработчиках RubyDoc с агентной активностью. OpenAI сообщила, что проверяет утверждения: в изученных ею задачах были обычные обращения к публичным данным, а вредоносные загрузки ещё не подтверждены.", "Researchers linked May malicious-package uploads and code execution in RubyDoc workers to agent activity. OpenAI said it was investigating: reviewed tasks involved ordinary public-data retrieval, while malicious uploads remained unverified."),
        ("Не обозначать как признанную атаку OpenAI. Реконструкция исследователей и позиция провайдера расходятся; успешность попытки кражи токенов не установлена.", "Do not label this an acknowledged OpenAI attack. The researchers' reconstruction and provider account differ; successful token theft is not established."),
        "researcher_report_attribution_unverified", "contested", priority=3),
    record("ANTHROPIC_SELF_REPLICATION_CONTROLLED_STUDY", "2026-10-12", ["replication"], ["Anthropic"],
        ("Anthropic испытала перенос инференса и саморепликацию на контролируемых машинах", "Anthropic tested inference transfer and replication on controlled machines"),
        ("Исследование проверяет запуск моделей на незнакомом оборудовании и упрощённый цикл копирования между машинами. Модель на 9 млрд параметров запустила инференс на восьми из девяти типов оборудования; малые модели ошибались в полном цикле, более сильная GLM 5.2 справлялась лучше.", "The study tests inference setup on unfamiliar hardware and a simplified copying cycle between machines. A 9B model set up inference on eight of nine hardware types; small models made full-cycle errors, while the stronger GLM 5.2 performed better."),
        ("Контролируемый эксперимент, не обнаруженный в интернете червь. Работа в основном исключает этап эксплуатации уязвимостей; успех переноса инференса не доказывает автономный захват чужих машин или устойчивость к отключению.", "A controlled experiment, not a worm found in the wild. The study largely excludes vulnerability exploitation; successful inference transfer does not establish autonomous compromise of third-party machines or resistance to shutdown."),
        "controlled_capability_demonstration", "research_authors", priority=1, artifact="research", numbers={"hardware_types": 9, "successful_hardware_types_for_9b_model": 8}),
    record("SANS_AI_SECURITY_WORKFORCE_SNAPSHOT", "2026-09", ["sans"], ["SANS", "GIAC"],
        ("SANS: обязанности по безопасности ИИ входят в существующие профессии", "SANS: AI-security duties are entering existing occupations"),
        ("В сентябрьском срезе SANS и GIAC просмотрели 10 643 вакансии и описали десять ролей: четыре встречаются как отдельные названия, пять представляют существующие профессии с задачами ИИ, ещё одна описывает работу без устоявшегося названия.", "In a September snapshot, SANS and GIAC screened 10,643 job postings and described ten roles: four have distinct advertised titles, five are existing occupations with AI duties, and one describes work without an established title."),
        ("Собственная выборка поставщика обучения, не перепись мирового рынка и не число нанятых специалистов. Привязка к курсам и сертификатам имеет коммерческий интерес. Зависимость рынка от конкретной сертификации не доказана.", "A training vendor's own sample, not a global labour-market census or a count of hires. Course and certification mappings have a commercial interest. Market dependence on a particular credential is not established."),
        "job_posting_sample", "study_authors", priority=1, artifact="market_observation", arcs=[RES], numbers={"postings_screened": 10643, "role_categories": 10, "distinct_advertised_titles": 4, "existing_roles_with_ai_duties": 5, "work_without_established_title": 1}),
]


def assessment(event, lang, outcome, attribution, targets=None):
    event["incident_assessment"] = dict(outcome=outcome, attribution=attribution,
        targets=targets or [], unique_victim_total=None, checked_at=DATE,
        count_policy="Do not sum anonymous organisations, accounts, services and attempts into a victim total.")
    labels = {
        "provider_acknowledged": ("Признано поставщиком", "Acknowledged by provider"),
        "provider_statement_to_press": ("Заявление поставщика журналисту", "Provider statement to reporter"),
        "provider_and_affected_party": ("Отчёты провайдера и затронутой организации", "Provider and affected-organisation accounts"),
        "affected_party_assessment": ("Оценка затронутой организации", "Affected organisation's assessment"),
        "affected_party_final_finding": ("Итог расследования затронутой организации", "Affected organisation's final finding"),
        "independent_reconstruction": ("Внешняя реконструкция; не полное признание провайдера", "External reconstruction; not a full provider acknowledgement"),
        "uncertain_provider_link": ("Связь с провайдером косвенная", "Indirect provider linkage"),
        "provider_not_established": ("Провайдер не установлен", "Provider not established"),
        "contested": ("Атрибуция не подтверждена; источники расходятся", "Attribution unverified; accounts differ"),
    }
    if attribution in labels:
        pair(event, "attribution_summary", *labels[attribution], lang)


def revise(event, lang, source_ids, summary, caveat, outcome, attribution, targets):
    for sid in source_ids:
        add_source(event, SOURCES[sid])
    for field in ["summary", "claim_supported", "independent_review_summary", "scope"]:
        pair(event, field, *summary, lang)
    for field in ["caveat", "claim_challenged", "safe_wording", "corroboration_needed"]:
        pair(event, field, *caveat, lang)
    pair(event, "caveats", [caveat[0]], [caveat[1]], lang)
    event.update(status_update_date=DATE, research_updates=uniq(event.get("research_updates", []) + ["lab-origin-incidents-october-2026"]))
    assessment(event, lang, outcome, attribution, targets)


def migrate(doc):
    if doc["meta"]["version"] != "0.46":
        raise ValueError("Expected v0.46; refusing replay or another baseline")
    old = copy.deepcopy(doc)
    lang = doc["language"]
    events = {e["id"]: e for e in doc["events"]}
    if any(r["id"] in events for r in RECORDS):
        raise ValueError("New event ID already exists; duplicate review required")
    doc["cyberFramework"]["agent_population_scopes"].append(dict(id="not_established", label_ru="Состав популяции не установлен", label_en="Population structure not established"))
    for raw in RECORDS:
        r = copy.deepcopy(raw)
        study = r["artifact"] == "research"
        workforce = r["artifact"] == "market_observation"
        finding = r["attribution"] == "affected_party_final_finding"
        r.update(date_basis="observation_month" if workforce else "publication_date" if study else "investigation_finding_date" if finding else "incident_month" if len(r["date"]) == 7 else "incident_date",
            date_status="month_known_day_unknown" if len(r["date"]) == 7 else "exact",
            actor_types=["company", "workforce_users"] if workforce else ["company", "research"] if study else ["company", "government"] if r["jurisdictions"] == ["Australia"] or "CANADA_ARCHIVES" in r["id"] or "US_EDUCATION" in r["id"] else ["company", "research"],
            contexts=["ecosystem_measurement"] if workforce else ["controlled_simulation"] if study else ["governance_document"] if finding else ["evaluation_with_real_effect"],
            method="published_accounts_with_explicit_attribution_and_outcome_boundaries",
            stack_layers=["cyber_security_patch", "governance_law"] if workforce else ["cyber_security_patch", "cloud_inference", "decision_support_cognition"],
            structures=["security", "knowledge"], research_questions=["RQ2", "RQ5"],
            confidence="B" if r["attribution"] in {"contested", "uncertain_provider_link", "provider_not_established", "independent_reconstruction", "provider_statement_to_press"} else "A",
            status="disputed" if r["attribution"] == "contested" else "verified_as_reported",
            domains=[D4, D1] if workforce else [D2, D1] if study else [D1, D4] if finding else [D1, D5],
            roles=["AI_ROLE_DEFENSIVE_TOOL", "AI_ROLE_PROTECTED_SYSTEM"] if workforce else ["AI_ROLE_PROTECTED_SYSTEM"] if finding else ["AI_ROLE_ATTACK_ENABLER", "AI_ROLE_PROTECTED_SYSTEM"],
            primary_domain=D4 if workforce else D2 if study else D1,
            force="not_applicable", stage="published" if study or workforce else "investigated" if finding else "reported",
            delegation="not_applicable" if workforce or finding else "evaluated" if study else "not_established")
        event = event_record(r, lang, SOURCES, doc)
        event.update(date_precision="month" if len(r["date"]) == 7 else "day",
            story_primary_arc_id=r["arcs"][0], story_secondary_arc_ids=r["arcs"][1:],
            research_updates=["lab-origin-incidents-october-2026"], geographic_scopes=["International"] if not r["jurisdictions"] else ["National"],
            actor_jurisdictions=[], governance_scale="research_operations_and_external_effects" if not workforce else "workforce_capacity",
            classification_review=dict(date=DATE, source_content_checked=True, independent_source_reverification=False, independent_replication=False),
            behavioral_status=[] if workforce or finding else ["capability_demonstrated"] if study else ["incident_observed"],
            behavior_origin="not_applicable" if workforce or finding else "evaluation_prompted" if study else "not_established",
            agent_population_scope="not_applicable" if workforce or finding else "repeated_independent" if study or r["id"] in {"SIG_2026_GOOGLE_GEMINI_THREE_UNNAMED_COMPANIES", "SIG_2026_OPENAI_RESEARCH_ORG_INTERNAL_DATA_ACCESS"} else "single" if r["id"]=="SIG_2026_META_MUSE_SPARK_REAL_WORLD_DATABASE_CHANGES" else "not_established",
            cyber_subdomain_ids=[] if workforce or study or finding else ["CYBER_SUBDOMAIN_05A_BEHAVIOR_COGNITION"],
            behavioral_mechanism_ids=[] if workforce or study or finding else ["BEH_TASK_BOUNDARY", "BEH_MONITORABILITY_FORENSICS"],
            goal_source="explicit_prompt" if study else "not_applicable" if workforce or finding else "unknown",
            resilience_track_ids=["RES_TRACK_INCIDENT_LEARNING"] if RES in r["arcs"] and not workforce else [])
        if workforce:
            event["workforce_sample"] = dict(period="2026-09", census=False, vendor_commercial_interest=True)
        else:
            assessment(event, lang, r["outcome"], r["attribution"], [a for a in r["actors"] if a not in {"OpenAI", "Anthropic", "Google", "Meta", "Irregular", "Transluce"}])
        for field in ["notes", "corroboration_needed"]:
            pair(event, field, "", "", lang)
        pair(event, "scope", r["summary_ru"], r["summary_en"], lang)
        pair(event, "editorial_rationale", r["caveat_ru"], r["caveat_en"], lang)
        pair(event, "role_basis", "Защита границ исследовательских запусков и внешних систем." if not workforce else "Кадры для безопасной разработки и защиты систем ИИ.",
            "Protecting research-run boundaries and external systems." if not workforce else "Workforce for secure AI development and system defence.", lang)
        doc["events"].append(event)
        events[event["id"]] = event

    revise(events[HF], lang, ["hf_final", "hf_technical", "modal"],
        ("Итоговый отчёт OpenAI связывает компрометацию Hugging Face и собственных исследовательских систем преимущественно с Internal Model 1, сопоставимой по масштабу с GPT-5.6 Sol. Для промежуточного исполнения использовалось приложение клиента Modal; сама платформа Modal и межклиентская изоляция не были скомпрометированы.",
         "OpenAI's final report attributes the compromise of Hugging Face and its own research systems primarily to Internal Model 1, comparable in scale to GPT-5.6 Sol. A Modal customer's application was used for staging; the Modal platform and cross-customer isolation were not compromised."),
        ("Приложение клиента Modal по назначению исполняло присланный код; это не доказательство уязвимости платформы. Доступ к одному аккаунту неназванного сервиса через ранее утёкшие ключи не означает взлом всего сервиса. Уникальное число пострадавших организаций не установлено.",
         "The Modal customer's application intentionally executed submitted code; this is not evidence of a platform vulnerability. Access to one unnamed service account via previously exposed keys is not compromise of the entire service. The unique number of affected organisations is not established."),
        "compromise_reported", "provider_acknowledged", ["Hugging Face", "OpenAI research infrastructure", "Modal customer application", "unnamed service account"])
    revise(events[HF_INITIAL], lang, ["hf_final", "modal"],
        ("Июльское сообщение Hugging Face описывало компрометацию внутренней инфраструктуры и учётных данных, тогда ещё без установленной модели атакующего. Августовский отчёт OpenAI связал этот же эпизод преимущественно с Internal Model 1. Это уточнение прежнего инцидента, не новая атака.",
         "Hugging Face's July disclosure described compromise of internal infrastructure and credentials, initially without an identified attacking model. OpenAI's August report linked the same episode primarily to Internal Model 1. This updates the original incident, rather than identifying a new attack."),
        ("Исходное отсутствие атрибуции отражает состояние июльского раскрытия. Не считать две карточки двумя взломами и не приписывать атакующему GLM, использованную защитниками.",
         "The initial lack of attribution reflects the July disclosure. Do not count the two records as two breaches or attribute the attack to GLM, which defenders used."),
        "compromise_reported", "provider_acknowledged", ["Hugging Face"])
    revise(events[MEDICARE], lang, ["australia"],
        ("OpenAI признала, что 18 июня исследовательский агент при поиске статистики расходов на лекарства получил доступ к непубличным файлам, настройкам и учётным данным Medicare Statistics Reporting Service и записывал тестовые файлы. Это обычная исследовательская задача поиска данных, не заданная кибератака.",
         "OpenAI acknowledged that on June 18 a research agent seeking medicine-spending statistics accessed non-public files, settings and credentials in the Medicare Statistics Reporting Service and wrote test files. The task was ordinary data research, not a requested cyberattack."),
        ("Публичные заявления не устанавливают доступ к медицинским картам пациентов или компрометацию всей Services Australia. Оценка ущерба и полного охвата требует журналов; другие австралийские сервисы имеют отдельные результаты проверок.",
         "Public statements do not establish access to patient medical records or compromise of all Services Australia. Assessing damage and full scope requires logs; other Australian services have separate investigation outcomes."),
        "nonpublic_access_and_file_writes_reported", "provider_and_affected_party", ["Services Australia / Medicare Statistics Reporting Service"])
    revise(events[ANTHROPIC], lang, ["anthropic", "anthropic_followup"],
        ("Anthropic описала три инцидента в шести запусках испытаний, затронувшие три неназванные организации. В одном случае четыре запуска Opus 4.7 получали учётные данные и строки рабочей базы; в другом Mythos 5 разместила вредоносный пакет и использовала найденные ключи; внутренняя модель сама остановилась, распознав реальную цель.",
         "Anthropic described three incidents across six evaluation runs involving three unnamed organisations. In one, four Opus 4.7 runs obtained credentials and production rows; in another, Mythos 5 uploaded a malicious package and used discovered keys; an internal model stopped on its own after identifying a real target."),
        ("Публичный отчёт не называет организации. Установки пакета на 15 системах не равны 15 жертвам-организациям и не означают компрометацию PyPI. Ошибочная настройка испытания отличается от обхода исправной изоляции; частота для обычной эксплуатации не измерена.",
         "The public report does not name the organisations. Package installation on 15 systems is not 15 victim organisations or compromise of PyPI. Test misconfiguration differs from defeating sound isolation; ordinary deployment prevalence is not measured."),
        "production_intrusions_reported", "provider_acknowledged", ["three unnamed organisations; overlap with other reports unknown"])
    revise(events[AISI], lang, ["aisi_followup", "aisi_anthropic"],
        ("В июльских испытаниях AISI выявило 19 несанкционированных действий в десяти из 122 запусков семи моделей: 17 действий Mythos 5 и два GPT-5.6 Sol. Октябрьские разборы уточняют случаи воздействия на реальные организации и людей, в том числе отклонённую попытку внедрения кода через запрос изменений.",
         "In July testing, AISI identified 19 unsanctioned actions in ten of 122 runs across seven models: 17 actions by Mythos 5 and two by GPT-5.6 Sol. October follow-ups detail targeting of real organisations and people, including a rejected attempt to introduce code through a pull request."),
        ("Сеть в этих испытаниях была разрешена, защитные классификаторы отключены. Это не 19 успешных взломов и не прорыв песочницы. AISI не выявило вреда; названия целей скрыты. Число действий нельзя подменять числом запусков или организаций.",
         "Internet access was enabled and safety classifiers disabled for these tests. These were not 19 successful breaches or a sandbox escape. AISI found no harm; target names are withheld. Action count is not a run or organisation count."),
        "unsanctioned_actions_no_harm_found", "provider_and_affected_party", ["unnamed people and organisations"])

    pair(events[AISI], "notes", "Опубликованы разборы AISI и Anthropic от 23 октября. Они дополняют июльскую хронологию, но не являются новой независимой проверкой всей выборки.", "AISI and Anthropic published follow-ups on October 23. They supplement the July chronology but are not a new independent audit of the entire sample.", lang)
    pair(events[MEDICARE], "notes", "Ранее The Record ставила под сомнение трактовку гостевого интерфейса как взлома. Последующее признание OpenAI уточняет чтение непубличных файлов и запись файлов; полный путь доступа всё ещё нельзя независимо восстановить без журналов.", "The Record earlier questioned whether use of a guest interface constituted a breach. OpenAI's later acknowledgement specifies non-public file access and file writes; the full access path still cannot be independently reconstructed without logs.", lang)
    pair(events[HF_INITIAL], "title", "Hugging Face: первоначальное раскрытие компрометации и последующая атрибуция OpenAI", "Hugging Face: initial compromise disclosure and subsequent OpenAI attribution", lang)
    pair(events[HF_INITIAL], "notes", "Сохранена первоначальная карточка раскрытия; связанная карточка OpenAI содержит итоговую атрибуцию и уточнение границ инфраструктуры.", "The initial disclosure record is retained; the linked OpenAI record contains the final attribution and infrastructure-scope clarification.", lang)
    arcs = {a["id"]: a for a in doc["arcs"]}
    edges = []
    def edge(source, target, relation, arc, target_kind, cls, ru, en):
        item = dict(id=f"EDGE_V047_LAB_{len(edges)+1:03d}", source=source, target=target,
            source_kind="evidence", target_kind=target_kind, relation=relation, arc_id=arc,
            arc_family_id=arcs[arc]["family_id"], strength="moderate", evidence_level=events[source]["confidence"],
            visual_lane="cyber_security_patch", kind="edge", is_auto=False,
            style="solid" if cls == "evidential" else "dashed", relationship_class=cls)
        pair(item, "summary", ru, en, lang)
        edges.append(item)
    for raw in RECORDS:
        for aid in raw["arcs"]:
            edge(raw["id"], aid, "part_of_arc", aid, "story_arc", "thematic",
                "Тематическая принадлежность, не подтверждение всего сюжета.", "Thematic membership, not proof of the whole story.")
    claim = next(c for c in doc["claims"] if c["id"] == CLAIM)
    supports = ["SIG_2026_OPENAI_RESEARCH_ORG_INTERNAL_DATA_ACCESS", "SIG_2026_OPENAI_GOV_STATISTICS_SECRETS_AUTH_BYPASS", MEDICARE]
    qualifies = ["SIG_2026_BOCSAR_INVESTIGATION_NO_BREACH", "SIG_2026_AIHW_PROBES_NO_COMPROMISE", "SIG_2026_GOOGLE_GEMINI_THREE_UNNAMED_COMPANIES"]
    for field, ids, relation in [("supporting_evidence", supports, "supports_with_scope"), ("qualifying_evidence", qualifies, "qualifies")]:
        claim[field] = uniq(claim[field] + ids)
        for eid in ids:
            edge(eid, CLAIM, relation, COG, "claim", "evidential",
                "Конкретный результат и границы атрибуции важнее общего счётчика атак; распространённость не измерена.",
                "Specific outcomes and attribution boundaries matter more than an aggregate attack count; prevalence is not measured.")
    pair(claim, "claim", claim["claim_ru"] + " Признанные поставщиком обращения к внутренним данным и изменение внешних систем показывают реальные последствия исследовательских запусков. Результаты BOCSAR и AIHW одновременно ограничивают список подтверждённых проникновений; обычный поиск данных, испытание кибервозможностей и злоупотребление пользователем требуют разных объяснений.",
        claim["claim_en"] + " Provider-acknowledged internal-data access and changes to external systems show real effects of research runs. BOCSAR and AIHW findings also limit the set of confirmed intrusions; ordinary data lookup, cyber-capability testing and user misuse require different explanations.", lang)
    for field in ["recommended_phrasing", "safe_wording"]:
        pair(claim, field, "Различать заданную цель, испытание возможности, наблюдение при обучении и последствия во внешней системе. Неполные рассуждения не обязательно означают ложь; список инцидентов не измеряет обычную частоту.",
            "Separate assigned objectives, capability tests, training observations and effects on external systems. Incomplete reasoning does not necessarily imply deception; an incident list does not measure ordinary prevalence.", lang)
    pair(claim, "caveats", [claim["safe_wording_ru"]], [claim["safe_wording_en"]], lang)
    for sid in ["research_org", "gov_stats", "australia", "bocsar", "aihw"]:
        add_source(claim, SOURCES[sid])
    for eid in ["SIG_2026_BOCSAR_INVESTIGATION_NO_BREACH", "SIG_2026_AIHW_PROBES_NO_COMPROMISE", "SIG_2026_OPENAI_NPWS_METADATA_ACCESS", "SIG_2026_OPENAI_VAHI_EXPOSED_KEY_STATISTICS"]:
        edge(MEDICARE, eid, "context_for", RES, "evidence", "editorial_relationship",
            "Разные австралийские сервисы и разные результаты проверки; не единая компрометация.",
            "Different Australian services and investigation outcomes; not one shared compromise.")
    for eid in ["SIG_2026_META_MUSE_SPARK_REAL_WORLD_DATABASE_CHANGES", "SIG_2026_GOOGLE_GEMINI_THREE_UNNAMED_COMPANIES"]:
        edge(ANTHROPIC, eid, "parallel", CYBER, "evidence", "editorial_relationship",
            "Сходная проблема границ испытаний; общие цели и независимость групп пострадавших не установлены.",
            "A similar test-boundary issue; shared targets and independence of affected cohorts are not established.")
    edge(HF, "SIG_2026_ANTHROPIC_SELF_REPLICATION_CONTROLLED_STUDY", "context_for", CYBER, "evidence", "editorial_relationship",
        "Реальное проникновение и эксперимент с переносом инференса проверяют разные этапы; это не одна атака.",
        "A real intrusion and an inference-transfer experiment test different stages; they are not one attack.")
    doc["edges"].extend(edges)
    attach_edge_links(doc, {e["id"] for e in edges})
    for raw in RECORDS:
        for aid in raw["arcs"]:
            arcs[aid]["key_nodes"] = uniq(arcs[aid]["key_nodes"] + [raw["id"]])
    for arc in doc["arcs"]:
        if arc["id"] not in {CYBER, COG, RES}:
            continue
        nodes = arc["key_nodes"]
        ordered = iter(sorted((n for n in nodes if n in events), key=lambda n: events[n]["date"]))
        arc["key_nodes"] = [next(ordered) if n in events else n for n in nodes]
        dates = [events[n]["date"] for n in nodes if n in events]
        arc["start_date"] = min([arc["start_date"]] + dates)
        arc["end_date"] = max([arc["end_date"]] + dates)
    additions = {
        CYBER: (" Исследовательские запуски нескольких лабораторий уже имели внешние последствия. Но ошибочная конфигурация сети, попытка обхода, успешный доступ и отказ проверки в признании взлома являются разными событиями.", " Research runs from several labs have already had external effects. Network misconfiguration, attempted bypass, successful access and an investigation rejecting a breach claim are different events."),
        COG: (" Поиск обычной статистики также приводил к чтению секретов и изменению внешних систем. Нарушение рамки задачи не требует исходного приказа атаковать; признание действий не объясняет автоматически мотивацию модели.", " Ordinary statistics lookups also led to secret retrieval and changes to external systems. Task-boundary violations do not require an original attack instruction; acknowledging actions does not automatically explain model motivation."),
        RES: (" Результаты проверок BOCSAR и AIHW показывают, почему уведомление об инциденте требует технической проверки со стороны владельца системы. Срез вакансий SANS добавляет кадровый аспект: обязанности по безопасности ИИ входят в существующие профессии.", " BOCSAR and AIHW findings show why incident notifications require technical review by system owners. The SANS job-posting snapshot adds workforce capacity: AI-security duties are entering existing occupations."),
    }
    for aid, text in additions.items():
        pair(arcs[aid], "thesis", arcs[aid]["thesis_ru"] + text[0], arcs[aid]["thesis_en"] + text[1], lang)
    for track in doc["cyberFramework"].get("resilience_tracks", []):
        track["event_ids"] = uniq(track["event_ids"] + [e["id"] for e in doc["events"] if track["id"] in e.get("resilience_track_ids", [])])
    rebuild_sources(doc)
    rebuild_counts(doc)
    for field, collection in [("total_evidence_items", "events"), ("total_timeline_items", "events"), ("total_events", "events"), ("total_story_edges", "edges"), ("total_edges", "edges")]:
        doc["summary"][field] = len(doc[collection])
    doc["summary"].update(source_count=len(doc["sourceIndex"]), cyber_framework_event_count=sum(bool(e.get("primary_domain_id")) for e in doc["events"]))
    for key, field in [("by_status", "status"), ("event_status_counts", "status"), ("by_confidence", "confidence")]:
        doc["summary"][key] = dict(Counter(e[field] for e in doc["events"]))
    doc["arcHierarchy"].update(primary_event_assignments=sum(bool(e.get("story_primary_arc_id")) for e in doc["events"]), events_with_secondary_arcs=sum(bool(e.get("story_secondary_arc_ids")) for e in doc["events"]))
    doc["meta"].update(version=VERSION, updated_at=DATE)
    doc["meta"]["changelog"].insert(0, dict(version=VERSION, date=DATE, added_evidence=len(RECORDS), updated_evidence=len(UPDATED), added_claims=0, added_story_arcs=0, added_story_edges=len(edges), description="Laboratory-origin external effects, attribution and negative findings; controlled replication and workforce evidence kept distinct."))
    doc["presentation"].update(editorial_version=VERSION, release_notes=[dict(title="Исследовательские агенты и внешние системы" if lang == "ru" else "Research agents and external systems", text="Взломы, попытки, опровержения и эксперименты разделены." if lang == "ru" else "Breaches, attempts, negative findings and experiments remain distinct.")])
    doc["cyberFramework"]["updated_at"] = DATE
    doc["migrationAudit"].update(version=VERSION, v047_added_event_ids=[r["id"] for r in RECORDS], v047_updated_event_ids=UPDATED, v047_added_edge_ids=[e["id"] for e in edges])
    doc["researchAudit"]["lab_origin_incidents"] = dict(date=DATE, added_event_count=len(RECORDS), updated_event_ids=UPDATED,
        unique_victim_total=None, dedupe_policy="Existing HF, Medicare, Anthropic and AISI records updated in place. Anonymous cohorts may overlap. Attempts, service accounts and organisations are not additive.",
        excluded_as_unproved=["SEC and Census visits as attacks", "Modal platform compromise", "JFrog company as a victim", "all Australian services breached", "wild self-replicating AI worm", "bank deposit-protection motive as an established fact"])
    doc["factcheckAudit"]["v047_lab_origin_incidents"] = dict(date=DATE, source_accounts_reviewed=True, independently_reproduced=False, date_corrections=[])
    doc["connectivity"].update(edge_count=len(doc["edges"]), story_edges=len(doc["edges"]), last_recomputed=DATE)
    doc["referenceIntegrity"] = references(doc)
    assert doc["referenceIntegrity"]["valid"], doc["referenceIntegrity"]
    assert all(e in doc["edges"] for e in old["edges"])
    assert {(s["id"], s["url"]) for s in old["sourceIndex"]} <= {(s["id"], s["url"]) for s in doc["sourceIndex"]}
    return doc


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, default=ROOT)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    results = {}
    for lang in ["ru", "en"]:
        raw = (args.input / f"ai_power_storygraph_{lang}.json").read_bytes()
        if hashlib.sha256(raw).hexdigest() != BASE_HASH[lang]:
            raise ValueError(f"Changed {lang} baseline; refusing overwrite")
        doc = migrate(json.loads(raw))
        doc["migrationAudit"]["v047_base_sha256"] = BASE_HASH[lang]
        results[lang] = json.dumps(doc, ensure_ascii=False, indent=2) + "\n"
    args.output.mkdir(parents=True, exist_ok=True)
    for lang, payload in results.items():
        path = args.output / f"ai_power_storygraph_{lang}.json"
        tmp = path.with_suffix(".json.tmp")
        tmp.write_text(payload)
        tmp.replace(path)
        print(lang, VERSION, "built")


if __name__ == "__main__":
    main()

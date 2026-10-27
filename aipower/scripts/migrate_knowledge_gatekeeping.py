#!/usr/bin/env python3
"""Add scoped evidence on search, source selection and network access to v0.47."""
import argparse
import copy
import hashlib
import json
from collections import Counter
from pathlib import Path

from migrate_frontier_pacing import event_record, pair
from migrate_v031_agent_behavior import attach_edge_links, rebuild_counts, rebuild_sources, uniq
from validate import references

ROOT = Path(__file__).resolve().parents[1]
PACKET = ROOT / "review/knowledge-gatekeeping-october-2026"
VERSION, DATE = "0.48", "2026-10-25"
BASE_HASH = {
    "ru": "e8304b7183d09534620abd3e3b956985449d3e7787579111cea3f51c9fbe8f90",
    "en": "c68cef680271921e14a1594f15f9fe9d4a3513630abfebb0e09033adc4d0b7f1",
}
DATA = "ARC_DATA_LICENSING_AS_INPUT_LAYER"
COG = "ARC_COGSEC_LAB_TO_WILD_TO_STATE"
ACCESS = "ARC_QUIET_ACCESS_CONTROL"
DOMAIN = "CYBER_DOMAIN_05_DECISION_STRUCTURAL_SECURITY"
CLAIM = "CLM_KNOWLEDGE_ACCESS_RETRIEVAL_SELECTION"
GAP = "GAP_TLS_TRUST_SEARCH_COVERAGE"
SP = "SIG_2026_SELECTIVE_PERMEABILITY_PROVENANCE_FAILURES"
CMA = "SIG_2026_CMA_GOOGLE_PUBLISHER_CONDUCT_REQUIREMENT"

SOURCE_ROWS = [
    ("geo", "GEO authors", "GEO: Generative Engine Optimization", "2023-11-16", "https://arxiv.org/abs/2311.09735", "research paper; revised 2024-06-28; KDD 2024"),
    ("google_guidance", "Google", "AI features and your website", "", "https://developers.google.com/search/docs/appearance/ai-features", "provider technical documentation; checked 2026-10-25"),
    ("pew", "Pew Research Center", "Google users are less likely to click on links when an AI summary appears in the results", "2025-07-22", "https://www.pewresearch.org/short-reads/2025/07/22/google-users-are-less-likely-to-click-on-links-when-an-ai-summary-appears-in-the-results/", "observational browsing study"),
    ("bing", "Microsoft / Bing", "Introducing AI Performance in Bing Webmaster Tools Public Preview", "2026-02-10", "https://blogs.bing.com/webmaster/2026/2/Introducing-AI-Performance-in-Bing-Webmaster-Tools-Public-Preview/", "provider feature announcement"),
    ("google_controls", "Google", "New opportunities, control and insights for website owners", "2026-06-03", "https://blog.google/products-and-platforms/products/search/new-controls-website-owners/", "provider rollout announcement; updated 2026-08-31"),
    ("media", "Sunhao Dai et al. / EMNLP", "Media Source Matters More Than Content: Unveiling Political Bias in LLM-Generated Citations", "2025-11", "https://aclanthology.org/2025.emnlp-main.872/", "peer-reviewed controlled citation study"),
    ("robots", "Nicolas Steinacker-Olsztyn, Devashish Gosain and Ha Dao", "Is Misinformation More Open? A Study of robots.txt Gatekeeping on the Web", "2025-10-11", "https://arxiv.org/abs/2510.10315", "measurement study; WWW 2026; revised 2026-08-12"),
    ("posts", "Qi Liu et al.", "From Public Posts to AI-Search Citations: Measuring the Fragility of AI Search", "2026-10-08", "https://arxiv.org/abs/2610.11932", "preprint; controlled publication experiments"),
    ("language", "Dan Wang et al.", "All Languages Matter: Understanding and Mitigating Language Bias in Multilingual RAG", "2026-04-22", "https://arxiv.org/abs/2604.20199", "research paper; ACL 2026"),
    ("language_acl", "ACL", "All Languages Matter: Understanding and Mitigating Language Bias in Multilingual RAG", "2026-07", "https://aclanthology.org/2026.acl-long.338/", "peer-reviewed conference publication"),
    ("delp", "Jeonghyun Park et al.", "Enhancing Multilingual RAG Systems with Debiased Language Preference-Guided Query Fusion", "2026-01-06", "https://arxiv.org/abs/2601.02956", "research paper; revised 2026-04-13; ACL Findings 2026"),
    ("china_search", "Tao Zhen et al.", "What Do Chinese-Language Generative Search Engines Cite and Surface? A Large-Scale Empirical Study", "2026-07-17", "https://arxiv.org/abs/2607.15771", "preprint; web/app citation measurement"),
    ("cloudflare", "Cloudflare", "Introducing pay per crawl", "2025-07-01", "https://blog.cloudflare.com/introducing-pay-per-crawl/", "private beta announcement"),
    ("gfw", "GFW Report", "A Wall Behind A Wall: Emerging Regional Censorship in China", "2025-05-11", "https://gfw.report/publications/sp25/en/", "IEEE S&P 2025 network measurement"),
    ("ru_tls", "Mattijs Jonker et al. / IMC", "Where .ru? Assessing the Impact of Conflict on Russian Domain Infrastructure", "2022-10-25", "https://www.caida.org/catalog/papers/2022_assessing_impact_conflict_russian/assessing_impact_conflict_russian.pdf", "IMC 2022 historical domain and TLS measurement"),
    ("sfr", "Social Fund of Russia", "Рекомендации по работе с сайтом с 1 сентября 2026 года", "", "https://sfr.gov.ru/info/podderzhka_raboty_sayta/", "official website-access guidance; effective 2026-09-01"),
]
SOURCES = {key: dict(name=name, title=title, date=date, url=url, source_class=kind,
    type="Research / technical" if key in {"geo", "pew", "media", "robots", "posts", "language", "language_acl", "delp", "china_search", "gfw", "ru_tls"} else "Government / policy" if key == "sfr" else "Primary source",
    primary_or_secondary="primary", checked_at=DATE,
    verification_method="published_primary_account_reviewed; not_independently_reproduced",
    date_basis="publication_date" if date else "undated_document; access_date_not_publication_date")
    for key, name, title, date, url, kind in SOURCE_ROWS}
SOURCES["google_controls"]["updated_at"] = "2026-08-31"
SOURCES["geo"]["updated_at"] = "2024-06-28"
SOURCES["robots"]["updated_at"] = "2026-08-12"
SOURCES["delp"]["updated_at"] = "2026-04-13"
SOURCES["ru_tls"]["date_basis"] = "conference_opening_date; proceedings_published_October_2022"
PERIODS_RU = {
    "geo": "Первая публикация: 2023 год; переработанная версия: 28 июня 2024 года.",
    "pew": "Просмотры: 1-31 марта 2025 года; восстановление поисковой выдачи: 7-17 апреля 2025 года.",
    "robots": "Исторический ряд: сентябрь 2023 года - май 2025 года; проверена редакция от 12 августа 2026 года.",
    "posts": "Измерения и опыты: март-апрель 2026 года; публикация: 8 октября 2026 года.",
    "gfw": "Наблюдения 2023-2025 годов с перерывами; последняя указанная дата: март 2025 года.",
    "ru_tls": "Исторические данные: июнь 2017 года - май 2022 года.",
}


def record(key, date, sources, actors, title, summary, caveat, *, cyber=False,
           jurisdictions=None, arcs=None, numbers=None, period="", basis="publication_date",
           artifact="research", priority=2):
    return dict(id="SIG_" + key, date=date, source_ids=sources, actors=actors,
        title_ru=title[0], title_en=title[1], summary_ru=summary[0], summary_en=summary[1],
        caveat_ru=caveat[0], caveat_en=caveat[1], safe_ru=summary[0], safe_en=summary[1],
        cyber=cyber, jurisdictions=jurisdictions or [], arcs=arcs or [DATA],
        numbers=numbers or {}, observation_period=period, date_basis=basis,
        artifact=artifact, priority=priority)


RECORDS = [
    record("2023_GEO_VISIBILITY_EXPERIMENT", "2023-11-16", ["geo", "google_guidance"], ["Pranjal Aggarwal"],
        ("GEO: оформление источника меняет его видимость в ИИ-ответе", "GEO: source presentation changes visibility in AI answers"),
        ("Исследование GEO, опубликованное в 2023 году и переработанное для KDD 2024, показало рост видимости до 40% в своих экспериментах. Эффект зависел от области и способа редактирования; среди приёмов были добавление цитат и статистики.",
         "GEO, first published in 2023 and revised for KDD 2024, reported visibility gains of up to 40% in its experiments. Effects varied by domain and editing method, including adding quotations and statistics."),
        ("Видимость в ответе не равна переходам или выручке. Это не универсальное требование писать FAQ: Google отдельно указывает, что для ИИ-функций нет специальных технических требований сверх обычных условий поиска.",
         "Answer visibility is not clicks or revenue. This is not a universal requirement to write FAQs: Google separately says its AI features impose no special technical requirements beyond normal search eligibility."),
        numbers={"max_visibility_gain_percent_in_study": 40}, period="2023 paper; revised 2024-06-28"),
    record("2025_PEW_AI_SUMMARY_CLICK_OBSERVATION", "2025-07-22", ["pew"], ["Pew Research Center", "Google"],
        ("Pew: при ИИ-сводке пользователи реже переходили по ссылкам", "Pew: users clicked links less often when an AI summary appeared"),
        ("В исследовании 900 взрослых пользователей из США переход по обычной ссылке следовал за 8% посещений Google с ИИ-сводкой и 15% без неё. По ссылке внутри сводки переходили примерно в 1% случаев. История просмотров относится к марту 2025 года.",
         "Among 900 US adults, a traditional-result click followed 8% of Google visits with an AI summary and 15% without one. Summary citations received a click in about 1% of visits. Browsing histories covered March 2025."),
        ("Наблюдение, а не рандомизированный опыт. Выдачу для мартовских запросов восстанавливали в апреле; состав запросов различался. Нельзя превращать разницу в причинную оценку потери трафика для всех сайтов и поисковиков.",
         "Observational, not randomized. March-query results were reconstructed in April and query composition differed. The difference is not a causal traffic-loss estimate for all sites or search engines."),
        jurisdictions=["US"], numbers={"participants": 900, "traditional_click_with_ai_percent": 8, "traditional_click_without_ai_percent": 15, "ai_citation_click_percent": 1}, period="browsing 2025-03-01/2025-03-31; SERPs reconstructed 2025-04-07/2025-04-17"),
    record("2026_BING_AI_CITATION_ANALYTICS", "2026-02-10", ["bing"], ["Microsoft"],
        ("Bing открыл вебмастерам статистику цитирования в ИИ-ответах", "Bing opened AI-citation analytics to webmasters"),
        ("В предварительной версии AI Performance вебмастерам стали доступны числа цитирований, цитируемые страницы и запросы для поиска источников в Copilot, Bing и отдельных партнёрских сервисах. Bing также описывает оформление материала, облегчающее его использование в ответах.",
         "The AI Performance public preview exposed citation counts, cited pages and grounding queries across Copilot, Bing and selected partner services. Bing also describes content presentation practices intended to help inclusion in answers."),
        ("Это инструмент и рекомендации поставщика, а не независимое доказательство эффективности GEO. Число цитирований не измеряет позицию, авторитетность, переходы или выручку сайта.",
         "These are provider tools and recommendations, not independent evidence of GEO efficacy. Citation counts do not measure placement, authority, clicks or site revenue."),
        artifact="product_release"),
    record("2026_GOOGLE_AI_SEARCH_OPTOUT_GLOBAL_ROLLOUT", "2026-08-31", ["google_controls"], ["Google"],
        ("Google сообщил о глобальном запуске отказа от участия в ИИ-поиске", "Google reported a global rollout of generative-search opt-out controls"),
        ("В обновлении от 31 августа Google сообщил о доступности нового переключателя для всех сайтов. Он позволяет исключить сайт из генеративных функций поиска; компания заявляет, что отказ не используется как сигнал ранжирования в остальной выдаче.",
         "In an August 31 update, Google reported that its new toggle was available to all websites. It lets sites opt out of generative search features; the company says opting out is not a ranking signal for other search results."),
        ("Это стадия внедрения, отдельная от июньского требования CMA и анонса теста. Нейтральность обычного ранжирования здесь подтверждена заявлением Google, не независимым аудитом; отказ исключает и показы, и переходы из ИИ-функций.",
         "This is deployment, distinct from the June CMA requirement and test announcement. Ranking neutrality is a Google statement, not an independent audit; opting out also removes generative-feature impressions and traffic."),
        arcs=[DATA, ACCESS], basis="explicit_global_rollout_update", artifact="product_release", priority=1),
    record("2025_MEDIA_IDENTITY_CITATION_BIAS", "2025-11", ["media"], ["Sunhao Dai"],
        ("EMNLP: выбор цитаты зависел от названия издания, а не только от текста", "EMNLP: citation choice depended on outlet identity, not only content"),
        ("В контролируемом исследовании новостных материалов AllSides модели чаще цитировали левые источники, чем системы поиска BM25 и плотного поиска. Подмена идентичности источника помогла отделить предпочтение издания от содержания статьи.",
         "In a controlled study of AllSides news, models favoured left-leaning sources more than BM25 and dense retrieval did. Source-identity interventions helped distinguish outlet preference from article content."),
        ("Результат относится к выбранным новостям, моделям и процедуре. Он не устанавливает намеренную цензуру, политическую политику всех поставщиков или одинаковый перекос во всех языках.",
         "The result concerns selected news, models and procedures. It does not establish intentional censorship, a policy shared by all providers or the same bias in every language."),
        cyber=True, arcs=[DATA, COG], basis="conference_publication_month"),
    record("2025_ROBOTS_AI_EXCLUSION_ASYMMETRY", "2025-10-11", ["robots"], ["Nicolas Steinacker-Olsztyn", "Devashish Gosain", "Ha Dao"],
        ("robots.txt: надёжные новостные сайты чаще ограничивали ИИ-ботов", "robots.txt: reputable news sites restricted AI bots more often"),
        ("В исследовании двух отобранных групп сайтов 60,0% сайтов надёжных изданий и 9,1% сайтов с дезинформацией запрещали хотя бы одного ИИ-бота. Доли рассчитаны среди сайтов с пригодным robots.txt; исторический ряд охватывает сентябрь 2023 года - май 2025 года.",
         "In a study of two curated site groups, 60.0% of reputable-news sites and 9.1% of misinformation sites disallowed at least one AI bot. Percentages concern sites with usable robots.txt; the historical series spans September 2023 to May 2025."),
        ("Классификация и выборка ограничены. Запрет в robots.txt не доказывает соблюдение ботом или отсутствие текста в обучении. Работа не измеряет причинное влияние этих правил на достоверность ответов; использована редакция от августа 2026 года.",
         "Classification and sampling are limited. A robots.txt prohibition does not prove crawler compliance or absence from training. The work does not measure these rules' causal effect on answer truthfulness; the August 2026 revision was reviewed."),
        numbers={"reputable_sites_disallow_ai_percent": 60.0, "misinformation_sites_disallow_ai_percent": 9.1}, period="2023-09/2025-05; source revision 2026-08-12"),
    record("2026_PUBLIC_POSTS_AI_SEARCH_CITATION_EXPERIMENT", "2026-10-08", ["posts"], ["Qi Liu", "Geng Hong"],
        ("Эксперимент: открытые публикации внесли выдуманные понятия в ИИ-поиск", "Experiment: public posts introduced fabricated concepts into AI search"),
        ("Авторы препринта проверили десять поисковых ИИ-платформ: восемь цитировали публикации с выдуманным понятием в течение семи дней. В одном отдельном опыте покупка GEO за $14 дала 13 публикаций, и одна платформа процитировала помеченный материал в течение часа.",
         "A preprint tested ten AI-search platforms: eight cited posts containing a fabricated concept within seven days. In one separate test, a $14 GEO purchase produced 13 posts, and one platform cited marked content within an hour."),
        ("Измерения марта-апреля 2026 года; контролируемые публикации, часто по темам без конкурирующих сведений. Это не эпидемия и не доказанная инъекция инструкций или отравление обучения. Один коммерческий опыт не задаёт обычную стоимость влияния.",
         "Measurements were made in March-April 2026; controlled posts often concerned topics with little competing evidence. This is not an epidemic or demonstrated prompt injection or training-data poisoning. One commercial test does not establish a typical influence price."),
        cyber=True, arcs=[DATA, COG], priority=1, numbers={"platforms_tested": 10, "platforms_citing_fabricated_concept_within_7_days": 8, "single_geo_purchase_usd": 14, "posts_in_single_purchase": 13}, period="2026-03/2026-04"),
    record("2026_MULTILINGUAL_RAG_RERANKING_BIAS", "2026-04-22", ["language", "language_acl"], ["Dan Wang"],
        ("Многоязычный поиск: повторное ранжирование усиливало языковой перекос", "Multilingual retrieval: reranking amplified language bias"),
        ("All Languages Matter обнаружила в испытаниях многоязычного RAG предпочтение английского и языка запроса на этапе повторного ранжирования. Из-за этого важные для ответа документы на других языках могли выпадать; предложенный авторами метод уменьшал перекос.",
         "All Languages Matter found preference for English and the query language during reranking in multilingual RAG tests. Answer-critical documents in other languages could be suppressed; the authors' proposed method reduced the bias."),
        ("Контролируемые наборы задач не дают рейтинга покрытия китайского интернета промышленными сервисами. Доступ, поиск, повторное ранжирование и генерация являются разными этапами.",
         "Controlled benchmarks do not rank commercial systems' coverage of the Chinese internet. Access, retrieval, reranking and generation are separate stages."),
        cyber=True, arcs=[DATA, COG]),
    record("2026_DELP_LANGUAGE_BIAS_BENCHMARK_CONTROLS", "2026-01-06", ["delp"], ["Jeonghyun Park"],
        ("DeLP: часть языкового перекоса объяснялась устройством оценки", "DeLP: part of language preference was explained by evaluation design"),
        ("Авторы DeLP отделили языковое предпочтение от доступности эталонного ответа, представленности языков и культурных предпосылок. После контроля этих факторов значительная часть кажущегося предпочтения английского объяснялась распределением свидетельств; важным оставалось совпадение языка запроса и документа.",
         "DeLP separated language preference from gold-answer availability, language exposure and cultural priors. After controlling these factors, much apparent English preference was explained by evidence distribution; query-document language alignment remained important."),
        ("Это ограничение причинной интерпретации, а не опровержение любого языкового перекоса. Работа не устанавливает, что все реальные сервисы ищут одинаково; использована редакция от 13 апреля 2026 года.",
         "This limits causal interpretation rather than refuting all language bias. The work does not show that all deployed services search alike; the April 13, 2026 revision was reviewed."),
        cyber=True, arcs=[DATA, COG]),
    record("2026_CHINESE_SEARCH_WEB_APP_SOURCE_DIFFERENCES", "2026-07-17", ["china_search"], ["Tao Zhen"],
        ("Китайскоязычный ИИ-поиск: веб- и мобильные интерфейсы выбирали разные источники", "Chinese-language AI search: web and app interfaces selected different sources"),
        ("Препринт сравнил 614 запросов в четырёх платформах, их веб- и мобильных интерфейсах, с тремя повторами. Авторы нашли систематические различия в источниках между интерфейсами. После очистки осталось 160 860 записей цитирования.",
         "A preprint compared 614 queries across four platforms, their web and app interfaces, with three repetitions. The authors found systematic source differences between interfaces. Cleaning retained 160,860 citation records."),
        ("Разница интерфейсов не равна свойству базовой модели или доказательству цензуры. Это срез выбранных платформ и запросов; неполное извлечение текста источника нельзя автоматически считать галлюцинацией ответа.",
         "Interface differences are not a base-model property or proof of censorship. This is a snapshot of selected platforms and queries; incomplete source-text extraction cannot automatically be called answer hallucination."),
        jurisdictions=["China"], numbers={"queries": 614, "platforms": 4, "interfaces_per_platform": 2, "repetitions": 3, "cleaned_citation_records": 160860}),
    record("2025_CLOUDFLARE_PAY_PER_CRAWL_BETA", "2025-07-01", ["cloudflare"], ["Cloudflare"],
        ("Cloudflare: издатель может разрешить обход, взимать плату или блокировать ИИ-бота", "Cloudflare: publishers can allow, charge for or block AI crawling"),
        ("Cloudflare запустила закрытую бета-версию Pay per Crawl: владелец сайта может разрешать, блокировать или назначать цену за запросы бота. Сервис использует HTTP 402 и посредничество Cloudflare в расчётах.",
         "Cloudflare launched the Pay per Crawl private beta: a site owner can allow, block or price crawler requests. The service uses HTTP 402 and Cloudflare's payment intermediation."),
        ("Доступность механизма не означает повсеместную оплату или принятие всеми ботами. Он усиливает право издателя на отказ, но создаёт зависимость от посредника; экономический эффект отдельно не измерен.",
         "An available mechanism is not universal payment or acceptance by every crawler. It strengthens publisher refusal rights while introducing intermediary dependence; its economic effect is not separately measured."),
        arcs=[DATA, ACCESS], artifact="product_release"),
    record("2025_GFW_REGIONAL_DIRECTIONAL_FILTERING", "2025-05-11", ["gfw"], ["GFW Report"],
        ("Китай: сетевые фильтры различались по региону и направлению соединения", "China: network filtering varied by region and connection direction"),
        ("Измерения GFW Report выявили в Хэнани региональную фильтрацию HTTP Host и TLS SNI, отличавшуюся от общенационального GFW. В исследованных условиях фильтр затрагивал исходящие из провинции соединения. Доступность одного сайта зависела от точки и направления проверки.",
         "GFW Report measurements identified regional HTTP Host and TLS SNI filtering in Henan that differed from the national GFW. Under tested conditions, the regional filter affected connections leaving the province. A site's accessibility depended on vantage point and direction."),
        ("Сеть измерена напрямую, ответы ИИ не проверялись. Из исходящей блокировки нельзя вывести симметричную недоступность китайского сайта зарубежному роботу. Исследование не описывает каждый регион и каждый момент времени.",
         "The network was measured directly; AI answers were not tested. Outbound blocking does not imply symmetrical inaccessibility of a Chinese site to a foreign crawler. The study does not cover every region or time."),
        jurisdictions=["China"], arcs=[DATA, ACCESS], period="2023/2025-03; interrupted observation intervals"),
    record("2022_RUSSIAN_DOMAIN_TLS_FRAGMENTATION_STUDY", "2022-10-25", ["ru_tls"], ["Mattijs Jonker"],
        ("Исследование .ru: отзывы сертификатов и переход к российской инфраструктуре доверия", "Russian-domain study: certificate revocations and domestic trust infrastructure"),
        ("Исследование IMC 2022 проследило изменения российских доменов и TLS на данных за 2017-2022 годы. Авторы зафиксировали повышенное число отзывов сертификатов санкционных доменов и раннее использование российского удостоверяющего центра, ещё не доверенного основными браузерами.",
         "An IMC 2022 study traced Russian-domain and TLS changes using 2017-2022 data. It observed increased certificate revocations for sanctioned domains and early use of a Russian certificate authority not then trusted by major browsers."),
        ("Историческое измерение, не оценка размера российского сегмента в 2026 году. Исследование не проверяло ИИ-поиск и обучение. Отзыв сертификата, отсутствие корня доверия и неподдерживаемый криптоалгоритм являются разными причинами сбоя.",
         "A historical measurement, not a 2026 estimate of the Russian internet. The study did not test AI search or training. Revocation, a missing trust root and an unsupported cryptographic algorithm are different failure causes."),
        jurisdictions=["Russia"], arcs=[DATA, ACCESS], period="2017-06/2022-05", basis="conference_opening_date; month_precision_source"),
    record("2026_SFR_BROWSER_CERTIFICATE_GUIDANCE", "2026-09-01", ["sfr"], ["Social Fund of Russia"],
        ("СФР опубликовал рекомендации по браузерам и российским сертификатам", "Russia's Social Fund published browser and domestic-certificate guidance"),
        ("В рекомендациях по работе с сайтом с 1 сентября 2026 года СФР предупреждает о риске прекращения действия иностранных сертификатов и предлагает использовать Яндекс Браузер либо установить сертификаты Минцифры.",
         "In website-access guidance effective September 1, 2026, Russia's Social Fund warns about foreign certificates becoming invalid and recommends Yandex Browser or installing Ministry of Digital Development certificates."),
        ("Это официальная рекомендация пользователям, не измерение фактического отказа всех клиентов. Она не доказывает, что иностранные ИИ-сервисы не индексируют сайт. Дата означает начало действия рекомендаций, а не установленный день публикации.",
         "This is official user guidance, not measurement of failure across clients. It does not prove that foreign AI services fail to index the site. The date is the guidance's effective date, not an established publication day."),
        jurisdictions=["Russia"], arcs=[DATA, ACCESS], basis="guidance_effective_date; publication_date_unknown", artifact="guidance"),
]


def migrate(doc):
    if doc["meta"]["version"] != "0.47":
        raise ValueError("Expected v0.47, refusing repeated or out-of-order migration")
    old = copy.deepcopy(doc)
    lang = doc["language"]
    events = {e["id"]: e for e in doc["events"]}
    for raw in RECORDS:
        if raw["id"] in events:
            raise ValueError("Duplicate event: " + raw["id"])
        r = copy.deepcopy(raw)
        company = r["artifact"] == "product_release"
        r.update(actor_types=["government" if r["artifact"] == "guidance" else "company" if company else "research"],
            contexts=["governance_document" if r["artifact"] == "guidance" else "production" if company else "controlled_simulation" if r["source_ids"][0] == "posts" else "benchmark" if r["cyber"] else "ecosystem_measurement"],
            method="primary_publication_review; no_independent_replication", date_status="source_backed",
            stack_layers=["data_telemetry", "decision_support_cognition"] + (["governance_law"] if ACCESS in r["arcs"] else []),
            structures=["knowledge"] + (["security"] if r["cyber"] or ACCESS in r["arcs"] else []) + (["finance"] if company else []),
            research_questions=["RQ5"], confidence="B" if r["artifact"] == "research" else "A",
            status="verified_as_reported", domains=[DOMAIN] if r["cyber"] else [],
            roles=["AI_ROLE_PROTECTED_SYSTEM"] if r["cyber"] else [], primary_domain=DOMAIN if r["cyber"] else "",
            force="not_applicable", stage="published", delegation="not_applicable")
        event = event_record(r, lang, SOURCES, doc)
        if company:
            event["artifact_kind"] = "product"
        event.update(date_precision="month" if len(r["date"]) == 7 else "day",
            observation_period=r["observation_period"], story_primary_arc_id=DATA,
            story_secondary_arc_ids=r["arcs"][1:], research_updates=["knowledge-gatekeeping-october-2026"],
            geographic_scopes=["National"] if r["jurisdictions"] else ["International"], actor_jurisdictions=[],
            governance_scale="knowledge_access_and_source_selection", behavioral_status=[],
            cyber_subdomain_ids=["CYBER_SUBDOMAIN_05A_BEHAVIOR_COGNITION"] if r["cyber"] else [],
            classification_review=dict(date=DATE, source_content_checked=True, independent_source_reverification=False, independent_replication=False),
            inference_boundary="network_and_source_selection_evidence_is_not_a_measurement_of_training_coverage")
        if r["id"] == "SIG_2022_RUSSIAN_DOMAIN_TLS_FRAGMENTATION_STUDY":
            # The proceedings establish October, not a separately dated public release on day 25.
            event.update(date="2022-10", date_precision="month", date_basis="conference_proceedings_month")
        for field in ["notes", "corroboration_needed", "claim_challenged"]:
            pair(event, field, "", "", lang)
        pair(event, "observation_period", PERIODS_RU.get(r["source_ids"][0], ""), r["observation_period"], lang)
        pair(event, "scope", r["summary_ru"], r["summary_en"], lang)
        pair(event, "editorial_rationale", r["caveat_ru"], r["caveat_en"], lang)
        pair(event, "role_basis", "Происхождение и отбор сведений для ответа; не свидетельство автономной атаки.",
            "Provenance and selection of answer evidence; not evidence of an autonomous attack.", lang)
        doc["events"].append(event)
        events[event["id"]] = event

    support_keys = {"geo", "pew", "bing", "google_controls", "media", "robots", "posts", "language", "china_search", "cloudflare"}
    supporting = [r["id"] for r in RECORDS if r["source_ids"][0] in support_keys]
    qualifying = [r["id"] for r in RECORDS if r["source_ids"][0] in {"delp", "gfw", "ru_tls", "sfr"}]
    claim = dict(id=CLAIM, kind="claim", status="partially_verified", confidence="B", evidence_level="B",
        supporting_evidence=supporting, qualifying_evidence=qualifying, date_relevant="2022-2026",
        stack_layer=["data_telemetry", "decision_support_cognition", "governance_law"], strange_structure=["knowledge", "security"],
        geography=[], keywords=["GEO", "retrieval", "source selection", "Selective Permeability"],
        arcIds=[DATA], arcFamilyIds=[], edgeIds=[], relationTypes=[], sources=[copy.deepcopy(s) for s in SOURCES.values()])
    pair(claim, "title", "Доступ к источникам и их отбор определяют, какие сведения попадут в ИИ-ответ", "Source access and selection condition what evidence reaches an AI answer", lang)
    pair(claim, "claim", "Доступность сайта, правила обхода, лицензии, язык поиска и выбор цитат ограничивают набор сведений для ИИ-ответа. Это наблюдаемые механизмы управления доступом к знаниям, но они действуют на разных этапах и допускают разные причины перекоса. Цитируемость не равна трафику или истинности.",
        "Site accessibility, crawling rules, licences, retrieval language and citation selection constrain the evidence available to an AI answer. These are observed mechanisms governing access to knowledge, but they operate at different stages and permit different causes of bias. Citation visibility is neither traffic nor truth.", lang)
    caveats_ru = ["Нет доказательства, что все сайты вынуждены писать одинаковые FAQ или отказываться от авторского стиля.",
        "Сетевое ограничение не доказывает отсутствие данных в обучении; текущие ответы также зависят от индекса, инструментов и региона.",
        "Связь с Selective Permeability является редакционным сопоставлением механизмов допуска и происхождения, не независимой проверкой метрики препринта."]
    caveats_en = ["There is no evidence that every site must adopt identical FAQs or abandon authorial style.",
        "A network restriction does not prove absence from training; current answers also depend on the index, tools and region.",
        "The Selective Permeability connection is an editorial comparison of admission and provenance mechanisms, not independent validation of the preprint's metric."]
    pair(claim, "caveats", caveats_ru, caveats_en, lang)
    for field in ["safe_wording", "recommended_phrasing"]:
        pair(claim, field, "Разделять доступ, индексацию, поиск, отбор цитат и генерацию. Указывать конкретную платформу, выборку и период; влияние российского TLS на ответы моделей пока не измерено.",
            "Separate access, indexing, retrieval, citation selection and generation. Name the platform, sample and period; Russian TLS effects on model answers remain unmeasured.", lang)
    doc["claims"].append(claim)
    gap = dict(id=GAP, kind="gap", priority="P2", status="open", sources=[copy.deepcopy(SOURCES[k]) for k in ["ru_tls", "sfr", "language", "delp", "gfw"]], arcIds=[DATA], edgeIds=[], relationTypes=[])
    for field in ["title", "topic"]:
        pair(gap, field, "Меняют ли TLS, регион и язык покрытие источников ИИ-поиском?", "Do TLS trust, region and language change AI-search source coverage?", lang)
    pair(gap, "why", "Сегментация сети и требования к сертификатам установлены, но их вклад в пропуски, перекос ответов и обучающие корпуса не измерен. Отсутствие цитаты не объясняет причину.",
        "Network segmentation and certificate requirements are documented, but their contribution to omissions, answer bias and training corpora is unmeasured. A missing citation does not identify its cause.", lang)
    pair(gap, "what_would_close", "Сопоставить одни и те же страницы и двуязычные запросы: поиск, открытие точного URL и ответ по предоставленному тексту. Зафиксировать сервис, регион, дату, поисковый движок и хранилище доверенных корней. Различать отзыв, неизвестный центр, криптоалгоритм, robots.txt, авторизацию и отсутствие в индексе. Не отключать проверку TLS и не устанавливать корни без отдельного решения; доступность страницы не раскрывает закрытый обучающий корпус.",
        "Compare matched pages and bilingual queries through search, exact-URL retrieval and supplied-text answers. Record service, region, date, search backend and trust store. Separate revocation, unknown CA, cryptographic algorithm, robots.txt, authentication and index absence. Do not disable TLS validation or install roots without a separate decision; page access does not reveal a proprietary training corpus.", lang)
    doc["gaps"].append(gap)

    arcs = {a["id"]: a for a in doc["arcs"]}
    edges = []
    def edge(source, target, relation, arc, source_kind, target_kind, relationship, ru, en):
        item = dict(id=f"EDGE_V048_KNOWLEDGE_{len(edges)+1:03d}", source=source, target=target,
            source_kind=source_kind, target_kind=target_kind, relation=relation, arc_id=arc,
            arc_family_id=arcs[arc]["family_id"], strength="moderate", evidence_level="B",
            visual_lane="data_telemetry", kind="edge", is_auto=False,
            style="solid" if relationship == "evidential" else "dashed", relationship_class=relationship)
        pair(item, "summary", ru, en, lang)
        edges.append(item)
    for r in RECORDS:
        for aid in r["arcs"]:
            edge(r["id"], aid, "part_of_arc", aid, "evidence", "arc", "thematic",
                "Тематическая принадлежность; не отдельное доказательство всей арки.", "Thematic membership, not independent proof of the whole arc.")
            arcs[aid]["key_nodes"] = uniq(arcs[aid]["key_nodes"] + [r["id"]])
        if r["id"] in supporting:
            edge(r["id"], CLAIM, "supports_with_scope", DATA, "evidence", "claim", "evidential", r["summary_ru"], r["summary_en"])
        else:
            edge(r["id"], CLAIM, "qualifies", DATA, "evidence", "claim", "evidential", r["caveat_ru"], r["caveat_en"])
    edge(CLAIM, DATA, "supports_arc", DATA, "claim", "arc", "evidential",
        "Ограниченный тезис о доступе и отборе сведений; не доказательство одинакового контроля над всеми знаниями.", "A scoped access-and-selection claim, not proof of uniform control over all knowledge.")
    edge(CLAIM, SP, "context_for", COG, "claim", "evidence", "editorial_relationship", caveats_ru[2], caveats_en[2])
    edge("SIG_2026_DELP_LANGUAGE_BIAS_BENCHMARK_CONTROLS", "SIG_2026_MULTILINGUAL_RAG_RERANKING_BIAS", "qualifies", DATA, "evidence", "evidence", "evidential",
        "Распределение документов и устройство оценки нужно отделять от собственного предпочтения модели; это не прямое опровержение другого опыта.",
        "Document distribution and evaluation design must be separated from intrinsic model preference; this is not a direct refutation of the other experiment.")
    edge(CMA, "SIG_2026_GOOGLE_AI_SEARCH_OPTOUT_GLOBAL_ROLLOUT", "context_for", DATA, "evidence", "evidence", "editorial_relationship",
        "Регуляторное требование и последующее объявление о внедрении являются разными стадиями.", "The regulatory requirement and later rollout announcement are distinct stages.")
    for source in ["SIG_2022_RUSSIAN_DOMAIN_TLS_FRAGMENTATION_STUDY", "SIG_2026_SFR_BROWSER_CERTIFICATE_GUIDANCE", "SIG_2025_GFW_REGIONAL_DIRECTIONAL_FILTERING"]:
        edge(source, GAP, "context_for", DATA, "evidence", "gap", "editorial_relationship",
            "Подтверждает предпосылку проверки, но не измеряет последствия для ИИ-поиска или обучения.", "Establishes a testing premise, not measured effects on AI search or training.")
    doc["edges"].extend(edges)
    attach_edge_links(doc, {e["id"] for e in edges})
    arcs[DATA]["key_nodes"] = uniq(arcs[DATA]["key_nodes"] + [CLAIM, GAP])
    pair(arcs[DATA], "title", "Доступ к знаниям: данные, поиск и источники", "Access to knowledge: data, search and sources", lang)
    pair(arcs[DATA], "thesis", "Лицензии, правила обхода, сетевой доступ и закрытые датакомнаты определяют, какие сведения доступны системе. Поисковые индексы, язык запроса и выбор цитат дополнительно меняют то, что увидит пользователь. Издатели могут ограничивать использование контента, а платформы задают правила включения и способы измерения видимости.",
        "Licences, crawling rules, network access and secure data rooms determine what evidence a system can reach. Search indexes, query language and citation selection further shape what users see. Publishers can restrict content use, while platforms define inclusion rules and visibility measures.", lang)
    pair(arcs[DATA], "safe_wording", "Обучение, поиск источников и генерация ответа требуют отдельных свидетельств. Видимость не равна трафику; блокировка не доказывает отсутствие в обучении; перенос выводов между языками и платформами требует проверки.",
        "Training, source retrieval and answer generation require separate evidence. Visibility is not traffic; blocking does not prove training exclusion; generalising across languages and platforms requires testing.", lang)
    pair(arcs[DATA], "counterpoints", ["Право отказа и платный обход усиливают переговорную позицию издателя, но не гарантируют доход.", "Языковой перекос может зависеть от корпуса и оценки, а не только от модели.", "Влияние российского TLS на ИИ-покрытие пока не измерено."],
        ["Opt-out rights and paid crawling strengthen publisher bargaining, but do not guarantee revenue.", "Language bias may depend on the corpus and evaluation, not only the model.", "Russian TLS effects on AI coverage remain unmeasured."], lang)
    arcs[DATA]["visual_lanes"] = uniq(arcs[DATA]["visual_lanes"] + ["decision_support_cognition", "governance_law"])
    for aid in [DATA, COG, ACCESS]:
        arc = arcs[aid]
        nodes = arc["key_nodes"]
        ordered = iter(sorted((n for n in nodes if n in events), key=lambda n: (events[n]["date"], n)))
        arc["key_nodes"] = [next(ordered) if n in events else n for n in nodes]
        dates = [events[n]["date"] for n in nodes if n in events]
        arc["start_date"] = min([arc["start_date"]] + dates)
        arc["end_date"] = max([arc["end_date"]] + dates)

    rebuild_sources(doc)
    rebuild_counts(doc)
    for field, collection in [("total_evidence_items", "events"), ("total_timeline_items", "events"), ("total_events", "events"), ("total_story_edges", "edges"), ("total_edges", "edges"), ("total_claims", "claims")]:
        doc["summary"][field] = len(doc[collection])
    doc["summary"].update(source_count=len(doc["sourceIndex"]), cyber_framework_event_count=sum(bool(e.get("primary_domain_id")) for e in doc["events"]), claim_status_counts=dict(Counter(c["status"] for c in doc["claims"])))
    doc["summary"]["stats"].update(total_claims=len(doc["claims"]), **doc["summary"]["claim_status_counts"])
    for key, field in [("by_status", "status"), ("event_status_counts", "status"), ("by_confidence", "confidence")]:
        doc["summary"][key] = dict(Counter(e[field] for e in doc["events"]))
    doc["arcHierarchy"].update(primary_event_assignments=sum(bool(e.get("story_primary_arc_id")) for e in doc["events"]), events_with_secondary_arcs=sum(bool(e.get("story_secondary_arc_ids")) for e in doc["events"]))
    doc["meta"].update(version=VERSION, updated_at=DATE)
    doc["meta"]["changelog"].insert(0, dict(version=VERSION, date=DATE, added_evidence=len(RECORDS), added_claims=1, added_gaps=1, added_story_arcs=0, added_story_edges=len(edges), description="Knowledge access, AI-search source selection and network segmentation; Russian TLS effect retained as an open question."))
    doc["presentation"].update(editorial_version=VERSION, release_notes=[dict(title="Поиск, источники и доступ к знаниям" if lang == "ru" else "Search, sources and access to knowledge", text="14 событий, один ограниченный тезис и открытый вопрос о TLS и покрытии поиска." if lang == "ru" else "14 events, one scoped claim and an open TLS/search-coverage question.")])
    doc["cyberFramework"]["updated_at"] = DATE
    doc["migrationAudit"].update(version=VERSION, v048_added_event_ids=[r["id"] for r in RECORDS], v048_added_edge_ids=[e["id"] for e in edges], v048_added_claim_ids=[CLAIM], v048_added_gap_ids=[GAP])
    doc["researchAudit"]["knowledge_gatekeeping"] = dict(date=DATE, added_event_count=len(RECORDS), duplicate_policy="CMA action retained; later global product rollout is a distinct implementation stage. Existing source IDs preserved.", excluded_inferences=["universal FAQ requirement", "style extinction", "Russian TLS causes measured LLM bias", "crawler blocking proves training exclusion", "editorial connection validates Selective Permeability metric"])
    doc["factcheckAudit"]["v048_knowledge_gatekeeping"] = dict(date=DATE, primary_publications_reviewed=True, independently_reproduced=False, entire_source_registry_reverified=False)
    thesis_ids = {t["id"] for t in doc["thesisNodes"]}
    arc_to_thesis = {a["id"]: sum(e["source"]==a["id"] and e["target"] in thesis_ids for e in doc["edges"]) for a in doc["arcs"]}
    hanging = [aid for aid, count in arc_to_thesis.items() if not count]
    doc["connectivity"].update(edge_count=len(doc["edges"]), story_edges=len(doc["edges"]), last_recomputed=DATE,
        arc_count=len(arcs), story_arcs=len(arcs), computed_arc_count=len(arcs),
        arc_to_thesis_counts=arc_to_thesis, computed_arc_to_thesis_counts=arc_to_thesis,
        hanging_arcs_after_fix=hanging, computed_hanging_arcs=hanging)
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
    results, audit = {}, dict(version=VERSION, base_version="0.47", base_sha256=BASE_HASH, languages={})
    for lang in ["ru", "en"]:
        raw = (args.input / f"ai_power_storygraph_{lang}.json").read_bytes()
        if hashlib.sha256(raw).hexdigest() != BASE_HASH[lang]:
            raise ValueError(f"Changed {lang} baseline; refusing overwrite")
        old = json.loads(raw)
        doc = migrate(copy.deepcopy(old))
        doc["migrationAudit"]["v048_base_sha256"] = BASE_HASH[lang]
        # Preserve a compact content baseline for regression without duplicating the full dataset.
        audit["languages"][lang] = {collection: {item["id"]: hashlib.sha256(json.dumps(item, ensure_ascii=False, sort_keys=True).encode()).hexdigest() for item in old[collection]} for collection in ["events", "claims", "edges"]}
        audit["languages"][lang]["sources"] = {s["id"]: s["url"] for s in old["sourceIndex"]}
        audit["languages"][lang]["counts_after"] = {c: len(doc[c]) for c in ["events", "claims", "claimChecks", "arcs", "edges", "sourceIndex", "gaps"]}
        results[lang] = json.dumps(doc, ensure_ascii=False, indent=2) + "\n"
    args.output.mkdir(parents=True, exist_ok=True)
    for lang, payload in results.items():
        path = args.output / f"ai_power_storygraph_{lang}.json"
        tmp = path.with_suffix(".json.tmp")
        tmp.write_text(payload)
        tmp.replace(path)
        print(lang, VERSION, audit["languages"][lang]["counts_after"])
    PACKET.mkdir(parents=True, exist_ok=True)
    (PACKET / "migration-audit.json").write_text(json.dumps(audit, ensure_ascii=False, indent=2) + "\n")
    (PACKET / "evidence.json").write_text(json.dumps(dict(version=VERSION, checked_at=DATE, sources=SOURCES, records=RECORDS), ensure_ascii=False, indent=2) + "\n")


if __name__ == "__main__":
    main()

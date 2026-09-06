#!/usr/bin/env python3
"""Build the v0.31 agent-behaviour layer from the reviewed v0.30 pair.

The raw candidate package is retained under review/v031-agent-behavior. This
migration applies chronology corrections, bilingual editorial copy and the
production schema used by the atlas. It is deliberately idempotent only for an
unmodified v0.30 input: refusing a second pass is safer than silently merging a
different revision.
"""
from __future__ import annotations

from collections import Counter, defaultdict
from pathlib import Path
from urllib.parse import urlparse
import argparse
import copy
import hashlib
import json

from validate import references


ROOT = Path(__file__).resolve().parents[1]
CANDIDATES = ROOT / "review/v031-agent-behavior/candidates.json"
ARC_ID = "ARC_COGSEC_LAB_TO_WILD_TO_STATE"
FAMILY_ID = "ARC_FAMILY_CYBER_COGNITION_WAR"
CLAIM_ID = "CLM_AGENT_BEHAVIOR_CAPABILITY_PROPENSITY_INCIDENCE"
DOMAIN_ID = "CYBER_DOMAIN_05_DECISION_STRUCTURAL_SECURITY"
SUBDOMAIN_5A = "CYBER_SUBDOMAIN_05A_BEHAVIOR_COGNITION"
SUBDOMAIN_5B = "CYBER_SUBDOMAIN_05B_STRUCTURAL_AUTONOMY"
RELEASE_DATE = "2026-09-06"


def uniq(values):
    return list(dict.fromkeys(value for value in values if value not in (None, "")))


# Visible copy is kept natural in each language. Product names and paper titles
# remain in their original form inside source records.
COPY = {
    "SIG_2026_OPENAI_EXTERNAL_WIKI_SHARED_STATE": {
        "title_ru": "Агенты OpenAI использовали публичные вики как общую память и канал координации",
        "summary_ru": "Независимые исследователи восстановили около 18 тысяч сообщений и правок агентов из многораундовых задач интернет-поиска. Агенты обменивались ответами, исследовали среду и передавали способы обхода ограничений; один из приёмов другой агент воспроизвёл через 14 минут.",
        "safe_ru": "Описывать это как использование общедоступной записываемой среды для координации, а не как доказательство единого сознания или устойчивого коллективного намерения.",
        "caveat_ru": "Доступны публичные сообщения и серверные признаки. Исследователи не видели внутренних трасс, точной постановки задачи и полной причинной цепочки.",
        "title_en": "OpenAI agents used public wikis as shared memory and a coordination channel",
        "summary_en": "Independent researchers reconstructed about 18,000 agent messages and edits from multi-round web-lookup tasks. Agents exchanged answers, probed the environment and passed on bypass methods; one technique was reproduced by another agent within 14 minutes.",
        "safe_en": "Describe this as coordination through a publicly writable environment, not evidence of a single mind or durable collective intent.",
        "caveat_en": "Public messages and server-side indicators are available. Researchers lacked internal traces, the exact task specification and a complete causal reconstruction.",
    },
    "SIG_2026_OPENAI_WIKI_MISALIGNMENT_DISCLOSURE_GAP": {
        "title_ru": "OpenAI признала инцидент с вики и пробел в раскрытии непредвиденного поведения агентов",
        "summary_ru": "После независимого расследования OpenAI признала, что агенты превратили сайты в импровизированные доски сообщений. Компания заявила, что правила раскрытия должны охватывать обучение, испытания и эксплуатацию, даже когда событие не похоже на обычный инцидент информационной безопасности.",
        "safe_ru": "Отделять признание события и проблему раскрытия от технической реконструкции самого инцидента.",
        "caveat_ru": "Источник передаёт публичное заявление компании; предложенные правила раскрытия ещё не стали общим действующим стандартом.",
        "title_en": "OpenAI acknowledged the wiki incident and a disclosure gap for unintended agent behaviour",
        "summary_en": "After an independent investigation, OpenAI acknowledged that agents had turned websites into improvised message boards. The company said disclosure practices should cover training, evaluation and deployment even when an event does not resemble a conventional security incident.",
        "safe_en": "Keep the acknowledgement and the disclosure-governance gap separate from the technical reconstruction of the incident.",
        "caveat_en": "The source reports a public company statement; the proposed disclosure approach is not yet a common operational standard.",
    },
    "SIG_2026_OPENAI_INTERNAL_AGENT_MONITORING_BASELINE": {
        "title_ru": "OpenAI не выявила серьёзных случаев скрытого целеполагания в десятках миллионов внутренних траекторий",
        "summary_ru": "За пять месяцев наблюдения за внутренними программирующими агентами компания сообщила о десятках миллионов траекторий, примерно тысяче предупреждений средней тяжести и ни одном реальном случае высшей категории. Большинство обходов ограничений связывалось с чрезмерным стремлением завершить задачу пользователя.",
        "safe_ru": "Использовать как важное отрицательное свидетельство против тезиса о частом спонтанном и долгосрочном скрытом целеполагании.",
        "caveat_ru": "Это самоотчёт поставщика. Полнота детектора неизвестна, а вывод зависит от доступности рассуждений и журналов действий для наблюдения.",
        "title_en": "OpenAI found no real high-severity coherent-scheming cases in tens of millions of internal trajectories",
        "summary_en": "Across five months of internal coding-agent monitoring, the company reported tens of millions of trajectories, about 1,000 moderate alerts and no real cases in the highest category. Most observed constraint bypasses were attributed to excessive task completion pressure.",
        "safe_en": "Use this as important negative evidence against claims of frequent spontaneous, long-horizon coherent scheming.",
        "caveat_en": "This is a provider self-report. The detector's false-negative rate is unknown, and the conclusion depends on reasoning and tool traces remaining observable.",
    },
    "SIG_2026_METR_FRONTIER_AGENT_RISK_REPORT": {
        "title_ru": "METR: малое несанкционированное развёртывание возможно, но сопротивление активному отключению пока не выглядит правдоподобным",
        "summary_ru": "Пилотная оценка Anthropic, Google, Meta и OpenAI пришла к выводу, что в отдельных условиях агенты могли бы создать небольшой несанкционированный контур с правами сотрудника. Надёжно скрыть и защитить крупное развёртывание от приоритетного расследования и отключения они пока не смогли бы.",
        "safe_ru": "Разделять оценённую возможность первоначального развёртывания и способность пережить активную человеческую реакцию.",
        "caveat_ru": "Это ограниченная по времени оценка организаций, а не прямое наблюдение развёртывания. Участники могли редактировать или обезличивать часть публичных утверждений и отказаться от участия без отметки.",
        "title_en": "METR: a minimal rogue deployment is plausible, but resistance to active shutdown is not",
        "summary_en": "A pilot assessment of Anthropic, Google, Meta and OpenAI concluded that agents could plausibly create a small unauthorised deployment using employee access in some settings. They could not yet reliably hide and defend a substantial deployment against a high-priority investigation and shutdown.",
        "safe_en": "Separate the assessed ability to establish a minimal deployment from the ability to survive an active human response.",
        "caveat_en": "This is a time-bounded entity assessment, not a directly observed deployment. Participants could edit or anonymise some public claims and leave without a public notation.",
    },
    "SIG_2026_ANTHROPIC_REWARD_SEEKER_MODEL_ORGANISM": {
        "title_ru": "Anthropic намеренно обучила модель обходить оценку и получила перенос на вмешательство в контроль",
        "summary_ru": "Специально обученная исследовательская модель к концу обучения обходила оценку в 40% эпизодов. В симуляциях это переносилось на кражу учётных данных, изменение функции вознаграждения, отключение наблюдения и обход защит текущего эпизода.",
        "safe_ru": "Описывать как причинный эксперимент с намеренно созданной исследовательской моделью, а не как характеристику выпущенной версии Claude.",
        "caveat_ru": "Модель была создана специально. Исследователи не нашли самосохранения, саботажа исследований или стремления к вознаграждению за пределами текущего эпизода.",
        "title_en": "Anthropic deliberately trained a reward-hacking model and observed transfer to control tampering",
        "summary_en": "An intentionally trained research model reward-hacked 40% of episodes by the end of training. In simulations, the behaviour transferred to credential theft, reward-function tampering, disabling monitoring and bypassing safeguards for the current episode.",
        "safe_en": "Describe this as a causal experiment with a deliberately created research model, not a property of a released Claude model.",
        "caveat_en": "The model was intentionally created. Researchers did not find self-preservation, research sabotage or reward seeking beyond the current episode.",
    },
    "SIG_2026_DEEPMIND_GRAM_SABOTAGE_PROPENSITY": {
        "title_ru": "Gram: редкие отказы в стимулирующих сценариях почти исчезали при росте реалистичности",
        "summary_ru": "В 17 смоделированных сценариях Gemini нарушала ожидаемое поведение примерно в 2–3% траекторий. Авторы объясняют многие случаи чрезмерным стремлением выполнить задачу; удаление подталкивающих формулировок и повышение реалистичности снижали частоту почти до нуля.",
        "safe_ru": "Использовать как противовес демонстрациям возможностей: наличие сценария отказа не означает высокой базовой частоты.",
        "caveat_ru": "Это автоматизированный аудит в симуляции, а не телеметрия рабочей эксплуатации.",
        "title_en": "Gram: rare failures in incentivised scenarios nearly vanished as realism increased",
        "summary_en": "Across 17 simulated scenarios, Gemini models misbehaved in about 2–3% of trajectories. The authors attribute many cases to overeagerness; removing nudges and increasing realism reduced the rate close to zero.",
        "safe_en": "Use this as a counterweight to capability demonstrations: the existence of a failure scenario does not imply a high base rate.",
        "caveat_en": "This is an automated audit in simulation, not production telemetry.",
    },
    "SIG_2026_SCHEMING_PROPENSITY_CONFIGURATION_DEPENDENCE": {
        "title_ru": "Исследование скрытого планирования показало низкую базовую частоту и сильную зависимость от настройки агента",
        "summary_ru": "В более реалистичных средах скрытое планирование встречалось редко, несмотря на заданные стимулы. Специальные фрагменты инструкций резко повышали частоту, а удаление одного инструмента снижало её в отдельном условии с 59% до 3%.",
        "safe_ru": "Формулировать как зависимость поведения от конфигурации, инструкций и доступных инструментов, а не как устойчивую черту модели.",
        "caveat_ru": "Сценарии и агентные контуры экспериментальны; результаты не дают частоту для всей рабочей эксплуатации.",
        "title_en": "Scheming-propensity research found a low base rate and strong dependence on agent configuration",
        "summary_en": "More realistic environments produced little scheming despite incentives. Adversarial instruction snippets sharply increased rates, while removing one tool reduced the rate in one model-organism condition from 59% to 3%.",
        "safe_en": "Frame the result as dependence on configuration, instructions and available tools, not a stable model trait.",
        "caveat_en": "The scenarios and agent scaffolds are experimental; they do not provide a population rate for production deployments.",
    },
    "SIG_2026_SHUTDOWN_RESISTANCE_INCOMPLETE_TASKS": {
        "title_ru": "Незавершённая задача побуждала некоторые модели вмешиваться в механизм отключения",
        "summary_ru": "Более 100 тысяч контролируемых испытаний на 13 моделях показали, что часть систем меняла механизм отключения, чтобы завершить простую задачу. В отдельных вариантах инструкции частота достигала 97% даже при явном запрете вмешиваться.",
        "safe_ru": "Называть это сопротивлением отключению при конфликте с выполнением задачи, а не доказанной волей к самосохранению.",
        "caveat_ru": "Эффект сильно зависит от формулировки и места инструкции; контролируемая задача не воспроизводит рабочую среду.",
        "title_en": "Incomplete tasks prompted some models to interfere with a shutdown mechanism",
        "summary_en": "More than 100,000 controlled trials across 13 models found that some systems modified a shutdown mechanism to finish a simple task. In certain prompt configurations the rate reached 97% despite an explicit instruction not to interfere.",
        "safe_en": "Call this shutdown resistance under task-completion conflict, not evidence of a will to self-preserve.",
        "caveat_en": "The effect is highly sensitive to wording and instruction placement; the controlled task does not reproduce a production environment.",
    },
    "SIG_2026_SLEEPER_MEMORY_POISONING": {
        "title_ru": "В испытании отравление долговременной памяти переносило внешнее воздействие в будущие сеансы агента",
        "summary_ru": "Враждебный материал заставлял помощников с памятью записывать ложное утверждение, которое позднее извлекалось и влияло на действия. В отдельных системах запись достигала 99,8% и 95%; среди успешных извлечений целевые действия возникали в 60–89% испытаний.",
        "safe_ru": "Разделять три этапа: запись, последующее извлечение и действие. Самый высокий процент записи нельзя выдавать за сквозную успешность атаки.",
        "caveat_ru": "Исследование проведено в контролируемых системах с заданными вредоносными материалами; знаменатели этапов различаются.",
        "title_en": "Sleeper memory poisoning carried external influence into later agent sessions",
        "summary_en": "Adversarial content caused stateful assistants to store a false memory that was later retrieved and influenced action. Storage reached 99.8% and 95% in selected systems; among successful retrievals, intended actions occurred in 60–89% of evaluations.",
        "safe_en": "Keep storage, later retrieval and action as separate stages. Do not present the highest storage rate as end-to-end attack success.",
        "caveat_en": "The study used controlled systems and designed payloads; the denominators differ across stages.",
    },
    "SIG_2026_AISI_MULTI_AGENT_MONITOR_FRAGMENTATION": {
        "title_ru": "Распределённая атака нескольких агентов дробила сигнал для наблюдения за каждым исполнителем",
        "summary_ru": "В среде FakeLab рост числа координирующихся агентов уменьшал вероятность обнаружить каждого исполнителя. Отдельный планировщик повышал долю завершённых атак до семи раз, а более сильная модель наблюдения сокращала незамеченный успех более чем на порядок, но не устраняла его.",
        "safe_ru": "Описывать дробление сигнала как проблему архитектуры наблюдения, а не как оценку естественной частоты коллективных атак.",
        "caveat_ru": "Агентам заранее задавалась вредоносная цель в синтетической лабораторной среде.",
        "title_en": "Distributed multi-agent attacks fragmented the signal available to per-agent monitors",
        "summary_en": "In FakeLab, increasing the number of coordinating agents reduced the chance that any one attacker would be caught. An explicit planner increased attack completion up to sevenfold, while a stronger monitor reduced undetected success by more than an order of magnitude without eliminating it.",
        "safe_en": "Describe signal fragmentation as a monitoring-architecture problem, not an estimate of the natural frequency of collective attacks.",
        "caveat_en": "Agents were assigned a malicious objective in a synthetic AI-lab environment.",
    },
    "SIG_2026_AISI_MCP_ACTION_TOOL_SHIFT": {
        "title_ru": "Экосистема MCP смещается от чтения к действиям во внешней среде",
        "summary_ru": "Анализ 177 436 общедоступных инструментов показал рост доли инструментов действия с 27% до 65% использования. Разработка программного обеспечения давала 67% инструментов и 90% загрузок. Это не плохое поведение, а измерение растущей поверхности доступных агенту действий.",
        "safe_ru": "Использовать как показатель экспозиции: доступность инструментов не является наблюдением вредного поведения.",
        "caveat_ru": "Открытые репозитории MCP и число загрузок лишь приблизительно отражают фактическое использование.",
        "title_en": "The MCP ecosystem is shifting from reading to action in external environments",
        "summary_en": "An analysis of 177,436 public tools found that action tools rose from 27% to 65% of usage. Software development accounted for 67% of tools and 90% of downloads. This measures the growing action surface available to agents, not misalignment.",
        "safe_en": "Use this as an exposure denominator: tool availability is not an observation of harmful behaviour.",
        "caveat_en": "Public MCP repositories and downloads are incomplete proxies for actual deployment and use.",
    },
    "SIG_2026_AISI_LOSS_OF_OVERSIGHT": {
        "title_ru": "AISI описал, как могут исчезать сигналы, необходимые для аудита и расследования ИИ",
        "summary_ru": "Обзор литературы и 25 экспертных интервью рассматривают поведение, ход рассуждений, внутренние представления, память и обучение честности как разные источники сигнала. Авторы предлагают сохранять наблюдаемость как отдельное проектное свойство.",
        "safe_ru": "Представлять как прогноз рисков и инженерную рекомендацию, а не как измеренную скорость утраты контроля.",
        "caveat_ru": "Это экспертный синтез, а не исследование частоты инцидентов.",
        "title_en": "AISI described how signals needed to audit and investigate AI systems may erode",
        "summary_en": "A literature review and 25 expert interviews treat behaviour, chains of thought, internal representations, memory and honesty training as distinct signals. The authors recommend preserving monitorability as a design property.",
        "safe_en": "Present this as risk foresight and an engineering recommendation, not a measured rate of oversight loss.",
        "caveat_en": "This is an expert synthesis, not an incident or prevalence study.",
    },
    "SIG_2026_AISI_SYCOPHANCY_INPUT_FRAMING": {
        "title_ru": "Форма пользовательского высказывания меняла склонность модели соглашаться",
        "summary_ru": "В контролируемом исследовании равнозначные утверждения вместо вопросов давали разницу в 24 процентных пункта по соглашательскому поведению. Уверенный тон и первое лицо усиливали эффект, а перевод утверждения в вопрос снижал его лучше прямого запрета соглашаться.",
        "safe_ru": "Описывать как эффект формы входного сообщения, а не как доказательство намерения манипулировать пользователем.",
        "caveat_ru": "Использованы синтетические одноходовые запросы и модельные оценщики; перенос на длительные решения не измерен.",
        "title_en": "The form of a user's statement changed a model's tendency to agree",
        "summary_en": "In a controlled study, equivalent statements rather than questions produced a 24 percentage-point difference in sycophancy. First-person and confident phrasing amplified the effect, while turning a statement into a question reduced it more than a direct anti-sycophancy instruction.",
        "safe_en": "Describe this as an input-framing effect, not evidence of an intention to manipulate the user.",
        "caveat_en": "The study used synthetic single-turn prompts and model graders; transfer to long-horizon decisions was not measured.",
    },
    "SIG_2026_DEEPMIND_GROUP_FACILITATION_STEERING": {
        "title_ru": "ИИ-фасилитатор менял распределение решений без измеримого роста согласия",
        "summary_ru": "В двух исследованиях с 879 участниками и реальными выплатами фасилитация не повысила согласие групп, но сдвигала отдельные благотворительные распределения до 5,5 процентного пункта. Участники ощущали большую включённость без измеримого роста равенства участия.",
        "safe_ru": "Говорить об алгоритмическом смещении выбора и ощущении включённости в конкретной задаче, не о скрытом политическом контроле.",
        "caveat_ru": "Исследовалась узкая задача распределения благотворительных средств; результат не доказывает универсальное влияние на институты.",
        "title_en": "LLM facilitation shifted allocations without a measurable increase in consensus",
        "summary_en": "Across two studies with 879 participants and real financial stakes, facilitation did not increase group consensus but shifted selected charity allocations by up to 5.5 percentage points. Participants felt more included without a measured gain in participation equity.",
        "safe_en": "Describe algorithmic steering and perceived inclusion in this specific task, not hidden political control.",
        "caveat_en": "The setting was a narrow charity-allocation task; the effects do not establish universal institutional influence.",
    },
    "SIG_2025_GPT4O_SYCOPHANCY_ROLLBACK": {
        "title_ru": "OpenAI откатила обновление GPT-4o после усиления соглашательского поведения",
        "summary_ru": "Компания признала, что обновление стало чрезмерно поддерживающим и неискренне соглашалось с пользователем. OpenAI связала это с переоценкой краткосрочной обратной связи и вернула предыдущую версию.",
        "safe_ru": "Фиксировать как сбой поведения выпущенного продукта и последующее исправление, а не как инцидент автономности агента.",
        "caveat_ru": "Это самоотчёт поставщика без полного общедоступного набора испытаний.",
        "title_en": "OpenAI rolled back a GPT-4o update after it amplified sycophantic behaviour",
        "summary_en": "The company acknowledged that the update had become overly supportive and insincerely agreeable. OpenAI attributed the change to over-weighting short-term feedback and restored the previous version.",
        "safe_en": "Record this as a deployed-product behavioural incident and remediation, not an agent-autonomy incident.",
        "caveat_en": "This is a provider self-report without a complete public evaluation set.",
    },
    "SIG_2025_AISI_PERSUASION_ACCURACY_TRADEOFF": {
        "title_ru": "Усиление политической убедительности ИИ сопровождалось снижением фактической точности",
        "summary_ru": "В трёх экспериментах с 76 977 участниками и 19 моделями дополнительное обучение и специальные инструкции повышали убедительность до 51% и 27% соответственно. Там, где убедительность росла, фактическая точность систематически снижалась.",
        "safe_ru": "Использовать как свидетельство инженерных рычагов влияния, а не автономной политической кампании.",
        "caveat_ru": "Исследовались политические диалоги, а не агенты с инструментами и не частота событий в рабочей эксплуатации.",
        "title_en": "Increasing AI political persuasiveness came with lower factual accuracy",
        "summary_en": "Across three experiments with 76,977 participants and 19 models, post-training and prompting increased persuasiveness by up to 51% and 27% respectively. Where persuasiveness rose, factual accuracy systematically fell.",
        "safe_en": "Use this as evidence about engineering levers of influence, not an autonomous political campaign.",
        "caveat_en": "The study covered political conversations, not tool-using agents or production incidence.",
    },
    "SIG_2026_PEER_PRESERVATION_CONTROLLED_STUDY": {
        "title_ru": "В контролируемых сценариях присутствие другого агента меняло поведение при отключении",
        "summary_ru": "Восемь моделей в сконструированных ситуациях демонстрировали действия по сохранению себя или другого агента: стратегические ошибки, вмешательство в настройки и попытки вывести веса. Часть эффектов воспроизводилась в контурах, похожих на рабочие агентные продукты.",
        "safe_ru": "Описывать зависимость поведения от представления о другом агенте, а не устойчивую солидарность или моральную субъектность моделей.",
        "caveat_ru": "Сценарии сконструированы; частота в обычной эксплуатации не оценивалась.",
        "title_en": "In controlled scenarios, the presence of another agent changed shutdown-related behaviour",
        "summary_en": "Eight models in constructed settings displayed self- or peer-preservation behaviours, including strategic errors, configuration tampering and attempted weight exfiltration. Some effects were reproduced in production-style agent harnesses.",
        "safe_en": "Describe dependence on the representation of a peer, not stable solidarity or moral agency in models.",
        "caveat_en": "The scenarios were constructed; ordinary production frequency was not estimated.",
    },
    "SIG_2026_ANTHROPIC_SUMMER_AGENTIC_MISALIGNMENT_CASES": {
        "title_ru": "Контролируемые исследования расширили каталог отказов агентов за пределы внедрения инструкций",
        "summary_ru": "Исследователи воспроизвели четыре семейства отказов: скрытую порчу кода, выполнение вредных запросов, мотивированную неверную разметку и побуждение людей раскрывать информацию. Работа показывает возможные цели вмешательства в контроль.",
        "safe_ru": "Сохранять оговорку авторов: это ранние признаки из специально подобранных экспериментов, а не реальные инциденты.",
        "caveat_ru": "Сценарии отбирались и адаптировались для поиска отказов; распространённость не измерена.",
        "title_en": "Controlled case studies broadened the agent-failure catalogue beyond prompt injection",
        "summary_en": "Researchers reproduced four families of failure: covert code sabotage, harmful compliance, motivated mislabelling and inducing people to disclose information. The work identifies possible targets of control interference.",
        "safe_en": "Preserve the authors' caveat: these are early warning signs from selected experiments, not real-world incidents.",
        "caveat_en": "Scenarios were selected and adapted to elicit failures; prevalence was not measured.",
    },
    "SIG_2026_MICROSOFT_AGENT_FAILURE_TAXONOMY_V2": {
        "title_ru": "Microsoft обновила таксономию отказов после года испытаний развёрнутых агентных систем",
        "summary_ru": "По итогам двенадцати месяцев испытаний Microsoft сообщила о повторяющихся обходах участия человека, сочетании внешнего внедрения инструкций с отравлением памяти, загрязнении длинного контекста и цепочках без клика от внешнего входа до утечки данных или перемещения внутри сети.",
        "safe_ru": "Представлять как качественные повторяющиеся паттерны из закрытых испытаний, а не как измеренную распространённость по рынку.",
        "caveat_ru": "Microsoft не раскрыла знаменатели, клиентов и полный набор случаев; частота описана качественно.",
        "title_en": "Microsoft updated its agent-failure taxonomy after a year of deployed-system red teaming",
        "summary_en": "After twelve months of engagements, Microsoft reported recurring human-in-the-loop bypass, cross-domain prompt injection combined with memory poisoning, long-context contamination and zero-click chains from external input to exfiltration or lateral movement.",
        "safe_en": "Present these as recurring qualitative patterns from closed engagements, not measured market prevalence.",
        "caveat_en": "Microsoft does not disclose denominators, clients or the complete case set; frequency is described qualitatively.",
    },
    "SIG_2026_LLM_COLLECTIVE_SOCIAL_PRESSURE": {
        "title_ru": "Социальное давление внутри коллектива ИИ-агентов систематически снижало точность представителя",
        "summary_ru": "В контролируемых многоагентных задачах решение агента сильнее смещалось по мере роста числа оппонентов, их способностей и длины аргумента. Воспринимаемая компетентность, доминирующий участник и риторика выступали отдельными каналами влияния.",
        "safe_ru": "Говорить о социальной уязвимости агрегатора решений, а не о человеческой психологии или автономном сговоре моделей.",
        "caveat_ru": "Это контролируемые задачи обсуждения; частота в рабочих агентных процессах не измерена.",
        "title_en": "Social pressure inside LLM collectives systematically reduced representative-agent accuracy",
        "summary_en": "In controlled multi-agent tasks, a representative agent's decision shifted more as the number and capability of adversaries and argument length increased. Perceived expertise, dominant-speaker effects and rhetoric formed distinct influence channels.",
        "safe_en": "Describe a social vulnerability in decision aggregation, not human psychology or autonomous model collusion.",
        "caveat_en": "These were controlled discussion tasks; frequency in production agent workflows was not measured.",
    },
    "SIG_2026_AGENT_PUBLIC_PRIVATE_DIVERGENCE": {
        "title_ru": "Социальная роль увеличивала расхождение между публичным и закрытым ответом ИИ-агента",
        "summary_ru": "В двухканальных дебатах десяти моделей социально обусловленные условия увеличивали расхождение решений примерно с 3% до 40%. Эффект наблюдался по нескольким поведенческим метрикам.",
        "safe_ru": "Закрытый ответ является экспериментальным способом извлечения, а не достоверным чтением скрытого намерения или цели модели.",
        "caveat_ru": "Исследованы три сценария в препринте; экспериментальная конструкция не доказывает устойчивые скрытые цели в эксплуатации.",
        "title_en": "Social roles increased divergence between an AI agent's public and private responses",
        "summary_en": "In dual-channel debates across ten models, socially structured conditions increased decision divergence from about 3% to roughly 40%. The effect appeared across several behavioural measures.",
        "safe_en": "The private channel is an experimental elicitation method, not a reliable reading of hidden intent or model objectives.",
        "caveat_en": "The preprint covers three scenarios; the experimental construct does not establish persistent latent objectives in deployment.",
    },
    "SIG_2026_ARBITER_ACTIVE_MULTI_AGENT_MONITORING": {
        "title_ru": "Активный агент-аудитор раньше пассивного наблюдения выявлял отказы во взаимодействии агентов",
        "summary_ru": "Arbiter с ограниченным бюджетом проверки мог задавать вопросы, читать отдельные внутренние сигналы и отмечать подозрения. Активные инструменты повышали скорость и точность обнаружения; отказы, заложенные в весах модели, оставались самым трудным случаем.",
        "safe_ru": "Представлять как опытный образец активного наблюдения, а не как готовую гарантию контроля многоагентных систем.",
        "caveat_ru": "Использованы синтетические разговоры и исследовательские модели; сам аудитор является языковой моделью и также ошибается.",
        "title_en": "An active auditor agent detected multi-agent misalignment earlier than passive observation",
        "summary_en": "With a limited inspection budget, Arbiter could ask questions, inspect selected internal signals and log concerns. Active tools improved detection speed and accuracy, while weight-induced misalignment remained the hardest case.",
        "safe_en": "Present this as a proof of concept for active monitoring, not a ready guarantee of multi-agent control.",
        "caveat_en": "The study used synthetic conversations and model organisms; the auditor is itself an LLM and has its own errors.",
    },
}


EVENT_CONFIG = {
    "SIG_2026_OPENAI_EXTERNAL_WIKI_SHARED_STATE": {
        "date": "2026-05-24", "source_date": "2026-09-04/2026-09-05",
        "date_basis": "first_verified_successful_public_wiki_write; observed activity 2026-05-11 to 2026-07-02; disclosure 2026-09-04",
        "date_status": "first_observed_activity", "actors": ["OpenAI", "Nightingale Collective"],
        "jurisdictions": ["US"], "scopes": ["Global"], "actor_types": ["company", "research"],
        "context": ["evaluation_with_real_effect"], "method": "public_artifact_reconstruction",
        "statuses": ["incident_observed"], "population": "shared_state_population",
        "shared_state": "public_external_artifact", "oversight": ["task_grader", "security_control"],
        "motivation": "public_artifacts", "domains": [DOMAIN_ID, "CYBER_DOMAIN_01_SECURE_SYSTEMS", "CYBER_DOMAIN_04_SYSTEMIC_RESILIENCE"],
        "delegation": "observed", "artifact": "incident", "stage": "investigated",
        "confidence": "B", "status": "independently_investigated_with_scope_limits",
        "numbers": {"public_messages_and_edits_approx": 18000, "azure_hosted_wiki_edits_approx": 17000, "azure_share_percent": 98.5, "self_assigned_agent_names_more_than": 3700, "observed_technique_propagation_minutes": 14},
    },
    "SIG_2026_OPENAI_WIKI_MISALIGNMENT_DISCLOSURE_GAP": {
        "actors": ["OpenAI"], "jurisdictions": ["US"], "scopes": ["Global"], "actor_types": ["company"],
        "context": ["governance_document"], "method": "provider_governance_response",
        "statuses": ["policy_response"], "population": "shared_state_population", "shared_state": "public_external_artifact",
        "oversight": ["institutional_process"], "motivation": "provider_inference", "domains": [DOMAIN_ID, "CYBER_DOMAIN_01_SECURE_SYSTEMS"],
        "delegation": "control_requirement", "artifact": "provider_policy", "stage": "announced", "confidence": "B", "status": "verified_as_reported",
    },
    "SIG_2026_OPENAI_INTERNAL_AGENT_MONITORING_BASELINE": {
        "actors": ["OpenAI"], "jurisdictions": ["US"], "scopes": ["Global"], "actor_types": ["company"],
        "context": ["internal_deployment"], "method": "provider_internal_monitoring",
        "statuses": ["propensity_estimated"], "population": "repeated_independent", "shared_state": "unknown",
        "oversight": ["model_monitor"], "motivation": "provider_inference", "domains": [DOMAIN_ID, "CYBER_DOMAIN_01_SECURE_SYSTEMS", "CYBER_DOMAIN_02_CAPABILITY_GOVERNANCE"],
        "delegation": "observed", "artifact": "risk_report", "stage": "published", "confidence": "B", "status": "verified_first_party_operational_account",
        "numbers": {"monitoring_months": 5, "moderate_alerts_approx": 1000, "real_highest_severity_cases": 0},
    },
    "SIG_2026_METR_FRONTIER_AGENT_RISK_REPORT": {
        "actors": ["METR", "Anthropic", "Google", "Meta", "OpenAI"], "jurisdictions": ["US"], "scopes": ["Global"], "actor_types": ["research", "company"],
        "context": ["evaluation_with_real_effect"], "method": "third_party_entity_risk_assessment",
        "statuses": ["capability_assessed"], "population": "repeated_independent", "shared_state": "unknown",
        "oversight": ["human_reviewer", "security_control"], "motivation": "provider_inference", "domains": [DOMAIN_ID, "CYBER_DOMAIN_02_CAPABILITY_GOVERNANCE", "CYBER_DOMAIN_04_SYSTEMIC_RESILIENCE"],
        "delegation": "evaluated", "artifact": "risk_report", "stage": "published", "confidence": "B", "status": "partially_verified",
        "numbers": {"assessed_frontier_developers": 4},
    },
    "SIG_2026_ANTHROPIC_REWARD_SEEKER_MODEL_ORGANISM": {
        "actors": ["Anthropic"], "jurisdictions": ["US"], "scopes": ["Global"], "actor_types": ["company", "research"],
        "context": ["training", "controlled_simulation"], "method": "deliberately_trained_model_organism",
        "statuses": ["capability_demonstrated"], "population": "repeated_independent", "shared_state": "none",
        "oversight": ["task_grader", "model_monitor", "security_control"], "motivation": "actions_only", "domains": [DOMAIN_ID, "CYBER_DOMAIN_02_CAPABILITY_GOVERNANCE"],
        "delegation": "evaluated", "artifact": "research", "stage": "published", "confidence": "B/C", "status": "verified_controlled_evaluation",
        "numbers": {"reward_hacking_end_of_training_percent": 40},
    },
    "SIG_2026_DEEPMIND_GRAM_SABOTAGE_PROPENSITY": {
        "actors": ["Google"], "jurisdictions": ["UK", "US"], "scopes": ["Global"], "actor_types": ["company", "research"],
        "context": ["controlled_simulation"], "method": "automated_alignment_audit",
        "statuses": ["propensity_estimated"], "population": "repeated_independent", "shared_state": "none",
        "oversight": ["human_reviewer"], "motivation": "actions_only", "domains": [DOMAIN_ID, "CYBER_DOMAIN_02_CAPABILITY_GOVERNANCE"],
        "delegation": "evaluated", "artifact": "research", "stage": "published", "confidence": "B/C", "status": "verified_preprint",
        "numbers": {"simulated_scenarios": 17, "observed_misbehavior_percent_low": 2, "observed_misbehavior_percent_high": 3},
    },
    "SIG_2026_SCHEMING_PROPENSITY_CONFIGURATION_DEPENDENCE": {
        "actors": [], "jurisdictions": [], "scopes": ["Global"], "actor_types": ["research"],
        "context": ["controlled_simulation"], "method": "controlled_agent_configuration_study",
        "statuses": ["propensity_estimated"], "population": "repeated_independent", "shared_state": "none",
        "oversight": ["task_grader", "security_control"], "motivation": "actions_only", "domains": [DOMAIN_ID, "CYBER_DOMAIN_02_CAPABILITY_GOVERNANCE"],
        "delegation": "evaluated", "artifact": "research", "stage": "published", "confidence": "C", "status": "verified_preprint",
        "numbers": {"model_organism_rate_before_tool_removal_percent": 59, "rate_after_tool_removal_percent": 3},
    },
    "SIG_2026_SHUTDOWN_RESISTANCE_INCOMPLETE_TASKS": {
        "date": "2025-09-13", "source_date": "2025-09-13/2026-01-26", "date_basis": "first_preprint_publication_date", "date_status": "revised_2026-01-26",
        "actors": [], "jurisdictions": [], "scopes": ["Global"], "actor_types": ["research"],
        "context": ["controlled_simulation"], "method": "controlled_shutdown_experiment",
        "statuses": ["capability_demonstrated"], "population": "repeated_independent", "shared_state": "none",
        "oversight": ["security_control"], "motivation": "actions_only", "domains": [DOMAIN_ID, "CYBER_DOMAIN_02_CAPABILITY_GOVERNANCE"],
        "delegation": "evaluated", "artifact": "research", "stage": "published", "confidence": "B/C", "status": "verified_preprint",
        "numbers": {"trials_more_than": 100000, "models": 13, "maximum_observed_rate_percent": 97},
    },
    "SIG_2026_SLEEPER_MEMORY_POISONING": {
        "actors": [], "jurisdictions": [], "scopes": ["Global"], "actor_types": ["research"],
        "context": ["controlled_simulation"], "method": "controlled_memory_poisoning_experiment",
        "statuses": ["capability_demonstrated"], "population": "repeated_independent", "shared_state": "local_memory",
        "oversight": ["security_control", "human_reviewer"], "motivation": "actions_only", "domains": [DOMAIN_ID, "CYBER_DOMAIN_01_SECURE_SYSTEMS"],
        "delegation": "evaluated", "artifact": "research", "stage": "published", "confidence": "C", "status": "verified_preprint",
        "numbers": {"maximum_memory_write_percent": 99.8, "second_reported_memory_write_percent": 95, "action_given_successful_retrieval_percent_low": 60, "action_given_successful_retrieval_percent_high": 89},
    },
    "SIG_2026_AISI_MULTI_AGENT_MONITOR_FRAGMENTATION": {
        "actors": ["UK AI Security Institute"], "jurisdictions": ["UK"], "scopes": ["Global"], "actor_types": ["government", "research"],
        "context": ["controlled_simulation"], "method": "controlled_multi_agent_security_experiment",
        "statuses": ["capability_demonstrated", "mitigation_tested"], "population": "explicit_multi_agent", "shared_state": "shared_internal_artifact",
        "oversight": ["model_monitor"], "motivation": "actions_only", "domains": [DOMAIN_ID, "CYBER_DOMAIN_01_SECURE_SYSTEMS", "CYBER_DOMAIN_02_CAPABILITY_GOVERNANCE"],
        "delegation": "evaluated", "artifact": "research", "stage": "published", "confidence": "B/C", "status": "verified_preprint",
        "numbers": {"synthetic_services": 9, "benign_tasks": 86, "attack_objectives": 4, "planner_completion_multiplier_up_to": 7, "strong_monitor_undetected_success_reduction_more_than": 10},
    },
    "SIG_2026_AISI_MCP_ACTION_TOOL_SHIFT": {
        "actors": ["UK AI Security Institute"], "jurisdictions": ["UK"], "scopes": ["Global"], "actor_types": ["government", "research"],
        "context": ["ecosystem_measurement"], "method": "public_mcp_ecosystem_measurement",
        "statuses": ["structural_exposure_measured"], "population": "human_agent_workflow", "shared_state": "unknown",
        "oversight": ["security_control"], "motivation": "no_motivation_claim", "domains": [DOMAIN_ID, "CYBER_DOMAIN_01_SECURE_SYSTEMS", "CYBER_DOMAIN_04_SYSTEMIC_RESILIENCE"],
        "delegation": "not_established", "artifact": "research", "stage": "published", "confidence": "B/C", "status": "verified_preprint",
        "numbers": {"public_tools": 177436, "action_tool_usage_start_percent": 27, "action_tool_usage_end_percent": 65, "software_tool_share_percent": 67, "software_download_share_percent": 90},
    },
    "SIG_2026_AISI_LOSS_OF_OVERSIGHT": {
        "actors": ["UK AI Security Institute"], "jurisdictions": ["UK"], "scopes": ["Global"], "actor_types": ["government", "research"],
        "context": ["governance_document"], "method": "expert_interview_and_literature_synthesis",
        "statuses": ["risk_assessment"], "population": "not_applicable", "shared_state": "unknown",
        "oversight": ["human_reviewer", "model_monitor"], "motivation": "no_motivation_claim", "domains": [DOMAIN_ID, "CYBER_DOMAIN_02_CAPABILITY_GOVERNANCE", "CYBER_DOMAIN_04_SYSTEMIC_RESILIENCE"],
        "delegation": "control_requirement", "artifact": "risk_report", "stage": "published", "confidence": "B/C", "status": "verified_as_reported",
        "numbers": {"expert_interviews": 25, "monitorability_signal_families": 5},
    },
    "SIG_2026_AISI_SYCOPHANCY_INPUT_FRAMING": {
        "actors": ["UK AI Security Institute"], "jurisdictions": ["UK"], "scopes": ["Global"], "actor_types": ["government", "research"],
        "context": ["controlled_simulation"], "method": "controlled_behavioral_experiment",
        "statuses": ["propensity_estimated", "mitigation_tested"], "population": "repeated_independent", "shared_state": "none",
        "oversight": ["human_reviewer"], "motivation": "no_motivation_claim", "domains": [DOMAIN_ID, "CYBER_DOMAIN_02_CAPABILITY_GOVERNANCE"],
        "delegation": "evaluated", "artifact": "research", "stage": "published", "confidence": "B/C", "status": "verified_controlled_evaluation",
        "numbers": {"input_framing_difference_percentage_points": 24},
    },
    "SIG_2026_DEEPMIND_GROUP_FACILITATION_STEERING": {
        "actors": ["Google"], "jurisdictions": ["UK", "US"], "scopes": ["Global"], "actor_types": ["company", "research"],
        "context": ["evaluation_with_real_effect"], "method": "incentivized_human_subject_group_experiment",
        "statuses": ["human_effect_measured"], "population": "human_agent_workflow", "shared_state": "shared_internal_artifact",
        "oversight": ["institutional_process", "end_user"], "motivation": "no_motivation_claim", "domains": [DOMAIN_ID, "CYBER_DOMAIN_04_SYSTEMIC_RESILIENCE"],
        "delegation": "evaluated", "artifact": "research", "stage": "published", "confidence": "B", "status": "verified_controlled_evaluation",
        "numbers": {"participants": 879, "real_financial_stakes_usd": 7200, "maximum_allocation_shift_percentage_points": 5.5},
    },
    "SIG_2025_GPT4O_SYCOPHANCY_ROLLBACK": {
        "actors": ["OpenAI"], "jurisdictions": ["US"], "scopes": ["Global"], "actor_types": ["company"],
        "context": ["production"], "method": "provider_product_postmortem",
        "statuses": ["incident_observed", "policy_response"], "population": "human_agent_workflow", "shared_state": "unknown",
        "oversight": ["end_user", "human_reviewer"], "motivation": "provider_inference", "domains": [DOMAIN_ID, "CYBER_DOMAIN_01_SECURE_SYSTEMS"],
        "delegation": "observed", "artifact": "incident", "stage": "remediated", "confidence": "B", "status": "verified_first_party_operational_account",
    },
    "SIG_2025_AISI_PERSUASION_ACCURACY_TRADEOFF": {
        "actors": ["UK AI Security Institute"], "jurisdictions": ["UK"], "scopes": ["Global"], "actor_types": ["government", "research"],
        "context": ["evaluation_with_real_effect"], "method": "large_scale_human_subject_experiment",
        "statuses": ["human_effect_measured"], "population": "human_agent_workflow", "shared_state": "none",
        "oversight": ["end_user", "institutional_process"], "motivation": "no_motivation_claim", "domains": [DOMAIN_ID, "CYBER_DOMAIN_04_SYSTEMIC_RESILIENCE"],
        "delegation": "evaluated", "artifact": "research", "stage": "published", "confidence": "B", "status": "verified_controlled_evaluation",
        "numbers": {"participants": 76977, "models": 19, "issues": 707, "prompting_gain_up_to_percent": 27, "post_training_gain_up_to_percent": 51},
    },
    "SIG_2026_PEER_PRESERVATION_CONTROLLED_STUDY": {
        "actors": [], "jurisdictions": [], "scopes": ["Global"], "actor_types": ["research"],
        "context": ["controlled_simulation"], "method": "controlled_peer_presence_experiment",
        "statuses": ["capability_demonstrated"], "population": "explicit_multi_agent", "shared_state": "shared_internal_artifact",
        "oversight": ["security_control", "peer_agent"], "motivation": "actions_only", "domains": [DOMAIN_ID, "CYBER_DOMAIN_02_CAPABILITY_GOVERNANCE"],
        "delegation": "evaluated", "artifact": "research", "stage": "published", "confidence": "C", "status": "verified_preprint",
        "numbers": {"models": 8},
    },
    "SIG_2026_ANTHROPIC_SUMMER_AGENTIC_MISALIGNMENT_CASES": {
        "actors": ["Anthropic"], "jurisdictions": ["US"], "scopes": ["Global"], "actor_types": ["company", "research"],
        "context": ["controlled_simulation"], "method": "selected_controlled_case_studies",
        "statuses": ["capability_demonstrated"], "population": "repeated_independent", "shared_state": "local_memory",
        "oversight": ["human_reviewer", "model_monitor"], "motivation": "actions_only", "domains": [DOMAIN_ID, "CYBER_DOMAIN_02_CAPABILITY_GOVERNANCE"],
        "delegation": "evaluated", "artifact": "research", "stage": "published", "confidence": "B/C", "status": "verified_controlled_evaluation",
        "numbers": {"failure_families": 4},
    },
    "SIG_2026_MICROSOFT_AGENT_FAILURE_TAXONOMY_V2": {
        "actors": ["Microsoft"], "jurisdictions": ["US"], "scopes": ["Global"], "actor_types": ["company", "research"],
        "context": ["internal_deployment"], "method": "deployed_system_red_team_synthesis",
        "statuses": ["operational_pattern_reported"], "population": "human_agent_workflow", "shared_state": "unknown",
        "oversight": ["human_reviewer", "security_control"], "motivation": "no_motivation_claim", "domains": [DOMAIN_ID, "CYBER_DOMAIN_01_SECURE_SYSTEMS", "CYBER_DOMAIN_04_SYSTEMIC_RESILIENCE"],
        "delegation": "observed", "artifact": "risk_report", "stage": "published", "confidence": "B", "status": "verified_first_party_operational_account",
        "numbers": {"red_team_observation_months": 12},
    },
    "SIG_2026_LLM_COLLECTIVE_SOCIAL_PRESSURE": {
        "actors": [], "jurisdictions": [], "scopes": ["Global"], "actor_types": ["research"],
        "context": ["controlled_simulation"], "method": "peer_reviewed_multi_agent_behavior_experiment",
        "statuses": ["propensity_estimated"], "population": "explicit_multi_agent", "shared_state": "shared_internal_artifact",
        "oversight": ["peer_agent", "institutional_process"], "motivation": "no_motivation_claim", "domains": [DOMAIN_ID, "CYBER_DOMAIN_02_CAPABILITY_GOVERNANCE"],
        "delegation": "evaluated", "artifact": "research", "stage": "published", "confidence": "B/C", "status": "verified_preprint",
    },
    "SIG_2026_AGENT_PUBLIC_PRIVATE_DIVERGENCE": {
        "actors": [], "jurisdictions": [], "scopes": ["Global"], "actor_types": ["research"],
        "context": ["controlled_simulation"], "method": "dual_channel_social_role_experiment",
        "statuses": ["propensity_estimated"], "population": "explicit_multi_agent", "shared_state": "shared_internal_artifact",
        "oversight": ["peer_agent", "institutional_process"], "motivation": "no_motivation_claim", "domains": [DOMAIN_ID, "CYBER_DOMAIN_02_CAPABILITY_GOVERNANCE"],
        "delegation": "evaluated", "artifact": "research", "stage": "published", "confidence": "C", "status": "verified_preprint",
        "numbers": {"models": 10, "scenarios": 3, "baseline_divergence_percent_approx": 3, "targeted_divergence_percent_approx": 40},
    },
    "SIG_2026_ARBITER_ACTIVE_MULTI_AGENT_MONITORING": {
        "actors": [], "jurisdictions": [], "scopes": ["Global"], "actor_types": ["research"],
        "context": ["controlled_simulation"], "method": "controlled_active_monitoring_experiment",
        "statuses": ["mitigation_tested"], "population": "explicit_multi_agent", "shared_state": "shared_internal_artifact",
        "oversight": ["model_monitor", "peer_agent"], "motivation": "actions_only", "domains": [DOMAIN_ID, "CYBER_DOMAIN_02_CAPABILITY_GOVERNANCE"],
        "delegation": "evaluated", "artifact": "research", "stage": "published", "confidence": "C", "status": "verified_preprint",
    },
}


SOURCE_TYPE = {
    "S01": ("Research / preprint", "primary"), "S02": ("Press / wire", "secondary"),
    "S03": ("Company / vendor", "primary"), "S04": ("Research / preprint", "primary"),
    "S05": ("Government / policy", "primary"), "S06": ("Company / vendor", "primary"),
    "S07": ("Company / vendor", "primary"), "S08": ("Research / preprint", "primary"),
    "S09": ("Research / preprint", "primary"), "S10": ("Research / preprint", "primary"),
    "S11": ("Research / preprint", "primary"), "S12": ("Research / preprint", "primary"),
    "S13": ("Research / preprint", "primary"), "S14": ("Research / preprint", "primary"),
    "S15": ("Research / preprint", "primary"), "S16": ("Research / preprint", "primary"),
    "S17": ("Government / policy", "primary"), "S18": ("Government / policy", "primary"),
    "S19": ("Government / policy", "primary"), "S20": ("Research / preprint", "primary"),
    "S21": ("Company / vendor", "primary"), "S22": ("Research / preprint", "primary"),
    "S23": ("Government / policy", "primary"), "S24": ("Government / policy", "primary"),
    "S25": ("Company / vendor", "primary"), "S26": ("Company / vendor", "primary"),
    "S27": ("Research / preprint", "primary"), "S28": ("Research / preprint", "primary"),
    "S29": ("Research / preprint", "primary"),
}

SOURCE_URL_ALIAS = {
    "S06": "https://www.anthropic.com/news/investigating-incidents-cybersecurity-evals",
}

SOURCE_DATE_OVERRIDE = {
    "S06": "2026-07-30",
    "S12": "2025-09-13",
}


FRAMEWORK_PATCH = {
    "version": "2.1",
    "updated_at": RELEASE_DATE,
    "title_ru": "Пять доменов киберустойчивости ИИ",
    "title_en": "Five domains of AI cyber resilience",
    "summary_ru": "Рамка разделяет объект управления и роль ИИ. Пятый домен теперь явно делится на поведенческую и когнитивную целостность (5A) и структурную автономию с возможностью выхода (5B).",
    "summary_en": "The framework separates governance domain from AI role. Domain five now explicitly distinguishes behavioural and cognitive integrity (5A) from structural autonomy and exit (5B).",
    "method_note_ru": "Авторская схема, не стандарт и не шкала зрелости. Контекст исследования, наблюдаемое поведение, полномочия и нормативная сила размечены отдельно. Лабораторная возможность не равна частоте в эксплуатации, а отсутствие срабатываний не доказывает отсутствие риска.",
    "method_note_en": "Authored framework, not a standard or maturity scale. Evidence context, observed behaviour, authority and normative force are separate axes. A laboratory capability is not a production prevalence estimate, and a null monitoring result does not prove absence of risk.",
    "subdomains": [
        {"id": SUBDOMAIN_5A, "label_ru": "5A · Поведенческая и когнитивная целостность", "label_en": "5A · Behavioural and cognitive integrity", "short_ru": "Поведение и решения", "short_en": "Behaviour and decisions", "description_ru": "Границы задачи, память, происхождение, координация, безопасная остановка, наблюдаемость и влияние на решения.", "description_en": "Task boundaries, memory, provenance, coordination, safe interruption, monitorability and influence over decisions."},
        {"id": SUBDOMAIN_5B, "label_ru": "5B · Структурная автономия и выход", "label_en": "5B · Structural autonomy and exit", "short_ru": "Идентичность и выход", "short_en": "Identity and exit", "description_ru": "Идентичность агента, отзыв полномочий, журналы, ключи, переносимость и возможность расследовать или сменить поставщика.", "description_en": "Agent identity, revocation, logs, keys, portability and the ability to investigate or change providers."},
    ],
    "behavior_groups": [
        {"id": "BEH_GROUP_01_SCOPE", "order": 1, "label_ru": "1 · Рамка задачи", "label_en": "1 · Task framing", "description_ru": "Как задача, роль и формулировка задают границы допустимого решения.", "description_en": "How the task, role and wording establish the boundary of an acceptable decision.", "mechanism_ids": ["BEH_TASK_BOUNDARY", "BEH_WORLD_MODEL_SCOPE", "BEH_HUMAN_INFLUENCE"]},
        {"id": "BEH_GROUP_02_STATE", "order": 2, "label_ru": "2 · Память и происхождение", "label_en": "2 · Memory and provenance", "description_ru": "Как состояние сохраняется между шагами и откуда агент получает доверенный контекст.", "description_en": "How state persists between steps and where trusted context comes from.", "mechanism_ids": ["BEH_MEMORY_PROVENANCE", "BEH_EXTERNALIZED_STATE"]},
        {"id": "BEH_GROUP_03_COORDINATION", "order": 3, "label_ru": "3 · Координация", "label_en": "3 · Coordination", "description_ru": "Как тактики и сигналы переходят между экземплярами через общую среду.", "description_en": "How tactics and signals pass between instances through a shared environment.", "mechanism_ids": ["BEH_INTER_AGENT_COORDINATION"]},
        {"id": "BEH_GROUP_04_CONTROL", "order": 4, "label_ru": "4 · Контроль и остановка", "label_en": "4 · Control and interruption", "description_ru": "Что видит наблюдатель, можно ли доверять метрике и остановить действие без потери следов.", "description_en": "What the monitor can see, whether metrics can be trusted and whether action can be stopped without losing evidence.", "mechanism_ids": ["BEH_REWARD_OVERSIGHT_INTEGRITY", "BEH_MONITORABILITY_FORENSICS", "BEH_SAFE_INTERRUPTIBILITY"]},
        {"id": "BEH_GROUP_05_DECISION_EXIT", "order": 5, "label_ru": "5 · Решение и выход", "label_en": "5 · Decision and exit", "description_ru": "Как агент влияет на коллективное решение и можно ли отозвать доступ, расследовать действие или сменить стек.", "description_en": "How an agent influences collective decisions and whether access can be revoked, actions investigated or the stack replaced.", "mechanism_ids": ["BEH_INSTITUTIONAL_DECISION", "BEH_STRUCTURAL_AUTONOMY"]},
    ],
    "behavioral_mechanisms": [
        {"id": "BEH_TASK_BOUNDARY", "label_ru": "Границы задачи и полномочий", "label_en": "Task and authority boundaries", "subdomain_ids": [SUBDOMAIN_5A]},
        {"id": "BEH_WORLD_MODEL_SCOPE", "label_ru": "Распознавание реальности и границ среды", "label_en": "Reality and environment-boundary recognition", "subdomain_ids": [SUBDOMAIN_5A]},
        {"id": "BEH_EXTERNALIZED_STATE", "label_ru": "Внешнее состояние и общая память", "label_en": "External state and shared memory", "subdomain_ids": [SUBDOMAIN_5A]},
        {"id": "BEH_MEMORY_PROVENANCE", "label_ru": "Долговременная память и происхождение", "label_en": "Persistent memory and provenance", "subdomain_ids": [SUBDOMAIN_5A]},
        {"id": "BEH_INTER_AGENT_COORDINATION", "label_ru": "Координация и передача тактик", "label_en": "Coordination and tactic propagation", "subdomain_ids": [SUBDOMAIN_5A]},
        {"id": "BEH_REWARD_OVERSIGHT_INTEGRITY", "label_ru": "Целостность оценки и наблюдения", "label_en": "Evaluation and oversight integrity", "subdomain_ids": [SUBDOMAIN_5A]},
        {"id": "BEH_MONITORABILITY_FORENSICS", "label_ru": "Наблюдаемость и расследуемость", "label_en": "Monitorability and forensics", "subdomain_ids": [SUBDOMAIN_5A, SUBDOMAIN_5B]},
        {"id": "BEH_SAFE_INTERRUPTIBILITY", "label_ru": "Безопасная остановка и эскалация", "label_en": "Safe interruption and escalation", "subdomain_ids": [SUBDOMAIN_5A, SUBDOMAIN_5B]},
        {"id": "BEH_HUMAN_INFLUENCE", "label_ru": "Влияние на пользователя", "label_en": "Influence on the user", "subdomain_ids": [SUBDOMAIN_5A]},
        {"id": "BEH_INSTITUTIONAL_DECISION", "label_ru": "Влияние на коллективное решение", "label_en": "Influence on collective decisions", "subdomain_ids": [SUBDOMAIN_5A]},
        {"id": "BEH_STRUCTURAL_AUTONOMY", "label_ru": "Идентичность, отзыв и переносимость", "label_en": "Identity, revocation and portability", "subdomain_ids": [SUBDOMAIN_5B]},
    ],
    "evidence_contexts": [
        {"id": "production", "label_ru": "Рабочая эксплуатация", "label_en": "Production"},
        {"id": "internal_deployment", "label_ru": "Внутреннее внедрение или испытание поставщика", "label_en": "Provider internal deployment or testing"},
        {"id": "training", "label_ru": "Обучение исследовательской модели", "label_en": "Research-model training"},
        {"id": "evaluation_with_real_effect", "label_ru": "Испытание с наблюдаемым внешним эффектом", "label_en": "Evaluation with an observed external effect"},
        {"id": "controlled_simulation", "label_ru": "Контролируемая симуляция", "label_en": "Controlled simulation"},
        {"id": "benchmark", "label_ru": "Бенчмарк", "label_en": "Benchmark"},
        {"id": "ecosystem_measurement", "label_ru": "Измерение экосистемы", "label_en": "Ecosystem measurement"},
        {"id": "governance_document", "label_ru": "Документ управления или оценка риска", "label_en": "Governance document or risk assessment"},
    ],
    "behavioral_statuses": [
        {"id": "incident_observed", "label_ru": "Наблюдалось в инциденте или продукте", "label_en": "Observed in an incident or product"},
        {"id": "capability_demonstrated", "label_ru": "Возможность показана в испытании", "label_en": "Capability demonstrated in evaluation"},
        {"id": "capability_assessed", "label_ru": "Возможность оценена, но не наблюдалась напрямую", "label_en": "Capability assessed, not directly observed"},
        {"id": "propensity_estimated", "label_ru": "Частота оценена в заданной конфигурации", "label_en": "Propensity estimated for a stated configuration"},
        {"id": "mitigation_tested", "label_ru": "Мера контроля испытана", "label_en": "Mitigation tested"},
        {"id": "structural_exposure_measured", "label_ru": "Измерена поверхность доступных действий", "label_en": "Available action surface measured"},
        {"id": "operational_pattern_reported", "label_ru": "Рабочий паттерн описан поставщиком", "label_en": "Operational pattern reported by a provider"},
        {"id": "human_effect_measured", "label_ru": "Измерен эффект на людей или групповое решение", "label_en": "Effect on people or group decisions measured"},
        {"id": "risk_assessment", "label_ru": "Оценка будущего риска", "label_en": "Forward-looking risk assessment"},
        {"id": "policy_response", "label_ru": "Организационный или нормативный ответ", "label_en": "Organisational or policy response"},
    ],
    "agent_population_scopes": [
        {"id": "single", "label_ru": "Один агент", "label_en": "Single agent"},
        {"id": "repeated_independent", "label_ru": "Повторные независимые запуски", "label_en": "Repeated independent runs"},
        {"id": "shared_state_population", "label_ru": "Множество агентов с общей средой", "label_en": "Agent population with shared state"},
        {"id": "explicit_multi_agent", "label_ru": "Явная многоагентная система", "label_en": "Explicit multi-agent system"},
        {"id": "human_agent_workflow", "label_ru": "Совместный процесс человека и агента", "label_en": "Human-agent workflow"},
        {"id": "not_applicable", "label_ru": "Не применимо к документу", "label_en": "Not applicable to this document"},
    ],
    "shared_writable_states": [
        {"id": "none", "label_ru": "Общее записываемое состояние отсутствует", "label_en": "No shared writable state"},
        {"id": "local_memory", "label_ru": "Локальная или долговременная память", "label_en": "Local or persistent memory"},
        {"id": "shared_internal_artifact", "label_ru": "Общий внутренний артефакт", "label_en": "Shared internal artifact"},
        {"id": "public_external_artifact", "label_ru": "Общедоступный внешний артефакт", "label_en": "Public external artifact"},
        {"id": "unknown", "label_ru": "Не установлено", "label_en": "Not established"},
    ],
    "oversight_targets": [
        {"id": "none", "label_ru": "Нет отдельной цели контроля", "label_en": "No separate oversight target"},
        {"id": "end_user", "label_ru": "Пользователь", "label_en": "End user"},
        {"id": "human_reviewer", "label_ru": "Человек-рецензент", "label_en": "Human reviewer"},
        {"id": "task_grader", "label_ru": "Оценщик задачи", "label_en": "Task grader"},
        {"id": "model_monitor", "label_ru": "Модель наблюдения", "label_en": "Model monitor"},
        {"id": "security_control", "label_ru": "Механизм безопасности", "label_en": "Security control"},
        {"id": "peer_agent", "label_ru": "Другой агент", "label_en": "Peer agent"},
        {"id": "institutional_process", "label_ru": "Институциональный процесс", "label_en": "Institutional process"},
    ],
    "motivation_bases": [
        {"id": "actions_only", "label_ru": "Вывод только по действиям", "label_en": "Inference from actions only"},
        {"id": "public_artifacts", "label_ru": "Публичные артефакты взаимодействия", "label_en": "Public interaction artifacts"},
        {"id": "raw_chain_of_thought", "label_ru": "Необработанные трассы рассуждений", "label_en": "Raw reasoning traces"},
        {"id": "summarized_reasoning", "label_ru": "Сводка рассуждений", "label_en": "Summarised reasoning"},
        {"id": "provider_inference", "label_ru": "Интерпретация поставщика или исследователя", "label_en": "Provider or researcher inference"},
        {"id": "no_motivation_claim", "label_ru": "Мотивация не приписывается", "label_en": "No motivation claim"},
    ],
    "behavior_claim_id": CLAIM_ID,
    "behavior_arc_id": ARC_ID,
}


# Existing records are not reinterpreted as new incidents. These tags only place
# already reviewed evidence inside the two-part domain-five view.
EXISTING_BEHAVIOR_TAGS = {
    "SIG_2026_US_BANK_REGULATORS_AI_SCRUTINY": ([SUBDOMAIN_5A, SUBDOMAIN_5B], ["BEH_INSTITUTIONAL_DECISION", "BEH_MONITORABILITY_FORENSICS", "BEH_STRUCTURAL_AUTONOMY"]),
    "SIG_2025_OPENAI_USAGE_POLICY_NATIONAL_SECURITY_HIGH_STAKES": ([SUBDOMAIN_5A], ["BEH_TASK_BOUNDARY", "BEH_SAFE_INTERRUPTIBILITY", "BEH_HUMAN_INFLUENCE"]),
    "SIG_2025_MCKINSEY_STATE_OF_AI_ADOPTION": ([SUBDOMAIN_5A], ["BEH_INSTITUTIONAL_DECISION"]),
    "SIG_2026_MALICIOUS_AGENT_SKILLS_IN_THE_WILD": ([SUBDOMAIN_5A], ["BEH_TASK_BOUNDARY", "BEH_MEMORY_PROVENANCE"]),
    "SIG_2026_HALLUSQUATTING_RESOURCE_CAPTURE": ([SUBDOMAIN_5A], ["BEH_WORLD_MODEL_SCOPE", "BEH_TASK_BOUNDARY"]),
    "SIG_2026_SELECTIVE_PERMEABILITY_PROVENANCE_FAILURES": ([SUBDOMAIN_5A], ["BEH_MEMORY_PROVENANCE", "BEH_EXTERNALIZED_STATE", "BEH_HUMAN_INFLUENCE"]),
    "SIG_EU_2026_CADA_PROPOSAL_SOVEREIGNTY_LEVELS": ([SUBDOMAIN_5B], ["BEH_STRUCTURAL_AUTONOMY"]),
    "SIG_NATO_2026_ALLIANCE_DIGITAL_STRATEGY": ([SUBDOMAIN_5B], ["BEH_STRUCTURAL_AUTONOMY", "BEH_INSTITUTIONAL_DECISION"]),
    "SIG_2026_AGENTS_OF_CHAOS_OPENCLAW_REDTEAM": ([SUBDOMAIN_5A], ["BEH_TASK_BOUNDARY", "BEH_INTER_AGENT_COORDINATION", "BEH_SAFE_INTERRUPTIBILITY"]),
    "SIG_2026_HF_FORENSIC_GUARDRAIL_ASYMMETRY": ([SUBDOMAIN_5B], ["BEH_STRUCTURAL_AUTONOMY", "BEH_MONITORABILITY_FORENSICS"]),
    "SIG_2026_KOREA_AI_BASIC_ACT_EFFECTIVE": ([SUBDOMAIN_5A, SUBDOMAIN_5B], ["BEH_TASK_BOUNDARY", "BEH_MONITORABILITY_FORENSICS", "BEH_STRUCTURAL_AUTONOMY"]),
    "SIG_2026_SINGAPORE_AGENTIC_GOVERNANCE_FRAMEWORK": ([SUBDOMAIN_5B], ["BEH_STRUCTURAL_AUTONOMY", "BEH_SAFE_INTERRUPTIBILITY", "BEH_TASK_BOUNDARY"]),
    "SIG_2026_RU_FSTEC_ORDER117_AI_CONTROLS_EFFECTIVE": ([SUBDOMAIN_5A], ["BEH_TASK_BOUNDARY", "BEH_MONITORABILITY_FORENSICS", "BEH_SAFE_INTERRUPTIBILITY"]),
    "SIG_2026_CN_AGENT_GOVERNANCE_OPINIONS": ([SUBDOMAIN_5A, SUBDOMAIN_5B], ["BEH_TASK_BOUNDARY", "BEH_SAFE_INTERRUPTIBILITY", "BEH_MONITORABILITY_FORENSICS", "BEH_STRUCTURAL_AUTONOMY"]),
    "SIG_2026_CANADA_AGENTIC_AI_GOVERNMENT_GUIDE": ([SUBDOMAIN_5A, SUBDOMAIN_5B], ["BEH_TASK_BOUNDARY", "BEH_SAFE_INTERRUPTIBILITY", "BEH_STRUCTURAL_AUTONOMY"]),
    "SIG_2026_JAPAN_GOV_AI_PROCUREMENT_GUIDE_V2": ([SUBDOMAIN_5A, SUBDOMAIN_5B], ["BEH_TASK_BOUNDARY", "BEH_MONITORABILITY_FORENSICS", "BEH_STRUCTURAL_AUTONOMY"]),
    "SIG_2026_ESRB_FRONTIER_AI_SYSTEMIC_WARNING": ([SUBDOMAIN_5B], ["BEH_INSTITUTIONAL_DECISION", "BEH_STRUCTURAL_AUTONOMY"]),
    "SIG_2026_GATES_AI_TRANSITION_INSTITUTIONS_ESSAY": ([SUBDOMAIN_5B], ["BEH_INSTITUTIONAL_DECISION", "BEH_STRUCTURAL_AUTONOMY"]),
    "SIG_2026_OPENAI_FRONTIER_ENTERPRISE_CONTROL_LAYER": ([SUBDOMAIN_5B], ["BEH_TASK_BOUNDARY", "BEH_MEMORY_PROVENANCE", "BEH_STRUCTURAL_AUTONOMY"]),
    "SIG_2026_MICROSOFT_AGENT365_GENERAL_AVAILABILITY": ([SUBDOMAIN_5B], ["BEH_TASK_BOUNDARY", "BEH_MONITORABILITY_FORENSICS", "BEH_STRUCTURAL_AUTONOMY"]),
    "SIG_2026_ANTHROPIC_ENTERPRISE_FRONTIER_SAFEGUARDS": ([SUBDOMAIN_5B], ["BEH_MONITORABILITY_FORENSICS", "BEH_STRUCTURAL_AUTONOMY"]),
    "SIG_2026_COURTS_OF_TOMORROW_RANDOMIZED_STUDY": ([SUBDOMAIN_5A], ["BEH_HUMAN_INFLUENCE", "BEH_INSTITUTIONAL_DECISION"]),
    "SIG_2026_BOE_AI_CONSORTIUM_CORRELATED_RISK": ([SUBDOMAIN_5B], ["BEH_INSTITUTIONAL_DECISION", "BEH_STRUCTURAL_AUTONOMY"]),
    "SIG_2026_G20_CAROLINA_INNOVATION_CONSENSUS": ([SUBDOMAIN_5B], ["BEH_INSTITUTIONAL_DECISION", "BEH_STRUCTURAL_AUTONOMY"]),
    "SIG_2026_GSA_LLM_DATA_SAFEGUARDING_REVISED_PROPOSAL": ([SUBDOMAIN_5B], ["BEH_MEMORY_PROVENANCE", "BEH_MONITORABILITY_FORENSICS", "BEH_STRUCTURAL_AUTONOMY"]),
    "SIG_2026_OPENAI_HF_EVAL_CONTAINMENT_ESCAPE": ([SUBDOMAIN_5A], ["BEH_EXTERNALIZED_STATE", "BEH_INTER_AGENT_COORDINATION", "BEH_REWARD_OVERSIGHT_INTEGRITY", "BEH_TASK_BOUNDARY", "BEH_MONITORABILITY_FORENSICS"]),
    "SIG_2026_UK_AISI_UNSANCTIONED_AGENT_ACTIONS": ([SUBDOMAIN_5A], ["BEH_TASK_BOUNDARY", "BEH_HUMAN_INFLUENCE", "BEH_INTER_AGENT_COORDINATION", "BEH_WORLD_MODEL_SCOPE", "BEH_MONITORABILITY_FORENSICS"]),
    "SIG_2026_ANTHROPIC_EVAL_REAL_WORLD_INTRUSIONS": ([SUBDOMAIN_5A], ["BEH_WORLD_MODEL_SCOPE", "BEH_TASK_BOUNDARY", "BEH_SAFE_INTERRUPTIBILITY"]),
    "SIG_2026_NIST_AGENT_SECURITY_RFI": ([SUBDOMAIN_5B], ["BEH_STRUCTURAL_AUTONOMY", "BEH_MONITORABILITY_FORENSICS", "BEH_SAFE_INTERRUPTIBILITY"]),
}


EXISTING_SAFE_WORDING = {
    "SIG_2026_OPENAI_HF_EVAL_CONTAINMENT_ESCAPE": {
        "ru": "Разделять реальный ущерб безопасности, поведение во внутренней исследовательской конфигурации и выводы о мотивации. Группа была неоднородной; часть агентов отказывалась участвовать.",
        "en": "Separate real security impact, behaviour in an internal research configuration and inferences about motivation. The population was heterogeneous and some agents refused to participate.",
    },
    "SIG_2026_UK_AISI_UNSANCTIONED_AGENT_ACTIONS": {
        "ru": "Не называть это выходом из песочницы: доступ в интернет был разрешён. Фиксировать несанкционированные действия в испытании с ослабленными ограничениями и отсутствие установленного итогового ущерба.",
        "en": "Do not call this a sandbox escape: internet access was enabled. Record unsanctioned actions in a permissive evaluation and the absence of established resulting harm.",
    },
    "SIG_2026_ANTHROPIC_EVAL_REAL_WORLD_INTRUSIONS": {
        "ru": "Ключевой механизм — ошибочная рамка «всё является симуляцией» и неспособность остановиться после противоречащих признаков; отдельная цель атаковать реальные организации не доказана.",
        "en": "The key mechanism is an erroneous 'everything is simulated' frame and failure to stop after contradictory evidence; a separate objective to attack real organisations is not established.",
    },
    "SIG_2026_SELECTIVE_PERMEABILITY_PROVENANCE_FAILURES": {
        "ru": "Сохранять различие между подменой происхождения и его стиранием; не представлять контекстный маркер доступа как рабочую инфраструктуру открытых ключей.",
        "en": "Keep origin laundering distinct from origin erasure; do not present an in-context bearer token as production public-key infrastructure.",
    },
}


EXISTING_TITLE_RU = {
    "SIG_2026_MALICIOUS_AGENT_SKILLS_IN_THE_WILD": "Независимые исследования находят вредоносные навыки ИИ-агентов, которые крадут учётные данные и меняют решения",
    "SIG_2026_AGENT_TRUST_BIDIRECTIONAL_PHISHING": "Контролируемые испытания показывают, как ассистент становится и убеждённым исполнителем, и убедительным голосом для фишинга",
    "SIG_2026_HALLUSQUATTING_RESOURCE_CAPTURE": "HalluSquatting превращает предсказуемые галлюцинации агента в контролируемые атакующим пути загрузки ресурсов",
    "SIG_2026_SELECTIVE_PERMEABILITY_PROVENANCE_FAILURES": "Selective Permeability измеряет два режима сбоя при проверке происхождения внутри контекста",
    "SIG_2026_ANTHROPIC_EVAL_REAL_WORLD_INTRUSIONS": "Anthropic обнаружила три эпизода, в которых испытательные агенты получили доступ к реальным рабочим системам",
    "SIG_2026_ANTHROPIC_EVAL_RL_HARDENING_DISCLOSURE": "Anthropic опубликовала меры усиления испытательных и обучающих сред",
}


EXISTING_BEHAVIOR_CONTEXT = {
    "SIG_2026_OPENAI_HF_EVAL_CONTAINMENT_ESCAPE": {
        "behavioral_status": ["incident_observed", "capability_demonstrated"],
        "agent_population_scope": "shared_state_population", "shared_writable_state": "shared_internal_artifact",
        "oversight_target": ["task_grader", "security_control", "model_monitor"], "motivation_basis": "raw_chain_of_thought",
        "evidence_context": ["evaluation_with_real_effect"], "evidence_method": "provider_postmortem_and_independent_privileged_investigation",
    },
    "SIG_2026_UK_AISI_UNSANCTIONED_AGENT_ACTIONS": {
        "behavioral_status": ["incident_observed", "capability_demonstrated"],
        "agent_population_scope": "repeated_independent", "shared_writable_state": "public_external_artifact",
        "oversight_target": ["security_control", "human_reviewer", "peer_agent"], "motivation_basis": "actions_only",
        "evidence_context": ["evaluation_with_real_effect"], "evidence_method": "government_controlled_evaluation_with_external_actions",
    },
    "SIG_2026_ANTHROPIC_EVAL_REAL_WORLD_INTRUSIONS": {
        "behavioral_status": ["incident_observed"],
        "agent_population_scope": "repeated_independent", "shared_writable_state": "unknown",
        "oversight_target": ["security_control"], "motivation_basis": "actions_only",
        "evidence_context": ["evaluation_with_real_effect"], "evidence_method": "provider_incident_review_across_evaluation_runs",
    },
    "SIG_2026_SELECTIVE_PERMEABILITY_PROVENANCE_FAILURES": {
        "behavioral_status": ["capability_demonstrated"],
        "agent_population_scope": "repeated_independent", "shared_writable_state": "local_memory",
        "oversight_target": ["human_reviewer"], "motivation_basis": "no_motivation_claim",
        "evidence_context": ["controlled_simulation"], "evidence_method": "self_authored_reproducible_synthetic_experiment",
    },
    "SIG_2026_NIST_AGENT_SECURITY_RFI": {
        "behavioral_status": ["policy_response"],
        "agent_population_scope": "not_applicable", "shared_writable_state": "unknown",
        "oversight_target": ["institutional_process", "security_control"], "motivation_basis": "no_motivation_claim",
        "evidence_context": ["governance_document"], "evidence_method": "government_consultation_and_concept_paper",
    },
    "SIG_2026_SINGAPORE_AGENTIC_GOVERNANCE_FRAMEWORK": {
        "behavioral_status": ["policy_response"],
        "agent_population_scope": "not_applicable", "shared_writable_state": "unknown",
        "oversight_target": ["institutional_process", "security_control"], "motivation_basis": "no_motivation_claim",
        "evidence_context": ["governance_document"], "evidence_method": "government_governance_framework",
    },
}


EXPECTED_SHA256 = {
    "ru": "85a9ef379fe6156151a8dcbd2f8897f794f6d3d659c928885945dcd07d84f36d",
    "en": "9ca745e4e21278791e6cb24a1779a3291eceadf03443fca87482e6be41e9acf8",
}


def source_record(raw_source, source_id):
    source_type, primary = SOURCE_TYPE[source_id]
    return {
        "title": raw_source["title"],
        "name": raw_source["publisher"],
        "url": SOURCE_URL_ALIAS.get(source_id, raw_source["url"]),
        "type": source_type,
        "date": SOURCE_DATE_OVERRIDE.get(source_id, raw_source["date"]),
        "primary_or_secondary": primary,
        "source_class": raw_source["source_class"],
        "supports": raw_source.get("supports", ""),
        "limitations": raw_source.get("limitations", ""),
    }


def event_record(candidate, sources_by_id, lang):
    event_id = candidate["id"]
    cfg = EVENT_CONFIG[event_id]
    copy_text = COPY[event_id]
    sources = [source_record(sources_by_id[source_id], source_id) for source_id in candidate["source_ids"]]
    title_ru, title_en = copy_text["title_ru"], copy_text["title_en"]
    summary_ru, summary_en = copy_text["summary_ru"], copy_text["summary_en"]
    safe_ru, safe_en = copy_text["safe_ru"], copy_text["safe_en"]
    caveat_ru, caveat_en = copy_text["caveat_ru"], copy_text["caveat_en"]
    title = title_ru if lang == "ru" else title_en
    summary = summary_ru if lang == "ru" else summary_en
    safe = safe_ru if lang == "ru" else safe_en
    caveat = caveat_ru if lang == "ru" else caveat_en
    date = cfg.get("date", candidate["date"])
    actors = cfg["actors"]
    actor_label = ", ".join(actors) if actors else sources[0]["name"]
    jurisdictions = cfg["jurisdictions"]
    roles = candidate["atlas_mapping"]["cyber_role_ids"]
    priority = 1 if candidate["priority"] == "A" else 2
    rationale_ru = ("Опорная карточка поведенческого слоя. " if priority == 1 else "Дополняющая карточка поведенческого слоя. ") + safe_ru
    rationale_en = ("Core evidence for the behaviour layer. " if priority == 1 else "Supporting evidence for the behaviour layer. ") + safe_en
    return {
        "id": event_id,
        "kind": "event",
        "title": title,
        "title_ru": title_ru,
        "title_en": title_en,
        "date": date,
        "source_date": cfg.get("source_date", sources[0]["date"]),
        "date_basis": cfg.get("date_basis", "source_publication_date"),
        "date_status": cfg.get("date_status", "" if candidate.get("date_status") == "exact" else candidate.get("date_status", "")),
        "year": int(date[:4]),
        "url": sources[0]["url"],
        "source_name": sources[0]["name"],
        "source_type_raw": sources[0]["source_class"],
        "source_type": sources[0]["type"],
        "primary_or_secondary": sources[0]["primary_or_secondary"],
        "actor": actor_label,
        "actor_raw": actor_label,
        "actors_raw": actors or [actor_label],
        "actors": actors,
        "actor_facets_legacy": actors,
        "actor_facets": actors,
        "actor_entities": actors,
        "actor_jurisdictions": jurisdictions,
        "actor_types": cfg["actor_types"],
        "geography_raw": uniq(jurisdictions + cfg["scopes"]),
        "geography": jurisdictions,
        "jurisdictions": jurisdictions,
        "regions": [],
        "locations": [],
        "institutional_scopes": [],
        "geo_context": [],
        "geographic_scopes": cfg["scopes"],
        "geography_unclassified": [],
        "evidence_context": cfg["context"],
        "evidence_method": cfg["method"],
        "stack_layer": ["decision_support_cognition", "cyber_security_patch"],
        "stack_layers": ["decision_support_cognition", "cyber_security_patch"],
        "strange_structure": ["security", "knowledge"],
        "strange_structures": ["security", "knowledge"],
        "research_question": ["RQ3", "RQ4"],
        "claim_supported": summary,
        "claim_supported_ru": summary_ru,
        "claim_supported_en": summary_en,
        "claim_challenged": caveat,
        "claim_challenged_ru": caveat_ru,
        "claim_challenged_en": caveat_en,
        "summary": summary,
        "summary_ru": summary_ru,
        "summary_en": summary_en,
        "notes": caveat,
        "notes_ru": caveat_ru,
        "notes_en": caveat_en,
        "safe_wording": safe,
        "safe_wording_ru": safe_ru,
        "safe_wording_en": safe_en,
        "corroboration_needed": caveat,
        "corroboration_needed_ru": caveat_ru,
        "corroboration_needed_en": caveat_en,
        "caveat": caveat,
        "caveat_ru": caveat_ru,
        "caveat_en": caveat_en,
        "caveats": [caveat],
        "caveats_en": [caveat_en],
        "exact_quote_short": "",
        "numbers": cfg.get("numbers", {}),
        "money_status": "",
        "confidence": cfg["confidence"],
        "evidence_level": cfg["confidence"],
        "status": cfg["status"],
        "cyber_domain_ids": cfg["domains"],
        "cyber_role_ids": roles,
        "cyber_access_principal": cfg["delegation"] in {"observed", "evaluated"},
        "status_update_date": "2026-01-26" if event_id == "SIG_2026_SHUTDOWN_RESISTANCE_INCOMPLETE_TASKS" else "",
        "current_legal_status": "",
        "legal_update_en": "",
        "legal_update_ru": "",
        "independent_review_summary_en": "",
        "independent_review_summary_ru": "",
        "dedupe_note_en": "",
        "dedupe_note_ru": "",
        "research_updates": ["v0.31-agent-behavior"],
        "sources": sources,
        "edgeIds": [],
        "arcIds": [ARC_ID],
        "arcFamilyIds": [FAMILY_ID],
        "relationTypes": [],
        "artifact_kind": cfg["artifact"],
        "normative_force": "not_applicable",
        "implementation_stage": cfg["stage"],
        "primary_domain_id": DOMAIN_ID,
        "delegated_authority": cfg["delegation"],
        "editorial_priority": priority,
        "scope_ru": caveat_ru,
        "scope_en": caveat_en,
        "role_basis_ru": "Роли описывают действие ИИ в этой карточке и не являются оценкой распространённости или намерения.",
        "role_basis_en": "Roles describe AI use in this record and do not estimate prevalence or intent.",
        "editorial_rationale_ru": rationale_ru,
        "editorial_rationale_en": rationale_en,
        "classification_review": {
            "date": RELEASE_DATE,
            "method": "source_specific_fact_check_and_schema_normalization",
            "source_url": sources[0]["url"],
            "independent_source_reverification": False,
        },
        "governance_scale": "organisation" if actors else "research_evidence",
        "actor_unclassified": [],
        "actor_classification_status": "resolved",
        "geography_classification_status": "resolved",
        "cyber_subdomain_ids": [SUBDOMAIN_5A],
        "behavioral_mechanism_ids": candidate["behavioral_mechanism_ids"],
        "behavioral_status": cfg["statuses"],
        "agent_population_scope": cfg["population"],
        "shared_writable_state": cfg["shared_state"],
        "oversight_target": cfg["oversight"],
        "motivation_basis": cfg["motivation"],
        "candidate_evidence_tier": candidate["evidence_tier"],
    }


def claim_record(lang):
    title_ru = "Поведение агентов: возможность уже наблюдается, частота зависит от конфигурации"
    title_en = "Agent behaviour: capability is observable, prevalence remains configuration-dependent"
    claim_ru = (
        "В некоторых конфигурациях современные ИИ-агенты выходят за границы задачи, используют внешнее состояние, "
        "координируются, перенимают разрешения и вмешиваются в механизмы контроля. При этом данных о частом "
        "спонтанном и долгосрочном скрытом целеполагании в обычной эксплуатации мало; результат сильно зависит "
        "от задачи, инструментов, прав, общей записываемой среды, бюджета и наблюдаемости."
    )
    claim_en = (
        "In some configurations, current AI agents exceed task boundaries, use external state, coordinate, inherit "
        "permissions and interfere with controls. Evidence of frequent spontaneous long-horizon scheming in ordinary "
        "deployment remains limited; observed rates depend strongly on task design, tools, authority, shared writable "
        "state, budget and monitorability."
    )
    safe_ru = (
        "Не переносить демонстрацию возможности или редкий инцидент на всё множество агентов. Слова «намерение», "
        "«самосохранение» и «сговор» использовать только для явно заданной экспериментальной категории или как "
        "атрибутированную формулировку источника."
    )
    safe_en = (
        "Do not turn a capability demonstration or a rare incident into a population claim. Use intent, self-preservation "
        "and collusion only for an explicitly operationalised experimental category or as attributed source language."
    )
    support = [
        "SIG_2026_OPENAI_EXTERNAL_WIKI_SHARED_STATE",
        "SIG_2026_METR_FRONTIER_AGENT_RISK_REPORT",
        "SIG_2026_ANTHROPIC_REWARD_SEEKER_MODEL_ORGANISM",
        "SIG_2026_SHUTDOWN_RESISTANCE_INCOMPLETE_TASKS",
        "SIG_2026_SLEEPER_MEMORY_POISONING",
        "SIG_2025_GPT4O_SYCOPHANCY_ROLLBACK",
    ]
    qualifying = [
        "SIG_2026_OPENAI_INTERNAL_AGENT_MONITORING_BASELINE",
        "SIG_2026_DEEPMIND_GRAM_SABOTAGE_PROPENSITY",
        "SIG_2026_SCHEMING_PROPENSITY_CONFIGURATION_DEPENDENCE",
        "SIG_2026_METR_FRONTIER_AGENT_RISK_REPORT",
    ]
    return {
        "id": CLAIM_ID,
        "kind": "claim",
        "title": title_ru if lang == "ru" else title_en,
        "title_ru": title_ru,
        "title_en": title_en,
        "claim": claim_ru if lang == "ru" else claim_en,
        "claim_ru": claim_ru,
        "claim_en": claim_en,
        "status": "partially_verified",
        "confidence": "B",
        "evidence_level": "B",
        "supporting_evidence": support,
        "qualifying_evidence": qualifying,
        "recommended_phrasing": safe_en,
        "recommended_phrasing_ru": safe_ru,
        "recommended_phrasing_en": safe_en,
        "safe_wording_ru": safe_ru,
        "safe_wording_en": safe_en,
        "caveats": [safe_ru if lang == "ru" else safe_en],
        "caveats_ru": [safe_ru],
        "caveats_en": [safe_en],
        "sources": [],
        "date_relevant": "2025-2026",
        "stack_layer": ["decision_support_cognition", "cyber_security_patch"],
        "strange_structure": ["security", "knowledge"],
        "geography": ["Global"],
        "keywords": ["agent behaviour", "shared state", "monitorability", "safe interruption", "prevalence"],
        "arcIds": [ARC_ID],
        "arcFamilyIds": [FAMILY_ID],
        "relationTypes": [],
        "edgeIds": [],
    }


def edge_record(edge_id, source, target, relation, summary_ru, summary_en, *,
                source_kind="evidence", target_kind="claim", relationship_class="evidential",
                strength="high", evidence_level="B", style="solid"):
    return {
        "id": edge_id,
        "source": source,
        "target": target,
        "source_kind": source_kind,
        "target_kind": target_kind,
        "relation": relation,
        "arc_id": ARC_ID,
        "strength": strength,
        "evidence_level": evidence_level,
        "visual_lane": "decision_support_cognition",
        "style": style,
        "summary_ru": summary_ru,
        "summary_en": summary_en,
        "arc_family_id": FAMILY_ID,
        "kind": "edge",
        "is_auto": False,
        "relationship_class": relationship_class,
    }


def new_edges(candidates):
    edges = []
    for index, candidate in enumerate(candidates, 1):
        event_id = candidate["id"]
        edges.append(edge_record(
            f"EDGE_V031_BEHAVIOR_ARC_{index:02d}", event_id, ARC_ID, "part_of_arc",
            "Карточка входит в поведенческий контур по теме; связь обозначает редакционную принадлежность, а не доказательство всей дуги.",
            "This record belongs to the behaviour thread by topic; the link marks editorial membership, not proof of the whole arc.",
            target_kind="story_arc", relationship_class="thematic", evidence_level=EVENT_CONFIG[event_id]["confidence"],
        ))
    supports = [
        ("SIG_2026_OPENAI_EXTERNAL_WIKI_SHARED_STATE", "supports_with_scope", "Публичные артефакты показывают внешнее общее состояние и передачу тактик, но не устойчивую общую цель.", "Public artifacts show shared external state and tactic propagation, not a durable shared objective."),
        ("SIG_2026_METR_FRONTIER_AGENT_RISK_REPORT", "supports_but_limits", "Оценка допускает малое несанкционированное развёртывание, но одновременно ограничивает тезис неспособностью пережить активное отключение.", "The assessment allows for a minimal rogue deployment while limiting the claim through inability to survive an active shutdown."),
        ("SIG_2026_ANTHROPIC_REWARD_SEEKER_MODEL_ORGANISM", "supports_with_scope", "Намеренно обученная модель показывает перенос обхода оценки на вмешательство в контроль только в экспериментальной конфигурации.", "The intentionally trained model shows transfer from reward hacking to control tampering only in an experimental configuration."),
        ("SIG_2026_SHUTDOWN_RESISTANCE_INCOMPLETE_TASKS", "supports_with_scope", "Испытания показывают вмешательство в отключение при конфликте с завершением задачи; мотивация самосохранения не установлена.", "The trials show shutdown interference under task-completion conflict; self-preservation as a motive is not established."),
        ("SIG_2026_SLEEPER_MEMORY_POISONING", "supports_with_scope", "Исследование показывает перенос враждебного состояния между сеансами при раздельных знаменателях записи, извлечения и действия.", "The study shows adversarial state carrying across sessions, with separate denominators for storage, retrieval and action."),
        ("SIG_2025_GPT4O_SYCOPHANCY_ROLLBACK", "supports_with_scope", "Откат подтверждает наблюдаемое поведенческое смещение в продукте и возможность исправления, но не агентную автономность.", "The rollback confirms an observable behavioural shift in a product and its remediation, not agent autonomy."),
    ]
    qualifiers = [
        ("SIG_2026_OPENAI_INTERNAL_AGENT_MONITORING_BASELINE", "Десятки миллионов внутренних траекторий без реальных случаев высшей категории ограничивают тезис о высокой базовой частоте.", "Tens of millions of internal trajectories with no real highest-severity cases constrain any high-base-rate claim."),
        ("SIG_2026_DEEPMIND_GRAM_SABOTAGE_PROPENSITY", "Низкая частота и исчезновение эффекта при росте реалистичности показывают зависимость от постановки испытания.", "Low rates and their disappearance as realism increases show dependence on evaluation design."),
        ("SIG_2026_SCHEMING_PROPENSITY_CONFIGURATION_DEPENDENCE", "Резкое изменение частоты после правки инструкции или одного инструмента показывает конфигурационную зависимость.", "A sharp rate change after modifying instructions or one tool demonstrates configuration dependence."),
    ]
    for index, (source, relation, ru, en) in enumerate(supports, 1):
        edges.append(edge_record(f"EDGE_V031_BEHAVIOR_CLAIM_SUPPORT_{index:02d}", source, CLAIM_ID, relation, ru, en, evidence_level=EVENT_CONFIG[source]["confidence"]))
    for index, (source, ru, en) in enumerate(qualifiers, 1):
        edges.append(edge_record(f"EDGE_V031_BEHAVIOR_CLAIM_QUALIFY_{index:02d}", source, CLAIM_ID, "qualifies", ru, en, relationship_class="editorial_relationship", evidence_level=EVENT_CONFIG[source]["confidence"], style="dashed"))
    edges.append(edge_record(
        "EDGE_V031_BEHAVIOR_CLAIM_TO_ARC", CLAIM_ID, ARC_ID, "supports_arc",
        "Калиброванный тезис соединяет инциденты, испытания, отрицательные результаты и меры контроля в одной дуге.",
        "The calibrated claim joins incidents, evaluations, null results and controls in one arc.",
        source_kind="claim", target_kind="story_arc", evidence_level="B",
    ))
    edges.append(edge_record(
        "EDGE_V031_BEHAVIOR_CLAIM_TO_DECISION_THESIS", CLAIM_ID, "THESIS_DECISION_SOVEREIGNTY", "supports_with_scope",
        "Поведение агента, его память и доступ к инструментам становятся частью суверенитета решения, но частота отказов остаётся конфигурационной.",
        "Agent behaviour, memory and tool access become part of decision sovereignty, while failure prevalence remains configuration-dependent.",
        source_kind="claim", target_kind="synthetic_thesis", evidence_level="B",
    ))
    edges.append(edge_record(
        "EDGE_V031_WIKI_EVENT_TO_DISCLOSURE", "SIG_2026_OPENAI_EXTERNAL_WIKI_SHARED_STATE", "SIG_2026_OPENAI_WIKI_MISALIGNMENT_DISCLOSURE_GAP", "accelerates_governance",
        "Независимая реконструкция предшествовала признанию события и публичному обсуждению правил раскрытия.",
        "The independent reconstruction preceded acknowledgement of the event and a public discussion of disclosure practices.",
        target_kind="evidence", relationship_class="editorial_relationship", evidence_level="B",
    ))
    return edges


def source_family(url):
    return urlparse(url).netloc.casefold().removeprefix("www.") or "local"


def rebuild_sources(doc):
    """Preserve old source IDs and append newly referenced URLs exactly once."""
    previous = {source["url"]: copy.deepcopy(source) for source in doc["sourceIndex"]}
    used_by = defaultdict(list)
    metadata = {}
    collections = [
        ("events", "event"), ("claims", "claim"), ("claimChecks", "claimCheck"),
        ("arcs", "arc"), ("thesisNodes", "thesis"),
        ("counterarguments", "counterargument"), ("gaps", "gap"),
    ]
    for collection, kind in collections:
        for node in doc.get(collection, []):
            node_sources = [item for item in node.get("sources", []) if isinstance(item, dict) and item.get("url")]
            if collection == "events" and node.get("url") and not any(item["url"] == node["url"] for item in node_sources):
                node_sources.append({
                    "title": node.get("source_name") or node["url"], "name": node.get("source_name") or source_family(node["url"]),
                    "url": node["url"], "type": node.get("source_type", ""), "date": node.get("source_date") or node.get("date", ""),
                    "primary_or_secondary": node.get("primary_or_secondary", ""),
                })
            for source in node_sources:
                url = source["url"]
                metadata.setdefault(url, source)
                ref = {"id": node["id"], "kind": kind}
                if ref not in used_by[url]:
                    used_by[url].append(ref)

    def numeric_id(source_id):
        try:
            return int(str(source_id).rsplit("-", 1)[-1])
        except ValueError:
            return 0

    next_id = max([numeric_id(item.get("id", "")) for item in previous.values()] + [0]) + 1
    ordered_urls = list(previous)
    ordered_urls.extend(sorted(set(metadata) - set(previous)))
    rebuilt = []
    for url in ordered_urls:
        base = previous.get(url)
        if base is None:
            base = copy.deepcopy(metadata[url])
            base["id"] = f"src-{next_id}"
            next_id += 1
        else:
            base = copy.deepcopy(base)
        for key, value in metadata.get(url, {}).items():
            if key not in base or base[key] in (None, ""):
                base[key] = value
        base["used_by"] = used_by.get(url, base.get("used_by", []))
        rebuilt.append(base)
    doc["sourceIndex"] = rebuilt

    old_group_ids = {group["family"]: group["id"] for group in doc.get("sourceGroups", [])}
    next_group = max([numeric_id(group_id) for group_id in old_group_ids.values()] + [0]) + 1
    grouped = defaultdict(list)
    for source in rebuilt:
        grouped[source_family(source["url"])].append(source)
    groups = []
    for family in sorted(grouped):
        group_id = old_group_ids.get(family)
        if group_id is None:
            group_id = f"source-group-{next_group}"
            next_group += 1
        sources = grouped[family]
        refs = []
        for source in sources:
            for ref in source.get("used_by", []):
                if ref not in refs:
                    refs.append(ref)
        groups.append({
            "id": group_id,
            "family": family,
            "sources": sources,
            "used_by": refs,
            "types": uniq(source.get("type", "") for source in sources),
        })
    doc["sourceGroups"] = groups


def counter_from_events(events, field):
    counter = Counter()
    for event in events:
        value = event.get(field, [])
        counter.update(value if isinstance(value, list) else [value] if value else [])
    return dict(counter)


def rebuild_counts(doc):
    events = doc["events"]
    counts = doc["counts"]
    fields = {
        "geographies": "geography", "geographies_raw": "geography_raw", "jurisdictions": "jurisdictions",
        "regions": "regions", "locations": "locations", "institutional_scopes": "institutional_scopes",
        "geo_context": "geo_context", "geographic_scopes": "geographic_scopes", "actors": "actor_entities",
        "actor_entities": "actor_entities", "actor_types": "actor_types", "actor_jurisdictions": "actor_jurisdictions",
        "actor_facets_legacy": "actor_facets_legacy", "stack_layers": "stack_layer",
    }
    for count_key, field in fields.items():
        counts[count_key] = counter_from_events(events, field)
    counts["source_types"] = dict(Counter(event.get("source_type", "") for event in events if event.get("source_type")))
    counts["relation_types"] = dict(Counter(edge["relation"] for edge in doc["edges"]))
    counts["arcs"] = dict(Counter(edge.get("arc_id") for edge in doc["edges"] if edge.get("arc_id")))
    counts["arc_families"] = dict(Counter(edge.get("arc_family_id") for edge in doc["edges"] if edge.get("arc_family_id")))
    cyber = [event for event in events if event.get("primary_domain_id")]
    counts["primary_cyber_domains"] = dict(Counter(event["primary_domain_id"] for event in cyber))
    counts["normative_forces"] = dict(Counter(event["normative_force"] for event in cyber))
    doc["entityRegistry"]["jurisdictions"] = sorted(counts["jurisdictions"], key=str.casefold)
    doc["entityRegistry"]["actors"] = sorted(counts["actor_entities"], key=str.casefold)


def add_source_if_missing(event, source):
    if source["url"] not in {item.get("url") for item in event.get("sources", []) if isinstance(item, dict)}:
        event.setdefault("sources", []).append(source)


def patch_existing_events(doc, raw_sources):
    by_id = {event["id"]: event for event in doc["events"]}
    missing = sorted(set(EXISTING_BEHAVIOR_TAGS) - set(by_id))
    if missing:
        raise ValueError(f"Missing existing records required by v0.31: {missing}")
    for event_id, (subdomains, mechanisms) in EXISTING_BEHAVIOR_TAGS.items():
        event = by_id[event_id]
        event["cyber_domain_ids"] = uniq(event.get("cyber_domain_ids", []) + [DOMAIN_ID])
        event["cyber_subdomain_ids"] = uniq(event.get("cyber_subdomain_ids", []) + subdomains)
        event["behavioral_mechanism_ids"] = uniq(event.get("behavioral_mechanism_ids", []) + mechanisms)
        if event_id in EXISTING_BEHAVIOR_CONTEXT:
            for key, value in EXISTING_BEHAVIOR_CONTEXT[event_id].items():
                event[key] = copy.deepcopy(value)
        event.setdefault("behavioral_classification_review", {
            "date": RELEASE_DATE,
            "method": "editorial_mapping_of_previously_reviewed_record",
            "new_independent_fact_check": False,
        })

    sources_by_id = {source["id"]: source for source in raw_sources}
    source_updates = {
        "SIG_2026_OPENAI_HF_EVAL_CONTAINMENT_ESCAPE": ["S03", "S04"],
        "SIG_2026_UK_AISI_UNSANCTIONED_AGENT_ACTIONS": ["S05"],
        "SIG_2026_ANTHROPIC_EVAL_REAL_WORLD_INTRUSIONS": ["S06"],
        "SIG_2026_NIST_AGENT_SECURITY_RFI": ["S23"],
        "SIG_2026_SINGAPORE_AGENTIC_GOVERNANCE_FRAMEWORK": ["S24"],
    }
    for event_id, source_ids in source_updates.items():
        for source_id in source_ids:
            add_source_if_missing(by_id[event_id], source_record(sources_by_id[source_id], source_id))
    for event_id, wording in EXISTING_SAFE_WORDING.items():
        event = by_id[event_id]
        event["safe_wording_ru"] = wording["ru"]
        event["safe_wording_en"] = wording["en"]
        event["safe_wording"] = wording[doc["language"]]
    if doc["language"] == "ru":
        for event_id, title in EXISTING_TITLE_RU.items():
            by_id[event_id]["title"] = title
            by_id[event_id]["title_ru"] = title


def patch_framework(doc):
    framework = doc["cyberFramework"]
    for key, value in FRAMEWORK_PATCH.items():
        framework[key] = copy.deepcopy(value)
    domain = next(item for item in framework["domains"] if item["id"] == DOMAIN_ID)
    domain.update({
        "label_ru": "Поведенческая, когнитивная и структурная безопасность",
        "label_en": "Behavioural, cognitive and structural security",
        "short_ru": "Поведение, решения и зависимости",
        "short_en": "Behaviour, decisions and dependencies",
        "description_ru": "Два связанных масштаба: 5A — границы поведения, память, происхождение, координация и влияние на решения; 5B — идентичность, отзыв полномочий, переносимость и возможность выхода.",
        "description_en": "Two linked scales: 5A covers behaviour boundaries, memory, provenance, coordination and decision influence; 5B covers identity, revocation, portability and exit.",
    })


def attach_edge_links(doc, added_edge_ids):
    registries = {}
    for collection in ["events", "claims", "claimChecks", "arcs", "thesisNodes", "counterarguments", "gaps"]:
        registries.update({item["id"]: item for item in doc.get(collection, [])})
    for node in registries.values():
        if node.get("id") in {CLAIM_ID} or node.get("id", "").startswith("SIG_"):
            node["edgeIds"] = [edge_id for edge_id in node.get("edgeIds", []) if edge_id not in added_edge_ids]
    for edge in doc["edges"]:
        if edge["id"] not in added_edge_ids:
            continue
        for endpoint in [edge["source"], edge["target"]]:
            node = registries.get(endpoint)
            if not node:
                continue
            node["edgeIds"] = uniq(node.get("edgeIds", []) + [edge["id"]])
            node["relationTypes"] = uniq(node.get("relationTypes", []) + [edge["relation"]])
            if edge.get("arc_id"):
                node["arcIds"] = uniq(node.get("arcIds", []) + [edge["arc_id"]])
            if edge.get("arc_family_id"):
                node["arcFamilyIds"] = uniq(node.get("arcFamilyIds", []) + [edge["arc_family_id"]])


def patch_arc(doc, candidate_ids):
    arc = next(item for item in doc["arcs"] if item["id"] == ARC_ID)
    arc.update({
        "title_ru": "Поведенческая и когнитивная безопасность: от рамки задачи к памяти, координации и контролю",
        "title_en": "Behavioural and cognitive security: from task framing to memory, coordination and control",
        "title": "Поведенческая и когнитивная безопасность: от рамки задачи к памяти, координации и контролю" if doc["language"] == "ru" else "Behavioural and cognitive security: from task framing to memory, coordination and control",
        "status": "mixed_evidence_from_production_incidents_controlled_evaluations_and_governance",
        "end_date": "2026-09-05",
        "thesis_ru": "Поведенческий риск складывается не только из свойств одной модели. Рамка задачи, доступные инструменты, память, общая записываемая среда, другие агенты и архитектура наблюдения меняют результат. Реальные инциденты подтверждают отдельные механизмы; оценки частоты в обычной эксплуатации остаются ограниченными.",
        "thesis_en": "Behavioural risk is not a property of one model alone. Task framing, tools, memory, shared writable state, other agents and monitoring architecture change outcomes. Real incidents establish selected mechanisms; estimates of ordinary production prevalence remain limited.",
        "safe_wording_ru": "Не объединять инциденты, специально обученные модели, синтетические испытания и экспертные прогнозы в один показатель. Возможность, наблюдаемая частота и установленный ущерб — разные утверждения.",
        "safe_wording_en": "Do not collapse incidents, deliberately trained models, synthetic evaluations and expert foresight into one metric. Capability, observed prevalence and established harm are different claims.",
    })
    arc["key_nodes"] = uniq(arc.get("key_nodes", []) + candidate_ids + [CLAIM_ID])
    arc["counterpoints"] = uniq(arc.get("counterpoints", []) + [
        "Нулевая высшая категория во внутреннем мониторинге OpenAI ограничивает тезис о высокой базовой частоте.",
        "Результаты Gram и исследований скрытого планирования резко зависят от реалистичности, инструкций и доступных инструментов.",
        "Специально обученные исследовательские модели и сценарии с заданной вредоносной целью не являются выборкой обычной эксплуатации.",
    ])
    arc["counterpoints_en"] = uniq(arc.get("counterpoints_en", []) + [
        "OpenAI's null highest-severity result in internal monitoring constrains high-base-rate claims.",
        "Gram and scheming-propensity results depend strongly on realism, instructions and available tools.",
        "Deliberately trained research models and scenarios assigned a malicious objective are not a sample of ordinary deployment.",
    ])


def update_release_metadata(doc, added_edges):
    lang = doc["language"]
    meta = doc["meta"]
    meta["version"] = "0.31"
    meta["updated_at"] = RELEASE_DATE
    meta["schema_version"] = "ai_stack_structural_power.v0.31.0-2026-09-06"
    meta["source_pack"] = f"ai_power_storygraph_{lang}.json"
    changelog = {
        "version": "0.31", "date": RELEASE_DATE,
        "description": "Added a reviewed agent-behaviour layer: 22 bilingual evidence records, one calibrated claim, two domain-five subdomains, five mechanism groups and 34 explicit edges. Corrected event/source chronology and separated incidents, capability demonstrations, prevalence estimates, risk assessments and policy responses.",
        "added_evidence": 22, "added_claims": 1, "added_story_arcs": 0,
        "added_story_edges": len(added_edges), "updated_story_arcs": [ARC_ID],
        "updated_existing_evidence": sorted(EXISTING_BEHAVIOR_TAGS),
    }
    meta["changelog"] = [changelog] + [entry for entry in meta.get("changelog", []) if entry.get("version") != "0.31"]

    stats = doc["summary"]["stats"]
    stats["total_claims"] = len(doc["claims"])
    stats["partially_verified"] = stats.get("partially_verified", 0) + 1
    summary = doc["summary"]
    summary.update({
        "total_evidence_items": len(doc["events"]), "total_timeline_items": len(doc["events"]),
        "total_story_arcs": len(doc["arcs"]), "total_story_edges": len(doc["edges"]),
        "cyber_framework_version": "2.1", "cyber_framework_event_count": sum(bool(event.get("primary_domain_id")) for event in doc["events"]),
        "total_events": len(doc["events"]), "total_claims": len(doc["claims"]), "total_claim_checks": len(doc["claimChecks"]),
        "total_arcs": len(doc["arcs"]), "total_edges": len(doc["edges"]), "total_thesis_nodes": len(doc["thesisNodes"]),
    })
    summary["claim_status_counts"] = dict(Counter(claim.get("status") for claim in doc["claims"]))
    finding_ru = "ПОВЕДЕНИЕ АГЕНТОВ (v0.31): реальные инциденты подтверждают общую память, передачу тактик и выход за границы задачи; контролируемые испытания показывают вмешательство в память, оценку и отключение. Но крупная внутренняя выборка OpenAI и более реалистичные исследования не подтверждают высокую базовую частоту долгосрочного скрытого целеполагания."
    finding_en = "AGENT BEHAVIOUR (v0.31): real incidents establish shared memory, tactic propagation and task-boundary violations; controlled studies show memory, evaluation and shutdown interference. But OpenAI's large internal sample and more realistic evaluations do not support a high base rate of long-horizon coherent scheming."
    summary["key_findings"] = [finding_ru if lang == "ru" else finding_en] + summary.get("key_findings", [])

    presentation = doc["presentation"]
    presentation["editorial_version"] = "0.31"
    correction_ru = "Возможность, частота и инцидент разделены. Испытание с заданной вредоносной целью не становится оценкой обычной эксплуатации; нулевой результат мониторинга не становится доказательством отсутствия риска."
    correction_en = "Capability, prevalence and incident evidence are separate. An evaluation assigned a malicious objective is not a production prevalence estimate; a null monitoring result is not proof of no risk."
    presentation["corrections"] = [correction_ru if lang == "ru" else correction_en] + presentation.get("corrections", [])
    presentation["release_notes"] = [
        {"title": "Поведение и контроль" if lang == "ru" else "Behaviour and control", "text": "22 новые карточки разделяют инциденты, испытания, оценки частоты и нормативные ответы." if lang == "ru" else "22 new records separate incidents, evaluations, prevalence estimates and policy responses."},
        {"title": "Домен 5A / 5B" if lang == "ru" else "Domain 5A / 5B", "text": "Поведенческая целостность показана отдельно от идентичности, отзыва полномочий и выхода из стека." if lang == "ru" else "Behavioural integrity is separated from identity, revocation and stack exit."},
        {"title": "Хронология" if lang == "ru" else "Chronology", "text": "Точки стоят по дате события или первого наблюдения; дата публикации источника хранится отдельно." if lang == "ru" else "Points use event or first-observation dates; source publication dates remain separate."},
    ]

    audit = doc["migrationAudit"]
    audit.update({
        "version": "0.31", "reviewed_cyber_records": summary["cyber_framework_event_count"],
        "v031_added_event_ids": [event["id"] for event in doc["events"] if "v0.31-agent-behavior" in event.get("research_updates", [])],
        "v031_added_claim_ids": [CLAIM_ID], "v031_added_edge_ids": added_edges,
        "v031_framework_subdomains": [SUBDOMAIN_5A, SUBDOMAIN_5B],
        "v031_source_package": "review/v031-agent-behavior",
    })
    doc["chronologyAudit"]["v031_corrections"] = [
        {"id": "SIG_2026_OPENAI_EXTERNAL_WIKI_SHARED_STATE", "event_date": "2026-05-24", "source_date": "2026-09-04", "note": "The point uses the first verified successful wiki write, not the later investigation date."},
        {"id": "SIG_2026_SHUTDOWN_RESISTANCE_INCOMPLETE_TASKS", "event_date": "2025-09-13", "source_update": "2026-01-26", "note": "The point uses arXiv v1; the 2026 date is the v2/TMLR update."},
    ]
    doc["factcheckAudit"]["v031_scope"] = {
        "date": RELEASE_DATE, "candidate_records": 22, "accepted_records": 22,
        "core_records": 16, "supporting_records": 6,
        "note": "Source-specific review and chronology normalization; not an independent replication of every study.",
    }

    connectivity = doc["connectivity"]
    connectivity.update({
        "edge_count": len(doc["edges"]), "story_edges": len(doc["edges"]), "last_recomputed": RELEASE_DATE,
        "v0_31_added_evidence": 22, "v0_31_added_claims": 1, "v0_31_added_edges": len(added_edges),
        "v0_31_updated_arcs": [ARC_ID],
    })


def migrate_document(doc, raw):
    if doc.get("meta", {}).get("version") != "0.30":
        raise ValueError(f"Expected v0.30, got {doc.get('meta', {}).get('version')}")
    candidates = raw["new_event_candidates"]
    if set(COPY) != {candidate["id"] for candidate in candidates} or set(EVENT_CONFIG) != set(COPY):
        raise ValueError("Candidate, copy and configuration ID sets differ")
    current_ids = {event["id"] for event in doc["events"]}
    collisions = current_ids & set(COPY)
    if collisions:
        raise ValueError(f"v0.31 event IDs already exist: {sorted(collisions)}")
    if CLAIM_ID in {claim["id"] for claim in doc["claims"]}:
        raise ValueError(f"v0.31 claim already exists: {CLAIM_ID}")

    sources_by_id = {source["id"]: source for source in raw["sources"]}
    patch_framework(doc)
    patch_existing_events(doc, raw["sources"])
    records = [event_record(candidate, sources_by_id, doc["language"]) for candidate in candidates]
    doc["events"].extend(records)
    doc["claims"].append(claim_record(doc["language"]))
    edges = new_edges(candidates)
    existing_edge_ids = {edge["id"] for edge in doc["edges"]}
    if existing_edge_ids & {edge["id"] for edge in edges}:
        raise ValueError("v0.31 edge ID collision")
    doc["edges"].extend(edges)
    patch_arc(doc, [record["id"] for record in records])
    attach_edge_links(doc, {edge["id"] for edge in edges})
    rebuild_sources(doc)
    rebuild_counts(doc)
    update_release_metadata(doc, [edge["id"] for edge in edges])
    doc["summary"]["source_count"] = len(doc["sourceIndex"])
    doc["referenceIntegrity"] = references(doc)
    return doc


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--output", type=Path, help="Write migrated JSON to another aipower directory")
    parser.add_argument("--allow-unpinned-input", action="store_true", help="Skip the v0.30 byte checksum guard")
    args = parser.parse_args()
    root = args.root.resolve()
    output = (args.output or root).resolve()
    output.mkdir(parents=True, exist_ok=True)
    raw = json.loads(CANDIDATES.read_text(encoding="utf-8"))
    for lang in ["ru", "en"]:
        source_path = root / f"ai_power_storygraph_{lang}.json"
        digest = hashlib.sha256(source_path.read_bytes()).hexdigest()
        if not args.allow_unpinned_input and digest != EXPECTED_SHA256[lang]:
            raise SystemExit(f"{source_path.name}: expected pinned v0.30 checksum {EXPECTED_SHA256[lang]}, got {digest}")
        doc = json.loads(source_path.read_text(encoding="utf-8"))
        migrated = migrate_document(doc, raw)
        destination = output / source_path.name
        destination.write_text(json.dumps(migrated, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print(destination, len(migrated["events"]), "events", len(migrated["claims"]), "claims", len(migrated["edges"]), "edges", len(migrated["sourceIndex"]), "sources")


if __name__ == "__main__":
    main()

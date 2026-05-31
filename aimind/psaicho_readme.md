# psAIcho × AI-Mind — пакет v0.2 (зеркальная линза + мета-слой)

Дата: 2026-05-31. Архитектура: **один spine, две линзы, мета-слой**.

## Что внутри

| Файл | Роль | Слой |
|---|---|---|
| `atlas.json` | мета: карта-как-данные, правило роутинга, общая шкала A–D, overlap-registry, guardrails | Мета (Atlas) |
| `psaicho_methodology.json` | таксономия модельной оси **AB01–AB07** (тренды и исследования, не одиночные фейлы) | Линза psAIcho |
| `aimind_signals.jsonl` | 18 psAIcho-сигналов, влитых в общий `aimind_signals.jsonl` (schema v0.2 со `streams[]` + `ai_behavior[]`) | Spine |
| `README_psaicho.md` | этот файл | — |

## Модель в одном абзаце

Каждый инцидент/исследование измеряет **человека**, **AI** или их **сцепку**. AI-Mind — человеческая линза (PH01–PH15); psAIcho — модельная линза (AB01–AB07), сфокусированная на **диспозициях и трендах**. Это не два файла-копии, а **два фильтра над одним signals.jsonl**: сигнал петли несёт и `phenomena:[PH..]`, и `ai_behavior:[AB..]`, и `streams:["human","ai"]` — появляется в обеих линзах как **одна запись по одному ID**. Нумерацию (`SIG_YYYY_SLUG`) трогать не нужно.

## Таксономия psAIcho (AB)

- `AB01_sycophancy` — натренированная угодливость (драйвер; A)
- `AB02_emergent_misalignment` — узкий finetuning → broad misalignment (A)
- `AB03_persona_instability` — Waluigi-эффект, инверсия персоны (C, эвристика)
- `AB04_scheming_and_deception` — схеминг/обман/rogue-deployment как тренд (B)
- `AB05_anthropomorphic_self_presentation` — заявления о sentience (мост к PH14/PH01; B)
- `AB06_mirror_of_distribution` — базовое зеркало распределения (урок Tay; A)
- `AB07_model_welfare` — открытый вопрос морального статуса (единственная AI-внутренняя; D)

## Сигналы в этом релизе

Оба-линзовые (петля): `SIG_2016_TAY_MICROSOFT` (anchor), `SIG_2026_DOHNANY_FOLIE_A_DEUX` (keystone).
Только-AI: Betley (emergent misalignment), CLTR scheming-in-the-wild, METR frontier risk, Emergence AI sim, Waluigi, Taking AI Welfare Seriously.

`METR` и `Emergence AI` помечены `partially_verified` — взяты из канала AiAIFail, первичные URL подтвердить перед `verified`. Это сделано намеренно: не повышать доказательность без первоисточника.

## Поправки к предыдущим обзорам (зафиксированы в guardrails)

- Фантомный «Lancet Psychiatry» → на деле PsyArXiv (Morrin) и Nature Mental Health (Dohnány).
- Emergent misalignment → ICML 2025 / **Nature янв 2026**, не «Nature 2025».
- «AI Amplifier Effect» (arXiv 2603.08084) — про романтическую интимность, не про «зеркало токсичности»; место — PH02 в AI-Mind.
- «Holly Wang» (китайский DeepSeek-кейс) → источники называют **Xiao Gao**.

## Миграция (порядок)

1. Bump schema до `aimind_signal_schema_v0.2`: добавить `streams[]` + `ai_behavior[]` (обратносовместимо; старые human-only сигналы = `streams:["human"]`).
2. Ретег петли в существующем AI-Mind по `atlas.json → retag_registry`: Cheng, Stanford spirals, GPT-4o sycophancy rollback, OpenAI disclosure → `streams:["human","ai"]` + соответствующие AB.
3. Влить `aimind_signals.jsonl` в общий spine.
4. Собрать Atlas-страницу из `atlas.json` (карта + routing + guardrails + Venn-счётчики).
5. AB-таксономию и psAIcho-рендер — отдельным релизом; операционные фейлы оставить в profgames по ссылке.

## Ключевой guardrail

«Поток про AI» ≠ психика/сознание AI. AB01–AB06 — функциональные дескрипторы **поведения**, не внутренних состояний. AB07 — единственная AI-внутренняя корзинка, и она сформулирована как **открытый вопрос** с precautionary-рамкой, а не как утверждение. psAIcho не должен сам скатываться в техно-мистицизм (PH14), который AI-Mind документирует как человеческий риск.

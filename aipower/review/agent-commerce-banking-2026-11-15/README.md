# Банки, агенты и право доступа

Дата проверки: 15 ноября 2026 года. Интеграция v0.58 -> v0.59, RU/EN.

## Отбор

Статья [Habr](https://habr.com/ru/articles/1108024/) использована как отправная точка для поиска, а не как подтверждение неизбежного исчезновения маркетплейсов. В мастер-базу вошли девять самостоятельных событий из первичных документов. У них десять URL, отсутствовавших в базовом реестре. Совпадение темы не превращается в дубликат, а отдельные наблюдения из одного раскрытия не размножаются в карточки.

| Дата | Документ | Решение и предел вывода |
| --- | --- | --- |
| 2025-09-16 | [JPMorgan/Plaid](https://www.jpmorganchase.com/newsroom/press-releases/2025/jpmc-plaid-renewed-data-access-agreement) | Новый предшествующий эпизод: цена доступа к данным. Не специальный запрет ИИ, тарифы не раскрыты. |
| 2026-08-04 | [Апелляционный суд](https://cdn.ca9.uscourts.gov/datastore/opinions/2026/08/04/26-1444.pdf) | Новая стадия прежнего дела, а не новый спор. Отмена предварительного запрета ограничивает мартовскую интерпретацию; не окончательное разрешение всех требований. |
| 2026-08-24 | [AP2](https://arxiv.org/abs/2608.23858) | Контролируемый стенд, не взлом действующей платёжной системы. Подпись не гарантирует целостности контекста до авторизации. |
| 2026-10-13 | [JPMorgan earnings call](https://www.jpmorganchase.com/content/dam/jpmc/jpmorgan-chase-and-co/investor-relations/documents/quarterly-earnings/2026/3rd-quarter/3q26-earnings-transcript.pdf) | Пилот SmartCash и позиция по внешним агентам объединены в одну карточку раскрытия. Не измерение оттока депозитов. |
| 2026-10-16 | [Visa live pilot](https://www.visa.com/en-us/thought-leadership/innovation/first-live-pilot-for-ai-payments) | Дата обновления публикации, не первой транзакции. [Требования участия](https://developer.visa.com/docs/visa-intelligent-commerce/docs-getting-started) проверены 15 ноября и не датируются задним числом. |
| 2026-10-26 | [BoE/FCA](https://www.bankofengland.co.uk/report/2026/artificial-intelligence-in-uk-financial-services-2026) | Новый опрос, связанный с карточкой 2024 года. Сохраняются знаменатели: организации, полная анкета, отношения с поставщиками. |
| 2026-10-28 | [Shopify](https://www.shopify.com/news/fall-26-edition-merchant) | Объявленные правила каталога и ранжирования. Не независимое измерение покупок и не установленная платная выдача. |
| 2026-10-28 | [SAFE](https://safe-frankfurt.de/news-latest/safe-finance-blog/details/agentic-bank-runs-could-ai-agents-become-a-risk-to-financial-stability.html) | Сценарий авторов с ограничителями внедрения, не наблюдаемое бегство вкладчиков. |
| 2026-11-04 | [BIS](https://www.bis.org/publications/scenarios-future-banking-implications-profitability-liquidity-and-solvency) | Условные сценарии распределения активов и доходов, не прогноз и не измеренный ущерб банков. |

## Связи и дедупликация

- 20 связей `part_of_arc` показывают тематическую принадлежность. Четыре связи между записями обозначают два обновления, исторический контекст и ограничивающее свидетельство.
- Использованы существующие арки финансов, институциональных решений, доступа, источников, облачной зависимости и когнитивной безопасности. Новых арок и тезисов нет.
- Соглашение с Plaid не дублирует внедрение ИИ в JPMorgan. Пилот Visa не дублирует Google UCP. Опрос 2026 года не заменяет результаты 2024 года.
- Мартовский судебный ID и дата сохранены. Две подписи старых связей исправлены; ID, направление, тип и принадлежность рёбер не менялись, прежние формулировки сохранены в `editorial_history`.
- Защита банками депозитной базы и доходов остаётся возможным объяснением стимулов. Источники не устанавливают её как единственный мотив доступа. Опасения о безопасности и ответственности сохранены как позиция банка.
- Доказательств неизбежного исчезновения банков или маркетплейсов в пакет не добавлено.

## Воспроизведение

Из каталога `aipower`:

```sh
python3 -B scripts/migrate_agent_commerce.py --apply
python3 -B scripts/build.py
python3 -B scripts/validate.py
python3 -B tests/agent_commerce_test.py
node --test tests/lenses_test.js tests/audit_navigation_test.js tests/audit_visuals_test.js
python3 -B tests/agent_commerce_browser_test.py
ATLAS_BROWSER_REPORT_DIR=review/agent-commerce-banking-2026-11-15/crosscutting python3 -B tests/lenses_browser_test.py
```

Браузерные тесты требуют Python Playwright и Google Chrome. Миграция проверяет хеши базовых файлов и отказывается перезаписывать неизвестные изменения. Снимки: [manifest](baseline-manifest.json); записи и источники: [reviewed-records.json](reviewed-records.json); журнал полей: [migration-audit.json](migration-audit.json).

Проверяются обе локализации, сохранность исходных ID и URL, типы связей, обратные указатели, хронология, фильтры, постоянные ссылки, мобильная компоновка и доступность ограничивающего судебного свидетельства. Результаты: [данные](test-report.json), [новые карточки](browser/report.json), [сквозные срезы](crosscutting/browser/report.json). Это проверка нового пакета, не повторная независимая проверка всех 987 источников.

Пройдены 1022 общие и 322 интеграционные проверки, 37 Node-тестов, 145 браузерных проверок карточек и 129 проверок сквозных срезов. В каждом языке разрешаются все 17 509 ссылок; ошибок JavaScript и горизонтального переполнения в проверенных размерах не обнаружено.

English: nine source-reviewed events and one historical legal correction extend existing views. Scenarios, self-reports, pilot deployment, laboratory evaluation and appellate holdings remain distinct. Previous IDs and edge topology are retained, including counterevidence to unrestricted platform control. Integration does not establish agent-driven deposit flight or a universal right of agent access.

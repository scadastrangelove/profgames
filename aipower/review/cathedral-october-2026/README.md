# Cathedral: безопасность лаборатории и государственный надзор

Обновление v0.50 от 28 октября 2026 года. Проверены новые сообщения и заявления сторон, а не заново весь корпус атласа.

## Принятые записи

- `SIG_2026_CATHEDRAL_ANTHROPIC_THIRD_PARTY_ACCESS`: раскрытие от 26 октября. Anthropic признала ограниченный доступ к бизнес-системам через стороннее ПО; полнота раскрытия и соблюдение границ исследования оспариваются. Точная дата доступа и самостоятельность решений агентов не установлены.
- `SIG_2026_US_SI_FORCE_INCIDENT_NOTIFICATION_DEMAND`: опубликованное 9 октября требование уведомлять власти и устранять последствия инцидентов с моделями. Заявленная обязательность отделена от доказанного механизма принуждения.

Добавлены восемь связей: пять тематических `part_of_arc`, две редакционные `context_for` и одна ограниченная `supports_with_scope`. SI Force предшествует новости Cathedral: причинной связи между ними не утверждается. Дополнены существующие арки киберустойчивости и государственного контроля, новых верхнеуровневых арок нет.

Cathedral не включена в выборку самостоятельных лабораторных побегов или нарушений намерений оператора. ИИ как инструмент проникновения и корпоративная инфраструктура ИИ-компании как объект защиты показаны отдельно от автономности. SI Force не попадает в фильтр обязательных правовых норм. Старое раскрытие Anthropic и уточнение Джорджии сохранены.

## Источники и пределы проверки

- [The Washington Post, 26 октября](https://www.washingtonpost.com/technology/2026/10/26/researchers-cybersecurity-start-up-cathedral-got-inside-anthropic/): исходное сообщение о неопубликованном отчёте Cathedral и реакциях сторон.
- [Anadolu Agency, 27 октября](https://m.aa.com.tr/en/world/months-old-us-startup-accessed-anthropic-s-sensitive-data-in-under-12-hours-report/4102515): пересказ того же материала, не независимая техническая проверка.
- [Логан Грэм / Anthropic](https://x.com/logangraham/status/2114849047953670635): возражения компании о длительности, двух уязвимостях и границах программы. Прямой запрос к X вернул 403; содержание проверено через зеркало и [The Decoder](https://the-decoder.com/ai-agents-hacked-anthropic-maker-of-arguably-the-most-capable-ai-models-for-cyberdefense/), который ссылается на этот пост. Канонический URL сохранён с оговоркой о способе чтения.
- [Responsible Disclosure Policy](https://www.anthropic.com/responsible-disclosure-policy): публичные правила Anthropic исключают системы третьих лиц. Отдельные разрешения или соглашения Cathedral публично не установлены.
- [Axios, 9 октября](https://www.axios.com/2026/10/09/anthropic-ai-security-white-house): передаёт заявление SI Force; отдельный правоприменительный документ не проверен.
- [Anthropic, 9 октября](https://www.anthropic.com/research/investigating-unintended-model-actions): уже учтённое раскрытие действий моделей на внешних системах, а не атака Cathedral на Anthropic.

Сообщения СМИ не суммируются как независимые подтверждения. Публичного технического журнала, версии модели и распределения действий между человеком и агентом нет. Не утверждаются государственный заказ, доказанный умысел сокрытия, отказ в выплате, уголовная квалификация или причинная связь между Cathedral и более ранним требованием SI Force. Политическая реакция показывает трактовку безопасности лаборатории как государственного интереса, но не измеряет фактическую степень контроля.

## Сохранность и воспроизведение

Итог: 469 событий, 76 тезисов, 32 проверки тезисов, 26 арок, 1197 связей, 680 URL. Все 467 прежних событий сохранены по содержанию; пересчитаны только обратные ссылки. Все 1189 прежних связей и 674 исходных URL с их идентификаторами сохранены. Из семи используемых URL один уже был в базе.

`migration-audit.json` содержит хеши исходных записей, `evidence.json` содержит принятые записи и происхождение источников. Миграция требует точных SHA-256 обеих файлов v0.49 и отклоняет повторный запуск. Не редактируйте входные файлы для обхода этой проверки.

```bash
python3 scripts/migrate_cathedral.py --input /path/to/v049 --output /path/to/v050
python3 scripts/build.py
python3 scripts/validate.py
python3 tests/cathedral_test.py
python3 tests/cathedral_browser_test.py --chromium /path/to/chrome
```

Проверки: 948 общих проверок данных, 138 проверок миграции, 176 общих и 76 новых браузерных проверок. Все 11 142 ссылочных поля разрешаются в каждой языковой версии. Размеры экрана: 1440×1100 и 390×844. Результаты: `validation.json`, `tests-results.json`, `full-browser-tests.json`, `browser-tests.json`; снимки находятся рядом.

Браузерные тесты используют локальную загрузку автономного HTML без сетевых запросов. Проверка опубликованного сайта и публикация в Git в этот прогон не входят. Недоступность встроенного браузерного адаптера обойдена штатным Playwright-прогоном проекта в Chromium, не изменением настроек безопасности браузера.

## English Summary

Two records distinguish Cathedral's reported access and disputed research scope from the earlier SI Force incident-reporting demand. Statements, observed effects, uncertain autonomy and legal enforceability remain separate. The release preserves all previous events, edges and source identities; it adds no top-level arc and makes no causal claim linking the October 26 news to the October 9 demand. Tests check data preservation, bilingual HTML parity, typed references, navigation, filters and mobile layout, not independent technical replication of the incident.

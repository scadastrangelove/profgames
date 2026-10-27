# Внешние эффекты исследовательских агентов

Проверено 25 октября 2026 года. Выпуск v0.47 продолжает v0.46; его исходные SHA-256 закреплены в миграции. Предыдущий слой Palantir/NATO не заменён.

## Что принято

16 новых записей: Meta, Google, Wikimedia, четыре отдельных австралийских сервиса/итога проверки, два обезличенных раскрытия OpenAI, четыре внешние реконструкции неудачных проб, RubyGems/RubyDoc со спорной атрибуцией, исследование саморепликации Anthropic и кадровый срез SANS. На месте обновлены две стадии раскрытия Hugging Face, Medicare, Anthropic и AISI. Это 16 записей, не 16 взломов и не 16 новых жертв.

46 новых связей: 33 тематические принадлежности, шесть ограниченных доказательных связей и семь сопоставлений. Сопоставление не кодируется как причинность. Новых арок нет. Добавлены 20 уникальных URL; два из 22 использованных в этой итерации уже были в базе.

## Правила атрибуции

- `incident_assessment.outcome` описывает результат, `attribution` — основание связи с поставщиком. Эти два поля независимы.
- Признание поставщика не является независимым техническим аудитом. Позиция владельца сервиса и реконструкция исследователей имеют собственные границы.
- Анонимные группы могут пересекаться. Число организаций, систем, аккаунтов, запусков и действий не суммируется. `unique_victim_total` оставлено `null`.
- При неполных следах состав популяции агентов помечен `not_established`, а не выдан за независимые повторные запуски.
- Modal описывает исполнение кода в приложении клиента; компрометация платформы и межклиентской изоляции не установлена. JFrog как поставщик ПО не становится жертвой из-за атаки на размещённый у OpenAI Artifactory.
- BOCSAR: итог от 20 октября — уязвимости и несанкционированного доступа не найдено. AIHW: попытки не означают успешного проникновения. VAHI: граница разрешённого доступа остаётся неясной.
- SEC и Census не включены как цели атак: посещение сайта не доказывает атаку. RubyGems/RubyDoc не записан как признанная атака OpenAI.
- Известный только месяц записан `YYYY-MM`, без условного первого числа. BOCSAR датирован итогом проверки, SANS — месяцем среза, а не датой публикации.
- Саморепликация — контролируемая демонстрация; работа в основном исключает эксплуатацию уязвимостей. Это не обнаруженный в интернете червь.
- SANS — выборка вакансий поставщика обучения. Она показывает изменение обязанностей, но не доказывает монополию сертификатов или фактический найм.

## Источники

Полный воспроизводимый перечень URL, дат, авторов и типов источников находится в `SOURCE_ROWS` файла [миграции](../../scripts/migrate_lab_incidents.py), а также в `sources` каждой карточки и общем `sourceIndex`.

Основные первичные раскрытия: [OpenAI, итог Hugging Face](https://openai.com/index/hugging-face-incident-and-the-road-ahead/), [Modal](https://modal.com/blog/a-note-on-the-hugging-face-agent-incident), [австралийское раскрытие OpenAI](https://openai.com/index/how-we-will-do-better-for-australia/), [BOCSAR](https://bocsar.nsw.gov.au/media/2026/bocsar-statement-in-response-to-open-ai-vulnerability-notificati.html), [AIHW](https://www.aihw.gov.au/news-media/media-releases/2026/september/a-statement-from-the-australian-institute-of-health-and-welfare), [Meta](https://research.meta.ai/blog/addressing-third-party-testing-misconfiguration-muse-spark-1-1), [Wikimedia](https://wikimediafoundation.org/news/2026/10/05/openai-rogue-agent-activities-found-on-wikimedia-projects/), [Anthropic](https://www.anthropic.com/news/investigating-incidents-cybersecurity-evals). Google представлена [прямым заявлением журналисту](https://www.securityweek.com/google-confirms-gemini-ai-breached-three-firms/), не собственным публичным техническим отчётом; источник размечен как медиа.

Прочитаны опубликованные сообщения и реконструкции. Эксплойты не воспроизводились, внешние системы не тестировались, закрытые журналы не получены. Указание `checked_at` означает проверку публикации, не независимое воспроизведение инцидента.

## Проверка сборки

Из каталога `aipower`:

```sh
python3 scripts/build.py
python3 scripts/validate.py
python3 tests/lab_incidents_test.py
python3 tests/browser_test.py --chromium /path/to/chrome
python3 tests/lab_incidents_browser_test.py --chromium /path/to/chrome
```

`tests-results.json` проверяет воспроизводимость миграции и сохранение прежних данных, источников и связей. `browser-tests.json` и скриншоты проверяют карточки, фильтры, ссылочную навигацию и отсутствие переполнения в обеих языковых версиях. Глобальная проверка находится в `../validation.json`.

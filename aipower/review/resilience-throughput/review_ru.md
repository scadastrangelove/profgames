# v0.34 — изменения двух доменов

## Главный вывод

Не «AI slop исчез». Даже после проверки остаётся значительный поток реальной инженерной работы. Для отдельных важных проектов узкое место сместилось к ёмкости сопровождения и доставки проверенных исправлений. Степень переноса этого наблюдения на всю отрасль остаётся неизвестной.

## Пакет

15 новых событий, 1 частично подтверждённый тезис, 45 связей; 16 существующих записей получили привязки к локальным дорожкам. Ни одного нового верхнеуровневого домена или сюжета. Шесть дорожек объединяют 31 уникальную карточку; одна карточка может входить в несколько дорожек.

Ниже — принятые события. Источники и ограничения каждого события доступны в JSON и drawer атласа.

| Дата | Событие | Статус в пакете |
|---|---|---|
| 2026-01-26 | curl объявляет прекращение bug bounty: исторический этап недостоверных сообщений | announced |
| 2026-03-06 | Codex Security: контекст и воспроизведение перед передачей находки разработчику | limited_access |
| 2026-04-22 | curl: апрельский переход от мусора к перегрузке качественными сообщениями | reported |
| 2026-06-24 | curl 8.21.0: 18 исправленных уязвимостей вытесняют разработку новых функций | remediated |
| 2026-06-25 | Akrites: общая команда раскрытия и инженерная помощь вместо потока разрозненных сообщений | announced |
| 2026-07-01 | curl приостанавливает приём уязвимостей для восстановления ёмкости сопровождения | observed |
| 2026-07-07 | Банк Англии: ускоренное исправление может само порождать системные сбои | published |
| 2026-07-27 | Open Secure AI Alliance: открытые средства как альтернативный канал киберзащиты | announced |
| 2026-08-04 | SAFE: RFC об инцидентах, near misses и проверяемых защитных мерах | draft |
| 2026-08-18 | Linux networking: реальные гонки перегружают сопровождение; модели включают в ревью | reported |
| 2026-08-26 | Anthropic CVD: тысячи проверенных находок и очередь уже подтверждённых ошибок | reported |
| 2026-08-31 | Watershed 250: отраслевой пилот помощи водным операторам Техаса | launched |
| 2026-09-02 | curl 8.22.0: после паузы выпущены ещё девять security fixes | remediated |
| 2026-09-03 | Daybreak: обязательство на $1 млрд субсидируемого доступа и поддержки защитников | announced |
| 2026-09-06 | Defense Factory: воспроизведение, ответственный и проверка развёрнутого исправления | reported |

## Основные правки существующих записей

**Firefox:** добавлена первичная публикация Mozilla от 21 апреля; прежний источник сохранён. 271 исправление в Firefox 150 не смешивается с другими числами из прессы и не означает установку патчей всеми пользователями.

**rust-in-peace:** исходная дата 6 августа и исторические числа сохранены. Отдельное наблюдение — сводка автора с 37 fixed/merged и два проверенных upstream PR: fontations #2012 и h2 #936. Полного пересчёта всех сообщений не проводилось; private/rejected и новые суммарные заявки не объявлены подтверждёнными уязвимостями. Опорный статус относится к наблюдаемому пути до принятых исправлений.

**Hugging Face:** добавлена связь с системной доступностью средств реагирования; пересказ участниками нового альянса не считается независимой форензикой.

**Существующие письмо OpenAI, Oracle, Rapid7, EBA, BoE, Gold Eagle и Cyber Shield:** новые тематические связи без дублирования событий и без переноса обещаний в прошлые даты.

## Что не включено

FS-ISAC и Steel Resolve: приглашения/программы не выданы за отчёты о проведении или достигнутую готовность. USB-mailbox: первичная публикация недоступна для повторной проверки; вместо числа писем опорным Linux-свидетельством служит доступное письмо netdev. IMF: механизм общих зависимостей уже покрыт; лишняя карточка не добавлена.

## Чтение и проверка

Открыть русскую или английскую страницу, перейти в кибервкладку и раскрыть «От находки к устойчивости». Верхние фильтры действуют на дорожки. Режим «Все факты» показывает предысторию; опорный режим концентрируется на подтверждённых результатах и существенных ответах. Метрики CVD намеренно показаны отдельными карточками, не диаграммой убывающей воронки.

Результаты: 600 статических и 244 браузерных проверки. 6 896 ссылочных полей в каждой версии. Миграция воспроизводится на точной паре v0.33; изменённые входы отвергаются. Внешние источники старого корпуса не перепроверены целиком, исследования не реплицировались.

## Проверенные источники нового слоя

**S01 — Daniel Stenberg / curl.** The end of the curl bug-bounty. Дата: 2026-01-26. [Источник](https://daniel.haxx.se/blog/2026/01/26/the-end-of-the-curl-bug-bounty/).

**S02 — Daniel Stenberg / curl.** High-Quality Chaos. Дата: 2026-04-22. [Источник](https://daniel.haxx.se/blog/2026/04/22/high-quality-chaos/).

**S03 — Daniel Stenberg / curl.** curl 8.21.0. Дата: 2026-06-24. [Источник](https://daniel.haxx.se/blog/2026/06/24/curl-8-21-0/).

**S04 — Daniel Stenberg / curl.** curl summer of bliss. Дата: 2026-06-15. [Источник](https://daniel.haxx.se/blog/2026/06/15/curl-summer-of-bliss/).

**S05 — Daniel Stenberg / curl.** What the bliss taught us. Дата: 2026-08-03. [Источник](https://daniel.haxx.se/blog/2026/08/03/what-the-bliss-taught-us/).

**S06 — Daniel Stenberg / curl.** curl 8.22.0. Дата: 2026-09-02. [Источник](https://daniel.haxx.se/blog/2026/09/02/curl-8-22-0/).

**S07 — Anthropic.** Coordinated vulnerability disclosure dashboard — snapshot 26 August 2026. Дата: 2026-08-26. [Источник](https://red.anthropic.com/2026/cvd/).

**S08 — Anthropic.** About the CVD dashboard. Дата: 2026-08-26. [Источник](https://red.anthropic.com/2026/cvd/about/).

**S09 — Jakub Kicinski / Linux netdev.** [GIT PULL] Networking for 7.3. Дата: 2026-08-18. [Источник](https://lists.openwall.net/linux-kernel/2026/08/18/2125).

**S10 — Linux Foundation.** Linux Foundation and Industry Leaders Launch Akrites. Дата: 2026-06-25. [Источник](https://www.linuxfoundation.org/press/linux-foundation-and-industry-leaders-launch-akrites-to-defend-critical-open-source-software-against-ai-enabled-cyber-threats?hs_amp=true).

**S11 — Akrites.** We All Depend on Open Source. We Will Defend It Together.. Дата: 2026-06-25. [Источник](https://akrites.org/letter/).

**S12 — NVIDIA.** Industry Leaders Unite in Open Secure AI Alliance for AI Safety and Security. Дата: 2026-07-27. [Источник](https://blogs.nvidia.com/blog/open-secure-ai-alliance/).

**S13 — Open Secure AI Alliance.** Shared AI Findings Exchange (SAFE) — pinned RFC. Дата: 2026-08-04. [Источник](https://github.com/OpenSecureAIAlliance/RFCs/blob/4ec7660569f41224c6bb8a1311c053e285a4d53d/rfc-safe-proposal.md).

**S14 — NVIDIA.** AI Leaders Propose SAFE Guidelines for Cybersecurity Transparency. Дата: 2026-08-04. [Источник](https://blogs.nvidia.com/blog/open-secure-ai-alliance-contributions/).

**S15 — OpenAI.** Defense Factory. Дата: недатированная страница; наблюдение 2026-09-06. [Источник](https://openai.com/the-defense-factory/).

**S16 — OpenAI.** Daybreak for Frontline Defenders. Дата: 2026-09-03. [Источник](https://openai.com/index/daybreak-for-frontline-defenders/).

**S17 — OpenAI.** Codex Security: now in research preview. Дата: 2026-03-06. [Источник](https://openai.com/index/codex-security-now-in-research-preview/).

**S18 — Texas Cyber Command.** Texas to lead Project Watershed 250 cybersecurity pilot. Дата: 2026-09-01. [Источник](https://www.txcc.texas.gov/news/project-watershed-250).

**S19 — National Association of Water Companies.** Statement on the Launch of the White House Water Cybersecurity Pilot. Дата: 2026-09-01. [Источник](https://nawc.org/news/statement-from-nawc-on-the-launch-of-the-white-house-water-cybersecurity-pilot/).

**S20 — Bank of England.** Financial Stability Report — July 2026, frontier AI and operational risk. Дата: 2026-07-07. [Источник](https://www.bankofengland.co.uk/financial-stability-report/2026/july-2026).

**S21 — Mozilla.** The zero-days are numbered. Дата: 2026-04-21. [Источник](https://blog.mozilla.org/en/firefox/privacy-security/ai-security-zero-day-vulnerabilities/).

**S22 — rust-in-peace.** Public disclosure log — summary dated 18 August, observed 6 September. Дата: 2026-08-18. [Источник](https://github.com/scadastrangelove/rust-in-peace/blob/main/DISCLOSURES-PUBLIC.md).

**S23 — Google Fonts / fontations.** PR #2012: do not panic on absent VARC variation store. Дата: 2026-08-05. [Источник](https://github.com/googlefonts/fontations/pull/2012).

**S24 — hyperium/h2.** PR #936: prevent double counting pushed streams after 1xx responses. Дата: 2026-08-17. [Источник](https://github.com/hyperium/h2/pull/936).

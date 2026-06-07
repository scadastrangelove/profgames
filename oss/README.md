# На трёх слонах

> OSS / JITI / рента посредников: боковая ветка цикла «Игры в профессию» про то, как AI меняет равновесие вокруг кода, open source, платформ и посредников.

**Публикация:** [scadastrangelove.github.io/profgames/oss/](https://scadastrangelove.github.io/profgames/oss/)  
**Событийный слой:** [ai_oss_events.html](https://scadastrangelove.github.io/profgames/oss/ai_oss_events.html)  
**Автор:** Сергей Гордейчик · [teletype](https://teletype.in/@sergey_gordey) · [telegram](https://t.me/aiakyn) · [github](https://github.com/scadastrangelove/profgames) · тег **#profgames**

## Что это

`oss/` — приложение к статье **«На трёх слонах»**: манифест + машинно-читаемый слой из **110 сигналов** по OSS, музыке, издательскому делу, data commons, праву, security disclosure и cloud/runtime.

Центральная рамка: старое равновесие вокруг кода держалось на трёх вещах — дороговизне копирования, доказуемости происхождения и достижимости нарушителя. AI одновременно удешевляет копирование, размывает provenance артефакта и переносит принуждение с права на платформы. Поэтому рента уходит не к тому, кто создал артефакт, а к тому, кто контролирует вход, исполнение и доверие.

## Файлы

| Файл | Назначение |
| --- | --- |
| [`index.html`](https://scadastrangelove.github.io/profgames/oss/) | Публикационная HTML-версия статьи |
| [`manifest_tri_slona.md`](manifest_tri_slona.md) | Markdown-исходник статьи |
| [`ai_oss_events.html`](https://scadastrangelove.github.io/profgames/oss/ai_oss_events.html) | Интерактивный каталог событий: timeline, карточки, фильтры, матрица и равновесия |
| [`ai_oss_signals.jsonl`](ai_oss_signals.jsonl) | 110 сигналов, один JSON-объект на строку |
| [`ai_oss_meta.json`](ai_oss_meta.json) | Методический слой, гипотезы, market baseline, сводки и changelog |

## Как читать датасет

Каждый сигнал в `ai_oss_signals.jsonl` содержит:

```text
id              — стабильный идентификатор SIG_<год>_<тема>
title           — краткое название события
date            — дата события
region          — US | EU | CN | RU | global
evidence_level  — A | B | C
confidence      — high | medium | low
description     — что произошло
why_important   — почему это важно для рамки
dimensions      — привязка к 10 осям
actors          — привязка к акторам
sources[]       — ссылки на первичные и вторичные источники
relationships[] — откаты, уточнения, эскалации и split-решения
```

Уровни доказательности совместимы с остальным проектом:

- **A** — primary / official / court / arXiv / peer-reviewed;
- **B** — вторичные источники, медиа и расследования с проверяемыми ссылками;
- **C** — спорный claim или одиночный источник.

## Связь с profgames

Это не основная статья A–D, а боковая ветка той же рамки: про сжатие посредников, перенос доверия в контроль точки входа и новую геометрию ренты. Главная страница цикла: [scadastrangelove.github.io/profgames](https://scadastrangelove.github.io/profgames/).


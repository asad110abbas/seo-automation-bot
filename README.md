<div align="center">

# 🔎 BRIHA · SEO Automation Bot

**A multi-agent AI system that automates end-to-end SEO for local businesses: audit, keywords, competitors, Google Business Profile, content, links and monthly reports.**

![Part of BRIHA](https://img.shields.io/badge/Part_of-BRIHA-8B5CF6?style=for-the-badge&labelColor=0B1024)
![Python](https://img.shields.io/badge/Python-3776AB?logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-009688?logo=fastapi&logoColor=white)
![Groq](https://img.shields.io/badge/Groq-Llama_3.3_70B-F55036)
![Next.js](https://img.shields.io/badge/Next.js_14-000000?logo=nextdotjs&logoColor=white)
![Celery](https://img.shields.io/badge/Celery-Redis-37814A?logo=celery&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-4169E1?logo=postgresql&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-2496ED?logo=docker&logoColor=white)
![License](https://img.shields.io/badge/license-MIT-green)

</div>

> ⚡ **Part of [BRIHA](https://github.com/asad110abbas)**, built by Syed Asad Abbas.

---

## Overview

Local businesses (clinics, restaurants, law firms…) need SEO but can't afford an agency. This bot replaces a
whole SEO team with **7 specialized AI agents** coordinated by an orchestrator. Each agent runs as a background
job, streams live progress to the dashboard over WebSockets, and stores structured results you can act on.

## Architecture

```mermaid
flowchart TB
    UI["Next.js dashboard"] -- REST + WebSocket --> API["FastAPI"]
    API --> Q[("Redis queue")]
    Q --> W["Celery workers"]
    W --> O{"SEO Orchestrator"}
    O --> A1["🕷️ Website Audit"]
    O --> A2["🔑 Keyword Research"]
    O --> A3["🥊 Competitor Analysis"]
    O --> A4["📍 GBP Optimization"]
    O --> A5["✍️ Content"]
    O --> A6["🔗 Link Building"]
    O --> A7["📄 Reporting (PDF)"]
    A2 & A3 --> S["SerpAPI"]
    A1 --> C["Crawler (httpx + Playwright)"]
    A1 & A2 & A3 & A4 & A5 & A6 & A7 --> L["Groq LLM"]
    W --> DB[("PostgreSQL")]
```

## The 7 agents

| Agent | What it does |
|---|---|
| 🕷️ **Website Audit** | Crawls the site and flags technical SEO issues: titles, meta, headings, broken links, speed signals |
| 🔑 **Keyword Research** | Generates seed keywords with the LLM, enriches them with live SERP data, and ranks opportunities |
| 🥊 **Competitor Analysis** | Finds who ranks for your keywords and what they do better |
| 📍 **GBP Optimization** | Recommendations for the Google Business Profile: categories, description, posts |
| ✍️ **Content** | SEO-optimized page and blog drafts for target keywords |
| 🔗 **Link Building** | Backlink and citation opportunities for local SEO |
| 📄 **Reporting** | Monthly client-ready PDF report (Jinja2 + WeasyPrint) |

## Features
- **Background jobs** with Celery + Redis and live progress over WebSockets
- **Per-run token and cost tracking** with usage dashboards (per project and global)
- **Rate limiting** per project per day, JWT auth, retries with exponential backoff
- **Alembic** migrations, async SQLAlchemy, structured logging
- **Dockerized**: dev and production compose files

## Quick start

```bash
git clone https://github.com/asad110abbas/seo-automation-bot.git
cd seo-automation-bot
cp backend/.env.example backend/.env     # add GROQ_API_KEY, SERPAPI_KEY, SECRET_KEY
docker compose up --build
```
- Dashboard: http://localhost:3000
- API docs: http://localhost:8000/docs

## Tech stack

| Layer | Technologies |
|---|---|
| AI | Groq (Llama 3.3 70B), prompt-engineered agents |
| Backend | Python, FastAPI, SQLAlchemy (async), Alembic, Celery, Redis |
| Data | PostgreSQL, SerpAPI |
| Scraping | httpx, BeautifulSoup, Playwright |
| Reports | Jinja2, WeasyPrint |
| Frontend | Next.js 14, TypeScript, Tailwind CSS, TanStack Query |
| Ops | Docker, Docker Compose |

## License

[MIT](LICENSE)

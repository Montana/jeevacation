# Jeevacation

![Jeevacation Logo](https://github.com/user-attachments/assets/df05d79f-1db6-4d68-a1b7-11965aad0894)

On the front end jeevacation takes the nightmare of digging through endless stacks of court documents and turns it into something straightforward and smart. Forget scrolling through PDFs for hours—this tool gives you organized access to the Epstein case releases through easy-to-use command-line interfaces, REST APIs, and a slick web app. At its core, it's all about answering one key question quickly: who shows up where in these public filings? And it does so in a way that's easy to repeat, track, and share.

Inspired by [EpsteIn](https://github.com/cfinke/EpsteIn), jeevacation builds on that idea by scanning your LinkedIn connections against the document database to spot any matches. It goes further with AI-driven context analysis, categorizing mentions (like whether someone's a witness, employee, or something else) and gauging sentiment to help you understand the tone. You can visualize connections through interactive network graphs that highlight relationships and co-occurrences across documents. Plus, it keeps an eye on new releases with automated alerts, and lets you export everything in formats like HTML, JSON, or CSV for whatever you need next.

This isn't just for tech whizzes—it's designed for journalists piecing together stories, researchers building out networks, legal pros keeping tabs on references, or really anyone curious about mentions in these public records. Whether you're spotting patterns or just checking facts, it makes the process feel less like a chore and more like a tool that works for you.

## Key Features

The search engine at the heart of Jeevacation is built for speed and smarts. It handles batch processing asynchronously, so queries fly through without bogging you down. It catches false positives, matches name variations like nicknames or abbreviations, and ranks results based on context to put the most relevant stuff first.

If you opt in, the AI layer adds real depth: it automatically sorts mentions into categories, analyzes sentiment (think neutral, concerning, or benign), pulls out key facts from excerpts, and even scores matches for confidence. This turns raw data into something insightful without you having to do all the heavy lifting.

The web interface is intuitive—drag and drop your LinkedIn CSV, filter and sort in real time, spot visual risk indicators at a glance, and export with a single click. For a bigger picture, the network visualization creates graphs of relationships, detects clusters of related people, weights connections by strength, and lets you zoom, pan, and hover for details.

On the monitoring side, it runs background checks for fresh documents, lets you set alert timings, sends email notifications via SendGrid, and tracks changes over time. Under the hood, it uses SQLAlchemy for database management (SQLite or PostgreSQL), caches PDFs for quick repeats, logs every search for audits, and supports exports in multiple formats.

The REST API keeps things flexible with JSON endpoints, rate limiting, authentication hooks, and webhook support for integrating into your own setups.

## Getting Started

You'll need Python 3.9 or higher, along with pip (or pipx if you prefer isolated environments). For container fans, Docker is optional but handy. If you want the AI bells and whistles, grab an Anthropic API key; for alerts, a SendGrid key does the trick.

Kick things off in three simple steps: clone the repo from https://github.com/Montana/jeevacation.git, hop into the directory, and run ./quickstart.sh. That script sets up a virtual environment, installs what you need, initializes the database, and creates config templates.

Once that's done, activate the venv with source .venv/bin/activate, then try your first search: python cli.py search --connections /path/to/Connections.csv. To fire up the web UI, just run python cli.py web and head to http://localhost:5000 in your browser.

For a more hands-on install without the script, after cloning, create and activate a venv, pip install -r requirements.txt and pip install -e ., copy .env.example to .env, and run python cli.py db init. Toss in those optional API keys to .env if you're using them.

If Docker's your thing, docker compose up --build gets you running, with the app at http://localhost:5000.

## Grabbing Your LinkedIn Data

To feed in your connections, head to LinkedIn's Settings & Privacy under Data privacy. Request a copy of your data, select Connections, and download the archive. Unzip it, and you'll find Connections.csv ready to go.

## How to Use It

The CLI is your entry point—check python cli.py --help for all options. A basic search is as easy as python cli.py search --connections Connections.csv. Amp it up with AI: add --use-ai --api-key sk-xxx. Export to JSON with --format json --output results.json, or build a graph via python cli.py graph --connections Connections.csv --output network.html.

For the web experience, python cli.py web launches it—upload your CSV, search, filter, and explore visuals right there.

If you're coding, import the modules like this in Python:

```python
import asyncio
from jeevacation.core.search_client import EpsteinSearchClient
from jeevacation.core.linkedin_parser import LinkedInParser
from jeevacation.ai.analyzer import AIAnalyzer

async def main():
    contacts = LinkedInParser.parse_csv("Connections.csv")
    async with EpsteinSearchClient() as client:
        results = await client.batch_search([c.full_name for c in contacts], batch_size=10)

    analyzer = AIAnalyzer()
    for name, excerpts in results.items():
        if excerpts:
            analysis = analyzer.analyze_mentions(name, excerpts)
            print(f"{name}: {analysis.category} ({analysis.sentiment})")

asyncio.run(main())
```

The REST API starts with python cli.py api. Upload a CSV using curl -X POST http://localhost:5000/api/upload -F "file=@Connections.csv", then trigger a search: curl -X POST http://localhost:5000/api/search -H "Content-Type: application/json" -d '{"filter_common_names": true, "use_ai_analysis": true}'.

## Under the Hood

The project's laid out clearly: core/ handles search and parsing, ai/ does the smart analysis, web/ powers the UI, api/ manages endpoints, database/ deals with storage and models, monitoring/ covers alerts and checks, utils/ has helpers for reports and graphs, and cli.py ties it all together as the main entry.

## A Word of Caution

Remember, just because a name pops up in these documents doesn't mean anything shady—people show up as witnesses, staff, victims, or even random mentions. Always dig into the full context, see AI insights as a jump-off point, watch for false hits (common names are tricky), and never jump to conclusions or accusations based on this alone. Jeevacation is about making public info easier to navigate, not about judging anyone.

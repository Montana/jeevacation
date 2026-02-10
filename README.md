# jeevacation

![Jeevacation Logo](https://github.com/user-attachments/assets/df05d79f-1db6-4d68-a1b7-11965aad0894)

jeevacation transforms the overwhelming task of sifting through millions of pages of court documents into a streamlined, intelligent process. Instead of manually combing through PDFs, this system provides structured access to Epstein document releases via command-line tools, REST APIs, and an interactive web application.

It's built for anyone who needs quick, reliable answers to a simple question: **who appears where** in public court filings—in a way that's repeatable, auditable, and exportable.

## What It Does
- **Searches LinkedIn connections** against document databases for matches.
- **Analyzes context** with AI-powered categorization and sentiment analysis.
- **Visualizes relationships** through network graphs between people and documents.
- **Monitors releases** with automated alerts for new documents.
- **Exports findings** in versatile formats like HTML, JSON, and CSV.

## Who It's For
- Journalists uncovering connections.
- Researchers mapping document networks.
- Legal professionals tracking references.
- Anyone exploring public court filings for mentions and contexts.

## Features

### Intelligent Search
- Asynchronous batch processing for lightning-fast queries.
- False positive detection and smart filtering.
- Name variation matching (e.g., nicknames, abbreviations).
- Context-aware ranking of results.

### AI Analysis (Optional)
- Automated categorization of mentions (e.g., witness, employee, victim).
- Sentiment analysis (neutral, concerning, benign).
- Key fact extraction from relevant excerpts.
- Confidence scoring for each match.

### Web Interface
- Drag-and-drop CSV upload for LinkedIn connections.
- Real-time filtering, sorting, and search.
- Visual risk indicators for quick insights.
- One-click exports to share findings.

### Network Visualization
- Interactive graphs showing co-occurrences in documents.
- Cluster detection to identify related groups.
- Weighted edges based on connection strength.
- Intuitive controls: zoom, pan, hover for details.

### Monitoring & Alerts
- Automated background checks for new document releases.
- Customizable alert intervals.
- Email notifications powered by SendGrid.
- Change tracking to monitor updates over time.

### Data Layer
- SQLAlchemy ORM with support for SQLite or PostgreSQL.
- PDF caching for optimized repeated access.
- Full audit trail of all searches.
- Exports to HTML, JSON, and CSV.

### REST API
- JSON-based endpoints for requests and responses.
- Built-in rate limiting and authentication support.
- Webhook integration for seamless workflows.

## Quick Start

### Prerequisites
- Python 3.9+
- pip (or pipx for isolated installs)
- (Optional) Docker for containerized deployment
- (Optional) Anthropic API key for AI features
- (Optional) SendGrid API key for email alerts

### Install in 3 Steps
```bash
git clone https://github.com/Montana/jeevacation.git
cd jeevacation
./quickstart.sh
```

The `quickstart.sh` script handles everything: creates a virtual environment, installs dependencies, initializes the database, and generates config templates.

### First Search
```bash
source .venv/bin/activate
python cli.py search --connections /path/to/Connections.csv
```

### Launch Web UI
```bash
python cli.py web
```
Open [http://localhost:5000](http://localhost:5000) in your browser.

## Detailed Installation

### Local Development
```bash
git clone https://github.com/Montana/jeevacation.git
cd jeevacation

python3 -m venv .venv
source .venv/bin/activate

pip install -r requirements.txt
pip install -e .

cp .env.example .env
python cli.py db init
```

Add optional keys to `.env`:
```
ANTHROPIC_API_KEY=sk-ant-your-key-here
SENDGRID_API_KEY=SG.your-key-here
```

### Docker
```bash
docker compose up --build
```
Access the web app at [http://localhost:5000](http://localhost:5000).

## Getting Your LinkedIn Connections.csv
1. Go to LinkedIn → Settings & Privacy → Data privacy.
2. Select "Get a copy of your data" → Choose "Connections" → Request archive.
3. Download the ZIP, extract it, and find `Connections.csv`.

## Usage

### CLI
Explore commands:
```bash
python cli.py --help
```

Basic search:
```bash
python cli.py search --connections Connections.csv
```

With AI analysis:
```bash
python cli.py search --connections Connections.csv --use-ai --api-key sk-xxx
```

Export to JSON:
```bash
python cli.py search --connections Connections.csv --format json --output results.json
```

Generate network graph:
```bash
python cli.py graph --connections Connections.csv --output network.html
```

### Web UI
```bash
python cli.py web
```
Upload your CSV, run searches, and visualize results interactively.

### Python API
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

### REST API
Start the server:
```bash
python cli.py api
```

Upload CSV:
```bash
curl -X POST http://localhost:5000/api/upload -F "file=@Connections.csv"
```

Run search:
```bash
curl -X POST http://localhost:5000/api/search \
  -H "Content-Type: application/json" \
  -d '{"filter_common_names": true, "use_ai_analysis": true}'
```

## Architecture
```
jeevacation/
├── core/        # Search and parsing logic
├── ai/          # AI context analysis
├── web/         # Web UI components
├── api/         # REST endpoints
├── database/    # Persistence and models
├── monitoring/  # Alerts and scheduled checks
├── utils/       # Reports, graphs, and helpers
└── cli.py       # CLI entrypoint
```

## Important Disclaimer
A mention in court documents does **not** imply wrongdoing, involvement, or guilt. Individuals may appear for legitimate reasons, such as being witnesses, employees, legal professionals, victims, or through incidental references.

Use this tool responsibly:
- Always review full context before drawing conclusions.
- Treat AI outputs as starting points, not final verdicts.
- Account for false positives, especially with common names.
- Avoid making accusations based solely on matches.

This project promotes discoverability and transparency in public records—it does not draw conclusions.

Inspired by: [https://github.com/cfinke/EpsteIn](https://github.com/cfinke/EpsteIn)

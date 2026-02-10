# jeevacation

![Jeevacation Logo](https://github.com/user-attachments/assets/df05d79f-1db6-4d68-a1b7-11965aad0894)

**jeevacation** helps you quickly check whether names from your LinkedIn connections (or any contact list) appear in newly released public records, without manually digging through thousands of pages.

I was drawing some inspiration from the clever [EpsteIn](https://github.com/cfinke/EpsteIn) and thought could I improve this?

**“Who shows up where in these files?”**

Below are the fastest ways to get started.

---

## Quick Command Examples

| Task           | Command                                                                                  | What It Does                       |
| -------------- | ---------------------------------------------------------------------------------------- | ---------------------------------- |
| Run basic scan | `python cli.py search --connections Connections.csv`                                     | Checks if names appear in the docs |
| Use AI context | `python cli.py search --connections Connections.csv --use-ai`                            | Adds role + sentiment analysis     |
| Export JSON    | `python cli.py search --connections Connections.csv --format json --output results.json` | Saves structured results           |
| Generate graph | `python cli.py graph --connections Connections.csv --output network.html`                | Builds a relationship map          |
| Start web UI   | `python cli.py web`                                                                      | Launches browser interface         |
| Start API      | `python cli.py api`                                                                      | Runs REST server                   |

---

## What jeevacation Actually Does

Drawing inspiration from the EpsteIn project, **jeevacation** takes things further by cross-checking your LinkedIn network against the documents to flag possible name matches. From there it can optionally:

* Categorize mentions (witness, staffer, attorney, etc.)
* Add sentiment context (neutral, concerning, benign)
* Build visual relationship graphs
* Monitor for new document releases
* Export findings in multiple formats

It’s designed for:

* Journalists tracking leads
* Researchers mapping connections
* Lawyers scanning references
* Curious readers exploring public filings

Instead of brute-force reading, **jeevacation** turns document review into something structured, auditable, and fast.

---

## Quickstart (Fastest Path)

| Step            | Command                                                |
| --------------- | ------------------------------------------------------ |
| Clone repo      | `git clone https://github.com/Montana/jeevacation.git` |
| Enter directory | `cd jeevacation`                                       |
| Auto setup      | `./quickstart.sh`                                      |
| Activate env    | `source .venv/bin/activate`                            |
| Test search     | `python cli.py search --connections Connections.csv`   |

---

## Optional Modes

| Mode       | Command                     | Use Case                     |
| ---------- | --------------------------- | ---------------------------- |
| Web app    | `python cli.py web`         | Non-technical users          |
| API server | `python cli.py api`         | Integration into other tools |
| Docker     | `docker compose up --build` | Clean containerized run      |

---

## Key Capabilities

| Feature            | Details                                                     | Why It Matters           |
| ------------------ | ----------------------------------------------------------- | ------------------------ |
| Intelligent search | Name matching, nickname detection, false-positive filtering | Finds real hits faster   |
| AI analysis        | Role tagging + sentiment scoring                            | Adds context to mentions |
| Visualization      | Co-mention network graphs                                   | Spot patterns quickly    |
| Monitoring         | Auto-checks for new document drops                          | Stay up to date          |
| Data layer         | SQLite/Postgres + audit logs                                | Traceable and repeatable |
| Exports            | HTML, CSV, JSON                                             | Easy sharing and review  |

---

## Important Context

A name appearing in documents does **not** imply wrongdoing. Mentions can include:

* Witnesses
* Staff
* Legal professionals
* Victims
* Passing references

**jeevacation** is a research and discovery tool for public records — not a conclusions engine. Always review source context.

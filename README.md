# NexusAI Intern Challenge

**Author:** Raj Kumar Malik

This repository contains my complete submission for the NexusAI Backend Engineering Intern Challenge. The project demonstrates asynchronous API handling, robust database design using PostgreSQL, parallel data fetching, and business-logic validation using Test-Driven Development (TDD).

## Repository Structure

* `task1/` - Asynchronous AI Message Handler (OpenAI API integration, rate-limit/timeout handling)
* `task2/` - Database Schema & Async Repository (PostgreSQL, `asyncpg`, parameterized queries)
* `task3/` - Parallel Data Fetcher (`asyncio.gather`, graceful degradation with `return_exceptions`)
* `task4/` - Escalation Decision Engine (Strict business logic, edge-case handling)
* `ANSWERS.md` - System design and architecture written responses

## Setup Instructions

1. **Clone the repository:**
   ```bash
   git clone [https://github.com/YOUR-GITHUB-USERNAME/nexusai-intern-challenge.git](https://github.com/YOUR-GITHUB-USERNAME/nexusai-intern-challenge.git)
   cd nexusai-intern-challenge
Install dependencies:

```Bash
pip install -r requirements.txt

Environment Variables:
For task1 and task2, you will need a .env file in the root directory.

Plaintext
OPENAI_API_KEY=sk-proj-your-key-here
DATABASE_URL=postgresql://postgres:yourpassword@localhost:5432/postgres

How to Run the Tasks
Task 1: AI Message Handler
To verify the error handling, timeouts, and rate-limit retries without incurring live API costs, run the mocked test suite:

```Bash
pytest task1/test_handler.py -v

Task 2: Database Repository
Ensure your local PostgreSQL instance is running and the DATABASE_URL is set in your .env. To build the schema, insert a test record, and run the analytics query:

```Bash
python task2/test_db.py

Task 3: Parallel Data Fetcher
To demonstrate the >2x latency speedup and the graceful handling of the injected 10% timeout failure:

```Bash
python task3/main.py

Task 4: Escalation Decision Engine
To validate the 6 escalation rules and edge cases via the TDD test suite:

```Bash
pytest task4/ -v
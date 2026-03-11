# Telecom AI - Database Layer (Task 2)

Hey there! Welcome to the database portion of my submission. 

For this task, I designed a strict PostgreSQL schema to store our customer interactions and built an asynchronous Python data access layer using `asyncpg`. My main goal here was **data integrity**—making sure bad data can never make it into the database, even if the application layer messes up.

## 🏗️ Architectural & Design Decisions

Rather than just making every column a `VARCHAR` and calling it a day, I utilized native PostgreSQL features to lock down the data:

* **Strict Typing & Constraints:** * I created custom `ENUM` types for both `channel` and `outcome`.
  * I added a `CHECK` constraint on `confidence_score` so it absolutely cannot fall outside the `0.0` to `1.0` range.
  * I added a `CHECK` constraint on `csat_score` to restrict it to `1` through `5` (and made it nullable, since CSAT is collected after the fact).
* **Security:** The `CallRecordRepository` strictly uses `asyncpg` connection pools and parameterized queries (`$1`, `$2`, etc.). There is zero string formatting in the SQL execution, making SQL injection impossible.
* **Analytics Optimization:** For the complex aggregation query (lowest resolution rate by intent), I used Postgres' native `FILTER (WHERE outcome = 'resolved')` clause. This calculates the conditional percentage in a single pass, which is much faster than a clunky `CASE WHEN` statement.

## ⚡ Indexing Strategy

I added three specific indexes to optimize the exact access patterns our app requires:

1. `idx_call_records_phone`: We frequently query a customer's history (e.g., the `get_recent` method). This index makes fetching those past calls instantaneous.
2. `idx_call_records_created_at`: Time-series data is almost always queried by date (like "last 7 days"). This prevents full table scans for time-based reporting.
3. `idx_call_records_intent_outcome`: A composite index specifically designed to optimize the heavy analytics query. Since we group by intent and filter/count by outcome, having them indexed together speeds up the aggregation.

## 🚀 How to Run and Test

I wrote a test script so you don't have to manually wire up a Python file to check my work. 

**1. Database Setup:**
Apply the `schema.sql` file to your local PostgreSQL instance to build the tables and ENUMs.

**2. Environment Variables:**
Create a `.env` file in this directory and add your Postgres connection string:
```text
DATABASE_URL=postgresql://your_user:your_password@localhost:5432/your_db
3. Run the Tests:
Ensure you have asyncpg and python-dotenv installed, then run the test script. It will connect to the pool, insert a dummy record, fetch it back, and run the analytics query.

Bash
pip install -r requirements.txt
python test_db.py
Thanks for reviewing the architecture! Let me know if you have any questions about the SQL logic.
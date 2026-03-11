# Telecom AI - Parallel Data Fetcher (Task 3)

When an AI agent is interacting with a customer on a live voice call, latency is the enemy. Every millisecond counts. If an agent has to wait for CRM, Billing, and Ticket History sequentially, the customer will experience unnatural, robotic pauses.

## Why Async Parallelism Matters

In a sequential architecture, execution blocks while waiting for network I/O. If CRM takes 400ms, Billing takes 350ms, and Tickets take 300ms, the total wait time is a massive **1050ms**. 

By utilizing asynchronous parallelism via `asyncio.gather()`, we fire all three network requests simultaneously. The event loop switches context while waiting for the network responses. This means the total fetch time is only constrained by the **slowest single request** (in this case, ~400ms max), resulting in a massive speed improvement.

## Graceful Degradation (`return_exceptions=True`)

In a microservice architecture, partial failures are guaranteed. The billing service might go down, but the AI should still be able to greet the user by name (from CRM) and ask about their open router ticket. 

By passing `return_exceptions=True` into `asyncio.gather()`, we prevent a `TimeoutError` in the Billing fetcher from crashing the CRM and Ticket fetchers. The failed fetch simply returns the exception object, which we safely catch using `isinstance()`, log as a warning, and replace with `None` in the `CustomerContext` dataclass. The application continues running seamlessly.

## Execution Proof

Here is real output from my local testing demonstrating a **4.13x speedup** and a successful, graceful catch of a random billing timeout without crashing the app:

```text
--- 🐢 Running Sequential Fetch ---
Time Taken: 851.76 ms
Data Complete: True

--- ⚡ Running Parallel Fetch ---
WARNING: Billing Fetch Failed: Billing API timed out for phone +1234567890
Time Taken: 206.05 ms
Data Complete: False

🚀 Parallel execution was 4.13x faster!

--- Final CustomerContext Object (Parallel) ---
CustomerContext(
    account_info={'phone': '+1234567890', 'name': 'Jane Doe', 'plan': 'Unlimited 5G', 'customer_since': '2023-01-15'}, 
    payment_status=None, 
    ticket_history=[{'id': 'TKT-101', 'issue': 'Slow internet speeds', 'status': 'closed'}, {'id': 'TKT-102', 'issue': 'Router rebooting randomly', 'status': 'open'}], 
    data_complete=False, 
    fetch_time_ms=206.05000000068685
)
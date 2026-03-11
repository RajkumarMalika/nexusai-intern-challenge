import asyncio
import random
import logging

# Set up logging for our timeout warnings
logging.basicConfig(level=logging.WARNING, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

async def fetch_crm(phone: str) -> dict:
    """Simulates fetching account info (200-400ms delay)."""
    delay = random.uniform(0.200, 0.400)
    await asyncio.sleep(delay)
    return {
        "phone": phone,
        "name": "Jane Doe",
        "plan": "Unlimited 5G",
        "customer_since": "2023-01-15"
    }

async def fetch_billing(phone: str) -> dict:
    """Simulates fetching payment status (150-350ms delay, 10% failure rate)."""
    delay = random.uniform(0.150, 0.350)
    await asyncio.sleep(delay)
    
    # 10% random chance to raise a TimeoutError
    if random.random() < 0.10:
        raise TimeoutError(f"Billing API timed out for phone {phone}")
        
    return {
        "balance_due": 45.99,
        "status": "paid",
        "next_bill_date": "2026-04-01"
    }

async def fetch_tickets(phone: str) -> list:
    """Simulates fetching ticket history (100-300ms delay)."""
    delay = random.uniform(0.100, 0.300)
    await asyncio.sleep(delay)
    return [
        {"id": "TKT-101", "issue": "Slow internet speeds", "status": "closed"},
        {"id": "TKT-102", "issue": "Router rebooting randomly", "status": "open"}
    ]
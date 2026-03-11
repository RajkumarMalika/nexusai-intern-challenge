import asyncio
import time
import logging
from fetchers import fetch_crm, fetch_billing, fetch_tickets
from models import CustomerContext

logger = logging.getLogger(__name__)

async def fetch_sequential(phone: str) -> CustomerContext:
    """Fetches data one by one. Total time = sum of all delays."""
    start_time = time.perf_counter()
    data_complete = True
    
    # CRM
    crm_data = await fetch_crm(phone)
    
    # Billing (Handled individually to prevent crash on sequential)
    try:
        billing_data = await fetch_billing(phone)
    except TimeoutError as e:
        logger.warning(f"Sequential Failure: {e}")
        billing_data = None
        data_complete = False
        
    # Tickets
    ticket_data = await fetch_tickets(phone)

    fetch_time_ms = (time.perf_counter() - start_time) * 1000

    return CustomerContext(
        account_info=crm_data,
        payment_status=billing_data,
        ticket_history=ticket_data,
        data_complete=data_complete,
        fetch_time_ms=fetch_time_ms
    )

async def fetch_parallel(phone: str) -> CustomerContext:
    """Fetches data concurrently. Total time = longest single delay."""
    start_time = time.perf_counter()
    
    # CRITICAL: return_exceptions=True prevents the entire gather from blowing up 
    # if fetch_billing raises a TimeoutError. It simply returns the exception object in the list.
    results = await asyncio.gather(
        fetch_crm(phone),
        fetch_billing(phone),
        fetch_tickets(phone),
        return_exceptions=True
    )
    
    fetch_time_ms = (time.perf_counter() - start_time) * 1000
    
    # Unpack the results in the exact order we passed them into gather()
    crm_data, billing_data, ticket_data = results
    data_complete = True
    
    # Verify CRM data
    if isinstance(crm_data, Exception):
        logger.warning(f"CRM Fetch Failed: {str(crm_data)}")
        crm_data = None
        data_complete = False
        
    # Verify Billing data
    if isinstance(billing_data, Exception):
        logger.warning(f"Billing Fetch Failed: {str(billing_data)}")
        billing_data = None
        data_complete = False
        
    # Verify Ticket data
    if isinstance(ticket_data, Exception):
        logger.warning(f"Ticket Fetch Failed: {str(ticket_data)}")
        ticket_data = None
        data_complete = False

    return CustomerContext(
        account_info=crm_data,
        payment_status=billing_data,
        ticket_history=ticket_data,
        data_complete=data_complete,
        fetch_time_ms=fetch_time_ms
    )

async def run_comparison():
    phone = "+1234567890"
    
    print("\n--- 🐢 Running Sequential Fetch ---")
    seq_context = await fetch_sequential(phone)
    print(f"Time Taken: {seq_context.fetch_time_ms:.2f} ms")
    print(f"Data Complete: {seq_context.data_complete}")
    
    print("\n--- ⚡ Running Parallel Fetch ---")
    par_context = await fetch_parallel(phone)
    print(f"Time Taken: {par_context.fetch_time_ms:.2f} ms")
    print(f"Data Complete: {par_context.data_complete}")
    
    speedup = seq_context.fetch_time_ms / par_context.fetch_time_ms
    print(f"\n🚀 Parallel execution was {speedup:.2f}x faster!")
    
    print("\n--- Final CustomerContext Object (Parallel) ---")
    print(par_context)

if __name__ == "__main__":
    # Run the script multiple times in your terminal! 
    # Eventually, you will trigger the 10% billing timeout.
    asyncio.run(run_comparison())
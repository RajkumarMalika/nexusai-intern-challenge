from dataclasses import dataclass
from typing import Optional, Dict, Any, List

@dataclass
class CustomerContext:
    account_info: Optional[Dict[str, Any]]
    payment_status: Optional[Dict[str, Any]]
    ticket_history: Optional[List[Dict[str, Any]]]
    data_complete: bool
    fetch_time_ms: float
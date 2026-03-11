from models import CustomerContext

def should_escalate(
    context: CustomerContext, 
    confidence_score: float, 
    sentiment_score: float, 
    intent: str
) -> tuple[bool, str]:
    """
    Evaluates whether an interaction should be handled by the AI or escalated to a human.
    Returns a tuple of (should_escalate: bool, reason: str).
    """
    
    # Rule 4: Absolute Business Rule - Always escalate cancellations
    if intent == "service_cancellation":
        return True, "service_cancellation"
        
    # Rule 2: Emotional state - Angry customers need a human, regardless of AI confidence
    if sentiment_score < -0.6:
        return True, "angry_customer"
        
    # Rule 5: High-value at-risk customers (VIPs with overdue bills)
    is_vip = False
    if context.account_info and "vip" in str(context.account_info.get("plan", "")).lower():
        is_vip = True
        
    is_overdue = False
    if context.payment_status and context.payment_status.get("status") == "overdue":
        is_overdue = True
        
    if is_vip and is_overdue:
        return True, "vip_overdue"

    # Rule 1: Base AI Safety - Low confidence always escalates
    if confidence_score < 0.65:
        return True, "low_confidence"
        
    # Rule 6: Context Safety - If data is missing, we require a much higher confidence threshold
    if not context.data_complete and confidence_score < 0.80:
        return True, "incomplete_data_low_confidence"
        
    # Rule 3: Historical Frustration - Repeat complaints
    if context.ticket_history:
        # Count how many times this exact intent appears in their past tickets
        intent_count = sum(1 for ticket in context.ticket_history if ticket.get("issue") == intent)
        if intent_count >= 3:
            return True, "repeat_complaint"

    # Default fallback: The AI is cleared to handle the interaction
    return False, "handled_by_ai"
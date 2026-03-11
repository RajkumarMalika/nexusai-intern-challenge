import pytest
from models import CustomerContext
from engine import should_escalate

# Helper function to generate a clean base context for our tests
def get_base_context() -> CustomerContext:
    return CustomerContext(
        account_info={"plan": "Standard"},
        payment_status={"status": "paid"},
        ticket_history=[],
        data_complete=True,
        fetch_time_ms=100.0
    )

def test_rule_1_low_confidence():
    """
    Testing Rule 1: Confidence below 0.65 triggers escalation.
    Why it matters: If the AI is unsure, it might hallucinate or give wrong instructions. 
    It is safer to hand off to a human.
    """
    context = get_base_context()
    escalate, reason = should_escalate(context, confidence_score=0.60, sentiment_score=0.5, intent="billing_question")
    assert escalate is True
    assert reason == "low_confidence"

def test_rule_2_angry_customer():
    """
    Testing Rule 2: Sentiment below -0.6 triggers escalation.
    Why it matters: AI struggles with true empathy. Furious customers need a human 
    touch to de-escalate the situation and prevent brand damage.
    """
    context = get_base_context()
    escalate, reason = should_escalate(context, confidence_score=0.90, sentiment_score=-0.8, intent="router_reboot")
    assert escalate is True
    assert reason == "angry_customer"

def test_rule_3_repeat_complaint():
    """
    Testing Rule 3: Intent appearing 3 or more times triggers escalation.
    Why it matters: If the AI hasn't solved the router issue the last 3 times, 
    the customer is stuck in a loop. A human needs to intervene.
    """
    context = get_base_context()
    context.ticket_history = [
        {"issue": "router_reboot"}, {"issue": "router_reboot"}, {"issue": "router_reboot"}
    ]
    escalate, reason = should_escalate(context, confidence_score=0.90, sentiment_score=0.0, intent="router_reboot")
    assert escalate is True
    assert reason == "repeat_complaint"

def test_rule_4_service_cancellation():
    """
    Testing Rule 4: Service cancellation requests are always escalated.
    Why it matters: Retention is critical. Only trained human retention specialists 
    should handle cancellation requests to attempt to save the account.
    """
    context = get_base_context()
    escalate, reason = should_escalate(context, confidence_score=0.99, sentiment_score=0.8, intent="service_cancellation")
    assert escalate is True
    assert reason == "service_cancellation"

def test_rule_5_vip_overdue():
    """
    Testing Rule 5: VIP customers with overdue billing trigger escalation.
    Why it matters: High-value customers shouldn't be auto-suspended by an AI. 
    A human should review to offer grace periods or white-glove service.
    """
    context = get_base_context()
    context.account_info["plan"] = "VIP 5G Plan"
    context.payment_status["status"] = "overdue"
    
    escalate, reason = should_escalate(context, confidence_score=0.90, sentiment_score=0.5, intent="payment_extension")
    assert escalate is True
    assert reason == "vip_overdue"

def test_rule_6_incomplete_data_low_confidence():
    """
    Testing Rule 6: Incomplete data combined with confidence below 0.80 triggers escalation.
    Why it matters: If an API timed out (like billing) AND the AI is slightly unsure (0.75), 
    the risk of a wrong answer compounding with missing context is too high.
    """
    context = get_base_context()
    context.data_complete = False
    
    escalate, reason = should_escalate(context, confidence_score=0.75, sentiment_score=0.5, intent="billing_question")
    assert escalate is True
    assert reason == "incomplete_data_low_confidence"

def test_edge_case_1_happy_cancellation():
    """
    Testing Edge Case 1: Rule Conflict (Rule 4 vs high sentiment/confidence).
    Why it matters: Evaluates precedence. Even if the AI is 100% confident and the customer 
    is extremely happy, a cancellation must still route to a human retention agent.
    """
    context = get_base_context()
    escalate, reason = should_escalate(context, confidence_score=1.0, sentiment_score=1.0, intent="service_cancellation")
    assert escalate is True
    assert reason == "service_cancellation"

def test_edge_case_2_incomplete_data_but_high_confidence():
    """
    Testing Edge Case 2: Incomplete data but exceptionally high AI confidence.
    Why it matters: Proves Rule 6 does not blanket-escalate all missing data. If the AI is 
    95% confident (e.g., answering a generic tech question), it can proceed despite a billing API timeout.
    """
    context = get_base_context()
    context.data_complete = False
    
    escalate, reason = should_escalate(context, confidence_score=0.95, sentiment_score=0.5, intent="generic_tech_support")
    assert escalate is False
    assert reason == "handled_by_ai"
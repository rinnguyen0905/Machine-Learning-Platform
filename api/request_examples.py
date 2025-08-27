"""
Request body examples cho API của Credit Scoring System
"""

# Ví dụ cho Application Scorecard
APPLICATION_EXAMPLE = {
    "customer_id": "CUS000123",
    "age": 35,
    "income": 50000,
    "employment_length": 5.5,
    "debt_to_income": 0.25,
    "credit_history_length": 7,
    "number_of_debts": 2,
    "number_of_delinquent_debts": 0,
    "homeowner": 1
}

# Ví dụ cho Behavior Scorecard
BEHAVIOR_EXAMPLE = {
    "customer_id": "CUS000456",
    "current_balance": 3500,
    "average_monthly_payment": 850,
    "payment_ratio": 0.65,
    "number_of_late_payments": 1,
    "months_since_last_late_payment": 8,
    "number_of_credit_inquiries": 2,
    "current_limit": 10000,
    "average_utilization": 0.35
}

# Ví dụ cho Collections Scoring
COLLECTIONS_EXAMPLE = [
    {
        "customer_id": "CUS000789",
        "days_past_due": 45,
        "outstanding_amount": 2500,
        "number_of_contacts": 3,
        "previous_late_payments": 2,
        "promised_payment_amount": 500,
        "broken_promises": 1,
        "months_on_book": 24,
        "last_payment_amount": 300
    },
    {
        "customer_id": "CUS000790",
        "days_past_due": 60,
        "outstanding_amount": 3600,
        "number_of_contacts": 5,
        "previous_late_payments": 3,
        "promised_payment_amount": 1000,
        "broken_promises": 2,
        "months_on_book": 18,
        "last_payment_amount": 450
    }
]

# Ví dụ cho Desertion Scoring
DESERTION_EXAMPLE = [
    {
        "customer_id": "CUS000321",
        "months_to_maturity": 3,
        "total_relationship_value": 75000,
        "number_of_products": 2,
        "satisfaction_score": 6.5,
        "number_of_complaints": 1,
        "months_since_last_interaction": 2,
        "age": 42,
        "tenure_months": 36,
        "monthly_average_balance": 8500
    },
    {
        "customer_id": "CUS000322",
        "months_to_maturity": 1,
        "total_relationship_value": 125000,
        "number_of_products": 3,
        "satisfaction_score": 8.0,
        "number_of_complaints": 0,
        "months_since_last_interaction": 0.5,
        "age": 35,
        "tenure_months": 60,
        "monthly_average_balance": 12000
    }
]

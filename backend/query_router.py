def route_question(question):
    q = question.lower()

    # Cross-board questions first
    cross_board_terms = [
        "compare",
        "comparison",
        "relationship",
        "sales and operations",
        "pipeline and work",
        "pipeline with work",
        "deals and work orders",
        "deals with work orders",
        "sales pipeline with",
        "sales pipeline and",
        "work-order activity",
        "work order activity",
        "across both",
        "across the boards",
        "overall business",
    ]

    if any(term in q for term in cross_board_terms):
        return "both"

    # Deals / sales questions
    deal_terms = [
        "pipeline",
        "deal",
        "deals",
        "sales",
        "opportunity",
        "opportunities",
        "closure",
        "closing",
        "prospect",
        "lead",
    ]

    if any(term in q for term in deal_terms):
        return "deals"

    # Work-order / operations questions
    work_order_terms = [
        "work order",
        "work orders",
        "work-order",
        "execution",
        "project",
        "projects",
        "billing",
        "billed",
        "invoice",
        "invoiced",
        "collection",
        "collected",
        "receivable",
        "receivables",
        "outstanding",
        "operations",
    ]

    if any(term in q for term in work_order_terms):
        return "work_orders"

    # When unclear, query both datasets
    return "both"
# Monday.com column IDs → meaningful names
from datetime import datetime, date

DEAL_COLUMNS = {
    "color_mm7bwz5": "deal_status",
    "date_mm7bcmha": "close_date",
    "color_mm7brhzn": "closure_probability",
    "numeric_mm7bbz6a": "deal_value",
    "date_mm7b94mh": "tentative_close_date",
    "color_mm7b350a": "deal_stage",
    "color_mm7b9psv": "product_deal",
    "color_mm7bdhg3": "sector",
    "date_mm7b3rfc": "created_date",
}

WORK_ORDER_COLUMNS = {
    "dropdown_mm7ba2t2": "customer_code",
    "color_mm7b30fx": "nature_of_work",
    "color_mm7b2ffe": "execution_status",
    "date_mm7b7p8m": "po_date",
    "date_mm7bhs2t": "probable_start_date",
    "date_mm7b8jmf": "probable_end_date",
    "color_mm7bh5te": "sector",
    "color_mm7b3wyw": "type_of_work",
    "numeric_mm7b30k1": "billed_value_excl_gst",
    "numeric_mm7bnepv": "billed_value_incl_gst",
    "numeric_mm7bhpp2": "collected_amount",
    "numeric_mm7b597": "amount_receivable",
    "numeric_mm7bv813": "quantity_billed",
    "numeric_mm7bkv8z": "balance_quantity",
    "color_mm7by76f": "invoice_status",
    "color_mm7b2p1b": "actual_billing_month",
    "text_mm7btmpq": "actual_collection_month",
    "color_mm7by1cg": "wo_status_billed",
    "text_mm7bzket": "collection_status",
    "text_mm7bqsyc": "collection_date",
    "color_mm7bdkan": "billing_status",
}

def rename_columns(record, mapping):
    cleaned = {
        "id": record.get("id"),
        "name": record.get("name")
    }

    for monday_id, friendly_name in mapping.items():
        cleaned[friendly_name] = record.get(monday_id)

    return cleaned
def to_number(value):
    try:
        if value is None or value == "":
            return 0.0

        value = str(value).replace(",", "").replace("₹", "").strip()
        return float(value)

    except (ValueError, TypeError):
        return 0.0

def data_quality_summary(records, fields):
    quality = {}

    for field in fields:
        missing = sum(
            1 for record in records
            if record.get(field) is None
        )

        if missing > 0:
            quality[field] = missing

    return quality

def parse_date(value):
    if not value:
        return None

    try:
        value = str(value).strip()

        formats = [
            "%Y-%m-%d",
            "%d-%m-%Y",
            "%d/%m/%Y",
            "%m/%d/%Y",
        ]

        for fmt in formats:
            try:
                return datetime.strptime(value, fmt).date()
            except ValueError:
                continue

    except (ValueError, TypeError):
        pass

    return None

def filter_records_by_date(records, date_field, start_date=None, end_date=None):
    filtered = []

    for record in records:
        record_date = parse_date(record.get(date_field))

        if record_date is None:
            continue

        if start_date and record_date < start_date:
           continue

        if end_date and record_date > end_date:
            continue

        filtered.append(record)

    return filtered

def deal_pipeline_by_date(records, start_date=None, end_date=None):
    filtered = filter_records_by_date(
        records,
        "tentative_close_date",
        start_date,
        end_date
    )
   
    open_deals = [
        record for record in filtered
        if str(record.get("deal_status", "")).lower() == "open"
    ]

    return {
        "total_deals": len(filtered),
        "open_deals": len(open_deals),
        "pipeline_value": sum(
            to_number(record.get("deal_value"))
            for record in open_deals
        )
    }

def deal_summary(records):
    total_deals = len(records)

    open_deals = [
        r for r in records
        if str(r.get("deal_status", "")).lower() == "open"
    ]

    pipeline_value = sum(
        to_number(r.get("deal_value"))
        for r in open_deals
    )

    sectors = {}

    for record in open_deals:
        sector = record.get("sector") or "Unknown"
        sectors[sector] = sectors.get(sector, 0) + 1

    stages = {}

    for record in open_deals:
        stage = record.get("deal_stage") or "Unknown"
        stages[stage] = stages.get(stage, 0) + 1

    data_quality = data_quality_summary(
        records,
        [
            "deal_status",
            "close_date",
            "closure_probability",
            "deal_value",
            "deal_stage",
            "sector"
        ]
    )

    return {
        "total_deals": total_deals,
        "open_deals": len(open_deals),
        "pipeline_value": pipeline_value,
        "open_deals_by_sector": sectors,
        "open_deals_by_stage": stages,
        "data_quality": data_quality
    }


def work_order_summary(records):
    total_work_orders = len(records)

    active_orders = [
        r for r in records
        if str(r.get("execution_status", "")).lower()
        not in ["completed", "closed"]
    ]

    billed = sum(
        to_number(r.get("billed_value_incl_gst"))
        for r in records
    )

    collected = sum(
        to_number(r.get("collected_amount"))
        for r in records
    )

    receivable = sum(
        to_number(r.get("amount_receivable"))
        for r in records
    )

    data_quality = data_quality_summary(
    records,
    [
        "customer_code",
        "execution_status",
        "po_date",
        "probable_start_date",
        "probable_end_date",
        "sector",
        "type_of_work",
        "billed_value_incl_gst",
        "collected_amount",
        "amount_receivable",
        "invoice_status",
        "billing_status"
    ]
    )
    return {
        "total_work_orders": total_work_orders,
        "active_work_orders": len(active_orders),
        "total_billed": billed,
        "total_collected": collected,
        "total_receivable": receivable,
        "data_quality": data_quality
    }
def cross_board_summary(deals, work_orders):
    # Open deals by sector
    open_deals_by_sector = {}

    for deal in deals:
        if str(deal.get("deal_status") or "").lower() == "open":
            sector = deal.get("sector") or "Unknown"
            open_deals_by_sector[sector] = (
                open_deals_by_sector.get(sector, 0) + 1
            )

    # Active work orders by sector
    active_work_orders_by_sector = {}

    for order in work_orders:
        status = str(order.get("execution_status") or "").lower()

        if status not in ["completed", "closed"]:
            sector = order.get("sector") or "Unknown"
            active_work_orders_by_sector[sector] = (
                active_work_orders_by_sector.get(sector, 0) + 1
            )

    # Find sectors appearing in either dataset
    sectors = sorted(
        set(open_deals_by_sector) |
        set(active_work_orders_by_sector)
    )

    sector_comparison = {}

    for sector in sectors:
        sector_comparison[sector] = {
            "open_deals": open_deals_by_sector.get(sector, 0),
            "active_work_orders": active_work_orders_by_sector.get(
                sector, 0
            )
        }

    return {
        "open_deals": sum(open_deals_by_sector.values()),
        "active_work_orders": sum(active_work_orders_by_sector.values()),
        "sector_comparison": sector_comparison
    }
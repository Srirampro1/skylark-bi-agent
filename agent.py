from monday_client import get_all_board_items
import pandas as pd


# ============================================================
# MONDAY.COM BOARD IDs
# ============================================================

WORK_ORDERS_BOARD_ID = 5030967820
DEALS_BOARD_ID = 5030967822


# ============================================================
# CONVERT MONDAY DATA TO DATAFRAME
# ============================================================

def convert_to_dataframe(board_data):

    rows = []

    for item in board_data.get("items", []):

        row = {
            "item_id": item.get("id"),
            "item_name": item.get("name")
        }

        for column in item.get("column_values", []):

            column_id = column.get("id")

            column_text = column.get(
                "text",
                ""
            )

            if column_id:
                row[column_id] = column_text

        rows.append(row)

    return pd.DataFrame(rows)


# ============================================================
# LOAD DATA FROM MONDAY.COM
# ============================================================

def load_data():

    print("Loading Monday.com data...")

    work_orders_data = get_all_board_items(
        WORK_ORDERS_BOARD_ID
    )

    deals_data = get_all_board_items(
        DEALS_BOARD_ID
    )

    work_orders = convert_to_dataframe(
        work_orders_data
    )

    deals = convert_to_dataframe(
        deals_data
    )

    return work_orders, deals


# ============================================================
# FIND COLUMN
# ============================================================

def find_column(df, possible_names):

    for name in possible_names:

        if name in df.columns:
            return name

    return None


# ============================================================
# CLEAN NUMBER
# ============================================================

def clean_number(value):

    if pd.isna(value):
        return None

    value = str(value)

    value = value.replace(
        ",",
        ""
    )

    value = value.replace(
        "₹",
        ""
    )

    value = value.strip()

    try:

        return float(value)

    except:

        return None


# ============================================================
# PIPELINE SUMMARY
# ============================================================

def pipeline_summary(deals):

    result = []

    result.append(
        "SALES PIPELINE"
    )

    result.append(
        "=" * 50
    )

    result.append(
        f"Total deals: {len(deals)}"
    )

    # Find columns
    status_col = find_column(
        deals,
        [
            "deal_status",
            "status"
        ]
    )

    stage_col = find_column(
        deals,
        [
            "deal_stage",
            "stage"
        ]
    )

    sector_col = find_column(
        deals,
        [
            "sector_service",
            "sector"
        ]
    )

    value_col = find_column(
        deals,
        [
            "deal_value",
            "value"
        ]
    )

    # --------------------------------------------------------
    # DEAL STATUS
    # --------------------------------------------------------

    if status_col:

        result.append(
            "\nDeal Status:"
        )

        status_counts = (
            deals[status_col]
            .fillna("Missing")
            .astype(str)
            .replace(
                "",
                "Missing"
            )
            .value_counts()
        )

        result.append(
            status_counts.to_string()
        )

    # --------------------------------------------------------
    # DEAL STAGE
    # --------------------------------------------------------

    if stage_col:

        result.append(
            "\nDeal Stage:"
        )

        stage_counts = (
            deals[stage_col]
            .fillna("Missing")
            .astype(str)
            .replace(
                "",
                "Missing"
            )
            .value_counts()
        )

        result.append(
            stage_counts.to_string()
        )

    # --------------------------------------------------------
    # SECTOR
    # --------------------------------------------------------

    if sector_col:

        result.append(
            "\nDeals by Sector:"
        )

        sector_counts = (
            deals[sector_col]
            .fillna("Missing")
            .astype(str)
            .replace(
                "",
                "Missing"
            )
            .value_counts()
        )

        result.append(
            sector_counts.to_string()
        )

    # --------------------------------------------------------
    # DEAL VALUE
    # --------------------------------------------------------

    if value_col:

        values = deals[value_col].apply(
            clean_number
        )

        total_value = (
            values.dropna().sum()
        )

        result.append(
            f"\nTotal pipeline value: "
            f"{total_value:,.2f}"
        )

        result.append(
            f"Missing/non-numeric deal values: "
            f"{values.isna().sum()}"
        )

    return "\n".join(result)


# ============================================================
# SECTOR PIPELINE
# ============================================================

def sector_pipeline(
    deals,
    sector
):

    sector_col = find_column(
        deals,
        [
            "sector_service",
            "sector"
        ]
    )

    if not sector_col:

        return (
            "Sector information is not "
            "available in the Deals board."
        )

    mask = (
        deals[sector_col]
        .fillna("")
        .astype(str)
        .str.contains(
            sector,
            case=False,
            na=False
        )
    )

    sector_deals = deals[mask]

    if len(sector_deals) == 0:

        return (
            f"No deals found for "
            f"{sector.title()}."
        )

    result = []

    result.append(
        f"{sector.title()} Sector Pipeline"
    )

    result.append(
        "=" * 50
    )

    result.append(
        f"Total deals: "
        f"{len(sector_deals)}"
    )

    status_col = find_column(
        sector_deals,
        [
            "deal_status",
            "status"
        ]
    )

    stage_col = find_column(
        sector_deals,
        [
            "deal_stage",
            "stage"
        ]
    )

    value_col = find_column(
        sector_deals,
        [
            "deal_value",
            "value"
        ]
    )

    if status_col:

        result.append(
            "\nDeal Status:"
        )

        result.append(
            sector_deals[status_col]
            .fillna("Missing")
            .astype(str)
            .replace(
                "",
                "Missing"
            )
            .value_counts()
            .to_string()
        )

    if stage_col:

        result.append(
            "\nDeal Stage:"
        )

        result.append(
            sector_deals[stage_col]
            .fillna("Missing")
            .astype(str)
            .replace(
                "",
                "Missing"
            )
            .value_counts()
            .to_string()
        )

    if value_col:

        values = sector_deals[
            value_col
        ].apply(
            clean_number
        )

        result.append(
            f"\nPipeline value: "
            f"{values.dropna().sum():,.2f}"
        )

    return "\n".join(result)


# ============================================================
# WORK ORDER SUMMARY
# ============================================================

def work_order_summary(work_orders):

    result = []

    result.append(
        "WORK ORDER SUMMARY"
    )

    result.append(
        "=" * 50
    )

    result.append(
        f"Total work orders: "
        f"{len(work_orders)}"
    )

    status_col = find_column(
        work_orders,
        [
            "effective_status",
            "execution_status",
            "wo_status"
        ]
    )

    sector_col = find_column(
        work_orders,
        [
            "sector"
        ]
    )

    receivable_col = find_column(
        work_orders,
        [
            "amount_receivable"
        ]
    )

    billed_col = find_column(
        work_orders,
        [
            "billed_value"
        ]
    )

    collected_col = find_column(
        work_orders,
        [
            "collected_amount"
        ]
    )

    # --------------------------------------------------------
    # STATUS
    # --------------------------------------------------------

    if status_col:

        result.append(
            "\nWork Order Status:"
        )

        result.append(
            work_orders[status_col]
            .fillna("Missing")
            .astype(str)
            .replace(
                "",
                "Missing"
            )
            .value_counts()
            .to_string()
        )

    # --------------------------------------------------------
    # SECTOR
    # --------------------------------------------------------

    if sector_col:

        result.append(
            "\nWork Orders by Sector:"
        )

        result.append(
            work_orders[sector_col]
            .fillna("Missing")
            .astype(str)
            .replace(
                "",
                "Missing"
            )
            .value_counts()
            .to_string()
        )

    # --------------------------------------------------------
    # RECEIVABLE
    # --------------------------------------------------------

    if receivable_col:

        values = work_orders[
            receivable_col
        ].apply(
            clean_number
        )

        result.append(
            f"\nTotal receivable: "
            f"{values.dropna().sum():,.2f}"
        )

    # --------------------------------------------------------
    # BILLED
    # --------------------------------------------------------

    if billed_col:

        values = work_orders[
            billed_col
        ].apply(
            clean_number
        )

        result.append(
            f"Total billed: "
            f"{values.dropna().sum():,.2f}"
        )

    # --------------------------------------------------------
    # COLLECTED
    # --------------------------------------------------------

    if collected_col:

        values = work_orders[
            collected_col
        ].apply(
            clean_number
        )

        result.append(
            f"Total collected: "
            f"{values.dropna().sum():,.2f}"
        )

    return "\n".join(result)


# ============================================================
# DATA QUALITY
# ============================================================

def data_quality_report(
    deals,
    work_orders
):

    result = []

    result.append(
        "DATA QUALITY REPORT"
    )

    result.append(
        "=" * 50
    )

    # --------------------------------------------------------
    # DEALS
    # --------------------------------------------------------

    result.append(
        "\nDEALS"
    )

    result.append(
        f"Total records: {len(deals)}"
    )

    for column in deals.columns:

        missing = (
            deals[column]
            .isna()
            .sum()
        )

        blank = (
            deals[column]
            .fillna("")
            .astype(str)
            .str.strip()
            .eq("")
            .sum()
        )

        missing = max(
            missing,
            blank
        )

        if missing > 0:

            result.append(
                f"{column}: "
                f"{missing} missing/blank"
            )

    # --------------------------------------------------------
    # WORK ORDERS
    # --------------------------------------------------------

    result.append(
        "\nWORK ORDERS"
    )

    result.append(
        f"Total records: "
        f"{len(work_orders)}"
    )

    for column in work_orders.columns:

        missing = (
            work_orders[column]
            .isna()
            .sum()
        )

        blank = (
            work_orders[column]
            .fillna("")
            .astype(str)
            .str.strip()
            .eq("")
            .sum()
        )

        missing = max(
            missing,
            blank
        )

        if missing > 0:

            result.append(
                f"{column}: "
                f"{missing} missing/blank"
            )

    return "\n".join(result)


# ============================================================
# CROSS-BOARD ANALYSIS
# ============================================================

def cross_board_analysis(
    deals,
    work_orders
):

    result = []

    # Find client/customer columns
    deal_client_col = find_column(
        deals,
        [
            "client_code",
            "customer_code",
            "client"
        ]
    )

    wo_client_col = find_column(
        work_orders,
        [
            "customer_code",
            "client_code",
            "client"
        ]
    )

    receivable_col = find_column(
        work_orders,
        [
            "amount_receivable"
        ]
    )

    if not deal_client_col:

        return (
            "Client information was not "
            "found in the Deals board."
        )

    if not wo_client_col:

        return (
            "Customer information was not "
            "found in the Work Orders board."
        )

    if not receivable_col:

        return (
            "Receivable information was not "
            "found in the Work Orders board."
        )

    # --------------------------------------------------------
    # FIND OPEN DEALS
    # --------------------------------------------------------

    status_col = find_column(
        deals,
        [
            "deal_status",
            "status"
        ]
    )

    if status_col:

        open_mask = (
            deals[status_col]
            .fillna("")
            .astype(str)
            .str.contains(
                "open",
                case=False,
                na=False
            )
        )

        open_deals = deals[
            open_mask
        ]

    else:

        open_deals = deals

    # --------------------------------------------------------
    # FIND OUTSTANDING RECEIVABLES
    # --------------------------------------------------------

    work_orders_copy = (
        work_orders.copy()
    )

    work_orders_copy[
        "receivable_numeric"
    ] = work_orders_copy[
        receivable_col
    ].apply(
        clean_number
    )

    outstanding = (
        work_orders_copy[
            work_orders_copy[
                "receivable_numeric"
            ] > 0
        ]
    )

    # --------------------------------------------------------
    # CREATE CUSTOMER SETS
    # --------------------------------------------------------

    deal_clients = set(
        open_deals[
            deal_client_col
        ]
        .dropna()
        .astype(str)
        .str.strip()
    )

    receivable_clients = set(
        outstanding[
            wo_client_col
        ]
        .dropna()
        .astype(str)
        .str.strip()
    )

    common_clients = (
        deal_clients &
        receivable_clients
    )

    # --------------------------------------------------------
    # RESULT
    # --------------------------------------------------------

    result.append(
        "CROSS-BOARD CUSTOMER ANALYSIS"
    )

    result.append(
        "=" * 50
    )

    result.append(
        f"Customers with both open deals "
        f"and outstanding receivables: "
        f"{len(common_clients)}"
    )

    if not common_clients:

        result.append(
            "\nNo matching customers were found."
        )

        return "\n".join(result)

    for customer in sorted(
        common_clients
    ):

        customer_deals = open_deals[
            open_deals[
                deal_client_col
            ]
            .fillna("")
            .astype(str)
            .str.strip()
            .eq(customer)
        ]

        customer_work_orders = outstanding[
            outstanding[
                wo_client_col
            ]
            .fillna("")
            .astype(str)
            .str.strip()
            .eq(customer)
        ]

        receivable_total = (
            customer_work_orders[
                "receivable_numeric"
            ]
            .sum()
        )

        result.append(
            f"\nCustomer: {customer}"
        )

        result.append(
            f"Open deals: "
            f"{len(customer_deals)}"
        )

        result.append(
            f"Outstanding receivable: "
            f"{receivable_total:,.2f}"
        )

    result.append(
        "\nManagement insight:"
    )

    result.append(
        "These customers represent both "
        "sales opportunity and collection exposure."
    )

    return "\n".join(result)


# ============================================================
# LEADERSHIP UPDATE
# ============================================================

def leadership_update(
    deals,
    work_orders
):

    result = []

    result.append(
        "LEADERSHIP UPDATE"
    )

    result.append(
        "=" * 50
    )

    result.append(
        "\n1. SALES PIPELINE"
    )

    result.append(
        pipeline_summary(deals)
    )

    result.append(
        "\n2. OPERATIONS & COLLECTIONS"
    )

    result.append(
        work_order_summary(work_orders)
    )

    result.append(
        "\n3. DATA QUALITY"
    )

    result.append(
        data_quality_report(
            deals,
            work_orders
        )
    )

    result.append(
        "\n4. MANAGEMENT TAKEAWAY"
    )

    result.append(
        "Focus on high-value pipeline opportunities, "
        "outstanding receivables and records with "
        "missing critical information."
    )

    return "\n".join(result)


# ============================================================
# QUESTION HANDLER
# ============================================================

def answer_question(
    question,
    deals,
    work_orders
):

    q = question.lower().strip()

    # --------------------------------------------------------
    # CROSS BOARD
    # --------------------------------------------------------

    if (
        (
            "both" in q
            or "customer" in q
            or "customers" in q
        )
        and (
            "deal" in q
            or "pipeline" in q
        )
        and (
            "receivable" in q
            or "collection" in q
        )
    ):

        return cross_board_analysis(
            deals,
            work_orders
        )

    # --------------------------------------------------------
    # DATA QUALITY
    # --------------------------------------------------------

    if (
        "data quality" in q
        or "data issue" in q
        or "data issues" in q
        or "missing data" in q
        or "data problem" in q
        or "data problems" in q
    ):

        return data_quality_report(
            deals,
            work_orders
        )

    # --------------------------------------------------------
    # LEADERSHIP
    # --------------------------------------------------------

    if (
        "leadership" in q
        or "executive update" in q
        or "management update" in q
        or "leadership update" in q
    ):

        return leadership_update(
            deals,
            work_orders
        )

    # --------------------------------------------------------
    # SECTOR DETECTION
    # --------------------------------------------------------

    sectors = [
        "energy",
        "renewable",
        "renewables",
        "mining",
        "powerline",
        "railways",
        "construction"
    ]

    detected_sector = None

    for sector in sectors:

        if sector in q:

            detected_sector = sector
            break

    if detected_sector:

        if (
            "pipeline" in q
            or "deal" in q
            or "sector" in q
        ):

            return sector_pipeline(
                deals,
                detected_sector
            )

    # --------------------------------------------------------
    # PIPELINE
    # --------------------------------------------------------

    if (
        "pipeline" in q
        or "deal" in q
        or "opportunit" in q
    ):

        return pipeline_summary(
            deals
        )

    # --------------------------------------------------------
    # WORK ORDERS
    # --------------------------------------------------------

    if (
        "work order" in q
        or "work orders" in q
        or "operation" in q
        or "project status" in q
    ):

        return work_order_summary(
            work_orders
        )

    # --------------------------------------------------------
    # FINANCIAL
    # --------------------------------------------------------

    if (
        "receivable" in q
        or "receivables" in q
        or "billed" in q
        or "billing" in q
        or "collected" in q
        or "collection" in q
    ):

        return work_order_summary(
            work_orders
        )

    # --------------------------------------------------------
    # HELP
    # --------------------------------------------------------

    return (
        "I can answer questions about:\n\n"
        "• Sales pipeline\n"
        "• Deals\n"
        "• Sector performance\n"
        "• Work orders\n"
        "• Billing\n"
        "• Collections\n"
        "• Receivables\n"
        "• Data quality\n"
        "• Cross-board analysis\n"
        "• Leadership updates\n\n"
        "Examples:\n"
        "• How is our pipeline looking?\n"
        "• How is our energy pipeline?\n"
        "• How much is receivable?\n"
        "• Which customers have both open deals "
        "and outstanding receivables?\n"
        "• What data quality issues do we have?\n"
        "• Give me a leadership update."
    )


# ============================================================
# RUN FROM TERMINAL
# ============================================================

if __name__ == "__main__":

    try:

        work_orders, deals = load_data()

        print("\nData loaded successfully!")

        print(
            "Work Orders:",
            len(work_orders)
        )

        print(
            "Deals:",
            len(deals)
        )

        while True:

            question = input(
                "\nAsk a business question "
                "(type exit to stop): "
            )

            if question.lower().strip() == "exit":

                print("Goodbye!")

                break

            print(
                "\n"
                + "=" * 60
            )

            print(
                "BUSINESS INTELLIGENCE ANSWER"
            )

            print(
                "=" * 60
            )

            answer = answer_question(
                question,
                deals,
                work_orders
            )

            print(answer)

    except Exception as e:

        print("\nERROR")
        print("=" * 60)
        print(str(e))
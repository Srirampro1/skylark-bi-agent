import pandas as pd


def items_to_dataframe(board_data):
    """Convert Monday.com items into a pandas DataFrame."""

    rows = []

    for item in board_data["items"]:

        row = {
            "item_id": item["id"],
            "item_name": item["name"]
        }

        for column in item["column_values"]:
            row[column["id"]] = column["text"]

        rows.append(row)

    return pd.DataFrame(rows)


def count_by_column(df, column):
    """Count records by a column."""

    if column not in df.columns:
        return {}

    return (
        df[column]
        .fillna("Missing")
        .replace("", "Missing")
        .value_counts()
        .to_dict()
    )


def numeric_column(df, column):
    """Safely convert a column to numbers."""

    if column not in df.columns:
        return pd.Series(dtype=float)

    return pd.to_numeric(
        df[column],
        errors="coerce"
    )


def total_numeric(df, column):
    """Calculate total of a numeric column."""

    values = numeric_column(df, column)

    return values.sum()


def get_pipeline_summary(deals_df):
    """Generate sales pipeline summary."""

    result = {
        "total_deals": len(deals_df)
    }

    # Try to find the actual Monday column names
    status_column = find_column(
        deals_df,
        ["deal_status", "status"]
    )

    stage_column = find_column(
        deals_df,
        ["deal_stage", "stage"]
    )

    sector_column = find_column(
        deals_df,
        ["sector_service", "sector"]
    )

    value_column = find_column(
        deals_df,
        ["deal_value", "value"]
    )

    if status_column:
        result["deal_status"] = count_by_column(
            deals_df,
            status_column
        )

    if stage_column:
        result["deal_stage"] = count_by_column(
            deals_df,
            stage_column
        )

    if sector_column:
        result["sector"] = count_by_column(
            deals_df,
            sector_column
        )

    if value_column:
        result["total_deal_value"] = total_numeric(
            deals_df,
            value_column
        )

    return result


def get_work_order_summary(work_orders_df):
    """Generate Work Orders summary."""

    result = {
        "total_work_orders": len(work_orders_df)
    }

    status_column = find_column(
        work_orders_df,
        ["effective_status", "execution_status", "wo_status"]
    )

    sector_column = find_column(
        work_orders_df,
        ["sector"]
    )

    receivable_column = find_column(
        work_orders_df,
        ["amount_receivable"]
    )

    billed_column = find_column(
        work_orders_df,
        ["billed_value"]
    )

    collected_column = find_column(
        work_orders_df,
        ["collected_amount"]
    )

    if status_column:
        result["status"] = count_by_column(
            work_orders_df,
            status_column
        )

    if sector_column:
        result["sector"] = count_by_column(
            work_orders_df,
            sector_column
        )

    if receivable_column:
        result["total_receivable"] = total_numeric(
            work_orders_df,
            receivable_column
        )

    if billed_column:
        result["total_billed"] = total_numeric(
            work_orders_df,
            billed_column
        )

    if collected_column:
        result["total_collected"] = total_numeric(
            work_orders_df,
            collected_column
        )

    return result


def find_column(df, possible_names):
    """Find a matching column safely."""

    for name in possible_names:

        if name in df.columns:
            return name

    return None


def search_dataframe(df, column, value):
    """Search a DataFrame column."""

    if column not in df.columns:
        return pd.DataFrame()

    mask = (
        df[column]
        .fillna("")
        .astype(str)
        .str.contains(
            str(value),
            case=False,
            na=False
        )
    )

    return df[mask]
#!/usr/bin/env python3
"""
Solution for the Allsome Interview Test

Features
--------
* Loads `allsome_interview_test_orders.csv`.
* Allows duplicate order_id only for valid refunds (same order_id, sku, price) or
  multiple line items (different sku/price).
* Rejects duplicate (order_id, sku, price) when both rows have positive quantity.
* Validates:
    - sku matches pattern ^SKU-[A-Z0-9]+$
    - quantity and price are convertible to numbers.
    - Negative quantity allowed only when: (order_id, sku, price) matches a prior positive
      row, the refund row appears after the purchase row, and |quantity| <= purchase quantity.
* Computes:
    - total_revenue = sum(quantity * price) for valid rows
    - best-selling sku = sku with highest summed quantity
* Collects failed rows with reason and row_data.
* Emits JSON with total_revenue, best_selling_sku, and failed_rows.
"""

import csv
import json
import re
import sys
from collections import defaultdict
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple

# ---------------------------------------------------------------------------

CSV_PATH = Path("allsome_interview_test_orders.csv")
OUTPUT_JSON = Path("solution_output.json")

SKU_PATTERN = re.compile(r"^SKU-[A-Z0-9]+$")

# Failure reasons
REASON_MISSING_ORDER_ID = "Missing order_id."
REASON_MISSING_SKU = "Missing sku."
REASON_INVALID_SKU = "sku does not match required format SKU-XXX."
REASON_MISSING_QUANTITY = "Missing quantity."
REASON_QUANTITY_NOT_NUMBER = "quantity is not a number."
REASON_MISSING_PRICE = "Missing price."
REASON_PRICE_NOT_NUMBER = "price is not a number."
REASON_NEGATIVE_PRICE = "price must be non-negative."
REASON_DUPLICATE_ORDER_LINE = "Duplicate (order_id, sku, price) with positive quantity."
REASON_REFUND_WITHOUT_MATCH = "Negative quantity without matching (order_id, sku, price) for refund"
REASON_REFUND_BEFORE_PURCHASE = "Refund row must appear after the purchase row"
REASON_REFUND_EXCEEDS_PURCHASE = "Refund quantity exceeds original purchase quantity."


def validate_row(
    row: Dict[str, str], line_no: int
) -> Tuple[Optional[Tuple[str, float, float]], Optional[str]]:
    """
    Validate a CSV row. Returns (sku, quantity, price) on success, or (None, reason) on failure.
    Allows negative quantity; refund matching is checked separately.
    """
    # ---- order_id ---------------------------------------------------------
    oid = row.get("order_id", "").strip()
    if not oid:
        return None, REASON_MISSING_ORDER_ID

    # ---- sku ---------------------------------------------------------------
    sku = row.get("sku", "").strip()
    if not sku:
        return None, REASON_MISSING_SKU
    if not SKU_PATTERN.match(sku):
        return None, REASON_INVALID_SKU

    # ---- quantity ---------------------------------------------------------
    qty_raw = row.get("quantity", "").strip()
    if not qty_raw:
        return None, REASON_MISSING_QUANTITY
    try:
        quantity = float(qty_raw)
    except ValueError:
        return None, REASON_QUANTITY_NOT_NUMBER

    # ---- price ------------------------------------------------------------
    price_raw = row.get("price", "").strip()
    if not price_raw:
        return None, REASON_MISSING_PRICE
    try:
        price = float(price_raw)
    except ValueError:
        return None, REASON_PRICE_NOT_NUMBER
    if price < 0:
        return None, REASON_NEGATIVE_PRICE

    return (sku, quantity, price), None


def _make_failed_entry(line_no: int, reason: str, row: Dict[str, str]) -> Dict[str, Any]:
    """Build a failed_rows entry."""
    return {
        "line": line_no,
        "reason": reason,
        "row_data": dict(row),
    }


def process_csv(
    csv_path: Path,
) -> Tuple[float, str, int, List[Dict[str, Any]]]:
    """
    Single-pass processing. Refund rows must appear after the purchase row,
    and refund quantity must not exceed the original purchase quantity.

    Returns (total_revenue, best_sku, best_quantity, failed_rows).
    """
    failed_rows: List[Dict[str, Any]] = []
    # Remaining refundable quantity per (order_id, sku, price)
    remaining_positive: Dict[Tuple[str, str, float], float] = {}
    order_lines_seen: Set[Tuple[str, str, float]] = set()
    sku_quantity: Dict[str, float] = defaultdict(float)
    total_revenue = 0.0

    with csv_path.open(newline="") as f:
        reader = csv.DictReader(f)
        for line_no, row in enumerate(reader, start=2):
            parsed, reason = validate_row(row, line_no)
            if reason:
                failed_rows.append(_make_failed_entry(line_no, reason, row))
                continue

            sku, quantity, price = parsed
            oid = row.get("order_id", "").strip()
            key = (oid, sku, price)

            if quantity > 0:
                if key in order_lines_seen:
                    failed_rows.append(
                        _make_failed_entry(line_no, REASON_DUPLICATE_ORDER_LINE, row)
                    )
                    continue
                order_lines_seen.add(key)
                remaining_positive[key] = remaining_positive.get(key, 0) + quantity
            else:
                # Refund: must appear after purchase (remaining exists) and |qty| <= remaining
                refund_qty = abs(quantity)
                if key not in remaining_positive or remaining_positive[key] <= 0:
                    failed_rows.append(
                        _make_failed_entry(line_no, REASON_REFUND_BEFORE_PURCHASE, row)
                    )
                    continue
                if refund_qty > remaining_positive[key]:
                    failed_rows.append(
                        _make_failed_entry(line_no, REASON_REFUND_EXCEEDS_PURCHASE, row)
                    )
                    continue
                remaining_positive[key] -= refund_qty

            # Process valid row
            total_revenue += quantity * price
            sku_quantity[sku] += quantity

    # ---- Best-selling SKU --------------------------------------------------
    best_sku = ""
    best_quantity = 0
    if sku_quantity:
        best_sku, best_qty_float = max(sku_quantity.items(), key=lambda kv: kv[1])
        best_quantity = int(best_qty_float)

    return total_revenue, best_sku, best_quantity, failed_rows


def main() -> None:
    """Entry point – orchestrates processing and prints JSON."""
    try:
        revenue, best_sku, best_qty, failed_rows = process_csv(CSV_PATH)
    except Exception as exc:
        print(f"❌  Processing failed: {exc}", file=sys.stderr)
        sys.exit(1)

    result = {
        "total_revenue": round(revenue, 2),
        "best_selling_sku": {
            "sku": best_sku,
            "total_quantity": best_qty,
        },
        "failed_rows": failed_rows,
    }

    OUTPUT_JSON.write_text(json.dumps(result, indent=2))
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()

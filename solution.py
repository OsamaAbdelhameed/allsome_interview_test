#!/usr/bin/env python3
"""
Solution for the Allsome Interview Test

Features
--------
* Loads `allsome_interview_test_orders.csv`.
* Rejects duplicate `order_id`s.
* Validates:
    - `sku` matches pattern `^SKU-[A-Z0-9]+$`
    - `quantity` and `price` are convertible to numbers.
* Computes:
    - total_revenue = Σ quantity * price
    - best-selling sku = sku with highest summed quantity
* Emits JSON exactly as required.
"""

import csv
import json
import re
import sys
from collections import defaultdict
from pathlib import Path
from typing import Dict, Tuple

# ---------------------------------------------------------------------------

CSV_PATH = Path("allsome_interview_test_orders.csv")
OUTPUT_JSON = Path("solution_output.json")
DUPLICATE_ORDER_MSG = "Error: duplicate order_id '{}' found."

SKU_PATTERN = re.compile(r"^SKU-[A-Z0-9]+$")


def validate_row(row: Dict[str, str], line_no: int) -> Tuple[str, float, float]:
    """Validate a CSV row and return clean sku, quantity, price."""
    # ---- order_id ---------------------------------------------------------
    # (no action here – duplicate detection is done later)

    # ---- sku ---------------------------------------------------------------
    sku = row.get("sku", "").strip()
    if not sku:
        raise ValueError(f"Row {line_no}: missing sku.")
    if not SKU_PATTERN.match(sku):
        raise ValueError(f"Row {line_no}: sku '{sku}' does not match required format SKU-XXX.")

    # ---- quantity -----------------------------------------------------------
    qty_raw = row.get("quantity", "").strip()
    if not qty_raw:
        raise ValueError(f"Row {line_no}: missing quantity.")
    try:
        quantity = float(qty_raw)
    except ValueError:
        raise ValueError(f"Row {line_no}: quantity '{qty_raw}' is not a number.")
    if quantity < 0:
        raise ValueError(f"Row {line_no}: quantity must be non‑negative (got {quantity}).")

    # ---- price --------------------------------------------------------------
    price_raw = row.get("price", "").strip()
    if not price_raw:
        raise ValueError(f"Row {line_no}: missing price.")
    try:
        price = float(price_raw)
    except ValueError:
        raise ValueError(f"Row {line_no}: price '{price_raw}' is not a number.")
    if price < 0:
        raise ValueError(f"Row {line_no}: price must be non‑negative (got {price}).")

    return sku, quantity, price


def process_csv(csv_path: Path) -> Tuple[float, str, int]:
    """
    Reads the CSV, validates data, prevents duplicate order_id,
    and returns (total_revenue, best_sku, best_quantity).
    """
    order_ids_seen = set()
    sku_quantity: Dict[str, float] = defaultdict(float)
    total_revenue = 0.0

    with csv_path.open(newline="") as f:
        reader = csv.DictReader(f)
        for line_no, row in enumerate(reader, start=2):  # start=2 → accounting for header line
            # 1️⃣ Duplicate order_id detection
            oid = row.get("order_id", "").strip()
            if not oid:
                raise ValueError(f"Row {line_no}: missing order_id.")
            if oid in order_ids_seen:
                raise ValueError(DUPLICATE_ORDER_MSG.format(oid))
            order_ids_seen.add(oid)

            # 2️⃣ Validation of fields
            sku, quantity, price = validate_row(row, line_no)

            # 3️⃣ Revenue accumulation
            total_revenue += quantity * price

            # 4️⃣ SKU aggregation
            sku_quantity[sku] += quantity

    # Identify best‑selling sku
    if not sku_quantity:
        raise RuntimeError("No valid SKU data found.")
    best_sku, best_quantity = max(sku_quantity.items(), key=lambda kv: kv[1])

    return total_revenue, best_sku, int(best_quantity)


def main() -> None:
    """Entry point – orchestrates processing and prints JSON."""
    try:
        revenue, best_sku, best_qty = process_csv(CSV_PATH)
    except Exception as exc:
        print(f"❌  Processing failed: {exc}", file=sys.stderr)
        sys.exit(1)

    result = {
        "total_revenue": round(revenue, 2),
        "best_selling_sku": {
            "sku": best_sku,
            "total_quantity": best_qty,
        },
    }

    # Write human‑readable JSON file (optional)
    OUTPUT_JSON.write_text(json.dumps(result, indent=2))
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
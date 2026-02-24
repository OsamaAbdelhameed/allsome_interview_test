# Allsome Interview Test – Solution

Two implementations (Python and PHP) that process the provided `allsome_interview_test_orders.csv`
and produce the required JSON analytics. Both produce identical output.

## Project Layout

```
allsome_interview_test/
│
├─ solution.py                         # Python implementation
├─ solution.php                        # PHP implementation
├─ allsome_interview_test_orders.csv   # (provided) sample dataset
├─ solution_output.json                # output file
└─ README.md                           # this file
```

## Prerequisites

| Implementation | Requirement |
|----------------|-------------|
| Python | Python 3.8+ (standard library only, no external packages) |
| PHP | PHP 8.1+ (CLI, no extensions required) |

### Installing Python (if not already installed)

```bash
# Ubuntu / Debian
sudo apt update && sudo apt install -y python3

# macOS (with Homebrew)
brew install python3

# Verify
python3 --version
```

### Installing PHP (if not already installed)

```bash
# Ubuntu / Debian
sudo apt update && sudo apt install -y php-cli

# macOS (with Homebrew)
brew install php

# Verify
php --version
```

## How to Run

### Python

```bash
cd path/to/allsome_interview_test
python3 solution.py
```

### PHP

```bash
cd path/to/allsome_interview_test
php solution.php
```

Both scripts will:
* Print the JSON result to stdout (so you can pipe it elsewhere).
* Write the same JSON to `solution_output.json` for later reference.

## Output Structure

The script emits JSON with:

| Field | Description |
|-------|-------------|
| `total_revenue` | Sum of (quantity × price) for all valid rows |
| `best_selling_sku` | The SKU with the highest total quantity |
| `failed_rows` | Array of rows that could not be processed, each with `line`, `reason`, and `row_data` |

Example (with the provided CSV):

```json
{
  "total_revenue": 710.0,
  "best_selling_sku": {
    "sku": "SKU-A123",
    "total_quantity": 5
  },
  "failed_rows": [
    {"line": 8, "reason": "sku does not match required format SKU-XXX.", "row_data": {...}},
    {"line": 9, "reason": "Missing quantity.", "row_data": {...}},
    ...
  ]
}
```

See the [CSV Record Explanations](#csv-record-explanations) table for a full breakdown of each row.

## CSV Record Explanations

Each row in `allsome_interview_test_orders.csv` is processed and validated. Below is an explanation for each record:

| Line | Record | Status | Explanation |
|------|--------|--------|-------------|
| 2 | `1001,SKU-A123,2,50.0` | Valid | Order 1001: 2 units of SKU-A123 at 50.0. Revenue: 100. |
| 3 | `1002,SKU-B456,1,120.0` | Valid | Order 1002: 1 unit of SKU-B456 at 120.0. Revenue: 120. |
| 4 | `1003,SKU-A123,3,50.0` | Valid | Order 1003: 3 units of SKU-A123 at 50.0. Revenue: 150. |
| 5 | `1004,SKU-C789,5,20.0` | Valid | Order 1004: 5 units of SKU-C789 at 20.0. Revenue: 100. |
| 6 | `1005,SKU-B456,2,120.0` | Valid | Order 1005: 2 units of SKU-B456 at 120.0. Revenue: 240. |
| 7 | `1005,SKU-B456,-2,120` | Valid | Refund for order 1005: refunds 2 units (matches line 6). Revenue: -240. |
| 8 | `100,SKlksd,2,10` | Failed | SKU must match `SKU-XXX` (uppercase letters/numbers). `SKlksd` is invalid. |
| 9 | `1006,SKU-B345,,194` | Failed | Missing quantity (empty field). |
| 10 | `1006,SKU-B345,194,` | Failed | Missing price (empty field). |
| 11 | `1005,,-2,120` | Failed | Missing SKU (empty field). |
| 12 | `,SKU-C789,5,20.0` | Failed | Missing order_id (empty field). |
| 13 | `,,` | Failed | Missing order_id (and other required fields). |
| 14 | `1007,SKU-B456,2,120.0` | Valid | Order 1007: 2 units of SKU-B456 at 120.0. Revenue: 240. |

**Valid rows (2–7, 14)** contribute to `total_revenue` and `best_selling_sku`. **Failed rows (8–13)** appear in `failed_rows` with their reason.

## Refund Rules

**Negative quantities** are accepted only when they represent valid refunds:

1. **Order matters**: The refund row must appear **after** the purchase row in the CSV (the positive row must come first).
2. **Matching key**: The refund must have the same `order_id`, `sku`, and `price` as a prior purchase row.
3. **Quantity limit**: The refund quantity (in absolute value) must be less than or equal to the original purchase quantity.

**Valid refund example:**
```
1001,SKU-A123,5,50.0     ← original purchase (first)
1001,SKU-A123,-2,50.0    ← valid refund (second, |−2| ≤ 5)
```

**Invalid examples:**
```
1006,SKU-B456,-5,30      ← invalid: no prior purchase row with (1006, SKU-B456, 30)
1001,SKU-A123,-2,50.0    ← invalid if this appears before the purchase row
1001,SKU-A123,3,50.0
1001,SKU-A123,-5,50.0    ← invalid: refund (5) exceeds purchase (3)
```

## Error Handling

The script **does not abort** on the first error. Instead it:

* Continues processing all rows in the CSV.
* Collects invalid rows into the `failed_rows` array with:
  * `line` – 1-based line number in the CSV
  * `reason` – human-readable explanation
  * `row_data` – the raw row data

Invalid rows include:
* Missing or malformed `order_id`, `sku`, `quantity`, or `price`.
* Negative `price`.
* Refund row appearing before the purchase row.
* Refund quantity exceeding the original purchase quantity.
* Duplicate `(order_id, sku, price)` when both rows have positive quantity.

If the script cannot open the CSV or hits an unexpected error, it prints to stderr and exits with code 1.

## Testing / Extending

* **Python**: Drop the script into any environment that has Python 3. Replace `CSV_PATH` in `solution.py` with a different file path if needed. The function `process_csv` can be imported and unit-tested independently.
* **PHP**: Drop the script into any environment that has PHP 8.1+ CLI. Replace `$CSV_PATH` in `solution.php` with a different file path if needed. The `processCsv` function can be called from other PHP code.

## Example Revenue Calculation

For the sample CSV (valid rows: 2–7, 14):

* SKU-A123: (2 × 50) + (3 × 50) = 250
* SKU-B456: (1 × 120) + (2 × 120 − 2 × 120) + (2 × 120) = 120 + 0 + 240 = 360
* SKU-C789: (5 × 20) = 100  
* **Total revenue** = 250 + 360 + 100 = 710.0  
* **Best-selling SKU** = SKU-A123 with total quantity 5  

Failed rows (8–13) are listed in `failed_rows` with their specific validation reason.

## License

This solution is provided as-is for evaluation purposes.

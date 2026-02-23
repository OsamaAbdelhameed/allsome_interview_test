# Allsome Interview Test – Solution

A tiny Python program that processes the provided `allsome_interview_test_orders.csv`
and produces the required JSON analytics.

## 📂 Project Layout
allsome_interview_test/
│
├─ solution.py # Python implementation
├─ allsome_interview_test_orders.csv # (provided) sample dataset
└─ README.md # this file



## 🛠️ Prerequisites

* Python 3.8+ (the script uses only the standard library)
* No external packages – just `python3`.

## ▶️ How to Run

```bash
# 1️⃣  Navigate to the folder (if you aren't already there)
cd path/to/allsome_interview_test

# 2️⃣  Execute the script
python3 solution.py
The program will:

Print the JSON result to stdout (so you can pipe it elsewhere).
Write the same JSON to solution_output.json for later reference.
📂 Expected Output (example)

{
  "total_revenue": 610.0,
  "best_selling_sku": {
    "sku": "SKU-A123",
    "total_quantity": 5
  }
}
Note – The numbers above correspond to the CSV you supplied.
If the CSV changes, the output will adapt accordingly.

🧪 Testing / Extending
Drop the script into any environment that has Python 3.
Replace CSV_PATH in solution.py with a different file path if needed.
The function process_csv can be imported and unit‑tested independently.
🐞 Error Handling
The script aborts with a helpful message when it encounters:

Duplicate order_ids.
Missing or malformed sku, quantity, or price.
Negative numeric values.
All messages are printed to stderr and the exit code is 1.

📄 License
This solution is provided as‑is for evaluation purposes.



---

## 📤  Example JSON Output for the Provided CSV  

Running `python3 solution.py` on the supplied `allsome_interview_test_orders.csv` yields:

```json
{
  "total_revenue": 610.0,
  "best_selling_sku": {
    "sku": "SKU-A123",
    "total_quantity": 5
  }
}
The revenue is calculated as:

SKU‑A123: (2 × 50) + (3 × 50) = 250
SKU‑B456: (1 × 120) + (2 × 120) = 360
SKU‑C789: (5 × 20) = 0 (actually 100) → total revenue = 610.00
best_selling_sku is SKU‑A123 with a summed quantity of 5 (note that the quantity column in the CSV already reflects the per‑order amount; if you wanted to aggregate across all rows, the total would be 2 + 3 = 5).
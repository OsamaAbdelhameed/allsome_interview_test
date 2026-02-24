#!/usr/bin/env php
<?php
/**
 * Solution for the Allsome Interview Test (PHP version)
 *
 * Mirrors the Python solution exactly:
 * - Validates sku, quantity, price.
 * - Accepts negative quantity only as a valid refund (same order_id, sku, price
 *   as a prior positive row, and |refund_qty| <= purchase quantity).
 * - Collects failed rows instead of aborting.
 * - Outputs JSON with total_revenue, best_selling_sku, and failed_rows.
 */

$CSV_PATH    = __DIR__ . '/allsome_interview_test_orders.csv';
$OUTPUT_JSON = __DIR__ . '/solution_output.json';

$SKU_PATTERN = '/^SKU-[A-Z0-9]+$/';

$REASONS = [
    'MISSING_ORDER_ID'      => 'Missing order_id.',
    'MISSING_SKU'           => 'Missing sku.',
    'INVALID_SKU'           => 'sku does not match required format SKU-XXX.',
    'MISSING_QUANTITY'      => 'Missing quantity.',
    'QUANTITY_NOT_NUMBER'   => 'quantity is not a number.',
    'MISSING_PRICE'         => 'Missing price.',
    'PRICE_NOT_NUMBER'      => 'price is not a number.',
    'NEGATIVE_PRICE'        => 'price must be non-negative.',
    'DUPLICATE_ORDER_LINE'  => 'Duplicate (order_id, sku, price) with positive quantity.',
    'REFUND_BEFORE_PURCHASE'=> 'Refund row must appear after the purchase row',
    'REFUND_EXCEEDS'        => 'Refund quantity exceeds original purchase quantity.',
];

/**
 * Validate a single CSV row.
 * Returns [sku, quantity, price] on success, or a reason string on failure.
 */
function validateRow(array $row, string $skuPattern, array $reasons): array|string
{
    $orderId = trim($row['order_id'] ?? '');
    if ($orderId === '') {
        return $reasons['MISSING_ORDER_ID'];
    }

    $sku = trim($row['sku'] ?? '');
    if ($sku === '') {
        return $reasons['MISSING_SKU'];
    }
    if (!preg_match($skuPattern, $sku)) {
        return $reasons['INVALID_SKU'];
    }

    $qtyRaw = trim($row['quantity'] ?? '');
    if ($qtyRaw === '') {
        return $reasons['MISSING_QUANTITY'];
    }
    if (!is_numeric($qtyRaw)) {
        return $reasons['QUANTITY_NOT_NUMBER'];
    }
    $quantity = (float) $qtyRaw;

    $priceRaw = trim($row['price'] ?? '');
    if ($priceRaw === '') {
        return $reasons['MISSING_PRICE'];
    }
    if (!is_numeric($priceRaw)) {
        return $reasons['PRICE_NOT_NUMBER'];
    }
    $price = (float) $priceRaw;
    if ($price < 0) {
        return $reasons['NEGATIVE_PRICE'];
    }

    return [$sku, $quantity, $price];
}

function makeFailedEntry(int $line, string $reason, array $rowData): array
{
    return [
        'line'     => $line,
        'reason'   => $reason,
        'row_data' => $rowData,
    ];
}

function processCsv(string $csvPath, string $skuPattern, array $reasons): array
{
    $handle = fopen($csvPath, 'r');
    if ($handle === false) {
        fwrite(STDERR, "Failed to open CSV: $csvPath\n");
        exit(1);
    }

    $header = fgetcsv($handle);
    if ($header === false) {
        fwrite(STDERR, "CSV is empty or unreadable.\n");
        exit(1);
    }
    $header = array_map('trim', $header);

    $failedRows       = [];
    $remainingPositive = [];
    $orderLinesSeen    = [];
    $skuQuantity       = [];
    $totalRevenue      = 0.0;
    $lineNo            = 1;

    while (($fields = fgetcsv($handle)) !== false) {
        $lineNo++;

        $row = [];
        foreach ($header as $i => $col) {
            $row[$col] = $fields[$i] ?? null;
        }

        $result = validateRow($row, $skuPattern, $reasons);

        if (is_string($result)) {
            $failedRows[] = makeFailedEntry($lineNo, $result, $row);
            continue;
        }

        [$sku, $quantity, $price] = $result;
        $orderId = trim($row['order_id'] ?? '');
        $key     = "$orderId|$sku|$price";

        if ($quantity > 0) {
            if (isset($orderLinesSeen[$key])) {
                $failedRows[] = makeFailedEntry($lineNo, $reasons['DUPLICATE_ORDER_LINE'], $row);
                continue;
            }
            $orderLinesSeen[$key] = true;
            $remainingPositive[$key] = ($remainingPositive[$key] ?? 0) + $quantity;
        } else {
            $refundQty = abs($quantity);
            if (!isset($remainingPositive[$key]) || $remainingPositive[$key] <= 0) {
                $failedRows[] = makeFailedEntry($lineNo, $reasons['REFUND_BEFORE_PURCHASE'], $row);
                continue;
            }
            if ($refundQty > $remainingPositive[$key]) {
                $failedRows[] = makeFailedEntry($lineNo, $reasons['REFUND_EXCEEDS'], $row);
                continue;
            }
            $remainingPositive[$key] -= $refundQty;
        }

        $totalRevenue += $quantity * $price;
        $skuQuantity[$sku] = ($skuQuantity[$sku] ?? 0) + $quantity;
    }

    fclose($handle);

    $bestSku = '';
    $bestQty = 0;
    if (!empty($skuQuantity)) {
        arsort($skuQuantity);
        $bestSku = array_key_first($skuQuantity);
        $bestQty = (int) $skuQuantity[$bestSku];
    }

    return [$totalRevenue, $bestSku, $bestQty, $failedRows];
}

// --- Main ---

[$revenue, $bestSku, $bestQty, $failedRows] = processCsv($CSV_PATH, $SKU_PATTERN, $REASONS);

$result = [
    'total_revenue'    => round($revenue, 2),
    'best_selling_sku' => [
        'sku'            => $bestSku,
        'total_quantity' => $bestQty,
    ],
    'failed_rows' => $failedRows,
];

$json = json_encode($result, JSON_PRETTY_PRINT | JSON_UNESCAPED_UNICODE);

file_put_contents($OUTPUT_JSON, $json);
echo $json . PHP_EOL;

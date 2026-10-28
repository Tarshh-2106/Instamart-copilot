# Raw data audit

## customers.csv — shape (1200, 5)

Column | dtype | missing count | missing percent
---|---|---:|---:
customer_id | str | 0 | 0.00%
city | str | 0 | 0.00%
signup_date | str | 0 | 0.00%
age | float64 | 61 | 5.08%
gender | str | 30 | 2.50%

## orders.csv — shape (13084, 9)

Column | dtype | missing count | missing percent
---|---|---:|---:
order_id | str | 0 | 0.00%
customer_id | str | 0 | 0.00%
product_id | str | 0 | 0.00%
quantity | int64 | 0 | 0.00%
order_ts | str | 0 | 0.00%
status | str | 0 | 0.00%
discount_pct | int64 | 0 | 0.00%
order_amount | str | 53 | 0.41%
delivery_minutes | float64 | 2541 | 19.42%

## tickets.csv — shape (164, 5)

Column | dtype | missing count | missing percent
---|---|---:|---:
ticket_id | str | 0 | 0.00%
customer_id | str | 0 | 0.00%
order_id | str | 8 | 4.88%
text | str | 4 | 2.44%
true_category | str | 0 | 0.00%

## Required raw-data checkpoints

Metric | Count
---|---:
raw order rows | 13084
exact duplicate order rows | 119
pending rows | 656
distinct order IDs | 12309
non-numeric amounts | 120
negative delivery times | 106
blank delivery times | 2541
blank ages | 61
ages outside 10–100 | 6
distinct raw city spellings | 24
distinct nonblank gender spellings | 10
blank genders | 30

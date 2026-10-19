
-- 1. Total records in each table
SELECT 'customers' AS table_name, COUNT(*) AS total_rows FROM customers
UNION ALL
SELECT 'products', COUNT(*) FROM products
UNION ALL
SELECT 'orders', COUNT(*) FROM orders
UNION ALL
SELECT 'tickets', COUNT(*) FROM tickets;

-- 2. Order status distribution
SELECT status, COUNT(*) AS total_orders
FROM orders
GROUP BY status
ORDER BY total_orders DESC;

-- 3. Monthly order volume
SELECT substr(order_ts, 1, 7) AS order_month, COUNT(*) AS total_orders
FROM orders
GROUP BY order_month
ORDER BY order_month;

-- 4. Revenue by order status
SELECT status, ROUND(SUM(order_amount), 2) AS total_amount
FROM orders
GROUP BY status
ORDER BY total_amount DESC;

-- 5. Average delivery time by order status
SELECT status, ROUND(AVG(delivery_minutes), 2) AS avg_delivery_minutes
FROM orders
WHERE delivery_minutes IS NOT NULL
GROUP BY status;

-- 6. Top 10 customers by spending on completed orders
SELECT customer_id, ROUND(SUM(order_amount), 2) AS total_spending,
       COUNT(*) AS completed_orders
FROM orders
WHERE status = 'completed'
GROUP BY customer_id
ORDER BY total_spending DESC
LIMIT 10;

-- 7. Top 10 products by quantity ordered
SELECT p.product_id, p.product_name, SUM(o.quantity) AS total_quantity
FROM orders o
JOIN products p ON o.product_id = p.product_id
GROUP BY p.product_id, p.product_name
ORDER BY total_quantity DESC
LIMIT 10;

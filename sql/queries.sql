
SELECT 'customers' AS table_name, COUNT(*) AS total_rows FROM customers
UNION ALL
SELECT 'products', COUNT(*) FROM products
UNION ALL
SELECT 'orders', COUNT(*) FROM orders
UNION ALL
SELECT 'tickets', COUNT(*) FROM tickets;

SELECT status, COUNT(*) AS total_orders
FROM orders
GROUP BY status
ORDER BY total_orders DESC;

SELECT substr(order_ts, 1, 7) AS order_month, COUNT(*) AS total_orders
FROM orders
GROUP BY order_month
ORDER BY order_month;

SELECT status, COUNT(*) AS total_orders,
       COUNT(order_amount) AS orders_with_amount,
       ROUND(SUM(order_amount), 2) AS total_amount
FROM orders
GROUP BY status
ORDER BY status;

SELECT status, ROUND(AVG(delivery_minutes), 2) AS avg_delivery_minutes
FROM orders
WHERE delivery_minutes IS NOT NULL
GROUP BY status;

SELECT customer_id, ROUND(SUM(order_amount), 2) AS total_spending,
       COUNT(*) AS completed_orders
FROM orders
WHERE status = 'completed'
GROUP BY customer_id
ORDER BY total_spending DESC
LIMIT 10;

SELECT p.product_id, p.product_name, SUM(o.quantity) AS total_quantity
FROM orders o
JOIN products p ON o.product_id = p.product_id
GROUP BY p.product_id, p.product_name
ORDER BY total_quantity DESC
LIMIT 10;

SELECT COUNT(*) AS missing_order_amounts
FROM orders
WHERE order_amount IS NULL;

SELECT COUNT(*) AS missing_delivery_minutes
FROM orders
WHERE delivery_minutes IS NULL;

SELECT substr(order_ts, 1, 7) AS order_month,
       ROUND(SUM(order_amount), 2) AS completed_revenue
FROM orders
WHERE status = 'completed'
GROUP BY order_month
ORDER BY order_month;

SELECT discount_pct, COUNT(*) AS total_orders
FROM orders
GROUP BY discount_pct
ORDER BY discount_pct;

SELECT c.city, COUNT(o.order_id) AS completed_orders,
       ROUND(SUM(o.order_amount), 2) AS completed_revenue
FROM orders o
JOIN customers c ON o.customer_id = c.customer_id
WHERE o.status = 'completed'
GROUP BY c.city
ORDER BY completed_revenue DESC;

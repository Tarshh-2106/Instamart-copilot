-- Q1: WHERE and HAVING
SELECT customer_id, SUM(order_amount) AS qualifying_spend
FROM orders
WHERE status = 'completed' AND order_amount > 500
GROUP BY customer_id
HAVING SUM(order_amount) > 8000
ORDER BY qualifying_spend DESC;

-- Q2: revenue by city and product category
SELECT c.city, p.category, ROUND(SUM(o.order_amount), 2) AS revenue_inr
FROM orders o
JOIN customers c ON c.customer_id = o.customer_id
JOIN products p ON p.product_id = o.product_id
WHERE o.status = 'completed'
GROUP BY c.city, p.category
ORDER BY c.city, p.category;

-- Q3: products priced above the catalogue average
SELECT product_id, product_name, price_inr
FROM products
WHERE price_inr > (SELECT AVG(price_inr) FROM products)
ORDER BY price_inr DESC;

-- Q4: customers with no completed order
SELECT c.customer_id
FROM customers c
LEFT JOIN orders o
  ON o.customer_id = c.customer_id AND o.status = 'completed'
WHERE o.order_id IS NULL
ORDER BY c.customer_id;

-- Q5: customers spending above the customer-level average
WITH customer_spend AS (
    SELECT customer_id, SUM(order_amount) AS total_spend
    FROM orders
    WHERE status = 'completed'
    GROUP BY customer_id
),
average_spend AS (
    SELECT AVG(total_spend) AS average_total
    FROM customer_spend
)
SELECT customer_spend.customer_id, customer_spend.total_spend,
       average_spend.average_total
FROM customer_spend CROSS JOIN average_spend
WHERE customer_spend.total_spend > average_spend.average_total
ORDER BY customer_spend.total_spend DESC;

-- Q6: customer spend rankings within city
WITH customer_spend AS (
    SELECT c.city, c.customer_id, SUM(o.order_amount) AS total_spend
    FROM customers c
    JOIN orders o ON o.customer_id = c.customer_id
    WHERE o.status = 'completed'
    GROUP BY c.city, c.customer_id
)
SELECT city, customer_id, ROUND(total_spend, 2) AS total_spend,
       RANK() OVER (PARTITION BY city ORDER BY total_spend DESC) AS spend_rank,
       DENSE_RANK() OVER (PARTITION BY city ORDER BY total_spend DESC) AS dense_rank,
       ROW_NUMBER() OVER (PARTITION BY city ORDER BY total_spend DESC) AS row_number
FROM customer_spend
ORDER BY city, spend_rank, customer_id;

-- Q7: monthly completed revenue
SELECT substr(order_ts, 1, 7) AS order_month,
       ROUND(SUM(order_amount), 2) AS completed_revenue
FROM orders
WHERE status = 'completed'
GROUP BY order_month
ORDER BY order_month;

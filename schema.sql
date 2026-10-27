-- ============================================
--  SHOP EXPENSE & INVENTORY TRACKER SCHEMA
-- ============================================

CREATE DATABASE IF NOT EXISTS shop_tracker;
USE shop_tracker;

-- Products / Items table
CREATE TABLE IF NOT EXISTS products (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    category VARCHAR(50),
    unit VARCHAR(20) DEFAULT 'pcs',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Stock Purchases (what you bought)
CREATE TABLE IF NOT EXISTS purchases (
    id INT AUTO_INCREMENT PRIMARY KEY,
    product_id INT NOT NULL,
    quantity DECIMAL(10,2) NOT NULL,
    cost_per_unit DECIMAL(10,2) NOT NULL,
    total_cost DECIMAL(10,2) GENERATED ALWAYS AS (quantity * cost_per_unit) STORED,
    purchase_date DATE NOT NULL,
    month INT GENERATED ALWAYS AS (MONTH(purchase_date)) STORED,
    year INT GENERATED ALWAYS AS (YEAR(purchase_date)) STORED,
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE CASCADE
);

-- Sales table (what you sold)
CREATE TABLE IF NOT EXISTS sales (
    id INT AUTO_INCREMENT PRIMARY KEY,
    product_id INT NOT NULL,
    quantity DECIMAL(10,2) NOT NULL,
    sell_price_per_unit DECIMAL(10,2) NOT NULL,
    total_revenue DECIMAL(10,2) GENERATED ALWAYS AS (quantity * sell_price_per_unit) STORED,
    sale_date DATE NOT NULL,
    month INT GENERATED ALWAYS AS (MONTH(sale_date)) STORED,
    year INT GENERATED ALWAYS AS (YEAR(sale_date)) STORED,
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE CASCADE
);

-- Expenses (operational costs: rent, electricity, salaries, etc.)
CREATE TABLE IF NOT EXISTS expenses (
    id INT AUTO_INCREMENT PRIMARY KEY,
    category VARCHAR(50) NOT NULL,
    description VARCHAR(200),
    amount DECIMAL(10,2) NOT NULL,
    expense_date DATE NOT NULL,
    month INT GENERATED ALWAYS AS (MONTH(expense_date)) STORED,
    year INT GENERATED ALWAYS AS (YEAR(expense_date)) STORED,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================
--  VIEWS FOR MONTHLY REPORTS
-- ============================================

-- Monthly summary view
CREATE OR REPLACE VIEW monthly_summary AS
SELECT
    COALESCE(p.year, s.year, e.year) AS year,
    COALESCE(p.month, s.month, e.month) AS month,
    COALESCE(p.total_purchased, 0) AS stock_cost,
    COALESCE(s.total_sold, 0) AS total_revenue,
    COALESCE(e.total_expenses, 0) AS operational_expenses,
    COALESCE(s.total_sold, 0) - COALESCE(p.total_purchased, 0) - COALESCE(e.total_expenses, 0) AS net_profit
FROM
    (SELECT year, month, SUM(total_cost) AS total_purchased FROM purchases GROUP BY year, month) p
    LEFT JOIN (SELECT year, month, SUM(total_revenue) AS total_sold FROM sales GROUP BY year, month) s
        ON p.year = s.year AND p.month = s.month
    LEFT JOIN (SELECT year, month, SUM(amount) AS total_expenses FROM expenses GROUP BY year, month) e
        ON p.year = e.year AND p.month = e.month
UNION
SELECT
    COALESCE(p.year, s.year, e.year),
    COALESCE(p.month, s.month, e.month),
    COALESCE(p.total_purchased, 0),
    COALESCE(s.total_sold, 0),
    COALESCE(e.total_expenses, 0),
    COALESCE(s.total_sold, 0) - COALESCE(p.total_purchased, 0) - COALESCE(e.total_expenses, 0)
FROM
    (SELECT year, month, SUM(total_cost) AS total_purchased FROM purchases GROUP BY year, month) p
    RIGHT JOIN (SELECT year, month, SUM(total_revenue) AS total_sold FROM sales GROUP BY year, month) s
        ON p.year = s.year AND p.month = s.month
    LEFT JOIN (SELECT year, month, SUM(amount) AS total_expenses FROM expenses GROUP BY year, month) e
        ON s.year = e.year AND s.month = e.month
    WHERE p.year IS NULL;

-- Per-product inventory view
CREATE OR REPLACE VIEW product_inventory AS
SELECT
    p.id,
    p.name,
    p.category,
    p.unit,
    COALESCE(SUM(pu.quantity), 0) AS total_purchased,
    COALESCE(SUM(s.quantity), 0) AS total_sold,
    COALESCE(SUM(pu.quantity), 0) - COALESCE(SUM(s.quantity), 0) AS remaining_stock,
    COALESCE(SUM(pu.total_cost), 0) AS total_cost,
    COALESCE(SUM(s.total_revenue), 0) AS total_revenue,
    COALESCE(SUM(s.total_revenue), 0) - COALESCE(SUM(pu.total_cost), 0) AS gross_profit
FROM products p
LEFT JOIN purchases pu ON p.id = pu.product_id
LEFT JOIN sales s ON p.id = s.product_id
GROUP BY p.id, p.name, p.category, p.unit;

-- ============================================
--  SAMPLE DATA
-- ============================================

INSERT INTO products (name, category, unit) VALUES
('Rice', 'Groceries', 'kg'),
('Sugar', 'Groceries', 'kg'),
('Cooking Oil', 'Groceries', 'litre'),
('Soap Bar', 'Household', 'pcs'),
('Shampoo', 'Personal Care', 'bottle');

-- Purchases (May 2025)
INSERT INTO purchases (product_id, quantity, cost_per_unit, purchase_date) VALUES
(1, 100, 45.00, '2025-05-02'),
(2, 50, 40.00, '2025-05-02'),
(3, 30, 90.00, '2025-05-03'),
(4, 80, 15.00, '2025-05-05'),
(5, 40, 120.00, '2025-05-06');

-- Sales (May 2025)
INSERT INTO sales (product_id, quantity, sell_price_per_unit, sale_date) VALUES
(1, 70, 55.00, '2025-05-10'),
(2, 35, 50.00, '2025-05-12'),
(3, 20, 115.00, '2025-05-15'),
(4, 60, 22.00, '2025-05-18'),
(5, 25, 150.00, '2025-05-20');

-- Expenses (May 2025)
INSERT INTO expenses (category, description, amount, expense_date) VALUES
('Rent', 'Shop rent for May', 5000.00, '2025-05-01'),
('Electricity', 'Electricity bill', 1200.00, '2025-05-05'),
('Salary', 'Staff salary', 8000.00, '2025-05-31');

-- Purchases (June 2025)
INSERT INTO purchases (product_id, quantity, cost_per_unit, purchase_date) VALUES
(1, 120, 46.00, '2025-06-01'),
(2, 60, 41.00, '2025-06-02'),
(3, 40, 92.00, '2025-06-03');

-- Sales (June 2025)
INSERT INTO sales (product_id, quantity, sell_price_per_unit, sale_date) VALUES
(1, 80, 56.00, '2025-06-10'),
(2, 45, 52.00, '2025-06-12'),
(3, 30, 118.00, '2025-06-14');

-- Expenses (June 2025)
INSERT INTO expenses (category, description, amount, expense_date) VALUES
('Rent', 'Shop rent for June', 5000.00, '2025-06-01'),
('Electricity', 'Electricity bill', 1100.00, '2025-06-05');

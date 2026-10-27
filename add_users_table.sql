-- Run this in MySQL to add login support to ShopLedger
-- Command: mysql -u root -p shopledger < add_users_table.sql

USE shopledger;

-- Create users table
CREATE TABLE IF NOT EXISTS users (
    id            INT AUTO_INCREMENT PRIMARY KEY,
    username      VARCHAR(50)  NOT NULL UNIQUE,
    password_hash VARCHAR(64)  NOT NULL,
    full_name     VARCHAR(100),
    created_at    DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Insert default admin user
-- Username: admin  |  Password: admin123
INSERT INTO users (username, password_hash, full_name)
VALUES (
    'admin',
    SHA2('admin123', 256),
    'Shop Admin'
)
ON DUPLICATE KEY UPDATE username = username;

-- (Optional) Add more users:
-- INSERT INTO users (username, password_hash, full_name)
-- VALUES ('yourname', SHA2('yourpassword', 256), 'Your Name');

SELECT 'Users table ready! Login with admin / admin123' AS status;
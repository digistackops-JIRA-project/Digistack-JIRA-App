-- Create database
CREATE DATABASE IF NOT EXISTS admindb
  CHARACTER SET utf8mb4
  COLLATE utf8mb4_unicode_ci;

-- Create application user
CREATE USER IF NOT EXISTS 'appuser'@'%' IDENTIFIED BY 'P@55Word';

-- Grant privileges only to this database
GRANT ALL PRIVILEGES ON admindb.* TO 'appuser'@'%';

-- Apply privilege changes
FLUSH PRIVILEGES;

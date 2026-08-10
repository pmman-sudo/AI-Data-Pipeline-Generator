CREATE TABLE IF NOT EXISTS fct_users_created (
  user_id BIGINT PRIMARY KEY,
  created_at TIMESTAMP NOT NULL,
  email STRING NOT NULL
);

CREATE INDEX idx_created_at ON fct_users_created (created_at);

CREATE VIEW vw_users_created AS
SELECT 
  user_id,
  created_at,
  email
FROM 
  fct_users_created;

CREATE TABLE IF NOT EXISTS dim_users (
  user_id BIGINT PRIMARY KEY,
  email STRING NOT NULL
);

INSERT INTO dim_users (user_id, email)
SELECT 
  user_id,
  email
FROM 
  fct_users_created;

CREATE TABLE IF NOT EXISTS fct_users_created_daily AS
SELECT 
  DATE(created_at) AS created_date,
  COUNT(DISTINCT user_id) AS daily_users
FROM 
  fct_users_created
GROUP BY 
  DATE(created_at);

CREATE TABLE IF NOT EXISTS fct_users_created_monthly AS
SELECT 
  DATE_TRUNC('month', created_at) AS created_month,
  COUNT(DISTINCT user_id) AS monthly_users
FROM 
  fct_users_created
GROUP BY 
  DATE_TRUNC('month', created_at);

CREATE MATERIALIZED VIEW IF NOT EXISTS mv_users_created AS
SELECT 
  user_id,
  created_at,
  email,
  DATE(created_at) AS created_date,
  DATE_TRUNC('month', created_at) AS created_month
FROM 
  fct_users_created;
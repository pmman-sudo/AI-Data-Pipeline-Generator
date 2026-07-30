sql
CREATE TABLE fct_users_created (
  user_id VARCHAR(100),
  user_name BOOLEAN
);

INSERT INTO fct_users_created (user_id, user_name)
SELECT 
  user_id,
  user_name
FROM 
  logging_events
WHERE 
  event_type = 'user_created';
CREATE TABLE fct_users_created
(
    user_id VARCHAR(100),
    user_name BOOLEAN
)
WITH (
    OWNER = 'urn:li:corpuser:jdoe, urn:li:corpuser:datahub'
);

GRANT SELECT ON TABLE fct_users_created TO 'urn:li:corpuser:jdoe, urn:li:corpuser:datahub';

INSERT INTO fct_users_created (user_id, user_name)
SELECT 
    logging_events.user_id,
    logging_events.user_name IS NOT NULL AS user_name
FROM 
    logging_events
WHERE 
    logging_events.event_type = 'user_created';

-- Create indexes for query optimization
CREATE INDEX idx_user_id ON fct_users_created (user_id);

-- Create a view for simplified querying
CREATE VIEW vw_fct_users_created AS
SELECT * FROM fct_users_created;
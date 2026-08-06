CREATE TABLE fct_users_created (
    user_id BIGINT,
    created_at TIMESTAMP,
    email VARCHAR(255)
);

INSERT INTO fct_users_created (user_id, created_at, email)
SELECT 
    u.user_id,
    u.created_at,
    u.email
FROM 
    users u; 

CREATE VIEW fct_users_created_v AS
SELECT 
    f.user_id,
    f.created_at,
    f.email
FROM 
    fct_users_created f; 

CREATE INDEX idx_fct_users_created_user_id ON fct_users_created (user_id);
CREATE INDEX idx_fct_users_created_created_at ON fct_users_created (created_at);
CREATE INDEX idx_fct_users_created_email ON fct_users_created (email);
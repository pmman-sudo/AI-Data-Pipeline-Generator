CREATE TABLE fct_users_created (
  user_id BIGINT,
  created_at TIMESTAMP,
  email VARCHAR(255)
);

ALTER TABLE fct_users_created OWNER TO Demo;

COMMENT ON TABLE fct_users_created IS 'Demo';
COMMENT ON COLUMN fct_users_created.user_id IS 'user_id';
COMMENT ON COLUMN fct_users_created.created_at IS 'created_at';
COMMENT ON COLUMN fct_users_created.email IS 'email';
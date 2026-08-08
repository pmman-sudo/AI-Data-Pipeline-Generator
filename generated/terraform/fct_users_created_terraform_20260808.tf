terraform
# Configure the AWS Provider
provider "aws" {
  region = var.aws_region
}

# Create a variable for the database name
variable "database_name" {
  type        = string
  description = "The name of the database"
}

# Create a variable for the schema name
variable "schema_name" {
  type        = string
  description = "The name of the schema"
}

# Create a variable for the table name
variable "table_name" {
  type        = string
  default     = "fct_users_created"
  description = "The name of the table"
}

# Create a variable for the owners
variable "owners" {
  type        = list(string)
  default     = ["Paul"]
  description = "The owners of the table"
}

# Create a variable for the aws region
variable "aws_region" {
  type        = string
  description = "The AWS region"
}

# Create an AWS Redshift cluster
resource "aws_redshift_cluster" "this" {
  cluster_identifier = "redshift-cluster"
  database_name       = var.database_name
  master_username    = "awsuser"
  master_password     = aws_secretsmanager_secret_version.master_password.secret_string
  node_type           = "dc2.large"
  cluster_type        = "single-node"
  publicly_accessible = true
  skip_final_snapshot = true
}

# Create an AWS Redshift schema
resource "aws_redshift_schema" "this" {
  cluster_name = aws_redshift_cluster.this.cluster_identifier
  database_name = var.database_name
  schema_name   = var.schema_name
}

# Create an AWS Redshift table
resource "aws_redshift_table" "this" {
  cluster_name = aws_redshift_cluster.this.cluster_identifier
  database_name = var.database_name
  schema_name   = aws_redshift_schema.this.schema_name
  table_name    = var.table_name
  column {
    name = "id"
    data_type = "INT"
  }
}

# Create a Secrets Manager secret for the master password
resource "aws_secretsmanager_secret" "master_password" {
  name = "redshift-master-password"
}

# Create a Secrets Manager secret version for the master password
resource "aws_secretsmanager_secret_version" "master_password" {
  secret_id     = aws_secretsmanager_secret.master_password.id
  secret_string = "MasterPassword123"
}
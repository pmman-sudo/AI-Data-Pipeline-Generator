# File: main.tf
provider "aws" {
  region = var.aws_region
}

resource "aws_rds_cluster" "fct_users_created" {
  cluster_identifier = "fct-users-created-cluster"
  database_name     = "fct_users_created_db"
  master_username    = var.db_username
  master_password    = var.db_password
  engine             = "postgres"
  engine_version     = "13.4"
  port               = 5432
}

resource "aws_rds_cluster_instance" "fct_users_created" {
  identifier         = "fct-users-created-instance"
  cluster_identifier = aws_rds_cluster.fct_users_created.cluster_identifier
  instance_class     = var.instance_class
  engine             = aws_rds_cluster.fct_users_created.engine
  engine_version     = aws_rds_cluster.fct_users_created.engine_version
}

resource "aws_s3_bucket" "fct_users_created" {
  bucket = "fct-users-created-bucket"
  acl    = "private"
}

resource "aws_s3_bucket_object" "fct_users_created" {
  bucket = aws_s3_bucket.fct_users_created.id
  key    = "fct_users_created_schema.sql"
  source = "${path.module}/fct_users_created_schema.sql"
}

resource "aws_glue_catalog_database" "fct_users_created" {
  name = "fct_users_created_db"
}

resource "aws_glue_catalog_table" "fct_users_created" {
  name          = "fct_users_created"
  database_name = aws_glue_catalog_database.fct_users_created.name
  table_type    = "EXTERNAL_TABLE"
  owner         = "Paul"
  storage_descriptor {
    location = "s3://${aws_s3_bucket.fct_users_created.id}/fct_users_created/"
    serdes {
      name = "org.apache.hadoop.hive.serde2.OpenCSVSerde"
    }
    columns {
      name = "id"
      type = "int"
    }
  }
}

# File: variables.tf
variable "aws_region" {
  type = string
}

variable "db_username" {
  type = string
}

variable "db_password" {
  type = string
}

variable "instance_class" {
  type = string
}
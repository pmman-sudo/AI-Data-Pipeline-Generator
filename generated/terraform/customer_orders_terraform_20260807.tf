# Configure the AWS Provider
provider "aws" {
  region = var.region
}

# Create a database instance
resource "aws_rds_instance" "customer_orders_db" {
  instance_class = var.instance_class
  engine          = "postgres"
  engine_version  = "14.3"
  username        = var.database_username
  password        = var.database_password
  db_name         = "customer_orders_db"
  tags = {
    Owner = "Demo"
    Environment = "Demo"
  }
}

# Create a database
resource "aws_db_instance" "customer_orders" {
  instance_class = var.instance_class
  engine          = "postgres"
  engine_version  = "14.3"
  username        = var.database_username
  password        = var.database_password
  db_name         = "customer_orders"
  parameter_group_name = "default.postgres14"
  vpc_security_group_ids = [aws_security_group.customer_orders.id]
  tags = {
    Owner = "Demo"
    Environment = "Demo"
  }
}

# Create a security group
resource "aws_security_group" "customer_orders" {
  name        = "customer_orders_sg"
  description = "Security group for customer orders database"
  vpc_id      = var.vpc_id

  # Allow inbound traffic on port 5432
  ingress {
    from_port   = 5432
    to_port     = 5432
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Owner = "Demo"
    Environment = "Demo"
  }
}

# Create a table in the database
resource "aws_db_table" "customer_orders" {
  name         = "customer_orders"
  database_name = aws_db_instance.customer_orders.db_name
  engine       = "postgres"
  engine_version = "14.3"

  column {
    name = "user_id"
    type = "BIGINT"
    constraints {
      primary_key = true
    }
  }

  column {
    name = "created_at"
    type = "TIMESTAMP"
  }

  column {
    name = "email"
    type = "STRING"
  }
}

variable "region" {
  type        = string
  default     = "us-west-2"
  description = "The AWS region"
}

variable "instance_class" {
  type        = string
  default     = "db.t3.micro"
  description = "The instance class"
}

variable "database_username" {
  type        = string
  sensitive   = true
  description = "The database username"
}

variable "database_password" {
  type        = string
  sensitive   = true
  description = "The database password"
}

variable "vpc_id" {
  type        = string
  description = "The VPC ID"
}
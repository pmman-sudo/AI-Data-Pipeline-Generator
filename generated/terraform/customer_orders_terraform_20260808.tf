terraform
variable "environment" {
  type        = string
  description = "Environment name"
}

variable "database_username" {
  type        = string
  description = "Database username"
}

variable "database_password" {
  type        = string
  sensitive   = true
  description = "Database password"
}

variable "database_endpoint" {
  type        = string
  description = "Database endpoint"
}

variable "database_name" {
  type        = string
  description = "Database name"
}

provider "aws" {
  region = "us-west-2"
}

resource "aws_db_instance" "customer_orders_db" {
  identifier           = "customer-orders-db"
  instance_class         = "db.t2.micro"
  engine                 = "postgres"
  username               = var.database_username
  password               = var.database_password
  db_name                = var.database_name
  vpc_security_group_ids = [aws_security_group.customer_orders_sg.id]
  skip_final_snapshot    = true
}

resource "aws_security_group" "customer_orders_sg" {
  name        = "customer-orders-sg"
  description = "Security group for customer orders database"
}

resource "aws_security_group_rule" "customer_orders_sg_rule" {
  type        = "ingress"
  from_port   = 5432
  to_port     = 5432
  protocol    = "tcp"
  cidr_blocks = ["0.0.0.0/0"]
  security_group_id = aws_security_group.customer_orders_sg.id
}

resource "aws_rds_cluster" "customer_orders_cluster" {
  cluster_identifier = "customer-orders-cluster"
  database_name       = var.database_name
  master_username     = var.database_username
  master_password     = var.database_password
  db_subnet_group_name = aws_db_subnet_group.customer_orders_subnet_group.name
  vpc_security_group_ids = [aws_security_group.customer_orders_sg.id]
  skip_final_snapshot  = true
}

resource "aws_db_subnet_group" "customer_orders_subnet_group" {
  name        = "customer-orders-subnet-group"
  description = "Subnet group for customer orders database"
  subnet_ids = [aws_subnet.customer_orders_subnet.id]
}

resource "aws_subnet" "customer_orders_subnet" {
  cidr_block = "10.0.1.0/24"
  vpc_id     = aws_vpc.customer_orders_vpc.id
  availability_zone = "us-west-2a"
}

resource "aws_vpc" "customer_orders_vpc" {
  cidr_block = "10.0.0.0/16"
}

resource "aws_ssm_parameter" "database_endpoint" {
  name        = "customer-orders-database-endpoint"
  type        = "String"
  value       = aws_db_instance.customer_orders_db.endpoint
}

resource "aws_ssm_parameter" "database_username" {
  name        = "customer-orders-database-username"
  type        = "String"
  value       = var.database_username
}

resource "aws_ssm_parameter" "database_password" {
  name        = "customer-orders-database-password"
  type        = "SecureString"
  value       = var.database_password
}

resource "aws_ssm_parameter" "database_name" {
  name        = "customer-orders-database-name"
  type        = "String"
  value       = var.database_name
}

resource "aws_iam_role" "customer_orders_iam_role" {
  name        = "customer-orders-iam-role"
  description = "IAM role for customer orders database"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Principal = {
          Service = "ec2.amazonaws.com"
        }
        Effect = "Allow"
      }
    ]
  })
}

resource "aws_iam_policy" "customer_orders_iam_policy" {
  name        = "customer-orders-iam-policy"
  description = "IAM policy for customer orders database"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = [
          "rds:DescribeDBInstances",
          "rds:DescribeDBClusters",
          "rds:DescribeDBSubnetGroups",
          "rds:DescribeVPCs",
          "rds:DescribeSubnets",
        ]
        Resource = "*"
        Effect    = "Allow"
      }
    ]
  })
}

resource "aws_iam_role_policy_attachment" "customer_orders_iam_role_policy_attachment" {
  role       = aws_iam_role.customer_orders_iam_role.name
  policy_arn = aws_iam_policy.customer_orders_iam_policy.arn
}

resource "aws_db_table" "customer_orders_table" {
  name         = "customer_orders"
  database_name = var.database_name
  table_type   = "standard"

  column {
    name = "user_id"
    type = "BIGINT"
    attributes = {
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

  tags = {
    Owner = "Demo"
    Tags  = "Demo"
  }
}

output "customer_orders_database_endpoint" {
  value       = aws_db_instance.customer_orders_db.endpoint
  description = "Customer orders database endpoint"
}

output "customer_orders_database_username" {
  value       = var.database_username
  description = "Customer orders database username"
}

output "customer_orders_database_password" {
  value       = var.database_password
  sensitive   = true
  description = "Customer orders database password"
}

output "customer_orders_database_name" {
  value       = var.database_name
  description = "Customer orders database name"
}
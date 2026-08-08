terraform
variable "db_username" {
  type        = string
  sensitive   = true
}

variable "db_password" {
  type        = string
  sensitive   = true
}

variable "db_host" {
  type        = string
}

variable "db_port" {
  type        = number
}

variable "db_name" {
  type        = string
}

variable "environment" {
  type        = string
}

variable "owners" {
  type        = list(string)
  default     = ["Paul"]
}

resource "aws_db_instance" "fct_users_created_db" {
  identifier        = "fct-users-created-db"
  instance_class    = "db.t2.micro"
  engine             = "postgres"
  username           = var.db_username
  password           = var.db_password
  port              = var.db_port
  dbname             = var.db_name
  vpc_security_group_ids = [aws_security_group.fct_users_created_db_sg.id]
  publicly_accessible = false
}

resource "aws_db_subnet_group" "fct_users_created_db_subnet_group" {
  name       = "fct-users-created-db-subnet-group"
  subnet_ids = [aws_subnet.fct_users_created_db_subnet.id]
}

resource "aws_subnet" "fct_users_created_db_subnet" {
  cidr_block = "10.0.1.0/24"
  vpc_id     = aws_vpc.fct_users_created_vpc.id
  availability_zone = "us-east-1a"
}

resource "aws_vpc" "fct_users_created_vpc" {
  cidr_block = "10.0.0.0/16"
}

resource "aws_security_group" "fct_users_created_db_sg" {
  name        = "fct-users-created-db-sg"
  vpc_id      = aws_vpc.fct_users_created_vpc.id
  ingress {
    from_port   = var.db_port
    to_port     = var.db_port
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }
  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

resource "postgresql_database" "fct_users_created_db" {
  name  = var.db_name
  owner = "postgres"
}

resource "postgresql_table" "fct_users_created" {
  database = postgresql_database.fct_users_created_db.name
  name     = "fct_users_created"
  owner    = "postgres"
  table    = "fct_users_created"

  column {
    name = "id"
    type = "integer"
  }
}

output "db_instance_arn" {
  value = aws_db_instance.fct_users_created_db.arn
}

output "db_instance_endpoint" {
  value = aws_db_instance.fct_users_created_db.endpoint
}

output "db_instance_username" {
  value = var.db_username
  sensitive = true
}

output "db_instance_password" {
  value = var.db_password
  sensitive = true
}
provider "aws" {
  region = var.region
}

resource "aws_dynamodb_table" "customer_orders" {
  name           = "customer_orders"
  billing_mode   = "PAY_PER_REQUEST"
  hash_key       = "user_id"
  attribute {
    name = "user_id"
    type = "N"
  }
  attribute {
    name = "email"
    type = "S"
  }
  ttl {
    attribute_name = "created_at"
    enabled        = true
  }
  tags = {
    Owner = "Demo"
    Environment = "Demo"
  }
}

variable "region" {
  type        = string
  description = "AWS Region"
}

output "customer_orders_table_name" {
  value = aws_dynamodb_table.customer_orders.name
}

output "customer_orders_table_arn" {
  value = aws_dynamodb_table.customer_orders.arn
}
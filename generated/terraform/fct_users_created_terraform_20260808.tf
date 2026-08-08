provider "aws" {
  region = var.region
}

resource "aws_dynamodb_table" "fct_users_created" {
  name           = "fct_users_created"
  billing_mode   = "PAY_PER_REQUEST"
  hash_key       = "id"

  attribute {
    name = "id"
    type = "N"
  }

  tags = {
    Owners = "Paul"
  }
}

variable "region" {
  type        = string
  description = "AWS region"
}
terraform {
  required_version = ">= 1.0"
}

resource "aws_s3_bucket" "fct_users_created" {
  bucket = "fct-users-created-test"
}
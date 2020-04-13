# Provider Block
provider "aws" {
  version = "~> 2.7"
  # region -> Taken from env vars or defaulted from profile
}

resource "aws_s3_bucket" "test_s3bucket" {
  bucket_prefix = "lambda-cache"
  acl           = "private"
  force_destroy = true
}

resource "aws_ssm_parameter" "test_s3bucket_name" {
  type        = "String"
  description = "Name of s3 bucket to hold layer artifacts"
  name        = "/lambda-cache/s3/bucket_name"
  value       = aws_s3_bucket.test_s3bucket.bucket
  overwrite   = true
}


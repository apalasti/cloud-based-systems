resource "random_password" "app_secret_key" {
  length  = 48
  special = true
}

resource "aws_secretsmanager_secret" "app" {
  name = "${local.name_prefix}/app"
  tags = local.tags
}

resource "aws_secretsmanager_secret_version" "app" {
  secret_id = aws_secretsmanager_secret.app.id
  secret_string = jsonencode({
    SECRET_KEY = random_password.app_secret_key.result
  })
}


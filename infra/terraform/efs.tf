resource "aws_efs_file_system" "uploads" {
  encrypted = true
  tags      = merge(local.tags, { Name = "${local.name_prefix}-efs" })
}

resource "aws_efs_mount_target" "uploads" {
  count           = length(aws_subnet.private)
  file_system_id  = aws_efs_file_system.uploads.id
  subnet_id       = aws_subnet.private[count.index].id
  security_groups = [aws_security_group.efs.id]
}

resource "aws_efs_access_point" "uploads" {
  file_system_id = aws_efs_file_system.uploads.id

  root_directory {
    path = "/uploads"
    creation_info {
      owner_gid   = 0
      owner_uid   = 0
      permissions = "0777"
    }
  }
}


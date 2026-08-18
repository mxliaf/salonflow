#Provisiona a máquina virtual (EC2) e já instala o Docker e o Git automaticamente
data "aws_ami" "ubuntu" {
  most_recent = true
  owners      = ["099720109477"] # Canonical

  filter {
    name   = "name"
    values = ["ubuntu/images/hvm-ssd/ubuntu-jammy-22.04-amd64-server-*"]
  }
}

resource "aws_key_pair" "deployer_key" {
  key_name   = "salonflow-deploy-key"
  public_key = file("${path.module}/salonflow_key.pub")
}

resource "aws_instance" "app_server" {
  ami           = data.aws_ami.ubuntu.id
  instance_type = "t3.micro"
  key_name      = aws_key_pair.deployer_key.key_name

  vpc_security_group_ids = [aws_security_group.salonflow_sg.id]

  user_data = <<-EOF
              #!/bin/bash
              apt-get update -y
              apt-get install -y docker.io docker-compose-v2 git
              systemctl start docker
              systemctl enable docker
              usermod -aG docker ubuntu
              EOF

  tags = {
    Name = "SalonFlow-Server"
  }
}

output "ip_publico_servidor" {
  description = "O endereço IP publico da instancia EC2 do salao"
  value       = aws_instance.app_server.public_ip
}
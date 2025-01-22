
# gcp 사용
provider "google" {
    credentials = file("ethereal-creek-448408-k4-87309d3b45c5.json")
    project = "ethereal-creek-448408-k4"
    region  = "us-central1"  
    zone    = "us-central1-c" 
}

# 인스턴스 접속에 필요한 ssh key 추가
variable "ssh_key" {
    type        = string
    description = "SSH public key"
}

# 네트워크 추가
resource "google_compute_network" "vpc_network" {
    name                    = "myinsideout-vpc-network"
    auto_create_subnetworks = false
}

# 서브넷 추가
resource "google_compute_subnetwork" "subnet" {
    name          = "myinsideout-subnet"
    ip_cidr_range = "10.0.0.0/16"
    network       = google_compute_network.vpc_network.id
    region        = "us-central1"
}

# 고정 아이피 할당
resource "google_compute_address" "static_ip1" {
    name   = "myinsideout-static-ip"
    region = "us-central1"
}

# 방화벽 설정
resource "google_compute_firewall" "main-ssh-icmp" {
    name    = "main-ssh-icmp"
    network = google_compute_network.vpc_network.name

    allow {
        protocol = "tcp"
        ports    = ["22", "80", "443", "8000"]  # 포트 설정
    }

    allow {
        protocol = "icmp"
    }

    source_ranges = ["0.0.0.0/0"]
    target_tags = ["main-firewall"] # 방화벽 태그 설정
}

# 인스턴스 생성 
resource "google_compute_instance" "vm_instance1" {
    name         = "myinsideout-instance"
    machine_type = "e2-medium"  # 2 vCPUs, 4GB memory
    zone         = "us-central1-c"
    allow_stopping_for_update = true

    boot_disk {
    initialize_params {
        image  = "ubuntu-os-cloud/ubuntu-2004-lts" # 우분투 사용
        size   = 30  # 30 GB 디스크
        type   = "pd-balanced"
        }
    }
		# 생성해둔 네트워크 사용
    network_interface {
        subnetwork = google_compute_subnetwork.subnet.id
        access_config {
            nat_ip = google_compute_address.static_ip1.address
        }
    }

    tags = ["http-server", "https-server", "main-firewall"]
		
		# 인스턴스 프로비져닝과 함께 도커도 설치 및 ssh key 추가
    metadata = {
        ssh-keys = "ubuntu:${var.ssh_key}"
        startup-script = file("docker.sh")
    }
}

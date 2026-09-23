terraform {
  required_providers {
    libvirt = {
      source  = "dmacvicar/libvirt"
      version = "0.7.6"
    }
  }
}

provider "libvirt" {
  uri = "qemu:///system"
}

# Imagem base (baixada uma vez)
resource "libvirt_volume" "base" {
  name   = "${var.vm_name}-base.qcow2"
  pool   = var.storage_pool
  source = var.base_image_url
  format = "qcow2"
}

# Disco da VM, derivado da imagem base
resource "libvirt_volume" "disco" {
  name           = "${var.vm_name}-disco.qcow2"
  pool           = var.storage_pool
  base_volume_id = libvirt_volume.base.id
  size           = var.disk_size_bytes
  format         = "qcow2"
}

# cloud-init: o arquivo é um template que recebe usuário e chave pública
resource "libvirt_cloudinit_disk" "init" {
  name = "${var.vm_name}-cloudinit.iso"
  pool = var.storage_pool
  user_data = templatefile("${path.module}/cloud_init.cfg", {
    hostname       = var.vm_name
    vm_user        = var.vm_user
    ssh_public_key = trimspace(file(pathexpand(var.ssh_public_key_path)))
  })
}

resource "libvirt_domain" "vm" {
  name    = var.vm_name
  memory  = var.memory_mb
  vcpu    = var.vcpu
  running = true

  cloudinit = libvirt_cloudinit_disk.init.id

  network_interface {
    network_name   = var.network_name
    wait_for_lease = true
  }

  disk {
    volume_id = libvirt_volume.disco.id
  }

  console {
    type        = "pty"
    target_port = "0"
    target_type = "serial"
  }

  graphics {
    type        = "spice"
    listen_type = "address"
    autoport    = true
  }
}

output "vm_ip" {
  description = "IP da VM (use no inventário do Ansible e no SSH)"
  value       = libvirt_domain.vm.network_interface[0].addresses[0]
}

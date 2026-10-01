# Segunda VM para processamento/análise de dados

resource "libvirt_volume" "base_dados" {
  name   = "vm-dados-base.qcow2"
  pool   = var.storage_pool
  source = var.base_image_url
  format = "qcow2"
}

resource "libvirt_volume" "disco_dados" {
  name           = "vm-dados-disco.qcow2"
  pool           = var.storage_pool
  base_volume_id = libvirt_volume.base_dados.id
  size           = var.disk_size_bytes
  format         = "qcow2"
}

resource "libvirt_cloudinit_disk" "init_dados" {
  name = "vm-dados-cloudinit.iso"
  pool = var.storage_pool

  user_data = templatefile("${path.module}/cloud_init.cfg", {
    hostname       = "vm-dados"
    vm_user        = var.vm_user
    ssh_public_key = trimspace(file(pathexpand(var.ssh_public_key_path)))
  })
}

resource "libvirt_domain" "vm_dados" {
  name    = "vm-dados"
  memory  = 2048
  vcpu    = 2
  running = true

  cloudinit = libvirt_cloudinit_disk.init_dados.id

  network_interface {
    network_name   = var.network_name
    wait_for_lease = true
  }

  disk {
    volume_id = libvirt_volume.disco_dados.id
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

output "vm_dados_ip" {
  value = libvirt_domain.vm_dados.network_interface[0].addresses[0]
}
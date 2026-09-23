variable "vm_name" {
  description = "Nome da máquina virtual"
  type        = string
  default     = "vm-simulador"
}

variable "vcpu" {
  type    = number
  default = 2
}

variable "memory_mb" {
  type    = number
  default = 2048
}

variable "disk_size_bytes" {
  description = "Tamanho do disco (padrão: 10 GiB)"
  type        = number
  default     = 10737418240
}

variable "base_image_url" {
  description = "Imagem cloud do Ubuntu (qcow2)"
  type        = string
  default     = "https://cloud-images.ubuntu.com/jammy/current/jammy-server-cloudimg-amd64.img"
}

variable "ssh_public_key_path" {
  description = "Caminho da chave PÚBLICA SSH que terá acesso à VM"
  type        = string
  default     = "~/.ssh/id_ed25519.pub"
}

variable "vm_user" {
  description = "Usuário administrador criado pelo cloud-init"
  type        = string
  default     = "devops"
}

variable "storage_pool" {
  type    = string
  default = "default"
}

variable "network_name" {
  type    = string
  default = "default"
}

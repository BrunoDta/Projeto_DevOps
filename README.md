# Projeto Integrado – Ajuste de estoque de supermercado (Data Science)

Checkpoint 01 de DevOps e Infraestrutura Privada: uma VM Linux é criada por código
(OpenTofu + libvirt), configurada no primeiro boot (cloud-init), preparada com
Ansible, recebe o simulador via SSH/SCP e gera dados de estoque dentro dela.

## Estrutura

- `infraestrutura/` – OpenTofu (`main.tf`, `variables.tf`), `cloud_init.cfg`, `deploy.sh` e `ansible/`
- `simulador/` – `simulador.py` (gera registros de estoque em CSV)
- `dados/exemplo_dados.csv` – exemplo de saída do simulador

## Pré-requisitos (máquina hospedeira Linux)

- libvirt/KVM em funcionamento (`virsh -c qemu:///system list` sem erro) e usuário no grupo `libvirt`
- [OpenTofu](https://opentofu.org/), Ansible, cliente OpenSSH
- Um par de chaves SSH: `ssh-keygen -t ed25519` (a chave **privada nunca vai para o repositório**)

## Passo a passo

### 1. Provisionar a VM (OpenTofu + cloud-init)

```bash
cd infraestrutura
tofu init
tofu apply -var "ssh_public_key_path=~/.ssh/id_ed25519.pub"
```

Anote o IP exibido em `vm_ip` (ou `tofu output vm_ip`). Variáveis ajustáveis estão em `variables.tf`.

Testar o acesso e comprovar o cloud-init:

```bash
ssh -i ~/.ssh/id_ed25519 devops@<IP_DA_VM>
cat /etc/cloud-init-aplicado.txt
cloud-init status
```

### 2. Configurar o ambiente (Ansible)

Edite `ansible/inventory.ini` com o IP da VM e rode:

```bash
cd ansible
ansible-playbook -i inventory.ini playbook.yml
ansible-playbook -i inventory.ini playbook.yml   # 2ª execução: deve dar changed=0
```

### 3. Transferir e executar o simulador (SSH/SCP)

```bash
cd ..
./deploy.sh <IP_DA_VM>
```

O script copia `simulador/` para `/opt/supermercado/simulador` na VM com `scp`
e executa `simulador.py`. Os dados ficam em `/opt/supermercado/dados/estoque.csv`.
Cada nova execução **acrescenta** registros, sem apagar os anteriores.

### 4. Verificar os dados na VM

```bash
ssh -i ~/.ssh/id_ed25519 devops@<IP_DA_VM> "wc -l /opt/supermercado/dados/estoque.csv"
```

## Formato dos dados

`id_registro, data_hora, id_produto, produto, categoria, preco_unitario,
estoque_atual, estoque_minimo, vendas_dia, dias_ate_validade`

## Destruir o ambiente

```bash
cd infraestrutura && tofu destroy
```

## Segurança

Estado do OpenTofu (`*.tfstate`), chaves privadas e senhas estão no `.gitignore`
e não devem ser versionados.

# Projeto Integrado – Ajuste de estoque de supermercado (Data Science)

Checkpoint 01 de DevOps e Infraestrutura Privada.

Esta solução cria uma máquina virtual Linux **por código** (OpenTofu + libvirt),
configura seu primeiro boot com **cloud-init**, prepara o ambiente com **Ansible**,
transfere o simulador por **SSH/SCP** e gera dados de estoque dentro da VM.

## Arquitetura


## Estrutura do repositório

## Estrutura do repositório

## Pré-requisitos (máquina hospedeira Linux)

- **libvirt/KVM** instalado e ativo, com o usuário no grupo `libvirt`
- **OpenTofu** (o comando é `tofu`)
- **Ansible**
- Cliente **OpenSSH**
- Um par de chaves SSH (`ssh-keygen -t ed25519`). A chave **privada nunca deve ir para o repositório**.

### Preparar o libvirt (uma vez)

Confira se o libvirt está pronto:

```bash
virsh -c qemu:///system pool-list --all   # deve existir o pool "default" ativo
virsh -c qemu:///system net-list --all    # deve existir a rede "default" ativa
```

Se faltar o pool `default`:

```bash
virsh -c qemu:///system pool-define-as default dir --target /var/lib/libvirt/images
virsh -c qemu:///system pool-build default
virsh -c qemu:///system pool-start default
virsh -c qemu:///system pool-autostart default
```

Se a rede `default` estiver inativa:

```bash
virsh -c qemu:///system net-start default
virsh -c qemu:///system net-autostart default
```

## Passo a passo

### 1. Clonar o repositório

```bash
git clone git@github.com:BrunoDta/Projeto_DevOps.git
cd Projeto_DevOps
```

### 2. Provisionar a VM (OpenTofu + cloud-init)

```bash
cd infraestrutura
tofu init
tofu apply -var "ssh_public_key_path=~/.ssh/id_ed25519.pub"
```

Digite `yes` quando pedir. O primeiro `apply` baixa a imagem do Ubuntu e pode levar
alguns minutos. No final, o OpenTofu mostra o IP da VM:

```bash
tofu output vm_ip
```

Para comprovar o cloud-init, aguarde 1 ou 2 minutos e acesse a VM:

```bash
ssh -i ~/.ssh/id_ed25519 devops@<IP_DA_VM>
cat /etc/cloud-init-aplicado.txt
cloud-init status
exit
```

### 3. Configurar o ambiente (Ansible)

Em `infraestrutura/ansible/inventory.ini`, informe o IP mostrado pelo OpenTofu
(o IP muda se a VM for recriada):

```ini
vm1 ansible_host=<IP_DA_VM>
```

Execute o playbook:

```bash
cd ansible
ansible-playbook -i inventory.ini playbook.yml
ansible-playbook -i inventory.ini playbook.yml   # 2ª execução: changed=0
```

A segunda execução deve terminar com `changed=0`, o que mostra que o playbook
é idempotente.

### 4. Transferir e executar o simulador (SSH/SCP)

```bash
cd ..
chmod +x deploy.sh
./deploy.sh <IP_DA_VM>
```

O script copia `simulador/` para `/opt/supermercado/simulador` na VM com `scp`
e executa `simulador.py`. Cada execução gera 20 registros e os **acrescenta** a
`/opt/supermercado/dados/estoque.csv`, sem apagar os anteriores.

Se a chave SSH tiver outro nome:

```bash
./deploy.sh <IP_DA_VM> devops ~/.ssh/OUTRA_CHAVE
```

### 5. Verificar os dados gerados na VM

```bash
ssh -i ~/.ssh/id_ed25519 devops@<IP_DA_VM> \
  "ls -l /opt/supermercado/simulador; wc -l /opt/supermercado/dados/estoque.csv; head -5 /opt/supermercado/dados/estoque.csv"
```

A cada execução do `deploy.sh`, o total de linhas aumenta em 20.

### 6. Gerar um arquivo de exemplo (opcional)

```bash
ssh -i ~/.ssh/id_ed25519 devops@<IP_DA_VM> \
  "python3 /opt/supermercado/simulador/simulador.py --registros 20 --saida /tmp/exemplo_dados.csv"
scp -i ~/.ssh/id_ed25519 devops@<IP_DA_VM>:/tmp/exemplo_dados.csv ../dados/exemplo_dados.csv
```

### 7. Destruir o ambiente

```bash
cd infraestrutura
tofu destroy
```

## Simulador

`simulador/simulador.py` gera registros de estoque de produtos de supermercado.
Usa apenas a biblioteca padrão do Python 3 e roda sem interface gráfica:

```bash
python3 simulador.py [--registros 20] [--saida caminho/estoque.csv]
```

Por padrão grava em `../dados/estoque.csv` (relativo ao script), ou em
`$DADOS_DIR/estoque.csv` se a variável existir. O mínimo é 10 registros por execução.

Campos de cada registro:

| Campo | Descrição |
|---|---|
| `id_registro` | identificador único (UUID) |
| `data_hora` | data e hora da geração |
| `id_produto`, `produto`, `categoria` | identificação do item |
| `preco_unitario` | preço em reais |
| `estoque_atual`, `estoque_minimo` | quantidade em estoque e nível mínimo |
| `vendas_dia` | unidades vendidas no dia |
| `dias_ate_validade` | dias restantes até o vencimento |

## Problemas comuns

| Sintoma | Causa e solução |
|---|---|
| `can't find storage pool 'default'` | Crie o pool `default` (seção "Preparar o libvirt"). |
| `network 'default' is not active` | Rode `virsh -c qemu:///system net-start default`. |
| `domain 'vm-simulador' already exists` | Sobrou uma VM registrada de um `apply` anterior que falhou no meio. Rode `virsh -c qemu:///system undefine vm-simulador` antes de repetir o `tofu apply`. |
| `Could not open ... .qcow2: Permission denied` | Primeiro ajuste o dono dos discos: `sudo sh -c 'chown libvirt-qemu:kvm /var/lib/libvirt/images/vm-simulador-*'`. Se persistir, é o AppArmor bloqueando o QEMU. Confirme com `virsh -c qemu:///system capabilities | grep -A3 secmodel`: se aparecer `<model>apparmor</model>`, edite `/etc/libvirt/qemu.conf` e descomente a linha **`#security_driver = "none"`** (não é a `#security_driver = "selinux"` — no Ubuntu/Mint 24.04 a linha ativa por padrão é a do `"none"` comentado). Confirme com `sudo grep -n "^security_driver" /etc/libvirt/qemu.conf` e reinicie de forma completa: `sudo systemctl stop libvirtd libvirtd.socket libvirtd-ro.socket libvirtd-admin.socket && sudo pkill -9 libvirtd && sudo systemctl start libvirtd` (um `restart` simples pode não recarregar a mudança). Repita o `capabilities` para confirmar que `apparmor` sumiu da lista, remova a VM órfã (`virsh -c qemu:///system undefine vm-simulador`) e rode `tofu apply` de novo. |
| Ansible: `No route to host` | O IP no `inventory.ini` está desatualizado. Use `tofu output vm_ip`. |
| `./deploy.sh: Permissão negada` | Rode `chmod +x deploy.sh`. |
| `tofu` mostra erro de Python (`gi`, `Ufo`) | O comando `tofu` instalado é outro pacote. Remova-o e instale o OpenTofu oficial. |
| Instalador do OpenTofu falha na verificação de chave | Em sistemas em português, rode `LC_ALL=C ./install-opentofu.sh --install-method standalone`. |

## Segurança

Arquivos de estado do OpenTofu (`*.tfstate`), chaves privadas e senhas estão no
`.gitignore` e **não devem ser versionados**. O acesso à VM é feito somente por
chave pública; o login por senha está desativado pelo cloud-init.

# 🔐 Bitwarden RBW for Ulauncher
 > Uma extensão para o Ulauncher que integra o gerenciador de senhas Bitwarden via CLI **rbw** (Rust Bitwarden), permitindo copiar dados diretamente do seu cofre no launcher.
<br>

## ✨ Funcionalidades
🔑 Desbloquear e bloquear o cofre do Bitwarden ( **bw lock** | **bw unlock** ).

* 🔄 Sincronizar o cofre local com o servidor remoto ( **rbw sync** ).

* 🔍 Buscar e listar registros filtrando por pasta e nome.

* 📋 Exibir detalhes de itens como Credenciais, Cartões, Identidades e Notas.

* 🔔 Notificações nativas para sucesso e erros.

* ⚙️ Configuração de palavras-chave personalizadas para ações (lock, unlock, sync).

* 📁 Filtro de registros por pasta
<br>

## 🚀 Instalação

### 1. ✅ Instalação Automática via Ulauncher

Abra o Ulauncher e digite ext, depois pressione Enter.

A página de extensões será aberta no navegador.

> Clique em "Add Extension".

Cole o link abaixo e clique em Add:

👉 [https://github.com/silvan-batistella/rbw-ext]

### 2. 📦 Instale dependências do sistema (para Ubuntu/Debian):

```bash
sudo apt install libnotify-bin gir1.2-notify-0.7
```

> **Importante**: a extensão depende do CLI rbw instalado e configurado no seu sistema. Veja como instalar o rbw:
👉 [https://github.com/doy/rbw]
<br>

## 🧪 Como usar
Abrir a extensão
Abra o Ulauncher e digite a palavra-chave configurada para a extensão (**bw** por padrão).

* Com o **cofre bloqueado**, será exibida apenas a opção de **desbloqueio**.

* Com o **cofre desbloqueado**, a lista inicial inclui:

    * Bloquear (lock)

    * Sincronizar (sync)

    * Além da busca de registros


<br>

### Comandos rápidos (**Configuráveis**):

**lock** → Bloqueia o cofre.

**unlock** → Desbloqueia o cofre.

**sync** → Sincroniza o cofre local com o remoto.


<br>

### Busca de registros

Digite uma parte do nome do registro para listar os itens correspondentes.


<br>

### Filtrar por pasta

Digite **/** (barra) após a palavra-chave para listar todas as pastas do cofre.

É possível filtrar essa lista digitando o início do nome da pasta (filtro por startswith).

Após selecionar a pasta, apenas os registros nela contidos serão exibidos.


<br>

### Filtrar por palavra-chave dentro de uma pasta

Digite:

```bash
/nome_da_pasta termo_de_busca
```

A ordem é sempre **pasta → palavra-chave**.

Isso exibirá apenas os registros da pasta escolhida que contenham o termo informado no título.



<br>

## 📄 Licença
**MIT © 2025**

[Silvan S. Batistella](https://github.com/silvan-batistella)
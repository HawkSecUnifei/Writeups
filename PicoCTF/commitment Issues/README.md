# WriteUp: Commitment Issues

## Descrição do Desafio:
**Plataforma**: [PicoCTF](https://play.picoctf.org/)  
**Categoria**: General Skills  
**Dificuldade**: Easy  
**Data**: 2024  
**Descrição**:  
> I accidentally wrote the flag down. Good thing I deleted it!

## Passo a Passo da Solução

### 1. Configuração Inicial
Para resolver esse desafio, é necessário ter uma ferramenta de Git instalada na máquina. Aqui, utilizaremos o Git Bash.

Inicialmente, baixe o arquivo compactado do site do PicoCTF e extraia o seu conteúdo em uma pasta de trabalho.

### 2. Exploração do Diretório
Após a extração, você terá acesso a uma pasta chamada `drop-in`, que contém um diretório `.git` e um arquivo `message`. Ao abrir o arquivo `message`, o conteúdo exibido é apenas a string **"TOP SECRET"**.

A presença da pasta `.git` indica que esse diretório faz parte de um repositório versionado, ou seja, teve alterações registradas no histórico de commits.

### 3. Analisando o Histórico de Commits
Abra o Git Bash, navegue até o diretório `drop-in` e execute o seguinte comando para visualizar o histórico de commits:

```sh
 git log
```

Isso mostrará os commits feitos no repositório, incluindo os hashes identificadores de cada commit.

### 4. Recuperando um Commit Antigo
Para acessar o conteúdo de um commit anterior, utilizamos o comando:

```sh
 git checkout <hash_do_commit>
```

Substitua `<hash_do_commit>` pelo hash do commit mais antigo encontrado no `git log`.

Para visualizar corretamente o conteúdo desse commit sem perder a branch principal, crie uma nova branch e alterne para ela:

```sh
 git switch -c nova-branch
```

### 5. Encontrando a Flag
Agora, abra novamente o arquivo `message`. O conteúdo foi alterado e revela a flag necessária para resolver o desafio. Basta copiá-la e enviá-la no site do PicoCTF.

### FLAG
`picoCTF{s@n1t1z3_7246792d}`

## Conclusão
Neste desafio, praticamos conceitos essenciais do Git, como:
- Navegação no histórico de commits
- Checkout de versões anteriores
- Criação de branches para preservar informação

Essas habilidades são fundamentais para desenvolvedores e pesquisadores de segurança, permitindo recuperar informações perdidas, auditar históricos de projetos e identificar segredos deixados por engano em repositórios versionados.

Em competições de CTF, o conhecimento sobre Git pode ser crucial para resolver desafios relacionados a forensic e version control de maneira eficiente.

## Autor da WriteUp
[Membro de Investigation - Fquental](https://github.com/FQuental)


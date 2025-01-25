# PicoCTF: Power Cookie

**Author**: LT 'syreal' Jones \
**Plataforma**: PicoCTF\
**Categoria**: Web Exploitation\
**Dificuldade**: Medio\
**Descrição**: Can you get the flag? Go to this website and see what you can discover.



## Desafio

O desafio busca ensinar um pouco sobre o protocolo cookies e como manipula-los ao favor do atacante.

---

## Solução

### 1. Análise inicial

Ao acessar o site, vemos uma pagina web comum com um botao porem ao clicar ele te leva a outra pagina **/check.php** na qual esta escrito:

```
We apologize, but we have no guest services at the moment.
```

Ao analisar o codigo da pagina, nao a nada de especial no HTML.

---

### 2. Explorando os cookies

Ao inspecionar a pagina e ir na sessao de **Storage** verifiquei os Cookies e encontrei o seguinte cookie:

```
>> document.cookie
"isAdmin=0" 
```

Logo podemos ver que possui um cookie indicando se o usuario eh administrador ou nao. Apenas alterei o valor para **1** e recarreguei a pagina.

Com isso consegui capturar a flag.

### 3. Flag

```
picoCTF{gr4d3_A_c00k13_5d2505be}
```

---

## Autor da WriteUp

[Membro de Networking - leandrobalta](https://github.com/leandrobalta)
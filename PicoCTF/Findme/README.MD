# WriteUp: Findme


## Descrição do desafio
**Author**: Geoffrey Njogu \
**Plataforma**: [PicoCTF](https://play.picoctf.org/practice/challenge/349?category=1&difficulty=2&page=1) \
**Categoria**: Web Exploitation \
**Dificuldade**: Médio \
**Data**: 2023 

---

## Descrição do Desafio

No desafio, é disponibilizado um login e uma senha iniciais:  
- **Login:** test  
- **Senha:** test!  

Após realizar o login, somos redirecionados por algumas páginas até chegar à URL final:  
`http://saturn.picoctf.net:56117/home`.

Uma dica importante dada pelo desafio é:  
**"any redirections?"**

Isso sugere que precisamos investigar as URLs e seus redirecionamentos para encontrar pistas escondidas.

---

## Solução

### Passo 1: Analisando os redirecionamentos

Ao observar os redirecionamentos do site, notamos que ele passa por URLs intermediárias antes de chegar à página final.

Exemplo de URL encontrada ao voltar uma página:  
`http://saturn.picoctf.net:56117/next-page/id=bF90aGVfd2F5X2RmNDRjOTRjfQ==`

### Passo 2: Decodificando o ID

O parâmetro `id` dessa URL contém uma string codificada em **Base64**:  
`bF90aGVfd2F5X2RmNDRjOTRjfQ==`

Ao decodificar usando [Base64 Decode](https://www.base64decode.org/), obtemos:  
`l_the_way_df44c94c}`

---

### Passo 3: Encontrando outro redirecionamento

Voltando mais uma página, encontramos outra URL suspeita:  
`http://saturn.picoctf.net:56117/next-page/id=cGljb0NURntwcm94aWVzX2Fs`

Ao decodificar o ID (`cGljb0NURntwcm94aWVzX2Fs`) novamente em Base64, obtemos:  
`picoCTF{proxies_al`

---

### Passo 4: Montando a Flag

Combinando as duas partes obtidas:  
- `picoCTF{proxies_al`  
- `l_the_way_df44c94c}`  

Obtemos a flag completa:  
**`picoCTF{proxies_all_the_way_df44c94c}`**

---

## Conclusão

Este desafio destacou a importância de analisar os redirecionamentos de URLs em busca de informações escondidas. Utilizamos a técnica de decodificação Base64 para extrair as partes da flag em URLs intermediárias e combiná-las para resolver o desafio.

---

## Recursos Utilizados

- Navegador para monitorar redirecionamentos
- [Base64 Decode](https://www.base64decode.org/) para decodificar strings em Base64

**Flag Final:** `picoCTF{proxies_all_the_way_df44c94c}`

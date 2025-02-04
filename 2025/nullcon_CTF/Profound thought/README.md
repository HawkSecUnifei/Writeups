# WriteUp: Profound thought
## Descrição do Desafio
Categoria: misc

Descrição:
> An uprising online blogger wants to keep sharing their
>  
>  profound thoughts but fears that these statements will
> 
>  affect their social credit score. Therefore, they try to
> 
>  express themselves through images...

## Solução
O desafio apenas disponibiliza uma imagem em png.

![image](https://github.com/user-attachments/assets/0fe35420-e341-4479-9bc0-b9eeca902d0f)


Observando a imagem, não parece ter nada escondido nela. Então, podemos explorar três maneiras mais comum de esconder informações em imagem que é escondendo no próprio arquivo, nos metadados ou por esteganografia. 
Não é possível encontrar nada escondido nos arquivos da imagem e a imagem também não possui metadados. Então, sobrou apenas estanografia. 

Utilizando o site https://stylesuxx.github.io/steganography/  , podemos decodificar a imagem usando esteganografia. Fazendo isso, obtemos a seguinte mensagem escondida.

```
ENO{57394n09r4phy_15_w4y_c00l3r_7h4n_p0rn06r4phy}
```

Pronto, obtemos a flag.

### Flag: `ENO{57394n09r4phy_15_w4y_c00l3r_7h4n_p0rn06r4phy}`

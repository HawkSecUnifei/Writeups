# [pwn]-delulu
## Autor(s): Diego Valim & Murilo Gebra

Analisando o arquivo `delulu`, disponibilizado na plataforma do HTB, no ghidra, descobrimos um ponteiro(`local_40` (renomeada para `var_ptr` na imagem)) para um variável `local_48` (renomeada para ‘var’ na imagem) de valor `0x1337babe`.

![image](https://github.com/HawkSecUnifei/resources-hawksec/assets/36544397/335c6763-0711-4a26-8809-5dab56151262)

Prosseguindo com a análise do arquivo no ghydra, percebemos a vulnerabilidade que seria explorada: Strings de Formatação. Tal vulnerabilidade pode ser percebida na linha 23 da função main do código decompilado no ghidra. A função `printf((char *) &local_38)` tem a capacidade de executar comandos armazenados na variável `local_38` (renomeada para `buffer` na imagem), qual recebe o input do usuário.
No código podemos ver que após uma verificação da variável `var`, caso a operação seja bem-sucedida o código inicializa a função `delulu`.

![image](https://github.com/HawkSecUnifei/resources-hawksec/assets/36544397/58fc3b5d-bc8a-4574-b097-009b86d38473)

Nessa função, é onde será printada a nossa flag. Seguindo com o exploit do `printf`, precisamos descobrir onde está armazenada a variável `var`, através do ponteiro disponível. Desse modo, abrimos o arquivo com gdb: `gdb ./delulu` já na pasta do arquivo, após isso utilizamos `ctrl + c` para cancelar a execução direta do programa e entrarmos no debugger do pwndbg.

Após entrar no debugger enviamos `si` (single instruction) e logo em seguida `%p.` cerca de 9 vezes, desse modo, fazendo o `printf` printar variáveis de ponteiro, assim conseguimos achar o endereço onde está alocada a variável `var`.

![image](https://github.com/HawkSecUnifei/resources-hawksec/assets/36544397/7da63bc6-98b8-4c5f-b16e-34598076de47)

Depois de enviar, o processo de debugging já terá começado e vamos enviar a instrução `n` (next) no console até chegar na instrução do `printf`.

![image](https://github.com/HawkSecUnifei/resources-hawksec/assets/36544397/c5ec0e58-b1b6-4fd7-93b3-6bbfd518abd4)

Identificando o `printf` podemos identificar o valor `0x1337babe` de `var` e também seu offset (7 pois é o 7º item do print) que será mais importante depois logo em seguida, possivelmente seu ponteiro, devemos pegar esse possível ponteiro e verificar do seguinte modo:

1. Acabamos de verificar que este endereço pertence à variável `var`.
   ![image](https://github.com/HawkSecUnifei/resources-hawksec/assets/36544397/8454773e-1cc0-41d2-aa3c-a0c2cf355cfe)
2. Precisamos agora descobrir qual o valor de `beef` para substituirmos dentro do código, para fazer isso de forma simples basta digitar `p 0xbeef` descobrimos assim que convertendo beef para decimal obtemos 48879.
   ![image](https://github.com/HawkSecUnifei/resources-hawksec/assets/36544397/3323ed31-f76c-4b19-8ca9-cc5cb1e08c1a)

3. Para prepararmos o prompt de envio precisamos analisar algumas informações primeiro:
`%n`, `%hn` e `%hhn` ocupam respectivamente 4, 2 e 1 byte. Agora estamos prontos para fazer o prompt para receber a flag: 
	`%48879c` – número de casas que o código deve pular para chegar a variável para sobrescrever;
	`7$` – offset;
	`%hn` – precisamos sobrescrever 2 bytes (beef) portanto usaremos `%hn`;
	
	Assim obtemos nosso promp para enviar no console:
	`%48879c%7$hn`
	Digitando isso no console obtemos a tão esperada flag:
![image](https://github.com/HawkSecUnifei/resources-hawksec/assets/36544397/8a3d6a1a-c145-4495-b8df-f5f38cd1498b)


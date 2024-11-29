# Write-Up: Factory

## **Descrição do Desafio**

**Nome:** Factory

**Plataforma:** Hack The Box

**Categoria:** Hacking

**Dificuldade:** Fácil

**Data:** Novembro/2024

**Descrição:**

Sua infraestrutura foi atacada, e a interface HMI (onde você monitora e controla os sistemas) ficou offline, fazendo com que você perdesse o controle de alguns PLCs (controladores lógicos programáveis) críticos no seu sistema de controle industrial (ICS). Pouco após o ataque começar, você conseguiu identificar o alvo do ataque, mas não teve tempo de agir.

O problema principal é que os sensores de nível de água (alto/baixo) do tanque de armazenamento de água estão corrompidos, o que fez com que o PLC entrasse em um estado de "parada" (halt). Isso significa que o sistema não está mais operando corretamente, e o tanque pode transbordar se não for esvaziado a tempo.

No entanto, a boa notícia é que um dos operadores de campo conseguiu estabelecer uma **conexão remota diretamente com a rede serial** do sistema. Isso significa que, mesmo sem a interface HMI, o operador pode se conectar diretamente aos dispositivos e enviar comandos para tentar recuperar o controle e evitar o transbordamento do tanque.

Em resumo, a prioridade agora é usar a conexão remota para:
 
1. Recuperar o controle do PLC.
2. Forçar a operação do sistema para **esvaziar o tanque** e **evitar o transbordamento**.

---

## **Passo a Passo da Solução**

### **1. Análise Inicial**

- **Arquivo/Entrada:** Foram fornecidos dois arquivos de entrada:[`interface_setup`](https://github.com/HawkSecUnifei/Writeups/blob/main/HackTheBox/Easy/Factory/files/interface_setup.png), [`PLC_Ladder_Logic`](https://github.com/HawkSecUnifei/Writeups/blob/main/HackTheBox/Easy/Factory/files/PLC_Ladder_Logic.pdf). O primeiro arquivo contém um esquemático do sistema, que é essencial para nos orientar durante a resolução do exercício. O segundo arquivo apresenta uma descrição detalhada da configuração da interface do sistema, incluindo o endereço do PLC e as numerações das funções, além de uma breve explicação sobre como a conexão é realizada. Também foi disponibilizado um endereço IP e uma porta, que utilizaremos para acessar o sistema por meio do **nc** (netcat).

### **2. Acessando o sistema**

- Assim que a instância é iniciada, é fornecido um endereço IP e uma porta. Para acessá-los, utilizamos o seguinte comando em um terminal Linux: `nc endereço_ip porta` .

### **3.  Como mandar um comando para o sistema?**

- Para manipular o sistema, precisamos executar um comando que corresponda a uma carga útil (payload) encontrada em um pacote padrão do protocolo Modbus.
    
    ### **Comandos Modbus Comuns (Códigos de Função):**
    
    - **0x01**: Ler Bobinas (saídas binárias).
    - **0x02**: Ler Entradas Discretas (entradas binárias).
    - **0x03**: Ler Registradores de Manutenção (entradas ou saídas analógicas).
    - **0x04**: Ler Registradores de Entrada (entradas analógicas).
    - **0x05**: Escrever em uma Única Registro.
    - **0x06**: Escrever em um Único Registrador.
    - **0x0F**: Escrever em Múltiplas Registro.
    - **0x10**: Escrever em Múltiplos Registradores.
    
    ### **Como é a estrutura do protocolo Modbus**:
    
    > **AA BB CCCC DDDD**
    > 
    
    AA = Endereço do PLC.
    
    BB = Código da função.
    
    CCCC = Endereço do registro em formato hexadecimal (000F).
    
    DDDD = Valor enviado para o registro, nesse caso será “FF00” ou “0000”.
    
    O endereço do PCI é 82 em decimal e 52 em hexadecimal, usaremos a função 5 (hex) para escrever em um único registro, o endereço do registro irá mudar dependendo do registro usado.
    

**4.  Sequência de Passos** 

1. Para ligar o modo manual
    
    Modbus command: 520526DBFF00
    
    ![image.png](/images/image.png)
    
2. Ligando a válvula de saída
    
    Modbus command: 52050034FF00
    
    ![image.png](/images/image%201.png)
    
3. Desligando a válvula de entrada
    
    Modbus command: 5205001AFF00
    
    ![image.png](/images/image%202.png)
    

Após essa sequência de passos o problema foi resolvido, portanto a flag é liberada.

**Flag:**

`HTB{14dd32_1091c_15_7h3_1091c_c12cu175_f02_1ndu572141_5y573m5}`

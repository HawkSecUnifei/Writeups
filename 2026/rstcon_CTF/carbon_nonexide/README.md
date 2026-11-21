# WriteUp: Carbon Noneoxide

## Descrição do Desafio

**Categoria:** rev 

**Descrição:**

> "There's a weird port open on my smart carbon monoxide detector. Here's the firmware from their website. Kinda weird website ngl."

### Arquivos

| Arquivo | Descrição |
| --- | --- |
| firmware.bin.chal | Firmware binário do dispositivo. |
| ChudMaxxing_AirSensor_v1.23.0_ProductSheet.pdf | Datasheet do produto. |

## Passo a Passo da Solução

### 1. Análise da Arquitetura e Extração de Strings

Analisando os primeiros bytes do firmware fornecido (`firmware.bin.chal`), identificamos a tabela de vetores do ARM Cortex-M3, apontando para a arquitetura LM3S6965, que é amplamente utilizada em emulações ARM com QEMU.

O primeiro passo prático é extrair as *strings* legíveis do binário para mapear o funcionamento básico e buscar credenciais armazenadas em texto claro.

```bash
strings firmware.bin.chal

```

A extração revela informações cruciais sobre um *Debug Shell* e a senha `charlotte` embutida no *offset* `0x1FD4`:

```text
[Admin] Task started
charlotte
--- Debug Shell ---
Device : LM3S6965 (Cortex-M3)
Sensor : virtual CO2 sensor
$ 
rstcon{???????????}

```

### 2. Análise do Fluxo e Comandos do Shell

A partir da análise do fluxo do sistema operacional FreeRTOS embutido, notamos que a *Admin Task* escuta na porta 1337. Ela aguarda uma conexão, solicita a credencial e, ao receber a senha correta (`charlotte`), libera o acesso ao *shell* interativo.

O tratador de comandos deste *shell* utiliza uma *switch table* baseada no primeiro caractere digitado pelo usuário. O comando `h` executa a ação de "Help" e, no ambiente do servidor remoto, revela a flag real no lugar do *placeholder* encontrado no firmware local.

### 3. Exploit

Para obter a flag, precisamos conectar ao servidor remoto utilizando o `netcat`, inserir a credencial encontrada durante a análise estática e solicitar a ajuda do sistema.

{% code title="Exploração" %}

```bash
nc 18.215.143.250 1337
# Inserir a senha hardcoded:
charlotte
# Executar o comando help para capturar a flag:
h

```

{% endcode %}

{% hint style="info" %}

**Nota (Buffer Overflow):** Além do caminho direto pela senha, o tratador do comando de injeção de leitura de CO (`i`) possui uma falha de limite de *buffer*. O contador de leituras é armazenado a exatos 512 bytes (128 slots) após o início do *array* na SRAM. A partir da 129ª injeção, o valor submetido sobrescreve o contador, e as injeções subsequentes corrompem o *task handle*, permitindo escrita arbitrária na memória do sistema.

{% endhint %}

{% hint style="warning" %}

**Aviso:** O servidor remoto do CTF já foi encerrado. A flag extraída via análise estática é apenas um *placeholder*, mas a metodologia de exploração descrita acima é o caminho planejado para a resolução.

{% endhint %}

### Flag

`rstcon{???????????}`

## Autor da WriteUp

[Membro de Exploitation - Jenni-Lopes](https://github.com/Jenni-Lopes)
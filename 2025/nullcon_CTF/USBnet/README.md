# WriteUp: USBnet
## Descrição do Desafio
Categoria: misc

Descrição:
> How good are your USB skills? Show me by recovering the flag!

### Arquivos
| Arquivo | Descrição |
| ------- | --------- |
| usbnet.pcapng | Captura de pacotes de rede fornecida |

> 📥 **Download:** [Arquivos](https://github.com/HawkSecUnifei/Writeups/raw/refs/heads/main/2025/nullcon_CTF/USBnet/usbnet.pcapng)

## Solução
Ao abrir o .pcap no wireshark nos deparamos com 226 pacotes do protocolo USB.

Como não são muitos, apenas de passar o seletor de cima para baixo podemos ver os pacotes com dados mais incomuns, que parecem ter algo além do próprio padrão do protocolo.

Assim no pacote 170,
![image](https://github.com/user-attachments/assets/39ebcd11-8bc4-4717-8e58-4a78923d18f6)
se nota um arquivo PNG dentro dos dados, começando pelo PNG e terminando pelo IEND.


Passando para o CyberChef, simplesmente colando os dados copiados `...as a Hex Stream` temos algo ilegível. Apagando todos os bytes anteriores ao começo do cabeçalho PNG, que é `89504e` (compare com qualquer PNG para comparar).
Use o `From Hex` do Cyberchef e temos a nossa imagem bruta, simplesmente use o `Render Image` e a imagem se formará.


![image](./qrcode.png)

Escaneando temos a flag.

### Flag: `ENO{USB_ETHERNET_ADAPTER_ARE_COOL_N!C3}`

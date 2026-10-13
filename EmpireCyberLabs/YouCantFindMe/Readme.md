# WriteUp: YouCantFIndMe

## Descrição do Desafio

**Categoria:** rev 

**Descrição:**

> The vault stands silent, its guardian convinced no one will ever peer behind its mask. But secrets whispered in code leave echoes for those patient enough to listen. Find what hides in the shadows.

### Arquivos

| Arquivo | Descrição |
| --- | --- |
| SecureVault.exe | Executável principal. |
| SecureVault.dll | Assembly .NET contendo a lógica principal. |
| SecureVault.pdb | Símbolos de depuração. |
| SecureVault.deps.json | Dependências do projeto. |
| SecureVault.runtimeconfig.json | Configuração do runtime .NET. |


## Passo a Passo da Solução

### 1. Análise do Arquivo Fornecido

Ao extrair o arquivo `YouCantFIndMe.zip`,existe um aplicativo desenvolvido em **.NET 6.0** com interface gráfica **WinForms**, confirmado pelo arquivo `SecureVault.runtimeconfig.json`:

```json
{
  "runtimeOptions": {
    "tfm": "net6.0",
    "frameworks": [
      { "name": "Microsoft.NETCore.App", "version": "6.0.0" },
      { "name": "Microsoft.WindowsDesktop.App", "version": "6.0.0" }
    ]
  }
}

```

Ao executar a aplicação, é exibido um formulário de login com os campos *Username*, *Password* e o botão *ACCESS VAULT*. Qualquer tentativa de autenticação incorreta resulta na mensagem `ACCESS DENIED - Invalid credentials`.

{% hint style="info" %}

Nota: Como binários em .NET não são compilados diretamente para código de máquina nativo, mas sim para CIL (Common Intermediate Language), podemos decompilar a DLL e ler o código-fonte praticamente original utilizando ferramentas como dnSpy ou ILSpy.
{% endhint %}

### 2. Decompilação 

Abrindo a DLL `SecureVault.dll` em um decompiler, navegamos até o *namespace* do projeto para inspecionar a classe do formulário de login (`LoginForm` / `MainForm`).

No método do evento de clique do botão (`LoginButton_Click`), encontramos a seguinte lógica de validação:

```csharp
private void LoginButton_Click(object sender, EventArgs e)
{
    string user = XorDecrypt(encryptedUser, xorKey);
    string pass = XorDecrypt(encryptedPass, xorKey);

    if (this.usernameBox.Text == user && this.passwordBox.Text == pass)
    {
        string flag = XorDecrypt(encryptedFlag, xorKey);
        this.statusLabel.ForeColor = Color.LimeGreen;
        this.statusLabel.Text = "ACCESS GRANTED!\n" + flag;
    }
    else
    {
        this.statusLabel.ForeColor = Color.Red;
        this.statusLabel.Text = "ACCESS DENIED\nInvalid credentials";
    }
}

```
Nesta lógica é possível notar que:

1. O programa armazena as credenciais e a flag em *arrays* de *bytes* criptografados (`encryptedUser`, `encryptedPass` e `encryptedFlag`).
2. A descriptografia é feita pela função `XorDecrypt()` utilizando a chave global `xorKey`.
3. Se inserirmos o *Username* e a *Password* corretos no formulário, o programa descriptografa e exibe a flag na tela.

### 3. Análise da Função de Descriptografia e Obtenção da Chave

Vendo a função `XorDecrypt` e a declaração das variáveis globais no mesmo arquivo:

```csharp
private static int xorKey = 66; // 0x42 em hexadecimal

private static string XorDecrypt(byte[] data, int key)
{
    byte[] result = new byte[data.Length];
    for (int i = 0; i < data.Length; i++)
    {
        result[i] = (byte)((int)data[i] ^ key);
    }
    return Encoding.ASCII.GetString(result);
}

```

A função apenas percorre o *array* de *bytes* recebido e aplica a operação **XOR** (`^`) com a chave fixa **66** (`0x42` em hex).

Ao checar o construtor estático (`.cctor`) ou as propriedades dos campos na aba de estruturas do dnSpy, encontramos os *bytes* brutos armazenados:

* **`encryptedUser` (10 bytes):** `[0x23, 0x25, 0x27, 0x2C, 0x36, 0x1D, 0x38, 0x27, 0x30, 0x2D]`
* **`encryptedPass` (15 bytes):** `[0x31, 0x2A, 0x76, 0x26, 0x72, 0x35, 0x1D, 0x32, 0x30, 0x72, 0x36, 0x72, 0x21, 0x72, 0x2E]`
* **`encryptedFlag` (29 bytes):** `[0x39, 0x3B, 0x72, 0x37, 0x1D, 0x24, 0x72, 0x37, 0x2C, 0x26, 0x1D, 0x2F, 0x71, 0x1D, 0x73, 0x2C, 0x1D, 0x36, 0x2A, 0x71, 0x1D, 0x31, 0x2A, 0x76, 0x26, 0x72, 0x35, 0x31, 0x3F]`

### 4. Descriptografando os Dados

Como a operação de XOR é simétrica ($A \oplus B \oplus B = A$), aplicar o XOR com `0x42` em cada *byte* revela a string original em ASCII. Assim obtemos:

#### **Username:** `agent_zero`

#### **Password:** `sh4d0w_pr0t0c0l`

#### **Flag:** `{y0u_f0und_m3_1n_th3_sh4d0ws}`

Inserindo as credenciais `agent_zero` e `sh4d0w_pr0t0c0l` na interface do aplicativo, o acesso é liberado e a flag é exibida no painel.

### Flag

`{y0u_f0und_m3_1n_th3_sh4d0ws}`

## Autor da WriteUp

[Membro de Exploitation - Jenni-Lopes](https://github.com/Jenni-Lopes)
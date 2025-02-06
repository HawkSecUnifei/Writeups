# WriteUp: flag checker
## Descrição do Desafio
**Categoria**: rev

**Descrição**:
> All you need to do is to guess the flag!

### Arquivos
| Arquivo | Descrição |
| ------- | --------- |
| flag_checker | Executável do desafio. |
| solve.py | Script em Python que resolve o desafio. |

> 📥 **Download:** [Arquivos](https://github.com/HawkSecUnifei/Writeups/raw/refs/heads/main/2025/nullcon_CTF/flag%20checker/Arquivos.zip)

## Solução
O desafio disponibliza um arquivo binário. Executando o arquivo:

```shell
└─$ ./flag_checker     
Enter the flag: flag{abc} 
Incorrect!
```

Como o título do desafio sugere, o programa apensa verifica se o input do usuário corresponde à flag. Abrindo o programa no ghidra:

{% code title="main.c" overflow="wrap" lineNumbers="true" %}

```c
undefined8 FUN_00101318(void)

{
  int iVar1;
  size_t sVar2;
  long in_FS_OFFSET;
  char local_38 [40];
  long local_10;
  
  local_10 = *(long *)(in_FS_OFFSET + 0x28);
  printf("Enter the flag: ");
  fgets(local_38,0x23,stdin);
  sVar2 = strcspn(local_38,"\n");
  local_38[sVar2] = '\0';
  iVar1 = FUN_0010127a(local_38);
  if (iVar1 == 0) {
    puts("Incorrect!");
  }
  else {
    puts("Correct!");
  }
  if (local_10 != *(long *)(in_FS_OFFSET + 0x28)) {
                    /* WARNING: Subroutine does not return */
    __stack_chk_fail();
  }
  return 0;
}
```

{% endcode %}

Podemos observar que essa função recebe o input do usuário na variável `local_38`, chama a função `FUN_0010127a` e verifica o retorno da função para saber se a flag está correta ou incorreta.

Nesse tipo de desafio, podemos utilizar um script que usa a biblioteca angr para resolver de maneira bem simples esse tipo de programa. Para utilizar esse script, precisamos descobrir o tamanho da flag, algum endereço que é acessado apenas quando o input corresponde à flag e algum endereço que é acessado apenas quando o endereço não corresponde à flag.

Olhando a chamada da função `fgets`, percebemos que a função pega 35 (0x23) caracteres do usuário, então a flag possui 35 caracteres. Como o `puts("Correct!");` é acessado apenas quando o input é igual a flag e `puts("Incorrect!");` quando o input é diferente da flag, podemos pegar o endereço dessas instruções.

{% code title="" overflow="wrap" lineNumbers="true" %}

```asm
        00101386 85 c0           TEST       EAX,EAX
        00101388 74 11           JZ         LAB_0010139b
        0010138a 48 8d 05        LEA        RAX,[s_Correct!_00102055]                        = "Correct!"
                 c4 0c 00 00
        00101391 48 89 c7        MOV        RDI=>s_Correct!_00102055,RAX                     = "Correct!"
        00101394 e8 07 fd        CALL       <EXTERNAL>::puts                                 int puts(char * __s)
                 ff ff
        00101399 eb 0f           JMP        LAB_001013aa
                             LAB_0010139b                                    XREF[1]:     00101388(j)  
        0010139b 48 8d 05        LEA        RAX,[s_Incorrect!_0010205e]                      = "Incorrect!"
                 bc 0c 00 00
        001013a2 48 89 c7        MOV        RDI=>s_Incorrect!_0010205e,RAX                   = "Incorrect!"
        001013a5 e8 f6 fc        CALL       <EXTERNAL>::puts                                 int puts(char * __s)
                 ff ff
```

{% endcode %}

Observando o assembly dessa parte do código, conseguimos ver que o endereço `0x00101391` é um endereço acessado quando o input do usuário é igual à flag e o endereço `0x0010139b` é acessado quando o input é incorreta. Portanto, podemos fazer o nosso script. (Obs: como a biblioteca angr utiliza o endereço base 0x400000, precisamo mudar os endereços obtidos levando em consideração essa base)

{% code title="solve.py" overflow="wrap" lineNumbers="true" %}

```py
import angr
import claripy

FLAG_LEN = 35

project = angr.Project("./flag_checker", main_opts={'base_addr': 0x400000}, auto_load_libs=False)


flag_chars = [claripy.BVS('flag_%d' % i, 8) for i in range(FLAG_LEN)]
flag = claripy.Concat( *flag_chars + [claripy.BVV(b'\n')]) # Add \n for scanf() to accept the input

state = project.factory.full_init_state(
        args=['./flag_checker'],
        add_options=angr.options.unicorn,
        stdin=flag,
)

for k in flag_chars:
    state.solver.add(k >= ord('!'))
    state.solver.add(k <= ord('~'))

sm = project.factory.simulation_manager(state)

good_address = 0x00401391   # Endereço correto
avoid_address = 0x0040139b  # Endereço incorreto

sm.explore(find=good_address, avoid=avoid_address)

print(sm)
print(sm.found[0].posix.dumps(0))
```

{% endcode %}

Agora, basta apenas rodar esse script. Rodando ele, obtemos:

```
<SimulationManager with 1 found, 34 avoid>
b'ENO{R3V3R53_3NG1N33R1NG_M45T3R!!!}"\n'
```

### Flag: `ENO{R3V3R53_3NG1N33R1NG_M45T3R!!!}`

## Autor da WriteUp
[Membro de Exploitation - CaioMendesRRosa](https://github.com/CaioMendesRRosa)
# Simulador de execução fora de ordem com scoreboard - MO401 - 2s2025

## Objetivo Geral

Adicionar minhas mudanças aqui

1. Montar init instruction status table, que no primeiro estágio está vazio  

    1.1 Parser das instruções 

    1.2 Armazena em cada estágio cada instrução está, None no começo
2. Init da functional unit status table 

    2.1. Parser do arquivo de config 

Issue:
Pega a instrução da tabela "Instruction status" 
Verifica qual fu ela quer usar
Verifica se tem fu correspondente livre na tabela "Functional unit status"
Verifica se alguém vai escrever no registrador rd (destino) na tabela "Register Status" 
Caso não, reserva FU na fus_status_table
Reserva RD register_status

## Testes 
### RAW (Read after write) Hazard -- Read Operands
```
fld  f1, 0(x2)     
fadd f3, f1, f4 
```

Saída esperada:
```
Instruction/Cicle  Issue  Read  Execute  Write
  fld  f1, 0(x2)       1     2        3      4
  fadd f3, f1, f4      2     5        7      8
```

### WAR (Write after read) Hazard -- Write Results
```
fadd f5, f2, f3
fmul f2, f6, f7
```

Saída esperada:
```
Instruction/Cicle  Issue  Read  Execute  Write
  fadd f5, f2, f3      1     2        4      5
  fmul f2, f6, f7      2     3        7      8
```

### WAW (Write after write) Hazard -- Issue
```
fmul f8, f1, f2
fadd f8, f3, f4
```

Saída esperada:
```
Instruction/Cicle  Issue  Read  Execute  Write
  fmul f8, f1, f2      1     2        6      7
  fadd f8, f3, f4      8     9       11     12
```

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


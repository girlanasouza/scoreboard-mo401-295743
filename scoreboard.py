import pandas as pd

OPCODES = {
    'fld': 0,
    'fsd': 1,
    'fadd': 2,
    'fsub': 3,
    'fmul': 4,
    'fdiv': 5
}

REG_PREFIXES = {
    'x': 'int',
    'f': 'float'
}

def has_pending_instructions(inst_status):
    return any(inst['write_result'] is None for inst in inst_status)

def formatar_tabela_scoreboard(instruction_status):
    df = pd.DataFrame(instruction_status)
    tabela_final = df[['inst', 'issue', 'read_operands', 'execution_complete', 'write_result']]

    tabela_final = tabela_final.rename(columns={
        'inst': 'Instruction/Cicle',
        'issue': 'Issue',
        'read_operands': 'Read',
        'execution_complete': 'Execute', 
        'write_result': 'Write'
    })

    tabela_final = tabela_final.fillna("-")

    return tabela_final

# ----------------------------------------------------------------------- #

# INIALIZAÇÃO DOS REGISTRADORES
def ini_register_status():
    register_status = {}
    for i in range(32):
        register_status[f"x{i}"] = {"x": i, "x_type": "int", "writer": None} # x0...x31
    for i in range(32):
        register_status[f"f{i}"] = {"f": i, "f_type": "float", "writer": None} # f1...f31
    return register_status


# PARSER E INICIALIZAÇÃO DAS INSTRUÇÕES 
def init_instruction_status(program_name):
    instruction_status =[]
    with open(program_name, "r") as file:
        for i, line in enumerate(file):
            op = OPCODES[line.split()[0]]
            if (op == 0 or op==1):
                rd = line.split()[1].replace(",", "")
                rs1 = line.split()[2].split("(")[1].replace(")", "")
                rs2 = None
                imm = line.split()[2].split("(")[0]
                fu_type = 0
            else:
                if op == 2 or op == 3: fu_type = 2
                elif op == 4: fu_type = 1
                elif op == 5: fu_type = 3
                rd = line.split()[1].replace(",", "")
                rs1 = line.split()[2].replace(",", "")
                rs2 = line.split()[3].replace(",", "")
                imm = None          
            instruction_status.append({ 
                "id": i,
                "inst": line.replace("\n", ""),
                "opcode": op,
                "fu_name": None,
                "fu_type": fu_type,
                "rd": rd,
                "rs1": rs1,
                "rs2": rs2,
                "issue": None,
                "read_operands": None,
                "execution_complete": None,
                "write_result": None

            })
    return  instruction_status

# PARSER E INICIALIZAÇÃO DAS UNIDADES FUNCIONAIS 
def parser_fus_configs(config_name):
    fus_configs = {}
    with open(config_name, 'r') as f:
        linhas = f.readlines()
        for linha in linhas:
            partes = linha.strip().split()
            fus_configs[partes[0]] = {'qtd': partes[1], 'cycles': partes[2]}
    return fus_configs

def init_fus_status(programa_config):
    fus_configs = parser_fus_configs(programa_config)
    fus_status = {}
    for uf_type, config in fus_configs.items():
        if uf_type == 'int':
            op = 0
        elif uf_type == 'mult':
            op = 1
        elif uf_type == 'add':
            op = 2
        elif uf_type == 'div':
            op = 3
        for c in range(int(config['qtd'])):
            fus_status[f'{uf_type}{c+1}'] = {
                'Opcode': op, 
                'Busy': False, 
                'Op': None, 
                'Fi': None,
                'Fj': None, 
                'Fk': None, 
                'Qj': None, 
                'Qk': None,
                'Rj': False, 
                'Rk': False, 
                'Cycles_left': int(config['cycles']), 
                'Cycles': int(config['cycles'])
            }
    return fus_status

## ESTÁGIO: ISSUE
def issue(instr, fus_status, register_status):
    id_i = instr['id']
    rs1_i = instr['rs1']
    rs2_i = instr['rs2']
    rd_i = instr['rd']
    fu_type = instr['fu_type']

    for fu_name, fu in fus_status.items():
        if fu['Opcode'] != fu_type:
            continue

        if fu['Busy']:
            continue

        if register_status[rd_i]['writer'] is not None:
            return False
        
        fu['Busy'] = True
        fu['Op'] = id_i
        fu['Fi'] = rd_i
        fu['Fj'] = rs1_i
        fu['Fk'] = rs2_i
        fu['Qj'] = register_status[rs1_i]['writer'] if rs1_i is not None else None
        fu['Qk'] = register_status[rs2_i]['writer'] if rs2_i is not None else None
        fu['Rj'] = fu['Qj'] is None
        fu['Rk'] = fu['Qk'] is None
        register_status[rd_i]['writer'] = fu_name
        instr['fu_name'] = fu_name
        return True
    return False

## ESTÁGIO: READ OPERANDS
def read_operands(fu, inst, register_status, instruction_status, cycle):
    if not fu['Rj']:
        writer_j = register_status.get(fu['Fj'], {}).get('writer')
        if writer_j is None:  # ninguém está escrevendo em Rj
            fu['Rj'] = True
            fu['Qj'] = None
        # se alguem estver escrevendo -- Rj não fica true e não consegue avançar na leitura

    if not fu['Rk']:
        if not fu['Fk']:  # não tem Fk
            fu['Rk'] = True
        else:
            writer_k = register_status.get(fu['Fk'], {}).get('writer')
            if writer_k is None:
                fu['Rk'] = True
                fu['Qk'] = None

    if fu['Rj'] and fu['Rk']:
        inst['read_operands'] = cycle
        fu['Rj'] = False
        fu['Rk'] = False

## ESTÁGIO: COMPLETE EXECUTION
def execute(fu, cycle, inst):
    if fu['Cycles_left'] > 0:
        fu['Cycles_left'] -= 1
    if fu['Cycles_left'] == 0:
        inst['execution_complete'] = cycle
        fu['Cycles_left'] = fu['Cycles']

## ESTÁGIO: WRITE RESULTS
def write_results(fus_status, inst, cycle, register_status):
    fu = fus_status[inst['fu_name']]
    fi = fu['Fi'] # pega o resgistrador de destino da inst atual
    for other_fu_name, other_fu in fus_status.items():
        if other_fu_name == inst['fu_name']:
            continue

        if other_fu['Rj'] and other_fu['Fj'] == fi: # verifica se o Fj é o Fi que vai ser escrito
            # se sim, ele não escreve no Fi
            return 
        if other_fu['Rk'] and other_fu['Fk'] == fi:  # verifica se o Fk é o Fi que vai ser escrito
            return 
    # se Fi não for Fj/Fk para nenhuma outra fu, prossegue com a escrita
    inst['write_result'] = cycle

    # libera o registrador de destino no register_status
    if fi and register_status[fi]['writer'] == inst['fu_name']:
        register_status[fi]['writer'] = None
    # libera a unidade funcional que está fazendo a execução da instrução
    fu.update({
        'Busy': False, 'Op': None, 'Fi': None, 'Fj': None, 'Fk': None,
        'Qj': None, 'Qk': None, 'Rj': False, 'Rk': False
    })

## SCOREBOARD
def scoreboard(prog_file, fus_file):
    pc = 0
    cycle = 1

    register_status = ini_register_status()
    instruction_status = init_instruction_status(prog_file)
    fus_status = init_fus_status(fus_file)

    while pc < len(instruction_status) or has_pending_instructions(instruction_status):
        liberar_write = False
        
        # WRITE RESULT
        for inst in instruction_status:
            if inst['execution_complete'] is not None and inst['execution_complete'] < cycle and inst['write_result'] is None:
                write_results(fus_status, inst, cycle, register_status)
                liberar_write = True
                
        # EXECUTE 
        for inst in instruction_status:
            if inst['read_operands'] is not None and inst['read_operands'] < cycle and inst['execution_complete'] is None:
                fu = fus_status[inst['fu_name']]
                execute(fu, cycle, inst)

        # READ OPERANDS
        for inst in instruction_status:
            if inst['issue'] is not None and inst['read_operands'] is None:
                if liberar_write:
                    continue  # pula leitura no ciclo de write_results
                fu = fus_status[inst['fu_name']]
                read_operands(fu, inst, register_status, instruction_status, cycle)

        # ISSUE
        if pc < len(instruction_status):
            if not liberar_write: 
                next_instruction = instruction_status[pc]
                if issue(next_instruction, fus_status, register_status):
                    next_instruction['issue'] = cycle
                    pc += 1
        cycle += 1
    return instruction_status


if __name__ == "__main__":
    prog_file = "tests/ex4.s" # nome do arquivo do programa assembly
    fus_file = "tests/uf_config4.in" # nome do programa com as configuraçoes das UFs
    
    instruction_status = scoreboard(prog_file, fus_file)

    tabela_de_resultados = formatar_tabela_scoreboard(instruction_status)
    print(tabela_de_resultados.to_string(index=False))
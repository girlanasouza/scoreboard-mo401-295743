import pandas as pd

import parser_inst
import parser_config



'''
    busy: unidade funcional ocupada
    op: operação em execução
    fi: registrador de destino
    fj, fk: registradores de origem
    qj, qk: unidade funcional que produzirá o valor dos registradores de origem
    rj, rk: bits que indicam se os valores dos registradores de origem estão
'''

def init_register_status():
    register_status = {}

    # Registradores inteiros (x0..x31)
    for i in range(32):
        register_status[f"x{i}"] = {"x": i, "x_type": "int", "writer": None}

    # Registradores de ponto flutuante (f0..f31)
    for i in range(32):
        register_status[f"f{i}"] = {"f": i, "f_type": "float", "writer": None}

    return register_status

# Instruction status
def init_inst_status(program_name):
    insts = parser_inst.parse_instructions(program_name)
    inst_status = []
    for inst in insts:
        inst_status.append({"instr": inst, "issue": None, "read": None, "exec": None, "write": None})
    return inst_status

# Functional unit status
def init_fus(program_name):
    fus_configs = parser_config.parse_config(program_name)
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


def aux_issue(instruction):
    opcode = instruction['opcode']
    rs1 = instruction['rs1']
    rs1_type = instruction['rs1_type']
    rs2 = instruction['rs2']
    rs2_type = instruction['rs2_type']
    rd = instruction['rd']
    rd_type = instruction['rd_type']

    prefix_rd = "x" if rd_type == "int" else "f"
    key_rd = f"{prefix_rd}{rd}"

    prefix_rs1 = "x" if rs1_type == "int" else "f"
    key_rs1 = f"{prefix_rs1}{rs1}"

    prefix_rs2 = "x" if rs2_type == "int" else "f"
    key_rs2 = f"{prefix_rs2}{rs2}"

    return opcode, key_rd, key_rs1, key_rs2

def issue(idx, opcode, key_rd, key_rs1, key_rs2, fus, register_status, inst_status, stages):
    '''
        aloca unidade funcional
        marca registrador destino como ocupado
        atualiza instruction_status[instr]["issue"] = cycle
    '''

    opcodes = {0, 1, 2, 3, 4, 5} 

    for fu_name, fu in fus.items():
        if fu['Opcode'] != opcode or fu['Busy']:
            continue
        if  register_status[key_rd]['writer'] is not None:
            continue
        fu['Busy'] = True
        fu['Op'] = opcode
        fu['Fi'] = key_rd if opcode in opcodes else None
        fu['Fj'] = key_rs1
        fu['Fk'] = key_rs2
        fu['Qj'] = register_status[key_rs1]['writer']
        fu['Qk'] = register_status[key_rs2]['writer']
        fu['Rj'] = fu['Qj'] is None
        fu['Rk'] = fu['Qk'] is None
        fu['CyclesLeft'] = fu['Cycles']
        
        if opcode in opcodes:
            register_status[key_rd]['writer'] = fu_name

        inst_status[idx]['issue'] = 1
        stages['Instruction/Cicle'][idx] = inst_status[idx]['instr']
        stages['Issue'][idx] = inst_status[idx]['issue']

        return True
    return False  

def can_read(instruction, fus, register_status):
    '''
        retorna true se Rj e Rk forem verdadeiros
    '''
    return True

def read(unit, cycke, instruction_status):
    '''
        marca instrução como tendo lido os operandos
        atualiza instruction_status[instr]["read"] = cycle
    '''

def execute(unit, cycle, instruction_status):
    '''
        decrementa cycles_left
        se cycles_left == 0, atualiza instruction_status[instr]["execute"] = cycle
    '''

def can_write(unit, fus, register_status):
    '''
        retorna true se nenhuma outra unidade funcional estiver dependendo do registrador de destino
    '''
    return True

def write(unit, cycle, instruction_status, register_status):
    '''
        marca registrador destino como livre
        atualiza instruction_status[instr]["write"] = cycle
        libera unidade funcional
    '''
    pass


def step_cycle(cycle, program, instruction_status, fus, register_status):
    '''
        executa na ordem: isseu, read, execute, write
        atualiza estruturas de dados
    '''

def init_stages(num_instructions):
    stages = {
    "Header": ["Instruction/Cycle", "Issue", "Read", "Execute", "Write"],
        "Instruction/Cicle": [None]*len(inst_status),
        "Issue": [None]*len(inst_status),
        "Read": [None]*len(inst_status),
        "Execute": [None]*len(inst_status),
        "Write": [None]*len(inst_status)
    }

def any_fu_busy(fus):
    for fu_name, fu in fus.items():
        if fu['Busy']:
            return True
    return False

def scoreboard(program_name):
    instructions_status = init_inst_status(program_name) # inicializa instruction status table
    register_status = init_register_status() # inicializa register status table
    fus = init_fus(program_name) # inicializa functional unit status table
    stages = init_stages(len(instructions_status)) # inicializa estágios

    # inst_status[idx]['instr']
    for idx, i in enumerate(inst_status):
        inst = i['instr']
        opcode, key_rd, key_rs1, key_rs2 = aux_issue(inst)
        print(inst)

    
    ## ISSUE
    idx = 0
    issued = issue(
        idx, opcode, key_rd, key_rs1, key_rs2,
        fus, register_status, inst_status, stages
    )
    if issued:
        idx += 1

    return instructions_status

def montar_instrucao(stages):
    for idx, i in enumerate(stages['Instruction/Cicle']):
        if i is not None:
            if i['opcode'] == 0:
                rd = f"f{i['rd']}" if i['rd_type'] == 'float' else f"x{i['rd']}"
                rs1 = f"f{i['rs1']}" if i['rs1_type'] == 'float' else f"x{i['rs1']}"
                imm = i.get('imm', 0)
                i_mont = f"fld {rd}, {imm}({rs1})"
                stages['Instruction/Cicle'][idx] = i_mont 


def print_result(stages):
    df_stages = pd.DataFrame({
        "Instruction/Cycle": stages["Instruction/Cicle"],
        "Issue": stages["Issue"],
        "Read": stages["Read"],
        "Execute": stages["Execute"],
        "Write": stages["Write"]
    })
    print(df_stages.to_string(index=False))



if __name__ == "__main__":
    # mostrar_tabela()ambiente
    nome_programa = "tests/ex.s"
    inst_status = scoreboard(nome_programa)
    print(inst_status)
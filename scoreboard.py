import pandas as pd

import parser_inst
import parser_config

# instructions_status = [
#     {
#         "Instruction": "fld f1, 0(x1)",
#         "Issue": None,
#         "Read": None,
#         "Execute": None,
#         "Write": None
#     }
# ]

#  Register Status Table
#  Mapeia cada registrador para a unidade funcional que irá escrever nele


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
    for uf, config in fus_configs.items():
        for c in config:
            qnt = int(c)
            ciclos = int(config[c])
            fus_status[uf] = []
            for i in range(qnt):
                fus_status[uf].append({
                    'id': f'{uf}{i+1}',
                    'busy': False,
                    'op': None,
                    'fi': None,
                    'fj': None,
                    'fk': None,
                    'qj': None,
                    'qk': None,
                    'rj': False,
                    'rk': False,
                    'cycles_left': 0,
                    'cycles': ciclos
                })
    return fus_status


def can_issue(instruction, fus_status, register_status):
    '''
        verifica se há unidade funcional livre para a instrução
        verifica se o registrador de destino não está aguardando outra unidade
    '''


    return True

def issue(instruction, fus, register_status):
    '''
        aloca unidade funcional
        marca registrador destino como ocupado
        atualiza instruction_status[instr]["issue"] = cycle
    '''

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

def scoreboard(program_name):
    instructions_status = init_inst_status(program_name) # inicializa instruction status table

    return instructions_status


def print_result(instruction_status, program):
    print(f"{'Instruction/Cycle':<25}{'Issue':<8}{'Read':<8}{'Execute':<10}{'Write':<8}")
    for instr, status in zip(program, instruction_status):
        issue   = status.get("issue",  "-")
        read    = status.get("read",   "-")
        execute = status.get("exec",   "-")
        write   = status.get("write",  "-")
        
        print(f"{instr:<25}{issue!s:<8}{read!s:<8}{execute!s:<10}{write!s:<8}")



if __name__ == "__main__":
    # mostrar_tabela()ambiente
    nome_programa = "tests/ex.s"
    inst_status = scoreboard(nome_programa)
    print(inst_status)
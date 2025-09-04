import pandas as pd
import os

OPCODES = {
    'fld': 0,
    'fsd': 1,
    'fadd': 2,
    'fsub': 3,
    'fmul': 4,
    'fdiv': 5
}

# Define register prefix constants
REG_PREFIXES = {
    'x': 'int',
    'f': 'float'
}

def has_pending_instructions(inst_status):
    return any(inst['write_result'] is None for inst in inst_status)

def init_register_status():
    register_status = {}
    for i in range(32):
        register_status[f"x{i}"] = {"x": i, "x_type": "int", "writer": None}
    for i in range(32):
        register_status[f"f{i}"] = {"f": i, "f_type": "float", "writer": None}
    return register_status

def init_instruction_status(program_name):
    instruction_status =[]
    with open(program_name, "r") as file:
        for i, line in enumerate(file):
            op = OPCODES[line.split()[0]]
            if (op == 0):
                rd = line.split()[1].replace(",", "")
                rs1 = line.split()[2].split("(")[1].replace(")", "")
                rs2 = None
                fu_type = 0
            elif (op==1):
                rd = None
                rs1 = line.split()[1].replace(",", "")
                rs2 = None
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
                'just_freed': False,
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


def issue(instr, fus_status, register_status, fus_liberadas_no_ciclo):
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

        if rd_i and register_status[rd_i]['writer'] is not None:
            return False

        if fu_name in fus_liberadas_no_ciclo:
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

        if rd_i is not None:
            register_status[rd_i]['writer'] = fu_name
        instr['fu_name'] = fu_name

        return True

    return False

def read_operands(fu, inst, register_status, cycle):
    if not fu['Rj']:
        writer_j = register_status.get(fu['Fj'], {}).get('writer')
        if writer_j is None: 
            fu['Rj'] = True
            fu['Qj'] = None

    if not fu['Rk']:
        if not fu['Fk']:  
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

def execute(fu, cycle, inst):
    if fu['Cycles_left'] > 0:
        fu['Cycles_left'] -= 1
    if fu['Cycles_left'] == 0:
        inst['execution_complete'] = cycle
        fu['Cycles_left'] = fu['Cycles']

def write_results(fus_status, inst, cycle, register_status):
    fu = fus_status[inst['fu_name']]
    fi_register = fu['Fi']

    if fi_register:
        for other_fu_name, other_fu in fus_status.items():
            if other_fu_name == inst['fu_name']:
                continue

            if other_fu['Rj'] and other_fu['Fj'] == fi_register:
                return None, None 

            if other_fu['Rk'] and other_fu['Fk'] == fi_register:
                return None, None 

    inst['write_result'] = cycle
    fu.update({
        'Busy': False, 'Op': None, 'Fi': None, 'Fj': None, 'Fk': None,
        'Qj': None, 'Qk': None, 'Rj': False, 'Rk': False
    })

    if fi_register and register_status[fi_register]['writer'] == inst['fu_name']:
        register_status[fi_register]['writer'] = None
    return fi_register, inst['fu_name']

def scoreboard(prog_file, fus_file):
    register_status = init_register_status()
    instruction_status = init_instruction_status(prog_file)
    fus_status = init_fus_status(fus_file)

    pc = 0
    cycle = 1

    while pc < len(instruction_status) or has_pending_instructions(instruction_status):

        liberar_write = False
        fu_name_i = ""
        registradores_escritos_no_ciclo = set()
        fus_liberadas_no_ciclo = set()
        for inst in instruction_status:
            if inst['execution_complete'] is not None and inst['execution_complete'] < cycle and inst['write_result'] is None:
                resultado = write_results(fus_status, inst, cycle, register_status)
                if resultado != (None, None):
                    fi_escrita, fu_name_i = resultado
                    if fi_escrita:
                        registradores_escritos_no_ciclo.add(fi_escrita)

                    if fu_name_i:
                        fus_liberadas_no_ciclo.add(fu_name_i)
                    liberar_write = True

        for inst in instruction_status:
            if inst['read_operands'] is not None and inst['read_operands'] < cycle and inst['execution_complete'] is None:
                fu = fus_status[inst['fu_name']]
                execute(fu, cycle, inst)

        # 1. Read operands
        for inst in instruction_status:
            if inst['issue'] is not None and inst['read_operands'] is None:
                fu = fus_status[inst['fu_name']]
                if fu['Fj'] in registradores_escritos_no_ciclo or fu['Fk'] in registradores_escritos_no_ciclo:
                    continue  # Pula a leitura APENAS para esta instrução
                read_operands(fu, inst, register_status, cycle)

        if pc < len(instruction_status):
            next_instruction = instruction_status[pc]
            if liberar_write and next_instruction['rd'] == fi_escrita:
                pass
            else:
                fu_type = next_instruction['fu_type']
                if any(fus_status[fu]['Opcode'] == fu_type and fu in fus_liberadas_no_ciclo for fu in fus_status):
                    pass
                else:
                    if issue(next_instruction, fus_status, register_status, fus_liberadas_no_ciclo):
                        next_instruction['issue'] = cycle
                        pc += 1


        cycle += 1
    return instruction_status

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

if __name__ == "__main__":
    # listas de programas e configs
    instr_files = [f"./tests/in_puts_insts/t{i}.S" for i in range(1, 14)] # mudar aqui para testar
    fus_files   = [f"./tests/in_puts_configs/fu_config{i}.in"   for i in range(1, 14)] # mudar aqui para testar

    output_file = "./tests/out_puts/resultados.out"

    with open(output_file, "w") as out:
        for i in range(len(instr_files)):
            prog_file = instr_files[i]
            fus_file = fus_files[i]

            out.write(f"\n=== Execução {i+1}: {prog_file} + {fus_file} ===\n")

            instruction_status = scoreboard(prog_file, fus_file)
            tabela_de_resultados = formatar_tabela_scoreboard(instruction_status)

            out.write(tabela_de_resultados.to_string(index=False))
            out.write("\n\n")
import pandas as pd

instructions_status = [
    {
        "Instruction": "fld f1, 0(x1)",
        "Issue": None,
        "Read": None,
        "Execute": None,
        "Write": None
    }
]

register_status = {
    "x0" : None, "x1" : None, "x2" : None, "x3" : None, "x4" : None, "x5" : None, 
    "x6" : None, "x7" : None, "x8" : None, "x9" : None, "x10": None, "x11": None, 
    "x6" : None, "x7" : None, "x8" : None, "x9" : None, "x10": None, "x11": None,
    "x12": None, "x13": None, "x14": None, "x15": None, "x16": None, "x17": None,
    "x18": None, "x19": None, "x20": None, "x21": None, "x22": None, "x23": None,
    "x24": None, "x25": None, "x26": None, "x27": None, "x28": None, "x29": None,
    "x30": None, "x31": None,


    "f0": None, "f1": None, "f2": None, "f3": None, "f4": None, "f5": None,
    "f6": None, "f7": None, "f8": None, "f9": None, "f10": None, "f11": None,
    "f12": None, "f13": None, "f14": None, "f15": None, "f16": None, "f17": None,
    "f18": None, "f19": None, "f20": None, "f21": None, "f22": None, "f23": None,
    "f24": None, "f25": None, "f26": None, "f27": None, "f28": None, "f29": None,
    "f30": None, "f31": None, "f0": None, "f31": None
}

'''
    busy: unidade funcional ocupada
    op: operação em execução
    fi: registrador de destino
    fj, fk: registradores de origem
    qj, qk: unidade funcional que produzirá o valor dos registradores de origem
    rj, rk: bits que indicam se os valores dos registradores de origem estão
'''


def parse_config(arquivo):
    # Status das unidades funcionais
    uf_status = {}
    with open(arquivo, 'r') as f:
        linhas = f.readlines()
        for linha in linhas:
            partes = linha.strip().split()
            uf_status[partes[0]] = {partes[1]: partes[2]}
    return uf_status

def init_fus(uf_status):
    fus = {}
    for uf, config in uf_status.items():
        for c in config:
            qnt = int(c)
            ciclos = int(config[c])
            fus[uf] = []
            for i in range(qnt):
                fus[uf].append({
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
    return fus


def can_issue(instruction, fus, register_status):
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

def scoreboard():
    # Exemplo de uso das funções
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
    scoreboard()
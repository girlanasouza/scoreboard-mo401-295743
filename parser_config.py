def parse_config(arquivo):
    fus_configs = {}
    with open("tests/uf_config2.in", 'r') as f:
        linhas = f.readlines()
        for linha in linhas:
            partes = linha.strip().split()
            fus_configs[partes[0]] = {partes[1]: partes[2]}
    return fus_configs
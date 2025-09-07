def formatar_texto(texto, maiusculas=False):
    texto_formatado = ' '.join(texto.split())
    if maiusculas:
        texto_formatado = texto_formatado.upper()
    return texto_formatado

def inverter_string(texto):
    return texto[::-1]
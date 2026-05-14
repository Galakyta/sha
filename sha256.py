'''pre processamento'''

'''operacoes basicas'''

def rotr (x,n):
    #girando a direita
    return ((x >> n) | (x << (32 - n))) & 0xFFFFFFFF

def shr(x, n):
    return x >> n


'''
assert rotr(0b00000000000000000000000000000001, 1) == 0b10000000000000000000000000000000
assert shr(0b00000000000000000000000000001000, 3) == 0b00000000000000000000000000000001
print("foi")'''

def ch(x, y, z):
    return ((x & y) ^ (~x & z)) & 0xFFFFFFFF

def maj(x,y,z):
    return ((x & y) ^ (x & z) ^ (y & z)) & 0xFFFFFFFF

def sigma0_maiusculo(x):
    return rotr(x,2) ^ rotr(x,13) ^ rotr(x,22)

def sigma1_maiusculo(x):
    return rotr(x,6) ^ rotr(x,11) ^ rotr(x,25)

def sigma0_minusculo(x):
    return rotr(x, 7) ^ rotr(x, 18) ^ shr(x, 3)

def sigma1_minusculo(x):
    return rotr(x,17) ^ rotr(x,19) ^ shr(x,10)

x, y, z = 0b1100, 0b1010, 0b0110

#assert ch(x, y, z) & 0xF == 0b1010  # resultado simplificado
#assert maj(x, y, z) & 0xF == 0b1110
#print("✅ Passo 2: Funções lógicas OK")

K = [0x428a2f98, 0x71374491, 0xb5c0fbcf, 0xe9b5dba5, 0x3956c25b, 0x59f111f1,
    0x923f82a4, 0xab1c5ed5, 0xd807aa98, 0x12835b01, 0x243185be, 0x550c7dc3,
    0x72be5d74, 0x80deb1fe, 0x9bdc06a7, 0xc19bf174, 0xe49b69c1, 0xefbe4786,
    0x0fc19dc6, 0x240ca1cc, 0x2de92c6f, 0x4a7484aa, 0x5cb0a9dc, 0x76f988da,
    0x983e5152, 0xa831c66d, 0xb00327c8, 0xbf597fc7, 0xc6e00bf3, 0xd5a79147,
    0x06ca6351, 0x14292967, 0x27b70a85, 0x2e1b2138, 0x4d2c6dfc, 0x53380d13,
    0x650a7354, 0x766a0abb, 0x81c2c92e, 0x92722c85, 0xa2bfe8a1, 0xa81a664b,
    0xc24b8b70, 0xc76c51a3, 0xd192e819, 0xd6990624, 0xf40e3585, 0x106aa070,
    0x19a4c116, 0x1e376c08, 0x2748774c, 0x34b0bcb5, 0x391c0cb3, 0x4ed8aa4a,
    0x5b9cca4f, 0x682e6ff3, 0x748f82ee, 0x78a5636f, 0x84c87814, 0x8cc70208,
    0x90befffa, 0xa4506ceb, 0xbef9a3f7, 0xc67178f2]

H = [
    0x6a09e667, 0xbb67ae85, 0x3c6ef372, 0xa54ff53a,
    0x510e527f, 0x9b05688c, 0x1f83d9ab, 0x5be0cd19
]

def pre_processamento(mensagem_bytes):
    if isinstance(mensagem_bytes, str):
        mensagem_bytes = mensagem_bytes.encode('utf-8') 
        
    comprimento_bits = len(mensagem_bytes) * 8
    
    mensagem_bytes += b'\x80'
    
    while (len(mensagem_bytes) % 64) != 56:
        mensagem_bytes += b'\x00'
        
    mensagem_bytes += comprimento_bits.to_bytes(8, 'big')
    
    blocos = [mensagem_bytes[i:i+64] for i in range(0, len(mensagem_bytes), 64)]
    
    return blocos

'''
print("Testando pré-processamento...")
blocos_vazio = pre_processamento(b"")
print(f"Mensagem vazia: {len(blocos_vazio)} bloco(s)")
print(f"Tamanho do bloco: {len(blocos_vazio[0])} bytes (deve ser 64)")
'''

def expandir_mensagem(bloco):
    
    w = [0] * 64
    
    
    for i in range(16):
        inicio = i * 4
        w[i] = int.from_bytes(bloco[inicio:inicio+4], 'big')
        
    for i in range(16, 64):
        s0 = sigma0_minusculo(w[i-15])
        s1 = sigma1_minusculo(w[i-2])
        w[i] = (w[i-16] + s0 + w[i-7] + s1) & 0xFFFFFFFF

    return w  # Bug 4 fixed: return w is inside the function

test_bloco = b'A' * 64

w_expandido = expandir_mensagem(test_bloco)

print(f"\nExpansao 64 palavras")
for i in range(5):
    print(f" w[{i}] = {hex(w_expandido[i])}")
    

def comprimir(bloco, H):
    w = expandir_mensagem(bloco)

    a, b, c, d, e, f, g, h = H

    for i in range(64):
        T1 = (h + sigma1_maiusculo(e) + ch(e, f, g) + K[i] + w[i]) & 0xFFFFFFFF
        T2 = (sigma0_maiusculo(a) + maj(a, b, c)) & 0xFFFFFFFF

        h = g
        g = f
        f = e
        e = (d + T1) & 0xFFFFFFFF
        d = c
        c = b
        b = a
        a = (T1 + T2) & 0xFFFFFFFF

    return [
        (H[0] + a) & 0xFFFFFFFF,
        (H[1] + b) & 0xFFFFFFFF,
        (H[2] + c) & 0xFFFFFFFF,
        (H[3] + d) & 0xFFFFFFFF,
        (H[4] + e) & 0xFFFFFFFF,
        (H[5] + f) & 0xFFFFFFFF,
        (H[6] + g) & 0xFFFFFFFF,
        (H[7] + h) & 0xFFFFFFFF,
    ]


def sha256(mensagem):
    blocos = pre_processamento(mensagem)

    estado = H[:] 

    for bloco in blocos:
        estado = comprimir(bloco, estado)

    return ''.join(f'{x:08x}' for x in estado)


# Teste
print(sha256(""))
print(sha256("abc"))
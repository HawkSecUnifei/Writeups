import hashlib

def find_collision(target):
    target_hash = hashlib.md5(target.encode()).hexdigest()
    target_prefix = target_hash[:6]
    print(f"Prefixo alvo: {target_prefix}")

    i = 0
    while True:
        candidate = f"hawk{i}"
        hash_value = hashlib.md5(candidate.encode()).hexdigest()
        if hash_value.startswith(target_prefix):
            print(f"Colisão Encontrada: Entrada = {candidate}, Hash = {hash_value}")
            return
        i += 1

find_collision("Flag do Desafio")
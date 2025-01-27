import hashlib

def find_collision(target):
    target_hash = hashlib.md5(target.encode()).hexdigest()
    target_prefix = target_hash[:6]
    print(f"Target Prefix: {target_prefix}")

    i = 0
    while True:
        candidate = f"test{i}"
        hash_value = hashlib.md5(candidate.encode()).hexdigest()
        if hash_value.startswith(target_prefix):
            print(f"Found collision: Input = {candidate}, Hash = {hash_value}")
            return candidate
        i += 1

collision_input = find_collision("Flag")
print(f"Collision Input: {collision_input}")
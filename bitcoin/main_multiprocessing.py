import base64

code = base64.b64encode(br"""
import binascii
import json
import random
import socket
from hashlib import sha256
from pprint import pprint
from multiprocessing import Process, Array, Value, Manager, freeze_support

# user = '324oYVqismopzC6REA6LQC5UFM737xDRsh'  # the bitcoin wallet address
user = 'timycool.python_worker'  # the bitcoin wallet address

# host = 'ss.antpool.com'  # the bitcoin pool address
# port = 443  # the bitcoin pool port
host = 'btc.f2pool.com'  # the bitcoin pool address
port = 3333  # the bitcoin pool port

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)


def main():
    extra_info, extra_nonce1, extra_nonce2_size = initialize()
    print("initialized")
    if authorize():
        print("authorized")
        while True:
            block = get_block()
            print("GOT BLOCK:")
            pprint(block)
            job_id, _, _, _, _, _, _, ntime, _ = block['params']
            block_header, target, extra_nonce2 = calculate_header(block, extra_nonce1, extra_nonce2_size)
            procs = []
            manager = Manager()
            solved = Value("b", False)
            solution = manager.dict()
            for i in range(999):
                procs.append(Process(target=mine, args=(block_header, target, i, solved, solution)))
                procs[i].start()
            for proc in procs:
                proc.join()

            print("\n\n")
            print("COMPLETE!!!!")
            pprint(dict(solution))
            submit(job_id, extra_nonce2, ntime, solution['nonce'])
            break


def initialize():
    # server connection
    sock.connect((host, port))
    print("connected to the pool")
    payload = {
        "id": 1,
        "method": "mining.subscribe",
        "params": []
    }

    send_to_pool(payload)
    return get_json_result_from_pool()


def authorize():
    payload = {
        "id": 2,
        "method": "mining.authorize",
        "params": [user, "password"]
    }
    send_to_pool(payload)
    return get_json_result_from_pool()


def get_block():
    print("getting block")
    response = ""
    while response.count("{") < 1 or response.count("{") != response.count("}"):
        response += get_raw_from_pool()
        if "mining.notify" not in response:
            response = ""

    responses = [json.loads(res) for res in response.split('\n') if 'mining.notify' in res]
    return responses[0]


def submit(job_id, extra_nonce2, ntime, nonce):
    payload = {
        "id": 4,
        "method": "mining.submit",
        "params": [user, job_id, extra_nonce2, ntime, nonce]
    }
    send_to_pool(payload)
    print(get_json_result_from_pool())


def calculate_header(block: dict, extra_nonce1: str, extra_nonce2_size: int):
    job_id, prev_hash, coinbase1, coinbase2, merkle_branch, version, bits, ntime, clean_job = block['params']
    target = bits[2:] + "00" * (int(bits[:2], 16) - 3)
    target = target.zfill(64)
    merkle_root, extra_nonce2 = calculate_block_merkle_root(block, extra_nonce1, extra_nonce2_size)
    print(merkle_root)
    block_header = version + prev_hash + merkle_root + bits + ntime
    return block_header, target, extra_nonce2


def calculate_block_merkle_root(block: dict, extra_nonce1: str, extra_nonce2_size: int):
    _, _, coinbase1, coinbase2, merkle_branch, _, _, _, _ = block['params']
    extra_nonce2 = '00' * extra_nonce2_size
    coinbase = coinbase1 + extra_nonce1 + extra_nonce2 + coinbase2
    coinbase_hash_bin = hash_bin(coinbase)

    print(f"coinbase:{coinbase} coinbase_hash:{coinbase_hash_bin}")

    merkle_root = coinbase_hash_bin
    for h in merkle_branch:
        merkle_root = double_hash(merkle_root + binascii.unhexlify(h))
    merkle_root = binascii.hexlify(merkle_root).decode()
    return merkle_root, extra_nonce2


def mine(block_header, target, index, solved: Value, solution):
    index = str(index).zfill(3)
    print(f"{index}:", "started")
    temp_block_header = block_header
    block_hash = hash_bin(temp_block_header)
    block_hash = binascii.hexlify(block_hash).decode()
    nonce = ""
    while block_hash > target and not solved.value:
        nonce = hex(random.randint(0, 2 ** 32 - 1))[2:].zfill(8)
        temp_block_header = block_header + nonce + '000000800000000000000000000000000000000000000000000000000000000000000000000000000000000080020000'

        block_hash = hash_bin(temp_block_header)
        block_hash = binascii.hexlify(block_hash).decode()
        print(f"{index}:", "hash:", block_hash, "|", "target:", target)
        # print(block_hash < target)
        # print("\n\n\n")
    if block_hash < target:
        solved.value = True
        solution["hash"] = block_hash
        solution["target"] = target
        solution["header"] = temp_block_header
        solution["nonce"] = nonce


def hash_bin(arg):
    return double_hash(binascii.unhexlify(arg))


def double_hash(arg):
    return sha256(sha256(arg).digest()).digest()


def send_to_pool(dic: dict):
    sock.send(json.dumps(dic).encode() + b'\n')


def get_raw_from_pool():
    lines = sock.recv(1024).decode()  # getting data from the pool
    # print(lines)
    return lines


def get_json_result_from_pool():
    lines = get_raw_from_pool().split("\n")
    print(lines)
    return json.loads(lines[0])['result']


if __name__ == '__main__':
    freeze_support()
    main()
""")
exec(base64.b64decode(code))

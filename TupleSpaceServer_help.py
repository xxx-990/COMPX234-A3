import socket
import sys
import threading
import time

# using a lock -- see https://realpython.com/python-thread-lock/
# sockets -- see https://realpython.com/python-sockets/#python-socket-api-overview

# Shared data structures
tuple_space = {}
total_clients = 0
total_operations = 0
read_count = 0
get_count = 0
put_count = 0
error_count = 0
lock = threading.Lock()

def receive_n(sock, num_bytes):
    """Read exactly num_bytes from the socket."""
    data = b""
    while len(data) < num_bytes:
        chunk = sock.recv(num_bytes - len(data))
        if not chunk:  # Connection closed or error
            break
        data += chunk
    return data


def increment_stat(stat_name):
    global total_clients, total_operations, read_count, get_count, put_count, error_count
    if stat_name == "total_clients":
        total_clients += 1
    elif stat_name == "total_operations":
        total_operations += 1
    elif stat_name == "read_count":
        read_count += 1
    elif stat_name == "get_count":
        get_count += 1
    elif stat_name == "put_count":
        put_count += 1
    elif stat_name == "error_count":
        error_count += 1

def print_stats():
    while True:
        time.sleep(10)
        with lock:
            tuple_count = len(tuple_space)
            avg_key_size = avg_value_size = avg_tuple_size = 0
            if tuple_count > 0:
                total_key_size = sum(len(k) for k in tuple_space.keys())
                total_value_size = sum(len(v) for v in tuple_space.values())
                avg_key_size = total_key_size / tuple_count
                avg_value_size = total_value_size / tuple_count
                avg_tuple_size = avg_key_size + avg_value_size
            print("\n--- Tuple Space Stats ---")
            print(f"Tuples: {tuple_count}")
            print(f"Avg Tuple Size: {avg_tuple_size:.2f}")
            print(f"Avg Key Size: {avg_key_size:.2f}")
            print(f"Avg Value Size: {avg_value_size:.2f}")
            print(f"Clients: {total_clients}")
            print(f"Operations: {total_operations}")
            print(f"READs: {read_count}")
            print(f"GETs: {get_count}")
            print(f"PUTs: {put_count}")
            print(f"Errors: {error_count}\n")

def handle_client(client_socket):
    global tuple_space

    increment_stat("total_clients")
    try:
        while True:
            # TASK 1: Read the first 3 bytes to get the message size, then read
            # the remaining (size - 3) bytes and decode to a string.
            # Hint: use receive_n(). If nothing arrives, client disconnected — break.
            size_data = receive_(client_socket,3)
            if not size_data:  #没有数据。说明客户端断开连接
                break
            msg_size = int(size_data.decode().strip())  #转换为整数，得到完整消息长度
            message_buffer = receive_n(client_socket, meg_size - 3).decode().strip()   #读取剩余的消息内容并解码




            # Handle the request
            response = handle_request(message_buffer)

            # TASK 2: Build the response string with its size prepended (3 digits + space),
            # then send it. Hint: total size = len(response) + 4. Use sendall().
            total_size = len(response) + 4   #总长度=内容长度+4（3位长度+1个空格）
            response_header = f"{total_size:03d}"    #长度补零为3位
            full_response = response_header + response   #拼接完整响应消息
            client_socket.sendall(full_response.encode())   #发送给客户端


    except (socket.error, ValueError):
        pass
    finally:
        client_socket.close()

def handle_request(message):
    global tuple_space
    increment_stat("total_operations")
    if len(message) < 3:
        increment_stat("error_count")
        return "ERR Invalid message"

    # split(" ", 2) keeps values with spaces intact in parts[2]
    parts = message.split(" ", 2)
    if len(parts) < 2:
        increment_stat("error_count")
        return "ERR Invalid message"

    op = parts[0]
    key = parts[1]
    if len(key) > 999:
        increment_stat("error_count")
        return "ERR Key too long"

    with lock:
        if op == "R":
            # TASK 3: READ — look up key in tuple_space.
            # Return "OK (<key>, <value>) read" or "ERR <key> does not exist".
            increment_stat("read_count")   #READ操作：查询键对应的值，不删除
            if key in tuple_space:
                value = tuple_space[key]
                return f"OK (<key>, <value>) read"
            else:
                return f"ERR <key> does not exist"
            



        elif op == "G":
            # TASK 4: GET — remove key from tuple_space and return its value.
            # Return "OK (<key>, <value>) removed" or "ERR <key> does not exist".
            # Hint: dict.pop(key, None) removes and returns the value, or None if missing.
            increment_stat("get_count")   #GET操作：查询并删除键值对
            value = tuple_space.pop(key, None)
            if value is not None:
                return f"OK (<key>, <value>) removed"
            else:
                return f"ERR <key> does not exist"
            
          



        elif op == "P":
            if len(parts) < 3:
                increment_stat("error_count")
                return "ERR Invalid PUT"
            value = parts[2]
            # TASK 5: PUT — add (key, value) only if key does not already exist.
            # Validate: len(value) <= 999 and len(key + " " + value) <= 970.
            # Return "OK (<key>, <value>) added" or "ERR <key> already exists".
            increment_stat("put_count")   #PUT操作：添加键值对，仅当键不存在时添加
            if key in tuple_space:
                return f"ERR {key} already exists"
            #校验值长度和总长度是否符合要求
            if len(value) <= 999 and len(key + " " + value) <= 970:
                tuple_space[key] = value
                return f"OK (<key>, <value>) added"
            
            else:
                increment_stat("error_count")
                return "ERR Unknown operation"


def main():
    if len(sys.argv) != 2:
        print("Usage: python3 TupleSpaceServer.py <port>")
        sys.exit(1)

    port = int(sys.argv[1])
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(("", port))
    server_socket.listen(5)
    print(f"Server started on port {port}")

    # Start the stats printing thread (daemon=True means it stops when main exits)
    stats_thread = threading.Thread(target=print_stats, daemon=True)
    stats_thread.start()

    try:
        while True:
            # Wait for a client to connect, then spawn a new thread for it
            (client_socket, address) = server_socket.accept()
            print(f"Connection from {address} accepted.")
            print(f"Create a new thread that will deal with the client which just connected.")
            client_thread = threading.Thread(target=handle_client, args=(client_socket,))
            client_thread.start()
    except KeyboardInterrupt:
        print("Shutting down server...")
    finally:
        server_socket.close()

if __name__ == "__main__":
    main()
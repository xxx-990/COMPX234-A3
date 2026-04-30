import socket
import sys
import os

def main():
    if len(sys.argv) != 4:
        print("Usage: python tuple_space_client.py <server-hostname> <server-port> <input-file>")
        sys.exit(1)

    hostname = sys.argv[1]
    port = int(sys.argv[2])
    input_file_path = sys.argv[3]

    if not os.path.exists(input_file_path):
        print(f"Error: Input file '{input_file_path}' does not exist.")
        sys.exit(1)

    with open(input_file_path, 'r') as file:
        lines = file.readlines()

    # TASK 1: Create a TCP/IP socket and connect it to the server.
    # Hint: socket.socket(socket.AF_INET, socket.SOCK_STREAM) creates the socket.
    # Then call sock.connect((hostname, port)) to connect.
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((hostname, port))  #发起连接


    try:
        for line in lines:
            line = line.strip()
            if not line:
                continue

            parts = line.split(" ", 2)
            cmd = parts[0]
            message = ""

            # TASK 2: Build the protocol message string to send to the server.
            # Format:  "NNN X key"        for READ / GET
            #          "NNN P key value"   for PUT
            # where NNN is the total message length as a zero-padded 3-digit number,
            # X is "R" for READ and "G" for GET.
            # Hint: for READ/GET, size = 6 + len(key). For PUT, size = 7 + len(key) + len(value).
            # Reject lines with invalid format or key+" "+value > 970 chars.
            if cmd == "READ":
                if len(parts) < 2:  #校验格式
                    print(f"{line}: ERR Invalid READ format")
                    continue
                key = parts[1]
                body = f"R {key}"   #消息体："R key"
                total_len = 6 + len(key)
                message = f"{total_len:03d}{body}"   #拼接完整消息：3位长度 + 空格 + 消息体
            
            elif cmd == "GET":
                if len(parts)<2:
                    print(f"{line}: ERR Invalid GET format")
                    continue
                key = parts[1]
                body = f"G{key}"
                total_len = 6 + len(key)
                message = f"{total_len:03d}{body}"

            elif cmd == "PUT":
                if len(parts)<3:
                    print(f"{line}: ERR Invalid PUT format")
                    continue
                key = parts[1]
                value = parts[2]
                if len(f"{key}{value}") >970:
                    print(f"{line}: ERR Key+Value too long (max 970 chars)")
                    continue
                body = f"P{key}{value}"
                total_len = 7+len(key)+len(value) 
                message = f"{total_len:03d}{body}"

            else:
                print(f"{line}: ERR Unknown command '{cmd}'")
                continue

            


            # TASK 3: Send the message to the server, then receive the response.
            # - Send:    sock.sendall(message.encode())
            # - Receive: first read 3 bytes to get the response size (like the server does).
            #            Then read the remaining (size - 3) bytes to get the response body.
            sock.sendall(message.encode())  #发送信息给服务器
            resp_len_bytes = sock.recv(3)
            if not resp_len_bytes:  #服务端断开连接
                print(f"{line}: ERR Server disconnected")
                break
            resp_len = int(resp_len_bytes.decode().strip())

            response_buffer = sock.recv(resp_len - 3)
            


            response = response_buffer.decode().strip()
            print(f"{line}: {response}")

    except (socket.error, ValueError) as e:
        print(f"Error: {e}")
        sys.exit(1)
    finally:
        # TASK 4: Close the socket when done (already called for you — explain why
        # finally: is the right place to do this even if an error occurs above).
        sock.close()

if __name__ == "__main__":
    main()
import socket

def send_message(message,host='127.0.01',port=65432):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        #主动发起连接
        s.accept((host,port))
        print(f"Connected to server at {host}:{port}")

        try:
            #发送数据
            s.sendall(message.encode())
            print(f"Sent:{message}")

            #接收相应
            response = s.recv(1024)
            print(f"Received:{response.decode()}")

        except Exception as e:
            print(f"Connection error: {e}")

        finally:
            print("Connection closed")
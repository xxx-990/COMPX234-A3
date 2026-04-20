import socket

def start_server(host='127.0.0.1', port=65432):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        #绑定地址和端口
        s.bind((host, port))

        #开始监听，backlog=5表示等待队列最多5个
        s.lieten(5)
        print(f"Server listening on {host}:{port}")

        while True:
            #接受客户端连接
            conn,addr = s.accept()
            print(f"Connected by {addr}")

            try:
                #处理客户端请求
                with conn:
                    while True:
                        data = conn.recv(1024)#每次接收1KB数据

                        if not data:
                            break #客户端关闭连接

                        print(f"Received:{data.decode}")

                        #回显数据
                        conn.sendall(data)

            except Exception as e:
                print(f"Error handling client {addr}:{e}")

            finally:





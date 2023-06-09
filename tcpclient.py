import socket

class TCPClient:

    # へなちょこブラウザ-----
    
    # TCP通信を行うクライアントを表すクラス

    def request(self):
        #　サーバーへリクエストを送信する

        print('=== クライアントを起動します ===')

        try:
            # socketを生成
            client_socket = socket.socket()
            client_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

            # サーバーと接続する
            print('=== サーバーと接続します ===')
            client_socket.connect(("127.0.0.1", 80))
            print('=== サーバーとの接続が完了しました ===')

            #サーバーに送信するリクエストを、ファイルから取得する
            with open('client_send.txt', "rb") as f:
                request = f.read()
                
            #サーバーへリクエストを送信する
            #send = 送信
            response = client_socket.send(request)

            #サーバーからレスポンスが送られてくるのを待ち、取得する
            # recv = 受信
            response = client_socket.recv(4096)

            # レスポンスの内容をファイルに書き出す
            with open("client_recv.txt","wb") as f:
                f.write(response)

            #通信を終了させる
            client_socket.close()
            

        finally:
            print("=== クライアントを停止します。 ===")


if __name__ == "__main__":
    client = TCPClient()
    client.request()
import socket
from henango.server.worker import Worker

class Server:
    # webサーバーを表すクラス

    def serve(self):
        """
        サーバーを起動する
        """

        print('==== server: サーバーを起動します===')

        try:
            # socketを生成
            server_socket = self.create_server_socket()

            while True:
                #　外部からの接続待ち、接続があったらコネクションを確立する
                print("=== server: クライアントからの接続を待ちます ===")
                (client_socket, address) = server_socket.accept()
                print(f"=== server: クライアントとお接続を完了しました　remote_address:{address} ===")

                # クライアントを処理するスレッドを作成
                thread = Worker(client_socket, address)

                # スレッドを実行
                thread.start()

        finally:
            print('=== server: サーバーを停止します。 ===')        
    
    def create_server_socket(self) -> socket:
        # 通信を待ち,受けるためのserver_socketを生成する
        
        # socketの生成
        server_socket = socket.socket()
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR,1)

        #socketをlocalhostのポート8080番に割り当てる
        server_socket.bind(("localhost",8080))
        server_socket.listen(10)
        return server_socket
    






import os
import re
import traceback
from re import Match
from socket import socket
from datetime import datetime
from threading import Thread
from typing import Tuple

from henango.http.request import HTTPRequest
from henango.http.response import HTTPResponse
from henango.urls.resolver import URLResolver


class Worker(Thread):
    # 拡張子とMINE Typeの対応
    MIME_TYPES = {
        "html": "text/html; charset=UTF-8",
        "css": "text/css",
        "png": "image/png",
        "jpg": "image/jpg",
        "gif": "image/gif",
    }

    # ステータスコードとステータスラインの対応
    STATUS_LINES = {
        200: "200 OK",
        302: "302 Found",
        404: "404 Not Found",
        405: "405 Method Allowed",
    }

    def __init__(self, client_socket: socket,address: Tuple[str, int]):
        super().__init__()

        self.client_socket = client_socket
        self.client_address = address

    def run(self) -> None:
        """
        クライアントとの接続済みのsocketを引数として受け取り、
        リクエストを処理してレスポンスを送信
        """

        try:
            # クライアントから送られてきたデータを取得
            request_bytes = self.client_socket.recv(4096)
    

            #クライアントから送られてきたデータをファイルに書き出す
            with open('text/server_recv.txt',"wb") as f:
                f.write(request_bytes)

            #リクエストラインをバースする
            request = self.parse_http_request(request_bytes)

            # URL解決を試みる
            view = URLResolver().resolve(request)
            
            # URL解決できた場合は、viewからレスポンスを取得する
            response = view(request)

            # レスポンスボディを生成
            if isinstance(response.body, str):
                response.body = response.body.encode()

            # レスポンスラインを生成
            response_line = self.build_response_line(response)
            
            # レスポンスヘッダーを生成
            response_header = self.build_response_header(response,request)

            # レスポンス全体を生成する
            response_bytes = (response_line + response_header + "\r\n").encode() + response.body

            # クライアントへレスポンスを送信する
            self.client_socket.send(response_bytes)

        except Exception:
            # リクエストの処理中に例外が発生した場合はコンソールにエラーログを出力し、
            # 処理を続行する
            print("=== worker: リクエストの処理中にエラーが発生しました ===")
            traceback.print_exc()

        finally:
            # 例外が発生した場合も、発生しなかった場合も、TCP通信のcloseは行う
            print(f"=== worker: クライアントとの通信を終了します　remote_address:{self.client_address} ===")
            self.client_socket.close()

    def parse_http_request(self, request:bytes) -> HTTPRequest:
        """
        生のHTTPリクエストを、HTTPRequesクラスへ変換する
        """
        # リクエスト全体を
        #　ー　リクエストライン（１行目） 
        #　ー　リクエストヘッダー（２行目　〜　空行）
        #　ー　リクエストボディ（空行〜）
        #　にパースする

        request_line, remain = request.split(b"\r\n", maxsplit=1)
        request_header, request_body = remain.split(b"\r\n\r\n", maxsplit=1)

        # リクエストラインを文字列に変換してパースする
        method, path, http_version = request_line.decode().split(" ")

        # リクエストラインを文字列に変換してパースする
        headers = {}
        for header_row in request_header.decode().split("\r\n"):
            key, value = re.split(r": *", header_row, maxsplit=1)
            headers[key] = value
            
        

        cookies = {}
        if "Cookie" in headers:
            # str から list　へ変換
            cookie_strings = headers["Cookie"].split("; ")

            # list から dict へ変換
            for cookie_string in cookie_strings:
                name, value = cookie_string.split("=", maxsplit=1)
                cookies[name] = value

        print(cookies)

        return HTTPRequest(
            method=method, path=path, http_version=http_version, headers=headers, cookies=cookies, body=request_body
        )

    def build_response_line(self, response: HTTPResponse) -> str:
        """
        レスポンスラインを構築
        """
        status_line = self.STATUS_LINES[response.status_code]
        return f"HTTP/1.1 {status_line}"

    def build_response_header(self,response: HTTPResponse, request: HTTPRequest) -> str:
        """
        レスポンスヘッダーを構築する
        """

        # content_typeが指定されていない場合はpathから特定する        
        if response.content_type is None:
            # pathから拡張子を取得
            if "." in request.path:
                ext = request.path.rsplit(".",maxsplit=1)[-1]
                # 拡張子からMIME Typeを取得
                # 知らない対応してない拡張子の場合はoctet-streamとする
                response.content_type = self.MIME_TYPES.get(ext, "application/octet-stream")
            else:
                # pathに拡張子がない場合はhtml扱いする
                response.content_type = "text/html; charset=UTF-8"

        response_header = ""
        response_header += f"Date: {datetime.utcnow().strftime('%a, %d %b %Y %H:%M:%S GMT')}\r\n"
        response_header += "Host: HenaServer/0.1\r\n"
        response_header += f"Content-Length: {len(response.body)}\r\n"
        response_header += "Connection: Close\r\n"
        response_header += f"Content-Type: {response.content_type}\r\n"

        

        # cookieヘッダーの生成
        for cookie in response.cookies:
            cookie_header = f"Set-Cookie: {cookie.name}={cookie.value}"
            if cookie.expires is not None: 
                cookie_header += f"; Expires={cookie.expires.strftime('%a, %d %b %Y %H:%M:%S GMT')}"
            if cookie.max_age is not None:
                cookie_header += f"; Max-Age={cookie.max_age}"
            if cookie.domain:
                cookie_header += f"; Domain={cookie.domain}"
            if cookie.path:
                cookie_header += f"; Path={cookie.path}"
            if cookie.secure:
                cookie_header += f"; Secure"
            if cookie.http_only:
                cookie_header += f"; HttpOnly"

            response_header += cookie_header + "\r\n"

        # その他ヘッダーの生成
        for header_name, header_value in response.headers.items():
            response_header += f"{header_name}: {header_value}\r\n"

        return response_header
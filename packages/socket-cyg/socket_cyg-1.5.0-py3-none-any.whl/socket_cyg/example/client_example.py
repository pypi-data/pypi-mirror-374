# pylint: skip-file
import time

from socket_cyg.socket_client import SocketClient


if __name__ == "__main__":
    def my_callback(data: bytes):
        """示例回调函数。"""
        print(f"回调收到数据: {data.decode('UTF-8')}")

    client = SocketClient("127.0.0.1", 9001, my_callback)
    if client.connect():
        try:
            client.send_data(b"ffffff")
            time.sleep(500000)
        finally:
            client.disconnect()
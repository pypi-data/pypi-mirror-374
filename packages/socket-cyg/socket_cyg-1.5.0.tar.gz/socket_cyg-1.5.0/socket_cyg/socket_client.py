# pylint: skip-file

import socket
import threading
import logging
from typing import Callable, Optional


class SocketClient:
    """用于持续与服务器通信的 TCP Socket 客户端."""

    def __init__(self, host: str, port: int,
                 receive_callback: Optional[Callable[[bytes], None]] = None,
                 buffer_size: int = 1024):
        """初始化 Socket 客户端.

        Args:
            host: 要连接的服务器主机名或 IP 地址.
            port: 服务器端口号.
            receive_callback: 处理接收数据的回调函数, 回调函数应接受 bytes 类型作为唯一参数.
            buffer_size: 接收缓冲区大小（字节）,默认为 1024.
        """
        self.host = host
        self.port = port
        self.buffer_size = buffer_size
        self.receive_callback = receive_callback
        self.socket = None
        self.is_connected = False
        self.receive_thread = None
        self.logger = logging.getLogger(self.__class__.__name__)

    def connect(self) -> tuple[bool, str]:
        """建立与服务器的连接, 连接成功后会自动启动后台线程持续接收数据.

        Returns:
            tuple[bool, str]: 连接成功返回 (True, 描述信息), 否则返回 (False, 错误信息).
        """
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.connect((self.host, self.port))
            self.is_connected = True
            self.logger.info("已连接到服务器 %s: %s", self.host, self.port)

            self.receive_thread = threading.Thread(
                target=self._receive_data,
                daemon=True
            )
            self.receive_thread.start()
            return True, "连接成功"
        except Exception as e:
            self.logger.warning("连接失败, %s", str(e))
            self.is_connected = False
            return False, str(e)

    def disconnect(self):
        """断开与服务器的连接并释放资源."""
        if self.is_connected:
            self.is_connected = False
            try:
                if self.socket:
                    self.socket.close()
                if self.receive_thread and self.receive_thread.is_alive():
                    self.receive_thread.join(timeout=1)
            except Exception as e:
                self.logger.warning("断开连接时出错: %s", str(e))
            finally:
                self.logger.info("已断开与服务器的连接")

    def send_data(self, data: bytes) -> tuple[bool, str]:
        """向服务器发送数据.

        Args:
            data: 要发送的字节数据.

        Returns:
            tuple[bool, str]: 发送成功返回 (True, 成功信息), 失败返回 (False, 失败信息).
        """
        if not self.is_connected:
            self.logger.warning("未连接到服务器")
            return False, "未连接服务端"

        try:
            self.socket.sendall(data)
            return True, "发送成功"
        except Exception as e:
            self.logger.warning("发送数据出错: %s", str(e))
            self.disconnect()
            return False, str(e)

    def _receive_data(self):
        """持续接收数据的内部方法."""
        while self.is_connected:
            try:
                data = self.socket.recv(self.buffer_size)
                if not data:  # 服务器关闭连接
                    self.logger.info("服务器关闭了连接")
                    self.disconnect()
                    break

                if self.receive_callback:
                    self.logger.info("收到数据: %s", data)
                    self.logger.info("触发回调函数")
                    self.receive_callback(data)
                else:
                    self.logger.info("收到数据: %s", data)
            except ConnectionResetError:
                self.logger.warning("连接被服务器重置")
                self.disconnect()
                break
            except Exception as e:
                if self.is_connected:
                    self.logger.warning("接收数据出错: %s", str(e))
                    self.disconnect()
                break

    def __enter__(self):
        """实现上下文管理协议,进入时自动连接."""
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """实现上下文管理协议,退出时自动断开连接."""
        self.disconnect()

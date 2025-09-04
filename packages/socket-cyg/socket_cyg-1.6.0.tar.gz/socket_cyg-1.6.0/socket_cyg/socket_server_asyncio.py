# pylint: skip-file
"""异步socket."""
import asyncio
import datetime
import logging
import os
import pathlib
import socket
import sys
from asyncio import AbstractEventLoop
from logging.handlers import TimedRotatingFileHandler


class CygSocketServerAsyncio:
    """异步socket class."""
    LOG_FORMAT = "%(asctime)s - %(levelname)s - %(module)s:%(lineno)d - %(message)s"

    clients = {}  # 保存已连接的client
    tasks = {}
    loop: AbstractEventLoop = None

    def __init__(self, address: str = "127.0.0.1", port: int = 1830, save_log: bool = False):
        """CygSocketServerAsyncio 构造方法.

        Args:
            address: 服务端 ip address.
            port: 服务端端口.
            save_log: 是否保存日志, 默认不保存.
        """
        logging.basicConfig(level=logging.INFO, encoding="UTF-8", format=self.LOG_FORMAT)

        self.save_log = save_log
        self._address = address
        self._port = port
        self.logger = logging.getLogger(__name__)
        self._file_handler = None
        self._initial_log_config()

    def _initial_log_config(self) -> None:
        """日志配置."""
        if self.save_log:
            self._create_log_dir()
            self.logger.addHandler(self.file_handler)  # 保存日志

    @staticmethod
    def _create_log_dir():
        """判断log目录是否存在, 不存在就创建."""
        log_dir = pathlib.Path(f"{os.getcwd()}/log")
        if not log_dir.exists():
            os.mkdir(log_dir)

    @property
    def file_handler(self) -> TimedRotatingFileHandler:
        """设置保存日志的处理器, 每隔 24h 自动生成一个日志文件.

        Returns:
            TimedRotatingFileHandler: 返回 TimedRotatingFileHandler 日志处理器.
        """
        if self._file_handler is None:
            self._file_handler = TimedRotatingFileHandler(
                f"{os.getcwd()}/log/socket.log",
                when="D", interval=1, backupCount=10, encoding="UTF-8"
            )
            self._file_handler.namer = self._custom_log_name
            self._file_handler.setFormatter(logging.Formatter(self.LOG_FORMAT))
        return self._file_handler

    @staticmethod
    def _custom_log_name(log_path: str):
        """自定义新生成的日志名称.

        Args:
            log_path: 原始的日志文件路径.

        Returns:
            str: 新生成的自定义日志文件路径.
        """
        _, suffix, date_str, *__ = log_path.split(".")
        new_log_path = f"{os.getcwd()}/log/socket_{date_str}.{suffix}"
        return new_log_path

    async def operations_return_data(self, data: bytes):
        """操作返回数据."""
        data = data.decode("UTF-8")
        self.logger.warning("没有重写 operations_return_data 函数, 默认是回显.")
        return data

    async def socket_send(self, client_connection, data: bytes):
        """发送数据给客户端."""
        if client_connection:
            client_ip = client_connection.getpeername()
            await self.loop.sock_sendall(client_connection, data)
            self.logger.info("%s 发送成功, %s", client_ip, data)
        else:
            self.logger.info("发送数据 % 失败", data)

    async def receive_send(self, client_connection: socket.socket):
        """接收后发送数据."""
        client_ip = client_connection.getpeername()[0]  # 获取连接客户端的ip
        try:
            while data := await self.loop.sock_recv(client_connection, 1024 * 1024):
                self.logger.info("%s", "-" * 60)
                self.logger.info("接收到客户端 %s 的数据: %s", client_ip, data.decode("UTF-8"))
                send_data = await self.operations_return_data(data)  # 这个方法实现具体业务, 需要重写, 不重写回显
                send_data_byte = send_data.encode("UTF-8")
                await self.loop.sock_sendall(client_connection, send_data_byte)
                self.logger.info("回复客户端 %s 的数据是: %s", client_ip, send_data)
                self.logger.info("%s", "-" * 60)
        except Exception as e:  # pylint: disable=W0718
            self.logger.warning("通讯出现异常, 异常信息是: %s", str(e))
        finally:
            self.clients.pop(client_ip)
            self.tasks.get(client_ip).cancel()
            self.logger.warning("客户端 %s 断开了", client_ip)
            client_connection.close()

    async def listen_for_connection(self, socket_server: socket):
        """异步监听连接."""
        self.logger.info("服务端 %s 已启动,等待客户端连接", socket_server.getsockname())

        while True:
            self.loop = asyncio.get_running_loop()
            client_connection, address = await self.loop.sock_accept(socket_server)
            client_connection.setblocking(False)
            self.clients.update({address[0]: client_connection})
            self.tasks.update({
                address[0]: self.loop.create_task(self.receive_send(client_connection))
            })
            self.logger.warning("客户端 %s 连接了", address)

    async def run_socket_server(self):
        """运行socket服务, 并监听客户端连接."""
        socket_server = socket.socket()
        socket_server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        socket_server.setblocking(False)
        socket_server.bind((self._address, self._port))
        socket_server.listen()
        await self.listen_for_connection(socket_server)

# -*- coding: utf-8 -*-

from typing import (
    Any,
    Callable,
    cast,
    Dict,
    IO,
    Iterator,
    List,
    Optional,
    Tuple,
)

from paramiko import Transport, RSAKey
from paramiko.sftp_attr import SFTPAttributes
from paramiko.sftp_client import SFTPClient
from paramiko.ssh_exception import AuthenticationException
from paramiko.ssh_exception import BadHostKeyException
from paramiko.ssh_exception import NoValidConnectionsError
from paramiko.ssh_exception import SSHException


class SftpClient:
    """
    It provides a wrapper for an SFTP connection...

    Examples...

        client = SftpClient("test.rebex.net", "demo", "password")
        client.connect()

        for x in client.list_files("/"):
            print(x)

        client.close()

        with SftpClient("test.rebex.net", "demo", "password") as _client:
            _client.download_file("readme.txt", "/tmp/readme.txt")
    """

    def __init__(
        self,
        host: str,
        port: int = 22,
        user: Optional[str] = None,
        password: Optional[str] = None,
        private_key_path: str = "",
        passphrase: Optional[str] = None,
        transport_kwargs: Optional[Dict] = None,
        connection_kwargs: Optional[Dict] = None,
        disabled_algorithms: bool = False,
        algorithms_to_disable: Optional[List[str]] = None,
    ) -> None:
        """
        :param host: Host or IP of the remote machine.
        :param user: Username at the remote machine.
        :param password: Password at the remote machine.
        :param private_key_path: Path to private key file.
        :param passphrase: Passphrase to use along the private key.
        :param transport_kwargs: Named arguments for transport.
        :param connection_kwargs: Named arguments for connection.

        :param disabled_algorithms: If true, a list of algorithms will be disabled.
        :param algorithms_to_disable: Algorithms to disable.
        """

        self.host = host
        self.port = port
        self.user = user
        self.password = password
        self.private_key_path = private_key_path
        self.passphrase = passphrase

        self.connection_kwargs = connection_kwargs or {}
        self.transport_kwargs = transport_kwargs or {}
        self._sftp_client: Optional[SFTPClient] = None
        self._transport: Optional[Transport] = None

        # It's a bug in Paramiko. It does not handle correctly absence
        # of server-sig-algs extension on the server side...
        # https://stackoverflow.com/questions/70565357/paramiko-authentication-fails-with-agreed-upon-rsa-sha2-512-pubkey-algorithm
        if disabled_algorithms:
            self.transport_kwargs["disabled_algorithms"] = {
                "pubkeys": algorithms_to_disable or ["rsa-sha2-512", "rsa-sha2-256"]
            }

    @property
    def client(self) -> SFTPClient:
        """
        It provides access to the underline client to call methods that
        are not exposed via the wrapper...
        """

        if self._sftp_client is None:
            self.connect()

        return cast(SFTPClient, self._sftp_client)

    def _ensure_transport(self) -> Transport:
        if self._transport is None:
            self._transport = Transport(
                (self.host, self.port),  # type: ignore
                **self.transport_kwargs,
            )

        return self._transport

    def __enter__(self):
        self.connect()
        return self

    def connect(self):
        data: Dict[str, Any] = {
            "username": self.user,
            "password": self.password,
        }

        try:
            if self.private_key_path:
                data["pkey"] = RSAKey.from_private_key_file(
                    self.private_key_path,
                    self.passphrase,
                )

            _transport = self._ensure_transport()
            _transport.connect(**data, **self.connection_kwargs)
            self._sftp_client = SFTPClient.from_transport(_transport)
            return self

        except AuthenticationException as error:
            raise SftpClientError(f"Authentication error: {error}.")

        except BadHostKeyException as error:
            raise SftpClientError(f"HostKeys error: {error}.")

        except SSHException as error:
            raise SftpClientError(f"SSH error: {error}.")

        except NoValidConnectionsError as error:
            raise SftpClientError(f"Connection error: {error}")

        except Exception as error:
            raise SftpClientError(f"Error: {error}.")

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def close(self):
        self.client.close()
        self._ensure_transport().close()

    def get_cwd(self):
        """It returns the current working directory"""
        return self.client.getcwd()

    def chdir(self, remote_path: str):
        """It changes the current working directory"""
        self.client.chdir(remote_path)

    def list_files(self, remote_path) -> Iterator[Tuple[str, SFTPAttributes]]:
        """
        Read files under a remote directory...

        :param remote_path: Remote directory path.
        :return: Iterator of tuples in the form ("file_name", SFTPAttributes)
        """

        try:
            for attr in self.client.listdir_attr(remote_path):
                yield attr.filename, attr

        except IOError as error:
            raise SftpClientError(f"Error accessing directory: {error}")

    def download_file(self, remote_file_path, local_file_path):
        try:
            self.client.get(remote_file_path, local_file_path)
            return local_file_path

        except IOError as error:
            raise SftpClientError(f"Error downloading file: {error}")

    def upload_file(
        self,
        file_path: str,
        remote_path: str,
        callback: Optional[Callable[[int, int], Any]] = None,
        confirm: bool = False,
    ) -> SFTPAttributes:
        return self.client.put(
            file_path,
            remotepath=remote_path,
            callback=callback,
            confirm=confirm,
        )

    def upload_object(
        self,
        file_like: IO[Any],
        remote_path: str,
        file_size=0,
        callback: Optional[Callable[[int, int], Any]] = None,
        confirm: bool = False,
    ) -> SFTPAttributes:
        return self.client.putfo(
            file_like,
            remote_path,
            file_size=file_size,
            callback=callback,
            confirm=confirm,
        )

    def delete(self, remote_path: str, is_folder: bool = False):
        func = self.client.rmdir if is_folder else self.client.remove
        func(remote_path)


class SftpClientError(Exception):
    """Custom exception for SFTP Connection"""

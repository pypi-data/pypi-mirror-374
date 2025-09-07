# -*- coding: utf-8 -*-

from __future__ import annotations

from abc import ABC
from typing import Any, Iterator, Optional

from core_etl.file_based import IBaseEtlFromFile

from core_ftp.clients.sftp import SftpClient


class IBaseEtlFromFtpFile(IBaseEtlFromFile, ABC):
    """
    Base class for an ETL task that need to do something with a
    file retrieved from an FTP server...

    Example...

        docker run -v /home/alejandro/Documents:/home/foo/upload \
                   -p 22:22 \
                   -d atmoz/sftp foo:pass:::upload

        class SftpTask(IBaseEtlFromFtpFile):
            @classmethod def registered_name(cls) -> str:
                return "SftpTask"

        SftpTask(
            host="localhost", user="foo", password="pass",
            path="/upload", file_prefix="prefix", file_ext="csv",
            delete_file_on_success=True).execute()
    """

    def __init__(
        self,
        host: str,
        port: int = 22,
        user: Optional[str] = None,
        password: Optional[str] = None,
        path: Optional[str] = None,
        file_prefix: Optional[str] = None,
        file_ext: Optional[str] = None,
        delay_in_days: int = 1,
        monthly_basis: bool = False,
        private_key_path: str = "",
        delete_file_on_success: bool = False,
        **kwargs,
    ) -> None:
        """
        :param host: sFTP host.
        :param port: sFTP port.
        :param user: sFTP User.
        :param password: sFTP Password.
        :param private_key_path: Path to private key file.

        :param path: Reports folder path.
        :param file_prefix: Prefix for report files.
        :param file_ext: File extension.

        :param delete_file_on_success: If True, the files will be deleted once are processed.
        :param delay_in_days: Number of days before today to retrieve the file if applicable.
        :param monthly_basis: If True, the data should be collected each month.
        """

        super().__init__(**kwargs)

        self.host = host
        self.port = port

        self.user = user
        self.password = password
        self.private_key_path = private_key_path

        self.path = path
        self.delete_file_on_success = delete_file_on_success
        self.file_prefix = file_prefix
        self.file_ext = file_ext

        self.delay_in_days = delay_in_days
        self.monthly_basis = monthly_basis

        self.ftp_client = SftpClient(
            host=self.host,
            port=self.port,
            user=self.user,
            password=self.password,
            private_key_path=self.private_key_path,
            disabled_algorithms=True,
        )

    def pre_processing(self, **kwargs) -> None:
        super(IBaseEtlFromFtpFile, self).pre_processing(**kwargs)
        self.ftp_client.connect()

    def get_paths(self, last_processed: Any = None, *args, **kwargs) -> Iterator[str]:
        for file_name, attr in self.ftp_client.list_files(self.path):
            if not self.file_ext or file_name.endswith(self.file_ext):
                if not self.file_prefix or file_name.startswith(self.file_prefix):
                    yield file_name

    def process_file(self, path: str, *args, **kwargs):
        self.info(f"Processing remote file: {path}...")

    def on_success(self, path: str, **kwargs):
        if self.delete_file_on_success:
            self.ftp_client.client.remove(path)
            self.info(f'File "{path}" was deleted!')

    def clean_resources(self):
        self.ftp_client.close()

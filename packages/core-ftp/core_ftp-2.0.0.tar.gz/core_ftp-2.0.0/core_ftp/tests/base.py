# -*- coding: utf-8 -*-

import os
from unittest.mock import Mock
from unittest.mock import patch

from core_tests.tests.base import BaseTestCase
from paramiko.sftp_attr import SFTPAttributes


class BaseFtpTestCase(BaseTestCase):
    """Base class for Test Cases related to FTP connections"""

    init_transport_mock = None
    connect_transport_mock = None
    from_private_key_mock = None
    close_transport_mock = None
    from_transport_mock = None

    init_transport_patcher = patch("paramiko.transport.Transport.__init__")
    connect_transport_patcher = patch("paramiko.transport.Transport.connect")
    from_transport_patcher = patch("paramiko.sftp_client.SFTPClient.from_transport")
    from_private_key_patcher = patch("paramiko.pkey.PKey.from_private_key_file")
    close_transport_patcher = patch("paramiko.transport.Transport.close")

    _cwd = ""
    _root_path = ""

    @classmethod
    def setUpClass(cls) -> None:
        super(BaseFtpTestCase, cls).setUpClass()
        cls._root_path = os.getcwd()
        cls._cwd = ""

        cls.init_transport_mock = cls.init_transport_patcher.start()
        cls.connect_transport_mock = cls.connect_transport_patcher.start()
        cls.from_private_key_mock = cls.from_private_key_patcher.start()
        cls.close_transport_mock = cls.close_transport_patcher.start()
        cls.from_transport_mock = cls.from_transport_patcher.start()

        cls.init_transport_mock.return_value = None
        cls.from_transport_mock.return_value = cls.get_client_mock()

    @classmethod
    def tearDownClass(cls) -> None:
        super(BaseFtpTestCase, cls).tearDownClass()

        cls.init_transport_patcher.stop()
        cls.connect_transport_patcher.stop()
        cls.from_private_key_patcher.stop()
        cls.from_transport_patcher.stop()
        cls.close_transport_patcher.stop()

    @classmethod
    def get_client_mock(cls):
        client_mock = Mock()
        client_mock.listdir_attr.side_effect = cls.list_dir_attr
        client_mock.getcwd.side_effect = cls.get_cwd
        client_mock.chdir.side_effect = cls.chdir
        client_mock.get.side_effect = cls.get
        client_mock.put.side_effect = cls.put
        client_mock.putfo.side_effect = cls.put_fo
        client_mock.remove.side_effect = cls.remove
        return client_mock

    @classmethod
    def get_cwd(cls):
        return cls._cwd if cls._cwd else os.path.join(os.getcwd(), "tests/resources")

    @classmethod
    def chdir(cls, remote_path: str):
        cls._cwd = remote_path
        os.chdir(remote_path)

    @classmethod
    def list_dir_attr(cls, remote_path: str):
        for file_name in os.listdir(remote_path):
            attr = SFTPAttributes()
            attr.filename = file_name
            yield attr

    @staticmethod
    def get(remote_path: str, local_path: str, **kwargs):
        with open(local_path, "x") as f:
            f.write("This is a test!")

    @staticmethod
    def put(file_path, *args, **kwargs):
        """Implement if required"""

    @staticmethod
    def put_fo(file_like_object, remote_path, *args, **kwargs):
        """Implement if required"""

    @staticmethod
    def rmdir(path: str):
        """Implement if required"""

    @staticmethod
    def remove(path: str):
        """Implement if required"""

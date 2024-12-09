import tarfile
import tempfile
import unittest
from unittest.mock import patch, mock_open
import os
import json
from main import ShellEmulator

class TestShellEmulator(unittest.TestCase):
    def setUp(self):
        self.username = "test_user"

        # Create a temporary tar file
        self.tar_path = tempfile.NamedTemporaryFile(delete=False, suffix='.tar').name
        self.log_path = "test_log.json"

        # Create a sample TAR structure
        with tarfile.open(self.tar_path, 'w') as tar:
            # Create directories and files in the tar
            tarinfo = tarfile.TarInfo(name="root/")
            tarinfo.size = 0
            tar.addfile(tarinfo)

            tarinfo = tarfile.TarInfo(name="root/folder1/")
            tarinfo.size = 0
            tar.addfile(tarinfo)

            tarinfo = tarfile.TarInfo(name="root/folder1/file1.txt")
            tarinfo.size = 0
            tar.addfile(tarinfo)

            tarinfo = tarfile.TarInfo(name="root/folder2/")
            tarinfo.size = 0
            tar.addfile(tarinfo)

        # Create an empty log file
        with open(self.log_path, 'w') as log_file:
            json.dump([], log_file)

        # Initialize the ShellEmulator
        self.shell = ShellEmulator(self.username, self.tar_path, self.log_path)

    def tearDown(self):
        # Clean up the temporary tar file and log file if they were created
        if os.path.exists(self.tar_path):
            os.remove(self.tar_path)
        if os.path.exists(self.log_path):
            os.remove(self.log_path)

    def mock_tarfile_open(self, name, mode='r'):
        class MockTar:
            def __enter__(self):
                return self

            def __exit__(self, exc_type, exc_val, exc_tb):
                pass

            def getmembers(self):
                for path, content in self.sample_tar_structure.items():
                    yield tarfile.TarInfo(path)

        return MockTar()

    def test_ls_root(self):
        with patch("builtins.print") as mock_print:
            self.shell.ls()
            mock_print.assert_called_once_with("folder1 folder2")

    def test_cd_valid(self):
        self.shell.cd("folder1")
        self.assertEqual(self.shell.current_path, "/folder1")

    def test_cd_invalid(self):
        with patch("builtins.print") as mock_print:
            self.shell.cd("nonexistent")
            mock_print.assert_called_once_with("nonexistent: no such file or directory.")

    def test_mkdir_new(self):
        self.shell.mkdir("new_folder")
        self.assertIn("new_folder", self.shell.file_structure["root"])

    def test_mkdir_duplicate(self):
        self.shell.mkdir("folder1")
        with patch("builtins.print") as mock_print:
            self.shell.mkdir("folder1")
            mock_print.assert_called_once_with("Cannot create directory 'folder1': Directory exists")

    def test_history(self):
        self.shell.command_history.append("ls")
        self.shell.command_history.append("cd folder1")
        with patch("builtins.print") as mock_print:
            self.shell.history()
            mock_print.assert_any_call("1 ls")
            mock_print.assert_any_call("2 cd folder1")

    def test_exit(self):
        with self.assertRaises(SystemExit):
            self.shell.exit()

    def test_log_action(self):
        command = "ls"
        self.shell.edit_log(command)
        with open(self.log_path, 'r') as log_file:
            log_data = json.load(log_file)
        self.assertEqual(log_data[0]["command"], command)

if __name__ == "__main__":
    unittest.main()

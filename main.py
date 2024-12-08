import argparse
import os
import tarfile
import json
import datetime

def parse_args():
    parser = argparse.ArgumentParser(description="Shell-эмулятор")
    parser.add_argument("--username", required=True, help="Имя пользователя")
    parser.add_argument("--tar", required=True, help="Путь к tar-архиву с виртуальной файловой системой")
    parser.add_argument("--log", required=True, help="Путь к лог-файлу")

    return parser.parse_args()

class ShellEmulator:
    def __init__(self, username, tar_path, log_path):
        self.username = username
        self.tar_path = tar_path
        self.log_path = log_path
        self.current_path = '/'
        self.command_history = []
        self.file_structure = {}

        if not os.path.exists(tar_path):
            raise FileNotFoundError(f"{tar_path}: no such file or directory.")
        if not os.path.exists(log_path):
            raise FileNotFoundError(f"{log_path}: no such file or directory.")



if __name__ == "__main__":
    args = parse_args()


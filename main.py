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

        self.load_tar_file()
        self.initialize_log()

    #
    # тар-архив
    def load_tar_file(self):
        with tarfile.open(self.tar_path, 'r:*') as tar:
            for member in tar.getmembers():
                parts = member.name.split('/')
                current = self.file_structure
                for part in parts:
                    if part:
                        current = current.setdefault(part, {})

    #
    # лог-файл
    def initialize_log(self):
        with open(self.log_path, 'w') as log_file:
            json.dump([], log_file)

    def edit_log(self, command):
        timestamp = datetime.datetime.now().isoformat(sep=' ', timespec='seconds')
        entry = {
            "timestamp": timestamp,
            "user": self.username,
            "command": command
        }
        with open(self.log_path, 'r+') as log_file:
            log_data = json.load(log_file)
            log_data.append(entry)
            log_file.seek(0)
            json.dump(log_data, log_file, indent=4)

    #
    # путь
    def relative_to_absolute_path(self, path):
        if path.startswith('/'):
            resolved_path = path
        else:
            resolved_path = os.path.join(self.current_path, path)
        parts = [part for part in resolved_path.split('/')
                 if part and part != '.']
        stack = []
        for part in parts:
            if part == '..':
                if stack:
                    stack.pop()
            else:
                stack.append(part)
        return '/' + '/'.join(stack)

    #
    # команды
    def ls(self):
        current = self.file_structure
        for part in self.current_path.strip('/').split('/'):  # удалить конечный и начальный слэши + разделение
            if part:
                current = current.get(part, {})
        print(' '.join(current.keys()))

    def cd(self, path):
        new_path = self.relative_to_absolute_path(path)
        current = self.file_structure
        for part in new_path.strip('/').split('/'):
            if part:
                current = current.get(part)
                if current is None:
                    print(f"{path}: no such file or directory.")
                    return
        self.current_path = new_path

    def mkdir(self, name):
        current = self.file_structure
        for part in self.current_path.strip('/').split('/'):
            if part:
                current = current.get(part, {})
        if name in current:
            print(f"Cannot create directory '{name}': Directory exists")
        else:
            current[name] = {}

    def history(self):
        for index, command in enumerate(self.command_history, 1):
            print(f"{index} {command}")

    def exit(self):
        print("Exiting...")
        exit()

    #
    # запуск
    def run(self):
        while True:
            command = input(f"{self.username}@shell:~{self.current_path}$ ").strip()
            self.command_history.append(command)
            self.edit_log(command)

            if command.startswith('ls'):
                self.ls()
            elif command.startswith('cd '):
                _, path = command.split(' ', 1)
                self.cd(path)
            elif command.startswith('mkdir '):
                _, name = command.split(' ', 1)
                self.mkdir(name)
            elif command == 'history':
                self.history()
            elif command == 'exit':
                self.exit()
            else:
                print(f"{command}: command not found")

if __name__ == "__main__":
    args = parse_args()

    try:
        shell = ShellEmulator(args.username, args.tar, args.log)
        shell.run()
    except Exception as err:
        print(f"Error: {err}")
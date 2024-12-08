import argparse

def parse_args():
    parser = argparse.ArgumentParser(description="Shell-эмулятор")
    parser.add_argument("--username", required=True, help="Имя пользователя")
    parser.add_argument("--tar", required=True, help="Путь к tar-архиву с виртуальной файловой системой")
    parser.add_argument("--log", required=True, help="Путь к лог-файлу")

    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()


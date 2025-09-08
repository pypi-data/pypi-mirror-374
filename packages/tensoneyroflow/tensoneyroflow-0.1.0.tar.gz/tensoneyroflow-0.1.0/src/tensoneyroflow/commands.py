import os
from .core import get_file_type

class TensorNeuroFlowLoader:
    """Класс для загрузки и обработки данных"""
    
    @staticmethod
    def load_1_1():
        """Команда load.1-1"""
        print("""import os
import struct


def get_file_type(file_path):
    \"\"\"Определяет тип файла по сигнатуре\"\"\"
    signatures = {
        b"\\xff\\xd8\\xff": "JPEG",
        b"\\x89PNG\\r\\n\\x1a\\n": "PNG",
        b"BM": "BMP",
        b"GIF87a": "GIF87a",
        b"GIF89a": "GIF89a",
        b"II*\\x00": "TIFF",
        b"MM\\x00*": "TIFF",
        b"RIFF": "WEBP",
    }

    try:
        with open(file_path, "rb") as f:
            header = f.read(12)

        for sig, ftype in signatures.items():
            if header.startswith(sig):
                return ftype
        return "Unknown"
    except:
        return "Error\"""")

    @staticmethod
    def load_1_2():
        """Команда load.1-2"""
        print("""
# Фиксированный путь к папке
folder_path = r"C:\\Users\\chvt\\Desktop\\Chvt_2025\\dataset"

# Поддерживаемые расширения
extensions = {".jpg", ".jpeg", ".png", ".bmp", ".gif", ".tiff", ".webp"}

# Счетчик файлов
file_count = 0

# Рекурсивный обход всех папок и подпапок
for root, dirs, files in os.walk(folder_path):
    for filename in files:
        if os.path.splitext(filename)[1].lower() in extensions:
            file_path = os.path.join(root, filename)
            file_type = get_file_type(file_path)
            print(f"Файл: {filename}, Тип файла: {file_type}")
            file_count += 1

# Вывод общего количества файлов
print(f"\\nОбщее количество файлов: {file_count}\")""")

def load(command):
    """Основная функция загрузки"""
    if command == "1-1":
        TensorNeuroFlowLoader.load_1_1()
    elif command == "1-2":
        TensorNeuroFlowLoader.load_1_2()
    else:
        print(f"Неизвестная команда: {command}")
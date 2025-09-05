import os
import re


class lfcrlf:
    
    @staticmethod
    def __fileconvert(dir: str, point: str) -> None:
        try:
            with open(dir, "rb") as file:
                content = file.read()
            if point == "lf":
                content = re.sub(b'(?<!\r)\n', b'\r\n', content)
            elif point == "crlf":
                content = content.replace(b'\r\n', b'\n')

            with open(dir, "wb") as file:
                file.write(content)
                
        except Exception as e:
            print(f"Error processing file {dir}: {str(e)}")

    @staticmethod
    def __dir_recursion(dir_path: str, point: str) -> None:
        try:
            dirlist = os.listdir(dir_path)
        except PermissionError:
            print(f"No access to folder: {dir_path}")
            return
            
        for file in dirlist:
            full_path = os.path.join(dir_path, file)
            if os.path.isdir(full_path):
                lfcrlf.__dir_recursion(full_path, point)  # Исправлено
            else:
                if file.endswith(('.txt', '.py', '.html', '.css', 
                                '.js', '.json', '.xml', '.md')):
                    lfcrlf.__fileconvert(full_path, point)  # Исправлено

    @staticmethod
    def convert_dir(dir_path: str, point: str) -> None:
        lfcrlf.__dir_recursion(dir_path, point)

    @staticmethod
    def convert_file(file_path: str, point: str) -> None:
        lfcrlf.__fileconvert(file_path, point)
                
def convert_dir(dir_path: str, point: str) -> None:
    abs_path = os.path.abspath(dir_path)
    lfcrlf.convert_dir(abs_path, point)

def convert_file(file_path: str, point: str) -> None:
    abs_path = os.path.abspath(file_path)
    lfcrlf.convert_file(abs_path, point)
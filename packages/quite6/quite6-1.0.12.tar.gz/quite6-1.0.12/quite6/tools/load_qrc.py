import os
import subprocess
import sys
from pathlib import Path

import PySide6
import st


def find_executable_rcc(filename: str):
    paths = os.environ['PATH'].split(os.pathsep)
    paths.append(os.path.dirname(PySide6.__file__))
    paths.append(str(Path(PySide6.__file__).parents[2]))
    paths.append(os.path.join(os.path.dirname(PySide6.__file__)))
    for path in paths:
        pyside6_rcc_path = os.path.join(path, filename)
        if os.path.exists(pyside6_rcc_path) and os.access(pyside6_rcc_path, os.X_OK):
            return pyside6_rcc_path
    return None


if sys.platform == 'darwin':
    pyside6_path = os.path.dirname(sys.executable)
    rcc_path = os.path.join(pyside6_path, 'pyside6-rcc')
    if not os.path.exists(rcc_path):
        print(f'PySide6 Resource Compiler (pyside6-rcc) Not Found in platform {rcc_path}!')
elif sys.platform == 'win32':
    rcc_path = find_executable_rcc('pySide6-rcc.exe')
    if rcc_path is None:
        rcc_path = find_executable_rcc('PySide6-rcc.exe')
        if rcc_path is None:
            if not os.path.exists('pySide6-rcc.exe') and not os.path.exists('PySide6-rcc.exe'):
                raise FileNotFoundError('PySide6 Resource Compiler (PySide6-rcc.exe) Not Found!')
else:
    print(f"Unsupported platform {sys.platform} for pyside6-rcc")


@st.make_cache
def compile_qrc(filename):
    command = rcc_path + ' -g python ' + filename
    p = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
    (output, error) = p.communicate()
    p.wait()
    if p.returncode != 0:
        raise IOError(f'There was an error compiling the .qrc file {filename}: {error}')
    output = output.decode()
    return output


def load_qrc(filename):
    code = compile_qrc(filename)
    st.run(code)

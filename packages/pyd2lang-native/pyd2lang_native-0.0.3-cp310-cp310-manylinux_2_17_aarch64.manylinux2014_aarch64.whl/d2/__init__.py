"""Bindings for the D2 Compiler"""

import ctypes
import os
import platform

__version__ = "0.0.3"

loc = os.path.dirname(os.path.abspath(__file__))

if platform.system() == 'Windows':
    lib_path = os.path.join(loc, 'resources', 'd2lib.lib')
elif platform.system() == 'Linux':
    lib_path = os.path.join(loc, 'resources', 'd2lib.so')
else:
    lib_path = os.path.join(loc, 'resources', 'd2lib.dylib')

folder_path = os.path.join(loc, 'resources')

if not os.path.exists(lib_path):
    if platform.system() == 'Windows':
            # Try different extension
            lib_path = os.path.join(loc, 'resources', 'd2lib.dll')
    if not os.path.exists(lib_path):
        raise FileNotFoundError(f"Could not find {lib_path}")

library = ctypes.cdll.LoadLibrary(lib_path)

runme = library.runme
runme.argtypes = [ctypes.c_char_p]
runme.restype = ctypes.c_char_p

def compile(code: str) -> str:
    try:
        graph_bytes = runme(code.encode('utf-8'))
        return graph_bytes.decode('utf-8')
    except Exception as e:
        print(e)
        return None


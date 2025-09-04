import ctypes
import os
import sys

# Try multiple locations for the DLL
dll_locations = [
    os.path.join(os.path.dirname(__file__), "calculator.dll"),  # Same directory as this file
    os.path.join(os.path.dirname(os.path.abspath(__file__)), "calculator.dll"),  # Absolute path version
    os.path.join(sys.prefix, "Lib", "site-packages", "pycalgo", "calculator.dll"),  # site-packages/pycalgo
    "calculator.dll"  # Current working directory
]

lib = None
for dll_path in dll_locations:
    if os.path.exists(dll_path):
        try:
            lib = ctypes.CDLL(dll_path)
            break
        except OSError:
            continue

if lib is None:
    raise FileNotFoundError("calculator.dll not found in any expected location")

def add(a, b): return lib.Add(a, b)
def sub(a, b): return lib.Sub(a, b)
def mul(a, b): return lib.Mul(a, b)
def div(a, b): return lib.Div(a, b)
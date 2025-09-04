import ctypes, os, platform

# Detect correct library file based on OS
base = os.path.dirname(__file__)
system = platform.system()

if system == "Windows":
    libname = "calculator.dll"
elif system == "Linux":
    libname = "calculator.so"
elif system == "Darwin":  # macOS
    libname = "calculator.dylib"
else:
    raise RuntimeError(f"Unsupported OS: {system}")

dll_path = os.path.join(base, libname)
lib = ctypes.CDLL(dll_path)

# =========================
# Function signatures
# =========================

# Basic arithmetic
lib.Add.argtypes = [ctypes.c_int, ctypes.c_int]
lib.Add.restype = ctypes.c_int

lib.Sub.argtypes = [ctypes.c_int, ctypes.c_int]
lib.Sub.restype = ctypes.c_int

lib.Mul.argtypes = [ctypes.c_int, ctypes.c_int]
lib.Mul.restype = ctypes.c_int

lib.Div.argtypes = [ctypes.c_int, ctypes.c_int]
lib.Div.restype = ctypes.c_int

# Scientific
lib.Sqrt.argtypes = [ctypes.c_double]
lib.Sqrt.restype = ctypes.c_double

lib.Pow.argtypes = [ctypes.c_double, ctypes.c_double]
lib.Pow.restype = ctypes.c_double

lib.Sin.argtypes = [ctypes.c_double]
lib.Sin.restype = ctypes.c_double

lib.Cos.argtypes = [ctypes.c_double]
lib.Cos.restype = ctypes.c_double

lib.Tan.argtypes = [ctypes.c_double]
lib.Tan.restype = ctypes.c_double

lib.Log.argtypes = [ctypes.c_double]
lib.Log.restype = ctypes.c_double

# Unique fast ops
lib.FastBitCount.argtypes = [ctypes.c_uint64]
lib.FastBitCount.restype = ctypes.c_int

lib.FastFactorialMod.argtypes = [ctypes.c_int, ctypes.c_int]
lib.FastFactorialMod.restype = ctypes.c_int

lib.XorShiftRand.argtypes = [ctypes.POINTER(ctypes.c_uint64)]
lib.XorShiftRand.restype = ctypes.c_uint64

# =========================
# Python Wrappers
# =========================

def add(a, b): return lib.Add(a, b)
def sub(a, b): return lib.Sub(a, b)
def mul(a, b): return lib.Mul(a, b)
def div(a, b): return lib.Div(a, b)

def sqrt(a): return lib.Sqrt(float(a))
def pow(a, b): return lib.Pow(float(a), float(b))
def sin(a): return lib.Sin(float(a))
def cos(a): return lib.Cos(float(a))
def tan(a): return lib.Tan(float(a))
def log(a): return lib.Log(float(a))

def bitcount(a): return lib.FastBitCount(int(a))
def factmod(n, mod): return lib.FastFactorialMod(int(n), int(mod))

def xorshift(seed_val):
    seed = ctypes.c_uint64(seed_val)
    rnd = lib.XorShiftRand(ctypes.byref(seed))
    return rnd, seed.value  # returns (random_number, updated_seed)

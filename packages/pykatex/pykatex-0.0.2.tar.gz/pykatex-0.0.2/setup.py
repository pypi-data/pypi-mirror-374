from setuptools import setup, Extension
import sys


extra_compile_args = []
define_macros = [("CONFIG_VERSION", "\"2025-04-26\"")]

if sys.platform == "win32":
    extra_compile_args += ["/std:c11", "/experimental:c11atomics"]
    define_macros += [("WIN32_LEAN_AND_MEAN",)]
elif sys.platform == "linux":
    define_macros += [("_GNU_SOURCE", None)]


pykatex_ext = Extension(
    "pykatex",
    sources=[
        "src/pykatex.c",
        "src/katex.c", 
        "src/quickjs/quickjs-libc.c",
        "src/quickjs/quickjs.c",
        "src/quickjs/libregexp.c",
        "src/quickjs/libunicode.c",
        "src/quickjs/cutils.c",
        "src/quickjs/xsum.c"
    ],
    include_dirs=["src/quickjs"],
    define_macros=define_macros,
    extra_compile_args=extra_compile_args,
)

setup(
    ext_modules=[pykatex_ext]
)

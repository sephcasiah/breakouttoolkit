
#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Recursively (de)compile .py files into .pyc or .pyo (Python 2.7 specific).

Usage:
    Decompile:
        python de_compyler.py -d <src_dir> <dst_dir> [-v] [-s]

    Compile (default pyc):
        python de_compyler.py -c <src_dir> <dst_dir> [pyc|pyo] [-v] [-s]
"""
import sys
if sys.version_info[0] != 2 or sys.version_info[1] != 7:
    print("\n[ERROR] This tool must be run with Python 2.7\n")
    print("You are using: Python {}.{}".format(sys.version_info[0], sys.version_info[1]))
    print("Example usage:")
    print("    C:\\Python27\\python.exe de_compyler.py -c/-d <src_dir> <dst_dir> [pyc|pyo] [-v] [-s]")
    sys.exit(1)

import os
import sys
import shutil
import subprocess
import py_compile
import hashlib

UNCOMPYLE6_PATH = r"C:\Python27\Scripts\uncompyle6.exe"

def show_banner():
    print("""
============================================================
   DE / COMPYLER  —  Python 2.7 Bulk Tool
------------------------------------------------------------
Decompile .pyo/.pyc → .py  OR  Compile .py → .pyc/.pyo

Usage:
    Decompile:
        python de_compyler.py -d <src_dir> <dst_dir> [-v] [-s]

    Compile (.py → .pyc):
        python de_compyler.py -c <src_dir> <dst_dir> [-v] [-s]

    Compile optimized .pyo:
        python de_compyler.py -c <src_dir> <dst_dir> pyo [-v] [-s]

Options:
    -v   Verbose output (print every action)
    -s   Smart mode (skip unchanged files)

============================================================
""")


def md5(path):
    h = hashlib.md5()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            h.update(chunk)
    return h.hexdigest()

def same_file(src, dst):
    return os.path.exists(dst) and md5(src) == md5(dst)

def decompile_file(src_file, in_root, out_root, verbose, smart):
    rel = os.path.relpath(src_file, in_root)
    dst_dir = os.path.dirname(os.path.join(out_root, rel))
    dst_py = os.path.join(dst_dir, os.path.splitext(os.path.basename(src_file))[0] + ".py")

    if smart and os.path.exists(dst_py):
        if verbose: print("[SKIP] (unchanged) {}".format(src_file))
        return

    if not os.path.exists(dst_dir):
        os.makedirs(dst_dir)

    try:
        subprocess.call([UNCOMPYLE6_PATH, "-o", dst_dir, src_file],
                        stdout=open(os.devnull, "w"), stderr=subprocess.STDOUT)

        if verbose:
            print("[OK] Decompiled → {}".format(dst_py))
        else:
            print("[OK]", src_file)

    except Exception as e:
        print("[ERR] {} : {}".format(src_file, e))


def run_decompile(src_root, dst_root, verbose, smart):
    if os.path.exists(dst_root):
        wipe = raw_input("Output folder exists. Wipe it first? (y/N): ").strip().lower()
        if wipe == "y":
            shutil.rmtree(dst_root)

    if not os.path.exists(dst_root):
        os.makedirs(dst_root)

    count = 0

    for root, _, files in os.walk(src_root):
        for f in files:
            if f.endswith(".pyo") or f.endswith(".pyc"):
                count += 1
                decompile_file(os.path.join(root, f), src_root, dst_root, verbose, smart)

    print("\n✓ Done. Decompiled {} files.\nSaved to: {}\n".format(count, dst_root))

def compile_all(src_root, dst_root, mode, verbose, smart):
    count = 0

    for root, _, files in os.walk(src_root):
        rel = os.path.relpath(root, src_root)
        out_dir = os.path.join(dst_root, rel)

        if not os.path.exists(out_dir):
            os.makedirs(out_dir)

        for f in files:
            if not f.endswith(".py"):
                continue

            src_file = os.path.join(root, f)
            dst_file = os.path.join(out_dir, f[:-3] + "." + mode)

            if smart and same_file(src_file, dst_file):
                if verbose: print("[SKIP] (unchanged) {}".format(src_file))
                continue

            try:
                if mode == "pyo":
                    subprocess.check_call([sys.executable, "-O", "-m", "py_compile", src_file])
                    built = src_file + "o"
                    if os.path.exists(built):
                        if os.path.exists(dst_file): os.remove(dst_file)
                        os.rename(built, dst_file)
                else:
                    py_compile.compile(src_file, cfile=dst_file, doraise=True)

                count += 1
                if verbose:
                    print("[OK] {} → {}".format(src_file, dst_file))
                else:
                    print("[OK]", dst_file)

            except Exception as e:
                print("[ERR] {} -> {}".format(src_file, e))

    print("\n✓ Done. Compiled {} .{} files.\nSaved to: {}\n".format(count, mode, dst_root))

def main():
    args = sys.argv[1:]

    if len(args) == 0 or "-h" in args or "--help" in args:
        show_banner()
        sys.exit(0)
        
    if len(args) < 3:
        show_banner()
        print(__doc__)
        sys.exit(1)

    verbose = "-v" in args
    smart = "-s" in args

    args = [a for a in args if a not in ("-v", "-s")]

    mode_flag = args[0].lower()

    src = os.path.abspath(args[1])
    dst = os.path.abspath(args[2])

    if mode_flag == "-d":
        run_decompile(src, dst, verbose, smart)

    elif mode_flag == "-c":
        mode = args[3].lower() if len(args) > 3 else "pyc"
        if mode not in ("pyc", "pyo"):
            print("Invalid mode. Use pyc or pyo.")
            sys.exit(1)
        compile_all(src, dst, mode, verbose, smart)

    else:
        print("Unknown option:", mode_flag)
        print(__doc__)


if __name__ == "__main__":
    main()

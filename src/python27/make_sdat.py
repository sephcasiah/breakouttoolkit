#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Pack the contents of a {filename} folder directly into {filename}.SDAT,
Storage Only!

Usage:
    python make_sdat.py /path/to/FOLDER /path/to/FOLDER.SDAT
"""

import os, sys, zipfile

def make_sdat(src_dir, output_file):
    src_dir = os.path.abspath(src_dir)

    with zipfile.ZipFile(output_file, 'w', zipfile.ZIP_STORED) as z:
        for root, dirs, files in os.walk(src_dir):
            for f in files:
                file_path = os.path.join(root, f)
                arcname = os.path.relpath(file_path, src_dir)
                arcname = arcname.replace("\\", "/")
                z.write(file_path, arcname)
                print("Added:", arcname)
    print("\nCreated:", output_file)

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python make_sdat.py <FOLDER_folder> <FOLDER.SDAT>")
        sys.exit(1)

    src = sys.argv[1]
    dst = sys.argv[2]
    make_sdat(src, dst)

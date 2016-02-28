#!/usr/bin/env python3

"""
patternScan.py
    application of pattern.py to a set of .sp files
"""

import pattern
import os
import sys
import multiprocessing
import argparse

script_dir_path = os.path.join(os.path.realpath(__file__),"..")
minter_root = os.path.abspath(os.path.join(script_dir_path, "../../../.."))

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("target", help= "Directory containing all files", default = "input/pattern/")
    parser.add_argument("-o", "--output", help= "Directory to output data to", default = os.path.join(minter_root, "output/pattern/"))
    parser.add_argument("-c", "--cores", help= "Number of cores to use (default 4)", type = int, default = 4)
    args = parser.parse_args()

    outDir = args.output
    if not os.path.exists(outDir):
        os.makedirs(outDir)

    target = args.target
    cores = args.cores
    files = [os.path.join(target, i) for i in os.listdir(target) ]
    files = filter(os.path.isfile, files)
    files = [(i, outDir) for i in files]
    print(files)
    with multiprocessing.Pool(cores) as pool:
       pool.starmap(pattern.execute, files)

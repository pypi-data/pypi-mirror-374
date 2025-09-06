#!/usr/bin/python
# -*- coding: UTF-8 -*-
import sys, os, re, glob, json, time
import argparse

try:
    from arnold import *
except:
    print('no arnold Plugin!')
    pass

scriptPath = os.path.dirname(os.sys.argv[0]).replace("\\", "/")
sys.path.append(scriptPath)

sys_name = "windows" if sys.platform.startswith('win') else "linux"
sys.path.append(os.path.join(scriptPath, sys_name))
if sys.version[0] == "2":
    import script

if sys.version[:3] == "3.7":
    import script37 as script

if sys.version[:3] == "3.9":
    import script39 as script

parser = argparse.ArgumentParser()
parser.add_argument("-task", help='task id', type=str)
parser.add_argument('-file', help='file path', type=str)
args = parser.parse_args()
print(args)

# global  var
file = args.file
task = args.task

script.main(file, task)
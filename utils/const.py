import copy
import datetime
import inspect
import getpass  # For the username running the program
import math
import multiprocessing
import matplotlib as mpl
# mpl.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import networkx as nx
import os
import operator
import pandas as pd
import pickle
import platform  # For the name of host machine
import pybnb
import random
import scipy.stats as st
import scipy.sparse as sp
import subprocess
import sys
import time
import traceback

from argparse import ArgumentParser
from collections import defaultdict
from functools import reduce
from operator import add
from ortools.linear_solver import pywraplp
from pysat.formula import WCNF
from tqdm import tqdm
try:
    from pysat.examples.rc2 import RC2
except ImportError:
    print("from pysat.examples.rc2 import RC2 didn't run successfully. CSP based methods will not work.")

try:
    from gurobipy import *
except ImportError:
    print("from gurobipy import * didn't run successfully. LP based methods will not work.")





# This line is here to make sure the line "Academic license - for non-commercial use only" prints at the top
try:
    gurobi_env = Env()
except GurobiError:
    print("Gurubi License is not working properly. LP based methods will not work")

# gurobi_env = Env()
# For users and platforms
user_name = getpass.getuser()
platform_name = platform.node()
# End of all users

print(f"Running on {user_name}@{platform_name}")

if user_name == "esadeqia":
    openwbo_path = "/home/esadeqia/external/openwbo"
    ms_path = "/home/esadeqia/external/ms"
    output_folder_path = "/home/esadeqia/PhISCS_BnB/Reports/Erfan"
    solutions_folder_path = "/home/esadeqia/PhISCS_BnB/Solutions"
    data_folder_path = "/home/esadeqia/PhISCS_BnB/Data"
    if "Carbonate" in os.getcwd():
        openwbo_path = "/gpfs/home/e/s/esadeqia/Carbonate/external/openwbo"
        ms_path = "/gpfs/home/e/s/esadeqia/Carbonate/external/ms"
        output_folder_path = "/gpfs/home/e/s/esadeqia/Carbonate/Phylogeny_BnB/Reports/Erfan"
        data_folder_path = "/gpfs/home/e/s/esadeqia/Carbonate/Phylogeny_BnB/Data"

    simulation_folder_path = data_folder_path + "/simulations/"
    noisy_folder_path = data_folder_path + "/noisy/"
elif user_name == "school":
    openwbo_path = None
    ms_path = None
    output_folder_path = "./reports/Erfan"
elif user_name == "frashidi":
    openwbo_path = "./Archived/Farid/archived/openwbo"
    ms_path = "./Archived/Farid/archived/ms"
    output_folder_path = "./reports"
    simulation_folder_path = "./simulations"
    noisy_folder_path = "./Data/noisy/"
else:
    print("User const not found!")
    exit(0)

import numpy as np
from utils import *
import networkx as nx
import subprocess
from collections import defaultdict

def lb_csp(D, changed_column, previous_G):
    if changed_column == None:
        G = nx.Graph()
    else:
        G = previous_G

    def calc_min0110_for_one_pair_of_columns(p, q, G):
        foundOneOne = False
        numberOfZeroOne = 0
        numberOfOneZero = 0
        for r in range(D.shape[0]):
            if D[r,p] == 1 and D[r,q] == 1:
                foundOneOne = True
            if D[r,p] == 0 and D[r,q] == 1:
                numberOfZeroOne += 1
            if D[r,p] == 1 and D[r,q] == 0:
                numberOfOneZero += 1
        if foundOneOne:
            G.add_edge(p, q, weight=min(numberOfZeroOne, numberOfOneZero))
        else:
            G.add_edge(p, q, weight=0)

    if changed_column == None:
        for p in range(D.shape[1]):
            for q in range(p + 1, D.shape[1]):
                calc_min0110_for_one_pair_of_columns(p, q, G)
    else:
        q = changed_column
        for p in range(D.shape[1]):
            if p < q:
                calc_min0110_for_one_pair_of_columns(p, q, G)
            elif q < p:
                calc_min0110_for_one_pair_of_columns(q, p, G)

    G = nx.Graph()
    G.add_edge(1,2,weight=3)
    print(G[5][2]["weight"])
    # best_pairing = nx.max_weight_matching(G)
    csp_solver_path = '/home/frashidi/software/temp/csp_solvers/maxino/code/build/release/maxino'
    outfile = '/data/frashidi/Phylogeny_BnB/cnf.tmp'
    command = '{} {}'.format(csp_solver_path, outfile)
    proc = subprocess.Popen(command.split(), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    output, error = proc.communicate()
    for i in range(D.shape[1]):
        for j in range(i, D.shape[1]):
            G[i][j]
        

    variables = output.decode().split('\n')[-2][2:-1].split(' ')
    print(variables)
    
    print(best_pairing)
    best_pair_qp, best_pair_w = (None, None), 0
    lb = 0
    # for a, b in best_pairing:
    #     if G[a][b]["weight"] > best_pair_w:
    #         best_pair_w = G[a][b]["weight"]
    #         best_pair_qp = (a, b)
    #     lb += G[a][b]["weight"]
    return lb, G, best_pair_qp


def lb_greedy(D, a, b):
    def get_important_pair_of_columns_in_conflict(D):
        important_columns = defaultdict(lambda: 0)
        for p in range(D.shape[1]):
            for q in range(p + 1, D.shape[1]):
                oneone = 0
                zeroone = 0
                onezero = 0
                for r in range(D.shape[0]):
                    if D[r,p] == 1 and D[r,q] == 1:
                        oneone += 1
                    if D[r,p] == 0 and D[r,q] == 1:
                        zeroone += 1
                    if D[r,p] == 1 and D[r,q] == 0:
                        onezero += 1
                ## greedy approach based on the number of conflicts in a pair of columns
                # if oneone*zeroone*onezero > 0:
                #     important_columns[(p,q)] += oneone*zeroone*onezero
                ## greedy approach based on the min number of 01 or 10 in a pair of columns
                if oneone > 0:
                    important_columns[(p,q)] += min(zeroone, onezero)
        return important_columns
    
    ipofic = get_important_pair_of_columns_in_conflict(D)
    sorted_ipofic = sorted(ipofic.items(), key=operator.itemgetter(1), reverse=True)
    pairs = [sorted_ipofic[0][0]]
    elements = [sorted_ipofic[0][0][0], sorted_ipofic[0][0][1]]
    sorted_ipofic.remove(sorted_ipofic[0])
    for x in sorted_ipofic[:]:
        notFound = True
        for y in x[0]:
            if y in elements:
                sorted_ipofic.remove(x)
                notFound = False
                break
        if notFound:
            pairs.append(x[0])
            elements.append(x[0][0])
            elements.append(x[0][1])
    lb = 0
    for x in pairs:
        lb += ipofic[x]
    
    icf, best_pair_qp = is_conflict_free_gusfield_and_get_two_columns_in_coflicts(D)
    return lb, {}, best_pair_qp
    

def lb_random(D, a, b):
    def get_partition_random(D):
        d = int(D.shape[1]/2)
        partitions_id = np.random.choice(range(D.shape[1]), size=(d, 2), replace=False)
        return partitions_id
    
    def calc_min0110_for_one_pair_of_columns(D, p, q):
        foundOneOne = False
        numberOfZeroOne = 0
        numberOfOneZero = 0
        for r in range(D.shape[0]):
            if D[r,p] == 1 and D[r,q] == 1:
                foundOneOne = True
            if D[r,p] == 0 and D[r,q] == 1:
                numberOfZeroOne += 1
            if D[r,p] == 1 and D[r,q] == 0:
                numberOfOneZero += 1
        if foundOneOne:
            return min(numberOfZeroOne, numberOfOneZero)
        else:
            return 0

    lb = 0
    for x in get_partition_random(D):
        lb += calc_min0110_for_one_pair_of_columns(D, x[0], x[1])
    
    icf, best_pair_qp = is_conflict_free_gusfield_and_get_two_columns_in_coflicts(D)
    return lb, {}, best_pair_qp


def lb_gurobi(D, a, b):
    solution, (flips_0_1, flips_1_0, flips_2_0, flips_2_1), c_time = PhISCS_I(D, beta=0.9, alpha=0.00000001)
    icf, best_pair_qp = is_conflict_free_gusfield_and_get_two_columns_in_coflicts(D)
    return flips_0_1, {}, best_pair_qp


def lb_max_weight_matching(D, changed_column, previous_G):
    if changed_column == None:
        G = nx.Graph()
    else:
        G = previous_G

    def calc_min0110_for_one_pair_of_columns(p, q, G):
        foundOneOne = False
        numberOfZeroOne = 0
        numberOfOneZero = 0
        for r in range(D.shape[0]):
            if D[r,p] == 1 and D[r,q] == 1:
                foundOneOne = True
            if D[r,p] == 0 and D[r,q] == 1:
                numberOfZeroOne += 1
            if D[r,p] == 1 and D[r,q] == 0:
                numberOfOneZero += 1
        if foundOneOne:
            G.add_edge(p, q, weight=min(numberOfZeroOne, numberOfOneZero))
        else:
            G.add_edge(p, q, weight=0)

    if changed_column == None:
        for p in range(D.shape[1]):
            for q in range(p + 1, D.shape[1]):
                calc_min0110_for_one_pair_of_columns(p, q, G)
    else:
        q = changed_column
        for p in range(D.shape[1]):
            if p < q:
                calc_min0110_for_one_pair_of_columns(p, q, G)
            elif q < p:
                calc_min0110_for_one_pair_of_columns(q, p, G)

    best_pairing = nx.max_weight_matching(G)
    # print(best_pairing)
    best_pair_qp, best_pair_w = (None, None), 0
    # for (u, v, wt) in G.edges.data('weight'):
    #     if wt > best_pair_w:
    #         best_pair_qp = (u, v)
    #         best_pair_w = wt
        # print(u, v, wt)
    lb = 0
    # best_pair_qp, best_pair_w = (None, None), 0
    for a, b in best_pairing:
        # print(a,b,G[a][b]["weight"])
        if G[a][b]["weight"] > best_pair_w:
            best_pair_w = G[a][b]["weight"]
            best_pair_qp = (a, b)
        lb += G[a][b]["weight"]
    return lb, G, best_pair_qp
from utils.const import *
from utils.interfaces import *
from utils.instances import *
from algorithms.simple import simple_alg

class RandomPartitioning(BoundingAlgAbstract):
    def __init__(self, ascending_order=False, na_value=None, priority_version=-2, pass_info=False, make_ub=False):
        """
        :param ratio:
        :param ascending_order: if True the column pair with max weight is chosen in extra info
        """
        super().__init__()
        self.ascending_order = ascending_order
        self.na_value = na_value
        self.dist = None  # an m x m matrix d_ij = cost of i,j column pair
        self.priority_version = priority_version
        self.pass_info = pass_info
        self.make_ub=False


    def get_name(self):
        params = [type(self).__name__,
                  self.ascending_order,
                  self.na_value,
                  self.priority_version,
                  self.pass_info,
                  self.make_ub
                  ]
        params_str = map(str, params)
        return "_".join(params_str)

    def get_extra_info(self):
        return None
        # return self._extra_info

    def reset(self, matrix):
        assert self.na_value is None, "N/A is not implemented yet"
        self.matrix = matrix
        self.dist = np.zeros(tuple([matrix.shape[1]] * 2), dtype=np.int)
        for i in range(self.dist.shape[0]):
            for j in range(i):
                self.dist[i, j] = self.cost_of_col_pair(i, j, self.matrix)
                self.dist[j, i] = self.dist[i, j]
        self._times = {"model_preparation_time": 0, "optimization_time": 0}


    def get_init_node(self):
        return None
        node = pybnb.Node()
        icf, solution = simple_alg(self.matrix, mx_iter = 500)

        nodedelta = sp.lil_matrix(np.logical_and(solution == 1, self.matrix == 0))
        node_na_delta = sp.lil_matrix(np.logical_and(solution == 1, self.matrix == self.na_value))
        node.state = (nodedelta, icf, None, nodedelta.count_nonzero(), self.get_state(), node_na_delta)
        node.queue_priority = 100000
        return node

    def get_bound(self, delta, na_delta=None):
        self._extra_info = None

        current_matrix = self.matrix + delta
        flips_mat = np.transpose(delta.nonzero())
        flipped_cols_set = set(flips_mat[:, 1])

        d = int(self.matrix.shape[1] / 2)
        partitions_id = np.random.choice(range(self.matrix.shape[1]), size=(d, 2), replace=False)
        lb = 0
        sign = 1 if self.ascending_order else -1

        opt_pair_value = delta.shape[0] * delta.shape[1] * (-sign)  # either + inf or - inf
        opt_pair = None

        for partition in partitions_id:
            cost_of_x = None
            if partition[0] not in flipped_cols_set and partition[1] not in flipped_cols_set:
                cost_of_x = self.dist[partition[0], partition[1]]
            else:
                cost_of_x = RandomPartitioning.cost_of_col_pair(partition[0], partition[1], current_matrix)
            lb += cost_of_x
            if cost_of_x * sign > opt_pair_value * sign and cost_of_x > 0:
                opt_pair_value = cost_of_x
                opt_pair = partition
        if lb > 0 and True:
            self._extra_info = {"icf": False, "one_pair_of_columns": (opt_pair[0], opt_pair[1])}
        return lb + flips_mat.shape[0]

    @staticmethod
    def cost_of_col_pair(p, q, mat):
        found_one_one = False
        number_of_zero_one = 0
        number_of_one_zero = 0
        for r in range(mat.shape[0]):
            if mat[r, p] == 1 and mat[r, q] == 1:
                found_one_one = True
            if mat[r, p] == 0 and mat[r, q] == 1:
                number_of_zero_one += 1
            if mat[r, p] == 1 and mat[r, q] == 0:
                number_of_one_zero += 1
        if found_one_one:
            if number_of_zero_one * number_of_one_zero > 0:
                return min(number_of_zero_one, number_of_one_zero)
        return 0


class DynamicMWMBounding(BoundingAlgAbstract):
    def __init__(self, ascending_order=False, na_value=None, priority_version=-2, pass_info=False, make_ub=False):
        """
        :param ratio:
        :param ascending_order: if True the column pair with max weight is chosen in extra info
        """
        super().__init__()
        self.matrix = None
        self.G = None
        self._extra_info = {}
        self.ascending_order = ascending_order
        self.na_value = na_value
        self.priority_version = priority_version
        self.pass_info = pass_info
        self.make_ub=False

    def get_name(self):
        params = [type(self).__name__,
                  self.ascending_order,
                  self.na_value,
                  self.priority_version,
                  self.pass_info,
                  self.make_ub
                  ]
        params_str = map(str, params)
        return "_".join(params_str)

    def reset(self, matrix):
        self.matrix = matrix
        self.G = nx.Graph()
        for p in range(self.matrix.shape[1]):
            for q in range(p + 1, self.matrix.shape[1]):
                self.calc_min0110_for_one_pair_of_columns(p, q, self.matrix)
        self._times = {"model_preparation_time": 0, "optimization_time": 0}

    def get_init_node(self):
        if not self.make_ub:
            return None
        node = pybnb.Node()
        icf, solution = simple_alg(self.matrix, mx_iter = 500)

        nodedelta = sp.lil_matrix(np.logical_and(solution == 1, self.matrix == 0))
        node_na_delta = sp.lil_matrix(np.logical_and(solution == 1, self.matrix == self.na_value))
        node.state = (nodedelta, icf, None, nodedelta.count_nonzero(), self.get_state(), node_na_delta)
        print("-----------", nodedelta.count_nonzero())
        node.queue_priority = 100000
        return node

    def get_extra_info(self):
        if self.pass_info:
            return self._extra_info
        else:
            return None

    def calc_min0110_for_one_pair_of_columns(self, p, q, current_matrix):
        found_one_one = False
        number_of_zero_one = 0
        number_of_one_zero = 0
        for r in range(current_matrix.shape[0]):
            if current_matrix[r, p] == 1 and current_matrix[r, q] == 1:
                found_one_one = True
            if current_matrix[r, p] == 0 and current_matrix[r, q] == 1:
                number_of_zero_one += 1
            if current_matrix[r, p] == 1 and current_matrix[r, q] == 0:
                number_of_one_zero += 1
        if self.G.has_edge(p, q):
            self.G.remove_edge(p, q)
        if found_one_one:
            self.G.add_edge(p, q, weight=min(number_of_zero_one, number_of_one_zero))

    def get_bound(self, delta, na_delta=None):
        self_extraInfo = None

        current_matrix = self.matrix + delta
        old_g = copy.deepcopy(self.G)
        flips_mat = np.transpose(delta.nonzero())
        flipped_cols_set = set(flips_mat[:, 1])
        for q in flipped_cols_set:  # q is a changed column
            for p in range(self.matrix.shape[1]):
                if p < q:
                    self.calc_min0110_for_one_pair_of_columns(p, q, current_matrix)
                elif q < p:
                    self.calc_min0110_for_one_pair_of_columns(q, p, current_matrix)

        best_pairing = nx.max_weight_matching(self.G)

        sign = 1 if self.ascending_order else -1

        opt_pair_value = delta.shape[0] * delta.shape[1] * (-sign)  # either + inf or - inf
        opt_pair = None
        lb = 0
        for a, b in best_pairing:
            lb += self.G[a][b]["weight"]
            if self.G[a][b]["weight"] * sign > opt_pair_value * sign and self.G[a][b]["weight"] > 0:
                opt_pair_value = self.G[a][b]["weight"]
                opt_pair = (a, b)
        self.G = old_g
        self._extra_info = {"icf": (lb == 0), "one_pair_of_columns": opt_pair if lb > 0 else None}
        return lb + flips_mat.shape[0]

    def get_priority(self, till_here, this_step, after_here, icf=False):
        if icf:
            return self.matrix.shape[0] * self.matrix.shape[1] + 10
        else:
            sgn = np.sign(self.priority_version)
            pv_abs = self.priority_version * sgn
            if pv_abs == 1:
                return sgn * (till_here + this_step + after_here)
            elif pv_abs == 2:
                return sgn * (this_step + after_here)
            elif pv_abs == 3:
                return sgn * (after_here)
            elif pv_abs == 4:
                return sgn * (till_here + after_here)
            elif pv_abs == 5:
                return sgn * (till_here)
            elif pv_abs == 6:
                return sgn * (till_here + this_step)
            elif pv_abs == 7:
                return 0
        assert False, "get_priority did not return anything!"

# todo remove these in a few weeks if not needed

# class StaticMWMBounding(BoundingAlgAbstract):
#     def __init__(self, ratio=None, ascending_order=False):
#         """
#         :param ratio:
#         :param ascending_order: if True the column pair with max weight is chosen in extra info
#         """
#         super().__init__()
#         self.ratio = ratio
#         self.matrix = None
#         self.ascending_order = ascending_order
#         self._extra_info = {}
#         self.G = None
#
#     def get_name(self):
#         return type(self).__name__ + f"_{self.ratio}_{self.ascending_order}"
#
#     def reset(self, matrix):
#         self.matrix = matrix
#
#     def get_extra_info(self):
#         return self._extra_info
#
#     def get_bound(self, delta):
#         self._extra_info = None
#         n_flips = delta.count_nonzero()
#         current_matrix = self.matrix + delta
#         self.G = nx.Graph()
#         for p in range(current_matrix.shape[1]):
#             for q in range(p + 1, current_matrix.shape[1]):
#                 self.calc_min0110_for_one_pair_of_columns(p, q, current_matrix)
#         best_pairing = nx.max_weight_matching(self.G)
#
#         sign = 1 if self.ascending_order else -1
#
#         opt_pair_value = delta.shape[0] * delta.shape[1] * (-sign)  # either + inf or - inf
#         opt_pair = None
#         lb = 0
#         for a, b in best_pairing:
#             lb += self.G[a][b]["weight"]
#             if self.G[a][b]["weight"] * sign > opt_pair_value * sign and self.G[a][b]["weight"] > 0:
#                 opt_pair_value = self.G[a][b]["weight"]
#                 opt_pair = (a, b)
#
#         self._extra_info = {"icf": (lb == 0), "one_pair_of_columns": opt_pair if lb > 0 else None}
#
#         if self.ratio is None:
#             return_value = lb + n_flips
#         else:
#             return_value = np.int(np.ceil(self.ratio * lb)) + n_flips
#         return return_value
#
#     def calc_min0110_for_one_pair_of_columns(self, p, q, current_matrix):
#         found_one_one = False
#         number_of_zero_one = 0
#         number_of_one_zero = 0
#         for r in range(current_matrix.shape[0]):
#             if current_matrix[r, p] == 1 and current_matrix[r, q] == 1:
#                 found_one_one = True
#             if current_matrix[r, p] == 0 and current_matrix[r, q] == 1:
#                 number_of_zero_one += 1
#             if current_matrix[r, p] == 1 and current_matrix[r, q] == 0:
#                 number_of_one_zero += 1
#         if self.G.has_edge(p, q):
#             self.G.remove_edge(p, q)
#         if found_one_one:
#             self.G.add_edge(p, q, weight=min(number_of_zero_one, number_of_one_zero))


if __name__ == "__main__":
    n, m = 10, 5
    x = np.random.randint(2, size=(n, m))
    delta = sp.lil_matrix((n, m))

    # x = np.array([[0, 1, 1, 1, 1, 1],
    #        [1, 0, 1, 1, 0, 1],
    #        [1, 0, 1, 1, 0, 1],
    #        [0, 0, 0, 0, 1, 1],
    #        [0, 0, 0, 0, 1, 1],
    #        [1, 0, 1, 1, 0, 0],
    #        [0, 0, 0, 0, 1, 0],
    #        [1, 1, 1, 0, 0, 1]])
    # delta = sp.lil_matrix([[0, 0, 0, 0, 0, 0],
    #         [0, 1, 0, 0, 0, 0],
    #         [0, 1, 0, 0, 0, 0],
    #         [0, 1, 1, 1, 0, 0],
    #         [0, 1, 1, 1, 0, 0],
    #         [0, 1, 0, 0, 0, 1],
    #         [0, 0, 0, 1, 0, 0],
    #         [0, 0, 0, 0, 0, 0]], dtype=np.int8)

    algs = [
        # StaticMWMBounding(),
        DynamicMWMBounding(ascending_order=False),
        DynamicMWMBounding(ascending_order=True),
        RandomPartitioning(ascending_order=False),
        RandomPartitioning(ascending_order=True),
    ]
    # print("optimal:", myPhISCS_B(np.array(x + delta)))
    for algo in algs:
        resetTime = time.time()
        algo.reset(x)
        resetTime = time.time() - resetTime
        print(algo.get_name(), algo.get_bound(delta), resetTime)

    for t in range(3):
        ind = np.nonzero(1 - (x + delta))
        if ind[0].shape[0] == 0:
            print("DONE!")
            break
        a, b = ind[0][0], ind[1][0]
        delta[a, b] = 1
        print("t =", t)
        for algo in algs:
            print(algo.get_name(), algo.get_bound(delta), algo.get_extra_info())


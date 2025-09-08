from .utils import generate_all_permutations, run_permutation, run_permutation_hardcoded
from matmulbench.common.timing import start_timer, end_timer
from matmulbench.common import response_format

def benchmark(N=32):
    my_list = [1, 2, 3]
    all_perms = generate_all_permutations(my_list)
    # print(all_perms) -> [(1, 2, 3), (1, 3, 2), (2, 1, 3), (2, 3, 1), (3, 1, 2), (3, 2, 1)]
    info = []
    for permutation in all_perms:
        start_timer()
        run_permutation(permutation=permutation, M=N, N=N, K=N)
        timing = end_timer()
        print(permutation, timing, sep= " ")
        info.append(response_format(permutation, timing))
    return info

def benchmark_hardcoded(N=32):
    my_list = ['i', 'j', 'k']
    all_perms = generate_all_permutations(my_list)
    print(all_perms) #-> [(1, 2, 3), (1, 3, 2), (2, 1, 3), (2, 3, 1), (3, 1, 2), (3, 2, 1)]
    info = []
    for permutation in all_perms:
        start_timer()
        run_permutation_hardcoded(permutation=permutation, M=N, N=N, K=N)
        timing = end_timer()
        print(permutation, timing, sep= " ")
        info.append(response_format(permutation, timing))
    return info
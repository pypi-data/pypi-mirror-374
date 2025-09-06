from .utils import generate_all_permutations, run_permutation

def benchmark(N=32):
    my_list = [1, 2, 3]
    all_perms = generate_all_permutations(my_list)
    # print(all_perms) -> [(1, 2, 3), (1, 3, 2), (2, 1, 3), (2, 3, 1), (3, 1, 2), (3, 2, 1)]

    for permutation in all_perms:
        run_permutation(permutation=permutation, M=N, N=N, K=N)
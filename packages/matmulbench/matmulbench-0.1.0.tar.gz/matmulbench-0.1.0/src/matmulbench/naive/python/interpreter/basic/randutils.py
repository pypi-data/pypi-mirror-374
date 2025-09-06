import numpy as npy

def get_matrices(M, N, K):
    shapes = [(M,K), (M,N)]
    A = npy.random.rand(*shapes[0])
    B = npy.random.rand(*shapes[1])
    
    M, K = A.shape
    K2, N = B.shape

    assert K == K2, "Inner dimensions must match"
    C = npy.zeros((M,N))

    return A,B,C
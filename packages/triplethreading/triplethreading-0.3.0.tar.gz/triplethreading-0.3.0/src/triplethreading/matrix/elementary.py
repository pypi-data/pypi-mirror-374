import numpy as np
import copy

def rowswap(M, source_row, target_row):
    M[[source_row, target_row]] = M[[target_row, source_row]]

def rowscale(M, source_row, scaling_factor):
    M[source_row, :] = scaling_factor * M[source_row, :]

def rowreplacement(M, row_1, row_2, j , k):
    copy_M = copy.deepcopy(M)
    rowscale(copy_M, row_1, j)
    rowscale(copy_M, row_2, k)
    M[row_2] = copy_M[row_1] + copy_M[row_2]

def rref(M):

    rows, cols = M.shape
    print(rows)
    for i in range(rows):
        if M[i,i] == 0:
            for ii in range(i, rows):
                if M[ii, i] != 0:
                    rowswap(M, i, ii)
                    print('Swamp rows' , i, 'and', ii, '\n', M)
                    break
        if M[i,i] != 0:
            print('Scale row', i, 'by', M[i,i])
            rowscale(M, i, 1/M[i,i]) ## If the pivot == 1, the row stays the same
            print(M)
            for ii in range(i, rows-1):
                rowreplacement(M, i, ii+1, -M[ii+1,i], M[i,i])
                print('Clean up row:', ii+1)
                print(M)
            
if __name__ == '__main__':
    A = np.array([[1, 3, 0, 0, 3],
            [0, 0, 1, 0, 9],
            [0, 0, 0, 1, -4]])

    B = np.array([[3, 3, 6],
            [2, -1, 1],
            [1, 2, -4]], dtype = float)

    #print(A)
    #rowswap(A, 0 , 1)
    #print(A)
    #rowscale(A, 2, 10)
    #print(A)
    #rowreplacement(A, 0, 2, -3, 1)
    #print(A)
    print(B)
    rref(B)
    print(B)

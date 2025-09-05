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
    row = 0
    col = 0
    #for i in range(rows):
    while row < rows and col < cols:
        #print('Current loop: row = ', row, ' col = ', col)
        if M[row,col] == 0:
            for i in range(row+1, rows):
                if M[i, col] != 0:
                    rowswap(M, row, i)
                    #print('Swamp rows' , row, 'and', i, '\n', M)
                    break
        # If all elements in a column are zero, search for a pivot in next column
        if M[row,col] == 0:
            #print('M[', row, ',', col, '] is still zero')
            col += 1
            #print('row = ',row)
            #print('col = ', col)
            continue
        if M[row,col] != 0:
            #print('Scale row', row, 'by', M[row,col])
            rowscale(M, row, 1/M[row,col]) ## If the pivot == 1, the row stays the same
            #print(M)
            for i in range(row + 1, rows):
                rowreplacement(M, row, i, -M[i,col], M[row, col])
                #print('Clean up row:', i)
                #print(M)
        
        row += 1
        col += 1
            
if __name__ == '__main__':
    A = np.array([[1, 3, 0, 0, 3],
            [0, 0, 1, 0, 9],
            [0, 0, 0, 1, -4]])

    B = np.array([[1, 4, 7, 10, 13],
                  [2, 5, 8, 11, 14],
                  [3, 6, 9, 12, 15]], dtype = float)

    print('Initial matrix A:')
    print(A)
    rowswap(A, 0 , 1)
    print('Swap rows 0 and 1:')
    print(A)
    rowscale(A, 2, 10)
    print('Scale row 2 by 10:')
    print(A)
    rowreplacement(A, 0, 2, -3, 1)
    print('Check row replacement:')
    print(A)
    
    print('Check the rref:')
    print('Initial Matrix B:')
    print(B)
    rref(B)
    print('rref of matrix B:')
    print(B)

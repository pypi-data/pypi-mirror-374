import torch

def rowswap(A, src_row, tar_row):
    '''
    Takes a matrix as input, along with the index of source row
    and the target row, and swap the content of source row with the target row.

    Input -> A: Matrxi
             src_rox: source row
             tar_row: target row
    Output -> A_swap: The matrix after swap the content of source row with the target row
    '''

    # first check the matrix A
    if A.numel() == 0:
        print("Empty Matrix")
        return 0
    
    # check the source row and target row
    if src_row >= len(A) or tar_row >= len(A):
        print("Exceed Boundary")
    
    # clone the matrix A
    A_swap = A.clone()

    # clone the source row and target row
    clo_src_row = A_swap[src_row].clone()
    clo_tar_row = A_swap[tar_row].clone()

    # swap the row
    A_swap[src_row] = clo_tar_row
    A_swap[tar_row] = clo_src_row

    return A_swap


def rowscale(A, src_row, scl_fac):
    '''
    Takes a matrix as an input, along with the index of source
    row and scaling factor, and perform row-scaling and return the new matrix.

    Input -> A: Matrix
             src_row: source row
             scl_fac: scaling factor
    Output -> A_scl: new matrix after doing row-scaling
    '''

    # check the matrix
    if A.numel() == 0:
        print("Empty Matrix")
        return 0
    
    # check the source row
    if src_row >= len(A):
        print("Exceed Boundary")
        return 0
    
    # check the factor
    # if not isinstance(scl_fac, (int, float)):
    #     raise TypeError("scl_fac need to be int or float")
    
    # row-scaling
    A_scl = A.clone()
    A_scl[src_row] = scl_fac * A_scl[src_row]

    return A_scl
    

def rowreplacement(A, fir_row, sec_row, fac_j, tar_row, fac_k):
    '''
    To perform jRi + kRj that takes a matrix as an input,
    first row, the second row, the scaling factors j and k.

    Input -> A: matrix
             fir_row: first row
             sec_row: second row
             tar_row: target row
             fac_j: factor j applied on first row
             fac_k: factor k applied on second row
    Output -> A_rep: matrix after doing row replacement
    '''

    # check the matrix 
    if A.size == 0:
        print("Empty Matrix")
        return 0
    
    # check the row
    if fir_row > len(A) or sec_row > len(A):
        print("Exceed Boundary")
        return 0
    
    # check the factor
    if not isinstance(fac_j, (int, float)):
        raise TypeError("fac_j need to be int or float")
    if not isinstance(fac_k, (int, float)):
        raise TypeError("fac_k need to be int or float")
    
    # do scaling
    A_rep = A.clone()
    A_rep[tar_row] = fac_j * A_rep[fir_row] + fac_k * A_rep[sec_row]
    
    return A_rep


def rref(A):
    '''
    Takes a matrix as an input. The task is to (i) Make
    the pivot element in the every row 1, (ii) make all the element below pivot element as 0.

    Input -> A: matrix
    Output -> A_ref: Row Echelon Form of A
    '''

    # check the matrix A
    if A.numel() == 0:
        print("Empty Matrix")
        return 0
    
    A_ref = A.clone()
    row, col = A_ref.shape

    # begins rows
    m = 0
    choose_row = 0


    # main loop
    # first for the col
    for i in range(col):
        if m >= row:
            break
        
        # for each column, we need to find the maximum number
        max_vul = 0
        for j in range(m, row):
            cur_vul = abs(A_ref[j, i]) # current vule
            if cur_vul > max_vul:
                max_vul = cur_vul
                choose_row = j

        # if all number in this column is 0, then we skip this column
        if max_vul == 0:
            m += 1
            continue

        # then we swap the row
        if choose_row != i:
            A_ref = rowswap(A_ref, choose_row, i)

        # let the first element become 1
        fir_vul = A_ref[m, i]
        if abs(fir_vul) <= 0:
            continue
        A_ref = rowscale(A_ref, m, 1 / fir_vul)


        # make other element in this column to 0
        for k in range(i, row):
            if k == m:
                continue
            factor = A_ref[k, i]
            if abs(factor) > 0:
                A_ref[k] = A_ref[k] - factor * A_ref[m]
        

        # move to another column
        m += 1


    return A_ref


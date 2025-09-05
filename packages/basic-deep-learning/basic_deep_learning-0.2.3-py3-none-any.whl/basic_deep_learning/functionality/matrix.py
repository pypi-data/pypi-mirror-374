"""Module containing the Matrix class."""
from typing import Self
import random
from ..miscellaneous.linear_algebra import LinearAlgebraUtils
import matrix_ops

class Matrix:
    def __init__(self,
                matrix: list[list[int|float]]) -> None:
        """Implementation of matrices as a list of lists; each inner list representing a row.
        
        Example: The following matrix M=
        
        1 2\n
        3 4
        
        is implemented as "M=Matrix([[1,2],[3,4]])".
        
        If the user passes to the matrix argument a list of uneven rows, the constructor automatically fills the empty places with 0's."""
        if not matrix:
            raise TypeError("Cannot pass an empty matrix.")
        pmax = max(len(matrix[i]) for i in range(len(matrix)))
        if pmax < 1:
            raise TypeError("Cannot pass an empty matrix.")   
        self.format = (len(matrix), pmax) #The format of the matrix in the form of a (number of rows, numbers of columns) tuple.
        self.matrix = [row + [0] * (pmax - len(row)) for row in matrix] #The list of lists representing the matrix, where the empty spaces are filled with 0's.

    def __validate_indices(self,
                           i: int|None = None,
                           j: int|None = None) -> None: #Private method.
        """If at least one index is passesd, the method will raise an error if that index is within the appropriate range."""
        if i is not None and i not in range(1,self.format[0]+1):
            raise IndexError(f"Index {i} is out of the expected range [1,{self.format[0]}].")
        if j is not None and j not in range(1,self.format[1]+1):
            raise IndexError(f"Index {j} is out of the expected range [1,{self.format[1]}].")
    
    def get_entry(self,
                  i: int,
                  j: int) -> int|float:
        """Returns the entry at the i-th row and the j-th column of the matrix.
        
        The indexation of the matrix's rows and columns are according to the mathematical convention, ie. starts at 1.
        
        Raises an error if either one of the indices is out of range."""
        self.__validate_indices(i, j)
        return self.matrix[i-1][j-1]
    
    def set_entry(self,
                  value: int|float,
                  i: int,
                  j: int) -> None:
        """Takes a certain floating-point value and sets it as the (i, j) entry.
        
        The indexation of the matrix's rows and columns are according to the mathematical convention, ie. starts at 1.
        
        Raises an error if either one of the indices is out of range."""
        self.__validate_indices(i, j)
        self.matrix[i-1][j-1] = value
    
    def get_row(self,
                i: int) -> list[int|float]:
        """Returns the i-th row.
        
        The indexation of the matrix's rows and columns are according to the mathematical convention, ie. starts at 1.
        
        Raises an error if the index is out of range."""
        self.__validate_indices(i=i)
        return self.matrix[i-1]
    
    def get_column(self,
                j: int) -> list[int|float]:
        """Returns the j-th column.
        
        The indexation of the matrix's rows and columns are according to the mathematical convention, ie. starts at 1.
        
        Raises an error if the index is out of range."""
        self.__validate_indices(j=j)
        return [row[j - 1] for row in self.matrix]
    
    @classmethod
    def zero(cls,
            n: int,
            p: int) -> Self:
        """Takes a format (number of rows, number of columns) and returns a matrix with that format and whose entries are all zeros."""
        return cls([[0 for j in range(p)] for i in range(n)])
    
    def T(self) -> Self:
        """Returns the transposed matrix."""
        transposed = [[self.matrix[j][i] for j in range(self.format[0])] for i in range(self.format[1])]
        return Matrix(transposed)

    def __add__(self, B: Self) -> Self:
        """Overloads the + operator to Matrix objects.
        
        If M and N are two Matrix instances, "M+N" returns a matrix instance representing their sum.
        
        Raises an error if the formats of the matrices do not match."""
        if self.format != B.format:
            raise TypeError("Cannot add two matrices of different formats.")
        A_cpp = matrix_ops.Matrix(self.matrix)
        B_cpp = matrix_ops.Matrix(B.matrix)  # Changed from B.format to B.matrix
        C_cpp = matrix_ops.Matrix.sum(A_cpp, B_cpp)

        return Matrix(C_cpp.get_matrix())

    def __sub__(self, B: Self) -> Self:
        """Overloads the - operator to Matrix objects.
        
        If M and N are two Matrix instances, "M-N" returns a matrix instance representing their difference.
        
        Raises an error if the formats of the matrices do not match."""
        if self.format != B.format:
            raise TypeError("Cannot subtraact two matrices of different formats.")
        A_cpp = matrix_ops.Matrix(self.matrix)
        B_cpp = matrix_ops.Matrix(B.matrix)  # Changed from B.format to B.matrix
        minusB_cpp = matrix_ops.Matrix.scale(B_cpp, -1)
        C_cpp = matrix_ops.Matrix.sum(A_cpp, minusB_cpp)

        return Matrix(C_cpp.get_matrix())
        
    def __matmul__(self, B: Self) -> Self:
        """Overloads the @ operator to Matrix objects.
        
        If M and N are two Matrix instances, "M @ N" returns a matrix instance representing their element-wise product.
        
        Raises an error if the formats of the matrices do not match."""
        if self.format != B.format:
            raise TypeError("Cannot multiply component-wise two matrices of different formats.")
        A_cpp = matrix_ops.Matrix(self.matrix)
        B_cpp = matrix_ops.Matrix(B.matrix)
        C_cpp = matrix_ops.Matrix.cwise_prod(A_cpp, B_cpp)

        return Matrix(C_cpp.get_matrix())
    
    def __mul__(self, B: Self) -> Self:
        """Overloads the * operator to Matrix objects.
        
        If M and N are two Matrix instances, "M * N" returns a matrix instance representing their product.
        
        Raises an error if the number of columns of the first does not match the number of rows of the second."""
        if self.format[1] != B.format[0]:
            raise TypeError(f"Invalid matrix formats ({self.format[1]}≠{B.format[0]}).")
        A_cpp = matrix_ops.Matrix(self.matrix)
        B_cpp = matrix_ops.Matrix(B.matrix)
        C_cpp = matrix_ops.Matrix.product(A_cpp, B_cpp)
        return Matrix(C_cpp.get_matrix())
    
    def __rmul__(self, scalar: int|float) -> Self:
        """Overloads the * operator to allow multiplication of a Matrix instance by a scalar on the left.
        
        If M is a Matrix instance and c is a scalar, "c * M" returns a matrix instance representing their product."""
        A_cpp = matrix_ops.Matrix(self.matrix)
        scaledA_cpp = matrix_ops.Matrix.scale(A_cpp, scalar)
        return Matrix(scaledA_cpp.get_matrix())
    
    def __truediv__(self, scalar):
        # Add element-wise division by scalar
        if not isinstance(scalar, (int, float)):
            raise TypeError("Can only divide by scalar")
        A_cpp = matrix_ops.Matrix(self.matrix)
        scaledA_cpp = matrix_ops.Matrix.scale(A_cpp, 1/scalar)
        return Matrix(scaledA_cpp.get_matrix())
    
    def __eq__(self, B: Self) -> bool:
        """Overloads the == operator."""
        if self.matrix == B.matrix:
            return True
        else:
            return False

    def __str__(self) -> str:
        n = self.format[0]
        s = ''
        for i in range(n-1):
            s += f'\t{self.matrix[i]},\n'
        s += f'\t{self.matrix[n-1]}'
        return f'matrix([\n{s}\n])'
    
    @classmethod
    def randomize(cls,
                  n: int,
                  p: int,
                  min_value: int|float,
                  max_value: int|float) -> Self:
        """Takes a format (n, p) and a range of values to create a random Matrix instance."""
        matrix_instance = cls.zero(n, p)
        for i in range(1, n+1):
            for j in range(1, p+1):
                t = random.random()
                matrix_instance.set_entry(min_value*(1-t) + t*max_value, i, j)
        return matrix_instance
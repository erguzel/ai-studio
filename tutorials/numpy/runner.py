import exchelp.exception_helper as eh
import numpy as np

try:
    b = np.array([[1.5, 2, 3],[9,0,43]])
except Exception as e :
    eh.CoreException('some mess',e,True,True).Act()

print(
b.shape)
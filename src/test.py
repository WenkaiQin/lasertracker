from collections import deque
import numpy as np

# Updates all coordinates of a path with movement.
def update_path(path, rel):
	path_L = [ tuple(np.subtract(coord,rel)) for coord in path ]
	return deque(path_L)

path = deque(maxlen=3)
path.append((1,1))
path.append((2,2))
path.append((3,3))

print update_path(path, (2,2))
print path[0][0]

print 0<path[0][0]<2 and 0<path[1][0]<3

a = (1,1)
b = (2,2)

print tuple(np.subtract(a,b))
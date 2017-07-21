from collections import deque
import numpy as np

# Updates all coordinates of a path with movement.
def update_path(path, rel):
	path_L = [ tuple(np.subtract(coord,rel)) for coord in path ]
	return deque(path_L)

# Updates all coordinates of a path with movement.
def update_path_dst(path, ref, dst):
	rel = np.subtract(dst, ref)
	return update_path(path, rel)

path = deque(maxlen=3)
path.append((1,1))
path.append((2,2))
path.append((3,3))

# print update_path(path, (2,2))
print path
print update_path_dst(path, (1,1), (2,2))


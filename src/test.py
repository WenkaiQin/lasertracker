import numpy as np

def filter_path(path, dfilter = [
	0.0024, 0.0162, 0.0553, 
	0.1224, 0.1923, 0.2226,	
	0.1923, 0.1224, 0.0553, 
	0.0162,	0.0024]):

	if len(path) < len(dfilter):
		return path[len(path)/2]
	elif len(path) > len(dfilter):
		print ' Path length too long.\n Current length:', len(path), '.\n Required length:', len(dfilter)
		return -1
	else:
		return tuple(np.dot(dfilter, path).astype(int))

path = [[1,2],[3,4],[5,6],[7,8],[9,10],[11,12],[1,2],[3,4],[5,6],[7,8],[9,10]]
print filter_path(path)
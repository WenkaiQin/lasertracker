from collections import deque

d = deque(maxlen=3)
d.append((20,20))
print d
d.append((21,20))
print d
d.append((22,20))
print d
d.append((23,20))
print d

for el in d:
	print el
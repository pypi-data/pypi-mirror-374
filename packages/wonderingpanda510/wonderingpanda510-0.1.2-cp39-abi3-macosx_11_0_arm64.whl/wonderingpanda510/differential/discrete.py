def diff(x, t):
	if len(x) != len(t):
		raise ValueError("error")
	v = []
	for i in range(1, len(x)):
		k = (x[i] - x[i - 1]) / (t[i] - t[i - 1])
		v.append(k)
	return v

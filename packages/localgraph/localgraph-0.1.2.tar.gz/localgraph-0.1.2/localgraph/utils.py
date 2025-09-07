# General utility functions related to local graph estimation

from collections import deque
import numpy as np

def max_cor_response(X, target_features):
	"""
	Compute the maximum absolute correlation of each target feature with all other features.

	Parameters
	----------
	X : numpy.ndarray
		Data matrix of shape (n, p), where n is the number of samples and p is the number of features.
	target_features : list of int
		Indices of the target features for which correlations are computed.

	Returns
	-------
	max_cors : list of float
		List of maximum absolute correlations, one value for each target feature in `target_features`.
	"""
	n = X.shape[0]
	Sigma_hat = X.T @ X / n
	abs_cor = np.abs(Sigma_hat)
	np.fill_diagonal(abs_cor, 0)
	max_cors = []
	for i in target_features:
		max_cor = np.max(abs_cor[i, :])
		max_cors.append(max_cor)
		
	return max_cors


def restrict_to_local_graph(A, target_features, max_radius):
	"""
	Restrict a full adjacency matrix to the local graph within a given radius of target features.

	Parameters
	----------
	A : numpy.ndarray
		Binary adjacency matrix (p x p).
	target_features : int or list of int
		Index/indices of the target features around which the local graph is built.
	max_radius : int
		Maximum radius for including neighbors in the local graph.

	Returns
	-------
	Q : dict
		Dictionary mapping edge tuples (i, j) to 1 if the edge is retained.
		Only edges with at least one endpoint within radius <= max_radius
		of a target feature are included. Edges where both endpoints are
		exactly at the outermost radius are excluded.
	"""

	if isinstance(target_features, int):
		target_features = [target_features]

	n = A.shape[0]
	dist = {t: 0 for t in target_features}
	frontier = deque(target_features)

	# Compute minimum distance from any target
	while frontier:
		u = frontier.popleft()
		if dist[u] >= max_radius:
			continue
		for v in np.nonzero(A[u])[0]:
			if v not in dist:
				dist[v] = dist[u] + 1
				frontier.append(v)

	# Build edge dictionary Q
	Q = {}
	for i in range(n):
		if i not in dist:
			continue
		for j in np.nonzero(A[i])[0]:
			if j <= i or j not in dist:
				continue
			# Exclude edges where both ends are at max_radius
			if not (dist[i] == dist[j] == max_radius):
				Q[(i, j)] = 1
				Q[(j, i)] = 1  # symmetric

	return Q



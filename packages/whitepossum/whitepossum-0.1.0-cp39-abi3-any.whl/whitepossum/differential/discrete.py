import array
def diff(tK: array.array, x: array.array) -> array:
  """
  Compute the velocity function for time series data.

  This function checks for array equality and raises an error if not equal.

  Formula: v(t) = (x(t_k) - x(t_(k - 1))) / (t_k - t_(k - 1))

  Arguments:
   tK: time value
   x:  a signal that is a function of t_k

  Raises:
    ValueError: if len(tK) != len(x)

  Returns:
    array: v(t) of time series data.

  """
  if len(tK) != len(x):
    raise ValueError("Arrays must be equal in length")
  k = 0
  vT = array.array("d")
  for arr in tK:
    numerator = x[k] - x[k-1]
    denomenator = arr - tK[k-1]
    v = numerator / denomenator
    vT.append(v)
    k=+1

  return vT

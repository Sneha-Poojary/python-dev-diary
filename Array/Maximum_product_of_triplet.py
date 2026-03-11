#Given an integer array, find a maximum product of a triplet in the array.
arr = [-10, -3, -5, -6, -20]

arr.sort()

n = len(arr)

case1 = arr[n-1] * arr[n-2] * arr[n-3]
case2 = arr[0] * arr[1] * arr[n-1]

print(max(case1, case2))
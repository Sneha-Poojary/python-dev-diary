#Given an array of integers arr[] of size n, the task is to rotate the array elements to the left by d positions.
arr = [1, 2, 3, 4]
d = 2

n = len(arr)
for i in range (d):
    first = arr[0]
    for j in range (n-1):
        arr[j]= arr[j+1]

    arr[n-1] = first

print(arr)
# arr = [1,2,3,4,5,6,7,8]
# d = 3
#
# result = arr[d:] + arr[:d]
# print(result)

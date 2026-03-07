#Given an array of positive integers arr[] of size n, the task is to find second largest distinct element in the array.
#Note: If the second largest element does not exist, return -1.
def Second_largest(arr):
    largest=-1
    second=-1
    for num in arr:
        if num > largest:
            second = largest
            largest = num
        elif num> second and num!= largest:
            second = num
    return second

arr = [12, 35,1,10,34,1]
print(Second_largest(arr))

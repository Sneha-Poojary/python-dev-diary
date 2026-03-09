#Given an array arr[] and an integer k, find the array after reversing every subarray of consecutive k elements in place.
#If the last subarray has fewer than k elements, reverse it as it is. Modify the array in place, do not return anything.
def reverse_group (arr,k):
    n = len(arr)
    for i in range(0,n,k):
        start = i
        end = min(i+k-1, n-1)
        while start < end:
            arr[start],arr[end] = arr[end],arr[start]
            start +=1
            end -=1
    return arr
arr = [1,2,3,4,5,6,7,8]
k=3
print(reverse_group(arr,k))

#Given an array of n integers, the task is to find the third largest element. All the elements in the array are distinct integers.
# def Second_largest(arr):
#     first=second=third=float('-inf')
#
#     for num in arr:
#         if num > first:
#             third=second
#             second = first
#             first = num
#         elif num > second:
#             third = second
#             second = num
#         elif num> third:
#             third = num
#     return third
# arr = [1, 14, 2, 16, 10, 20]
# print(Second_largest(arr))
arr = [1, 14, 2, 16, 10, 20]
arr.sort()
print(arr[-2])
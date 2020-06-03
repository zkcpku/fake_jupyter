def subOne(num):
	if num <= 0:
		return
	else:
		print(num)
		subOne(num - 1)


subOne(5)


for i in range(3):
	if i % 2 == 0:
		# 注释
		print(i)
	else:
		print(i + 1)


# 直接赋值
myDict = {}
myList = []
myDict[[1]] = 1 # list是不可哈希的，因此无法做字典的key
myDict['l'] = myList
myList.append(1)
print(myList)
print(myDict)


myList1 = [1]
myList2 = myList1
myList2.append(1)
print(myList1)
print(myList2)


# 浅拷贝
old = [1,[1,2,3],3]
new = old.copy()
print('Before:')
print(old)
print(new)
new[0] = 3
new[1][0] =3
print('After:')
print(old)
print(new)


# 深拷贝
import copy
old = [1,[1,2,3],3]
new = copy.deepcopy(old)
print('Before:')
print(old)
print(new)
new[0] = 3
new[1][0] = 3
print('After:')
print(old)
print(new)
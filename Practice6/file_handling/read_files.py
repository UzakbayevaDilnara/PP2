#1
f = open("demofile.txt")
print(f.read())

#2
f = open("D:\\myfiles\welcome.txt")
print(f.read())

#3
f = open("demofile.txt")
print(f.readline())
f.close()

#4
with open("demofile.txt") as f:
  print(f.readline())

#5
with open("demofile.txt") as f:
  print(f.readline())
  print(f.readline())

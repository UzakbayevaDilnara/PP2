#1
import shutil
shutil.move("test.txt", "folder/test.txt")
print("Файл перемещён!")

#2
with open("hello.txt", "w", encoding="utf-8") as file:
    file.write("Hello, world!")

print("Файл создан!")

#3
import os
os.rename("hello.txt", "new_hello.txt")
print("Файл переименован!")

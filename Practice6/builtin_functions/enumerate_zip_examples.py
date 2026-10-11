#1
fruits = ["apple", "banana", "orange", "grape"]

for index, fruit in enumerate(fruits):
    print(index, fruit)

#2
names = ["Ali", "Dana", "Arman"]
ages = [18, 20, 19]

for name, age in zip(names, ages):
    print(name, age)

#3
names = ["Ali", "Dana", "Arman"]
grades = [90, 85, 95]

for number, (name, grade) in enumerate(zip(names, grades), start=1):
    print(f"{number}. {name} - {grade} баллов")



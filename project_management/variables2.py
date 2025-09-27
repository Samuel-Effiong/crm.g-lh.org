import math

principal = 20000
rate = 5
time = 5

interest = (principal * rate * time) / 100

print(interest)


math.sqrt(interest)

b = 2 * 10**4
a = 1.7 * 10**2
c = 50

b_squared = b**2

square_root = math.sqrt(b_squared - (4 * a * c))

numerator = -b + square_root

denominator = 2 * a

result = numerator / denominator
print(result)
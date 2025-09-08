
def factorial(n):

    result = 1

    for i in range(1, n+1):

        result *= i

    return result

print(factorial(20))


"""
sentence = "how many vowels are in this exact sentence?"
vowels = "aeiouAEIOU"
count = 0
for char in sentence:
    if char in vowels:
        count += 1
print(count)
"""
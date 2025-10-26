"""
Practice file for testing the Python Learning Bot.

Try deleting the function below and rewriting it yourself!
The bot will guide you with progressive hints.
"""

def calculate_average(numbers):
    """Calculate the average of a list of numbers."""
    total = 0
    for num in numbers:
        total += num
    return total / len(numbers)


# Test the function
numbers = [10, 20, 30, 40, 50]
result = calculate_average(numbers)
print(f"Average: {result}")

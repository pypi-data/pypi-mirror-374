'''
AUTHOR:Niranjan <email:yvniranjanreddy@gmail.com>

'''

def addition(*args):
    return sum(args)

def subtraction(*args):
    if not args:
        return 0
    result=args[0]
    for i in args[1:]:
        result-=i
    return result


def multiplication(*args):
    result=1
    for i in args:                                   
        result*=i
    return result
def division(*args, direction=1):
    """
    direction = 1  -> left-to-right (normal)
    direction = -1 -> right-to-left (reverse)
    """
    if not args:
        return 0

    numbers = list(args)

    if direction == -1:
        # Right-to-left division
        result = numbers[-1]
        for i in reversed(numbers[:-1]):
            if result == 0:
                return "Error: Division by zero!"
            result = i / result
        return result
    else:
        # Left-to-right division (normal)
        result = numbers[0]
        for i in numbers[1:]:
            if i == 0:
                return "Error: Division by zero!"
            result = result / i
        return result

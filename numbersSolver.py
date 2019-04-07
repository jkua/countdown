#!/usr/bin/env python3

# This implements a solution generator for the Countdown numbers game
# using a Monte-Carlo approach
#
# Contact: John Kua <john@kua.fm>
#

import random
import time

def generateTarget():
    '''Generate a target - integers from 100-999'''
    return int(random.random() * 900 + 100)

def generateNumbers(numBig=None):
    '''Randomly generate a set of numbers, as per Countdown rules:
       Six numbers are selected from 24 tiles.
       There are four numbers in the large set { 25 , 50 , 75 , 100 }
       There are twenty numbers in the small set, two each of the numbers 1-10
       { 1 , 1 , 2 , 2 , 3 , 3 , 4 , 4 , 5 , 5 , 6 , 6 , 7 , 7 , 8 , 8 , 9 , 9 , 10 , 10 }
       In the game, the contestant may specify how many are drawn from the large set.
    '''
    if numBig is None:
        numBig = random.choice([0, 1, 2, 3, 4])
    bigs = [25, 50, 75, 100]
    littles = list(range(1,11)) * 2

    numbers = random.sample(bigs, numBig) + random.sample(littles, 6-numBig)
    return numbers

def generateRandomSequence(numbersIn):
    '''Randomly generate a valid numbers solution sequence.'''
    operatorSet = ['+', '-', '*', '/']
    sequence = []
    numbers = numbersIn.copy()
    interimResults = numbers.copy()
    random.shuffle(numbers)
    sequence.append(numbers.pop())
    sequence.append(numbers.pop())
    stack = sequence.copy()
    for i in range(9):
        # print('Stack: {}'.format(stack))
        # print('Solutions: {}'.format(interimResults))
        # Not enough numbers, must add number to stack
        if len(stack) < 2:
            nextElement = 'number'
        # No more numbers must add operator
        elif len(numbers) == 0:
            nextElement = 'operator'
        # Randomly select number or operator
        else:
            if random.random() < 0.5:
                nextElement = 'number'
            else:
                nextElement = 'operator'

        if nextElement == 'number':
            element = numbers.pop()
            sequence.append(element)
            stack.append(element)
        else:
            operators = random.sample(operatorSet, 4)
            for operator in operators:
                try:
                    rpnEvaluate(stack, operator)
                    break
                except ValueError:
                    continue
            sequence.append(operator)
            interimResults.append(stack[-1])
        # print('Next: {}'.format(sequence[-1]))

    return sequence, interimResults

def rpnEvaluate(stack, element):
    '''Update a RPN stack as a number is pushed or an operation executed.
       Follows Countdown rules:
       1. No negative results
       2. Only even division
    '''
    if type(element) is str:
        if element == '+':
            result = stack[-2] + stack[-1]
        elif element == '-':
            result = stack[-2] - stack[-1]
            if result < 0:
                raise ValueError
        elif element == '*':
            result = stack[-2] * stack[-1]
        elif element == '/':
            if stack[-1] == 0:
                raise ValueError
            result, remainder = divmod(stack[-2], stack[-1])
            if remainder != 0:
                raise ValueError
        stack.pop()
        stack[-1] = result
    else:
        stack.append(element)

    return stack

def formatSolution(sequence, target, ignoreMultiplyByOne=True):
    '''Format a solution sequence using infix notation'''
    calcStack = []
    outputStack = []
    for element in sequence:
        if ignoreMultiplyByOne and len(calcStack) > 0 and calcStack[-1] == 1 and element in ['*', '/']:
            print('Ignoring multiply/divide by 1')
            calcStack.pop()
            outputStack.pop()
            continue

        rpnEvaluate(calcStack, element)
        if type(element) is int:
            outputStack.append(str(element))
        else:
            if element in ['+', '*'] and len(outputStack[-2]) < len(outputStack[-1]):
                result = '({} {} {})'.format(outputStack[-1], element, outputStack[-2])
            else:
                result = '({} {} {})'.format(outputStack[-2], element, outputStack[-1])
            outputStack.pop()
            outputStack[-1] = result

            print('{} = {}'.format(outputStack[-1][1:-1], calcStack[-1]))
            if calcStack[-1] == target:
                break

    output = '{} = {}'.format(outputStack[-1], target)
    tempString = ''
    for char in outputStack[-1]:
        if char.isnumeric():
            tempString += char
        else:
            tempString += ' '
    tokens = tempString.split(' ')
    numbersUsed = 0
    for token in tokens:
        if len(token) > 0:
            numbersUsed += 1
    print('Numbers used: {}'.format(numbersUsed))

    return output, numbersUsed


if __name__=='__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--numbers', '-n', nargs=6, type=int, help='Specify the 6 numbers')
    parser.add_argument('--target', '-t', type=int, help='Specify the target')
    parser.add_argument('--limit', '-l', type=float, default=30, help='Time limit in seconds')
    parser.add_argument('--sequence', '-s', nargs=11, help='Solution sequence to print (for debugging)')
    args = parser.parse_args()

    if args.numbers is None:
        args.numbers = generateNumbers(2)

    if args.target is None:
        args.target = generateTarget()

    print('\nNumbers: {}'.format(', '.join([str(el) for el in args.numbers])))
    print('Target: {}'.format(args.target))

    if args.sequence:
        sequence = []
        for element in args.sequence:
            if element.isnumeric():
                sequence.append(int(element))
            else:
                sequence.append(element)
        print('Sequence: {}'.format(sequence))
        formattedSolution, numbersUsed = formatSolution(sequence, args.target)
        import sys; sys.exit(0)

    startTime = time.time()
    solutionAttempts = 0
    closestSolution = None

    # 30 second time limit, just like the show
    while time.time()-startTime < args.limit:
        print('\n{}: ****************'.format(solutionAttempts+1))
        sequence, interimResults = generateRandomSequence(args.numbers)
        print('Sequence: {}'.format(sequence))
        print('Results: {}'.format(interimResults))
        solutionAttempts += 1
        for result in interimResults:
            if closestSolution is None:
                closestSolution = (result, sequence)
            else:
                if abs(args.target - result) < abs(args.target - closestSolution[0]):
                    closestSolution = (result, sequence)
        if args.target in interimResults:
            break

    elapsedTime = time.time()-startTime
    print('\nNumbers: {}'.format(', '.join([str(el) for el in args.numbers])))
    print('Target: {}'.format(args.target))

    if args.target not in interimResults:
        print('\n**** FAILED TO FIND SOLUTION! - closest solution is {} ({} away)'.format(closestSolution[0], abs(args.target-closestSolution[0])))
        args.target, sequence = closestSolution
    print('Sequence: {}'.format(sequence))
    formattedSolution, numbersUsed = formatSolution(sequence, args.target)
    print('Elapsed time: {:.6f}, attempts: {}, attempt rate: {:.1f}'.format(elapsedTime, solutionAttempts, solutionAttempts/elapsedTime))

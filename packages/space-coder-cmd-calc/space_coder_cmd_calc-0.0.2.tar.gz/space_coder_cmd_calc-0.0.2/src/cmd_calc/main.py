'''
Regex-Calculator

Author: Madhav Garg
'''

import re
import time
import os
from pynput.keyboard import Key, Listener

pkey = ' '

def on_press(key):
    global pkey
    #print(key)
    try:
        pkey = key.char
        pkey += ' '
    except AttributeError:
        if key == Key.enter:
            pkey = key
            #print("enter")
        elif key == Key.backspace:
            pkey = ''
        elif key == Key.space:
            pkey = '  '
        else:
            pkey = ' '
    return False

# Collect events until released

def join():
    with Listener(on_press=on_press,) as listener:
        listener.join()

IS_WINDOWS = True if os.name == 'nt' else False
NORMAL_TEXT = "\033[0m"

RED = '\033[31m'
BLUE = '\033[0;34m'	
GREEN = '\033[0;32m'
YELLOW = '\033[0;33m'

BOLD = '\033[1;37m'


os.system("color")

def clear(after=0):
    time.sleep(after)
    if IS_WINDOWS:
        os.system("cls")
    else:
        os.system("clear")

def red(*strings, end=''):
    tbr = RED
    for string in strings:
        tbr += str(string)
        if string != strings[-1]:
            tbr += ' '
    tbr += NORMAL_TEXT
    tbr += end
    return tbr

def green(*strings, end=''):
    tbr = GREEN
    for string in strings:
        tbr += str(string)
        if string != strings[-1]:
            tbr += ' '
    tbr += NORMAL_TEXT
    tbr += end
    return tbr

def blue(*strings, end=''):
    tbr = BLUE
    for string in strings:
        tbr += str(string)
        if string != strings[-1]:
            tbr += ' '
    tbr += NORMAL_TEXT
    tbr += end
    return tbr

def yellow(*strings, end=''):
    tbr = YELLOW
    for string in strings:
        tbr += str(string)
        if string != strings[-1]:
            tbr += ' '
    tbr += NORMAL_TEXT
    tbr += end
    return tbr

def bold(*strings, end=''):
    tbr = BOLD
    for string in strings:
        tbr += str(string)
        if string != strings[-1]:
            tbr += ' '
    tbr += NORMAL_TEXT
    tbr += end
    return tbr


def mult(string):
    test = re.findall(r"([0-9]+(?:\.[0-9]+)?)[ ]*[\*][ ]*([0-9]+(?:\.[0-9]+)?)", string)
    #print(len(test[0]))

    try:
        return (True, round(float(test[0][0]) * float(test[0][1]), 15))
    except IndexError:
        #print()
        return (False, None)

    #print(test, string)

def add(string):
    test = re.findall(r"([0-9]+(?:\.[0-9]+)?)[ ]*[+][ ]*([0-9]+(?:\.[0-9]+)?)", string)
    #print(len(test[0]))

    try:
        return (True, round(float(test[0][0]) + float(test[0][1]), 15))
    except IndexError:
        #print()
        return (False, None)

    #print(test, string)

def subtract(string):
    test = re.findall(r"([0-9]+(?:\.[0-9]+)?)[ ]*[-][ ]*([0-9]+(?:\.[0-9]+)?)", string)
    #print(len(test[0]))

    try:
        return (True, round(float(test[0][0]) - float(test[0][1]), 15))
    except IndexError:
        #print()
        return (False, None)

    #print(test, string)

def divide(string):
    test = re.findall(r"([0-9]+(?:\.[0-9]+)?)[ ]*[\\/][ ]*([0-9]+(?:\.[0-9]+)?)", string)
    #print(len(test[0]))

    try:
        return (True, round(float(test[0][0]) / float(test[0][1]), 15))
    except IndexError:
        #print()
        return (False, None)

    #print(test, string)

def exponents(string):
    test = re.findall(r"([0-9]+(?:\.[0-9]+)?)[ ]*[\^][ ]*([0-9]+(?:\.[0-9]+)?)", string)
    #print(len(test[0]))

    try:
        return (True, round(float(test[0][0]) ** float(test[0][1]), 15))
    except IndexError:
        #print()
        return (False, None)

    #print(test, string)


def sqrt(string):
    test = re.findall(r"sqrt[ ]*([0-9]+(?:\.[0-9]+)?)", string)
    #print(len(test[0]))

    try:
        return (True, round(float(test[0][0]) ** 0.5, 15))
    except IndexError:
        #print()
        return (False, None)

    #print(test, string)

def ans(inp):
    ismult, multans = mult(inp)
    isadd, addans = add(inp)
    issub, subans = subtract(inp)
    isdiv, divans = divide(inp)
    isexp, expans = exponents(inp)
    issqrt, sqrtans = sqrt(inp)

    funcs = [ismult, isadd, issub, isdiv, isexp, issqrt]
    functions = 0
    final_answer = 0

    for function in funcs:
        if function == True:
            functions += 1
    error = ''
    if functions == 0:
        error = red("No Valid Operation Detected...")
        return error, False
    elif functions > 1:
        error = red("Calculating with multiple functions is not yet supported...")
        return error, False

    if ismult:
        final_answer = multans
    elif isadd:
        final_answer = addans
    elif issub:
        final_answer = subans
    elif isdiv:
        final_answer = divans
    elif isexp:
        final_answer = expans
    elif issqrt:
        final_answer = sqrtans

    return final_answer, True


def cinput(string='', special='normal'):
    global pkey
    output = ''
    print(end="\n" + string)
    pkey = ' '
    while True:
        join()
        if pkey == ' ':
            continue
        elif pkey == Key.enter:
            break
        output += pkey
        output = output[:-1]
        #print(output)

        a, b = ans(output)
        
        if b:
            final_answer = yellow(f" = {a:g}")
        elif not b:
            final_answer = ''
        else:
            raise RuntimeError("Check 'ans' function")


        clear()
        if special == 'normal':
            print(end="\n" + string + output + final_answer)
        elif special == 'green':
            print(end="\n" + string + green(output) + final_answer)
        elif special == 'bold':
            print(end="\n" + string + bold(output) + final_answer)
        else:
            raise IndexError(f"No special '{special}' found. Maybe try lowercase?")

    return output


def main():
    global pkey
    first = True
    clear()
    error = ''
    final_answer = 0
    while True:
        clear()

        if not first and b:
            inp = cinput(f">>  {inp} = {final_answer}\n{blue("Press Enter To Continue")}\n\n{bold(">>")}  ", special='bold')
        else:
            inp = cinput(bold(">>  "), special='bold')

        a, b = ans(inp)

        if b:
            final_answer = f"{a:g}"
        elif not b:
            final_answer = a
            print("\n" + final_answer)
        else:
            raise RuntimeError("Check 'ans' function")
              
        print(blue("\nPress Enter To Continue"))

        pkey = ' '
        while pkey != Key.enter:
            join()

        first = False

if __name__ == '__main__':
    main()

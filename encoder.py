"""
Encoder Decoder in scratch https://scratch.mit.edu/projects/666285422/
"""

import math

chars = " 0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ!@#$%^&*()_+-=~`[]{};:'\"\\|,<.>/?"


def decode(code: int):
    decoded = ""
    for i in range(0, math.ceil(len(str(code))), 2):
        decoded = decoded + chars[int(str(code)[i] + str(code)[i+1])-1]
    return decoded


def encode(input: str):
    encoded = ""
    for i in range(len(str(input))):
        j = str(chars.index(str(input)[i])+1)
        if int(j) < 10:
            j = "0" + j
        encoded = encoded + str(j)
    return encoded


def decode_list(code: str):
    output = []
    temp = ""
    for i in range(0, math.floor(len(code)), 2):
        if str(code[i]) + str(code[i+1]) == "00":
            output.append(temp)
            temp = ""
            continue
        temp += chars[int(str(code[i]) + str(code[i+1]))-1]
    output.append(temp)
    return output


def encode_list(list: list):
    output = ""
    for i in list:
        output += encode(i) + "00"
    return output

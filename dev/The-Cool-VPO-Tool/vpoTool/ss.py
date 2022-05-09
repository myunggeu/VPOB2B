#!/bin/python3

import sys

def appendAndDelete(s, t, k):
    #delete from end of string s and t until they both match
    temp_s = s
    append_delete = 0
    while temp_s not in t and append_delete <= k:
        if len(temp_s) > 0:
            temp_s = temp_s[:-1]
            append_delete += 1
            print("{},{}".format(temp_s, t))
            print(append_delete)
    #determine how many letters to append to get to t
    #leng
    append_delete = append_delete + len(t) - len(temp_s)
    print(append_delete)
    #is number <= k?
    if append_delete <= k:
        return ("Yes")
    else:
        return ("No")
    # Complete this function

if __name__ == "__main__":
    s = input().strip()
    t = input().strip()
    k = int(input().strip())
    result = appendAndDelete(s, t, k)
    print(result)
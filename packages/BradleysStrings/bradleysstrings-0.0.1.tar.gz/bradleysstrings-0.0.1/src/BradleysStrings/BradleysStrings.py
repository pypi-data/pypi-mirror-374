def insert(mainstr,pos,insertstr):
    mainstr1 = mainstr[:pos]
    mainstr2 = mainstr[pos:]
    return mainstr1 + insertstr + mainstr2

def replaceatpos(mainstr,pos,repstr):
    mainstr1 = mainstr[:pos]
    mainstr2 = mainstr[pos + 1:]
    return mainstr1 + repstr + mainstr2

def splitatpos(str,pos):
    return [str[:pos],str[pos:]]

def strtoarr(str):
    output = []
    for letter in str:
        output.append(letter)
    return output

def arrtostr(arr):
    output = ""
    for letter in arr:
        output = output + letter
    return output

def replaceinstr(str,replacedarray = ["A","b","1"],replacewitharr = ["A","b","1"]):
    output = str
    i = 0
    for letter in str:
        if letter in replacedarray:
            replacedi = replacedarray.index(letter)
            output = replaceatpos(output,i,replacewitharr[replacedi])
        i += 1

    return output

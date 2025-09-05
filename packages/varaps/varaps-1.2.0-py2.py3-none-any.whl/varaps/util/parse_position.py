def parse_position(s):
    '''
    returns the 1-based position of the given mutation.
    
    INPUT:
    s: string of the format RefNAlt, where Ref = reference letter(s), N = position in the reference sequence and Alt = altered letter(s)
    
    OUTPUT:
    positive integer, the position in the reference sequence (N)
    '''
    intS = intE = 0
    readInts = False
    for idx,letter in enumerate(s):
        if (letter in '0123456789'): 
            if not readInts:
                intS = idx
                readInts = True
        else:
            if readInts:
                intE = idx-1
                break
    return int(s[intS:intE+1])

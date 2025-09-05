from cigar import Cigar
import pandas as pd
#import numpy as np

def read_contains_given_mutation(readStartPos, cigarStr, readSeq, mut, refSeq):
    '''
    returns a boolean value indicating whether a given read contains the given mutation.
    
    INPUTS:
    readStartPos: positive integer; 0-based starting position in the reference sequence of the read.
    cigarStr: CIGAR string of the read's alignment.
    readSeq: string; the read sequence.
    mut: string; the mutation of interest. 
         Notations: 
         A100C := an A at refernce sequence's 100th (1-based)position is alternated to C
         AC100A := a C at refernce sequence's 101st (1-based)position is deleted
         A100AC := a C at refernce sequence's 101st (1-based)position is inserted
    refSeq: string; the refernce to which the read is compared to find mutations (substitutions, deletions and insertions)
    
    OUTPUTS:
    a boolean value indicating whether the read contains the mutation, or a "None" if the read doesn't cover the mutation's position.
    '''
    ref, targetPos, alt = split_info_string(mut)
    # make it 0-based
    targetPos -= 1 
    qryPos = get_position(readStartPos, targetPos, cigarStr)
    
    # qryPos is None if the given position is not covered by the query
    # or the given position is deleted from the query
    if qryPos is None: 
        return None
 
    # qryPos is an int if the given position is matched
    else:
        # substitutions or deletions
        if len(ref) >= len(alt): 
            return (readSeq[qryPos:qryPos+len(alt)]==alt) & (refSeq[targetPos:targetPos+len(ref)]==ref)
        
        # insertions
        else:
            isLastMatch, nextCigar = is_last_match(qryPos, cigarStr)
            isInsertion = isLastMatch & (nextCigar[0] == len(alt)-len(ref)) & (nextCigar[1]=='I')
            return isInsertion & (readSeq[qryPos:qryPos+len(alt)]==alt) & (refSeq[targetPos:targetPos+len(ref)]==ref)


def query_all_mutations(readInfoDf, refseq, mutations):
    res = pd.DataFrame(index=range(readInfoDf.shape[0]), columns=mutations)
    for mut in mutations:
        res[mut] = readInfoDf.apply(lambda x: read_contains_given_mutation(x['startIdx_0Based'],
                                                                           x['CIGAR'],
                                                                           x['Sequence'],
                                                                           mut,
                                                                           refseq), 
                                    axis=1)
    
    return res


# helper functions
def is_last_match(qryPos, cigarStr):
    '''
    return a tuple of (bool, cigar tuple)
    INPUTS
    qryPos: uint, position of interest in the query sequence
    cigarStr: str, CIGAR information
    
    OUTPUT
    tuple of (lastMatch, next CIGAR)
    lastMatch: bool, whether the given qryPos is the last matched element of a matched period
    next CIGAR: tuple, the closest next CIGAR opertion from the qryPos, 
                (-1,'') is returned if qryPos is already in the last CIGAR operation.
    '''
    cigars = list(Cigar(cigarStr).items())
    counter = 0
    lastOp = ''
    for cigar in cigars:
        # flag position
        ## qryPos is still far behind 
        ## => keep moving forward
        if counter <= qryPos:
            if cigar[1] not in ['D','N','H','P']:
                counter += cigar[0]
        ## qryPos is surpassed, i.e., qryPos sits within a trunk of contuguous segment 
        ## => qryPos is not one of the last elements
        elif counter > qryPos+1:
            return (False, cigar)
        ## qryPos is one of the last elements
        ## => check wether it is a last element of a matched segment
        else:
            return (lastOp == 'M', cigar)
        # end flag
        
        # update lastOp
        lastOp = cigar[1]
    
    # exit the loop without early break
    return ((lastOp=='M') & (counter == qryPos+1), (-1,''))

def get_position(startPos, targetPos, cigarStr):
    # the qry sequence starts later than the target position
    # (i.e. not in range)
    if startPos > targetPos:
        return None
        
    # if in range:
    shift = targetPos - startPos
    qryPos = 0
    cigars = list(Cigar(cigarStr).items())
    
    for cigar in cigars:
        # flag situations and update qryPos and/or shift
        
        ## D := deletion, N := skipped 
        ## => shift moves backward, qry index stays put
        if cigar[1] in ['D','N']:
            # if the target position is deleted from the query sequence
            if (cigar[1]=='D') & (shift>=qryPos) & (shift < qryPos+cigar[0]):
                return np.nan
            qryPos += 0
            shift -= cigar[0]
        
        ## H := hard clipping, P := padding 
        ## => do nothing and go to the next cigar WITHOUT moving any positions
        elif cigar[1] in ['H','P']:
            qryPos += 0    
            shift += 0
            
        ## I := insertion, S:= soft clip 
        ## => both qry idex and shift move forward
        elif cigar[1] in ['I','S']:
            qryPos += cigar[0]
            shift += cigar[0] 

        ## In all the other cases => qry index moves forward, shift stays put
        ## ['M','=','X'], 
        else:
            qryPos += cigar[0]
            shift += 0
        # end flag
        
        if qryPos > shift:
            return shift
        
    # if the loop goes to the end without early break (return), then the query sequence doesn't cover the target position
    # (i.e. not in range)
    return None

def split_info_string(s):
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
    return s[:intS], int(s[intS:intE+1]), s[intE+1:]


# # example

# # get reference sequence
# import pysam
# REFSEQ = ''
# with pysam.FastxFile('../data/Galaxy2-[RefSeq_SARS-CoV_NC_45512.fasta].fasta') as fh:
#    for entry in fh:
#        REFSEQ = str(entry.sequence)

# # an example read
# startPos = 4171
# cigarStr = '13S63M2D7M2I55M11S'
# seqStr = 'GTATAAGAGACTGACTAAAAAGGCAGGTGGCACGACTGAACTGCTAGCGAAAGCTTTGAGATATGTGCCTCCAGACTTATATATCACCACTGACCCGGGTCAGGGTTTCACTGGATACACTGTAGAGGCTGCAAAGACAGGGCATCCACAG'


# mutations = ['T4183A','T4192G','A4199C','A4220T','A4222T','A4228T',
#             'A4229C','CAA4234C','A4243ATC','T4250G','A4267C','A4269C',
#             'T4273A','A4287C','G4288T']
# for mut in mutations:
#    print(mut)
#    print(read_contains_given_mutation(startPos, cigarStr, seqStr, mut, REFSEQ))
#    print()

'''
By: Amanda Trinh
CS 143B Winter 2019 - Project 2
Virtual Memory Manager
Written in Python 3.6

When running using a new input files, please change the variable path
and input_file (both) in the main method to the correct path/filename(s)
'''

# create and initialize the PM to 0 (free)
PM = dict() # the size of PA is 19 bits
# PA is divided into 1024 frames, each of which is 512 words
for i in range(524288):
    PM[i] = 0


MASK = [None]*32 # used for set, reset, and search for bits in BM
# set up the MASK
# diagonal contains “1”, all other fields are “0”
for i in range(32):
    MASK[i] = 1 << (31-i)

# This code is not mine and credit goes to:
# https://stackoverflow.com/questions/699866/python-int-to-binary
get_bin = lambda x, n: format(x, 'b').zfill(n) # x is the binary number, n is length of binary
'''
# Testing that the mask was created properly
# IT WORKS
for i in range(len(MASK)):
    print(get_bin(MASK[i],32))
'''

# initialize the BM
# bit map is 1024 bits (one per frame)
BM = list() # used to keep track of free/occupied frames
BM = [0]*32 # will be an array of 32 integers, each 32 bit

# ST always resides in frame 0 and is never paged out
BM[0] = MASK[0] # frame 0 == MASK[0]


def VA_into_spw(VA):
    '''
    break each Virtual Address (VA) down into s, p, and w bits
    VA is an integer (32 bits)
    --first 4 bits in VA are unused
    --s is 9 bits so ST size is 512 words (int) size table
    --p is 10 bits, 1024 words
    --w is 9 bits, 512 words

    VA: takes in an integer

    returns s,p,w as a tuple of ints
    '''
    s = (VA & 0b00001111111110000000000000000000) >> 19
    p = (VA & 0b00000000000001111111111000000000) >> 9
    w = (VA & 0b00000000000000000000000111111111)
    return (s,p,w)
'''
# for testing purposes
# VA 1048586 == bin 00000000000100000000000000001010

print(get_bin(1048586,32)) # double-check VA to binary is same as above, GOOD
s,p,w = VA_into_spw(1048586)
print(1048586)
print(get_bin(s,32))
print(get_bin(p,32))
print(get_bin(w,32))
print(s)
print(p)
print(w)
'''


def update_BM(frame_address):
    '''
    updates the bitmap (and PM) to the frame addresses that are now occupied
    '''
    global BM
    if frame_address == -1:
        # check that frame address does not reside outside of PM
        return -1
    for i in range(512):
        PM[frame_address + i] = 0

    BM_index = int(frame_address /(512*32))
    new_BM_value = BM[BM_index] | MASK[int(frame_address/512) % 32]
    BM[BM_index] = new_BM_value
    return 0


''' THE TLB '''
LRU = list()  # will be size of 4
# in the format:
# [(0,s,p,f),(1,s,p,f),(2,s,p,f),(3,s,p,f)]
# 0: least recently accessed
# 3: most recently accessed


if __name__ == '__main__':
    '''
    Change path & file names down below
    ASSUMPTION: Input files are formatted properly
    '''
    path = "/Volumes/USB/"
    #path = "/Users/Amanda/Desktop/"

    outpath = path + "306479132.txt"
    outfile = open(outpath, "w")

    input_file1 = path + "input1.txt"
    input_file2 = path + "input2.txt"

    '''
    INITIALIZATION OF PM
    should only be two lines long
    first line: pairs of (s,f)
    second line: triples of (p,s,f)
    '''
    # should only be two lines long
    with open(input_file1) as file:
        linecount = 1
        for line in file:
            parseline = line.split()
            if linecount == 1:
                # we are on the first line
                if len(parseline) % 2 != 0:
                    # checked to make sure first line is filled with pairs
                    exit(1)
                segment = 0
                address_f = 0
                count = 1
                for i in parseline:
                    if count % 2 == 1:
                        # we are reading a segment s number
                        segment = int(i)
                    else:
                        # we are reading an address f number
                        address_f = int(i)
                        PM[segment] = address_f
                        if address_f != -1:
                            # update bitmap
                            # each new PT occupies 2 frames
                            update_BM(address_f)
                            update_BM(address_f + 512) # must add 512 for second consecutive frame
                    count += 1
            elif linecount == 2:
                # we are on the second line
                if len(parseline) % 3 != 0:
                    # checked to make sure second line is filled with triples
                    exit(1)
                page = 0
                segment = 0
                address_f = 0
                count = 1
                for i in parseline:
                    if count % 3 == 1:
                        # we are reading a segment s number
                        page = int(i)
                    elif count % 3 == 2:
                        # we are reading an address f number
                        segment = int(i)
                    else:
                        # we are reading an address f number
                        address_f = int(i)
                        PM[PM[segment] + page] = address_f
                        if address_f != -1:
                            # update bitmap, each new page occupies 1 frame
                            update_BM(address_f)
                    count += 1
            linecount += 1



    preempt = 'NONE'


    def search_TLB(s,p):
        global LRU
        if LRU:
            for item in LRU:
                if item[1] == s and item[2] == p:
                    return item # hit
        return -1 # miss


    def update_TLB_miss(s,p,frame):
        global LRU
        if not LRU:
            # currently nothing in TLB
            LRU.append((3,s,p,frame))
        else:
            k = 4 # find the index of least recently accessed item in TLB
            k_item = None
            for item in LRU:
                if item[0] < k:
                    k = item[0]
                    k_item = item
            if len(LRU) != 4:
                for i in range(len(LRU)):
                    k_item = LRU[i]
                    LRU[i] = (k_item[0]-1, k_item[1], k_item[2], k_item[3])
                LRU.append((3,s,p,frame))
            else:
                LRU.remove(k_item) # remove the least recently accessed item in TLB
                for i in range(len(LRU)):
                    k_item = LRU[i]
                    LRU[i] = (k_item[0]-1, k_item[1], k_item[2], k_item[3])
                LRU.append((3,s,p,frame))


    def update_TLB_hit(s,p,frame):
        global LRU
        k = 4 # find the index of least recently accessed item in TLB
        k_item = None
        for item in LRU:
            if item[1] == s and item[2] == p:
                k = item[0]
                k_item = item
        LRU.remove(k_item) # remove the current item in TLB aka the one we got a hit in
        for i in range(len(LRU)):
            if i > k:
                k_item = LRU[i]
                LRU[i] = (k_item[0]-1, k_item[1], k_item[2], k_item[3])
        LRU.append((3,s,p,frame))


    with open(input_file2) as file:
        '''ASSUMING THERE IS ONLY ONE LINE'''
        linecount = 1
        for line in file:
            parseline = line.split()
            if linecount == 1: # SANITY CHECKING WE ONLY HAVE ONE LINE
                if len(parseline) % 2 != 0:
                    # checked to make sure first line is filled with pairs
                    exit(1)
                o = None # read (0) or write (1)
                VA = 0 # virtual address is a positive integer
                count = 1
                for i in parseline:
                    if count % 2 == 1:
                        o = int(i)
                    else:
                        # we are reading a virtual address
                        VA = int(i)

                        '''We are assuming that the virtual address if valid'''
                        s,p,w = VA_into_spw(VA) # breaking down of virtual address

                        TLB_capture = search_TLB(s,p) # -1 if miss, else hit
                        if TLB_capture == -1:
                            if count > 3:
                                outfile.write(" ")
                            outfile.write("m")
                        else:
                            if count > 3:
                                outfile.write(" ")
                            outfile.write("h")

                        if o == 0: # we are reading

                            # do TLB stuff first
                            if TLB_capture == -1:
                                if PM[s] == -1 or PM[PM[s] + p] == -1:
                                    preempt = 'pf'
                                elif PM[s] == 0 or PM[PM[s] + p] == 0:
                                    preempt = 'err'
                                else:
                                    preempt = str(PM[PM[s] + p] + w)
                                if preempt != 'pf' and preempt != 'err':
                                    frame = PM[PM[s] + p]
                                    update_TLB_miss(s,p,frame)
                            else: # hit
                                frame = None
                                for item in LRU:
                                    if item[1] == s and item[2] == p:
                                        frame = item[3]
                                preempt = str(frame + w)
                                update_TLB_hit(s,p,frame)
                        else: # we are writing
                            if TLB_capture != -1:
                                frame = None
                                for item in LRU:
                                    if item[1] == s and item[2] == p:
                                        frame = item[3]
                                preempt = str(frame + w)
                                update_TLB_hit(s,p,frame)
                            else: # TLB miss
                                if PM[s] == -1 or PM[PM[s] + p] == -1:
                                    preempt = 'pf'
                                else:
                                    if PM[s] == 0:
                                        # if ST entry is 0
                                        # then allocate new blank PT (all zeros)
                                        # update the ST entry accordingly
                                        # continue with translation process
                                        ST_entry = 0
                                        for i in range(1023):
                                            j = i + 1
                                            # find two empty, consecutive frames in the bitmap
                                            if (BM[int(i/32)] & MASK[i%32]) == 0 and (BM[int(j/32)] & MASK[j%32]) == 0:
                                                update_BM(i*512)
                                                update_BM(j*512)
                                                ST_entry = i*512
                                                break
                                        PM[s] = ST_entry # update the ST entry accordingly
                                    if PM[s] == -1:
                                        preempt = 'pf'
                                    elif PM[PM[s] + p] == 0:
                                        # if PT entry is 0
                                        PT_entry = 0
                                        for i in range(1024):
                                            if (BM[int(i / 32)] & MASK[i % 32]) == 0:
                                                update_BM(i*512)
                                                PT_entry = i*512
                                                break
                                        PM[PM[s] + p] = PT_entry
                                    if PM[s] != -1 and PM[PM[s] + p] != -1:
                                        preempt = str(PM[PM[s] + p] + w)
                                        if preempt == "-1":
                                            preempt = 'pf'
                                        if preempt == "0":
                                            preempt = 'err'
                                    if preempt != 'pf' and preempt != 'err':
                                        frame = PM[PM[s] + p]
                                        update_TLB_miss(s,p,frame)

                        # writing to the output file
                        outfile.write(" " + preempt)

                    count += 1

    outfile.close()
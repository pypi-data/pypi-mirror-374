##################################################################################
## StringFix - an annotation-quided genome-reconstruction and proteome assember ##
## developed by Seokhyun Yoon (syoon@dku.edu) Oct. 04, 2020                     ##
##################################################################################

import time, re, os, copy, collections, datetime, queue, math, pickle, warnings, subprocess
import numpy as np
import pandas as pd
import sklearn.linear_model as lm
from scipy import optimize 
from multiprocessing import Pool, cpu_count

try:    
    import pybam
    PYBAM_ERR = False
except ImportError:
    PYBAM_ERR = True
    pass

if PYBAM_ERR:
    try:    
        import StringFix.pybam as pybam
        PYBAM_ERR = False
    except ImportError:
        PYBAM_ERR = True
        pass

## Configuration Parameters

#####################
# Contig build param.
StringFix_version = '0.7.0'
GTF_SOURCE = 'StringFix'
MIN_CONN_DEPTH = 1       # Not used for now
MIN_LENGTH_M = 10
MIN_RD_NUM_PER_GENE = 10  
NUM_PARALLEL_CHUNKS = 8000000

#################
# Trimming param.
MAX_DEV_NM = 20            
MAX_CFRAC_N_COMB = 0.02  # get_connection_mat()
MAX_CVG_N_COMB = 10      # get_connection_mat()
MAX_DEV_N = 1            # trim_contigs   
MAX_DEV_D = 15           # trim_contigs     
MAX_DEV_I = 15           # trim_contigs   
R_VALID_CVG = 3.2        # rem_low_cvg_rgns()
R_VALID_CFRAC = 0.002    # rem_low_cvg_rgns()
N_VALID_CVG = 1       
N_VALID_CFRAC = 0.01     # Not used 
I_VALID_CVG = 1.5      
I_VALID_CFRAC = 0.1    
D_VALID_CVG = 1.5      
D_VALID_CFRAC = 0.1  
MAX_INTRON_LENGTH = 150000

#####################
# splice graph param.
MAX_DIST_UC_TO_CONN = 50 
MAX_DIST_UC = 1000 # MAX_DIST_UC_TO_CONN*8  

###########################
## graph prunning param.
## select_nodes_and_edges()
MAX_NUM_PATHS_INIT = 200
MAX_NUM_PATHS = 20

MAX_BYPASS_CFRAC = 0.02  
MAX_BYPASS_DEPTH = 10    
MAX_BYPASS_LENGTH = 200  

MAX_PRUNING_DEPTH = 1  
MAX_PRUNING_LENGTH = 100
MAX_PRUNING_CFRAC = 0.02

##################
# td_and_ae param.
MIN_ISO_FRAC_SIC = 0.02
NUM_TRS_MULT = 1.2
MIN_ALPHA_FOR_EN = 0.0001
NOMINAL_L1_RATIO = 0.5
MIN_START_END_LENGTH = 20
MAX_PERCENT_SEC = 1

##########################
## td_and_ae - GTF guided 
MIN_COV_TO_SEL = 0.5
MIN_ABN_TO_SEL = 1
MIN_N_RDS_PER_GENE = 10
MIN_ISO_FRAC = 0.01
MIN_TR_LENGTH = 200
MIN_PR_LENGTH = 50
GEN_AAS_UNSPEC = True
MIN_CVG_FOR_SNP_CORRECTION = 3

TR_FILTER_SEL = 1
MAX_NUM_HOPS = 100
CVG_DEPTH_TMP = 0.001

## Data structure
'''
SAM_line = collections.namedtuple('SAM_line', 'qname, flag, flag_str, rname, pos, mapq, cigar, \
                                   rnext, pnext, tlen, seq, qual, cN, cD, cI, cS, xs')
QNAME, FLAG, FLAG_STR, RNAME, POS, MAPQ, CIGAR, RNEXT, PNEXT, TLEN, SEQ, QUAL, CN, CD, CI, CS = [i for i in range(16)]
'''
SAM_line = collections.namedtuple('SAM_line', 'qname, flag_str, rname, pos, mapq, cigar, \
                                   rnext, pnext, tlen, seq, qual, xs')
QNAME, FLAG_STR, RNAME, POS, MAPQ, CIGAR, RNEXT, PNEXT, TLEN, SEQ, QUAL, XS = [i for i in range(12)]

Transcript = collections.namedtuple('Transcript', \
                                    'prefix, gidx, grp_size, icnt, chr, start, end, \
                                     strand, cdng, seq, abn, tpm, iso_frac, prob, nexs, gvol')

'''
Transcript = collections.namedtuple('Transcript', \
                                    'prefix, gidx, grp_size, icnt, chr, start, end, \
                                     strand, cdng, seq, abn, tpm, iso_frac, prob, nexs, gvol')
'''

# GTF_line = collections.namedtuple('GTF_line', 'chr, src, feature, start, end, score, strand, frame, attr, name, ext, note')

## Constants
PREFIX, GIDX, GSIZE, ICNT, CHR, TSTART, TEND, TSTRAND, TCDNG, TSEQ, ABN, TPM, ISO_FRAC, PROB, NEXS = [i for i in range(15)]

'''
=============================================================================
SAM flag
=============================================================================
0   1     0x1    template having multiple segments in sequencing
1   2     0x2    each segment properly aligned according to the aligner

2   4     0x4    segment unmapped
3   8     0x8    next segment in the template unmapped
4   16    0x10   SEQ being reverse complemented
5   32    0x20   SEQ of the next segment in the template being reverse complemented
6   64    0x40   the first segment in the template
7   128   0x80   the last segment in the template

8   256   0x100  secondary alignment
9   512   0x200  not passing filters, such as platform/vendor quality controls
10  1024  0x400  PCR or optical duplicate
11  2048  0x800  supplementary alignment
=============================================================================
'''

def get_flag(values, bpos ):
    mask = np.repeat( 1 << bpos, len(values) )
    flag = (values & mask) > 0
    return(list(flag))


def get_col(nt_lst, n):
    
    lst = []
    for item in nt_lst: lst.append(item[n]) 
    return(lst)


def fline_cnt( fname ):
    count = 0.
    
    with open(fname, 'r') as f:
        for line in f:
            count += 1
    return(count)

def load_fasta1(file_genome, verbose = False ):

    if verbose: print('\rLoading FASTA .. ', end='', flush=True)
    hdr_lst = []
    full_seq_lst = []
    f = open(file_genome, 'r')
    cnt = 0
    header = None
    seq_lst = []
    for line in f :
        if line[0] == '>':
            # print('\r', line[1:-1], end='       ')
            if cnt > 0: 
                # genome.append( Genome(header, ''.join(seq_lst) ) )
                hdr_lst.append(header)
                full_seq_lst.append(''.join(seq_lst))
            cnt += 1
            header = line[1:-1]
            seq_lst = []
        else :
            seq_lst.append(line[:-1].upper())

    # genome.append( Genome(header, ''.join(seq_lst) ) )
    if header is not None: hdr_lst.append(header)
    full_seq_lst.append(''.join(seq_lst))
    if verbose: print('\rNum.entries = ', cnt, ' loaded                             ')
    f.close()
    return hdr_lst, full_seq_lst


class Genome:
    def __init__(self, header, seq, qual = None ):
        self.name = header.split()[0]
        self.header = header
        self.seq = seq
        self.len = len(seq)
        self.qual = qual
        self.cov = -1
        self.abn = -1
        self.tpm = -1

    def get_attr(self):
        items = self.header.split()
        for item in items:
            nv = item.split(':')
            if len(nv) == 2:
                (name, value) = nv
                if name == 'cov_frac': self.cov = np.float32(value)
                elif name == 'abn': self.abn = np.float32(value)
                elif name == 'tpm': self.tpm = np.float32(value)
            


def load_genome(file_genome, verbose = False ):

    genome = dict()
    f = open(file_genome, 'r')
    cnt = 0
    if verbose == True : print('\rLoading sequence .. ', end='', flush=True)
    seq_lst = []
    lcnt = 0
    for line in f :
        if line[0] == '>':
            if verbose == True : print('\rLoading sequence .. ', line[1:-1].split(' ')[0], end='                                   ')
            if cnt > 0: 
                # genome.append( Genome(header, ''.join(seq_lst) ) )
                chr_name = header.split()[0]
                genome[chr_name] = Genome(header, ''.join(seq_lst) )
                genome[chr_name].get_attr()
            cnt += 1
            header = line[1:-1]
            seq_lst = []
        else :
            seq_lst.append(line[:-1].upper())
        lcnt += 1

    # genome.append( Genome(header, ''.join(seq_lst) ) )
    if cnt > 0:
        chr_name = header.split()[0]
        genome[chr_name] = Genome(header, ''.join(seq_lst) )
    if verbose == True : print('\rLoading sequence .. done.  Num.Seq = ', cnt, '                                 ', flush=True)
    f.close()
    return(genome)


def save_genome( file_genome, genome_dict, verbose = False, title = 'genome' ):
    N = 50
    dN = 1/N
    print('Saving %s ..' % title, end='', flush=True)
    # for g in genome_lst :
    Keys = genome_dict.keys()
    f = open(file_genome, 'wt+')
    for kk, key in enumerate(Keys):
        print('\r' + ' '*100, end='')
        print('\rSaving %s .. %s ' % (title, key), end='')
        line_lst = []
        g = genome_dict[key]
        s = '>%s\n' % g.header
        # f.writelines(s)
        line_lst.append(s)
        g.len = len(g.seq)
        n_f = g.len/N
        n = int(n_f)
        r = n_f - n
        for m in range(n):
            s = '%s\n' % g.seq[(m*N):((m+1)*N)]
            # f.writelines(s)
            line_lst.append(s)
        if (r > 0) | (len(g.seq[(n*N):]) > 0):
            s = '%s\n' % g.seq[(n*N):]    
            line_lst.append(s)
            if len(g.seq[(n*N):]) > N:
                print('ERROR in save_genome: %i > %i ' % (len(g.seq[(n*N):]), N ))
        # f.writelines(s)
        f.writelines(''.join(line_lst))
        if verbose: print('.', end='', flush=True)
        
    # f.writelines(''.join(line_lst))
    print('\rSaving %s .. done. (%i)                ' % (title, len(Keys)), flush=True)
    f.close()
    

def load_fasta(file_genome, verbose = False ):

    genome = dict()
    f = open(file_genome, 'r')
    cnt = 0
    print('\rLoading sequence .. ', end='', flush=True)
    seq_lst = []
    for line in f :
        if line[0] == '>':
            # print('\rLoading sequence .. ', end='         ')
            if cnt > 0: 
                # genome.append( Genome(header, ''.join(seq_lst) ) )
                chr_name = header.split()[0]
                genome[chr_name] = Genome(header, ''.join(seq_lst) )
                genome[chr_name].get_attr()
            cnt += 1
            header = line[1:-1]
            seq_lst = []
        else :
            seq_lst.append(line[:-1].upper())

    # genome.append( Genome(header, ''.join(seq_lst) ) )
    chr_name = header.split()[0]
    genome[chr_name] = Genome(header, ''.join(seq_lst) )
    print('\rLoading sequence .. done.  Num.Seq = ', cnt, '   ', flush=True)
    f.close()
    return(genome)


def save_fasta( file_genome, genome_dict, verbose = False, title = 'seq.' ):

    print('Saving %s ..' % title, end='', flush=True)
    # for g in genome_lst :
    Keys = genome_dict.keys()
    f = open(file_genome, 'wt+')
    line_lst = []
    for key in Keys:
        # print('\rSaving %s .. %s' % (title, key), end='                    ')
        g = genome_dict[key]
        s = '>%s\n' % g.header
        line_lst.append(s)
        line_lst.append(g.seq+'\n')
        if verbose: print('.', end='', flush=True)

    f.writelines(''.join(line_lst))
        
    print('\rSaving %s .. done. (%i)                ' % (title, len(Keys)), flush=True)
    f.close()
    

def load_sam_lst( fname, n_rd_max = None, verbose = False, sdiv = 10 ):
    
    # chr_lst = list()
    # pos_lst = list()
    # qname_lst = list()
    # rgns_lst = list()
    
    slns = list()
    bytesize = os.path.getsize(fname)
    lines = []
    
    if verbose == True:
        print('Reading ',fname, ' ',end='')
        start_time = time.time()

    cN = 0
    cD = 0
    cI = 0
    cS = 0
    rd_len = 0
    cnt = 0
    n_bases = 0
    cnt_byte = 0
    qual = ' '
    flag_str = ' '
    step = np.ceil(bytesize/sdiv)
    ms = step;
    f = open(fname, 'r')
    while True:
        lines = f.readlines(1000)
        if not lines: break
        for line in lines : # range(len(x)) :
            cnt_byte += len(line)
            if line[0] != '@':
                items = line[:-1].split()
                flag_str = format(int(items[1])+4096, 'b')[::-1]
                pri = flag_str[8]

                if (pri == '0') & (items[2] != '*') & (items[5] != '*'):
                    qname = items[0]
                    flag = np.int(items[1])
                    rname = items[2]
                    pos = np.int(items[3])
                    mapq = np.int(items[4])
                    cigar = items[5]
                    rnext = items[6]
                    pnext = np.int(items[7])
                    tlen = np.int(items[8])
                    seq = items[9].upper()

                    XS = 0
                    if len(items) > 11:
                        if items[11][5] == '+': XS = 1
                        elif items[11][5] == '-': XS = -1
                    # qual = items[10]

                    '''
                    cN = np.int(cigar.count('N'))
                    cD = np.int(cigar.count('D'))
                    cI = np.int(cigar.count('I'))
                    cS = np.int(cigar.count('S'))
                    '''

                    sam_line = SAM_line( qname, flag, flag_str, rname, pos, mapq, cigar, rnext, pnext, \
                                        tlen, seq, qual, cN, cD, cI, cS, XS )
                    slns.append( sam_line )

                    # chr_lst.append(rname)
                    # pos_lst.append(pos)
                    # qname_lst.append(qname)
                    # r = get_rgns_from_sam_line( sam_line )
                    # rgns_lst.append(r)

                    cnt += 1
                    n_bases += len(seq)
                    rd_len = max(rd_len,len(seq))

                    if cnt == n_rd_max :
                        break
            else:
                # if verbose == True: print(line[:-1])
                pass

            if (verbose == True) & (cnt_byte > ms): 
                elapsed_time = time.time() - start_time
                print('.', end='')
                ms += step
            
        if cnt == n_rd_max :
            break
            
    f.close()
    if verbose == True: 
        # elapsed_time = time.time() - start_time
        if n_rd_max is None:
            print(' done. %i (%i) lines (bases), read length: %i' % (cnt, n_bases, rd_len))
        else:
            print(' done. read length: %i, %i' % (rd_len, cnt))
    
    return( slns, cnt, n_bases, rd_len )


def rename(sam_line_lst):
    Len = len(sam_line_lst)
    print('Len:', Len)
    for k in range(int(Len/2)):
        qname = sam_line_lst[k*2]
        sam_line_lst[k*2+1].qname = qname
        
    return(sam_line_lst)


def which( ai, value = True ) :
    wh = []
    a = list(ai)
    for k in range(len(a)): 
        if a[k] == value: 
            wh.append(k) 
    return(wh)

def parse_cigar( cigar_str ):
    matches = re.findall(r'(\d+)([A-Z]{1})', cigar_str)
    return(matches)

def compare_seq( s1, s2 ):
    cnt = 0
    mcnt = 0
    for k in range(len(s1)):
        if (s1[k] != ' ') & (s2[k] != ' '): 
            cnt += 1
            mcnt += (s1[k] != s2[k])
    return((mcnt,cnt))

def get_error_seq( s1, s2 ):
    cnt = 0
    mcnt = 0
    es = []
    for k in range(len(s1)):
        if (s1[k] != ' ') & (s2[k] != ' '): 
            cnt += 1
            mcnt += (s1[k] != s2[k])
            if s1[k] != s2[k]: es.append('e')
            else: es.append('_')
        elif (s1[k] == ' ') & (s2[k] != ' '): es.append('d')
        elif (s1[k] != ' ') & (s2[k] == ' '): es.append('x')
        else:
            es.append('_')
    return(''.join(es))

def get_seq_from_genome_o2(genome, sam_line):
    type_cnt = dict(D=0,I=0,N=0,S=0)
    Len = len(sam_line.seq) -1
    cigar = parse_cigar(sam_line.cigar)
    rseq = ''
    rpos = 0
    qseq = ''
    qpos = sam_line.pos-1
    for clen, ctype in cigar:
        if (ctype == 'D') | (ctype == 'I') | (ctype == 'N') | (ctype == 'S') :
            type_cnt[ctype] += 1
        # print(ctype,clen)
        Len = int(clen)
        if ctype == 'M': 
            qseq = qseq + genome[sam_line.rname].seq[qpos:(qpos+Len)]
            qpos += Len
            rseq = rseq + sam_line.seq[rpos:(rpos+Len)]
            rpos += Len
        elif ctype == 'S': 
            tseq = ''
            for n in range(Len): tseq = tseq + ' '
            qseq = qseq + tseq
            rseq = rseq + sam_line.seq[rpos:(rpos+Len)]
            rpos += Len
        elif ctype == 'N': 
            qpos += Len
        elif ctype == 'I': 
            tseq = ''
            for n in range(Len): tseq = tseq + ' '
            qseq = qseq + tseq
            rseq = rseq + sam_line.seq[rpos:(rpos+Len)]
            rpos += Len
        elif ctype == 'D': 
            tseq = ''
            for n in range(Len): tseq = tseq + ' '
            rseq = rseq + tseq
            qseq = qseq + genome[sam_line.rname].seq[qpos:(qpos+Len)]
            qpos += Len
        elif ctype == 'H': # No action
            pass
        elif ctype == 'P': # No action
            pass
        elif ctype == '=': # No action
            pass
        elif ctype == 'X': # No action
            pass
        else: 
            return(False, rseq, qseq, type_cnt)
            
    return(True, rseq, qseq, type_cnt)


##########################################################################
## Functions to handle Cmat
##########################################################################

NT_lst = 'ACGTN'
NT_dict = { 'A':0, 'C':1, 'G':2, 'T':3, 'N':4, 'U': 3, '*':4 }

def NTstr2NumSeq( nt_str ) :
    num_seq = np.array( [NT_dict[nt] for nt in nt_str] )
    return(num_seq)

def NumSeq2NTstr( num_seq ) :
    nt_str = ''.join([NT_lst[n] for n in num_seq])
    return(nt_str)

def NTstr2CMat_old( nt_str ) :
    
    # nn = np.int8(nt_str.count('N'))
    ns = NTstr2NumSeq( nt_str )
    cm = np.zeros([5,len(nt_str)], dtype=np.float32)
    for k in range(len(nt_str)) : cm[ns[k],k] = 1        
    return( cm )
    # return( cm[0:-1,0:] )

def NTstr2CMat( nt_str ) :
    
    # nn = np.int8(nt_str.count('N'))
    cm = np.zeros([5,len(nt_str)], dtype=np.float32)
    for k in range(len(nt_str)) : cm[NT_dict[nt_str[k]],k] = 1       
    return( cm )
    # return( cm[0:-1,0:] )

def CMat2NTstr( cmat ) :
    
    ns = np.argmax( cmat, axis=0 )
    cvg = np.sum( cmat, axis=0 )
    # wh = which(cvg,0)
    # if len(wh) > 0: ns[wh] = 4
    ns[cvg == 0] = 4
    nt_str = NumSeq2NTstr( ns )
    
    return( nt_str )

def CMat2NTstr_with_CVG( cmat ) :
    
    ns = np.argmax( cmat, axis=0 )
    cvg = np.sum( cmat, axis=0 )
    # wh = which(cvg,0)
    # if len(wh) > 0: ns[wh] = 4
    ns[cvg == 0] = 4
    nt_str = NumSeq2NTstr( ns )
    
    return( nt_str, cvg )

def get_cvg( cmat ) :
    
    cvg = np.sum( cmat, axis=0 )
    return( cvg )

def get_majority_cnt( cmat ) :
    
    cvg = np.max( cmat, axis=0 )
    return( cvg )

def merge_seq_to_cmat( cm1, pos, nt_str ) :
    
    l1 = cm1.shape[1]
    l2 = len(nt_str)
    
    if pos >= 0 :  ## Ref = cm2
        if l2 <= (l1-pos):
            # cm1[:,pos:(pos+l2)] = cm1[:,pos:(pos+l2)] + (cm2)
            for k in range(l2) : cm1[NT_dict[nt_str[k]],pos+k] += 1 
            return(cm1)
        else:
            cm = np.zeros( [cm1.shape[0],l2+pos], dtype=np.float32);
            cm[:,:l1] = (cm1)
            # cm[:,pos:] = cm[:,pos:] + (cm2)
            for k in range(l2) : cm[NT_dict[nt_str[k]],pos+k] += 1 
            return(cm)
        
    else :  ## Ref = cm2
        pos = -pos
        if l1 <= (l2-pos):
            cm = NTstr2CMat( nt_str )
            cm[:,pos:(pos+l2)] = cm[:,pos:(pos+l2)] + (cm1)
            return(cm2)
        else:
            cm = np.zeros( [cm1.shape[0],l1+pos], dtype=np.float32);
            # cm[:,:l2] = (cm2)
            for k in range(l2) : cm[NT_dict[nt_str[k]],k] += 1 
            cm[:,pos:] = cm[:,pos:] + (cm1)
            return(cm)

def merge_cmat( cm1, pos, cm2 ) :
    
    l1 = cm1.shape[1]
    l2 = cm2.shape[1]
    
    if pos >= 0 :  ## Ref = cm2
        if l2 <= (l1-pos):
            cm1[:,pos:(pos+l2)] = cm1[:,pos:(pos+l2)] + (cm2)
            return(cm1)
        else:
            cm = np.zeros( [cm1.shape[0],l2+pos], dtype=np.float32);
            cm[:,:l1] = (cm1)
            cm[:,pos:] = cm[:,pos:] + (cm2)
            return(cm)
        
    else :  ## Ref = cm2
        pos = -pos
        if l1 <= (l2-pos):
            cm2[:,pos:(pos+l2)] = cm2[:,pos:(pos+l2)] + (cm1)
            return(cm2)
        else:
            cm = np.zeros( [cm1.shape[0],l1+pos], dtype=np.float32);
            cm[:,:l2] = (cm2)
            cm[:,pos:] = cm[:,pos:] + (cm1)
            return(cm)

def merge_cmat2( cm1, pos, cm2 ) :
    
    l1 = cm1.shape[1]
    l2 = cm2.shape[1]
    
    if pos >= 0 :  ## Ref = cm2
        if l2 <= (l1-pos):
            cm1[:,pos:(pos+l2)] = cm1[:,pos:(pos+l2)] + (cm2)
        else:
            print('ERROR in merge_cmat2(A)')
        
    else :  ## Ref = cm2
        pos = -pos
        if l1 <= (l2-pos):
            cm2[:,pos:(pos+l2)] = cm2[:,pos:(pos+l2)] + (cm1)
            return(cm2)
        else:
            print('ERROR in merge_cmat2(B)')

def merge_cvg( cvg1, pos, cvg2 ) :
    
    l1 = len(cvg1)
    l2 = len(cvg2)
    
    if pos >= 0 :  ## Ref = cm2
        if l2 <= (l1-pos):
            # cvg = (cvg1);
            # cvg[pos:(pos+l2)] = cvg[pos:(pos+l2)] + cvg2
            cvg1[pos:(pos+l2)] = cvg1[pos:(pos+l2)] + cvg2
            return(cvg1)
        else:
            cvg = np.zeros( l2+pos, dtype=np.float32);
            cvg[:l1] = cvg1
            cvg[pos:] = cvg[pos:] + cvg2
            return(cvg)
        
    else :  ## Ref = cm2
        pos = -pos
        if l1 <= (l2-pos):
            # cvg = (cvg2);
            # cvg[pos:(pos+l2)] = cvg[pos:(pos+l2)] + cvg1
            cvg2[pos:(pos+l2)] = cvg2[pos:(pos+l2)] + cvg1
            return(cvg2)
        else:
            cvg = np.zeros( l1+pos, dtype=np.float32);
            cvg[:l2] = cvg2
            cvg[pos:] = cvg[pos:] + cvg1
            return(cvg)


##########################################################################
## regions objects
##########################################################################

class Region:
    def __init__(self, chr = None, start = None, end = None, align_type = None, seq = None, xs = 0 ):
        self.obj_type = 'rgn'
        self.chr = chr
        self.start = start
        self.end = end
        self.type = align_type
        self.xs = xs
        
    def print(self):
        print(self.chr,'(',self.type,')',':',self.start,'~',self.end, '(',(self.end)-(self.start)+1,')')

    def copy(self):
        rgn = region(self.chr, self.start, self.end, self.type)
        return( rgn )
    
    def isempty(self):
        if (self.chr is None) | (self.start is None) | (self.end is None) :
            return(True)
        else: return(False)
        
    def get_seq(self):
        seq = ''
        return(seq)
    
    def does_contain(self, rgn):
        if (rgn.start > self.start) & (rgn.end < self.end): loc = True
        else: loc = False
        return(loc)
    
    def contain(self,pos):
        if (pos > self.start) & (pos < self.end): loc = pos - self.start
        else: loc = -1
        return(loc)
    
    def contain_i(self,pos):
        if (pos >= self.start) & (pos <= self.end): loc = pos - self.start
        else: loc = -1
        return(loc)
    
    def get_len(self):
        return( self.end-self.start+1 )
    
    def has_intersection_with(self, a_rng, max_dev = 0):
        if (self.chr is None) | (a_rng.chr is None) | (a_rng.chr != self.chr):
            return(False)
        else:
            if (a_rng.type == 'M') & (self.type == 'M'):
                if (a_rng.start >= self.start):
                    if a_rng.start <= self.end:
                        return(True)
                    else: # a_rng.start > self.end
                        return(False)
                else: # a_rng.start < self.start
                    if a_rng.end >= self.start:
                        return(True)
                    else: # a_rng.end < self.start
                        return(False)
                    
            elif ((a_rng.type == 'I') & (self.type == 'I')) :
                b = False
                if (a_rng.start == self.start) & (a_rng.end == self.end): b = True
                # else: # a_rng.start > self.end
                '''
                if (abs(a_rng.start-self.start) <= abs(self.end-self.start)) & \
                   (abs(a_rng.end-self.end) <= abs(self.end-self.start)) :
                    print('Possible Intersection of Type:', self.type, \
                          '(%d-%i), (%d-%i)' % (self.start, self.end, a_rng.start, a_rng.end) )
                '''
                return(b)
                
            elif ((a_rng.type == 'D') & (self.type == 'D')) :
                #if (abs(self.start-a_rng.start) <= max_dev) & \
                #   (abs(self.end-a_rng.end) <= max_dev): \
                if (a_rng.start == self.start) & (a_rng.end == self.end):
                    return(True)
                else:
                    return(False)
                
                
            elif ((a_rng.type == 'N') & (self.type == 'N')) :
                b = False
                # if (abs(self.start-a_rng.start) <= max_dev) & \
                #    (abs(self.end-a_rng.end) <= max_dev): \
                if (a_rng.start == self.start) & (a_rng.end == self.end):
                   # (abs(self.end-self.start) <= abs(a_rng.end-a_rng.start)): \
                    b = True
                return(b)
                
            elif ((a_rng.type == 'S') & (self.type == 'S')) | ((a_rng.type == 'T') & (self.type == 'T')) :
                ### Note used
                return(False)
            
            elif ((a_rng.type == 'D') & (self.type == 'M')) | ((a_rng.type == 'M') & (self.type == 'D')):
                if (a_rng.start >= self.start):
                    if a_rng.start <= self.end:
                        return(True)
                    else: # a_rng.start > self.end
                        return(False)
                else: # a_rng.start < self.start
                    if a_rng.end >= self.start:
                        return(True)
                    else: # a_rng.end < self.start
                        return(False)
            elif (self.type is None) | (a_rng.type is None):
                if (a_rng.start >= self.start):
                    if a_rng.start <= self.end:
                        return(True)
                    else: # a_rng.start > self.end
                        return(False)
                else: # a_rng.start < self.start
                    if a_rng.end >= self.start:
                        return(True)
                    else: # a_rng.end < self.start
                        return(False)
            else:
                return False
    
    def has_ext_intersection_with(self, a_rng, max_dev = 0):
        if (self.chr is None) | (a_rng.chr is None) | (a_rng.chr != self.chr):
            return(False)
        else:
            if (a_rng.start >= self.start):
                if a_rng.start <= self.end:
                    return(True)
                else: # a_rng.start > self.end
                    return(False)
            else: # a_rng.start < self.start
                if a_rng.end >= self.start:
                    return(True)
                else: # a_rng.end < self.start
                    return(False)
                    
                    
    def is_the_same_as(self, a_rng): # assume intersection
        b = False
        if self.chr == a_rng.chr:
            if self.type == a_rng.type:
                if (self.start == a_rng.start) & (self.end == a_rng.end): b = True
        return b
        
    def get_union(self, a_rng): # assume intersection
        if self.chr == a_rng.chr:
            start = min(self.start,a_rng.start)
            end = max(self.end,a_rng.end)
            if (self.start <= a_rng.end) & (a_rng.start <= self.end):
                return start, end 
            else:
                return 1, 0
        else:
            return 1, 0
        
    def get_intersection(self, a_rng): # assume intersection
        if self.chr == a_rng.chr:
            start = max(self.start,a_rng.start)
            end = min(self.end,a_rng.end)
            if start <= end:
                return start, end 
            else: 
                return 1, 0
        else:
            return 1,0
        
    def get_overlap_len(self, a_rng): # assume intersection
        s, e = self.get_intersection(a_rng)
        return( e-s+1 )
        
    def update(self, a_rng):
        if (self.chr is None) | (a_rng.chr is None) | (a_rng.chr != self.chr):
            return(False)
        else:
            if self.has_intersection_with(a_rng) == True: # (a_rng.start >0) & (a_rng.end >0) & (self.start >0) & (self.end >0):
                self.start, self.end = self.get_union(a_rng)
                return(True)
            else:
                return(False)

            
class Region_ext(Region):

    def __init__(self, chr = None, start = None, end = None, align_type = None, seq_or_cmat = '', \
                 cvg_dep = 1, cm = True, xs = 0 ):
        super(Region_ext, self).__init__( chr, start, end, align_type, xs=xs )
        if isinstance(seq_or_cmat,str) == True:
            self.seq = seq_or_cmat
            if cm: 
                if cvg_dep == 0:
                    Len = end - start + 1
                    self.cmat = np.zeros([5,Len], dtype=np.float32)
                else:
                    self.cmat = NTstr2CMat( seq_or_cmat ) 
                    if cvg_dep != 1: self.cmat = self.cmat*cvg_dep
            else:
                self.cmat = None
        else:
            self.cmat = seq_or_cmat
            self.seq = CMat2NTstr( self.cmat )
            if cvg_dep != 1: self.cmat = self.cmat*cvg_dep
        self.cvg = None
        self.ave_cvg = cvg_dep

        self.cov_len = -1
        self.cvg_frac = -1

        # self.cvg = self.get_cvg()  
        # self.ave_cvg = self.set_ave_cvg_depth()

    def convert_to_text_lines(self, sn, N, n ):
        lines = []
        hdr = '>%i\t%i\t%i\t%s\t%i\t%i\t%s\t%i\n' % (sn, N, n+1, self.chr, self.start, self.end, self.type, self.xs)
        lines.append(hdr)
        seq = self.get_seq() + '\n'
        lines.append(seq)
        for k in range(5):
            line = ''
            for m in range(len(seq)-2): line = line + ('%i\t' % self.cmat[k,m])
            line = line + ('%i\n' % self.cmat[k,len(seq)-2])
            lines.append(line)
        if (self.end-self.start+1) != (len(seq)-1):
            print('ERROR in Region_ext::convert_to_text_lines(): %i != %i' % ((self.end-self.start+1), (len(seq)-1)) )
        return(lines)
    
    def set_from_text_lines(self, lines ):
        b = True
        if len(lines) < 7:
            print('ERROR in Region_ext::set_from_text_lines()')
            b = False
        else:
            items = lines[0][1:-1].split()
            sn = int(items[0])
            N = int(items[1])
            n = int(items[2])
            self.chr = items[3]
            self.start = int(items[4])
            self.end = int(items[5])
            self.type = items[6]
            self.xs = int(items[7])
            seq = lines[1][:-1]
            self.cmat = np.zeros([5,len(seq)], dtype=np.float32)
            for k in range(5):
                items = lines[k+2][:-1].split()
                for m in range(len(seq)):
                    self.cmat[k,m] = items[m] # np.int32(items[m])
            self.cvg = self.get_cvg() 
            # self.ave_cvg = self.set_ave_cvg_depth()
            if self.end >= self.start:
                if (self.end-self.start+1) != len(seq):
                    print('ERROR in Region_ext::set_from_text_lines(): %i != %i, %i' % ((self.end-self.start+1), len(seq), len(items) ) )
                    print(lines[0][:-1])
                    print(seq)
                    print(lines[1])
            
        return(b)
    
            
    def get_volume(self):
        if len(self.cvg) > 0:
            vol = np.sum( self.cvg )
            return(int(vol))
        else:
            return(int(0))
        
    def get_cov(self):
        self.get_cvg()
        if len(self.cvg) > 0:
            return ((len(self.cvg) - self.get_seq().count('N'))/len(self.cvg))
        else:
            return(int(0))
        
    def set_ave_cvg_depth(self):
        if len(self.cvg) > 0:
            self.ave_cvg = np.mean( self.cvg )
            return((self.ave_cvg))
        else:
            self.ave_cvg = 0
            return(0)
    
    def med_cvg_depth(self):
        if len(self.cvg) > 0:
            mcvg = np.median( self.cvg )
            return(mcvg)
        else:
            return(0)
    
    def ave_cvg_depth(self):
        '''
        if len(self.cvg) > 0:
            mcvg = np.mean( self.cvg )
            return(round(mcvg,2))
        else:
            return(0)
        '''
        return(self.ave_cvg)
    
    def cvg_depth_start(self):
        if len(self.cvg) > 0:
            return(round(self.cvg[0],2))
        else: return(0)
    
    def cvg_depth_end(self):
        if len(self.cvg) > 0:
            return(round(self.cvg[-1],2))
        else: return(0)
        
    def get_cov_len(self):
        cnt_n = self.seq.count('N')
        self.cov_len = len(self.seq) - cnt_n
        return self.cov_len
        
    def get_seq(self):
        self.seq = CMat2NTstr( self.cmat )
        return(self.seq)
    
    def get_seq2(self):
        self.seq = CMat2NTstr( self.cmat[:4,:] )
        return(self.seq)
    
    def get_cvg(self):
        self.seq, self.cvg = CMat2NTstr_with_CVG( self.cmat )
        self.ave_cvg = self.set_ave_cvg_depth()
        return(self.cvg)
    
    def get_seq_n_cvg(self):
        self.seq, self.cvg = CMat2NTstr_with_CVG( self.cmat )
        self.ave_cvg = self.set_ave_cvg_depth()
        return((self.seq, self.cvg))
    
    def print(self):
        if self.xs == 0: st = ' '
        else: st = ' {0:+}'.format(self.xs)
        print('CHR:',self.chr,'(',self.type, st,')',':',self.start,'~',self.end, '(',abs(self.end)-abs(self.start)+1,',', \
              '%4.1f' % (self.ave_cvg_depth()), ') ', CMat2NTstr( self.cmat ))
        
    def print_short(self):
        seq = CMat2NTstr( self.cmat )
        if self.xs == 0: st = ' '
        else: st = ' {0:+}'.format(self.xs)
        if self.get_len() > 34:
            half_len = int(self.get_len()/2)
            # print(self.chr,'(',self.type,')',':',self.start,'~',self.end, '(',abs(self.end)-abs(self.start)+1,',', \
            #       '%4.1f' % self.ave_cvg_depth(),') ', seq[:min(20,half_len)], '...', seq[-min(20,half_len):])
            print(self.chr,'(',self.type, st,')',':',self.start,'~',self.end, '(',abs(self.end)-abs(self.start)+1,',', \
                  '%4.1f' % (self.ave_cvg_depth()),') ', 'CF: %5.3f' % self.cvg_frac, seq[:min(16,half_len)], '...', seq[-min(16,half_len):])
        else:
            print(self.chr,'(',self.type, st,')',':',self.start,'~',self.end, '(',abs(self.end)-abs(self.start)+1,',', \
                  '%4.1f' % (self.ave_cvg_depth()),') ', 'CF: %5.3f' % self.cvg_frac, seq)
        
    def print_minimal(self):
        if self.xs == 0: st = ' '
        else: st = ' {0:+}'.format(self.xs)
        print(self.chr,'(',self.type, st,')',':',self.start,'~',self.end, '(',abs(self.end)-abs(self.start)+1,') ', 'CF: %5.3f' % self.cvg_frac )
        

    def print_short2(self):
        seq = CMat2NTstr( self.cmat )
        if self.xs == 0: st = ' '
        else: st = ' {0:+}'.format(self.xs)
        if self.get_len() > 60:
            ss = ''
            step = len(self.seq)/60.0
            # kk = np.zeros(60, dtype = np.int)
            for k in range(60):
                # kk[k] = int(step*k+17)
                ss = ss + self.seq[min(int(step*k+step/2),len(self.seq)-1)]

            half_len = int(self.get_len()/2)
            print(self.chr,'(',self.type, st,')',':',self.start,'~',self.end, '(',abs(self.end)-abs(self.start)+1,',', \
                  '%4.1f' % (self.ave_cvg_depth()),') ', 'CF: %5.3f' % self.cvg_frac, ss)
        else:
            print(self.chr,'(',self.type, st,')',':',self.start,'~',self.end, '(',abs(self.end)-abs(self.start)+1,',', \
                  '%4.1f' % (self.ave_cvg_depth()),') ', 'CF: %5.3f' % self.cvg_frac, seq)
        
    def print_cvg(self):
        if self.xs == 0: st = ' '
        else: st = ' {0:+}'.format(self.xs)
        cvg_s = ''
        step = (len(self.seq))/10.0
        for k in range(10):
            ac = self.cvg[int(k*step):min(int((k+1)*step), len(self.seq))].mean()
            cvg_s = cvg_s + ' %6.2f,' % ac
            
        print(self.chr,'(',self.type, st,')',':',self.start,'~',self.end, '(',abs(self.end)-abs(self.start)+1,') ', cvg_s)
        
    def copy(self, update = True):
        
        if update: 
            rgn_ext = Region_ext(self.chr, self.start, self.end, self.type, np.copy(self.cmat), xs=self.xs)
            rgn_ext.get_cvg()
            # rgn_ext.cmat = np.copy(self.cmat)
            # rgn_ext.cvg = np.copy(self.cvg)
            # rgn_ext.ave_cvg = np.mean(rgn_ext.cvg)
        else:
            rgn_ext = Region_ext(self.chr, self.start, self.end, self.type, xs=self.xs)
            rgn_ext.seq = self.seq
            rgn_ext.ave_cvg = self.ave_cvg

        rgn_ext.cov_len = self.cov_len
        rgn_ext.cvg_frac = self.cvg_frac
            
        return( rgn_ext )
    
    def update(self, a_rng, cm=True):
        if (a_rng.chr != self.chr) | (a_rng.type != self.type): # (self.chr is None) | (a_rng.chr is None) | (a_rng.chr != self.chr):
            return(False)
        else:
            if self.has_intersection_with(a_rng) == True: 
                if cm:
                    if self.cmat is None: self.cmat = NTstr2CMat( self.seq )*self.ave_cvg 
                    
                    if a_rng.cmat is None:
                        # self.cmat = merge_seq_to_cmat( self.cmat, a_rng.start-self.start, a_rng.seq )
                        #'''
                        cmat = NTstr2CMat( a_rng.seq )*a_rng.ave_cvg
                        if self.start <= a_rng.start:
                            self.cmat = merge_cmat( self.cmat, a_rng.start-self.start, cmat )
                        else:
                            self.cmat = merge_cmat( cmat, self.start-a_rng.start, self.cmat )
                        #'''
                    else:
                        if self.start <= a_rng.start:
                            self.cmat = merge_cmat( self.cmat, a_rng.start-self.start, a_rng.cmat )
                        else:
                            self.cmat = merge_cmat( a_rng.cmat, self.start-a_rng.start, self.cmat )
                self.start, self.end = self.get_union(a_rng)  
                
                self.xs += a_rng.xs
                return(True)
            else: 
                return(False)
            
    def get_portion(self, s, e):
        
        oss = s - self.start
        ose = e - self.start + 1
        if (oss < ose) & (oss >= 0) & (ose > 0):
            return self.cmat[:,oss:ose]
        else:
            print('ERROR in get_portion: %i, %i' % (oss,ose) )
            return None
            
    def set_portion(self, s, e, cmat):
        
        oss = s - self.start
        ose = e - self.start + 1
        if (oss < ose) & (oss >= 0) & (ose > 0):
            self.cmat[:,oss:ose] = self.cmat[:,oss:ose] + cmat
        else:
            print('ERROR in get_portion: %i, %i' % (oss,ose) )
            
    def update_intersection(self, a_rng, cm=True):
        if (a_rng.chr != self.chr): # | (a_rng.type != self.type): # (self.chr is None) | (a_rng.chr is None) | (a_rng.chr != self.chr):
            return(False)
        else:
            if self.has_ext_intersection_with(a_rng) == True: 
                if cm:
                    if self.cmat is None: self.cmat = np.zeros([5,(self.end-self.start+1)], dtype=np.float32) 
                    
                    # self.cmat = merge_seq_to_cmat( self.cmat, a_rng.start-self.start, a_rng.seq )
                    #'''
                    if a_rng.type == 'M':
                        if a_rng.cmat is not None:
                            s, e = self.get_intersection(a_rng)
                            if e > 0:
                                cmat_tmp = a_rng.get_portion(s,e)
                                self.set_portion(s,e, cmat_tmp)
                            else:
                                return False
                    elif a_rng.type == 'D':
                        s, e = self.get_intersection(a_rng)
                        if e > 0:
                            cmat_tmp = np.ones([5,(e-s+1)], dtype=np.float32)*a_rng.ave_cvg_depth()
                            self.set_portion(s,e, cmat_tmp)
                        else:
                            return False
                    else: return False
                        
                self.xs += a_rng.xs
                return(True)
            else: 
                return(False)
            
    def alloc_cm(self):
        Len = self.end - self.start + 1
        self.cmat = np.zeros([5,Len], dtype=np.float32)
            
    def set_cm(self):
        if self.cmat is None: self.cmat = NTstr2CMat( self.seq )
    
    def concatenate(self, a_rng, update=True):
        if (self.chr is None) | (a_rng.chr is None) | (a_rng.chr != self.chr):
            return(False)
        else:
            if update:
                self.cmat = np.concatenate((self.cmat, a_rng.cmat), axis=1)
                self.end = a_rng.end
                self.get_cvg()
            else:
                self.end = a_rng.end
                self.ave_cvg = (len(self.seq)*self.ave_cvg+len(a_rng.seq)*a_rng.ave_cvg)/(len(self.seq)+len(a_rng.seq))
                self.seq = self.seq + a_rng.seq
                self.get_cov_len()
                
            return(True)
        
    def cut(self, pos):
        
        if (pos > self.start) & (pos < self.end):
            sp = pos
            ep = self.end
            loc = pos - self.start
            if self.cmat is None:
                rgn_new = region(self.chr, sp, ep, self.type, xs = self.xs)
            else:
                cmat = self.cmat[:,loc:]
                rgn_new = region(self.chr, sp, ep, self.type, cmat, xs = self.xs)
                rgn_new.get_cvg()

            self.end = pos -1
            if self.cmat is not None:
                self.cmat = self.cmat[:,:loc]
                self.get_cvg()

            return rgn_new
        else:
            return None

        
    def compare_and_replace_N_old( self, seq_to_compare ):
        
        if len(self.seq) == 0:
            self.get_cvg()
            
        if self.seq.count('N') == 0:
            return False
        else:
            seq_ary = np.array(list(self.seq))
            b = seq_ary == 'N'
            self.cmat[4,b] = 0
            cmat = NTstr2CMat(seq_to_compare)
            self.cmat[:,b] = self.cmat[:,b] + cmat[:,b]
            self.get_cvg()
            return True

            
    def compare_and_replace_N_old2( self, seq_to_compare ):
        
        if len(self.seq) == 0:
            self.get_cvg()

        if len(self.cvg) == 0:
            return False
        else:
            if (self.seq.count('N') == 0) & (self.cvg.min() >= MIN_CVG_FOR_SNP_CORRECTION):
                return False
            else:
                self.cmat[4,:] = 0
                self.cmat = self.cmat + NTstr2CMat(seq_to_compare)*max(MIN_CVG_FOR_SNP_CORRECTION-0.5, 0)
                self.get_cvg()
                return True

            
    def compare_and_replace_N( self, seq_to_compare ):
        
        if len(self.seq) == 0:
            self.cmat = NTstr2CMat(seq_to_compare)*0.001
            self.get_cvg()
            return True

        elif len(self.seq) != len(seq_to_compare):
            print('ERROR IN compare_and_replace_N: %i != %i' % (len(self.seq), len(seq_to_compare)))
            return False
        else:
            if (self.seq.count('N') == 0) & (self.cvg.min() >= MIN_CVG_FOR_SNP_CORRECTION):
                return False
            else:
                self.cmat[4,:] = 0
                self.cmat = self.cmat + NTstr2CMat(seq_to_compare)*max(MIN_CVG_FOR_SNP_CORRECTION-0.5, 0)
                self.get_cvg()
                return True

            
# class region(Region_ext): pass
region = Region_ext

#######################################

class regions:
    def __init__(self, rgn = None):
        self.obj_type = 'rgns'
        self.cnt_r = 0
        self.cnt_s = 0
        
        if rgn == None:
            self.rgns = []
        else:
            if rgn.obj_type == 'rgn': # type(rgn) == region:
                self.rgns = []
                self.rgns.append(rgn)
            else:
                if rgn.obj_type == 'rgns': # type(rgn) == regions:
                    self.rgns = rgn.rgns
                    self.cnt_r = rgn.cnt_r
                    self.cnt_s = rgn.cnt_s
                else:
                    print('ERROR: unrecognized object 1',rgn.obj_type ) # type(rgn))
                    self.rgns = []
        
    def set_r_cnt(self, cr, cs):
        
        self.cnt_r = cr
        self.cnt_s = cs
         
        
    def convert_to_text_lines_ho(self, sn = 0):
        lines = []
        for k in range(len(self.rgns)):
            line_lst = self.rgns[k].convert_to_text_lines(sn,len(self.rgns),k)
            ln = line_lst[0][:-1] + '\t cvg: %3.1f\n' % self.rgns[k].ave_cvg_depth()
            lines = lines + [ln]
        return(lines)

    def convert_to_text_lines(self, sn = 0):
        lines = []
        for k in range(len(self.rgns)):
            line_lst = self.rgns[k].convert_to_text_lines(sn,len(self.rgns),k)
            lines = lines + line_lst
        return(lines)

    def set_from_text_lines(self,lines):
        if len(lines)%7 != 0:
            print('ERROR in regions::set_from_text_lines()')
        else:
            n_rgns = int(len(lines)/7)
            self.rgns = [] 
            for k in range(n_rgns):
                lines_tmp = []
                for m in range(7): lines_tmp.append(lines[k*7+m])
                rgn = region()
                rgn.set_from_text_lines(lines_tmp)
                self.rgns.append(rgn)

    def print(self):
        # self.order()
        print('I have ',len(self.rgns))
        for k in range(len(self.rgns)): 
            print('  ',k,': ', end='')
            self.rgns[k].print()
                    
    def print_short(self):
        # self.order()
        print('I have ',len(self.rgns))
        for k in range(len(self.rgns)): 
            print('  ',k,': ', end='')
            self.rgns[k].print_short()
                    
    def print_compact(self, sel = 0):

        rs_tmp = regions()
        flag = True
        for k, r in enumerate(self.rgns):
            if flag:
                if (r.type == 'M') | (r.type == 'exon'):
                    rgn = self.rgns[k].copy()
                    flag = False
            else:
                if (r.type == 'M') | (r.type == 'exon'):
                    if (k > 0) & (k < (len(self.rgns)-1)):
                        if (rgn.end+1) == r.start:
                            rgn.concatenate(r.copy())
                        else:
                            rs_tmp.rgns.append(rgn.copy())
                            rgn = r.copy()
                    if k == (len(self.rgns)-1):
                        if (rgn.end+1) == r.start:
                            rgn.concatenate(r.copy())
                            rs_tmp.rgns.append(rgn.copy())
                        else:
                            rs_tmp.rgns.append(rgn.copy())
                            rs_tmp.rgns.append(r.copy())

        print('I have ',len(rs_tmp.rgns))
        for k in range(len(rs_tmp.rgns)): 
            print('  ',k,': ', end='')
            if sel == 0: rs_tmp.rgns[k].print_cvg()
            elif sel == 1: rs_tmp.rgns[k].print_short2()
            else: rs_tmp.rgns[k].print_short()

                    
    def print_minimal(self):
        # self.order()
        print('I have ',len(self.rgns))
        for k in range(len(self.rgns)): 
            print('  ',k,': ', end='')
            self.rgns[k].print_minimal()
                    
    def copy(self, update = True):
        r = regions()
        for k in range(len(self.rgns)):
            r.rgns.append(self.rgns[k].copy(update))
        r.cnt_r = self.cnt_r
        r.cnt_s = self.cnt_s
        return(r)
    
    def isempty(self):
        if len(self.rgns) == 0: return(True)
        else: return(False)
        
    def set_rgn(self, rgn, cm, si):
        if rgn.obj_type == 'rgns': # type(rgn) == regions:
            self.rgns = []
            for r in rgn.rgns: 
                if cm & (r.cmat is None): r.set_cm()
                self.rgns.append(r)
            self.cnt_r = rgn.cnt_r
            self.cnt_s = rgn.cnt_s
        else:
            if rgn.obj_type == 'rgn': # type(rgn) == region:
                self.rgns = []
                if cm & (rgn.cmat is None): rgn.set_cm()
                self.rgns.append(rgn)
                if si > 0: self.cnt_r = 1
                if si > 1: self.cnt_s = 1
            else:
                print('ERROR: unrecognized object 2', rgn.obj_type) # type(rgn))
                
    def get_span( self ):               
        if self.isempty() == False:
            span = region(self.rgns[0].chr, self.rgns[0].start, self.rgns[0].end, self.rgns[0].type)
            for rgn in self.rgns:
                span.start = min(rgn.start, span.start)
                span.end = max(rgn.end, span.end)
            return(span)
        else:
            return(region(0,0,0,0,0,0))
                
    def get_span2( self ):               
        if self.isempty() == False:
            # span = region(self.rgns[0].chr, self.rgns[0].start, self.rgns[0].end, self.rgns[0].type, 0)
            start = self.rgns[0].start
            end = self.rgns[0].end
            for k in range(1,len(self.rgns)):
                # span.start = min(rgn.start, span.start)
                # span.end = max(rgn.end, span.end)
                if self.rgns[k].start < start: start = self.rgns[k].start
                if self.rgns[k].end > end: end = self.rgns[k].end
            return(start,end)
        else:
            return(0,0)
                
    def get_span3( self ):               
        if self.isempty() == False:
            # span = region(self.rgns[0].chr, self.rgns[0].start, self.rgns[0].end, self.rgns[0].type, 0)
            start = self.rgns[0].start
            end = self.rgns[0].end
            for k in range(1,len(self.rgns)):
                # span.start = min(rgn.start, span.start)
                # span.end = max(rgn.end, span.end)
                if self.rgns[k].start < start: start = self.rgns[k].start
                if self.rgns[k].end > end: end = self.rgns[k].end
            return(self.rgns[0].chr, start,end)
        else:
            return(0,0,0)
                
    def get_volume(self):
        if self.isempty() == False:
            vol = 0 
            for rgn in self.rgns:
                vol += rgn.get_volume()
            return(int(vol))
        else:
            return(int(0))

    def get_cvgs_and_lens(self, path = None):
        
        if self.isempty() == False:
            if path is None:
                cvgs = np.zeros(len(self.rgns), dtype=np.float32)
                lens = np.zeros(len(self.rgns), dtype=np.int32)
                for k, rgn in enumerate(self.rgns): 
                    cvgs[k] = rgn.ave_cvg_depth()
                    lens[k] = rgn.get_len()
                return cvgs, lens
            else:
                cvgs = np.zeros(len(path), dtype=np.float32)
                lens = np.zeros(len(path), dtype=np.int32)
                n = len(self.rgns)
                for k, p in enumerate(path): 
                    if p < n:
                        cvgs[k] = self.rgns[p].ave_cvg_depth()
                        lens[k] = self.rgns[p].get_len()
                return cvgs, lens
        else:
            return np.zeros(0), np.zeros(0)
        
        
    def get_seq_of_path(self, path):
        if self.isempty() == False:
            seq = ''
            n = len(self.rgns)
            for p in path: 
                if p < n:
                    seq = seq + self.rgns[p].seq
            return seq
        else:
            return None
        
        
    def set_cvg(self):
        if self.isempty() == False:
            for rgn in self.rgns: rgn.get_cvg()
        
    def get_length( self ):               
        if self.isempty() == False:
            Len = 0 
            for rgn in self.rgns:
                Len += rgn.get_len()
            return(Len)
        else:
            return(0)

    def count_valid_NT(self):
        if self.isempty() == False:
            # Len = 0 
            cntN = 0
            for rgn in self.rgns:
                if type(rgn).__name__ != 'region_nd':
                    # Len += rgn.get_len()
                    cntN += rgn.get_cov_len()
            return(cntN)
        else:
            return(0)
        
        
    def get_cov( self ):               
        if self.isempty() == False:
            Len = 0 
            cntN = 0
            for rgn in self.rgns:
                Len += rgn.get_len()
                cntN += rgn.get_cov_len()
            return(cntN/Len)
        else:
            return(0)
        
        
    def get_coverage( self ):               
        if self.isempty() == False:
            self.set_cvg()
            Len = 0 
            for rgn in self.rgns:
                if rgn.cvg is not None:
                    if (isinstance(rgn.cvg,int)) | (isinstance(rgn.cvg,float)):
                        Len += rgn.get_len()
                    else:
                        Len += np.sum(rgn.cvg > 0)
            return(Len)
        else:
            return(0)
                
    def merge( self, rgns ): 
        self.rgns = self.rgns + rgns.rgns
                
    def get_idx_of_type(self,type_in):
        idx = []
        for k in range(len(self.rgns)):
            if self.rgns[k].type == type_in: idx.append(k)
        return(idx)
    
    def order(self):
        if len(self.rgns) > 0:
            Len = len(self.rgns)
            ss = np.zeros(Len)
            for k, rgn in enumerate(self.rgns): ss[k] = rgn.start
            odr = ss.argsort()
            rgns_tmp = []
            for o in odr:
                rgns_tmp.append(self.rgns[o])
            self.rgns = rgns_tmp
            
            for k, rgn in enumerate(self.rgns):
                if (rgn.type == 'I') | (rgn.type == 'insersion'):
                    if self.rgns[k-1].start == rgn.start:
                        if (self.rgns[k-1].type == 'M') | (self.rgns[k-1].type == 'exon'):
                            rgn_tmp = self.rgns[k-1].copy()
                            self.rgns[k-1] = rgn
                            self.rgns[k] = rgn_tmp
                            
            return odr
        else:
            return []
    
    def has_intersection_with(self, rgn):
        if rgn.obj_type == 'rgns': # type(rgn) == regions:
            b = False
            for my_rgn in reversed(self.rgns):
                for your_rgn in rgn.rgns:
                    b = your_rgn.has_intersection_with(my_rgn)
                    if b == True: break
                if b == True: break
            return(b)
        else:
            if rgn.obj_type == 'rgn': # type(rgn) == region:
                b = False
                for my_rgn in reversed(self.rgns):
                    b = rgn.has_intersection_with(my_rgn)
                    if b == True: break
                return(b)
            else:
                print('ERROR: unrecognized object 3', rgn.obj_type ) # type(rgn))
                return(False)
    
    def has_ext_intersection_with(self, rgn):
        if rgn.obj_type == 'rgns': # type(rgn) == regions:
            b = False
            for my_rgn in reversed(self.rgns):
                for your_rgn in rgn.rgns:
                    b = your_rgn.has_ext_intersection_with(my_rgn)
                    if b == True: break
                if b == True: break
            return(b)
        else:
            if rgn.obj_type == 'rgn': # type(rgn) == region:
                b = False
                for my_rgn in reversed(self.rgns):
                    b = rgn.has_ext_intersection_with(my_rgn)
                    if b == True: break
                return(b)
            else:
                print('ERROR: unrecognized object 3', rgn.obj_type ) # type(rgn))
                return(False)
    

    def get_intersection_cvg(self, rgn):
        if rgn.obj_type == 'rgns': # type(rgn) == regions:
            b = False
            c = 0
            for my_rgn in reversed(self.rgns):
                for your_rgn in rgn.rgns:
                    b = your_rgn.has_ext_intersection_with(my_rgn)
                    if b == True: 
                        start = max(your_rgn.start, my_rgn.start)
                        end = min(your_rgn.end, my_rgn.end)
                        c = np.mean(my_rgn.cvg[(start-my_rgn.start):(end-my_rgn.start+1)])
                        break
                if b == True: break
            return b, c
        else:
            if rgn.obj_type == 'rgn': # type(rgn) == region:
                b = False
                c = 0
                for my_rgn in reversed(self.rgns):
                    b = rgn.has_ext_intersection_with(my_rgn)
                    if b == True: 
                        start = max(rgn.start, my_rgn.start)
                        end = min(rgn.end, my_rgn.end)
                        c = np.mean(my_rgn.cvg[(start-my_rgn.start):(end-my_rgn.start+1)])
                        break
                return b, c
            else:
                print('ERROR: unrecognized object 3', rgn.obj_type ) # type(rgn))
                return False, 0
    

    def get_overlap_length(self, rgn):
        if rgn.obj_type == 'rgns': # type(rgn) == regions:
            olen = 0
            for my_rgn in reversed(self.rgns):
                for your_rgn in rgn.rgns:
                    ol = your_rgn.get_overlap_len(my_rgn)
                    olen += ol
                    if ol > 0: break
            return(olen)
        else:
            if rgn.obj_type == 'rgn': # type(rgn) == region:
                olen = 0
                for my_rgn in reversed(self.rgns):
                    ol = rgn.get_overlap_len(my_rgn)
                    olen += ol
                    # if b == True: break
                return(olen)
            else:
                print('ERROR: unrecognized object 3', rgn.obj_type ) # type(rgn))
                return(0)
    
    def update(self, rgn = None, xc = True, cm = True, si = 0):
        
        if rgn is not None:
            b = False
            if len(self.rgns) == 0:
                self.set_rgn(rgn, cm, si)
            else:
                b = False
                if rgn.obj_type == 'rgns': # type(rgn) == regions:
                    for n in range(len(rgn.rgns)):
                        b2 = False
                        for k in reversed(range(len(self.rgns))):
                            b2 = self.rgns[k].update(rgn.rgns[n], cm)
                            if b2 == True: 
                                b = True
                                break
                        if b2 == False: 
                            if rgn.rgns[n].chr == self.rgns[0].chr:
                                if cm & (rgn.rgns[n].cmat is None): rgn.rgns[n].set_cm()
                                self.rgns.append(rgn.rgns[n])
                                # b = True
                    if b:
                        self.cnt_r += rgn.cnt_r
                        self.cnt_s += rgn.cnt_s

                else:
                    if rgn.obj_type == 'rgn': # type(rgn) == region:
                        b2 = False
                        for k in reversed(range(len(self.rgns))):
                            b2 = self.rgns[k].update(rgn, cm)
                            if b2 == True: 
                                b = True
                                break
                        if b2 == False: 
                            if rgn.chr == self.rgns[0].chr:
                                if cm & (rgn.cmat is None): rgn.set_cm()
                                self.rgns.append(rgn)
                                # b = True
                        if b:
                            if si > 0: self.cnt_r += 1
                            if si > 1: self.cnt_s += 1
                            
                    else:
                        print('ERROR: unrecognized object 4', rgn.obj_type ) # type(rgn))
                        rgn.print_short()
                        pass
        else:
            b = True

        if (b == True) & (xc==True):
            to_del = []
            for k in range((len(self.rgns)-1)):
                for n in range(k+1,len(self.rgns)):
                    b = self.rgns[n].update(self.rgns[k], cm)
                    if b == True: 
                        to_del.append(k)
                        break

            if len(to_del) > 0:
                to_del.sort(reverse=True)
                for k in to_del: del self.rgns[k]
                    
            self.order()
        return(b)

    def update_intersection(self, rgn = None, xc = True, cm = True, si = 0):
        
        if rgn is not None:
            b = False
            if len(self.rgns) == 0:
                self.set_rgn(rgn, cm, si)
            else:
                b = False
                if rgn.obj_type == 'rgns': # type(rgn) == regions:
                    for n in range(len(rgn.rgns)):
                        b2 = False
                        for k in reversed(range(len(self.rgns))):
                            b2 = self.rgns[k].update_intersection(rgn.rgns[n], cm)
                            if b2 == True: 
                                b = True
                                break
                    if b:
                        self.cnt_r += rgn.cnt_r
                        self.cnt_s += rgn.cnt_s

                else:
                    if rgn.obj_type == 'rgn': # type(rgn) == region:
                        b2 = False
                        for k in reversed(range(len(self.rgns))):
                            b2 = self.rgns[k].update_intersection(rgn, cm)
                            if b2 == True: 
                                b = True
                                break
                        if b:
                            if si > 0: self.cnt_r += 1
                            if si > 1: self.cnt_s += 1
                            
                    else:
                        print('ERROR: unrecognized object 4', rgn.obj_type ) # type(rgn))
                        rgn.print_short()
                        pass
        else:
            b = False

        return(b)

    def alloc_cm(self):    
        for k in range(len(self.rgns)):
            self.rgns[k].alloc_cm()
            
    def check_rgns(self):   
        b = True
        for k in range(len(self.rgns)):
            Len = self.rgns[k].end - self.rgns[k].start + 1
            if self.rgns[k].cmat is None:
                print('ERROR in check_rgns(A): %i/%i: %i != None ' % (k, len(self.rgns), Len))
                b = False
            elif Len != self.rgns[k].cmat.shape[1]:
                print('ERROR in check_rgns(B): %i/%i: %i != %i ' % (k, len(self.rgns), Len, self.rgns[k].cmat.shape[1]))
                b = False
        return(b)
            
                        
    def get_cvg_stat(self):    

        a_cvg = np.zeros(len(self.rgns))
        for k in range(len(self.rgns)):
            a_cvg[k] = self.rgns[k].ave_cvg_depth()
            
        return(np.min(a_cvg), np.median(a_cvg), np.max(a_cvg))
    
    def remove_rgns_num(self, max_num):

        if len(self.rgns) > max_num:
            a_cvg = np.zeros(len(self.rgns))
            for k in range(len(self.rgns)):
                a_cvg[k] = self.rgns[k].ave_cvg_depth()

            odr = a_cvg.argsort()
            L = len(self.rgns) - max_num
            to_del = list(odr[:L])
            
            max_cvg = 0
            for k in to_del:
                max_cvg = max(max_cvg, self.rgns[k].ave_cvg_depth())

            if len(to_del) > 0:
                to_del.sort(reverse=True)
                for k in to_del: del self.rgns[k]
                    
            return(max_cvg)
        
        else:
            return(0)
    
    def remove_rgns_cvg(self, min_cvg):

        to_del = []
        for k in range(len(self.rgns)):
            if self.rgns[k].ave_cvg_depth() <= min_cvg: to_del.append(k)

        if len(to_del) > 0:
            to_del.sort(reverse=True)
            for k in to_del: del self.rgns[k]

        return(len(to_del))    

#######################################
                        
class region_nd(Region):
    def __init__(self, chr = None, start = None, end = None, align_type = None, cvg_dep = None, xs = 0 ):
        super(region_nd, self).__init__( chr, start, end, align_type, xs=xs )
        if (cvg_dep is None):
            self.cvg = 0 # np.ones(0, dtype=np.int32)
            self.ave_cvg = 0
        else:
            self.cvg = cvg_dep
            self.ave_cvg = cvg_dep
            '''
            self.ave_cvg = self.set_ave_cvg_depth()
            if (self.end-self.start+1) > 0:
                if len(cvg) != (self.end-self.start+1):
                    print('region_nd: Initialization error.',len(cvg), '!=', (self.end-self.start+1))
            '''

        self.cvg_frac = -1

        
    def convert_to_text_lines(self, sn, N, n ):
        line = '>%i\t%i\t%i\t%s\t%i\t%i\t%s\t%i\t%i\n' \
               % (sn, N, n+1, self.chr, self.start, self.end, self.type, self.cvg, self.xs)
        return(line)
    
    def set_from_text_lines(self, line ):
        b = True
        items = line[1:-1].split()
        sn = int(items[0])
        N = int(items[1])
        n = int(items[2])
        self.chr = items[3]
        self.start = int(items[4])
        self.end = int(items[5])
        self.type = items[6]
        self.cvg = float(items[7]) # -np.ones(self.end-self.start+1, dtype=np.int32)
        self.xs = int(items[8])
        self.ave_cvg = self.set_ave_cvg_depth()
        return(b)
    
    def print(self):
        if self.xs == 0: st = ' '
        else: st = ' {0:+}'.format(self.xs)
        st = self.xs
        print(self.chr,'(',self.type, st,')',':',self.start,'~',self.end, \
              '(',abs(self.end)-abs(self.start)+1,') ', 'CVG_Dep: %4.1f' % self.ave_cvg_depth() )
    
    def print_short(self):
        if self.xs == 0: st = ' '
        else: st = ' {0:+}'.format(self.xs)
        print(self.chr,'(',self.type, st,')',':',self.start,'~',self.end, \
              '(',abs(self.end)-abs(self.start)+1,') ', 'CVG_Dep: %4.1f, CF: %5.3f' % (self.ave_cvg_depth(), self.cvg_frac) )
    
    def set_ave_cvg_depth(self):
        self.ave_cvg = self.cvg # np.mean(self.cvg)
        return(self.cvg)
        
    def get_cvg(self):
        self.ave_cvg = self.cvg # np.mean(self.cvg)
        return(self.cvg)
        
    def ave_cvg_depth(self):
        # return(round(np.mean(self.cvg),2))
        return(self.cvg)
        
    def copy(self, update = True):
        rgn_nd = region_nd(self.chr, self.start, self.end, self.type, self.cvg, xs=self.xs)
        if update: rgn_nd.get_cvg()

        rgn_nd.cvg_frac = self.cvg_frac

        return( rgn_nd )
    
    def update(self, a_rng, cm = True):
        b = False
        if (a_rng.chr != self.chr) | (a_rng.type != self.type): 
            pass
        else:
            b = self.has_intersection_with(a_rng)
            if b == True:
                if cm:
                    if self.start <= a_rng.start: 
                        self.cvg = self.cvg + a_rng.cvg 
                        self.ave_cvg = self.cvg
                    else:  
                        self.cvg = self.cvg + a_rng.cvg 
                        self.ave_cvg = self.cvg
                    
                super(region_nd, self).update(a_rng)  
                self.xs += a_rng.xs
        return(b)
    
    def update_intersection(self, a_rng, cm=True):

        b = False
        if (a_rng.chr != self.chr): # | (a_rng.type != self.type): # (self.chr is None) | (a_rng.chr is None) | (a_rng.chr != self.chr):
            pass
        else:
            b = self.has_ext_intersection_with(a_rng)
            if b == True:
                if cm:
                    self.cvg = self.cvg + a_rng.cvg 
                    self.ave_cvg = self.cvg
                    
                self.xs += a_rng.xs
        return(b)

#######################################
            
class regions_nd:
    def __init__(self, rgn = None):
        if rgn == None:
            self.rgns = []
        else:
            if rgn.obj_type == 'rgn': # type(rgn) == region_nd:
                self.rgns = []
                self.rgns.append(rgn)
            else:
                if rgn.obj_type == 'rgns': # type(rgn) == regions_nd:
                    self = rgn.copy()
                else:
                    print('ERROR: unrecognized object 1',rgn.obj_type ) # type(rgn))
                    self.rgns = []
        self.obj_type = 'rgns'

    def convert_to_text_lines(self, sn = 0):
        lines = []
        for k in range(len(self.rgns)):
            line = self.rgns[k].convert_to_text_lines(sn, len(self.rgns), k)
            lines = lines + [line]
        return(lines)

    def set_from_text_lines(self,lines):
        n_rgns = int(len(lines))
        self.rgns = [] 
        for line in lines:
            rgn = region_nd()
            rgn.set_from_text_lines(line)
            self.rgns.append(rgn)

    def print(self):
        self.order()
        print('I have ',len(self.rgns))
        for k in range(len(self.rgns)): 
            print('  ',k,': ', end='')
            self.rgns[k].print()
                    
    def print_short(self):
        self.order()
        print('I have ',len(self.rgns))
        for k in range(len(self.rgns)): 
            print('  ',k,': ', end='')
            self.rgns[k].print_short()
                    
    def copy(self, update = True):
        r = regions_nd()
        for k in range(len(self.rgns)):
            r.rgns.append(self.rgns[k].copy(update))
        # self.set_cvg()
        return(r)
    
    def isempty(self):
        if len(self.rgns) == 0: return(True)
        else: return(False)
        
    def set_rgn(self, rgn):
        if rgn.obj_type == 'rgns': # type(rgn) == regions_nd:
            self.rgns = []
            for r in rgn.rgns: 
                self.rgns.append(r)
            
        else:
            if rgn.obj_type == 'rgn': # type(rgn) == region_nd:
                self.rgns = []
                self.rgns.append(rgn)
            else:
                print('ERROR: unrecognized object 2', rgn.obj_type ) # type(rgn))
                
    def get_span( self ):               
        if self.isempty() == False:
            span = region(self.rgns[0].chr, self.rgns[0].start, self.rgns[0].end, self.rgns[0].type, 0)
            for rgn in self.rgns:
                span.start = min(rgn.start, span.start)
                span.end = max(rgn.end, span.end)
            return(span)
        else:
            return(region(0,0,0,0))
                
    def get_span2( self ):               
        if self.isempty() == False:
            # span = region(self.rgns[0].chr, self.rgns[0].start, self.rgns[0].end, self.rgns[0].type, 0)
            start = self.rgns[0].start
            end = self.rgns[0].end
            for k in range(1,len(self.rgns)):
                # span.start = min(rgn.start, span.start)
                # span.end = max(rgn.end, span.end)
                if self.rgns[k].start < start: start = self.rgns[k].start
                if self.rgns[k].end > end: end = self.rgns[k].end
            return(start,end)
        else:
            return(0,0)
                
    def get_length( self ):               
        if self.isempty() == False:
            Len = 0 # region(self.rgns[0].chr, self.rgns[0].start, self.rgns[0].end)
            for rgn in self.rgns:
                Len += rgn.get_len()
            return(Len)
        else:
            return(0)
                
    def get_cvgs_and_lens(self):
        if self.isempty() == False:
            cvgs = np.zeros(len(self.rgns), dtype=np.float32)
            lens = np.zeros(len(self.rgns), dtype=np.int32)
            for k, rgn in enumerate(self.rgns): 
                cvgs[k] = rgn.ave_cvg_depth()
                lens[k] = rgn.get_len()
            return cvgs, lens
        else:
            return np.zeros(0), np.zeros(0)
                
    def set_cvg(self):
        if self.isempty() == False:
            for rgn in self.rgns: rgn.set_ave_cvg_depth()
        
    def order(self):
        if len(self.rgns) > 0:
            Len = len(self.rgns)
            ss = np.zeros(Len)
            k = 0
            for rgn in self.rgns: 
                ss[k] = rgn.start
                k += 1
            odr = ss.argsort()
            rgns_tmp = []
            for o in odr:
                rgns_tmp.append(self.rgns[o])
            self.rgns = rgns_tmp
    
    def merge( self, rgns ): 
        self.rgns = self.rgns + rgns.rgns

                
    def get_intersection_cvg(self, rgn):
        if rgn.obj_type == 'rgns': # type(rgn) == regions_nd:
            b = False
            c = 0
            for my_rgn in reversed(self.rgns):
                for your_rgn in rgn.rgns:
                    b = your_rgn.has_ext_intersection_with(my_rgn)
                    if b == True: 
                        start = max(your_rgn.start, my_rgn.start)
                        end = min(your_rgn.end, my_rgn.end)
                        c = my_rgn.cvg # np.mean(my_rgn.cvg[(start-my_rgn.start):(end-my_rgn.start)])
                        break
                if b == True: 
                    break
            return b, c
        else:
            if rgn.obj_type == 'rgn': # type(rgn) == region_nd:
                b = False
                c = 0
                for my_rgn in reversed(self.rgns):
                    b = rgn.has_ext_intersection_with(my_rgn)
                    if b == True: 
                        start = max(rgn.start, my_rgn.start)
                        end = min(rgn.end, my_rgn.end)
                        c = my_rgn.cvg # np.mean(my_rgn.cvg[(start-my_rgn.start):(end-my_rgn.start)])
                        break
                return b,c
            else:
                print('ERROR: unrecognized object 3', rgn.obj_type ) # type(rgn))
                return False, 0               
                
    def has_intersection_with(self, rgn):
        if rgn.obj_type == 'rgns': # type(rgn) == regions_nd:
            b = False
            for my_rgn in reversed(self.rgns):
                for your_rgn in rgn.rgns:
                    b = your_rgn.has_intersection_with(my_rgn)
                    if b == True: 
                        break
                if b == True: 
                    break
            return(b)
        else:
            if rgn.obj_type == 'rgn': # type(rgn) == region_nd:
                b = False
                for my_rgn in reversed(self.rgns):
                    b = rgn.has_intersection_with(my_rgn)
                    if b == True: 
                        break
                return(b)
            else:
                print('ERROR: unrecognized object 3', rgn.obj_type ) # type(rgn))
                return(False)
    
    def update(self, rgn = None, xc=True, cm = True):
        
        if rgn is not None:
            b = False
            if rgn.obj_type == 'rgns': # type(rgn) == regions_nd:
                for n in range(len(rgn.rgns)):
                    b2 = False
                    for k in reversed(range(len(self.rgns))):
                        b2 = self.rgns[k].update(rgn.rgns[n], cm)
                        if b2 == True: 
                            b = True
                            break
                    if b2 == False: self.rgns.append(rgn.rgns[n])
                        
            else:
                if rgn.obj_type == 'rgn': # type(rgn) == region_nd:
                    b2 = False
                    for k in reversed(range(len(self.rgns))):
                        b2 = self.rgns[k].update(rgn, cm)
                        if b2 == True: 
                            b = True
                            break
                        else: pass
                    if b2 == False: self.rgns.append(rgn)

                else:
                    print('ERROR: unrecognized object 4', rgn.obj_type ) # type(rgn))
                    pass
        else:
            b = True

        if (b == True) & (xc==True):
            to_del = []
            for k in range((len(self.rgns)-1)):
                for n in range(k+1,len(self.rgns)):
                    b = self.rgns[n].update(self.rgns[k], cm)
                    if b == True: 
                        to_del.append(k)
                        break
                    else:
                        pass

            if len(to_del) > 0:
                to_del.sort(reverse=True)
                for k in to_del:
                    del self.rgns[k]
            self.order()

            
    def update_intersection(self, rgn = None, xc=True, cm = True):
        
        if rgn is not None:
            b = False
            if rgn.obj_type == 'rgns': # type(rgn) == regions_nd:
                for n in range(len(rgn.rgns)):
                    b2 = False
                    for k in reversed(range(len(self.rgns))):
                        b2 = self.rgns[k].update_intersection(rgn.rgns[n], cm)
                        if b2 == True: 
                            b = True
                            break
                        
            else:
                if rgn.obj_type == 'rgn': # type(rgn) == region_nd:
                    b2 = False
                    for k in reversed(range(len(self.rgns))):
                        b2 = self.rgns[k].update_intersection(rgn, cm)
                        if b2 == True: 
                            b = True
                            break
                        else: pass
                else:
                    print('ERROR: unrecognized object 4', rgn.obj_type ) # type(rgn))
                    pass
        else:
            b = True

            
    def alloc_cm(self):    
        for k in range(len(self.rgns)):
            self.rgns[k].cvg = 0
            self.rgns[k].ave_cvg = 0
                    
    def get_cvg_stat(self):    

        a_cvg = np.zeros(len(self.rgns))
        for k in range(len(self.rgns)):
            a_cvg[k] = self.rgns[k].ave_cvg_depth()
            
        return(np.min(a_cvg), np.median(a_cvg), np.max(a_cvg))
    
    def remove_rgns_num(self, max_num):

        if len(self.rgns) > max_num:
            a_cvg = np.zeros(len(self.rgns))
            for k in range(len(self.rgns)):
                a_cvg[k] = self.rgns[k].ave_cvg_depth()

            odr = a_cvg.argsort()
            L = len(self.rgns) - max_num
            to_del = list(odr[:L])
            
            max_cvg = 0
            for k in to_del:
                max_cvg = max(max_cvg, self.rgns[k].ave_cvg_depth())

            if len(to_del) > 0:
                to_del.sort(reverse=True)
                for k in to_del: del self.rgns[k]
                    
            return(max_cvg)
        
        else:
            return(0)

    
    def remove_rgns_cvg(self, min_cvg):

        to_del = []
        for k in range(len(self.rgns)):
            if self.rgns[k].ave_cvg_depth() <= min_cvg: to_del.append(k)

        if len(to_del) > 0:
            to_del.sort(reverse=True)
            for k in to_del: del self.rgns[k]

        return(len(to_del))    
                
    def check_bistrand(self):
        
        pn = 0
        nn = 0
        for r in self.rgns:
            if r.type == 'N':
                if r.xs > 0: pn += 1
                elif r.xs < 0: nn += 1
                
        if (pn > 0) & (nn > 0): 
            return True, pn, nn
        else: 
            return False, pn, nn
            
#'''    


##########################################################################
## Object for loading SAM/BAM
##########################################################################

def get_sam_end_pos( sam_line ): 

    cigar = parse_cigar(sam_line.cigar)
    Len = 0
    for (clen, ctype) in cigar:

        if ctype == 'M': 
            Len += int(clen)
        elif ctype == 'N': 
            Len += int(clen)
        elif ctype == 'D': 
            Len += int(clen)

    return(Len+sam_line.pos)


LINE_VALID = 0
NO_MORE_LINE = 4
LINE_INVALID = 2

CONTINUED = 0
NEW_CHRM = 1
# LINE_INVALID = 2
NOT_SORTED = 3

class sam_obj:

    def __init__(self, file_name, n_max = 0, sa = 1 ):

        self.ftype = file_name.split('.')[-1].upper()
        self.sa = sa
        self.byte_size = os.path.getsize(file_name)
        self.num_bytes = 0
        self.num_lines = 0
        self.num_reads = 0
        self.num_bases = 0
        self.read_len = 0
        self.num_max = n_max
        self.line_q = queue.Queue()
        self.sam_line_last = None
        self.regions_last = None
        self.end_pos_last = 0

        self.chr_prev = 'non_chr'
        self.pos_prev = 0
        
        if self.ftype == 'SAM':
            self.j = 5
            self.f = open(file_name, 'r')
        
            ## skip header lines
            while True:
                line = self.f.readline()
                if line[0] != '@':
                    self.line_q.put(line)
                    '''
                    items = line[:-1].split()
                    self.chr_prev = items[2] # chromosome name
                    self.pos_prev = np.int(items[3])
                    '''
                    break
        else:
            self.j = 7
            self.f = pybam.read(file_name)
            

    def close(self):
        if self.ftype == 'SAM': self.f.close()
        
    def get_lines(self):
        
        if self.ftype == 'SAM':
            b = True
            lines = self.f.readlines(100)
            if not lines: 
                b = False
            else:
                for line in lines:
                    self.line_q.put(line)
                    self.num_bytes += len(line)
            return b
        else:
            cnt = 0
            for line in self.f:
                sam_line = line.sam
                self.line_q.put(sam_line)
                cnt += 1
                if cnt == 100: break
                    
            self.num_bytes = self.f.file_bytes_read
            if cnt == 0:
                return False
            else:
                return True

    def read_line(self):
        
        '''
        if self.line_q.empty():
            b = self.get_lines()
            if not b:
                return NO_MORE_LINE, 0
        
        line = self.line_q.get()
        self.num_lines += 1
        '''
        if self.ftype == 'SAM':
            line = self.f.readline()   
            self.num_bytes += len(line)
        else:
            # if self.line_q.empty(): b = self.get_lines()
            # line = self.line_q.get()
            line = None
            for l in self.f:
                line = l.sam
                break
            self.num_bytes = self.f.file_bytes_read
            
        if not line: 
            return NO_MORE_LINE, 0
        
        self.num_lines += 1

        items = line[:-1].split()
        # flag_str = format(int(items[1])+4096, 'b')[::-1]
        # pri = flag_str[8]
        if self.sa > 0:
            pri = 0
            # if self.sa > 1: pri = int(items[1]) & 0b1100
        else:
            pri = int(items[1]) & 0b100000000
            
        if (pri == 0) & (items[2] != '*') & (items[5] != '*') & (items[9][0] != '*') & (int(items[4]) > 7): 

            '''
            qname = items[0]
            flag = np.int(items[1])
            rname = items[2]
            pos = np.int(items[3])
            mapq = np.int(items[4])
            cigar = items[5]
            rnext = items[6]
            pnext = np.int(items[7])
            tlen = np.int(items[8])
            seq = items[9].upper()
            qual = 0
            '''
            seq = items[9].upper()
            # qual = items[10]

            XS = 0
            '''
            if len(items) > 11:
                if items[11][self.j] == '+': XS = 1
                elif items[11][self.j] == '-': XS = -1
                else: print('(%s)' % items[11] )
            '''
            if len(items) > 11:
                for item in items[11:]:
                    if item[:4] == 'XS:A':
                        if item[self.j] == '+': XS = 1
                        elif item[self.j] == '-': XS = -1
                        # else: print('(%s)' % items[11] )
                    
            '''
            cN = np.int(cigar.count('N'))
            cD = np.int(cigar.count('D'))
            cI = np.int(cigar.count('I'))
            cS = np.int(cigar.count('S'))
            '''

            # sam_line = SAM_line( qname, flag, 0, rname, pos, mapq, cigar, rnext, pnext, \
            #                     tlen, seq, qual, 0, 0, 0, 0, XS ) # cN, cD, cI, cS )
            flag_str = format(int(items[1])+4096, 'b')[::-1]
            '''
            sam_line = SAM_line( items[0], np.int(items[1]), flag_str, items[2], np.int(items[3]), \
                                 np.int(items[4]), items[5], items[6], np.int(items[7]), \
                                 np.int(items[8]), seq, 0, 0, 0, 0, 0, XS ) # cN, cD, cI, cS )
            '''
            # slns.append( sam_line )
            '''
            SAM_line = collections.namedtuple('SAM_line', 'qname, flag_str, rname, pos, mapq, cigar, \
                                               rnext, pnext, tlen, seq, qual, xs')
            '''
            sam_line = SAM_line( items[0], flag_str, items[2], np.int(items[3]), \
                                 np.int16(items[4]), items[5], items[6], np.int(items[7]), \
                                 np.int(items[8]), seq, '', XS ) 

            self.num_reads += 1
            self.num_bases += len(seq)
            self.read_len = max(self.read_len,len(seq))
            
            if self.num_max > 0:
                if self.num_reads > self.num_max:
                    return NO_MORE_LINE, sam_line
            
            return LINE_VALID, sam_line
        
        else:
            return LINE_INVALID, 0
        
    def get_sam_line(self):
        
        while True:
            b, sam_line = self.read_line()
            if b != LINE_INVALID:
                break
                
        if b == LINE_VALID:
            if sam_line.rname != self.chr_prev:
                self.chr_prev = sam_line.rname
                self.pos_prev = sam_line.pos
                return NEW_CHRM, sam_line
            elif self.pos_prev > sam_line.pos:
                return NOT_SORTED, 0
            else:
                self.pos_prev = sam_line.pos
                return CONTINUED, sam_line
                
        else:
            return b, 0

    def get_sam_lines_for_one_chrm(self):
        
        sam_line_lst = []
        if self.sam_line_last is None:
            c, sam_line = self.get_sam_line()
            sam_line_lst.append(sam_line)
        else:
            sam_line_lst.append(self.sam_line_last)
        
        while True:
            c, sam_line = self.get_sam_line()
            if c == CONTINUED:
                sam_line_lst.append(sam_line)
            elif c == NEW_CHRM:
                self.sam_line_last = sam_line
                break
            else:
                break
                    
        return c, sam_line_lst
            

    def get_rgns_for_one_chrm(self):
        
        r_m_lst = []
        r_nd_lst = []
        r_sti_lst = []
        
        if self.sam_line_last is None:
            c, sam_line = self.get_sam_line()
            r_m, r_sti, r_nd = get_rgns_from_sam_line_ext( sam_line, cm = False )
        else:
            r_m, r_sti, r_nd = get_rgns_from_sam_line_ext( self.sam_line_last, cm = False )
            
        if len(r_m.rgns) > 0:
            r_m_lst.append(r_m)
            r_nd_lst.append(r_nd)
            r_sti_lst.append(r_sti)
        
        while True:
            c, sam_line = self.get_sam_line()
            if c == CONTINUED:
                r_m, r_sti, r_nd = get_rgns_from_sam_line_ext( sam_line, cm = False )
                if len(r_m.rgns) > 0:
                    r_m_lst.append(r_m)
                    r_nd_lst.append(r_nd)
                    r_sti_lst.append(r_sti)
            elif c == NEW_CHRM:
                self.sam_line_last = sam_line
                break
            else:
                break
                    
        return c, r_m_lst, r_nd_lst, r_sti_lst
            
        
    def get_one_overlaped_rgns(self):
        
        r_m_lst = []
        r_nd_lst = []
        r_sti_lst = []
        
        if self.regions_last is None:
            c, sam_line = self.get_sam_line()
            r_m, r_sti, r_nd = get_rgns_from_sam_line_ext( sam_line, cm = False )
        else:
            # r_m, r_sti, r_nd = get_rgns_from_sam_line_ext( self.sam_line_last, cm = False )
            r_m = self.regions_last[0]
            r_nd = self.regions_last[1]
            r_sti = self.regions_last[2]
            
        startp, self.end_pos_last = r_m.get_span2()
        
        if len(r_m.rgns) > 0:
            r_m_lst.append(r_m)
            r_nd_lst.append(r_nd)
            r_sti_lst.append(r_sti)
        
        while True:
            c, sam_line = self.get_sam_line()
            if c == CONTINUED:
                r_m, r_sti, r_nd = get_rgns_from_sam_line_ext( sam_line, cm = False )
                startp, endp = r_m.get_span2()
                if startp < (self.end_pos_last + MAX_DIST_UC):
                    self.end_pos_last = max(self.end_pos_last,endp)
                    if len(r_m.rgns) > 0:
                        r_m_lst.append(r_m)
                        r_nd_lst.append(r_nd)
                        r_sti_lst.append(r_sti)
                else:
                    self.regions_last = [r_m, r_nd, r_sti]
                    break
                    
            elif c == NEW_CHRM:
                # self.sam_line_last = sam_line
                r_m, r_sti, r_nd = get_rgns_from_sam_line_ext( sam_line, cm = False )
                self.regions_last = [r_m, r_nd, r_sti]
                self.end_pos_last = 0
                break
            else:
                break
                    
        return c, r_m_lst, r_nd_lst, r_sti_lst
            

    def get_one_overlaped_sam(self):
        
        sam_lst = []
        
        if self.sam_line_last is None:
            c, sam_line = self.get_sam_line()
        else:
            sam_line = self.sam_line_last
            
        # startp = sam_line.pos
        self.end_pos_last = get_sam_end_pos(sam_line)
        
        sam_lst.append(sam_line)
        
        while True:
            c, sam_line = self.get_sam_line()
            if c == CONTINUED:
                # startp = sam_line.pos
                endp = get_sam_end_pos(sam_line)
                if sam_line.pos < (self.end_pos_last + MAX_DIST_UC):
                    self.end_pos_last = max(self.end_pos_last,endp)
                    sam_lst.append(sam_line)
                else:
                    self.sam_line_last = sam_line
                    break
                    
            elif c == NEW_CHRM:
                self.sam_line_last = sam_line
                self.end_pos_last = 0
                break
            else:
                break
                    
        return c, sam_lst, self.num_reads
                    

##########################################################################
## Functions to build contigs
##########################################################################

def gen_seq(nt_char,Len):
    tseq = ''
    for n in range(Len): tseq = tseq + nt_char
    return(tseq)


def get_rgns_from_sam_line_ext( sam_line, cm = True, wgt = 1 ): # , max_intron_len = MAX_INTRON_LENGTH ):
    
    cigar = parse_cigar(sam_line.cigar)
    rpos = 0              # 0-base position
    qpos = sam_line.pos   # 1-base position
    rgns_m = regions()
    rgns_sti = regions()
    rgns_nd = regions_nd()
    
    cnt = 0
    
    clen_th = MIN_LENGTH_M
    b = np.zeros(len(cigar))
    cnt_n = 0
    
    for k, (clen, ctype) in enumerate(cigar):
        
        Len = int(clen)
        if ctype == 'M': 
            b[k] = 1
            if (k == 0) | (k == (len(cigar)-1)):
                if Len < clen_th: b[k] = 0
                    
            if b[k] > 0:
                rgn = region( sam_line.rname, qpos, qpos+Len-1, 'M', sam_line.seq[rpos:(rpos+Len)], \
                              cvg_dep = wgt, cm=cm, xs=sam_line.xs*wgt)
                rgns_m.rgns.append(rgn)
                
            qpos += Len
            rpos += Len
            
        elif ctype == 'N': 
            if (b[k-1] == 1) & (int(cigar[k+1][0]) >= clen_th):
                rgn = region_nd( sam_line.rname, qpos, qpos+Len-1, 'N', cvg_dep = wgt, xs=sam_line.xs*wgt) # np.ones(Len))
                rgns_nd.rgns.append(rgn)
                b[k] = 1
                cnt_n += 1
                
            qpos += Len
            
        elif ctype == 'D': 
            # if (b[k-1] == 1) & (int(cigar[k+1][0]) >= clen_th):
            rgn = region_nd( sam_line.rname, qpos, qpos+Len-1, 'D', cvg_dep = wgt, xs=sam_line.xs*wgt) # np.ones(Len))
            rgns_nd.rgns.append(rgn)
            b[k] = 1
                
            qpos += Len
            
        elif ctype == 'I': 
            # if (b[k-1] == 1) & (int(cigar[k+1][0]) >= clen_th):
            rgn = region( sam_line.rname, qpos, qpos+Len-1, 'I', sam_line.seq[rpos:(rpos+Len)], \
                          cvg_dep = wgt, cm=cm, xs=sam_line.xs*wgt)
            rgns_sti.rgns.append(rgn)
            b[k] = 1
                
            rpos += Len
            
        elif ctype == 'S':
            '''
            if k == 0:
                rgn = region( sam_line.rname, qpos, qpos+Len-1, 'S', sam_line.seq[rpos:(rpos+Len)], \
                              cvg_dep = wgt, cm=cm, xs=sam_line.xs*wgt)
                rgns_sti.rgns.append(rgn)
            else:
                rgn = region( sam_line.rname, qpos, qpos+Len-1, 'T', sam_line.seq[rpos:(rpos+Len)], \
                              cvg_dep = wgt, cm=cm, xs=sam_line.xs*wgt)
                rgns_sti.rgns.append(rgn)
            '''    
            rpos += Len
            b[k] = 1
            
        elif ctype == '=': 
            b[k] = 1
            if (k == 0) | (k == (len(cigar)-1)):
                if Len < clen_th: b[k] = 0
                    
            if b[k] > 0:
                rgn = region( sam_line.rname, qpos, qpos+Len-1, 'M', sam_line.seq[rpos:(rpos+Len)], \
                              cvg_dep = wgt, cm=cm, xs=sam_line.xs*wgt)
                rgns_m.rgns.append(rgn)
                
            qpos += Len
            rpos += Len
            
            
        elif ctype == 'X': 
            b[k] = 1
            if (k == 0) | (k == (len(cigar)-1)):
                if Len < clen_th: b[k] = 0
                    
            if b[k] > 0:
                rgn = region( sam_line.rname, qpos, qpos+Len-1, 'M', sam_line.seq[rpos:(rpos+Len)], \
                              cvg_dep = wgt, cm=cm, xs=sam_line.xs*wgt)
                rgns_m.rgns.append(rgn)
                
            qpos += Len
            rpos += Len
            
        cnt += 1
        
    if (int(sam_line.flag_str[8]) == 0):
        rgns_m.set_r_cnt(1,0)
    else:
        rgns_m.set_r_cnt(1,1)
        
    if cnt_n > 1:
        start = 0
        end = 0
        for r in rgns_nd.rgns:
            if r.type == 'N':
                if start == 0:
                    start = r.start
                else:
                    start = min(start, r.start)
                if end == 0:
                    end = r.end
                else:
                    end = min(end, r.end)
        rgn = region_nd( sam_line.rname, start, end, 'N', cvg_dep = wgt, xs=sam_line.xs*wgt) # np.ones(Len))
        rgns_nd.rgns.append(rgn)
            
    return(rgns_m, rgns_sti, rgns_nd)

#### For building

def get_rows( lst, wh ):
    lst_sel = []
    for w in wh: lst_sel.append( lst[w] )
    return(lst_sel) 

def find_pair(qname_lst):
    
    my_pair = np.full(len(qname_lst),-1,dtype=np.int64)
    qf = pd.factorize(qname_lst)
    qnames = qf[1]
    if len(qnames) < len(qname_lst):
        qnum_lst = qf[0]
        odr_t = qnum_lst.argsort()
        pqn = qnum_lst[odr_t[0]]
        for k in range(1,len(qnum_lst)):
            cqn = qnum_lst[odr_t[k]]
            if cqn == pqn:
                my_pair[odr_t[k]] = odr_t[k-1]
                my_pair[odr_t[k-1]] = odr_t[k]
            pqn = cqn
            
    return(my_pair)


def get_weight(sam_line_lst):
    
    dict_qnames = {}
    for k, sam_line in enumerate(sam_line_lst):
        if sam_line.qname in dict_qnames.keys():
            dict_qnames[sam_line.qname].append(k)
        else:
            dict_qnames[sam_line.qname] = [k]

    div = np.ones(len(sam_line_lst), dtype=np.float32)  
    for k, sam_line in enumerate(sam_line_lst):
        if len(dict_qnames[sam_line.qname]) > 0:
            div[k] = 2/len(dict_qnames[sam_line.qname])

    # print( np.sum(div == 0), np.sum(div == 1), np.sum(div == 2), np.sum(div > 2) )
            
    return(div)


def find_closest( rgns_m1, rgns_m2, min_dist = MAX_DIST_UC ):
    
    Len1 = len(rgns_m1.rgns)
    Len2 = len(rgns_m2.rgns)
    # dist = np.ones([Len1,Len2])*1000000
    d = min_dist
    f = -1
    e = -1
    for k in range(Len1):
        for m in range(Len2):
            d1 = abs(rgns_m1.rgns[k].end - rgns_m2.rgns[m].start)
            d2 = abs(rgns_m1.rgns[k].start - rgns_m2.rgns[m].end)
            if d1 < d2:
                if (d1 <= min_dist):
                    if d1 < d:
                        d = d1
                        f = k
                        e = m
                        b = False
            elif d2 < d1:
                if (d2 <= min_dist):
                    if d2 < d:
                        d = d2
                        f = m
                        e = k
    return(f,e,d)


def get_regions_all_from_sam( sam_line_lst, verbose = 1, sdiv = 10, cm = True, sa = 0 ):
    
    # qname_lst = get_col(sam_line_lst, QNAME)
    # my_pair = find_pair(qname_lst)
    # find_pair_new(qname_lst)
    my_pair = None
    
    if sa > 1:
        #wgt = get_weight(sam_line_lst)
        #'''
        wgt = np.ones(len(sam_line_lst), dtype=np.float32)
        qn_cnt_dict = {}
        for k, sam_line in enumerate(sam_line_lst):
            if (int(sam_line.flag_str[8]) == 1):
                if sam_line.qname in qn_cnt_dict.keys():
                    qn_cnt_dict[sam_line.qname] += 1
                else:
                    qn_cnt_dict[sam_line.qname] = 1

        for k, sam_line in enumerate(sam_line_lst):
            if sam_line.qname in qn_cnt_dict.keys():
                if (int(sam_line.flag_str[8]) == 1):
                    wgt[k] = 1/(qn_cnt_dict[sam_line.qname]+1) ## for single-end read: (... + 1)
        del qn_cnt_dict
        #'''
    else:
        wgt = np.ones(len(sam_line_lst), dtype=np.float32)
            
    cmi = cm
    Len = len(sam_line_lst)
                
    rgn_idx = np.full(Len,-1,dtype=np.int64)
    rgns_lst_m = []
    rgns_lst_sti = []
    rgns_lst_nd = []
    rgn_cnt_m = 0
    
    b_proc = np.zeros(Len) # b_invalid

    r_cnt = 0
    n_loop = 0
    k_start = 0
    
    ### Init. rgns
    rgns_m = regions()
    rgns_sti = regions()
    rgns_nd = regions_nd()

    bs = False        
    for sam_line in sam_line_lst:
        r_m, r_sti, r_nd = get_rgns_from_sam_line_ext( sam_line, cm = False, wgt = wgt[0] )
        if len(r_m.rgns) > 0:
            span = region(r_m.rgns[0].chr, r_m.rgns[0].start, r_m.rgns[0].end, r_m.rgns[0].type)
            bs = True
            break

    # rx = {}
    rx = [None for k in range(Len)]

    while bs:
        cnt = 0
        for k in range(k_start, Len):

            #'''            
            if rx[k] is not None:
                r_m, r_sti, r_nd = rx[k]
            else:
                r_m, r_sti, r_nd = get_rgns_from_sam_line_ext( sam_line_lst[k], cm = False, wgt = wgt[k] )
            #'''
            #r_m, r_sti, r_nd = get_rgns_from_sam_line_ext( sam_line_lst[k], cm = False, wgt = wgt[k] )

            if b_proc[k] == 0:
                    
                if (rgns_m.isempty() == True):
                    ### Set/Update rgns
                    rgns_m.update(r_m, xc = False, cm = cmi)
                    rgns_nd.update(r_nd, xc = False)
                    rgns_sti.update(r_sti, xc = False, cm = cmi)
                    b_proc[k] = 1
                    rgn_idx[k] = rgn_cnt_m
                    r_cnt += 1
                    
                elif (rgns_m.has_intersection_with(r_m) == True):
                    ### Set/Update rgns
                    rgns_m.update(r_m, xc = False, cm = cmi)
                    rgns_nd.update(r_nd, xc = False)
                    rgns_sti.update(r_sti, xc = False, cm = cmi)
                    b_proc[k] = 1
                    rgn_idx[k] = rgn_cnt_m
                    r_cnt += 1
                    
                else:
                    span.start, span.end = rgns_m.get_span2()
                    if r_m.has_intersection_with(span) == True:
                        #'''
                        if cnt == 0: k_start = k
                        cnt += 1
                        rx[k] = (r_m, r_sti, r_nd)
                        #'''
                    else:   
                        ### Save Group of rgns
                        rgns_m.update(cm = cmi)
                        rgns_nd.update()
                        rgns_sti.update(cm = cmi)
                        
                        rgns_lst_m.append( rgns_m )
                        rgns_lst_nd.append( rgns_nd )
                        rgns_lst_sti.append( rgns_sti )
                        rgn_cnt_m += 1

                        ### Init. rgns
                        rgns_m = regions()
                        rgns_sti = regions()
                        rgns_nd = regions_nd()

                        if cnt > 0: 
                            rx[k] = (r_m, r_sti, r_nd)
                            break
                        else:
                            ### Set rgns
                            rgns_m.update(r_m, xc = False, cm = cmi)
                            rgns_nd.update(r_nd, xc = False)
                            rgns_sti.update(r_sti, xc = False, cm = cmi)
                            b_proc[k] = 1
                            rgn_idx[k] = rgn_cnt_m
                            r_cnt += 1
                            
        if rgns_m.isempty() == False: 
            rgns_m.update(cm = cmi)
            rgns_nd.update()
            rgns_sti.update(cm = cmi)

            rgns_lst_m.append( rgns_m )
            rgns_lst_nd.append( rgns_nd )
            rgns_lst_sti.append( rgns_sti )
            rgn_cnt_m += 1

            ### Init. rgns
            rgns_m = regions()
            rgns_sti = regions()
            rgns_nd = regions_nd()
           
        n_loop += 1
        if r_cnt == (len(rgn_idx)): break
            
    if bs:
        if rgns_m.isempty() == False: 
            rgns_m.update(cm = cmi)
            rgns_nd.update()
            rgns_sti.update(cm = cmi)

            rgns_lst_m.append( rgns_m )
            rgns_lst_nd.append( rgns_nd )
            rgns_lst_sti.append( rgns_sti )
            rgn_cnt_m += 1
        
        if cmi == False:

            for k in range(len(rgns_lst_m)):
                rgns_lst_m[k].alloc_cm()
                rgns_lst_sti[k].alloc_cm()

            step = np.ceil(Len/sdiv)
            for k in range(len(sam_line_lst)):
                r_idx = rgn_idx[k]
                if r_idx >= 0:
                    r_m, r_sti, r_nd = get_rgns_from_sam_line_ext( sam_line_lst[k], cm = False, wgt = wgt[k] )
                    rgns_lst_m[r_idx].update(r_m, xc = False)
                    rgns_lst_sti[r_idx].update(r_sti, xc = False)       

            for k in range(len(rgns_lst_m)):
                b = rgns_lst_m[k].check_rgns()
                b = rgns_lst_sti[k].check_rgns()

        if len(rgns_lst_m) > 0: 
            
            for r in rgns_lst_m: r.set_cvg()
            for r in rgns_lst_nd: r.set_cvg()
            for r in rgns_lst_sti: r.set_cvg()
            
            rgns_lst_m, rgns_lst_nd, rgns_lst_sti = \
                 connect_regions( rgns_lst_m, rgns_lst_nd, rgns_lst_sti, \
                                  rgn_idx, my_pair,verbose=0 )
            # r_lst_mi, r_lst_nd = trim_contigs( r_lst_m, r_lst_nd, r_lst_sti, verbose=v )
                        
    return((rgns_lst_m, rgns_lst_nd, rgns_lst_sti, rgn_idx))


class my_sparse_mat:
   
    def __init__(self):
        self.mat = {}
        self.keys = []
        
    def set(self,r,c,v):
        if (r,c) in self.keys:
            self.mat[(r,c)] = v
        else:
            self.mat[(r,c)] = v
            self.keys = self.mat.keys()

    def get(self,r,c):
        if (r,c) in self.keys:
            return(self.mat[(r,c)])
        else:
            return(0)

    def add(self,r,c,v):
        if (r,c) in self.keys:
            self.mat[(r,c)] = self.mat[(r,c)] + v
        else:
            self.mat[(r,c)] = v
            self.keys = self.mat.keys()
            
    def n_entries(self):
        return(len(self.keys))
    
    def get_keys(self):
        return(self.keys)
    
    def print(self):
        for key in self.keys:
            print(key, ':', self.mat[key] )    
            

def connect_regions( rgns_lst_m, rgns_lst_nd, rgns_lst_sti, rgn_idx, my_pair,
                     verbose = 1, sdiv = 10 ):
    
    start_time = time.time()
    #'''
    rgn_cnt_m = len(rgns_lst_m)
    

    if False: # True:
        min_connection_th = MIN_CONN_DEPTH
        
        ## Group Contigs using pairs
        conn_mat = my_sparse_mat()
        b_proc = np.zeros(len(my_pair))
        for k in range(len(my_pair)):
            if (b_proc[k] == 0) & (my_pair[k] >= 0):
                b_proc[k] = 1
                if (b_proc[int(my_pair[k])] == 0):
                    b_proc[int(my_pair[k])] = 1
                    if (rgn_idx[k]<rgn_cnt_m) & (rgn_idx[int(my_pair[k])]<rgn_cnt_m) & \
                       (rgn_idx[k]>=0) & (rgn_idx[int(my_pair[k])]>=0):
                        if rgn_idx[k] != rgn_idx[int(my_pair[k])]:
                            conn_mat.add(rgn_idx[k], rgn_idx[int(my_pair[k])], 1)
                            conn_mat.add(rgn_idx[int(my_pair[k])], rgn_idx[k], 1)

        keys = conn_mat.get_keys()
        for key in keys:
            if conn_mat.mat[key] >= min_connection_th:
                conn_mat.mat[key] = 1
            else:
                conn_mat.mat[key] = 0

        ## Using pairs
        if conn_mat.n_entries() > 0:

            if verbose == 2: 
                print('   Connecting',end='')
                print('(%i) ' % conn_mat.n_entries(), end=' ')
            elif verbose == 1: print('P',end='')

            lcnt = 0
            c_cnt = 0
            b_proc = np.zeros(rgn_cnt_m)
            step = int(np.ceil(rgn_cnt_m/sdiv))
            for k in range(rgn_cnt_m-1):
                if (b_proc[k]==0):
                    for m in range(k+1,rgn_cnt_m):
                        if (k != m) & (b_proc[m]==0):
                            if conn_mat.get(k,m) > 0:
                                b = rgns_lst_m[m].update(rgns_lst_m[k])
                                # if b == True:
                                rgns_lst_nd[m].update(rgns_lst_nd[k])
                                rgns_lst_sti[m].update(rgns_lst_sti[k])
                                b_proc[k] = 1
                                c_cnt += 1
                                break

                if verbose > 0: 
                    if k%step == 0: 
                        print('.', end='' )
                        lcnt += 1

            for k in reversed(range(len(rgns_lst_m))):
                if b_proc[k] > 0:             
                    del rgns_lst_m[k]
                    del rgns_lst_nd[k]
                    del rgns_lst_sti[k]
        #'''

        
    if verbose == 2: 
        print('   Merge regions  ',end='')
        
    rgn_cnt_m = len(rgns_lst_m)
    
    
    ## Using nearby contigs
    spn = []
    for k in range(rgn_cnt_m):
        sp_tmp = rgns_lst_m[k].get_span()
        sp_tmp.start -= MAX_DIST_UC
        sp_tmp.end += MAX_DIST_UC
        spn.append(sp_tmp)
        
    c_cnt = 0
    b_proc = np.zeros(rgn_cnt_m)
    step = int(np.ceil(rgn_cnt_m/sdiv))
    lcnt = 0
    for k in range(rgn_cnt_m-1):
        if (b_proc[k]==0):
            # flag = 0
            for m in range(k+1,rgn_cnt_m):
                if (k != m) & (b_proc[m]==0):
                    if spn[k].has_intersection_with(spn[m]) == True:
                        f,e,d = find_closest(rgns_lst_m[k], rgns_lst_m[m])
                        if (f >= 0) & (e >= 0) & (d <= MAX_DIST_UC) :
                            b = rgns_lst_m[m].update(rgns_lst_m[k])
                            # if b == True:
                            rgns_lst_nd[m].update(rgns_lst_nd[k])
                            rgns_lst_sti[m].update(rgns_lst_sti[k])
                            b_proc[k] = 1
                            c_cnt += 1
                            # if verbose == True: print('D_min=%i (%i,%i) of (%i,%i), Cnt=%i ' % (d,f,e,k,m,c_cnt))
                            break
                    else: break
                            
        if verbose > 0: 
            if k%step == 0: 
                print('.', end='' )
                lcnt += 1
                        
    for k in reversed(range(len(rgns_lst_m))):
        if b_proc[k] > 0:             
            del rgns_lst_m[k]
            del rgns_lst_nd[k]
            del rgns_lst_sti[k]
    
    if (verbose == 2): 
        elapsed_time = time.time() - start_time
        print(' done in', round(elapsed_time,2),'(sec), Cnt:', len(rgns_lst_m) )
        
    return rgns_lst_m, rgns_lst_nd, rgns_lst_sti


##########################################################################
## Functions for contigs trimming
##########################################################################

def check_connection( r_m, r_n, max_dev, max_dev_d = 0  ):
    if (r_n.end - r_n.start + 1) > 0:
        if r_n.type == 'N':
            max_dev = min(max_dev, MAX_DEV_NM)
            if abs(r_m.end + 1 - r_n.start) <= max_dev:
                return( (r_m.end + 1 - r_n.start), 1 )
            elif abs(r_n.end + 1 - r_m.start) <= max_dev:
                return( (r_n.end + 1 - r_m.start), -1 )
            else: return( 0, 0 ) 

        elif r_n.type == 'D':
            Len = r_n.end - r_n.start + 1
            max_dev_d = min(Len-1, max_dev_d)
            if abs(r_m.end + 1 - r_n.start) <= max_dev_d:
                return( (r_m.end + 1 - r_n.start), 1 )
            elif abs(r_n.end + 1 - r_m.start) <= max_dev_d:
                return( (r_n.end + 1 - r_m.start), -1 )
            else: return( 0, 0 )  

        elif (r_n.type == 'I') & (r_m.type == 'M'):
            if r_m.end == (r_n.start-1):
                return( 0, 1 )
            elif r_m.start == r_n.start:
                return( 0, -1 )
            else: return( 0, 0 )  
            
    elif (r_n.end - r_n.start + 1) == 0:
        
        if (r_n.type == 'I') & (r_m.type == 'M'):
            if r_m.end == (r_n.start-1):
                return( 0, 1 )
            elif r_m.start == r_n.start:
                return( 0, -1 )
            else: return( 0, 0 )  
        else:
            ovlp = 0
            if r_m.start == r_n.start : mode = -1
            elif r_m.end == r_n.end : mode = 1
            else: mode = 0
            return( ovlp, mode )
        
    else: return( 0, 0 ) 

def check_connection_m( r_m, rs_nd, max_dev, max_dev_d = 0 ):
    
    Len = r_m.end - r_m.start + 1
    md = min(Len,max_dev)
    res = np.zeros([2,len(rs_nd.rgns)])
    for k in range(len(rs_nd.rgns)):
        ovlp, mode = check_connection( r_m, rs_nd.rgns[k], md, max_dev_d )
        res[0,k] = ovlp
        res[1,k] = mode
    
    return( res )

def check_connection_nd( rs_m, r_nd, max_dev = MAX_DEV_NM ):
    
    max_dev = min(max_dev, r_nd.get_len())
    res = np.zeros([2,len(rs_m.rgns)])
    for k in range(len(rs_m.rgns)):
        if rs_m.rgns[k].type == 'M':
            ovlp, mode = check_connection( rs_m.rgns[k], r_nd, max_dev )
            res[0,k] = ovlp
            res[1,k] = mode

    if (r_nd.end-r_nd.start+1) >= 0:
        if sum(res[1,:] > 0) > 1:
            wh = which(res[1,:] > 0)
            v = abs(res[0,wh])
            imin = np.argmin(v)
            for k in range(len(wh)):
                if k != imin: res[:,wh[k]] = 0
                
        elif sum(res[1,:] < 0) > 1:
            wh = which(res[1,:] < 0)
            v = abs(res[0,wh])
            imin = np.argmin(v)
            for k in range(len(wh)):
                if k != imin: res[:,wh[k]] = 0
        
    return( res )

    
def rem_nm_2long_and_2thin( rs_nd, rs_m, verbose = False, sdiv = 10 ):
    
    b = 0
    to_del_m = []
    to_del_nd = []

    Ave_depth_th = N_VALID_CVG # max( N_VALID_CFRAC*Ave_depth/len(rs_m.rgns), MIN_DEPTH_N )
        
    for n in range(len(rs_nd.rgns)):
        if ((rs_nd.rgns[n].ave_cvg_depth() < Ave_depth_th)) & (rs_nd.rgns[n].get_len() > MAX_INTRON_LENGTH): # (rs_nd.rgns[n].type == 'N'):
            to_del_nd.append(n)
                                
    if len(to_del_nd) > 0:
        to_del_nd.sort(reverse=True)
        for k in to_del_nd: del rs_nd.rgns[k]
            
    return(rs_nd, rs_m, b)
           

def adj_nd( rs_nd, rs_m, verbose = False, sdiv = 10 ):
    
    b = 0
    to_del_m = []
    to_del_nd = []

    Ave_depth_th = N_VALID_CVG # max( N_VALID_CFRAC*Ave_depth/len(rs_m.rgns), MIN_DEPTH_N )
        
    b_proc = np.zeros(len(rs_m.rgns))
    for n in range(len(rs_nd.rgns)):
        if (rs_nd.rgns[n].ave_cvg_depth() <= Ave_depth_th) & (rs_nd.rgns[n].type == 'N'): # & (rs_nd.rgns[n].get_len() > MAX_INTRON_LENGTH): # (rs_nd.rgns[n].type == 'N'):
            r_nd = rs_nd.rgns[n]
            res = check_connection_nd( rs_m, r_nd )
            # b = False
            wh_l = which((res[1,:] > 0)) # & (res[0,:]==0))
            wh_r = which((res[1,:] < 0)) # & (res[0,:]==0))
            if (len(wh_l)>0) & (len(wh_r)>0):
                if (res[0,wh_l[0]] > 0) & (res[0,wh_r[0]] == 0):
                    if (rs_m.rgns[wh_l[0]].cvg[-1] > rs_m.rgns[wh_r[0]].cvg[0]):
                        r_nd.start += int(res[0,wh_l[0]])
                        r_nd.end += int(res[0,wh_l[0]])
                elif (res[0,wh_l[0]] == 0) & (res[0,wh_r[0]] > 0):
                    if (rs_m.rgns[wh_l[0]].cvg[-1] < rs_m.rgns[wh_r[0]].cvg[0]):
                        r_nd.start -= int(res[0,wh_r[0]])               
                        r_nd.end -= int(res[0,wh_r[0]])
    if len(to_del_m) > 0:
        to_del_m.sort(reverse=True)
        for k in to_del_m: del rs_m.rgns[k]
                                
    if len(to_del_nd) > 0:
        to_del_nd.sort(reverse=True)
        for k in to_del_nd: del rs_nd.rgns[k]
                                
    return(rs_nd, rs_m, b)
           

def get_connection_mat(rs_nd, max_dev_n, max_dev_d, max_dev_i):
    
    conn_mat = np.zeros([len(rs_nd.rgns),len(rs_nd.rgns)])
    cvg_vec = np.zeros(len(rs_nd.rgns))
    len_vec = np.zeros(len(rs_nd.rgns))
    for k in range(len(rs_nd.rgns)):
        # conn_mat[k,k] = 1
        cvg_vec[k] = rs_nd.rgns[k].ave_cvg_depth()
        len_vec[k] = rs_nd.rgns[k].get_len()
        
        if (rs_nd.rgns[k].type == 'N'):
            for m in range(len(rs_nd.rgns)):
                if (m!=k) & (rs_nd.rgns[m].type == 'N'):
                    ck = rs_nd.rgns[k].ave_cvg_depth()
                    cm = rs_nd.rgns[m].ave_cvg_depth()
                    bc = ((ck < cm*MAX_CFRAC_N_COMB) & (ck < MAX_CVG_N_COMB)) | ((cm < ck*MAX_CFRAC_N_COMB) & (cm < MAX_CVG_N_COMB))
                    bx = np.sign(rs_nd.rgns[m].xs) == (np.sign(rs_nd.rgns[k].xs)) 
                    if bc & bx: # & (rs_nd.rgns[k].xs == rs_nd.rgns[m].xs):
                        be = (abs(rs_nd.rgns[m].end - rs_nd.rgns[k].end) <= max_dev_n)
                        bs = (abs(rs_nd.rgns[m].start - rs_nd.rgns[k].start) <= max_dev_n)
                        bl = ((rs_nd.rgns[m].end - rs_nd.rgns[m].start) == (rs_nd.rgns[k].end - rs_nd.rgns[k].start))
                        if be & bs & bl:
                            conn_mat[m,k] = 1
                            conn_mat[k,m] = 1
                        
        elif (rs_nd.rgns[k].type == 'I'):
            for m in range(len(rs_nd.rgns)):
                if (m!=k) & (rs_nd.rgns[m].type == 'I'):
                    be = (abs(rs_nd.rgns[m].end - rs_nd.rgns[k].end) <= max_dev_i)
                    bs = (abs(rs_nd.rgns[m].start - rs_nd.rgns[k].start) <= max_dev_i)
                    # bl = ((rs_nd.rgns[m].end - rs_nd.rgns[m].start) == (rs_nd.rgns[k].end - rs_nd.rgns[k].start))
                    if be & bs: # & bl:
                        conn_mat[m,k] = 1
                        conn_mat[k,m] = 1
                        
        elif (rs_nd.rgns[k].type == 'D'):
            for m in range(len(rs_nd.rgns)):
                if (m!=k) & (rs_nd.rgns[m].type == 'D'):
                    be = abs(rs_nd.rgns[m].end - rs_nd.rgns[k].end) <= max_dev_d
                    bs = abs(rs_nd.rgns[m].start - rs_nd.rgns[k].start) <= max_dev_d
                    if be & bs:
                        conn_mat[m,k] = 1
                        conn_mat[k,m] = 1
                    
    return(conn_mat, cvg_vec, len_vec)
    
def arg_max(vec):

    mxv = vec[0]
    mxi = 0
    for k in range(1,len(vec)):
        if mxv < vec[k]:
            mxv = vec[k]
            mxi = k
    return(int(mxi), mxv)
    
def arg_min(vec):

    mxv = vec[0]
    mxi = 0
    for k in range(1,len(vec)):
        if mxv > vec[k]:
            mxv = vec[k]
            mxi = k
    return(int(mxi), mxv)

# target_type should be 'I' or 'D'
def check_complte_overlap( rs_m, rs_nd_or_sti, target_type ): 
    
    vec = np.zeros(len(rs_nd_or_sti.rgns))
    for k, rgn in enumerate(rs_nd_or_sti.rgns):
        if rgn.type == target_type:
            b = False
            for r_m in rs_m.rgns:
                if r_m.does_contain(rgn):
                    b = True
                    break
            if b == False: vec[k] = 1
    return vec
    

def merge_nearby_ndi(rs_nd, max_dev_n, max_dev_d, max_dev_i, no_ovlp_ind_vec = None ):
    
    cm, cv, lv = get_connection_mat(rs_nd, max_dev_n, max_dev_d, max_dev_i)
    b_proc = np.ones(len(rs_nd.rgns))
    to_del = []
    cd = -cv
    odr = cd.argsort()
    for k in range(len(rs_nd.rgns)):
        # k = odr[n]
        if b_proc[k] > 0:
            if np.sum(cm[k,:]) > 0:
                wh = which(cm[k,:] > 0)
                wh.append(k)
                cvs = cv[wh]
                lvs = lv[wh]
                idx, xv = arg_max(cvs)
                cvs[idx] = 0
                idn, nv = arg_max(cvs)
                # idx, nv = arg_max(cvs)
                if xv > nv:
                    wx = wh[idx]
                else:
                    mlen = np.median(lvs)
                    idx = 0
                    for k in range(1,len(lvs)):
                        if lvs[k] == mlen: 
                            idx = k
                            break
                    wx = wh[idx]
                for w in wh:
                    if (w != wx) & (b_proc[w] > 0) :
                        if (rs_nd.rgns[w].type == 'N'):
                            rs_nd.rgns[w].start = rs_nd.rgns[wx].start
                            rs_nd.rgns[w].end = rs_nd.rgns[wx].end
                            # rs_nd.rgns[w].cvg = np.round(rs_nd.rgns[w].ave_cvg_depth())
                        elif (rs_nd.rgns[w].type == 'D'):
                            if no_ovlp_ind_vec[w] == 0:
                                rs_nd.rgns[w].start = rs_nd.rgns[wx].start
                                rs_nd.rgns[w].end = rs_nd.rgns[wx].end
                                # rs_nd.rgns[w].cvg = np.round(rs_nd.rgns[w].ave_cvg_depth())
                        elif (rs_nd.rgns[w].type == 'I'):
                            L = rs_nd.rgns[w].get_len()
                            Lx = rs_nd.rgns[wx].get_len()
                            if L <= Lx:
                                rs_nd.rgns[w].start = rs_nd.rgns[wx].start
                                rs_nd.rgns[w].end = rs_nd.rgns[w].start + L-1
                            else:
                                rs_nd.rgns[w].start = rs_nd.rgns[wx].start
                                rs_nd.rgns[w].end = rs_nd.rgns[w].start + Lx-1
                                rs_nd.rgns[w].cmat = rs_nd.rgns[w].cmat[:,:Lx]

                        rs_nd.rgns[wx].update( rs_nd.rgns[w] )
                        to_del.append(w)
                        b_proc[w] = 0
                    else:
                        b_proc[w] = 0

            b_proc[k] = 0
            
    if len(to_del) > 0:
        to_del = list(set(to_del))
        to_del.sort(reverse=True)
        for k in to_del: del rs_nd.rgns[k]
            
    return(rs_nd, cm)
           
        
def trim_m( rs_nd, rs_m, rs_sti, max_dev, max_dev_d, verbose = False ):
    
    b = False
    fc = 0
    for r_m in rs_m.rgns:
        res = check_connection_m( r_m, rs_nd, max_dev, max_dev_d )
        wh = which( (res[1,:] > 0) & (res[0,:] >= 0)) # Tail part  
        if (len(wh) > 0) : ## m with multiple out
            if (sum(res[0,wh] < 0)==0):
                fc += 1
                b = True
                min_ovlp = np.min(res[0,wh])
                max_ovlp = np.max(res[0,wh])
                if min_ovlp > 0: # != max_ovlp:
                    bb = True
                    if len(rs_sti.rgns) > 0:
                        for r_sti in rs_sti.rgns:
                            if (r_sti.start <= (r_m.end+1)) & (r_sti.start > (r_m.end-int(min_ovlp))):
                                bb = False
                                break
                    if bb:
                        if ((r_m.end-int(min_ovlp)) > r_m.start): # & (np.mean(r_m.cvg[-int(min_ovlp):]) <= r_m.ave_cvg_depth()*0.1):
                            r_m.end -= int(min_ovlp)
                            r_m.cmat = r_m.cmat[:,:-int(min_ovlp)]
                            r_m.get_cvg()
                            # rs_nd.print_short()
            else:
                wh2 = which((res[1,:] > 0) & (res[0,:] <= 0))
                if np.max(res[0,wh2]) < 0:
                    print('ERROR in trim_m(): Study required (0)')
                    r_m.print_short()
                    print(res)
                
        wh = which( (res[1,:] < 0) & (res[0,:] >= 0)) #  Head part   
        if (len(wh) > 0) : ## m with multiple in
            if (sum(res[0,wh] < 0)==0):
                fc += 1
                b = True
                min_ovlp = np.min(res[0,wh])
                max_ovlp = np.max(res[0,wh])
                if min_ovlp > 0: # != max_ovlp:
                    bb = True
                    if len(rs_sti.rgns) > 0:
                        for r_sti in rs_sti.rgns:
                            if (r_sti.start >= r_m.start) & (r_sti.start < (r_m.start + int(min_ovlp))):
                                bb = False
                                break
                    if bb:
                        if ((r_m.start+int(min_ovlp)) < r_m.end): #  & (np.mean(r_m.cvg[:int(min_ovlp)]) <= r_m.ave_cvg_depth()*0.1):
                            r_m.start += int(min_ovlp)
                            r_m.cmat = r_m.cmat[:,int(min_ovlp):]
                            r_m.get_cvg()
                            # rs_nd.print_short()
            else:
                wh2 = which((res[1,:] < 0) & (res[0,:] <= 0))
                if np.max(res[0,wh2]) < 0:
                    print('ERROR in trim_m(): Study required (1)')
                    r_m.print_short()
                    print(res)
                
    return(rs_nd, rs_m, fc)


def trim_d( rs_nd, rs_m, verbose = False, sdiv = 10 ):
    
    b = 0
    to_del = []
    for n in range(len(rs_nd.rgns)):
        if rs_nd.rgns[n].type == 'D':
            r_nd = rs_nd.rgns[n] #.copy()
            for k in range(len(rs_m.rgns)):
                if (r_nd.start > rs_m.rgns[k].start) & (r_nd.end < rs_m.rgns[k].end):
                    '''
                    r_nd.print_short()
                    rs_m.rgns[k].print_short()
                    print(rs_m.rgns[k].get_len(), len(rs_m.rgns[k].cvg), rs_m.rgns[k].cmat.shape)
                    print(rs_m.rgns[k].seq)
                    print('-----')
                    #'''
                    cvg = (rs_m.rgns[k].cvg[r_nd.start-rs_m.rgns[k].start-1] + rs_m.rgns[k].cvg[r_nd.end-rs_m.rgns[k].start+1])*0.5
                    r_nd.cvg_frac = r_nd.ave_cvg_depth()/cvg
                    # print('CD_del: %4.3f <- %4.3f, %4.3f ' % (r_nd.cvg_frac, r_nd.ave_cvg_depth(), cvg))

                    if (r_nd.ave_cvg_depth() >= cvg*D_VALID_CFRAC) & (r_nd.ave_cvg_depth() >= D_VALID_CVG) & (r_nd.cvg_frac < 1000):

                        r_m_new = region(rs_m.rgns[k].chr, r_nd.end+1, rs_m.rgns[k].end, rs_m.rgns[k].type, xs = rs_m.rgns[k].xs)
                        pos = r_nd.end+1 - rs_m.rgns[k].start
                        r_m_new.cmat = rs_m.rgns[k].cmat[:,pos:]
                        r_m_new.get_cvg()

                        rs_m.rgns[k].end = r_nd.start-1
                        Len = rs_m.rgns[k].end - rs_m.rgns[k].start + 1
                        if Len > 0 : 
                            rs_m.rgns[k].cmat = rs_m.rgns[k].cmat[:,:Len]
                            rs_m.rgns[k].get_cvg()
                        if Len == 0: 
                            rs_m.rgns[k] = r_m_new
                        else: 
                            rs_m.rgns.append(r_m_new)
                        b += 1 
                    else :
                        ## remove D if it is too thin
                        to_del.append(n)
                        #pass
                    break
                    
                elif (r_nd.start == rs_m.rgns[k].start) & (r_nd.end < rs_m.rgns[k].end):
                    
                    cvg = rs_m.rgns[k].cvg[r_nd.end-rs_m.rgns[k].start+1] # (rs_m.rgns[k].cvg[0] + rs_m.rgns[k].cvg[r_nd.end-rs_m.rgns[k].start+1])*0.5
                    r_nd.cvg_frac = r_nd.ave_cvg_depth()/cvg
                    # print('CD_del-S: %4.3f <- %4.3f, %4.3f ' % (r_nd.cvg_frac, r_nd.ave_cvg_depth(), cvg))

                    if (r_nd.ave_cvg_depth() >= cvg*D_VALID_CFRAC) & (r_nd.ave_cvg_depth() >= D_VALID_CVG):
                        cut_len = r_nd.get_len()
                        rs_m.rgns[k].start += cut_len 
                        rs_m.rgns[k].cmat = rs_m.rgns[k].cmat[:,cut_len:]
                        rs_m.rgns[k].get_cvg()
                        # to_del.append(n)
                    else :
                        ## remove D if it is too thin
                        if  (r_nd.cvg_frac >= 1000): to_del.append(n)
                        pass
                    break
                    
                elif (r_nd.end == rs_m.rgns[k].end) & (r_nd.start > rs_m.rgns[k].start):
                    
                    cvg = rs_m.rgns[k].cvg[r_nd.start-rs_m.rgns[k].start-1] # (rs_m.rgns[k].cvg[r_nd.start-rs_m.rgns[k].start] + rs_m.rgns[k].cvg[-1])*0.5
                    r_nd.cvg_frac = r_nd.ave_cvg_depth()/cvg
                    # print('CD_del-E: %4.3f <- %4.3f, %4.3f ' % (r_nd.cvg_frac, r_nd.ave_cvg_depth(), cvg))

                    if (r_nd.ave_cvg_depth() >= cvg*D_VALID_CFRAC) & (r_nd.ave_cvg_depth() >= D_VALID_CVG):
                        cut_len = r_nd.get_len()
                        rs_m.rgns[k].end -= cut_len 
                        rs_m.rgns[k].cmat = rs_m.rgns[k].cmat[:,:-cut_len]
                        rs_m.rgns[k].get_cvg()
                        # to_del.append(n)
                    else :
                        ## remove D if it is too thin
                        if  (r_nd.cvg_frac >= 1000): to_del.append(n)
                        pass
                    break

            if r_nd.cvg_frac < 0:
                r_nd.cvg_frac = 1
                                
    if len(to_del) > 0:
        to_del.sort(reverse=True)
        for k in to_del: del rs_nd.rgns[k]
            
    return(rs_nd, rs_m, b)
           
    
def trim_n_short( rs_nd, rs_m, verbose = False, sdiv = 10 ):
    
    min_m_len = rs_m.rgns[0].get_len()
    for rgn in rs_m.rgns: min_m_len = min( min_m_len, rgn.get_len() )
    # min_m_len = max( min_m_len, 0 )  ## r_m의 길이가 너무 작은 것이 있으면 문제 (임시로 해결함)
        
    step = np.ceil(len(rs_nd.rgns)/sdiv)
    b = 0
    for n in range(len(rs_nd.rgns)):
        if ( rs_nd.rgns[n].type == 'N' ) & (rs_nd.rgns[n].get_len() > 0): # & (rs_nd.rgns[n].get_len() < min_m_len):
            r_nd = rs_nd.rgns[n] #.copy()
            for k in range(len(rs_m.rgns)):
                locs = rs_m.rgns[k].contain( r_nd.start )
                loce = rs_m.rgns[k].contain( r_nd.end )
                if ((locs > 0) & (loce > 0) & (loce < (rs_m.rgns[k].get_len()-1)) ) :
                    
                    m1 = locs - min(MAX_DEV_NM, locs)
                    m2 = min(len(rs_m.rgns[k].cvg), locs+MAX_DEV_NM)
                    nd_dep = np.max(rs_m.rgns[k].cvg[m1:m2]) - r_nd.ave_cvg_depth()
                    
                    r_nd_new = region_nd( r_nd.chr, r_nd.start, r_nd.start-1, r_nd.type, (nd_dep), xs=0 ) 
                    r_nd_new.get_cvg()
                    r_nd_new.xs = 0
                    rs_nd.rgns.append(r_nd_new)
                            
                    m1 = loce - min(MAX_DEV_NM, loce)
                    m2 = min(len(rs_m.rgns[k].cvg), loce+MAX_DEV_NM)
                    nd_dep = np.max(rs_m.rgns[k].cvg[m1:m2]) - r_nd.ave_cvg_depth()
                    
                    r_nd_new = region_nd( r_nd.chr, r_nd.end+1, r_nd.end, r_nd.type, (nd_dep), xs=0 ) 
                    r_nd_new.get_cvg()
                    r_nd_new.xs = 0
                    rs_nd.rgns.append(r_nd_new)
                            
                    r_m_new = region(rs_m.rgns[k].chr, r_nd.end+1, rs_m.rgns[k].end, rs_m.rgns[k].type, xs = rs_m.rgns[k].xs)
                    r_m_new.cmat = rs_m.rgns[k].cmat[:,(loce+1):]
                    r_m_new.get_cvg()
                    
                    rs_m.rgns[k].end = r_nd.start-1
                    Len = rs_m.rgns[k].end - rs_m.rgns[k].start + 1
                    if Len > 0 : 
                        rs_m.rgns[k].cmat = rs_m.rgns[k].cmat[:,:Len]
                        rs_m.rgns[k].get_cvg()
                    
                    if Len == 0: rs_m.rgns[k] = r_m_new
                    else: rs_m.rgns.append(r_m_new)
                        
                    b += 1    
                    break
                                
    return(rs_nd, rs_m, b)
           
    
def split_m( rs_nd, rs_m, rs_sti, verbose = False ):
    
    b = False
    fc = 0
    for n in range(len(rs_nd.rgns)):
        if (rs_nd.rgns[n].type == 'N') & (rs_nd.rgns[n].get_len() > 0):
            r_nd = rs_nd.rgns[n] #.copy()
            res = check_connection_nd( rs_m, r_nd, 0 ) 
            
            whp = which( (res[1,:] > 0) )
            whn = which( (res[1,:] < 0) )
            
            if len(whp) == 0:
                pos = r_nd.start
                for k in range(len(rs_m.rgns)):
                    loc = rs_m.rgns[k].contain( pos )
                    if loc > 0:
                        if loc >= rs_m.rgns[k].cmat.shape[1]:
                            print('\n===== %i, %i, %i =====' % (pos,loc,rs_m.rgns[k].cmat.shape[1]))
                            rs_m.rgns[k].print_short()
                            rs_m.print_short()
                            rs_nd.print_short()

                        ## checj if any I is co-located here
                        bt = True
                        for r in rs_sti.rgns:
                            if r.type == 'I':
                                if pos == r.start: bt = False
                        if bt:
                            m1 = loc - min(MAX_DEV_NM, loc)
                            m2 = min(len(rs_m.rgns[k].cvg), loc+MAX_DEV_NM)
                            nd_dep = np.max(rs_m.rgns[k].cvg[m1:m2]) - r_nd.ave_cvg_depth()
                            nd_dep = max(1, nd_dep)
                            r_nd_new = region_nd( r_nd.chr, pos, pos-1, r_nd.type, (nd_dep), xs=0 ) 
                            r_nd_new.get_cvg()
                            r_nd_new.xs = 0
                            rs_nd.rgns.append(r_nd_new)
                        
                        r_m_new = region(rs_m.rgns[k].chr, pos, rs_m.rgns[k].end, rs_m.rgns[k].type, xs = rs_m.rgns[k].xs )
                        r_m_new.cmat = rs_m.rgns[k].cmat[:,loc:]
                        r_m_new.get_cvg()
                        rs_m.rgns.append(r_m_new)

                        rs_m.rgns[k].end = pos-1
                        rs_m.rgns[k].cmat = rs_m.rgns[k].cmat[:,:loc]
                        rs_m.rgns[k].get_cvg()
                        b = True

                        break

            if len(whn) == 0:
                pos = r_nd.end
                for k in range(len(rs_m.rgns)):
                    loc = rs_m.rgns[k].contain( pos )
                    if (loc < (rs_m.rgns[k].end-rs_m.rgns[k].start)) & (loc > 0):
                        
                        ## checj if any I is located here
                        bt = True
                        for r in rs_sti.rgns:
                            if r.type == 'I':
                                if (pos+1) == r.start: bt = False
                        if bt:
                            m1 = loc - min(MAX_DEV_NM, loc)
                            m2 = min(len(rs_m.rgns[k].cvg), loc+MAX_DEV_NM)
                            nd_dep = np.max(rs_m.rgns[k].cvg[m1:m2]) - r_nd.ave_cvg_depth()
                            nd_dep = max(1, nd_dep)
                            r_nd_new = region_nd( r_nd.chr, pos+1, pos, r_nd.type, (nd_dep), xs=0) #np.array([sum(rs_m.rgns[k].cmat[:,loc])]) )
                            r_nd_new.get_cvg()
                            r_nd_new.xs = 0
                            rs_nd.rgns.append(r_nd_new)
                       
                        r_m_new = region(rs_m.rgns[k].chr, pos+1, rs_m.rgns[k].end, rs_m.rgns[k].type, xs = rs_m.rgns[k].xs )
                        r_m_new.cmat = rs_m.rgns[k].cmat[:,(loc+1):]
                        r_m_new.get_cvg()
                        rs_m.rgns.append(r_m_new)

                        rs_m.rgns[k].end = pos
                        rs_m.rgns[k].cmat = rs_m.rgns[k].cmat[:,:(loc+1)]
                        rs_m.rgns[k].get_cvg()
                        b = True

                        break

    return(rs_nd, rs_m, b)
           
    
def add_i( rs_nd, rs_m, rs_sti, verbose = False ):
    
    b = False
    b2 = False
    fc = 0            
    to_del = []
    
    for n in range(len(rs_sti.rgns)):
        if rs_sti.rgns[n].type == 'I':
            r_sti = rs_sti.rgns[n] #.copy()
            
            w_left = -1; loc_left = -1
            w_right = -1; loc_right = -1
            for k in range(len(rs_m.rgns)) :
                if rs_m.rgns[k].type == 'M':
                    loc_left = rs_m.rgns[k].contain_i( r_sti.start-1 )
                    if loc_left >= 0: 
                        w_left = k
                        loc_left = rs_m.rgns[k].get_len() - loc_left -1
                        break
            for k in range(len(rs_m.rgns)) :
                if rs_m.rgns[k].type == 'M':
                    loc_right = rs_m.rgns[k].contain_i( r_sti.start )
                    if loc_right >= 0: 
                        w_right = k
                        break
                    
            if (w_left >= 0) & (w_right >= 0):
                
                if (w_left == w_right) :
                    cvg = r_sti.ave_cvg_depth()
                    r_sti.cvg_frac = cvg / rs_m.rgns[w_left].get_cvg()[loc_left]
                    # if (cvg >= I_VALID_CFRAC*(rs_m.rgns[w_left].get_cvg()[loc_right])) & (r_sti.ave_cvg_depth() >= I_VALID_CVG) : 
                    if (cvg >= (I_VALID_CFRAC*(rs_m.rgns[w_left].get_cvg()[loc_right]))) & (r_sti.ave_cvg_depth() >= I_VALID_CVG) : 
                    
                        r_m_new = region(rs_m.rgns[w_left].chr, r_sti.start, rs_m.rgns[w_left].end, rs_m.rgns[w_left].type, xs=rs_m.rgns[w_left].xs )
                        r_m_new.cmat = np.copy(rs_m.rgns[w_left].cmat[:,loc_right:])
                        r_m_new.cvg = r_m_new.get_cvg()
                        rs_m.rgns.append(r_m_new)

                        rs_m.rgns[w_left].end = r_sti.start-1
                        rs_m.rgns[w_left].cmat = rs_m.rgns[w_left].cmat[:,:loc_right]
                        rs_m.rgns[w_left].get_cvg()

                        rs_m.rgns.append(r_sti) #.copy())
                        b = True
                        
                    else:
                        # pass
                        to_del.append(n)
                        
                elif (w_left != w_right) & (loc_right == 0) & (loc_left == 0):
                    cvg = r_sti.ave_cvg_depth()
                    r_sti.cvg_frac = cvg *2/(rs_m.rgns[w_left].cvg_depth_end()+rs_m.rgns[w_right].cvg_depth_start())
                    # if (cvg >= I_VALID_CFRAC*2/(rs_m.rgns[w_left].cvg_depth_end()+rs_m.rgns[w_right].cvg_depth_start())) & (r_sti.ave_cvg_depth() >= I_VALID_CVG) :  
                    if (cvg >= (I_VALID_CFRAC*(rs_m.rgns[w_left].cvg_depth_end()+rs_m.rgns[w_right].cvg_depth_start())*0.5)) & (r_sti.ave_cvg_depth() >= I_VALID_CVG) :
                        rs_m.rgns.append(r_sti) #.copy())
                        b = True  
                        
                    else:
                        # pass
                        to_del.append(n)
                else:
                    to_del.append(n)
            else:
                to_del.append(n)

    if len(to_del) > 0:
        to_del.sort(reverse=True)
        for k in to_del: del rs_sti.rgns[k]
            
    return(rs_nd, rs_m, b)


##########################################################################
## Functions to handle splice-graph
##########################################################################

def BFS(graph,start,end):

    pq = []
    q = queue.Queue() 
    temp_path = [start]

    q.put(temp_path)

    while q.empty() == False:
        tmp_path = q.get()
        last_node = tmp_path[-1]
        if last_node == end:
            pq.append(tmp_path)

        for link_node in graph[last_node]:
            if link_node not in tmp_path:
                new_path = []
                new_path = tmp_path + [link_node]
                q.put(new_path)
    return(pq)


def BFS1(graph,start,end, max_num_hops = 10):

    b = True
    pq = []
    q = queue.Queue() 
    temp_path = [start]

    q.put(temp_path)

    cnt = 0
    while q.empty() == False:
        tmp_path = q.get()
        last_node = tmp_path[-1]
        if last_node == end:
            pq.append(tmp_path)

        for link_node in graph[last_node]:
            if link_node not in tmp_path:
                new_path = []
                new_path = tmp_path + [link_node]
                q.put(new_path)
        cnt += 1
        if cnt > max_num_hops: break
                
    return(pq)


def BFS2(graph,start,end, max_num_paths = 1000):

    b = True
    pq = []
    q = queue.Queue() 
    temp_path = [start]

    q.put(temp_path)

    while q.empty() == False:
        tmp_path = q.get()
        last_node = tmp_path[-1]
        if last_node == end:
            pq.append(tmp_path)

        for link_node in graph[last_node]:
            if link_node not in tmp_path:
                new_path = []
                new_path = tmp_path + [link_node]
                q.put(new_path)
            if q.qsize() > max_num_paths:
                b = False
                return(pq,b)
                
    return(pq, b)


def BFS3(graph,start,end, max_num_hops = 10):

    b = True
    pq = []
    q = queue.Queue() 
    temp_path = [start]

    q.put(temp_path)

    cnt = 0
    while q.empty() == False:
        tmp_path = q.get()
        last_node = tmp_path[-1]
        if last_node == end:
            pq.append(tmp_path)
            if len(pq) > 0: break

        for link_node in graph[last_node]:
            if link_node not in tmp_path:
                new_path = []
                new_path = tmp_path + [link_node]
                q.put(new_path)
        cnt += 1
        if cnt > max_num_hops: break
        if len(pq) > 0: break
                
    return(pq)

def BFS_all(graph,start, end_nodes):

    pq = []
    q = queue.Queue() 
    temp_path = [start]

    q.put(temp_path)

    while q.empty() == False:
        tmp_path = q.get()
        last_node = tmp_path[-1]
        if last_node in end_nodes:
            pq.append(tmp_path)

        for link_node in graph[last_node]:
            if link_node not in tmp_path:
                new_path = []
                new_path = tmp_path + [link_node]
                q.put(new_path)
    return(pq)


def BFS_all2(graph,start,end_nodes, max_num_paths = 1000):

    b = True
    pq = []
    q = queue.Queue() 
    temp_path = [start]

    q.put(temp_path)

    while q.empty() == False:
        tmp_path = q.get()
        last_node = tmp_path[-1]
        if last_node in end_nodes:
            pq.append(tmp_path)

        for link_node in graph[last_node]:
            if link_node not in tmp_path:
                new_path = []
                new_path = tmp_path + [link_node]
                q.put(new_path)
            if (q.qsize() + len(pq)) > max_num_paths:
                b = False
                return(pq,b)
                
    return(pq, b)


def get_start_nodes(grp):
    Len = len(grp)
    pi = np.zeros(Len)
    for k in range(Len):
        if len(grp[k]) > 0:
            for each in grp[k]: pi[each] += 1
    
    sn_lst = which(pi == 0)
    return(sn_lst)
    
    
def get_end_nodes(grp):
    Len = len(grp)
    en_lst = []
    for k in range(Len):
        if len(grp[k]) == 0: en_lst.append(k)
    return(en_lst)


def get_ambiguous_nodes(grp_f, grp_b, nodes, edges):
    
    asn_lst = []
    aen_lst = []
    cnt = 0
    n_nodes = len(nodes.rgns)
    n_edges = len(edges.rgns)
    for m, nd in enumerate(nodes.rgns):
        ## Check bistranded nodes
        if (len(grp_f[m]) > 0) & (len(grp_b[m]) > 0) & (nd.type == 'M'):
            p1, n1 = 0, 0
            for m1 in grp_f[m]:
                if m1 >= n_nodes:
                    m2 = m1 - n_nodes
                    if edges.rgns[m2].type == 'N':
                        if edges.rgns[m2].xs > 0: p1 += 1
                        elif edges.rgns[m2].xs < 0: n1 += 1

            p2, n2 = 0, 0
            for m1 in grp_b[m]:
                if m1 >= n_nodes:
                    m2 = m1 - n_nodes
                    if edges.rgns[m2].type == 'N':
                        if edges.rgns[m2].xs > 0: p2 += 1
                        elif edges.rgns[m2].xs < 0: n2 += 1

            if ((p1==0) & (n1>0) & (p2>0) & (n2==0)) | ((p1>0) & (n1==0) & (p2==0) & (n2>0)): # r-r or b-b
                asn_lst.append(m)
                aen_lst.append(m)
                cnt += 1

            elif ((p1>0) & (n1>0)) & (((p2==0) & (n2>0)) | ((p2>0) & (n2==0))):
                asn_lst.append(m)
                cnt += 1
            
            elif ((p2>0) & (n2>0)) & (((p1==0) & (n1>0)) | ((p1>0) & (n1==0))):
                aen_lst.append(m)
                cnt += 1
            
            elif ((p1>0) & (n1>0)) & ((p2>0) & (n2>0)):
                pass

    return asn_lst, aen_lst


def get_ambiguous_nodes_old(grp_f, grp_b, nodes, edges):
    
    an_lst = []
    cnt = 0
    n_nodes = len(nodes.rgns)
    n_edges = len(edges.rgns)
    for m, nd in enumerate(nodes.rgns):
        ## Check bistranded nodes
        if (len(grp_f[m]) > 0) & (len(grp_b[m]) > 0) & (nd.type == 'M'):
            p1, n1 = 0, 0
            for m1 in grp_f[m]:
                if m1 >= n_nodes:
                    m2 = m1 - n_nodes
                    if edges.rgns[m2].type == 'N':
                        if edges.rgns[m2].xs > 0: p1 += 1
                        elif edges.rgns[m2].xs < 0: n1 += 1

            p2, n2 = 0, 0
            for m1 in grp_b[m]:
                if m1 >= n_nodes:
                    m2 = m1 - n_nodes
                    if edges.rgns[m2].type == 'N':
                        if edges.rgns[m2].xs > 0: p2 += 1
                        elif edges.rgns[m2].xs < 0: n2 += 1

            if ((p1 > 0) & (n2 > 0 )) | ((n1 > 0) & (p2 > 0 )): 
                an_lst.append(m)
                cnt += 1
            elif ((p1 > 0) & (n1 > 0 )) | ((n2 > 0) & (p2 > 0 )): 
                an_lst.append(m)
                cnt += 1

    return an_lst


def get_all_paths(grp_f, grp_b = None, nodes = None, edges = None):
    
    sn_lst = get_start_nodes(grp_f)
    en_lst = get_end_nodes(grp_f)
    
    cnt = 0
    if (nodes is not None) & (edges is not None):
        asn_lst, aen_lst = get_ambiguous_nodes(grp_f, grp_b, nodes, edges)
        cnt = len(asn_lst) + len(aen_lst)
        sn_lst = sn_lst + asn_lst
        en_lst = en_lst + aen_lst
        
        sn_lst = list(set(sn_lst))
        en_lst = list(set(en_lst))

    path_lst = []
    for sn in sn_lst:
        ends = copy.deepcopy(en_lst)
        if sn in ends:
            ends.remove(sn)
        if len(ends) == 0:
            pq = [[sn]]
        else:
            pq = BFS_all(grp_f,sn,ends)
            if len(pq) == 0: pq = [[sn]]
                
        path_lst = path_lst + pq
            
    if False: # cnt > 0:
        n_nodes = len(nodes.rgns)
        n_edges = len(edges.rgns)
        
        to_del = []
        for k, p in enumerate(path_lst):
            np, nn = 0, 0
            for n in p:
                if n >= n_nodes:
                    if edges.rgns[n-n_nodes].type == 'N':
                        if edges.rgns[n-n_nodes].xs > 0: np += 1
                        elif edges.rgns[n-n_nodes].xs < 0: nn += 1
            if (np > 0) & (nn > 0):
                to_del.append(k)
                
        if len(to_del) > 0:
            to_del = list(set(to_del))
            to_del.sort(reverse=True)
            for k in to_del: del path_lst[k]
    
            
    return(path_lst)


def try_to_get_all_paths(grp_f, grp_b = None, nodes = None, edges = None, max_n_paths = 1000):

    b = True
    sn_lst = get_start_nodes(grp_f)
    en_lst = get_end_nodes(grp_f)

    cnt = 0
    if (nodes is not None) & (edges is not None):
        asn_lst, aen_lst = get_ambiguous_nodes(grp_f, grp_b, nodes, edges)
        cnt = len(asn_lst) + len(aen_lst)
        sn_lst = sn_lst + asn_lst
        en_lst = en_lst + aen_lst
        
        sn_lst = list(set(sn_lst))
        en_lst = list(set(en_lst))

            
    path_lst = []
    for sn in sn_lst:
        ends = copy.deepcopy(en_lst)
        if sn in ends:
            ends.remove(sn)
        if len(ends) == 0:
            pq = [[sn]]
            b = True
        else:
            pq, b = BFS_all2(grp_f,sn, ends, max_n_paths)
            if len(pq) == 0: pq = [[sn]]
        
        if b == False:
            break
        else:
            path_lst = path_lst + pq

    return(path_lst, b)


def get_initial_graph( rs_m, rs_nd ):
    
    n_nodes = len(rs_m.rgns)
    graph = {}
    for k in range(n_nodes): graph[k] = []
    graph_bwd = {}
    for k in range(n_nodes): graph_bwd[k] = []
        
    to_del = []
    for k in range(len(rs_m.rgns)):
        r_m = rs_m.rgns[k] #.copy()
        if r_m.type == 'M':
            res = check_connection_m( r_m, rs_nd, 0 )
            wh_nd = which( (res[1,:] > 0) ) # & (res[0,:] != 0 ) )
            for w in wh_nd:
                r_nd = rs_nd.rgns[w]
                res2 = check_connection_nd( rs_m, r_nd, 0 )
                wh_m = which( (res2[1,:] < 0) ) # & (res[0,:] != 0 ) )
                graph[k] = graph[k] + wh_m

            wh_nd = which( (res[1,:] < 0) ) # & (res[0,:] != 0 ) )
            for w in wh_nd:
                r_nd = rs_nd.rgns[w]
                res2 = check_connection_nd( rs_m, r_nd, 0 )
                wh_m = which( (res2[1,:] > 0) ) # & (res[0,:] != 0 ) )
                graph_bwd[k] = graph_bwd[k] + wh_m

        #'''
        elif r_m.type == 'I':
            w_left = -1
            w_right = -1
            for m in range(len(rs_m.rgns)):
                if (rs_m.rgns[m].type == 'M') & (rs_m.rgns[m].end == (r_m.start-1)): w_left = m
                elif (rs_m.rgns[m].type == 'M') & (rs_m.rgns[m].start == r_m.start): w_right = m

            if (w_left>=0) & (w_right>=0) :
                if True:
                    ## I의 depth가 충분히 크면, I를 연결
                    graph[w_left] =  graph[w_left] + [k]
                    graph[k] =  graph[k] + [w_right]
                    
                    graph_bwd[w_right] =  graph_bwd[w_right] + [k]
                    graph_bwd[k] =  graph_bwd[k] + [w_left]
                else:
                    graph[w_left] =  graph[w_left] + [w_right]
                    
                    graph_bwd[w_right] =  graph_bwd[w_right] + [w_left]
                    to_del.append(k)
                    ## I의 depth가 충분히 크지 않으면 I를 연결하지 않음
                    ## print('ERROR in Graph Building (0): I too thin --> May cause error.' )

            else:
                to_del.append(k)
        #'''   

    #'''
    b = False
    if len(to_del) > 0:
        to_del = list(set(to_del))
        to_del.sort(reverse=True)
        for k in to_del: del rs_m.rgns[k]
        b = True
    #'''
    return( graph, graph_bwd, b )


def get_graph( rs_m, rs_nd ):
    
    n_nodes = len(rs_m.rgns)
    n_edges = len(rs_nd.rgns)
    
    graph_fwd = {}
    for k in range(n_nodes+n_edges): graph_fwd[k] = []
    graph_bwd = {}
    for k in range(n_nodes+n_edges): graph_bwd[k] = []
        
    to_del = []
    for k in range(len(rs_m.rgns)):
        r_m = rs_m.rgns[k] #.copy()
        if r_m.type == 'M':
            res = check_connection_m( r_m, rs_nd, 0 )
            wh_nd = which( (res[1,:] > 0) ) # & (res[0,:] != 0 ) )
            graph_fwd[k] = graph_fwd[k] + [w+n_nodes for w in wh_nd]

            wh_nd = which( (res[1,:] < 0) ) # & (res[0,:] != 0 ) )
            graph_bwd[k] = graph_bwd[k] + [w+n_nodes for w in wh_nd]

        #'''
        elif r_m.type == 'I':
            w_left = -1
            w_right = -1
            for m in range(len(rs_m.rgns)):
                if (rs_m.rgns[m].type == 'M') & (rs_m.rgns[m].end == (r_m.start-1)): w_left = m
                elif (rs_m.rgns[m].type == 'M') & (rs_m.rgns[m].start == r_m.start): w_right = m

            if (w_left>=0) & (w_right>=0) :
                if True: 
                    graph_fwd[w_left] =  graph_fwd[w_left] + [k]
                    graph_fwd[k] =  graph_fwd[k] + [w_right]
                    
                    graph_bwd[w_right] =  graph_bwd[w_right] + [k]
                    graph_bwd[k] =  graph_bwd[k] + [w_left]
                else:
                    graph_fwd[w_left] =  graph_fwd[w_left] + [w_right]
                    
                    graph_bwd[w_right] =  graph_bwd[w_right] + [w_left]
                    to_del.append(k)

            else:
                to_del.append(k)
        #'''   

    #'''
    b = False
    if len(to_del) > 0:
        to_del = list(set(to_del))
        to_del.sort(reverse=True)
        for k in to_del: del rs_m.rgns[k]
        b = True
    #'''
    
    for k in range(len(rs_nd.rgns)):
        r_nd = rs_nd.rgns[k] #.copy()
        if (r_nd.type == 'N') | (r_nd.type == 'D'):
            res = check_connection_nd( rs_m, r_nd, 0 )
            wh_m = which( (res[1,:] < 0) ) # & (res[0,:] != 0 ) )
            graph_fwd[k+n_nodes] = graph_fwd[k+n_nodes] + wh_m

            wh_m = which( (res[1,:] > 0) ) # & (res[0,:] != 0 ) )
            graph_bwd[k+n_nodes] = graph_bwd[k+n_nodes] + wh_m

    return graph_fwd, graph_bwd, rs_m, rs_nd, b 

##############################
## Functions to run ElasticNet

def ms(ary):
    return( sum(ary**2) )


def run_ElasticNet( X, y, l1r = 0.5, alpha = 1 ):

    lmb = False
    if alpha < MIN_ALPHA_FOR_EN: 
        alpha = MIN_ALPHA_FOR_EN
        lmb = True
        
    ## MultiTaskElasticNet regressor and its parameters to use
    regressor = lm.ElasticNet()
    param = {'alpha': alpha, 'l1_ratio': l1r, 'fit_intercept':False, 'max_iter': 1000, \
             'copy_X': True, 'positive': True, 'random_state': 0, 'normalize': True } # , 'selection': 'random' }
    regressor.set_params(**param)
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")    
        regressor.fit(X.transpose(),y)
    coef = regressor.coef_

    n_samples = len(y)
    L1 = sum(abs(coef))
    L2 = ms(coef)
    mse = ms(y-np.dot(X.transpose(),coef))
    cost = 1/(2*n_samples)*mse + alpha*l1r*L1 + 0.5*alpha*(1-l1r)*L2

    return(coef, cost, lmb)


def run_ElasticNet_path( X, y, l1r = 0.5, n_alphas = 100 ):

    ## MultiTaskElasticNet regressor and its parameters to use
    regressor = lm.ElasticNet()
    param = {'l1_ratio': l1r, 'fit_intercept':False, 'max_iter': 400, \
             'copy_X': True, 'positive': True, 'random_state': 0, 'normalize': True } #, 'selection': 'random' }
    regressor.set_params(**param)
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")    
        alphas, coefs, gaps = regressor.path(X.transpose(),y, l1_ratio = l1r, n_alphas = n_alphas)

    return(coefs, alphas, gaps)


###############################
## functions for graph handling

def group_nodes(grp_f):
    
    start_nodes = get_start_nodes(grp_f)
    end_nodes = get_end_nodes(grp_f)

    bps = np.full(len(start_nodes),-1,dtype=np.int32)
    bpe = np.full(len(end_nodes),-1,dtype=np.int32)
    g_cnt = 0
    
    whs = which(bps < 0)
    if len(whs) > 0:
        ws = whs[0]
        bps[ws] = g_cnt
            
    while True:
        
        n_new = 0
        
        whs = which(bps == g_cnt)
        whe = which(bpe < 0)
        
        if (len(whe) > 0) & (len(whs) > 0):
            for ws in whs:
                sn = start_nodes[ws]
                for we in whe:
                    en = end_nodes[we]
                    plst = BFS(grp_f, sn, en)
                    if len(plst) > 0:
                        n_new += 1
                        bpe[we] = g_cnt
                    
        whe = which(bpe == g_cnt)
        whs = which(bps < 0)
        if (len(whe) > 0) & (len(whs) > 0):
            for we in whe:
                en = end_nodes[we]
                for ws in whs:
                    sn = start_nodes[ws]
                    plst = BFS(grp_f, sn, en)
                    if len(plst) > 0:
                        n_new += 1
                        bps[ws] = g_cnt
        
        if n_new == 0:
            g_cnt += 1
            if (sum(bps<0) == 0) & (sum(bpe<0) == 0):
                break
            else:
                whs = which(bps < 0)
                if len(whs) > 0:
                    ws = whs[0]
                    bps[ws] = g_cnt
                
    grp_idx = np.full(len(grp_f),-1,dtype=np.int32)
    for k in range(g_cnt):
        
        whs = which(bps == k)
        whe = which(bpe == k)
        
        for ws in whs:
            sn = start_nodes[ws]
            for we in whe:
                en = end_nodes[we]
                plst = BFS(grp_f, sn, en)
                if len(plst) > 0:
                    for p in plst:
                        for node in p:
                            grp_idx[node] = k
           
    return(grp_idx, g_cnt)


def minimize_graph(g_f_in, g_b_in):
    
    # rs_m = rs_m_incopy()
    n_nodes = len(g_f_in)
    g_f = copy.deepcopy(g_f_in)
    g_b = copy.deepcopy(g_b_in)
    b_del = np.zeros(n_nodes)
    b = True
    while b == True:
        b = False
        for k in range(n_nodes):
            if (b_del[k] == 0) & (len(g_f[k])==1):
                m = g_f[k][0]
                if (b_del[m] == 0) & (len(g_b[m])==1) :
                    b_del[m] = 1
                    g_f[k] = copy.deepcopy(g_f[m])
                    b = True
                    break

    if sum(b_del) != 0:
        wh = which( b_del == 0 )            
        graph_new_fwd = {}
        for k in range(len(wh)):
            w = wh[k]
            next_nodes_lst = []
            if len(g_f[w]) == 0:
                graph_new_fwd[k] = next_nodes_lst
            else:
                graph_new_fwd[k] = [wh.index(m) for m in g_f[w]]

        return graph_new_fwd
    else:
        return g_f_in


def get_partial_path(g_f, g_b, start):
    
    path = []
    v = start
    path = [v]
    while True:
        if len(g_f[v]) == 0:
            return( path )
        elif len(g_f[v]) == 1:
            e = g_f[v][0] # this should be an edge.
            if len(g_f[e]) == 1:
                w = g_f[e][0]
                if len(g_b[w]) == 1:
                    path.append(e)
                    path.append(w)
                    v = w
                else:
                    return(path)
            else:
                print('ERROR in get_partial_path(): N_nodes_connected_to_an_edge = %i' % len(g_b[e]) )
                
        elif len(g_f[v]) > 1:
            return(path)


def check_new_start( g_f, g_b, nidx ):
    
    if len(g_b[nidx]) != 1:
        return(True)
    else:
        pe = g_b[nidx][0]
        pn = g_b[pe][0]
        if len(g_f[pn]) > 1:
            return(True)
        else:
            return(False)
        

def get_minimal_graph(g_f, g_b, n_nodes, n_edges, nodes, wgt_edge = None, ga = None):
    
    if n_edges == 0:

        graph_new_fwd = g_f 
        graph_new_bwd = g_b
        nodes_ext = [[k] for k in range(len(nodes.rgns)) ]
        n_nodes_ext = n_nodes 
        n_edges_ext = 0 
        wgt_ext = np.zeros(0) 
        ber = 0
        return(graph_new_fwd, graph_new_bwd, nodes_ext, n_nodes_ext, n_edges_ext, wgt_ext, ber)
        
    else:  
        # combine nodes and edges having single connection into one node
        b_del = np.ones(n_nodes+n_edges)
        b = True
        ns_ext = []
        sn = []
        for k in range(n_nodes):
            if b_del[k] > 0:
                if nodes.rgns[k].type == 'M':
                    bs = check_new_start(g_f, g_b, k)
                    if bs:
                        sn.append(k)
                        path = get_partial_path(g_f, g_b, k)
                        ns_ext.append(path)
                        for m in path:
                            b_del[m] = 0

        if sum(b_del) == 0: # singly connected graph

            nodes_ext = ns_ext
            n_nodes_ext = len(ns_ext) 
            n_edges_ext = 0 
            wgt_ext = np.zeros(0) 
            ber = 0
            graph_new_fwd = {} 
            graph_new_bwd = {}
            for k in range(n_nodes_ext):
                graph_new_fwd[k] = []
                graph_new_bwd[k] = []

        else:
            ber = 0
            n_nodes_new = len(ns_ext)
            wh = which( b_del == 1 )
            if (min(wh) < n_nodes): ## all should be edge indices
                if (nodes.rgns[min(wh)].type == 'M'):
                    print('ERROR in get_minimal_graph(): incomplete min: %i < %i, %s' % (min(wh), n_nodes, nodes.rgns[min(wh)].type) )
                    if ga is not None: ga.print_short()
                    ber = 1
                    
            es_ext = []
            wgt_ext = np.zeros(len(wh))
            for k, w in enumerate(wh):
                eidx = [k]
                es_ext.append([w])
                if wgt_edge is not None: wgt_ext[k] = wgt_edge[w]

            graph_new_fwd = {} 
            graph_new_bwd = {}
            for k in range(len(ns_ext)+len(es_ext)):
                graph_new_fwd[k] = []
                graph_new_bwd[k] = []

            ##
            e_cov = np.ones(len(wh))*2
            for k in range(len(ns_ext)):
                be = ns_ext[k][-1]
                if len(g_f[be]) == 0:
                    graph_new_fwd[k] = []
                else:
                    for m, w in enumerate(g_f[be]):
                        eidx = wh.index(w) + n_nodes_new
                        graph_new_fwd[k].append(eidx)
                        graph_new_bwd[eidx].append(k)
                        e_cov[wh.index(w)] -= 1

                fe = ns_ext[k][0]
                if len(g_b[fe]) == 0:
                    graph_new_bwd[k] = []
                else:
                    graph_new_bwd[k] = []
                    for m, w in enumerate(g_b[fe]):
                        eidx = wh.index(w) + n_nodes_new
                        graph_new_bwd[k].append(eidx)
                        graph_new_fwd[eidx].append(k)
                        e_cov[wh.index(w)] -= 1

            if sum(e_cov) != 0:
                print('ERROR in get_minimal_graph(): some edges not covered. ', e_cov)
                ber = 4

            nodes_ext = ns_ext + es_ext
            n_nodes_ext = len(ns_ext)
            n_edges_ext = len(es_ext)

    return(graph_new_fwd, graph_new_bwd, nodes_ext, n_nodes_ext, n_edges_ext, wgt_ext, ber)


def get_org_path( p_lst, nodes_ext ):
    
    p_lst_recon = []
    for p in p_lst:
        path = []
        for n in p:
            path = path + nodes_ext[n]
        p_lst_recon.append(path)
            
    return(p_lst_recon)


##########################

def find_closest_from( rs_m, k, b_proc, gf, gb ):
    
    n = -1
    mode = 0
    dist = 1000000
    
    for m in range(len(rs_m.rgns)):
        if (b_proc[m] == 0):
            
            if (m < k) & (len(gf[m]) == 0) & (len(gb[k]) == 0) :
                dist_tmp = (rs_m.rgns[k].start - rs_m.rgns[m].end)
                if (dist_tmp < dist) & (dist_tmp >= 0):
                    dist = dist_tmp
                    mode = -1
                    n = m
                    if dist < 0: 
                        print('ERROR in find_closest_from(A): %i, %i, %i (%i-%i), (%i-%i)' % \
                              (dist, mode, m,rs_m.rgns[m].start,rs_m.rgns[m].end,rs_m.rgns[k].start,rs_m.rgns[k].end) )
                        
            if (m > k) & (len(gb[m]) == 0) & (len(gf[k]) == 0) :
                dist_tmp = (rs_m.rgns[m].start - rs_m.rgns[k].end)
                if (dist_tmp < dist) & (dist_tmp >= 0):
                    dist = dist_tmp
                    mode = 1
                    n = m
                    if dist < 0: 
                        print('ERROR in find_closest_from(B): %i, %i, %i (%i-%i), (%i-%i)' % \
                              (dist, mode, m,rs_m.rgns[k].start,rs_m.rgns[k].end,rs_m.rgns[m].start,rs_m.rgns[m].end) )
            
    return( n, mode, dist )     


def compare_path(p1, p2):
    
    if len(p1) != len(p2):
        return(False)
    else:
        b = True
        for k in range(len(p1)):
            if p1[k] != p2[k]:
                b = False
                break
        return(b)

def get_eq_path_idx(plst, p):
    
    idx = -1
    for k in range(len(plst)):
        b = compare_path(plst[k],p)
        if b == True: 
            idx = k
            break
            
    return(idx)       
        

##########################################################################
## Functions and objects to handle GTF file
##########################################################################

# GTF_line = collections.namedtuple('GTF_line', 'chr, src, feature, start, end, score, strand, frame, attr')
GTF_line = collections.namedtuple('GTF_line', 'chr, src, feature, start, end, score, strand, frame, attr, gid, gname, tid, tname, biotype')
CHR, SRC, FEATURE, GSTART, GEND, SCORE, STRAND, FRAME, ATTR, GID, GNAME, TID, TNAME, BIOTYPE = [i for i in range(14)]

def print_gtf(line):
    print('%s, %s, %i-%i, %s-%s ' % (line.chr, line.feature, line.start, line.end, line.gid, line.tid ) )

def print_gtf_lines(lines):
    for k, line in enumerate(lines):
        print('%i: %s, %s, %i-%i, %s-%s ' % (k, line.chr, line.feature, line.start, line.end, line.gid, line.tid ) )

def print_gtf_lines_to_str(lines):
    s_lst = []
    for k, line in enumerate(lines):
        s = '%i: %s, %s, %i-%i, %s-%s ' % (k, line.chr, line.feature, line.start, line.end, line.gid, line.tid )
        s_lst.append(s)
    return s

def get_gtf_lines_from_rgns( r_lst_m, r_lst_nd ):

    gtf_line_lst = []

    for n in range(len(r_lst_m)):
        
        rs_m = r_lst_m[n]
        rs_nd = r_lst_nd[n]

        if len(rs_m.rgns) > 0:
            
            chrm = rs_m.rgns[0].chr            
            span = rs_m.get_span()
            g_id = 'StringFix.%i' % n
            attr = 'gene_id "%s";' % (g_id)
            gtf_line = GTF_line( chrm, GTF_SOURCE, 'gene', span.start, span.end, '.', \
                                 '+', '.', attr, g_id, g_id, '', '', '' )
            gtf_line_lst.append(gtf_line)
            
            pos = np.zeros( len(rs_m.rgns) )
            for k in range(len(rs_m.rgns)): pos[k] = rs_m.rgns[k].start
            odr = pos.argsort()

            for k in range(len(rs_m.rgns)):
                m = odr[k]
                rgn = rs_m.rgns[m]
                t_id = 'StringFix.%i.%i' % (n,k)
                attr = 'gene_id "%s"; transcript_id "%s"; abn "%4.1f"; length "%i";' % \
                        (g_id, t_id, rgn.ave_cvg_depth(), rgn.get_len())
                gtf_line = GTF_line( chrm, GTF_SOURCE, 'exon', rgn.start, rgn.end, '.', '+', '.', \
                                     attr, g_id, g_id, t_id, t_id, '' )
                gtf_line_lst.append(gtf_line)

    return( gtf_line_lst)


def get_id_and_name_from_gtf_attr(str_attr):
    
    gid = ''
    gname = ''
    tid = ''
    tname = ''
    biotype = ''
    
    items = str_attr.split(';')
    for item in items[:-1]:
        sub_item = item.split()
        if sub_item[0] == 'gene_id':
            gid = sub_item[1].replace('"','')
        elif sub_item[0] == 'gene_name':
            gname = sub_item[1].replace('"','')
        elif sub_item[0] == 'transcript_id':
            tid = sub_item[1].replace('"','')
        elif sub_item[0] == 'transcript_name':
            tname = sub_item[1].replace('"','')
        elif sub_item[0] == 'gene_biotype':
            biotype = sub_item[1].replace('"','')
        elif sub_item[0] == 'transcript_biotype':
            biotype = sub_item[1].replace('"','')
    
    for item in items[:-1]:
        sub_item = item.split()
        if sub_item[0] == 'ref_gene_id':
            gid = sub_item[1].replace('"','')
        elif sub_item[0] == 'ref_gene_name':
            gname = sub_item[1].replace('"','')
        elif sub_item[0] == 'reference_id':
            tid = sub_item[1].replace('"','')
    
    return gid, gname, tid, tname, biotype


def get_other_attrs_from_gtf_attr(str_attr):
    
    exon_num = -1
    cov = -1
    abn = -1
    seq = None
    event = None
    status = None
    cfrac = -1
    
    items = str_attr.split(';')
    for item in items[:-1]:
        sub_item = item.split()
        if sub_item[0] == 'exon_number':
            exon_num = int(sub_item[1].replace('"',''))
        elif sub_item[0] == 'cvg':
            cov = np.float32(sub_item[1].replace('"',''))
        elif (sub_item[0] == 'abn') | (sub_item[0] == 'cov'):
            abn = np.float32(sub_item[1].replace('"',''))
        elif sub_item[0] == 'seq':
            seq = sub_item[1].replace('"','')
        elif sub_item[0] == 'event':
            event = sub_item[1].replace('"','')
        elif sub_item[0] == 'status':
            status = sub_item[1].replace('"','')
        elif sub_item[0] == 'cfrac':
            cfrac = np.float32(sub_item[1].replace('"',''))
    
    return exon_num, cov, abn, seq, event, status, cfrac

    
def load_gtf( fname, verbose = True, ho = False ):
    
    gtf_line_lst = []
    hdr_lines = []
    if verbose: print('Loading GTF ... ', end='', flush = True)

    f = open(fname,'r')
    if ho:
        for line in f:
            
            if line[0] == '#':
                # line.replace('#','')
                cnt = 0
                for m, c in enumerate(list(line)):
                    if c != '#': break
                    else: cnt += 1
                hdr_lines.append(line[cnt:-1])
            else:
                break
    else:
        for line in f:
            
            if line[0] == '#':
                # line.replace('#','')
                cnt = 0
                for m, c in enumerate(list(line)):
                    if c != '#': break
                    else: cnt += 1
                hdr_lines.append(line[cnt:-1])
            else:
                items = line[:-1].split('\t')
                if len(items) >= 9:
                    chrm = items[0]
                    src = items[1]
                    feature = items[2]
                    start = np.int(items[3])
                    end = np.int(items[4])
                    score = items[5]
                    strand = items[6]
                    frame = items[7]
                    attr = items[8]
                    gid, gname, tid, tname, biotype = get_id_and_name_from_gtf_attr(attr)
                    gl = GTF_line(chrm, src, feature, start, end, score, strand, frame, attr, gid, gname, tid, tname, biotype)
                    gtf_line_lst.append(gl)
        
    f.close()
    if verbose: print('done %i lines. ' % len(gtf_line_lst))
    
    return(gtf_line_lst, hdr_lines)

    
def save_gtf( fname, gtf_line_lst, hdr = None ):
    
    gtf_lines_str = []
    for gtf_line in gtf_line_lst:
        s = '%s\t%s\t%s\t%i\t%i\t%s\t%s\t%s\t%s\n' % \
            (gtf_line.chr,    gtf_line.src,     gtf_line.feature, gtf_line. start, gtf_line.end, \
             gtf_line.score,  gtf_line.strand,  gtf_line.frame,   gtf_line.attr )
        gtf_lines_str.append(s)
    
    f = open(fname,'w+')

    if hdr is not None:
        for line in hdr:
            f.writelines('# ' + line + '\n')

    '''
    for gtf_line in gtf_line_lst:
        s = '%s\t%s\t%s\t%i\t%i\t%s\t%s\t%s\t%s\n' % \
            (gtf_line.chr,    gtf_line.src,     gtf_line.feature, gtf_line. start, gtf_line.end, \
             gtf_line.score,  gtf_line.strand,  gtf_line.frame,   gtf_line.attr ) 
        f.writelines(s)
    '''
    f.writelines(''.join(gtf_lines_str))
    f.close()


def save_gtf2( fname, gtf_line_lst = None, hdr = None, fo = None, close = False ):
    
    if fo is None:
        f = open(fname,'w+')
    else: 
        f = fo

    if hdr is not None:
        for line in hdr:
            f.writelines('# ' + line + '\n')

    if (gtf_line_lst is not None) :
        if (len(gtf_line_lst) > 0):
            gtf_lines_str = []
            for gtf_line in gtf_line_lst:
                s = '%s\t%s\t%s\t%i\t%i\t%s\t%s\t%s\t%s\n' % \
                    (gtf_line.chr,    gtf_line.src,     gtf_line.feature, gtf_line. start, gtf_line.end, \
                     gtf_line.score,  gtf_line.strand,  gtf_line.frame,   gtf_line.attr )
                gtf_lines_str.append(s)

            f.writelines(''.join(gtf_lines_str))

    if close:
        f.close()

    return f

   
def save_gff( fname, gtf_line_lst ):
    
    gtf_lines_str = []
    for gtf_line in gtf_line_lst:
        s = '%s\t%s\t%s\t%i\t%i\t%s\t%s\t%s\t%s\n' % \
            (gtf_line.chr,    gtf_line.src,     gtf_line.feature, gtf_line. start, gtf_line.end, \
             gtf_line.score,  gtf_line.strand,  gtf_line.frame,   gtf_line.attr )
        gtf_lines_str.append(s)
        
    f = open(fname,'w+')
    '''
    for gtf_line in gtf_line_lst:            
        s = '%s\t%s\t%s\t%i\t%i\t%s\t%s\t%s\t%s\n' % \
            (gtf_line.chr,    gtf_line.src,    gtf_line.feature, gtf_line. start, gtf_line.end, \
             gtf_line.score,  gtf_line.strand, gtf_line.frame,   gtf_line.attr)
        f.writelines(s)
    '''
    f.writelines(gtf_lines_str)
    f.close()


##########################################################################
## Functions and objects to build splice-graph
##########################################################################

# GTF_line = collections.namedtuple('GTF_line', 'chr, src, feature, start, end, \
#                                    score, strand, frame, attr, gid, gname, tid, tname')
# CHR, SRC, FEATURE, GSTART, GEND, SCORE, STRAND, FRAME, ATTR, GID, GNAME, TID, TNAME = [i for i in range(13)]
        
    
def get_strand_char(strand):
    if strand < 0:
        c = '-'
    elif strand > 0:
        c = '+'
    else:
        c = '.'
    return c

'''
Transcript = collections.namedtuple('Transcript', \
                                    'prefix, gidx, grp_size, icnt, chr, start, end, \
                                     strand, cdng, seq, abn, tpm, iso_frac, prob, nexs, gvol')
'''
    
def get_tr_name( tr_lst ):
    
    tnames = []
    for tr in tr_lst:
        strand_c = get_strand_char(tr.strand)
        s = '%s_%s:%i-%i_%s_%s_%s_%i_%i_Abn:%4.3f_TPM:%4.2f_IFrac:%3.2f_P:%f_NE:%i_V:%i_L:%i' % \
            (tr.prefix, tr.chr, tr.start, tr.end, strand_c, tr.cdng, str(tr.gidx), tr.grp_size, tr.icnt, tr.abn, tr.tpm, \
             tr.iso_frac, tr.prob, tr.nexs, tr.gvol, len(tr.seq))
        tnames.append(s)
    return tnames


def get_gtf_lines_from_transcripts(tlst, path_lst, nodes, edges, strand = 0 ):

    tr_names = get_tr_name( tlst )
    gtf_lines = []
        
    for k, t in enumerate(tlst):
        
        strand_c = get_strand_char(t.strand)
        g_id = 'StringFix.%i' % t.gidx
        t_id = '%s' % tr_names[k]
        attr = 'gene_id "%s"; transcript_id "%s"; abn "%4.2f"; TPM "%4.2f";' % \
                (g_id, t_id, t.abn, t.tpm)
        gline = GTF_line(t.chr, GTF_SOURCE, 'transcript', t.start, t.end, \
                         1000, strand_c, '.', attr, g_id, g_id, t_id, t_id, '')
        gtf_lines.append(gline)
        cnt = 0
        for m,n in enumerate(path_lst[k]):
            if n < len(nodes.rgns):
                if nodes.rgns[n].type == 'M':
                    cnt += 1
                    attr2 = 'gene_id "%s"; transcript_id "%s"; exon_number "%i"; abn "%4.2f";' % \
                            (g_id, t_id, cnt, t.abn)
                    gline = GTF_line(t.chr, GTF_SOURCE, 'exon', nodes.rgns[n].start, nodes.rgns[n].end, \
                                     1000, strand_c, '.', attr2, g_id, g_id, t_id, t_id, '')
                    gtf_lines.append(gline)
            else:
                d = n - len(nodes.rgns)
                if edges.rgns[d].type == 'D':
                    cnt += 1
                    attr2 = 'gene_id "%s"; transcript_id "%s"; exon_number "%i"; abn "%4.2f";' % \
                            (g_id, t_id, cnt, t.abn)
                    gline = GTF_line(t.chr, GTF_SOURCE, 'exon', edges.rgns[d].start, edges.rgns[d].end, \
                                     1000, strand_c, '.', attr2, g_id, g_id, t_id, t_id)
                    gtf_lines.append(gline)
                
    return  gtf_lines       
                        
    

class splice_graph:
    
    def __init__(self, read_len, cnt = 0):
        
        self.read_len = read_len
        self.gcnt = cnt
        
        self.n_nodes = 0
        self.nodes = regions()
        self.graph_fwd = {}
        self.graph_bwd = {}
        self.n_paths = 0
        self.path_lst = []

        self.n_edges = 0
        self.edges = regions_nd()
        self.graph_f = {}
        self.graph_b = {}
        self.n_p = 0
        self.p_lst = []
        self.s_lst = []
        self.c_lst = []
        self.cov_lst = []
        self.strand = 0
        
        self.cvgs = None
        self.lens = None
        self.abn = None
        
        self.y = None
        self.H = None
        self.z = None
        self.G = None
        
        ## Only FYI
        self.nodes_min = []
        self.n_nodes_min = 0
        self.n_edges_min = 0
        self.graph_f_min = {}
        self.graph_b_min = {}
        self.n_p_min = 0
        self.p_lst_min = []
        
        self.cvgs_min = None
        self.lens_min = None
        
        self.z_min = None
        self.G_min = None
                
        self.n_p_detected = 0
        self.p_lst_detected = []
        self.n_p_candidate = 0
        self.p_lst_candidate = []

        self.bistranded = False
        self.np_in = self.n_p
        self.np_out = self.n_p


    def revise_graphs( self, to_del_nodes, to_del_edges ):

        n_nodes = self.n_nodes
        if len(to_del_nodes) > 0:
            to_del_nodes.sort(reverse = True)
            for k in to_del_nodes:
                del self.nodes.rgns[k]
            n_nodes = len(self.nodes.rgns)

        n_edges = self.n_edges
        if len(to_del_edges) > 0:
            to_del_edges.sort(reverse = True)
            for k in to_del_edges:
                del self.edges.rgns[k]
            n_edges = len(self.edges.rgns)

        cnt = 0
        imap = {}
        for k in range(self.n_nodes):
            if k not in to_del_nodes:
                imap[k] = cnt
                cnt += 1
        for k in range(self.n_edges):
            if k not in to_del_edges:
                imap[k+self.n_nodes] = cnt
                cnt += 1
        to_del_edges2 = [k+self.n_nodes for k in to_del_edges]
        to_del = to_del_edges2 + to_del_nodes

        g_f = {}
        for key in self.graph_f.keys():
            if key not in to_del:
                g_f[ imap[key] ] = []
                for n in self.graph_f[key]:
                    if n not in to_del: g_f[ imap[key] ].append( imap[n] )
        
        g_b = {}
        for key in self.graph_b.keys():
            if key not in to_del:
                g_b[ imap[key] ] = []
                for n in self.graph_b[key]:
                    if n not in to_del: g_b[ imap[key] ].append( imap[n] )
                                                 

        g_fwd = {}
        for key in self.graph_fwd.keys():
            if key not in to_del:
                g_fwd[ imap[key] ] = []
                for n in self.graph_fwd[key]:
                    if n not in to_del: g_fwd[ imap[key] ].append( imap[n] )
        
        g_bwd = {}
        for key in self.graph_bwd.keys():
            if key not in to_del:
                g_bwd[ imap[key] ] = []
                for n in self.graph_bwd[key]:
                    if n not in to_del: g_bwd[ imap[key] ].append( imap[n] )
        
        self.n_nodes = n_nodes
        self.n_edges = n_edges
        self.graph_f = g_f
        self.graph_b = g_b                                                 
        self.graph_fwd = g_fwd
        self.graph_bwd = g_bwd
        
        return self.nodes, self.edges
    
        
    def get_splice_graphs(self, rs_m, rs_nd):
        
        b = True
        while b:
            
            self.graph_f, self.graph_b, rs_m, rs_nd, b = get_graph( rs_m, rs_nd )

            self.n_nodes = len(rs_m.rgns)               
            self.n_edges = len(rs_nd.rgns)
            
            if not b:
                #'''
                self.nodes = regions()
                self.nodes.rgns = rs_m.rgns
                self.nodes.set_cvg()
                self.nodes.set_r_cnt(rs_m.cnt_r, rs_m.cnt_s)
                
                # self.n_edges = len(rs_nd.rgns)
                self.edges = regions_nd()
                # for k in range(len(rs_nd.rgns)): 
                #     self.edges.rgns.append(rs_nd.rgns[k])
                self.edges.rgns = rs_nd.rgns
                self.edges.set_cvg()
                #'''
                # self.nodes = rs_m.copy(update = True)
                # self.edges = rs_nd.copy()
                
                # self.graph_fwd, self.graph_bwd, b = get_initial_graph( rs_m, rs_nd )  
                self.graph_fwd = {k: [] for k in range(self.n_nodes)}
                self.graph_bwd = {k: [] for k in range(self.n_nodes)}
                
                for k in range(self.n_nodes):
                    next_nodes = self.graph_f[k]
                    for n_or_e in next_nodes:
                        if n_or_e < self.n_nodes:
                            self.graph_fwd[k].append(n_or_e)
                        else:
                            if len(self.graph_f[n_or_e]) == 1:
                                nn = self.graph_f[n_or_e][0]
                                self.graph_fwd[k].append( nn )
                            else:
                                pass
                                # print('WARNING in get_splice_graphs: A %i' % len(self.graph_f[n_or_e]) )
        
                    prev_nodes = self.graph_b[k]
                    for n_or_e in prev_nodes:
                        if n_or_e < self.n_nodes:
                            self.graph_bwd[k].append(n_or_e)
                        else:
                            if len(self.graph_b[n_or_e]) == 1:
                                nn = self.graph_b[n_or_e][0]
                                self.graph_bwd[k].append( nn )
                            else:
                                pass
                                # print('WARNING in get_splice_graphs: B %i' % len(self.graph_b[n_or_e]) )

        
    def get_all_paths(self):
        
        self.p_lst = []
        # self.p_lst = get_all_paths(self.graph_f)
        self.p_lst = get_all_paths(self.graph_f, self.graph_b, self.nodes, self.edges)
        self.n_p = len(self.p_lst)
        
        
    def get_cvgs_and_lens(self):
        cvgn, lenn = self.nodes.get_cvgs_and_lens()
        cvge, lene = self.edges.get_cvgs_and_lens()
        
        self.cvgs = np.concatenate((cvgn, cvge))
        self.lens = np.concatenate((lenn, lene))

        
    def get_stuffs(self, rs_m, rs_nd):
        
        self.get_splice_graphs(rs_m, rs_nd)
        self.get_all_paths()
        self.get_cvgs_and_lens()
        
    def revise_stuffs(self, to_del_nodes, to_del_edges):
        
        self.revise_graphs(to_del_nodes, to_del_edges)
        self.get_all_paths()
        self.get_cvgs_and_lens()
        
        
    ####################################################
    ### If any start and end node is an edge, remove it

    def rem_edge_start(self):

        rs_m = self.nodes
        rs_nd = self.edges

        start_nodes = get_start_nodes(self.graph_f)
        end_nodes = get_end_nodes(self.graph_f)        
        to_del = []
        to_del_m = []
        for k in start_nodes:
            if (k >= self.n_nodes): 
                to_del.append(k-self.n_nodes)
            else:
                if rs_m.rgns[k].type == 'I': 
                    to_del_m.append(k)
                
        for k in end_nodes:
            if (k >= self.n_nodes):
                to_del.append(k-self.n_nodes)
            else:
                if rs_m.rgns[k].type == 'I': 
                    to_del_m.append(k)
               
        b = False
        if len(to_del) > 0:
            # print('WARNING in build(A): %i Unconnected edges' % len(to_del) )
            to_del = list(set(to_del))
            # to_del.sort(reverse=True)
            # for k in to_del: del rs_nd.rgns[k]
            b = True
                        
        if len(to_del_m) > 0:
            # print('WARNING in build(A): %i Unconnected edges' % len(to_del) )
            to_del_m = list(set(to_del_m))
            # to_del_m.sort(reverse=True)
            # for k in to_del_m: del rs_m.rgns[k]
            b = True
                 
        if b:
            # self.get_splice_graphs(rs_m, rs_nd)
            self.revise_graphs(to_del_m, to_del)

        return self.nodes, self.edges
    
                   
    ###########################################
    # Find unconnected node (island) and remove
    # Use graph_f
    
    def rem_unconnected(self, len_th = 100, cvg_th = 2):
        
        rs_m = self.nodes
        rs_nd = self.edges

        grp_cnt = 0
        for k in range(len(rs_m.rgns)):
            if ((len(self.graph_f[k])==0) & (len(self.graph_b[k])==0)): grp_cnt += 1
        
        if (grp_cnt > 1):
            to_del = []
            for k in range(len(rs_m.rgns)):
                if ((len(self.graph_f[k])==0) & (len(self.graph_b[k])==0)):
                    if (rs_m.rgns[k].get_len() < len_th): # & (rs_m.rgns[k].ave_cvg_depth() <= cvg_th): 
                        to_del.append(k)
                        
            if len(to_del) > 0:
                # to_del.sort(reverse=True)
                # for k in to_del: del rs_m.rgns[k]
                    
                # self.get_splice_graphs(rs_m, rs_nd)
                self.revise_graphs(to_del, [])
                
        return self.nodes, self.edges
    
    
    def rem_low_cvg(self, ath = 0, c_th = None):

        rs_m = self.nodes
        rs_nd = self.edges
        graph_f = self.graph_f
        graph_b = self.graph_b
        
        nn = len(rs_m.rgns)
        if c_th is None:
            mc_m = 100000
            mc_nd = 10000
            #'''
            for k in range(len(rs_m.rgns)):
                if (rs_m.rgns[k].type == 'M') & ((len(graph_f[k])>0) | (len(graph_b[k])>0)):
                    mc_m = min(mc_m, np.ceil(rs_m.rgns[k].ave_cvg_depth()))
            #'''
            for k in range(len(rs_nd.rgns)):
                if (rs_nd.rgns[k].type == 'N') & ((len(graph_f[int(k+nn)])>0) | (len(graph_b[int(k+nn)])>0)):
                    mc_nd = min(mc_nd, np.ceil(rs_nd.rgns[k].ave_cvg_depth()))

            mc = np.ceil(min(mc_m,mc_nd)) + ath
        else:
            mc = c_th + ath
        
        to_del = []
        for k in range(len(rs_m.rgns)):
            if (rs_m.rgns[k].type == 'M') & ((len(graph_f[k])>0) | (len(graph_b[k])>0)):
                if rs_m.rgns[k].ave_cvg_depth() <= mc :
                    to_del.append(k)
                    
        to_del_nd = []
        #'''
        for k in range(len(rs_nd.rgns)):
            if (rs_nd.rgns[k].type == 'N') & ((len(graph_f[int(k+nn)])>0) | (len(graph_b[int(k+nn)])>0)):
                if rs_nd.rgns[k].ave_cvg_depth() <= mc :
                    to_del_nd.append(k)
        #'''
        b = False            
        if len(to_del) > 0:
            # to_del.sort(reverse=True)
            # for k in to_del: del rs_m.rgns[k]
            b = True
                
        if len(to_del_nd) > 0:
            # to_del_nd.sort(reverse=True)
            # for k in to_del_nd: del rs_nd.rgns[k]
            b = True
        
        if b:
            # self.get_splice_graphs(rs_m, rs_nd)
            rs_m, rs_nd = self.revise_graphs(to_del, to_del_nd)
            
        return rs_m, rs_nd, mc
 

   ####################################
    # Find Not-connected node
    # and connect it to the closest node
        
    def connect_closest_unconnected_nodes(self):
    
        rs_m = self.nodes
        rs_nd = self.edges
        
        b = False
        # gi, grp_cnt = group_nodes(self.graph_fwd)
        
        if (self.n_nodes > 1): #  & (grp_cnt > 1):
            
            to_del = []
            b_proc = np.zeros(self.n_nodes)
            
            max_dist_uc_to_conn = MAX_DIST_UC_TO_CONN
            cvgn, lenn = rs_m.get_cvgs_and_lens()
            Tlen = max(1, np.sum(lenn))
            ave_cvg_dep = np.sum(cvgn*lenn)/Tlen
            nn = 0
            for e in rs_nd.rgns: 
                if e.type == 'N': nn += 1
            if nn <= 1: 
                max_dist_uc_to_conn *= 2 
                if ave_cvg_dep < 20:
                    max_dist_uc_to_conn *= 2
            
            for k in range(self.n_nodes):

                if ((len(self.graph_fwd[k])==0) | (len(self.graph_bwd[k])==0)) & (b_proc[k] == 0):

                    m, mode, dist = find_closest_from( rs_m, k, b_proc, self.graph_fwd, self.graph_bwd )
                    
                    if (b_proc[m] == 0): # & (dist <= MAX_DIST_UC_TO_CONN): #  & (rs_m.rgns[k].ave_cvg_depth() >= min_depth_to_connect) :
                        
                        if ((dist <= max_dist_uc_to_conn)):
                        
                            if (mode > 0) & (len(self.graph_fwd[k])==0) & (len(self.graph_bwd[m])==0): # k--m
                                
                                Len = rs_m.rgns[k].get_len()
                                cmat_tmp = rs_m.rgns[k].cmat
                                ave_cvg_depth = rs_m.rgns[k].ave_cvg_depth()
                                seq = rs_m.rgns[k].get_seq() + gen_seq('N',dist)
                                rs_m.rgns[k].end = rs_m.rgns[m].start
                                rs_m.rgns[k].cmat = NTstr2CMat(seq)*((ave_cvg_depth+rs_m.rgns[m].ave_cvg_depth())*0.5)
                                rs_m.rgns[k].cmat[:,:Len] = cmat_tmp
                                rs_m.rgns[k].cmat[:,-1] = 0
                                ub = rs_m.rgns[m].update(rs_m.rgns[k])
                                rs_m.rgns[m].get_cvg()
                                if ub != True:
                                    print('ERROR in build(): Update:', ub, rs_m.rgns[m].ave_cvg_depth(), m, k )                        
                                
                                self.graph_bwd[m] = self.graph_bwd[k]
                                if len(self.graph_bwd[k]) > 0:
                                    for kp in self.graph_bwd[k]:
                                        for j in range(len(self.graph_fwd[kp])) :
                                            if self.graph_fwd[kp][j] == k: self.graph_fwd[kp][j] = m
                                
                                to_del.append(k)
                                b_proc[k] = 1

                            elif (mode < 0)  & (len(self.graph_bwd[k])==0) & (len(self.graph_fwd[m])==0): # m--k
                                
                                Len = rs_m.rgns[k].get_len()
                                cmat_tmp = rs_m.rgns[k].cmat
                                ave_cvg_depth = rs_m.rgns[k].ave_cvg_depth()
                                seq = gen_seq('N',dist) + rs_m.rgns[k].get_seq()
                                rs_m.rgns[k].start = rs_m.rgns[m].end
                                rs_m.rgns[k].cmat = NTstr2CMat(seq) # *int(round(ave_cvg_depth))
                                rs_m.rgns[k].cmat[:,-Len:] = cmat_tmp
                                rs_m.rgns[k].cmat[:,0] = 0
                                ub = rs_m.rgns[m].update(rs_m.rgns[k])
                                rs_m.rgns[m].get_cvg()
                                if ub != True:
                                    print('ERROR in build(): Update:', ub, rs_m.rgns[m].ave_cvg_depth(), m, k )                        
                                
                                self.graph_fwd[m] = self.graph_fwd[k]
                                if len(self.graph_fwd[k]) > 0:
                                    for kn in self.graph_fwd[k]:
                                        for j in range(len(self.graph_bwd[kn])) :
                                            if self.graph_bwd[kn][j] == k: self.graph_bwd[kn][j] = m
                                
                                to_del.append(k)
                                b_proc[k] = 1

            if len(to_del) > 0:
                to_del.sort(reverse=True)
                for k in to_del: del rs_m.rgns[k]
                b = True
                        
        self.get_splice_graphs(rs_m, rs_nd)
    
        return self.nodes, self.edges

    
    def build( self, rs_m, rs_nd, trim = True, len_th = 100 ): 

        self.__init__(self.read_len, self.gcnt)
            
        self.get_splice_graphs(rs_m, rs_nd)
        self.rem_edge_start()
        
        if trim: 
            rs_m, rs_nd = self.connect_closest_unconnected_nodes()

            while True: 
                
                to_del = []
                sn = np.array( get_start_nodes(self.graph_f) )
                en = np.array( get_end_nodes(self.graph_f) )
                
                if len(sn) > 1:
                    cvgs = np.zeros(len(sn), dtype=np.float32)
                    lens = np.zeros(len(sn), dtype=np.int32)
                    numo = np.ones(len(sn), dtype=np.int32)
                    nsib = np.zeros(len(sn), dtype=np.int32)
                    lenN = np.ones(len(sn), dtype=np.int32)*1000000
                    for k, s in enumerate(sn):
                        if s < self.n_nodes:
                            numo[k] = len(self.graph_f[s])
                            cvgs[k] = (rs_m.rgns[s].ave_cvg_depth())
                            lens[k] = np.int(rs_m.rgns[s].get_len())
                            if len(self.graph_f[s]) == 1:
                                e = self.graph_f[s][0]
                                if e >= self.n_nodes:
                                    lenN[k] = rs_nd.rgns[e-self.n_nodes].get_len()
                                else:
                                    lenN[k] = rs_m.rgns[e].get_len()
                                m = self.graph_f[e][0] 
                                nsib[k] = len(self.graph_b[m])
                        else:
                            print('ERROR (A) occurred while trimmimg start/end nodes.')
                    # vols = cvgs # *lens
                    mxv = cvgs.max()
                    b1 = (cvgs < mxv*MAX_PRUNING_CFRAC) & (cvgs < MAX_PRUNING_DEPTH) & (lens < self.read_len*0.7)
                    b2 = (lens < MIN_START_END_LENGTH) & (lenN == 0) # JJatoori
                    b = (b2 | b1) & (numo == 1) & (nsib > 1)
                    #'''
                    for k in range(len(b)):
                        if len(self.graph_f[sn[k]]) > 0:
                            b[k] = False
                            break
                    if np.sum(b) == len(b):
                        odr = lens.argsort()
                        b[odr[-1]] = False
                    #'''
                        
                    to_del = list(sn[b])


                if len(en) > 1:
                    cvge = np.zeros(len(en), dtype=np.float32)
                    lene = np.zeros(len(en), dtype=np.int32)
                    numi = np.ones(len(en), dtype=np.int32)
                    nsib = np.zeros(len(en), dtype=np.int32)
                    lenN = np.ones(len(en), dtype=np.int32)*1000000
                    for k, s in enumerate(en):
                        if s < self.n_nodes:
                            numi[k] = len(self.graph_b[s])
                            cvge[k] = (rs_m.rgns[s].ave_cvg_depth())
                            lene[k] = np.int(rs_m.rgns[s].get_len())    
                            if len(self.graph_b[s]) == 1:
                                e = self.graph_b[s][0]
                                if e >= self.n_nodes:
                                    lenN[k] = rs_nd.rgns[e-self.n_nodes].get_len()
                                else:
                                    lenN[k] = rs_m.rgns[e].get_len()
                                m = self.graph_b[e][0] 
                                nsib[k] = len(self.graph_f[m])
                        else:
                            print('ERROR (B) occurred while trimmimg start/end nodes.')
                    # vole = cvge # *lene
                    mxv = cvge.max()
                    b1 = (cvge < mxv*MAX_PRUNING_CFRAC) & (cvge < MAX_PRUNING_DEPTH) & (lene < self.read_len*0.7)
                    b2 = (lene < MIN_START_END_LENGTH) & (lenN == 0) # JJatoori
                    b = (b2 | b1) & (numi == 1) & (nsib > 1)
                    #'''
                    for k in reversed(range(len(b))):
                        if len(self.graph_b[en[k]]) > 0:
                            b[k] = False
                            break
                    if np.sum(b) == len(b):
                        odr = lene.argsort()
                        b[odr[-1]] = False
                    #'''

                    to_del = to_del + list(en[b])


                b = False
                if len(to_del) > 0:
                    to_del = list(set(to_del))
                    to_del_nodes = []
                    to_del_edges = []
                    for k in to_del: 
                        if k < self.n_nodes:
                            to_del_nodes.append(k)
                        else:
                            to_del_edges.append(k-self.n_nodes)
                    b = True
                else:
                    break

                if b: 
                    if len(to_del_nodes) == len(rs_m.rgns): return False, self.nodes, self.edges
                    else:
                        self.revise_graphs(to_del_nodes, to_del_edges)
                        self.rem_unconnected( len_th = len_th)
                        self.rem_edge_start()

                if len(self.nodes.rgns) == 0: return False, self.nodes, self.edges

        return True, self.nodes, self.edges
    
    
    def select_nodes_and_edges(self, len_th = 200, cvg_th = 0.01):

        ###################
        ## Initial prunning

        mn = 0
        cnt = 0
        
        while True:
            p_lst, b = try_to_get_all_paths(self.graph_f, self.graph_b, self.nodes, self.edges, \
                                            max_n_paths = MAX_NUM_PATHS_INIT)
            if b == False:
                a = np.floor(cnt*0.33)
                rs_m, rs_nd, mn = self.rem_low_cvg( ath = a)
                self.rem_edge_start()
            else:
                break                
        
        rs_m, rs_nd = self.rem_unconnected( len_th = len_th)
        
        if len(rs_m.rgns) == 0: 
            return False, 0, 0, rs_m, rs_nd
        
        ################################
        ## Remove thin bypass junctions
        
        to_del = []
        for k, r in enumerate(rs_nd.rgns):
            if (r.type == 'N'):
                # if (r.ave_cvg_depth() == 1):
                #     to_del.append(k)
                if (r.ave_cvg_depth() <= MAX_BYPASS_DEPTH):
                    e = k+self.n_nodes
                    mf = self.graph_b[e][0]
                    mb = self.graph_f[e][0]
                    plst = BFS( self.graph_f, mf, mb )
                    if len(plst) == 0: # False -> Not implemented
                        for p in plst:
                            if e not in p:
                                pp = p[1:-1]
                                if (len(pp) == 3) & (pp[1] < self.n_nodes):
                                    if (rs_m.rgns[pp[1]].type == 'M') & (rs_m.rgns[pp[1]].get_len() <= MAX_BYPASS_LENGTH):
                                        if r.ave_cvg_depth() <= rs_m.rgns[pp[1]].ave_cvg_depth()*MAX_BYPASS_CFRAC:
                                            if (pp[0] >= self.n_nodes) & (pp[2] >= self.n_nodes):
                                                e1 = pp[0] - self.n_nodes
                                                e2 = pp[2] - self.n_nodes
                                                if (rs_nd.rgns[e1].get_len()==0) | (rs_nd.rgns[e2].get_len()==0):
                                                     to_del.append(k)
                    #'''
                    elif len(plst) >= 2:
                        ac = np.zeros(len(plst), dtype=np.float32)
                        al = np.zeros(len(plst), dtype=np.float32)
                        for m, p in enumerate(plst):
                            if e not in p:
                                pp = p[1:-1]
                                cnt = 0
                                for n in pp:
                                    if n < self.n_nodes:
                                        if rs_m.rgns[n].type == 'M':
                                            al[m] += rs_m.rgns[n].get_len()
                                            cnt += rs_m.rgns[n].get_len()
                                            ac[m] += rs_m.rgns[n].ave_cvg_depth()*rs_m.rgns[n].get_len()
                                if cnt > 0: ac[m] = ac[m]/cnt
                        mxac = ac.max()
                        mxal = al.max()
                        if (r.ave_cvg_depth() < mxac*MAX_BYPASS_CFRAC): # & (mxal <= MAX_BYPASS_LENGTH): 
                            to_del.append(k)
                    #'''
                                            
        if len(to_del) > 0:
            to_del.sort(reverse=True)
            # for k in to_del: del rs_nd.rgns[k]
            rs_m, rs_nd = self.revise_graphs( [], to_del )
        #'''
                         
        if len(rs_m.rgns) == 0: 
            return False, 0, 0, rs_m, rs_nd
        else: 
            self.get_all_paths()
            
            if self.n_p > 0:
                self.np_in = self.n_p
                # psel = max(0, (min(self.n_p,MAX_NUM_PATHS1)-MAX_NUM_PATHS2)/(MAX_NUM_PATHS1 - MAX_NUM_PATHS2))*0.5
                # self.select_path_and_remove_nodes_and_edges(rs_m, rs_nd, MAX_NUM_PATHS2, psel)
                psel = np.int(max(0, (min(self.n_p,MAX_NUM_PATHS)-np.int(MAX_NUM_PATHS*0.5))/(MAX_NUM_PATHS - np.int(MAX_NUM_PATHS*0.5)))*0.5)
                self.select_path_and_remove_nodes_and_edges(np.int(MAX_NUM_PATHS*0.5), psel)
                self.np_out = self.n_p
                
                ## connect exons connected with length 0 edge
                to_del_nodes = []
                to_del_edges = []
                for m, r in enumerate(rs_m.rgns):
                    if (m not in to_del) & (len(self.graph_f[m]) == 1):
                        e = self.graph_f[m][0]
                        if e >= self.n_nodes:
                            m2 = e - self.n_nodes
                            if (rs_nd.rgns[m2].type == 'N') & (rs_nd.rgns[m2].get_len() == 0):
                                m1 = self.graph_f[e][0]
                                if (m1 not in to_del) & (len(self.graph_b[m1]) == 1):
                                    if rs_m.rgns[m1].start == (r.end+1):
                                        r.concatenate(rs_m.rgns[m1])
                                        rs_m.rgns[m1] = r.copy()
                                        to_del_nodes.append(m)
                                        to_del_edges.append(e - self.n_nodes)
                                
                if (len(to_del_nodes) + len(to_del_edges)) > 0:
                    self.revise_stuffs(to_del_nodes, to_del_edges)
            else:
                return False, 0, 0, self.nodes, self.edges
                
        return True, mn, cnt, self.nodes, self.edges


    def select_path_and_remove_nodes_and_edges(self, n_sel_max, psel = 0.5, len_th = 200):

        rs_m = self.nodes
        rs_nd = self.edges
        
        gvol = rs_m.get_volume()
        plen = np.zeros(self.n_p, dtype=np.float32)        
        pvol = np.zeros(self.n_p, dtype=np.float32)        
        for k, p in enumerate(self.p_lst):
            for n in p:
                if n < self.n_nodes:
                    plen[k] += rs_m.rgns[n].get_len()
                    pvol[k] += rs_m.rgns[n].get_len()*rs_m.rgns[n].ave_cvg_depth()
                else:
                    pvol[k] += rs_nd.rgns[n-self.n_nodes].ave_cvg_depth()*self.read_len
             
        #'''
        pvol_max = pvol.max()
        odr = pvol.argsort()
        idx = np.int(psel*len(pvol))
        pvol_med = pvol[odr[idx]]
        b = (plen >= len_th) & (pvol >= pvol_med) # & (plen >= plen_max*psel)
        #'''
        
        if gvol < 300*self.read_len:
            idx = np.int( np.ceil(gvol/(100*self.read_len)) )
            b[odr[:-idx]] = False
        else:
            if np.sum(b) > n_sel_max: b[odr[:-n_sel_max]] = False
        
        b_del = np.zeros(self.n_nodes+self.n_edges)
        for k, p in enumerate(self.p_lst):
            if b[k]:
                for n in p: b_del[n] = 1
                    
        to_del = which( b_del == 0 )
        if len(to_del) > 0:
            to_del_nodes = []
            to_del_edges = []
            for k in to_del: 
                if k < self.n_nodes:
                    to_del_nodes.append(k)
                else:
                    to_del_edges.append(k - self.n_nodes)

            self.revise_stuffs(to_del_nodes, to_del_edges)
            
        return
            
    
    def convert_to_text_lines(self, sel = None):
        
        lmat = np.zeros([self.n_nodes,self.n_nodes])
        cmat = np.zeros([self.n_nodes,self.n_nodes])
        cvec = np.zeros(self.n_nodes)
        lvec = np.zeros(self.n_nodes)
        Type = []
        cs = np.zeros(self.n_nodes)
        ce = np.zeros(self.n_nodes)
        
        for k in range(self.n_nodes):
            Type.append(self.nodes.rgns[k].type)
            cvec[k] = self.nodes.rgns[k].ave_cvg_depth()
            lvec[k] = self.nodes.rgns[k].get_len()
            cs[k] = self.nodes.rgns[k].cvg[0]
            ce[k] = self.nodes.rgns[k].cvg[-1]
            for m in self.graph_fwd[k]:
                mf = set(self.graph_f[k])
                mb = set(self.graph_b[m])
                if (len(mf) == 1) & (len(mb)==1) & (mf == set([m])) & (mb == set([k])):
                    if self.nodes.rgns[k].type == 'M':
                        cmat[k,m] = self.nodes.rgns[m].ave_cvg_depth()
                        lmat[k,m] = self.nodes.rgns[m].get_len()
                    else:
                        cmat[k,m] = self.nodes.rgns[k].ave_cvg_depth()
                        lmat[k,m] = self.nodes.rgns[k].get_len()
                else:
                    lst = list( mf.intersection(mb) )
                    if len(lst) == 1:
                        idx = lst[0]
                        if idx < self.n_nodes:
                            cmat[k,m] = self.nodes.rgns[idx].ave_cvg_depth()
                            lmat[k,m] = self.nodes.rgns[idx].get_len()
                        else:
                            if self.edges.rgns[idx%self.n_nodes].xs == 0:
                                cmat[k,m] = self.edges.rgns[idx%self.n_nodes].ave_cvg_depth()
                                lmat[k,m] = self.edges.rgns[idx%self.n_nodes].get_len()
                            else:
                                cmat[k,m] = self.edges.rgns[idx%self.n_nodes].ave_cvg_depth()*np.sign(self.edges.rgns[idx%self.n_nodes].xs)
                                lmat[k,m] = self.edges.rgns[idx%self.n_nodes].get_len()
                    else:
                        print('ERROR in save_graph_to_file(A): %i @ %i,%i' % (len(lst), k, m))
                        print(mf)
                        print(mb)
       
        line_lst = []
        line = '%i\n' % self.n_nodes
        line_lst.append(line)
        
        line = ''
        for k in range(self.n_nodes):
            if k == (self.n_nodes-1):
                line = line + '%s\n' % Type[k]
            else:
                line = line + '%s\t' % Type[k]
        line_lst.append(line)
       
        line = ''
        for k in range(self.n_nodes):
            if k == (self.n_nodes-1):
                line = line + '%f\n' % cvec[k]
            else:
                line = line + '%f\t' % cvec[k]
        line_lst.append(line)
       
        line = ''
        for k in range(self.n_nodes):
            if k == (self.n_nodes-1):
                line = line + '%f\n' % lvec[k]
            else:
                line = line + '%f\t' % lvec[k]
        line_lst.append(line)
        
        line = ''
        for k in range(self.n_nodes):
            if k == (self.n_nodes-1):
                line = line + '%f\n' % cs[k]
            else:
                line = line + '%f\t' % cs[k]
        line_lst.append(line)
       
        line = ''
        for k in range(self.n_nodes):
            if k == (self.n_nodes-1):
                line = line + '%f\n' % ce[k]
            else:
                line = line + '%f\t' % ce[k]
        line_lst.append(line)
       
        ## edge depth
        for m in range(self.n_nodes):
            line = ''
            for k in range(self.n_nodes):
                if k == (self.n_nodes-1):
                    line = line + '%f\n' % cmat[m,k]
                else:
                    line = line + '%f\t' % cmat[m,k]
            line_lst.append(line)

        ## edge length
        for m in range(self.n_nodes):
            line = ''
            for k in range(self.n_nodes):
                if k == (self.n_nodes-1):
                    line = line + '%f\n' % lmat[m,k]
                else:
                    line = line + '%f\t' % lmat[m,k]
            line_lst.append(line)

        if sel is None:
            sel = [m for m in range(self.n_p_detected)]
            
        line_lst.append('%i\n' % len(sel))
        for k in range(self.n_p_detected):
            if k in sel:
                line = 'P%4i: ' % (k)
                for m in self.p_lst_detected[k]:
                    if m < self.n_nodes:
                        line = line + '-%i(%i)-' % (m, np.round(self.nodes.rgns[m].ave_cvg_depth()))
                line = line + '\n'
                line_lst.append(line)
            
        line_lst.append('%i\n' % len(sel))
        for k in range(self.n_p_detected):
            nd_cnt = 0
            if k in sel:
                line = ''
                for m in self.p_lst_detected[k]:
                    if m < self.n_nodes:
                        line = line + '%i\t' % m
                        nd_cnt += 1
                line = line + '\n'
                line = '%i\t%i\t' % (k, nd_cnt) + line
                line_lst.append(line)
            
        line_lst.append('%i\n' % self.n_p_candidate)
        for k in range(self.n_p_candidate):
            nd_cnt = 0
            line = ''
            for m in self.p_lst_candidate[k]:
                if m < self.n_nodes:
                    line = line + '%i\t' % m
                    nd_cnt += 1
            line = line + '\n'
            line = '%i\t%i\t' % (k, nd_cnt) + line
            line_lst.append(line)
            
        return line_lst
    
            
    def print_minimal(self):
        print('=== %i ===' % self.gcnt)
        self.nodes.print_short()
        self.edges.print_short()
        print('Graph(fwd, bwd): %i, %i ' % (self.n_nodes, self.n_edges) )
        for k in range(self.n_nodes):
            print('    %d: ' % k, end='')
            print(self.graph_fwd[k], ' , ', end='')
            print(self.graph_bwd[k])
        print('Graph(f,b): %i, %i ' % (self.n_nodes, self.n_edges) )
        for k in range(self.n_nodes+self.n_edges):
            print('    %d: ' % k, end='')
            print(self.graph_f[k], ' , ', end='')
            print(self.graph_b[k])
        g = minimize_graph(self.graph_f, self.graph_b)   
        #'''
        print('------')
                
    def print_short(self):
        print('=== %i ===' % self.gcnt)
        self.nodes.print_short()
        self.edges.print_short()
        print('Graph(fwd, bwd): %i, %i ' % (self.n_nodes, self.n_edges) )
        for k in range(self.n_nodes):
            print('    %d: ' % k, end='')
            print(self.graph_fwd[k], ' , ', end='')
            print(self.graph_bwd[k])
        print('Graph(f,b): %i, %i ' % (self.n_nodes, self.n_edges) )
        for k in range(self.n_nodes+self.n_edges):
            print('    %d: ' % k, end='')
            print(self.graph_f[k], ' , ', end='')
            print(self.graph_b[k])
        g = minimize_graph(self.graph_f, self.graph_b)   
        print('Minimized Graph: %i ' % (len(g)) )
        for k in range(len(g)):
            print('    %d: ' % k, end='')
            print(g[k])
        #'''
        print('Paths')
        for k in range(self.n_p):
            print('    P%i: ' % (k), end='' )
            for m in self.p_lst[k]:
                if m >= self.n_nodes:
                    Len = self.edges.rgns[m-self.n_nodes].get_len()
                    Cvg = self.edges.rgns[m-self.n_nodes].ave_cvg_depth()
                    xs = self.edges.rgns[m-self.n_nodes].xs
                    print('[%i: %i,%i,%3.1f] ' % (m,xs,Len,Cvg), end='' )
                else:
                    Len = self.nodes.rgns[m].get_len()
                    Cvg = self.nodes.rgns[m].ave_cvg_depth()
                    xs = self.nodes.rgns[m].xs
                    print('(%i: %i,%3.1f) ' % (m,Len,Cvg), end='' )
            print(' ')
        #'''
        print('------')
                
            
    def print_full(self):
        print('=== %i ===' % self.gcnt)
        self.nodes.print_short()
        self.edges.print_short()
        print('Graph(fwd): %i, %i ' % (self.n_nodes, self.n_edges) )
        for k in range(self.n_nodes+self.n_edges):
            print('    %d: ' % k, end='')
            print(self.graph_f[k])
        print('Graph(bwd): %i, %i ' % (self.n_nodes, self.n_edges) )
        for k in range(self.n_nodes+self.n_edges):
            print('    %d: ' % k, end='')
            print(self.graph_b[k])
        g = minimize_graph(self.graph_f, self.graph_b)   
        print('Minimized Graph: %i ' % (len(g)) )
        for k in range(len(g)):
            print('    %d: ' % k, end='')
            print(g[k])
        print('Paths')
        for k in range(self.n_p):
            print('    P%i [%3.1f]: ' % (k, self.abn[k]), end='' )
            for m in self.p_lst[k]:
                if m >= self.n_nodes:
                    Len = self.edges.rgns[m-self.n_nodes].get_len()
                    Cvg = self.edges.rgns[m-self.n_nodes].ave_cvg_depth()
                else:
                    Len = self.nodes.rgns[m].get_len()
                    Cvg = self.nodes.rgns[m].ave_cvg_depth()
                print('(%i: %i,%3.1f) ' % (m,Len,Cvg), end='' )
            print(' ')
        print('======')
        
        
    def get_paths_over_minimal_graph(self):
        
        # cvgn, lenn = self.nodes.get_cvgs_and_lens()
        # cvge, lene = self.edges.get_cvgs_and_lens()
        # wgt_edge = np.concatenate((cvgn,cvge))
        wgt_edge = self.cvgs

        g_f, g_b, nodes_ext, nne, nee, wgt_ext, b = get_minimal_graph(self.graph_f, self.graph_b, self.n_nodes, \
                                                                 self.n_edges, self.nodes, wgt_edge, self )

        self.nodes_min = nodes_ext ## including edges_ext
        self.n_nodes_min = nne
        self.n_edges_min = nee
        self.graph_f_min = g_f
        self.graph_b_min = g_b
        self.p_lst_min = get_all_paths(self.graph_f_min)
        self.n_p_min = len(self.p_lst_min)
        
        self.p_lst_min = get_all_paths(self.graph_f_min) 
        self.n_p_min = len(self.p_lst_min)
    
        self.cvgs_min = np.zeros(nne+nee,dtype=np.float32)
        self.lens_min = np.zeros(nne+nee,dtype=np.float32)
        
        sn = get_start_nodes(self.graph_f_min)
        en = get_end_nodes(self.graph_f_min)
        
        ## nodes_ext
        for k in range(nne):
            Len = 0
            Vol = 0
            for n in self.nodes_min[k]:
                if n < self.n_nodes:
                    Len_tmp = self.nodes.rgns[n].get_len()
                    Vol += self.nodes.rgns[n].ave_cvg_depth()*Len_tmp
                    Len += Len_tmp
            self.lens_min[k] = Len
            self.cvgs_min[k] = Vol/Len
            
        ## edges_ext
        for m in range(nee):
            k = m + nne
            if self.nodes_min[k][0] >= self.n_nodes: 
                n = self.nodes_min[k][0] - self.n_nodes
                self.lens_min[k] = self.edges.rgns[n].get_len()
                self.cvgs_min[k] = self.edges.rgns[n].ave_cvg_depth()
            else:
                n = self.nodes_min[k][0]
                self.lens_min[k] = self.nodes.rgns[n].get_len()
                self.cvgs_min[k] = self.nodes.rgns[n].ave_cvg_depth()
                
                ## This case happened. Study required !!!
                ## It means edges_ext contains 'I' (Is it no problem?)
        
        return wgt_ext, b


    def dconv(self, v, abn_norm = 'log'):
        if abn_norm == 'log':
            return np.log2(1+v)
        elif abn_norm == 'lin':
            return v
        else:
            return 2*np.sqrt(v+(3/8))

    
    def get_z_and_G_using(self, cvg_node_n_edge, len_node_n_edge, n_nodes, \
                          graph_f, graph_b, p_lst, abn_norm = 'lin'):
        
        nn = len(cvg_node_n_edge) # n_nodes_and_edges
        n_p = len(p_lst)
        
        z_min = np.zeros(nn, dtype=np.float32)
        for k in range(nn): 
            z_min[k] = cvg_node_n_edge[k] # self.dconv(cvg_node_n_edge[k], abn_norm = abn_norm)
            # if k < n_nodes: z_min[k] =z_min[k]* np.sqrt(len_node_n_edge[k])
            # else: z_min[k] = z_min[k]*np.sqrt(self.read_len)
        
        G_min = np.zeros([n_p,nn], dtype=np.float32)
        for k in range(n_p):
            G_min[k,p_lst[k]] = 1

        b = np.sum(G_min, axis = 0)
        z_min = z_min[b>0]
        G_min = G_min[:,b>0]
        
        return z_min, G_min

    
    def get_valid_volume(self, cvg_node_n_edge, len_node_n_edge, n_nodes, \
                          graph_f, graph_b, p_lst, abn_norm = 'lin'):
        
        nn = len(cvg_node_n_edge) # n_nodes_and_edges
        n_p = len(p_lst)
        
        z_min = np.zeros(nn, dtype=np.float32)
        for k in range(nn): 
            z_min[k] = cvg_node_n_edge[k]*len_node_n_edge[k]
        
        G_min = np.zeros([n_p,nn], dtype=np.float32)
        for k in range(n_p):
            G_min[k,p_lst[k]] = 1

        b = np.sum(G_min, axis = 0)
        b[n_nodes:] = 0
        z_min = z_min[b>0]
        
        return np.sum(z_min)

    
    def naive_sic_ext(self, z, G, cvgs, lens, p_lst, ntr = 0):
    
        Abn = None
        n_p = G.shape[0]
        n_ne = len(z)

        if ntr == 0:
            ntr = n_p
            
        if n_p == 1:
            path = np.array(which( G[0,:n_ne] > 0 ))
            Abn = (cvgs[path]*lens[path]).sum()/lens.sum()
            Abn = np.array([Abn])
        else:         
            y = z
            H = G
            p_sel_lst = []
            Abn = np.zeros(n_p)
            cnt = 0
            mx_x_hat = 0
            mx_y = y.max()*2
            while True:

                x_hat_tmp = np.zeros(n_p)
                x_til_tmp = np.zeros(n_p)
                for m, p in enumerate(p_lst):
                    if m not in p_sel_lst:
                        wh = which(H[m,:] > 0)
                        z_sel = y[wh]
                        z_min = z_sel.min()
                        z_mean = z_sel.mean()

                        odr = z_sel.argsort()
                        if len(odr) > 7:
                            z_min = z_sel[odr[2]]
                        else:
                            z_min = z_sel[odr[0]]

                        x_hat_tmp[m] = z_min # z_min*mx_y + z_mean
                        x_til_tmp[m] = z_mean

                odr = x_til_tmp.argsort()
                w = odr[-1]

                if x_hat_tmp[w] == 0: break
                else:
                    p_sel_lst.append(w)
                    Abn[w] = x_hat_tmp[w]
                    y = y - H[w,:]*x_hat_tmp[w]
                    y[y < 0] = 0

                if cnt == 0:
                    mx_x_hat = x_hat_tmp[w]
                cnt += 1

                if x_hat_tmp[w] < mx_x_hat*MIN_ISO_FRAC_SIC: break

                if np.sum(Abn > 0) >= ntr: break
                        
                
        return Abn 
        
    
    def lasso_sic_ext(self, z, G, cvgs, lens, p_lst, ntr = 0):
    
        Abn = None
        n_p = G.shape[0]
        n_ne = len(z)

        if ntr == 0:
            ntr = n_p
            
        if n_p == 1:
            path = np.array(which( G[0,:n_ne] > 0 ))
            Abn = (cvgs[path]*lens[path]).sum()/lens.sum()
            Abn = np.array([Abn])
        else:         
            y = z
            H = G
            p_sel_lst = []
            Abn = np.zeros(n_p)
            cnt = 0
            mx_x_hat = 0
            
            K = min(ntr, MAX_NUM_PATHS)
            for k in range(K):

                x_hat_tmp = self.isolasso_ext(y, H, cvgs, lens, n_alphas = 40)

                odr = x_hat_tmp.argsort()
                w = odr[-1]

                if cnt == 0:
                    mx_x_hat = x_hat_tmp[w]
                cnt += 1
                
                if x_hat_tmp[w] < mx_x_hat*MIN_ISO_FRAC_SIC: break
                else:
                    p_sel_lst.append(w)
                    Abn[w] = x_hat_tmp[w]
                    y = y - H[w,:]*x_hat_tmp[w]
                    y[y < 0] = 0

                if ntr > 0:
                    if np.sum(Abn > 0) >= ntr: break
                
        return Abn 
        
    
    def isolasso_ext(self, z, G, cvgs, lens, ntr = 0, n_alphas = 100):
    
        Abn = None
        n_p = G.shape[0]
        n_ne = len(z)
        if n_p == 1:
            path = np.array(which( G[0,:n_ne] > 0 ))
            Abn = (cvgs[path]*lens[path]).sum()/lens.sum()
            Abn = np.array([Abn])
        else:         
            if n_alphas == 0:
                Abn, Alphas, Gaps = run_ElasticNet( G, z, alpha = MIN_ALPHA_FOR_EN, l1r = 0.5 )
            else:
                Abns, Alphas, Gaps = run_ElasticNet_path( G, z, l1r = NOMINAL_L1_RATIO, n_alphas = n_alphas )
                N_sel = np.sum( Abns != 0, axis=0 )
                odr = N_sel.argsort()

                if ntr > 0:
                    for k in range(len(Alphas)):
                        m = odr[k]
                        if N_sel[m] >= ntr:
                            Abn = Abns[:,m]

                if Abn is None:
                    if n_ne == 0: nf = 1
                    else: nf = 1/n_ne
                    b = False
                    for k in range(len(Alphas)):
                        m = odr[k]
                        Abn = Abns[:,m]
                        # wh = which(Abn>0)
                        cov = np.sum(G[Abn>0,:], axis=0)
                        n_cov = int(100*np.sum(cov != 0)*nf)
                        if (n_cov == 100): # & (np.sum(Abn < 0) == 0): 
                            b = True
                            break

                if (np.sum(Abn < 0) > 0):
                    # print('WARNING in isolasso_ext: N_neg = %i/%i ' % (np.sum(Abn < 0), len(Abn)))
                    Abn[Abn < 0] = 0
        return Abn 
        
            
    def get_abundance_for_single_tr_gene(self):
        
        abn = 0
        tr_len = 0
        seq = ''

        cvgs, lens = self.nodes.get_cvgs_and_lens()
        path = np.array(self.p_lst[0])
        nsel = path[path < self.n_nodes]
        abn = (cvgs[nsel]*lens[nsel]).sum()/lens[nsel].sum()
        cvg_med = np.median( cvgs[nsel] )
        
        pr = 0
        ecnt = 0
        for m in range(len(self.p_lst[0])):
            k = self.p_lst[0][m]
            if k < self.n_nodes:
                seq = seq + self.nodes.rgns[k].get_seq()
                # abn += (Len*self.nodes.rgns[k].ave_cvg_depth())
                # tr_len += Len
                # pr += np.sum(np.log(self.nodes.rgns[k].get_majority_ratio()))
                
        pr = 1 # pr/len(seq)
        
        return seq, abn, pr
    
    
    def get_trs_from_abn(self, Abn, strands = [], coding_ind = []):
        
        tr_lst = []
        is_lst = []
        gcnt = self.gcnt
        
        if self.n_p > 0:
            
            span = self.nodes.get_span()

            if len(self.p_lst) == 1:

                prefix = 'T'
                seq, Abn, pr = self.get_abundance_for_single_tr_gene()
                self.abn = np.array([Abn])

                if len(strands) > 0: strnd = strands[0]
                else: strnd = self.strand
                    
                if len(coding_ind) > 0: 
                    cdng = get_str_from_icdng( coding_ind[0] )
                else: cdng = 'unspecified'
                    
                tr = Transcript( prefix, gcnt, 1, 1, self.nodes.rgns[0].chr, \
                                 span.start, span.end, strnd, cdng, seq, Abn, Abn, 1, pr, (len(self.p_lst[0])+1)*0.5, 0 )
                tr_lst.append(tr)

            else:                
        
                prefix = 'I'
                prob = 1 # get_prob(Abn)
                grp_size = len(Abn) # np.sum(Abn > 0)
                g_abn = 1/np.sum(Abn)
                for n in range(len(Abn)): #len(self.p_lst)):
                    pr = 0
                    # if Abn[n] >= 0:
                    tr_len = 0
                    seq = ''
                    for m in range(len(self.p_lst[n])):
                        k = self.p_lst[n][m]
                        if k < self.n_nodes:
                            tseq = self.nodes.rgns[k].get_seq()
                            seq = seq + tseq
                            # pr += np.sum(np.log(self.nodes.rgns[k].get_majority_ratio()))

                    # pr = pr/len(seq)
                    pr = 1 # prob[n]
                    abn = Abn[n]

                    if len(strands) > 0: strnd = strands[n]
                    else: strnd = self.strand
                        
                    if len(coding_ind) > 0: 
                        cdng = get_str_from_icdng( coding_ind[0] )
                    else: cdng = 'unspecified'
                
                    tr = Transcript( prefix, gcnt, grp_size, n+1, self.nodes.rgns[0].chr, \
                                     span.start, span.end, strnd, cdng, seq, abn, abn, abn*g_abn, pr, (len(self.p_lst[n])+1)*0.5, 0 )
                    is_lst.append(tr)

                self.abn = Abn
                            
        return tr_lst, is_lst
        
        
    def select_edges_to_del( self, edges, strand ):
        
        ## Negative strand
        map_edges = []
        to_del = []
        eidx_se = []
        for k, edge in enumerate(edges.rgns):
            if ((edge.type == 'N')&(edge.xs*strand > 0)): eidx_se.append(k+self.n_nodes)
                
        for k, edge in enumerate(edges.rgns):
            if ((edge.type == 'N')&(edge.xs*strand < 0)): to_del.append(k)
            elif ((edge.type == 'N') & (edge.xs == 0)):
                b = False
                ps, bs = BFS_all2( self.graph_f, k+self.n_nodes, eidx_se )
                if len(ps) > 0:
                    cnt = 0
                    for p in ps:
                        for n in p:
                            if (n>=self.n_nodes):
                                if (edges.rgns[n-self.n_nodes].xs*strand < 0): cnt += 1
                    if cnt == 0: b = True
                else:
                    ps, bs = BFS_all2( self.graph_b, k+self.n_nodes, eidx_se )
                    if len(ps) > 0:
                        cnt = 0
                        for p in ps:
                            for n in p:
                                if (n>=self.n_nodes):
                                    if (edges.rgns[n-self.n_nodes].xs*strand < 0): cnt += 1
                        if cnt == 0: b = True
                            
                if b: map_edges.append(k)
                else: to_del.append(k)
                    
            else: map_edges.append(k)
        
        return map_edges, to_del
                
       
    def select_edges_and_nodes_to_del( self, edges, nodes, strand, len_th = 200 ):
        
        map_edges = []
        to_del_edges = []
        map_nodes = []
        to_del_nodes = []
        
        ## Edges
        to_del = []
        eidx_se = []
        for k, edge in enumerate(edges.rgns):
            if ((edge.type == 'N') & (edge.xs*strand > 0)): eidx_se.append(k+self.n_nodes)
                
        if len(eidx_se) > 0:
            
            ## Select edges
            for k, edge in enumerate(edges.rgns):
                if ((edge.type == 'N') & (edge.xs*strand < 0)): to_del.append(k)
                elif (edge.xs == 0): # & (edge.type == 'N'):
                    b = False
                    ps, bs = BFS_all2( self.graph_f, k+self.n_nodes, eidx_se )
                    if len(ps) > 0:
                        cnt = 0
                        hit = 0
                        for p in ps:
                            for n in p:
                                if (n>=self.n_nodes):
                                    if (edges.rgns[n-self.n_nodes].xs*strand < 0): cnt += 1
                                    if (edges.rgns[n-self.n_nodes].xs*strand > 0): hit += 1
                        if (cnt == 0) & (hit > 0): b = True
                    else:
                        ps, bs = BFS_all2( self.graph_b, k+self.n_nodes, eidx_se )
                        if len(ps) > 0:
                            cnt = 0
                            hit = 0
                            for p in ps:
                                for n in p:
                                    if (n>=self.n_nodes):
                                        if (edges.rgns[n-self.n_nodes].xs*strand < 0): cnt += 1
                                        if (edges.rgns[n-self.n_nodes].xs*strand > 0): hit += 1
                            if (cnt == 0) & (hit > 0): b = True

                    if b: map_edges.append(k)
                    else: to_del.append(k)

                else: map_edges.append(k)

            to_del_edges = to_del

            #'''
            ## Select Nodes
            pf = np.zeros(len(nodes.rgns))
            nf = np.zeros(len(nodes.rgns))

            for k, r in enumerate(nodes.rgns):
                if (len(self.graph_f[k]) == 0) & (len(self.graph_b[k]) == 0):
                    if (strand > 0) & (nodes.rgns[k].get_len() >= len_th): pf[k] += 1
                else:
                    if nodes.rgns[k].type == 'M':
                        kf = k
                        kb = k
                    else:
                        kf = self.graph_f[k][0]
                        kb = self.graph_b[k][0]
                        
                    while len(self.graph_f[kf]) == 1:
                        e = self.graph_f[kf][0]
                        if (e >= self.n_nodes):
                            if (edges.rgns[e-self.n_nodes].xs != 0):
                                break
                        kf = self.graph_f[e][0]


                    while len(self.graph_b[kb]) == 1:
                        e = self.graph_b[kb][0]
                        if (e >= self.n_nodes):
                            if (edges.rgns[e-self.n_nodes].xs != 0):
                                break
                        kb = self.graph_b[e][0]

                        
                    for e in self.graph_f[kf]:
                        if e >= self.n_nodes:
                            # if (edges.rgns[e-self.n_nodes].xs*strand > 0): pf[k] += 1
                            if (e-self.n_nodes) in map_edges: pf[k] += 1

                    for e in self.graph_b[kb]:
                        if e >= self.n_nodes:
                            # if (edges.rgns[e-self.n_nodes].xs*strand > 0): pf[k] += 1
                            if (e-self.n_nodes) in map_edges: pf[k] += 1
                                    
            b = (pf > 0) # | ((pf == 0) & (nf == 0))
            map_nodes = which(b)
            to_del_nodes = which(b == False)
            #'''
        
        return map_edges, to_del_edges, map_nodes, to_del_nodes
                
       
            
    def td_and_ae(self, len_th = 50, method = 'lasso', g_ret = False):
        
        # 
        t_lst_all = []
        i_lst_all = []
        gtf_lines_all = []
        self.n_p_detected = 0
        self.p_lst_detected = []
        self.n_p_candidate = 0
        self.p_lst_candidate = []
        gd = None
        
        if (len(self.graph_f) > 0) & (self.n_nodes > 0):
            
            
            nodes_org = self.nodes.copy()
            edges_org = self.edges.copy()
            nn = len(nodes_org.rgns) # = len(nodes_pos.rgns)
            ne = len(edges_org.rgns) # = len(nodes_pos.rgns)
            
            bistranded, n_pos, n_neg = self.edges.check_bistrand()
            if not bistranded:
                Loop = 1
                nodes_lst = [self.nodes.copy()]
                edges_lst = [self.edges.copy()]
                map_nodes = list(np.arange(nn+ne))
                node_map_lst = [map_nodes]
            else:
                Loop = 2

                ## make 2 copies
                ## 1: leave neg. stranded edges (neutral edges and unconnected edges?)
                ## 2: Use all other nodes and edges
                
                ## Copy first
                nodes_neg = self.nodes.copy()
                edges_neg = self.edges.copy()
                
                nodes_pos = self.nodes.copy()
                edges_pos = self.edges.copy()
                
                ##################
                ## Negative strand
                
                self.get_splice_graphs(nodes_neg, edges_neg)
                map_edges_neg, to_del_edges, map_nodes_neg, to_del_nodes = \
                    self.select_edges_and_nodes_to_del( edges_neg, nodes_neg, -1, len_th = len_th )
                
                if len(to_del_edges) == 0:
                    Loop = 1
                    nodes_lst = [self.nodes.copy()]
                    edges_lst = [self.edges.copy()]
                    map_nodes = list(np.arange(nn+ne))
                    node_map_lst = [map_nodes]
                else:
                    '''
                    to_del_edges.sort(reverse=True)
                    for k in to_del_edges: del edges_neg.rgns[k]
                        
                    if len(to_del_nodes) > 0:
                        to_del_nodes.sort(reverse=True)
                        for k in to_del_nodes: del nodes_neg.rgns[k]
                            
                    self.get_splice_graphs(nodes_neg, edges_neg)
                    #'''
                    nodes_neg, edges_neg = self.revise_graphs(to_del_nodes, to_del_edges)
                    
                    sn = get_start_nodes(self.graph_f)
                    en = get_end_nodes(self.graph_f)
                    bn = sn + en
                    to_del = []
                    for m in bn:
                        if m >= self.n_nodes:
                            to_del.append(m)
                        elif (m < self.n_nodes) & (nodes_neg.rgns[m].type != 'M'):
                            to_del.append(m)
                    
                    if len(to_del) > 0:
                        to_del = list(set(to_del))
                        to_del.sort(reverse=True)
                        for m in to_del:
                            if m < self.n_nodes:
                                del nodes_neg.rgns[m]
                                del map_nodes_neg[m]
                            else:
                                del edges_neg.rgns[m-self.n_nodes]
                                del map_edges_neg[m-self.n_nodes]
                    #'''
                    
                    map_nodes_neg = map_nodes_neg + [w+nn for w in map_edges_neg]
                        
                    ##################
                    ## Positive strand
                    
                    self.get_splice_graphs(nodes_pos, edges_pos)
                    map_edges_pos, to_del_edges, map_nodes_pos, to_del_nodes = \
                        self.select_edges_and_nodes_to_del( edges_pos, nodes_pos, 1, len_th = len_th )
                    
                    if len(to_del_edges) == 0:
                        Loop = 1
                        nodes_lst = [self.nodes.copy()]
                        edges_lst = [self.edges.copy()]
                        map_nodes = list(np.arange(nn+ne))
                        node_map_lst = [map_nodes]
                    else:
                        '''
                        to_del_edges.sort(reverse=True)
                        for k in to_del_edges: del edges_pos.rgns[k]

                        if len(to_del_nodes) > 0:
                            to_del_nodes.sort(reverse=True)
                            for k in to_del_nodes: del nodes_pos.rgns[k]

                        self.get_splice_graphs(nodes_pos, edges_pos)
                        #'''
                        nodes_pos, edges_pos = self.revise_graphs(to_del_nodes, to_del_edges)
                        
                        sn = get_start_nodes(self.graph_f)
                        en = get_end_nodes(self.graph_f)
                        bn = sn + en
                        to_del = []
                        for m in bn:
                            if m >= self.n_nodes:
                                to_del.append(m)
                            elif (m < self.n_nodes) & (nodes_pos.rgns[m].type != 'M'):
                                to_del.append(m)

                        if len(to_del) > 0:
                            to_del = list(set(to_del))
                            to_del.sort(reverse=True)
                            for m in to_del:
                                if m < self.n_nodes:
                                    del nodes_pos.rgns[m]
                                    del map_nodes_pos[m]
                                else:
                                    del edges_pos.rgns[m-self.n_nodes]
                                    del map_edges_pos[m-self.n_nodes]
                        #'''
                    
                        map_nodes_pos = map_nodes_pos + [w+nn for w in map_edges_pos]

                        nodes_lst = [nodes_neg, nodes_pos]
                        edges_lst = [edges_neg, edges_pos]
                        node_map_lst = [map_nodes_neg, map_nodes_pos]
                
                
            for loop in range(Loop):
                
                node_map = node_map_lst[loop]
                Nodes_cur = nodes_lst[loop]
                Edges_cur = edges_lst[loop]
                self.get_stuffs(Nodes_cur, Edges_cur)
                # self.get_splice_graphs(Nodes_cur, Edges_cur)
                
                if len(self.edges.rgns) == 0:
                    strand_cur = 0
                else:
                    b, n_pos, n_neg = self.edges.check_bistrand()
                    if b:
                        print('ERROR: Not divided correctly at L = %i.' % loop)
                        strand_cur = 0
                    else:
                        if n_neg > 0: strand_cur = -1
                        else: strand_cur = 1
                self.strand = strand_cur
                
            
                t_lst = []
                i_lst = []
                gtf_lines = []
                n_p_d = 0
                p_lst_d = []
                n_p_c = 0
                p_lst_c = []
                
                gi, grp_cnt = group_nodes(self.graph_f)
                if grp_cnt > 1: 
                    # self.print_short()
                    nodes = self.nodes.copy()
                    edges = self.edges.copy()
                    n_nodes = self.n_nodes
                    n_edges = self.n_edges

                for k in range(int(grp_cnt)):

                    if grp_cnt > 1:
                        nodes_tmp = regions()
                        edges_tmp = regions_nd()
                        wh_node = which(gi == k)
                        for w in wh_node:
                            if w < n_nodes:
                                nodes_tmp.rgns.append(nodes.rgns[w])
                            else:
                                edges_tmp.rgns.append(edges.rgns[int(w-n_nodes)])                        
                        self.get_stuffs(nodes_tmp,edges_tmp)
                        # self.filter_paths()
                    else:
                        # self.get_all_paths(  )
                        wh_node = list(np.arange(len(gi)))
                        

                    wgt_ext, b = self.get_paths_over_minimal_graph()
                    z, G = self.get_z_and_G_using( self.cvgs_min, self.lens_min, self.n_nodes_min, \
                                            self.graph_f_min, self.graph_b_min, self.p_lst_min, \
                                            abn_norm = 'lin')
                    Abn = self.isolasso_ext(z, G, self.cvgs_min, self.lens_min)
                    self.p_lst = get_org_path( self.p_lst_min, self.nodes_min )
                    self.n_p = len(self.p_lst)
                    tlst, ilst = self.get_trs_from_abn(Abn)

                    #################################################
                    ### Revise abundances and Store paths to be used externally

                    for m,p in enumerate(self.p_lst):
                        n_p_c += 1
                        p_tmp = [wh_node[nd] for nd in p]
                        p_lst_c.append(p_tmp)
                    
                    Vol_in = self.nodes.get_volume()

                    tlst2 = []
                    ilst2 = []
                    if len(tlst) > 0:
                        vol = 0
                        for tr in tlst:                            
                            vol += len(tr.seq)*tr.abn
                        nf = Vol_in/vol
                        for m, t in enumerate(tlst):
                            ABN = t.abn*nf
                            tr = Transcript(t.prefix,t.gidx,t.grp_size, self.n_p_detected+n_p_d, t.chr,\
                                            t.start,t.end,strand_cur, t.cdng,t.seq, ABN, t.tpm,t.iso_frac, t.prob, t.nexs, Vol_in)
                            tlst2.append(tr)

                            n_p_d += 1
                            p_tmp = [wh_node[nd] for nd in self.p_lst[m]]
                            p_lst_d.append(p_tmp)


                    if len(ilst) > 0:

                        mx_len = 0;
                        vol = 0
                        for tr in ilst:
                            vol += len(tr.seq)*tr.abn
                            mx_len = max( mx_len, len(tr.seq) )

                        if (vol <= 0) | (math.isnan(vol)):
                            print('ERROR in td_and_ae(): vol = %f' % vol )
                            vol = 1
                        nf = Vol_in/vol

                        for m, t in enumerate(ilst):
                            ABN = t.abn*nf
                            tr = Transcript(t.prefix,t.gidx,t.grp_size, self.n_p_detected+n_p_d, t.chr,\
                                            t.start,t.end,strand_cur, t.cdng, t.seq, ABN, t.tpm,t.iso_frac, t.prob, t.nexs, Vol_in)
                            n_p_d += 1
                            p_tmp = [wh_node[nd] for nd in self.p_lst[m]]
                            p_lst_d.append(p_tmp)
                            ilst2.append(tr)

                    # t_lst = t_lst + tlst2
                    # i_lst = i_lst + ilst2

                    if gd is None:
                        gd = gene_descriptor(Cov_th = MIN_COV_TO_SEL, Abn_th = MIN_ABN_TO_SEL)
                        gd.init( self )
                        
                    gd.add_tr( self.nodes, self.edges, self.p_lst, tlst2 + ilst2 )
                    
                #'''
                if grp_cnt > 1: self.get_stuffs(nodes,edges)
                gtf_lines = get_gtf_lines_from_transcripts(t_lst + i_lst, p_lst_d, self.nodes, self.edges)

                p_lst_d_mapped = []
                for p in p_lst_d:
                    path = [node_map[w] for w in p]
                    p_lst_d_mapped.append(path)

                p_lst_c_mapped = []
                for p in p_lst_c:
                    path = [node_map[w] for w in p]
                    p_lst_c_mapped.append(path)

                # gtf_lines = get_gtf_lines_from_transcripts(t_lst + i_lst, p_lst_d_mapped, nodes_org, edges_org)
                
                t_lst_all = t_lst_all + t_lst
                i_lst_all = i_lst_all + i_lst
                gtf_lines_all = gtf_lines_all + gtf_lines
                
                self.n_p_detected = self.n_p_detected + n_p_d
                self.p_lst_detected = self.p_lst_detected + p_lst_d_mapped

                self.n_p_candidate = self.n_p_candidate + n_p_c
                self.p_lst_candidate = self.p_lst_candidate + p_lst_c_mapped
                #'''

            ## End of Loop
            # self.get_stuffs(nodes_org,edges_org)
            
        return gd, t_lst_all, i_lst_all, gtf_lines_all


    def td_and_ae_using_annotation(self, gd, len_th = MIN_TR_LENGTH, method = 'lasso', g_ret = False, verbose = True):

        t_lst_all = []
        i_lst_all = []
        gtf_lines_all = []
        self.n_p_detected = 0
        self.p_lst_detected = []
        self.n_p_candidate = 0
        self.p_lst_candidate = []

        st = time.time()

        nodes = self.nodes # .copy()
        edges = self.edges # .copy()
        
        #####################
        ## remove unmapped rgns
        #'''
        cnt = 0
        unmapped_m = []
        for m, node in enumerate(nodes.rgns):
            if node.type == 'M':
                b = False
                for k, ge in enumerate(gd.exons.rgns):
                    if ge.has_ext_intersection_with(node): 
                        b = True
                        break
                if not b: unmapped_m.append(m)
        if len(unmapped_m) > 0:
            nodes, edges = self.revise_graphs( unmapped_m, [] )

        nn = len(self.nodes.rgns)
        to_del = []
        for m, e in enumerate(edges.rgns):
             if (len(self.graph_f[nn+m]) == 0) & (len(self.graph_b[nn+m]) == 0):
                to_del.append(m)

        if len(to_del) > 0:
            nodes, edges = self.revise_graphs( [], to_del )

        to_del2 = []
        for m, n in enumerate(nodes.rgns):
            if n.type != 'M':
                if (len(self.graph_f[m]) == 0) & (len(self.graph_b[m]) == 0):
                    to_del2.append(m)

        if len(to_del2) > 0:
            nodes, edges = self.revise_graphs( to_del2, [] )
            
        et0 = time.time() - st             

        #####################
        ## Trim regions
        st = time.time()

        ## build gd.exon to node map
        cnt = 0
        node_to_ge_map = {k: [] for k in range(len(nodes.rgns))}
        node_break_points = {k: [] for k in range(len(nodes.rgns))}
        b_proc_exons = np.ones(len(gd.exons.rgns))
        
        for m, node in enumerate(nodes.rgns):
            if node.type == 'M':
                for k, ge in enumerate(gd.exons.rgns):
                    if ge.has_ext_intersection_with(node): 
                        node_to_ge_map[m].append(k)
                        b_proc_exons[k] = 0
                        cnt += 1
                        if (node.start < ge.start):
                            node_break_points[m].append(ge.start-node.start)
                        if (node.end > ge.end):
                            Len = node.end - node.start + 1
                            node_break_points[m].append(Len - (node.end - ge.end))
                            
        for m, node in enumerate(nodes.rgns):
            node_break_points[m] = list(set(node_break_points[m]))
            node_break_points[m].sort()

        nodes_to_add = regions()
        edges_to_add = regions_nd()
        for m, node in enumerate(nodes.rgns):
            if (node.type == 'M') & (len(node_break_points[m]) > 0):
                prev_b_pnt = 0
                for k, b_pnt in enumerate(node_break_points[m]):
                    Len = b_pnt - prev_b_pnt
                    rm = region( node.chr, node.start, node.start+Len-1, 'M', node.cmat[:,:Len] )
                    rm.get_cvg()
                    nodes_to_add.rgns.append(rm)

                    rn = region_nd( node.chr, node.start+Len, node.start+Len-1, 'N', cvg_dep = rm.cvg[-1] )
                    edges_to_add.rgns.append(rn)

                    node.start = node.start + Len
                    node.cmat = node.cmat[:,Len:]
                    node.get_cvg()

                    prev_b_pnt = b_pnt

        bc = False
        if len(nodes_to_add.rgns) > 0:
            nodes.rgns = nodes.rgns + nodes_to_add.rgns
            bc = True
        if len(edges_to_add.rgns) > 0:
            edges.rgns = edges.rgns + edges_to_add.rgns
            bc = True

        #'''
        for k, ge in enumerate(gd.exons.rgns):
            if b_proc_exons[k] > 0: 
                Len = ge.get_len()
                rm = region( ge.chr, ge.start, ge.end, 'M', 'N'*Len, cvg_dep = CVG_DEPTH_TMP )
                rm.get_cvg()
                nodes.rgns.append(rm)
                bc = True
        #'''

        if bc:
            nodes.order() # update()
            edges.order() # update()
            nodes.set_cvg()
            # nodes.update()
            edges.set_cvg()
            # edges.update()
            self.get_splice_graphs(nodes, edges)

        et1 = time.time() - st   
          
        #####################
        ## Trim unconnected, short regions
        st = time.time()

        N = max(gd.ntr, 5)
        #'''
        if gd.ntr > 0:
            for kk in range(N):
                
                if kk == 0:
                    nodes = self.nodes #.copy()
                    edges = self.edges #.copy()
                else:
                    nodes.order() # update()
                    edges.order() # update()
                    nodes.set_cvg() # update()
                    edges.set_cvg() # update()
                    self.get_splice_graphs(nodes, edges)
                    nodes = self.nodes #.copy()
                    edges = self.edges #.copy()

                bc = False
                b_proc = np.ones(len(nodes.rgns))
                
                ## build gd.exon to node map
                cnt = 0
                ge_to_nodes_map = {k: [] for k in range(len(gd.exons.rgns))}
                for k, ge in enumerate(gd.exons.rgns):
                    for m, node in enumerate(nodes.rgns):
                        if node.type == 'M':
                            if ge.has_ext_intersection_with(node): 
                                ge_to_nodes_map[k].append(m)
                                cnt += 1

                nodes_to_add = regions()
                edges_to_add = regions()

                bp1 = np.zeros(len(gd.exons.rgns))
                bp2 = np.zeros(len(gd.exons.rgns))
                bp3 = np.zeros(len(gd.exons.rgns))
                bp4 = np.zeros(len(gd.exons.rgns))

                for k in range(gd.ntr):

                    e_lst = gd.te_to_ge_maps[k]
                    e_lst_p = []
                    e_lst_n = []
                    if k > 0: e_lst_p = gd.te_to_ge_maps[k-1]
                    if k < (gd.ntr-1): e_lst_n = gd.te_to_ge_maps[k+1]

                    for m, e in enumerate(e_lst):

                        if (len(ge_to_nodes_map[e]) == 0) & (bp1[e] == 0):
                            ## add exon to nodes if there is no reads mapped
                            Len = gd.exons.rgns[e].get_len()
                            r1 = region( gd.exons.rgns[e].chr, gd.exons.rgns[e].start, gd.exons.rgns[e].end, 'M', 'N'*Len, cvg_dep = CVG_DEPTH_TMP )
                            r1.get_cvg()
                            nodes_to_add.rgns.append(r1)
                            bc = True
                            bp1[e] = 1
                            # break

                        else:
                            if (len(ge_to_nodes_map[e]) > 1) & (bp2[e] == 0):
                                ## if two consecutive nodes are not connected, then connect them by filling with Ns
                                for i, n2 in enumerate(ge_to_nodes_map[e]):
                                    if (i > 0):
                                        n1 = ge_to_nodes_map[e][i-1]
                                        plst = BFS3( self.graph_f, n1, n2, MAX_NUM_HOPS )
                                        if len(plst) > 0:
                                            pass
                                        else:
                                            if (nodes.rgns[n1].end+1) == nodes.rgns[n2].start:
                                                r_n_new = region_nd( nodes.rgns[n1].chr, nodes.rgns[n2].start, nodes.rgns[n1].end, 'N', cvg_dep = nodes.rgns[n2].cvg[0] )
                                                edges_to_add.rgns.append(r_n_new)
                                                edges_to_add.set_cvg()
                                                bc = True
                                                bp2[e] = 1

                                            elif (nodes.rgns[n1].end+1) < nodes.rgns[n2].start:
                                                Len = nodes.rgns[n2].start - (nodes.rgns[n1].end+1)
                                                r1 = region( nodes.rgns[n1].chr, nodes.rgns[n1].end+1, nodes.rgns[n2].start-1, 'M', 'N'*Len, cvg_dep = CVG_DEPTH_TMP )
                                                r1.get_cvg()
                                                nodes_to_add.rgns.append(r1)
                                            
                                                r_n_1 = region_nd( nodes.rgns[n1].chr, nodes.rgns[n1].end+1, nodes.rgns[n1].end, 'N', cvg_dep = CVG_DEPTH_TMP )
                                                edges_to_add.rgns.append(r_n_1)

                                                r_n_2 = region_nd( nodes.rgns[n1].chr, nodes.rgns[n2].start, nodes.rgns[n2].start-1, 'N', cvg_dep = CVG_DEPTH_TMP )
                                                edges_to_add.rgns.append(r_n_2)

                                                edges_to_add.set_cvg()
                                                bc = True
                                                bp2[e] = 1
                                                # break
                                            else:
                                                ## ERROR
                                                pass
                                # if bc: break

                            n2 = ge_to_nodes_map[e][0]
                            if (nodes.rgns[n2].start > gd.exons.rgns[e].start) & (bp3[e] == 0):

                                bt = True
                                if len(self.graph_b[n2]) == 0: 
                                    Len = nodes.rgns[n2].start - gd.exons.rgns[e].start
                                    r1 = region( nodes.rgns[n2].chr, gd.exons.rgns[e].start, nodes.rgns[n2].start-1, 'M', 'N'*Len, cvg_dep = CVG_DEPTH_TMP )
                                    r1.get_cvg()
                                    nodes_to_add.rgns.append(r1)

                                    r_n_new = region_nd( nodes.rgns[n2].chr, nodes.rgns[n2].start, nodes.rgns[n2].start-1, 'N', cvg_dep = CVG_DEPTH_TMP )
                                    edges_to_add.rgns.append(r_n_new)
                                    edges_to_add.set_cvg()
                                    bc = True
                                    bp3[e] = 1
                                    # break

                            n2 = ge_to_nodes_map[e][-1]
                            if (nodes.rgns[n2].end < gd.exons.rgns[e].end) & (bp4[e] == 0):
                                bt = True
                                if len(self.graph_f[n2]) == 0:
                                    Len = gd.exons.rgns[e].end - nodes.rgns[n2].end
                                    r1 = region( nodes.rgns[n2].chr, nodes.rgns[n2].end+1, gd.exons.rgns[e].end, 'M', 'N'*Len, cvg_dep = CVG_DEPTH_TMP )
                                    r1.get_cvg()
                                    nodes_to_add.rgns.append(r1)

                                    r_n_new = region_nd( nodes.rgns[n2].chr, nodes.rgns[n2].end+1, nodes.rgns[n2].end, 'N', cvg_dep = CVG_DEPTH_TMP )
                                    edges_to_add.rgns.append(r_n_new)
                                    edges_to_add.set_cvg()
                                    bc = True
                                    bp4[e] = 1
                                    # break

                if bc: 
                    nodes.rgns = nodes.rgns + nodes_to_add.rgns
                    edges.rgns = edges.rgns + edges_to_add.rgns
                else: 
                    break
        #'''
        et2 = time.time() - st             
                
        ##########################################
        ## check if any D or I lies within an exon
        st = time.time()
        # '''
        b = False
        for e in edges.rgns:
            if e.type == 'D':
                for r in nodes.rgns:
                    if r.has_ext_intersection_with(e):
                        b = True
                        break
                if b: break
        if b: edges, nodes, bt = trim_d( edges, nodes )  
            
        rs_i = regions()
        to_del = []
        for m, n in enumerate(nodes.rgns):
            if n.type == 'I':
                for r in nodes.rgns:
                    if (n.start > r.start) & (n.start <= r.end):
                        to_del.append(m)
                        rs_i.rgns.append(n)
                        break
                
        if len(to_del) > 0:
            to_del.sort()
            for m in reversed(to_del): del nodes.rgns[m]           
            edges, nodes, bt = add_i( edges, nodes, rs_i )

        if b | (len(to_del) > 0):
            nodes.update()
            edges.set_cvg()
            edges.update()
            self.get_splice_graphs(nodes, edges)
        #'''
        et3 = time.time() - st             
            
        #####################
        ## Find paths
        st = time.time()

        N = 10
        gd.rgns = regions()
        
        for kk in range(N):
            bc = False
            
            #'''
            if kk == 0:
                nodes = self.nodes #.copy()
                edges = self.edges #.copy()
                
            # nodes.update()
            edges.order() # update()
            self.get_splice_graphs(nodes, edges)
            nodes = self.nodes #.copy()
            edges = self.edges #.copy()
            
            n_uc = 0
            #'''
            ## build gd.exon to node map
            cnt = 0
            ge_to_nodes_map = {k: [] for k in range(len(gd.exons.rgns))}
            for k, ge in enumerate(gd.exons.rgns):
                for m, node in enumerate(nodes.rgns):
                    if node.type == 'M':
                        if ge.has_ext_intersection_with(node): 
                            ge_to_nodes_map[k].append(m)
                            cnt += 1
            if cnt == 0:
                if verbose: print('ERROR in td_and_ae_using_annot: no overlaping exons found in G.%i' % (self.gcnt))
            #'''
            self.get_cvgs_and_lens()

            ## use gd.exon to node map to get nodes list 
            ## Then use node list to find a (partial) path

            n_p = 0
            p_lst = []
            s_lst = []
            c_lst = []
            # cov_lst = []
            p_idx = np.full(gd.ntr, -1)

            #'''
            edges_new = regions_nd()

            b_sel = np.zeros(self.n_nodes+self.n_edges)
            end_nodes = get_end_nodes(self.graph_f)

            bp = np.zeros( [len(self.nodes.rgns),len(self.nodes.rgns)] )
            for k in range(gd.ntr):

                e_lst = gd.te_to_ge_maps[k]
                n_lst = []
                for m, e in enumerate(e_lst):
                    n_lst = n_lst + ge_to_nodes_map[e]

                n_lst = list(set(n_lst))
                n_lst.sort()

                b = False
                if len(n_lst) == 0:
                    '''
                    print('WARNING in td_and_ae_using_annot: no path found for %i in G.%i (%i)' \
                          % (len(gd.td_lst), self.gcnt, len(n_lst)))
                    #'''
                    pass
                        
                elif len(n_lst) > 0:

                    path_lst = []
                    path = []
                    for m, n in enumerate(n_lst[:-1]):
                        nn = n_lst[m+1]
                        if n in end_nodes:
                            path = path + [n]
                            path_lst.append(path)
                            path = []
                        else:
                            if (self.nodes.rgns[n].type == 'M') & (self.nodes.rgns[nn].type == 'M'):
                                plst = BFS3( self.graph_f, n, nn, MAX_NUM_HOPS )
                                if len(plst) == 1:
                                    path = path + plst[0][:-1]
                                elif len(plst) == 0:
                                    path = path + [n]
                                    path_lst.append(path)
                                    path = []
                                else:
                                    # print('ERROR in td_and_ae_using_annot: # of connecting edges = %i' % (len(plst)) )
                                    # elif len(plst) > 1:
                                    Lens = np.zeros(len(plst))
                                    for i in range(len(plst)): Lens[i] = len(plst[i])
                                    odr = Lens.argsort()
                                    path = path + plst[odr[0]][:-1]
                            else:
                                print('ERROR in td_and_ae_using_annot: %s-%s' % (self.nodes.rgns[n].type, self.nodes.rgns[nn].type))        

                    path = path + [n_lst[-1]]
                    path_lst.append(path)

                    if len(path_lst) == 1:
                        path = path_lst[0]
                        ## check same path
                        b = True
                        midx = -1
                        for m, p in enumerate(p_lst):
                            if len(p) == len(path):
                                cnt_d = 0
                                for i, j in enumerate(p):
                                    if j != path[i]: 
                                        cnt_d += 1
                                        break
                                if cnt_d == 0: 
                                    b = False
                                    midx = m
                                    # print('Same path detected(A %i): %s == %s ' % (kk, gd.td_lst[m].tid, gd.td_lst[k].tid) )
                                    break
                        if b:
                            p_lst.append(path)
                            s_lst.append(gd.td_lst[k].istrand)
                            c_lst.append(gd.td_lst[k].icds)
                            p_idx[k] = n_p
                            n_p += 1
                        else:
                            p_idx[k] = midx
                            pass
                        
                        
                    elif len(path_lst) > 1:
                        if kk < (N-1):
                            for m in range(len(path_lst)-1):
                                n1 = path_lst[m][-1]
                                n2 = path_lst[m+1][0]
                                if bp[n1,n2] == 0:
                                    r1 = self.nodes.rgns[n1]
                                    r2 = self.nodes.rgns[n2]

                                    cd = r2.cvg[0]
                                    if len(self.graph_b[n2]) > 0:
                                        for rt in self.graph_b[n2]:
                                            if rt < self.n_nodes:
                                                cd -= self.nodes.rgns[rt].ave_cvg_depth()
                                            else:
                                                cd -= self.edges.rgns[rt%self.n_nodes].ave_cvg_depth()
                                    if cd <= 0: cd = 1
                                    r_n_new = region_nd( r1.chr, r1.end+1, r2.start-1, 'N', cvg_dep = CVG_DEPTH_TMP )
                                    b = True
                                    for r in edges_new.rgns:
                                        if r.is_the_same_as(r_n_new): 
                                            b = False
                                            break
                                    if b: 
                                        edges_new.rgns.append(r_n_new)
                                        bp[n1,n2] = 1
                                    bc = True

                                    # edges.rgns.append(r_n_new)
                                    # edges.set_cvg()
                                    # bc = True

                        else: ## last loop
                            Lens = np.zeros(len(path_lst))
                            for m, p in enumerate(path_lst):
                                for n in p:
                                    if n < self.n_nodes:
                                        Lens[m] += self.nodes.rgns[n].get_len()
                            odr = Lens.argsort()
                            path = path_lst[odr[-1]]
                            
                            ## check same path
                            b = True
                            midx = -1
                            for m, p in enumerate(p_lst):
                                if len(p) == len(path):
                                    cnt_d = 0
                                    for i, j in enumerate(p):
                                        if j != path[i]: 
                                            cnt_d += 1
                                            break
                                    if cnt_d == 0: 
                                        b = False
                                        midx = m
                                        # print('Same path detected(B %i): %s == %s ' % (kk, gd.td_lst[m].tid, gd.td_lst[k].tid) )
                                        break
                            if b:
                                p_lst.append(path)
                                s_lst.append(gd.td_lst[k].istrand)
                                c_lst.append(gd.td_lst[k].icds)
                                p_idx[k] = n_p
                                n_p += 1
                            else:
                                p_idx[k] = midx
                                pass
            
            if len(edges_new.rgns) == 0: break   
            else: edges.rgns = edges.rgns + edges_new.rgns
         
            if not bc: break
                
        et4 = time.time() - st             
                
        #####################
        #####################
        st = time.time()

        if n_p > 0:
            self.n_p = n_p
            self.p_lst = p_lst
            self.s_lst = s_lst
            self.c_lst = c_lst
            # self.cov_lst = cov_lst

            gd.read_len = self.read_len
            if n_p < gd.ntr:
                pass
                # if verbose: print('WARNING in td_and_ae_using_annot: %i < %i in G.%i' % (n_p, gd.ntr, self.gcnt))
                
            cov_lst = []
            to_del = []
            for k in range(gd.ntr):
                if p_idx[k] >= 0:
                    
                    path = p_lst[p_idx[k]]
                    rgns = regions()
                    rgns2 = regions_nd()
                    flag = 0
                    for n in path:
                        if n < self.n_nodes:
                            rgns.rgns.append(self.nodes.rgns[n]) #.copy(update = True))
                        else:
                            e = n - self.n_nodes
                            rgns2.rgns.append(self.edges.rgns[e]) #.copy(update = True))
                            if self.edges.rgns[e].type == 'D':
                                rgns.rgns.append(self.edges.rgns[e]) #.copy(update = True))
                                
                    gd.add_tr_rgns(k, rgns)
                    gd.td_lst[k].cov_len = rgns.count_valid_NT() # get_cov()
                    # if gd.td_lst[k].cov < 0.8: print('WARNING: %s cov = %4.2f' % (gd.td_lst[k].tid,gd.td_lst[k].cov))
                    # gd.td_lst[k].check_start_stop_codon_pos(rgns, verbose = True)
                                
        else:
            # if verbose: print('WARNING in td_and_ae_using_annot: no path found for %i in G.%i' \
            #                   % (len(gd.td_lst), self.gcnt))
            return([], [], [])

        self.n_p_detected = self.n_p
        self.p_lst_detected = self.p_lst
        
        et5 = time.time() - st             
        st = time.time()
        if self.n_p > 0:
            
            z, G = self.get_z_and_G_using( self.cvgs, self.lens, self.n_nodes, \
                                    self.graph_f, self.graph_b, self.p_lst, abn_norm = 'lin')

            Abn = self.isolasso_ext(z, G, self.cvgs, self.lens, n_alphas = 0)
            '''
            for a in Abn:
                if a < 0:
                    print('W neg abn: %5.2f ' % a)
            #'''
            Vol_in = self.get_valid_volume( self.cvgs, self.lens, self.n_nodes, \
                                    self.graph_f, self.graph_b, self.p_lst)
            
            vol = 0
            for m, p in enumerate(self.p_lst):
                for n in p:
                    if n < self.n_nodes:
                        vol += Abn[m]*self.nodes.rgns[n].get_len()
            
            # print(self.gcnt, Vol_in, vol, z.sum())
            if vol == 0: vol = 1
            nf = Vol_in/vol
            Abn = Abn*nf
            
            tlst, ilst = self.get_trs_from_abn(Abn, s_lst, c_lst)

            n_mapped_trs = np.zeros(self.n_p)
            for k, td in enumerate(gd.td_lst):
                n_mapped_trs[p_idx[k]] += 1
            
            for k, td in enumerate(gd.td_lst):
                if p_idx[k] >= 0:
                    gd.td_lst[k].abn = Abn[p_idx[k]]/n_mapped_trs[p_idx[k]]
           
        et6 = time.time() - st             
        ###########################################################
        ### Revise abundances and Store paths to be used externally

        t_lst = []
        i_lst = []
        gtf_lines = []
        '''
        n_p_d = 0
        p_lst_d = []

        tlst2 = []
        ilst2 = []
        if len(tlst) > 0:
            for m, t in enumerate(tlst):
                tr = Transcript(t.prefix,t.gidx,t.grp_size, n_p_d, t.chr,\
                                t.start,t.end,t.strand,t.cdng, t.seq, t.abn, t.tpm,t.iso_frac, t.prob, t.nexs, Vol_in)
                tlst2.append(tr)

                n_p_d += 1
                p_tmp = self.p_lst[m]
                p_lst_d.append(p_tmp)


        if len(ilst) > 0:

            for m, t in enumerate(ilst):
                tr = Transcript(t.prefix,t.gidx,t.grp_size, n_p_d, t.chr,\
                                t.start,t.end,t.strand,t.cdng,t.seq, t.abn, t.tpm,t.iso_frac, t.prob, t.nexs, Vol_in)
                n_p_d += 1
                p_tmp = self.p_lst[m]
                p_lst_d.append(p_tmp)
                ilst2.append(tr)

        t_lst = t_lst + tlst2
        i_lst = i_lst + ilst2
        #'''
        ets = np.array([et0, et1, et2, et3, et4, et5, et6])

        return gd, t_lst, i_lst, gtf_lines, ets



##########################################################################
## Gene/Transcript descriptor
##########################################################################

# GTF_line = collections.namedtuple('GTF_line', 'chr, src, feature, start, end, score, strand, frame, attr, gid, gname, tid, tname')
# CHR, SRC, FEATURE, GSTART, GEND, SCORE, STRAND, FRAME, ATTR, GID, TID, GNAME, TNAME = [i for i in range(13)]

def find_possible_ss_codon_pos_in(tseq, target = 'start', c = False):
    
    if target == 'start':
        if c: sc = reverse_complement(START_CODON)
        else: sc = START_CODON 
        pos_lst = find_all_s_in_str(tseq, sc)
    else:
        pos_lst = []
        for k, sc in enumerate(STOP_CODONS):
            if c: sc2 = reverse_complement(sc)
            else: sc2 = sc
            pos_lst = pos_lst + find_all_s_in_str(tseq, sc2)
            
        pos_lst.sort()
        
    return pos_lst


def gtf_line_to_str(gtf_line):
    
    l = gtf_line
    s = '%s, %s, %i, %i, %s, %s, %s' % (l.chr, l.feature, l.start, l.end, l.strand, l.gid, l.tid)
    return s
    
def parse_gtf_lines_and_split_into_genes_old( gtf_lines, g_or_t = 'gene', verbose = False ):
    
    gtf_lines_lst = []
    gtf_lines_tmp = []
    # features = get_col(gtf_lines, FEATURE)

    ## assume sorted
    ids = []
    id_prev = None
    nex_p = 10000
    
    for k, gl in enumerate(gtf_lines):
        b = True
        if (g_or_t == 'gene'):
            id_cur = gl.gid
        elif (g_or_t == 'transcript'):
            id_cur = gl.tid
            if (gl.feature == 'gene'): b = False
                
        if b:
            if (gl.feature == g_or_t) | (id_prev is None) | (id_cur != id_prev):
                if id_prev is not None:
                    gtf_lines_lst.append(gtf_lines_tmp)
                    ids.append(id_prev)

                gtf_lines_tmp = [gl]
                id_prev = id_cur
            else:
                gtf_lines_tmp.append(gl)
            
    if len(gtf_lines_tmp) > 0:
        gtf_lines_lst.append(gtf_lines_tmp)
    if verbose: print('\rSorting GTF lines (%s) ... done' % g_or_t )
    del gtf_lines_tmp
    del gtf_lines
    
    return gtf_lines_lst


def parse_gtf_lines_and_split_into_genes( gtf_lines, g_or_t = 'gene', verbose = False ):
    
    gtf_lines_lst = []
    
    if g_or_t == 'gene': 
        gids = get_col(gtf_lines, GID)
    elif g_or_t == 'transcript':
        gids = get_col(gtf_lines, TID)
    
    gid_set = list(set(gids))
    gtf_lines_dict = { gid: [] for gid in gid_set }
    
    for k, gl in enumerate(gtf_lines):
        gid = gids[k]
        if g_or_t == 'gene':
            gtf_lines_dict[gid].append(gl)
        else:
            if gl.feature != 'gene':
                gtf_lines_dict[gid].append(gl)
        
    for key in gtf_lines_dict.keys():
        if len(gtf_lines_dict[key]) > 0:
            gtf_lines_lst.append(gtf_lines_dict[key])
            
    if verbose: print('\rSorting GTF lines (%s) ... done' % g_or_t )
    return gtf_lines_lst


def get_base_cds_from_gtf_lines(gtf_lines):
    
    n = -1
    for line in gtf_lines:
        if line.feature == 'CDS':
            n = 0
            break
    return n
    '''
    features = get_col(gtf_lines, FEATURE)
    if 'CDS' in features: return 0
    else: return -1
    '''
    
POS_info = collections.namedtuple('POS_info', 'abs_start, abs_end, start, end') # one-base

class location_finder:
    
    def __init__(self):
        self.pos_lst = []
        
    def add( self, abs_start, abs_end, start):
        Len = abs_end - abs_start + 1
        end = start + Len - 1
        self.pos_lst.append( POS_info(abs_start, abs_end, start, end) )
        
    def abs_pos( self, loc ):
        abs_loc = -1
        for pos in self.pos_lst:
            if (loc >= pos.start) & (loc <= pos.end):
                abs_loc = pos.abs_start + (loc - pos.start)
                break
        return abs_loc
    
    def rel_pos( self, abs_loc ):
        loc = -1
        for pos in self.pos_lst:
            if (abs_loc >= pos.abs_start) & (abs_loc <= pos.abs_end):
                loc = pos.start + (abs_loc - pos.abs_start)
                break
        return loc
    
    def get_cds_regions( self, rel_start_pos, rel_stop_pos, tlen, chrm, istrand):
        
        Len = rel_stop_pos - rel_start_pos
        if rel_start_pos > rel_stop_pos:
            print('ERROR in get_regions: %i > %i' % (rel_start_pos, rel_stop_pos))
        if istrand >= 0:
            start = rel_start_pos
            end = rel_stop_pos-1
        else:
            start = tlen - (rel_stop_pos)
            end = tlen - (rel_start_pos) -1 
            
        Len2 = 0
        cds = regions()
        be = False
        if True:
            b = False
            for pos in self.pos_lst:
                if (start >= pos.start) & (start <= pos.end):
                    abs_start = pos.abs_start + (start-pos.start)
                    if end <= pos.end:
                        abs_end = pos.abs_start + (end - pos.start)
                        start = end
                        b = True
                    else:
                        abs_end = pos.abs_end
                        start = start + (abs_end - abs_start + 1)
                        if start > end: b = True
                        
                    r = region(chrm, abs_start, abs_end, 'CDS', xs = istrand)
                    cds.rgns.append(r)
                    Len2 += (abs_end - abs_start + 1)
                    
                    if b: break
                if b: break
                    
            if Len != Len2:
                print('ERROR in get_regions: %i != %i (%i)' % (Len, Len2, istrand))

            if not b:
                if start != end:
                    # print('WARNING: CDS not fully covered (%i > %i)' % (start, end))
                    be = True

        return cds, be
    
    def print(self):
        for pos in self.pos_lst:
            print('%i - %i: %i - %i' % (pos.abs_start, pos.abs_end, pos.start, pos.end))
    


def set_fa_header(name, Len, abn, strand, cdng):
    
    hdr = '%s length:%i abn:%3.2f strand:%s %s' % (name, Len, abn, get_c_from_istrand(strand), get_str_from_icdng(cdng))
    return hdr
    

CODON_NOT_SPECIFIED = -1
CODON_VALID = 0
CODON_NOT_COVERED = 1
CODON_WITH_VARIANT = 2
CODON_WITH_INDEL = 3
CODON_RELOCATED = 4
CODON_NOT_IDENTIFIED = 5
CODON_POS_ESTIMATED = 6

Codon_Status = {-1:'not specified', 0: 'valid', 1: 'not covered', 2: 'SNP found', \
                3: 'InDel found', 4: 'relocated', 5: 'not identified', 6: 'pos estimated'}
    
TR_exp_info = collections.namedtuple('TR_info', 'tid, tname, gid, gname, cov, abn, tpm')  

'''
Transcript = collections.namedtuple('Transcript', \
                                    'prefix, gidx, grp_size, icnt, chr, start, end, \
                                     strand, cdng, seq, abn, tpm, iso_frac, prob, nexs, gvol')
'''

NV_info_ext_tr = collections.namedtuple('NV_info_ext_tr', 'chr, pos_ref, pos_new, gene_id, gene_name, v_type, v_len, cvg_depth, cvg_frac, \
                                  ref_prev, ref_seq, ref_next, alt_prev, alt_seq, alt_next, v_class, \
                                  v_class_tr, strand, cDNA_change, Codon_change, Protein_change, Protein_change2') #, Check')  # one-base

def get_nv_info_tr( pseq_in, istrand, rel_pos_in, nv, tid ):

    v_class_tr = nv.v_class_tr
    if istrand > 0:
        pseq = pseq_in
        start = rel_pos_in
        Len = nv.v_len
        
        ref_prev = pseq[:start] # nv.ref_prev
        if nv.v_type == 'V':
            ref_next = pseq[(start+Len):] # nv.ref_next
        elif nv.v_type == 'D':
            ref_next = pseq[(start+Len):] # nv.ref_next
        elif nv.v_type == 'I':
            ref_next = pseq[start:] # nv.ref_next

        if nv.ref_seq == '-':
            ref_seq = ''
        else:
            ref_seq = nv.ref_seq
        if nv.alt_seq == '-':
            alt_seq = ''
        else:
            alt_seq = nv.alt_seq
            
    elif istrand < 0:
        
        pseq = reverse_complement(pseq_in)
        if nv.v_type == 'V':
            start = len(pseq) - (rel_pos_in + nv.v_len)
        elif nv.v_type == 'D':
            start = len(pseq) - (rel_pos_in + nv.v_len)
        elif nv.v_type == 'I':
            start = len(pseq) - (rel_pos_in)
            
        Len = nv.v_len
        ref_prev = pseq[:start] # reverse_complement(nv.ref_next)
        # ref_next = pseq[start:] # reverse_complement(nv.ref_prev)
        if nv.v_type == 'V':
            ref_next = pseq[(start+Len):] # nv.ref_next
        elif nv.v_type == 'D':
            ref_next = pseq[(start+Len):] # nv.ref_next
        elif nv.v_type == 'I':
            ref_next = pseq[start:] # nv.ref_next
        
        if nv.ref_seq == '-':
            ref_seq = ''
        else:
            ref_seq = reverse_complement(nv.ref_seq)
        if nv.alt_seq == '-':
            alt_seq = ''
        else:
            alt_seq = reverse_complement(nv.alt_seq)
    else:
        return None

    os = start%3
    if nv.v_type == 'V':
        os_e = (start+Len)%3
    elif nv.v_type == 'D':
        os_e = (start+Len)%3
    elif nv.v_type == 'I':
        os_e = (start)%3
        
    if nv.v_type == 'V':
        if Len == 1:
            dc = 'c.%i%s>%s' % (start+1, ref_seq, alt_seq)
        elif Len > 1:
            dc = 'c.%i_%i%s>%s' % (start+1, start+Len, ref_seq, alt_seq)
            
        sq_org = ref_seq.upper()
        sq_new = alt_seq.upper()
        if (os > 0) & (len(ref_prev) > 0):
            sq_org = ref_prev[max(0, len(ref_prev)-os):].lower() + sq_org
            sq_new = ref_prev[max(0, len(ref_prev)-os):].lower() + sq_new
        if (os_e > 0) & (len(ref_next) > 0):
            sq_org = sq_org + ref_next[:min((3-os_e)%3, len(ref_next))].lower()
            sq_new = sq_new + ref_next[:min((3-os_e)%3, len(ref_next))].lower()
                    
        cc = 'c.(%i-%i)%s>%s' % (start-os+1, start-os + len(sq_new), sq_org, sq_new)
        p_org = translate(sq_org)
        p_new = translate(sq_new)

        if p_org != p_new:
            v_class_tr = 'Missense_Mutation'
            pc = 'p.%s%i%s' % ( p_org, int((start-os)/3)+1,  p_new)
            pc2 = pc
        else:
            v_class_tr = 'Silent'
            pc = ''
            pc2 = pc
            
        if (start < 3):
            v_class_tr = 'Start_Codon_SNP'
        elif (start >= len(pseq)-3):
            # Stop codon invalid
            if (sq_new[-3:].upper() != 'TGA') & (sq_new[-3:].upper() != 'TAA') & (sq_new[-3:].upper() != 'TAG'):
                v_class_tr = 'Nonsense_Mutation (Stop codon garbled)'
        else:
            # early stop
            if p_new.find('*') >= 0:
                if p_org.find('*') == 0:
                    v_class_tr = 'Nonsense_Mutation (Early stop)' # % (int((len(pseq) - start)/3))
            
    elif nv.v_type == 'D':
        if Len == 1:
            dc = 'c.%idel%s' % (start+1, ref_seq)
        elif Len > 1:
            dc = 'c.%i_%idel%s' % (start+1, start+Len, ref_seq)

        sq_org = ref_seq.upper()
        sq_new = ''
        if (os > 0) & (len(ref_prev) > 0):
            sq_org = ref_prev[max(0, len(ref_prev)-os):].lower() + sq_org
            sq_new = ref_prev[max(0, len(ref_prev)-os):].lower() + sq_new
            
        if (os_e > 0) & (len(ref_next) > 0):
            sq_org = sq_org + ref_next[:min((3-os_e)%3, len(ref_next))].lower()
    
        os2 = len(sq_new)%3
        if (os2 > 0) & (len(ref_next) > 0):
            sq_new = sq_new + ref_next[:min((3-os2)%3, len(ref_next))].lower()
            
        cc = 'c.(%i-%i)%sdel' % (start-os+1, start+Len+(3-os_e)%3, sq_org)
        p_org = translate(sq_org)
        p_new = translate(sq_new)
        if Len%3 == 0:
            if os == 0:
                pc = 'p.%s%idel' % ( p_org, int((start-os)/3)+1)
                pc2 =pc #  'p.%s%idel%s' % ( p_org, int((start-os)/3), p_new)
            else:
                if p_new[0] == p_org[0]:
                    pc = 'p.%s%idel' % ( p_org[1:], int((start-os)/3)+2)
                    pc2 ='p.%i_%i%s>%s' % ( int((start-os)/3)+1, int((start-os)/3)+len(p_org), p_org, p_new) #  'p.%s%idel%s' % ( p_org, int((start-os)/3), p_new)
                else:
                    pc = 'p.%i_%i%s>%s' % ( int((start-os)/3)+1, int((start-os)/3)+len(p_org), p_org, p_new)
                    pc2 = pc
                    
            v_class_tr = 'In_Frame_Del'
        else:
            pc = 'p.%s%ifs' % ( p_org, int((start-os)/3)+1)
            pc2 = pc # + '_%s>%s...' % ( p_org, p_new) 
            v_class_tr = 'Frame_Shift_Del'
            
        if (start < 3):
            if sq_new[:3].upper() != 'ATG':
                v_class_tr = 'Start_Codon_Del'
        elif (start > len(pseq)-3):
            # Stop codon invalid
            if (sq_new[-3:].upper() != 'TGA') & (sq_new[-3:].upper() != 'TAA') & (sq_new[-3:].upper() != 'TAG'):
                v_class_tr = 'Nonsense_Mutation (Stop codon garbled)'
        else:
            # early stop
            if p_new.find('*') >= 0:
                if p_org.find('*') == 0:
                    v_class_tr = 'Nonsense_Mutation (Early stop)' # % (int((len(pseq) - start)/3))

    elif nv.v_type == 'I':
        
        dc = 'c.%i_%iins%s' % (start, start+1, alt_seq)
        
        sq_org = ''
        sq_new = alt_seq.upper()
        if (os > 0) & (len(ref_prev) > 0):
            sq_org = ref_prev[max(0, len(ref_prev)-os):].lower() + sq_org
            sq_new = ref_prev[max(0, len(ref_prev)-os):].lower() + sq_new

        if (os_e > 0) & (len(ref_next) > 0):
            sq_org = sq_org + ref_next[:min((3-os_e)%3, len(ref_next))].lower()
        if len(sq_org) == 0:
            sq_org = sq_org + ref_next[:min((3-os_e), len(ref_next))].lower()
            
        os2 = len(sq_new)%3
        if (os2 > 0) & (len(ref_next) > 0):
            sq_new = sq_new + ref_next[:min((3-os2)%3, len(ref_next))].lower()

        cc = 'c.(%i-%i)%sins' % (start-os+1, start+Len+(3-os2)%3, sq_new)
        p_org = translate(sq_org)
        p_new = translate(sq_new)
        if Len%3 == 0:
            if os == 0:
                pc = '%i_%iins%s' % ( int((start-os)/3), int((start-os)/3)+1, p_new)
                pc2 =pc #  'p.%s%idel%s' % ( p_org, int((start-os)/3), p_new)
            else:
                if p_new[0] == p_org[0]:
                    pc = '%i_%iins%s' % ( int((start-os)/3)+2, int((start-os)/3)+3, p_new[1:])
                    pc2 ='p.%i_%i%s>%s' % ( int((start-os)/3)+1, int((start-os)/3)+len(p_org), p_org, p_new)
                else:
                    pc = 'p.%i_%i%s>%s' % ( int((start-os)/3)+1, int((start-os)/3)+len(p_org), p_org, p_new)
                    pc2 =pc # + '_%s>%s' % ( p_org, p_new)
                    
            v_class_tr = 'In_Frame_Ins'
        else:
            pc = 'p.%s%ifs' % ( p_new, int((start-os)/3)+1)
            pc2 = pc # 'p.%s%iins%s' % ( p_org, int((start-os)/3)+1, p_new)
            v_class_tr = 'Frame_Shift_Ins'

        if (start < 3):
            if sq_new[:3].upper() != 'ATG':
                v_class_tr = 'Start_Codon_Ins'
        elif (start > len(pseq)-3):
            # Stop codon invalid
            if (sq_new[-3:].upper() != 'TGA') & (sq_new[-3:].upper() != 'TAA') & (sq_new[-3:].upper() != 'TAG'):
                v_class_tr = 'Nonsense_Mutation (Stop codon garbled)'
        else:
            # early stop
            if p_new.find('*') >= 0:
                if p_org.find('*') == 0:
                    v_class_tr = 'Nonsense_Mutation (Early stop)' # % (int((len(pseq) - start)/3))

    if istrand > 0:
        strand = '+'
    elif istrand < 0:
        strand = '-'
    else:
        strand = '.'

    if nv.v_type == 'V':
        L = Len
    elif nv.v_type == 'D':
        L = Len
    elif nv.v_type == 'I':
        L = 0
        
    nv_info = NV_info_ext_tr(nv.chr, nv.pos_ref, nv.pos_new, tid, nv.gene_name, nv.v_type, nv.v_len, nv.cvg_depth, \
                             nv.cvg_frac, nv.ref_prev, nv.ref_seq, nv.ref_next, nv.alt_prev, nv.alt_seq, nv.alt_next, nv.v_class, \
                             v_class_tr, strand, dc, cc, pc, pc2) #, pseq[max(0, start-3):min(start+3+L, len(pseq))] )
    return nv_info

class transcript_descriptor:

    # if self.istrand != 0
    def get_cds_nv_info( self, nv_info_lst_from_gene, cds_rgns, cnt_e ):

        nv_info_lst = []

        proc = np.full(len(nv_info_lst_from_gene), False)
        for k, nv in enumerate(nv_info_lst_from_gene):
            v_type = nv.v_type
            if nv.ref_seq == '-':
                r = region( nv.chr, nv.pos_ref, nv.pos_ref, 'cds', '', cvg_dep = 1 )
            else:
                r = region( nv.chr, nv.pos_ref, nv.pos_ref+nv.v_len-1, 'cds', nv.ref_seq, cvg_dep = 1 )

            b = False
            for i in self.tc_to_gc_map:
                if (cds_rgns[i].type.lower() == 'cds') | (cds_rgns[i].type.lower() == 'stop_codon'):
                    if cds_rgns[i].has_ext_intersection_with(r):
                        b = True
                        rel_pos = self.lof.rel_pos( nv.pos_ref )
                        if rel_pos > len(self.pseq):
                            cnt_e += 1
                            # print('\nERROR in transcript_descriptor:get_cds_nv_info: %i > %i' % (rel_pos, len(self.pseq)), end = '')
                        else:
                            nv_tr = get_nv_info_tr( self.pseq, self.istrand, rel_pos, nv, self.tid )
                            if nv_tr is not None:
                                nv_info_lst.append(nv_tr)
                            break
            proc[k] = b

        return  nv_info_lst, proc, cnt_e
    

    def get_org_coding_seq(self, cds_rgns, genome_seq):

        pseq = ''
        lof = location_finder()
        
        for i in self.tc_to_gc_map:
            if (cds_rgns[i].type.lower() == 'cds') | (cds_rgns[i].type.lower() == 'stop_codon'):
                lof.add( cds_rgns[i].start, cds_rgns[i].end, len(pseq))
                pseq = pseq + genome_seq[ (cds_rgns[i].start-1):cds_rgns[i].end ]
                
        self.pseq = pseq
        self.lof = lof

    
    def get_transcript_tuple(self):
        
        return Transcript(self.prefix, self.gid, self.grp_size, self.icnt, self.chr, self.begin, self.end, \
                          get_c_from_istrand(self.istrand), get_str_from_icdng(self.icds), self.tseq, \
                          self.abn, self.tpm, self.iso_frac, self.prob, self.nexons, self.gvol)

    def __init__(self, gtf_lines_of_a_tr = None, exon_rgns = None, cds_rgns = None, genome = None, \
                 cds = -1, fill = False, verbose = False):
 
        # self.gtf_lines = gtf_lines_of_a_tr
        self.chr = ''
        self.begin = -1      ## 1-base
        self.end = -1        ## 1-base
        
        self.gid = ''
        self.gname = ''
        self.tid = ''
        self.tname = ''
        self.biotype = ''
        self.istrand = 0
        self.icds = cds       ## -1: unspecified, 0: non-coding, 1: coding
        
        ## used in td_and_ae
        self.te_to_ge_map = []
        self.tc_to_gc_map = []
        self.tr_to_gr_map = []
        self.abn = 0
        self.cov = 0
        self.tlen = -1
        self.plen = -1
        
        self.cov_len = 0
        self.cov_ratio = 0

        ## Temporary variables
        self.prefix = 'X'
        self.prob = 0
        self.gvol = 0
        self.nexons = 0
        self.len_os = -1
        self.pos_start = -1  ## 0-base
        self.pos_stop = -1   ## 0-base
        
        ## Tr info
        self.tpm = -1
        self.icnt = -1
        self.grp_size = -1
        self.iso_frac = -1

        ## Codon pos and status
        self.start_codon_pos_org = (-1,-1)
        self.stop_codon_pos_org = (-1,-1)
        
        self.start_codon_event = -1
        self.stop_codon_event = -1
        
        self.start_codon_pos = (-1,-1)
        self.stop_codon_pos = (-1,-1)

        self.start_codon_status = -1
        self.stop_codon_status = -1
        
        ## filled with get_seq_from_exons()
        self.lof = None
        if genome is not None:
            self.lof = location_finder()
        self.tseq = ''
        self.pseq = ''
        self.aseq = ''

        if (gtf_lines_of_a_tr is not None):
        
            ##################
            ### Using GTF only
            
            # df = pd.DataFrame(gtf_lines_of_a_tr)
            tnames = np.array(get_col(gtf_lines_of_a_tr, TID))
            biotypes = np.array(get_col(gtf_lines_of_a_tr, BIOTYPE))
            feature_lst = get_col(gtf_lines_of_a_tr, FEATURE)
            features = np.array(feature_lst)
            chrms = np.array(get_col(gtf_lines_of_a_tr, CHR))
            strands = np.array(get_col(gtf_lines_of_a_tr, STRAND))
            
            ## check if all the lines have the same tid
            tr_names = list(set(tnames))

            if len(tr_names) != 1:
                print('   ERROR transcript_descriptor:init: %i tr_ids' % len(tr_names))
            
            self.gid = gtf_lines_of_a_tr[0].gid
            self.gname = gtf_lines_of_a_tr[0].gname
            self.tid = gtf_lines_of_a_tr[0].tid
            self.tname = gtf_lines_of_a_tr[0].tname
            self.biotype = gtf_lines_of_a_tr[0].biotype
            
            ## check if all the lines have the same tid
            chrs = list(set(chrms))
            if len(chrs) != 1:
                print('   WARNING transcript_descriptor:init: %i chrs found in %s' % (len(chrs), self.tid))
                # print('   This may cause unexpected results')
                # print('   Fusion genes are not considered in the current version of stringfix')

            self.chr = chrs[0]
            
            ## check if all the lines have the same tid
            strnds = list(set(strands))
            if len(strnds) != 1:
                print('   ERROR transcript_descriptor:init: %i strands' % len(strnds))
            
            if strands[0] == '+': self.istrand = +1
            elif strands[0] == '-': self.istrand = -1
            else: self.istrand = 0
            
            ## Check start/stop codon
            
            wh = which((features == 'start_codon') | (features == 'START_CODON'))
            if len(wh) > 0:
                w = wh[0]
                self.start_codon_pos_org = (gtf_lines_of_a_tr[w].start, gtf_lines_of_a_tr[w].end)
            if len(wh) > 1:
                if verbose: print('   WARNING transcript_descriptor:init: %i start codons' % len(wh))
            
            wh = which((features == 'stop_codon') | (features == 'STOP_CODON'))
            if len(wh) > 0:
                w = wh[0]
                self.stop_codon_pos_org = (gtf_lines_of_a_tr[w].start, gtf_lines_of_a_tr[w].end)
            if len(wh) > 1:
                if verbose: print('   WARNING transcript_descriptor:init: %i stop codons' % len(wh))
            
                
            ## initial start/stop position using start/stop codon info.
            pstart = -1
            pstop = -1
            for gtfl in gtf_lines_of_a_tr:
                if (gtfl.feature == 'start_codon') | (gtfl.feature == 'START_CODON'): 
                    self.start_codon_pos_org = (gtfl.start, gtfl.end)
                    if self.istrand >= 0:
                        pstart = gtfl.start-1
                    else:
                        pstart = gtfl.end
                elif (gtfl.feature == 'stop_codon') | (gtfl.feature == 'STOP_CODON'): 
                    self.stop_codon_pos_org = (gtfl.start, gtfl.end)
                    if self.istrand >= 0:
                        pstop = gtfl.start-1
                    else:
                        pstop = gtfl.end
                    
                    
            ## start/stop position using start/stop codon info.
            # self.exons = regions()
            # self.cds = regions()
            ecnt = 0
            t_len = 0
            p_len = 0
            start = -1
            stop = -1
            last_pos = 0
            for gtfl in gtf_lines_of_a_tr:
                pos_start = gtfl.start-1
                pos_end = gtfl.end
                
                if self.tid != gtfl.tid:
                    print('   ERROR in transcript_descriptor:init: %s != %s' % (self.tid, gtfl.tid) )
                else:
                    if (gtfl.feature.lower() == 'exon') | (gtfl.feature == 'insersion'):

                        ## to estimate start/stop codon pos
                        if (pstart >= 0):
                            if (pstart >= pos_start) & (pstart <= pos_end):
                                start = t_len + (pstart - pos_start)

                        if ((pstop >= 0)):
                            if (pstop >= pos_start) & (pstop <= pos_end):
                                stop = t_len + (pstop - pos_start)

                        ## to initialize self.exons
                        last_pos = pos_end
                        Len = pos_end - pos_start
                        t_len = t_len + Len

                        exon_num, cov, abn, seq, evnt, sts, cf = get_other_attrs_from_gtf_attr(gtfl.attr)
                        
                        if (cov == 0) & (seq is not None):
                            seq = 'N'*(pos_end-pos_start)
                        cm = True

                        if not fill:
                            abn, cm, seq = 0, False, ''

                        # elif fill & ((abn < 0) | (cov < 0) | (seq is None)):
                        #    cov, abn, cm, seq = 1, 1, True, 'N'*(pos_end-pos_start)

                        r = region( gtfl.chr, pos_start+1, pos_end, gtfl.feature, seq, cvg_dep = abn, cm = cm, xs = self.istrand )
                        r.cvg_frac = cf
                        # r_mi = region( gtfl.chr, pos_start+1, pos_end, gtfl.feature, seq_or_cmat = seq, cvg_dep = 0, xs = self.istrand )
                        # self.exons.rgns.append( r )
                        ##################################################
                        b = True
                        for m,s in enumerate(exon_rgns):
                            if r.is_the_same_as(s):
                                self.te_to_ge_map.append(m)
                                b = False
                                break
                        if b: 
                            m = len(exon_rgns)
                            self.te_to_ge_map.append(m)
                            exon_rgns.append( r )
                        ##################################################
                        ecnt += 1

                        ## to estimate transcript span
                        if self.begin < 0: 
                            self.begin = pos_start+1
                        else:
                            self.begin = min( self.begin, pos_start+1 )
                        if self.end < 0: 
                            self.end = pos_end
                        else:
                            self.end = max( self.end, pos_end )

                    elif (gtfl.feature == 'deletion'):

                        exon_num, cov, abn, seq, evnt, sts, cf = get_other_attrs_from_gtf_attr(gtfl.attr)

                        if not fill: 
                            abn = 0

                        r = region_nd( gtfl.chr, pos_start+1, pos_end, gtfl.feature, cvg_dep = abn, xs = self.istrand )
                        r.cvg_frac = cf
                        # r_d = region_nd( gtfl.chr, pos_start+1, pos_end, gtfl.feature, cvg_dep = abn, xs = self.istrand )
                        # self.exons.rgns.append( r )
                        ##################################################
                        b = True
                        for m,s in enumerate(exon_rgns):
                            if r.is_the_same_as(s):
                                self.te_to_ge_map.append(m)
                                b = False
                                break
                        if b: 
                            m = len(exon_rgns)
                            self.te_to_ge_map.append(m)
                            exon_rgns.append( r )
                        ##################################################
                        ecnt += 1

                    elif (gtfl.feature.lower() == 'cds') | (gtfl.feature.lower() == 'start_codon') | (gtfl.feature.lower() == 'stop_codon') |  (gtfl.feature.lower() == 'utr') \
                         | (gtfl.feature.lower() == 'five_prime_utr') | (gtfl.feature.lower() == 'three_prime_utr') | (gtfl.feature.lower() == 'selenocysteine'):
                        ## to initialize self.exons
                        Len = pos_end - pos_start
                        p_len = p_len + Len

                        exon_num, cov, abn, seq, evnt, sts, cf = get_other_attrs_from_gtf_attr(gtfl.attr)

                        '''
                        if (gtfl.feature.lower() == 'cds') | (gtfl.feature.lower() == 'stop_codon'):
                            if genome is not None:
                                if gtfl.chr in genome.keys():
                                    self.lof.add( gtfl.start, gtfl.end, len(self.pseq))
                                    psq =  genome[gtfl.chr].seq[(gtfl.start-1):gtfl.end]
                                    self.pseq = self.pseq + psq
                        '''
                        if (gtfl.feature.lower() == 'start_codon') & (evnt is not None): 
                            self.start_codon_event = int(evnt.split(':')[0])
                        elif (gtfl.feature.lower() == 'stop_codon') & (evnt is not None): 
                            self.stop_codon_event = int(evnt.split(':')[0])
                        
                        if seq is None: seq = ''
                        cm = True
                        if not fill: 
                            abn, cm, seq = 0, False, ''

                        r = region( gtfl.chr, pos_start+1, pos_end, gtfl.feature, seq, cm = False, cvg_dep = 0, xs = self.istrand )
                        # self.cds.rgns.append( r )
                        ##################################################
                        b = True
                        for m,s in enumerate(cds_rgns):
                            if r.is_the_same_as(s):
                                self.tc_to_gc_map.append(m)
                                b = False
                                break
                        if b: 
                            m = len(cds_rgns)
                            self.tc_to_gc_map.append(m)
                            cds_rgns.append( r )
                        ##################################################
                        
                    elif (gtfl.feature == 'transcript'):
                        exon_num, cov, abn, seq, evnt, sts, cf = get_other_attrs_from_gtf_attr(gtfl.attr)

                        if abn >= 0: self.abn = abn
                        if cov >= 0: self.cov = cov
            '''
            if len(self.te_to_ge_map) == 0:
                print('=========================')
                for gtfl in gtf_lines_of_a_tr:
                    print_gtf(gtfl)
            ''' 

            if len(self.tc_to_gc_map) > 0: self.icds = 1
                
            self.tlen = t_len
            if self.cov >= 0: self.cov_len = int(self.cov*t_len)
            self.plen = p_len
            self.nexons = ecnt
            # self.te_to_ge_map = np.full(ecnt,-1, dtype = np.int32)
            
            if p_len == 0:
                if (start >= 0) & (stop >= 0):
                    p_len = stop - start
                    pass
                elif (start >= 0) & (stop < 0):
                    if verbose: print('   WARNING transcript_descriptor:init: (A) start %i, stop %i, Plen = %i' % (start, stop, p_len))
                    p_len = t_len - start
                    self.len_os = p_len%3
                    stop = start + p_len - self.len_os
                elif (start < 0) & (stop >= 0):
                    if verbose: print('   WARNING transcript_descriptor:init: (B) start %i, stop %i, Plen = %i' % (start, stop, p_len))
                    p_len = stop
                    self.len_os = p_len%3
                    start = stop - (p_len - self.len_os)
            else:
                self.len_os = p_len%3
                if (start >= 0) & (stop >= 0):
                    pass
                elif (start >= 0) & (stop < 0):
                    if verbose: print('   WARNING transcript_descriptor:init: (C) start %i, stop %i, Plen = %i' % (start, stop, p_len))
                    stop = start + p_len
                elif (start < 0) & (stop >= 0):
                    if verbose: print('   WARNING transcript_descriptor:init: (D) start %i, stop %i, Plen = %i' % (start, stop, p_len))
                    start = stop - (p_len - self.len_os)
                else:
                    if verbose: print('   WARNING transcript_descriptor:init: (E) start %i, stop %i, Plen = %i' % (start, stop, p_len))
            

            if (p_len > 0) & (start >= 0) & (stop >= 0):
                if self.istrand >= 0:
                    self.pos_start = start
                    if (start >= 0):
                        if stop < 0: stop = start + p_len ## os may not be 0
                    self.pos_stop = stop
                else:
                    self.pos_start = t_len - start - 3
                    self.pos_stop = t_len - stop - 3
                    
            if len(self.pseq) > 0:
                if self.istrand > 0:
                    # if len(self.pseq)%3 != 0:
                    #     print('   WARNING transcript_descriptor:init: (E) G/TID: %s, %s, Len = %i' % (self.gid, self.tid, len(self.pseq)))
                    self.aseq = translate(self.pseq)
                elif self.istrand < 0:
                    # if len(self.pseq)%3 != 0:
                    #     print('   WARNING transcript_descriptor:init: (E) G/TID: %s, %s,  Len = %i' % (self.gid, self.tid, len(self.pseq)))
                    pseq = reverse_complement(self.pseq)
                    self.aseq = translate(pseq)
                else:
                    print('   WARNING transcript_descriptor:init: (E) G/TID: %s, %s, Strand unspecified' % (self.gid, self.tid) )
                
        return # self.te_to_ge_map
                

    '''
    CODON_NOT_SPECIFIED = -1
    CODON_VALID = 0
    CODON_NOT_COVERED = 1
    CODON_WITH_VARIANT = 2
    CODON_WITH_INDEL = 3
    CODON_RELOCATED = 4
    CODON_NOT_IDENTIFIED = 5
    CODON_POS_ESTIMATED = 6
    '''

    def check_start_stop_codon_pos(self, exons, verbose = False):
        
        if (exons is not None): 
            # exons = self.exons
            
            ## Update start/stop codon
            if (self.start_codon_pos_org[0] > 0):
                # find exon that contains start codon
                sc = region( self.chr, self.start_codon_pos_org[0], self.start_codon_pos_org[1], 'M')
                b = -1
                self.start_codon_event = CODON_NOT_COVERED
                for e in exons.rgns:
                    if e.has_ext_intersection_with(sc):
                        # check code
                        loc = sc.start - e.start
                        if self.istrand > 0:
                            if (loc >= 0) & (loc <= (e.get_len()-3)):
                                seq = e.get_seq()
                                if seq[loc:(loc+3)] == START_CODON:
                                    b = 0
                                    self.start_codon_event = CODON_VALID
                                elif seq[loc:(loc+3)].count('N') > 0:
                                    b = 0
                                    self.start_codon_event = CODON_NOT_COVERED
                                else:
                                    b = 1
                                    if len(self.tseq) > 0:
                                        scodon_org = self.tseq[self.pos_start:(self.pos_start+3)]
                                    else:
                                        scodon_org = START_CODON
                                    self.start_codon_event = CODON_WITH_VARIANT
                                    if verbose: print('   SNP detected in Start codon of %s: %s -> %s' % (self.tid, scodon_org, seq[loc:(loc+3)]) )
                            elif (loc > (e.get_len()-3)) | (loc < 0):
                                b = 2
                                self.start_codon_event = CODON_WITH_INDEL
                                # print('INDEL might happen')
                                # print('INFO in update_info: %s start codon seems to be moved. (Cov:%i, L:%i)' % (self.tid, int(100*self.cov/self.len), self.len))

                        elif self.istrand < 0:
                            if (loc >= 0) & (loc <= (e.get_len()-3)):
                                seq = e.get_seq()
                                if seq[loc:(loc+3)] == rc_START_CODON:
                                    b = 0
                                    self.start_codon_event = CODON_VALID
                                elif seq[loc:(loc+3)].count('N') > 0:
                                    b = 0
                                    self.start_codon_event = CODON_NOT_COVERED
                                else:
                                    b = 1
                                    if len(self.tseq) > 0:
                                        ps = len(self.tseq) - self.pos_start - 3
                                        scodon_org = self.tseq[ps:(ps+3)]
                                    else:
                                        scodon_org = rc_START_CODON
                                    self.start_codon_event = CODON_WITH_VARIANT
                                    if verbose: print('   SNP detected in Start codon of %s: %s -> %s' % (self.tid, scodon_org, seq[loc:(loc+3)]) )
                            elif (loc > (e.get_len()-3)) | (loc < 0):
                                b = 2
                                if loc < 0: 
                                    self.start_codon_event = CODON_WITH_INDEL
                                    if verbose: print('   INDEL detected in Start codon of %s' % (self.tid) )
                                # print('INFO in update_info: %s start codon seems to be moved. (Cov:%i, L:%i)' % (self.tid, int(100*self.cov/self.len), self.len))


                        if b == 0:
                            self.start_codon_pos = self.start_codon_pos_org
                            # self.start_codon_valid = True
                        #'''

                if False: # b < 0:
                    if verbose: 
                        print('INFO in update_info (%i): %s start codon not covered. (Cov:%i, L:%i)' \
                          % (b, self.tid, int(100*self.cov/self.len), self.len))

            ## Update start/stop codon
            if (self.stop_codon_pos_org[0] > 0):
                # find exon that contains stop codon
                sc = region( self.chr, self.stop_codon_pos_org[0], self.stop_codon_pos_org[1], 'M')
                b = -1
                self.stop_codon_event = CODON_NOT_COVERED
                for e in exons.rgns:
                    if e.has_ext_intersection_with(sc):
                        # check code
                        loc = sc.start - e.start
                        if self.istrand > 0:
                            if (loc >= 0) & (loc <= (e.get_len()-3)):
                                seq = e.get_seq()
                                cdn = seq[loc:(loc+3)]
                                if (cdn == STOP_CODONS[0]) | (cdn == STOP_CODONS[1]) | (cdn == STOP_CODONS[2]):
                                    b = 0
                                    self.stop_codon_event = CODON_VALID
                                elif cdn.count('N') > 0:
                                    b = 3
                                    self.stop_codon_event = CODON_NOT_COVERED
                                else:
                                    b = 1
                                    self.stop_codon_event = CODON_WITH_VARIANT
                                    if len(self.tseq) > 0:
                                        scodon_org = self.tseq[self.pos_stop:(self.pos_stop+3)]
                                    else:
                                        scodon_org = '%s,%s,%s' % (STOP_CODONS[0],STOP_CODONS[1],STOP_CODONS[2])
                                    if verbose: print('   SNP detected in Stop codon of %s: %s -> %s' % (self.tid, scodon_org, seq[loc:(loc+3)]) )
                                    
                            elif (loc > (e.get_len()-3)) | (loc < 0):
                                b = 2
                                self.stop_codon_event = CODON_WITH_INDEL
                                # print('INDEL might happen')
                                # print('INFO in update_info: %s stop codon seems to be moved. (Cov:%i, L:%i)' % (self.tid, int(100*self.cov/self.len), self.len))

                        elif self.istrand < 0:
                            if (loc >= 0) & (loc <= (e.get_len()-3)):
                                seq = e.get_seq()
                                cdn = seq[loc:(loc+3)]
                                if (cdn == reverse_complement(STOP_CODONS[0])) | \
                                   (cdn == reverse_complement(STOP_CODONS[1])) | \
                                   (cdn == reverse_complement(STOP_CODONS[2])):
                                    b = 0
                                    self.stop_codon_event = CODON_VALID
                                elif cdn.count('N') > 0:
                                    self.stop_codon_event = CODON_NOT_COVERED
                                    b = 3
                                else:
                                    b = 1
                                    self.stop_codon_event = CODON_WITH_VARIANT
                                    if len(self.tseq) > 0:
                                        ps = len(self.tseq) - self.pos_stop - 3
                                        scodon_org = self.tseq[ps:(ps+3)]
                                    else:
                                        scodon_org = '%s,%s,%s' % (reverse_complement(STOP_CODONS[0]),reverse_complement(STOP_CODONS[1]),reverse_complement(STOP_CODONS[2]))
                                    if verbose: print('   SNP detected in Stop codon of %s: %s -> %s' % (self.tid, scodon_org, seq[loc:(loc+3)]) )
                            elif (loc > (e.get_len()-3)) | (loc < 0):
                                b = 2
                                if loc < 0: 
                                    self.stop_codon_event = CODON_WITH_INDEL
                                    if verbose: print('   INDEL detected in Stop codon of %s' % (self.tid) )
                                # print('INFO in update_info: %s stop codon seems to be moved. (Cov:%i, L:%i)' % (self.tid, int(100*self.cov/self.len), self.len))


                        if b == 0:
                            self.stop_codon_pos = self.stop_codon_pos_org
                            # self.stop_codon_valid = True
                       #'''

                if False: # b < 0:
                    if verbose: 
                        print('INFO in update_info (%i): %s stop codon not covered. (Cov:%i, L:%i)' \
                          % (b, self.tid, int(100*self.cov/self.len), self.len))
                
        ## Update CDS
        return
    
    def get_td_cov_ratio(self, exons, rgns, sel):
        
        Len = 0
        Cov = 0
        if sel == 0:
            for r in rgns.rgns:
                if (r.type != 'deletion') & (r.type != 'D'):
                    Len += len(r.seq)
                    Cov += r.cov_len
        else:
            for r in exons.rgns:
                if (r.type != 'deletion') & (r.type != 'D'):
                    Len += len(r.seq)
                    Cov += r.cov_len
        
        if Len == 0: 
            return 0
        else:
            return Cov/Len
        
        
    def get_td_cov(self, exons, rgns):
        
        tlen = self.tlen # exons.get_length()
        if tlen == 0:
            return 0
        
        if len(rgns.rgns) > 0:
            if self.cov_len >= 0:
                olen = self.cov_len
            else:
                olen = 0
                for m in self.tr_to_gr_map:
                    olen += rgns.rgns[m].get_cov_len()
                
            return olen/tlen
        else:
            olen = exons.count_valid_NT()
            if tlen == 0:
                print('ERROR %s: length 0' % self.tid)
                for m in self.tr_to_gr_map:
                    rgns.rgns[m].print_short()
                return 1
            else:
                return olen/tlen
                
    '''
    TR_exp_info = collections.namedtuple('TR_info', 'tid, tname, gid, gname, cov, abn, tpm')  
    '''

    def get_td_info(self):
        
        if (self.cov <= 0) | (len(self.tr_to_gr_map) == 0):
            cov = 0
        else:
            cov = round(self.cov, 3)

        abn = round(self.abn, 3)
        if abn < 0: abn = 0                                     
        
        ti = TR_exp_info(self.tid, self.tname, self.gid, self.gname, cov, abn, abn)
        return ti
    

    def check_if_start_stop_codon_is_covered(self, rgns, cds, target = 'start_codon'):
        
        b = False
        for c in cds.rgns: 
            if c.type.lower() == target:
                sc = c
                b = True
                break
        if b:
            b = False
            for r in rgns.rgns:
                if sc.get_overlap_len(r) > 0:
                    b = True
                    break
            if b:
                return True
            else: 
                return False
        else:
            return False
        
        
    def get_gtf_lines_from_exons(self, exons_rgns, rgns_rgns, cds_rgns, genome, sel, add_seq, connect = False):
        
        gtf_lines = []

        if (sel == 0) & (len(self.tr_to_gr_map) > 0):
            rgns = rgns_rgns
            tgm = self.tr_to_gr_map
            
        else:
            rgns = exons_rgns
            tgm = self.te_to_ge_map
            
        entries = regions()
        # seqs = []
        # cnt = 0
        if not connect:
            for k, m in enumerate(tgm):
                e = rgns[m]
                r = region(e.chr, e.start, e.end, e.type, xs = 1)
                if (e.type != 'deletion'): 
                    r.seq = e.seq
                    r.cov_len = e.cov_len

                r.cvg_frac = e.cvg_frac
                r.ave_cvg = e.ave_cvg
                entries.rgns.append( r )
        else:
            for k, m in enumerate(tgm):
                e = rgns[m]
                if k == 0:
                    r = region(e.chr, e.start, e.end, e.type, xs = 1)
                    if (e.type != 'deletion'): 
                        r.seq = e.seq
                        r.cov_len = e.cov_len

                    r.cvg_frac = e.cvg_frac
                    r.ave_cvg = e.ave_cvg
                    entries.rgns.append( r )
                else:
                    b = True
                    if entries.rgns[-1].end == (e.start-1):
                        if e.type.lower() == 'exon':
                            if entries.rgns[-1].type == 'exon':
                                entries.rgns[-1].end = e.end
                                entries.rgns[-1].seq = entries.rgns[-1].seq + e.seq
                                b = False
                    if b:
                        r = region(e.chr, e.start, e.end, e.type, xs = 1)
                        if (e.type != 'deletion'): 
                            r.seq = e.seq
                            r.cov_len = e.cov_len

                        r.cvg_frac = e.cvg_frac
                        r.ave_cvg = e.ave_cvg
                        entries.rgns.append( r )
                # cnt += 1
                    
        if (len(cds_rgns) > 0) & (len(self.aseq) > 0):
            tgm = self.tc_to_gc_map
            for m in tgm:
                e = cds_rgns[m]
                r = region(e.chr, e.start, e.end, e.type, xs = -1)
                entries.rgns.append( r )

        entries.order()
                
                
        attr_hdr = 'gene_id "%s"; gene_name "%s"; transcript_id "%s"; transcript_name "%s";' %\
                    (self.gid, self.gname, self.tid, self.tname)
        attr_tail = ' cvg "%3.1f"; abn "%3.1f";' % (self.cov, self.abn )
        attr = attr_hdr + attr_tail

        c = get_c_from_istrand(self.istrand)
        gtf_line = GTF_line(self.chr, GTF_SOURCE, 'transcript', self.begin, self.end, '0', c, '0', attr, \
                            self.gid, self.gname, self.tid, self.tname, self.biotype )
        gtf_lines.append(gtf_line)

        exon_cnt = 0
        for k, e in enumerate(entries.rgns):

            ## set attr
            if (e.type == 'deletion'):
                attr_tail = ' cvg "%f"; abn "%3.1f"; cfrac "%5.3f";' % (1, e.ave_cvg, e.cvg_frac)
            elif (e.type == 'insersion'):

                if len(e.seq) > 0:
                    cov = e.cov_len/len(e.seq) # get_cov()
                else:
                    cov = 0
                    
                if add_seq:
                    if cov == 0: seq = ''
                    else: seq = e.seq # get_seq()
                    attr_tail = ' exon_number "%i"; cvg "%f"; abn "%3.1f"; cfrac "%5.3f"; seq "%s";' % \
                                (exon_cnt, cov, e.ave_cvg, e.cvg_frac, seq )
                else:
                    attr_tail = ' exon_number "%i"; cvg "%f"; abn "%3.1f"; cfrac "%5.3f";' % \
                                (exon_cnt, cov, e.ave_cvg, e.cvg_frac )
                exon_cnt += 1
                
            elif (e.type == 'exon'):

                if len(e.seq) > 0:
                    cov = e.cov_len/len(e.seq) # get_cov()
                else:
                    cov = 0
                    
                if add_seq:
                    if cov == 0: seq = ''
                    else: seq = e.seq # get_seq()
                    attr_tail = ' exon_number "%i"; cvg "%f"; abn "%3.1f"; seq "%s";' % \
                                (exon_cnt, cov, e.ave_cvg, seq )
                else:
                    attr_tail = ' exon_number "%i"; cvg "%f"; abn "%3.1f";' % \
                                (exon_cnt, cov, e.ave_cvg )
                exon_cnt += 1
                
            else: # from cds
                attr_tail = ''
                if (e.type.lower() == 'start_codon'):
                    attr_tail = ' event "%i:%s"; status "%i:%s";' % (self.start_codon_event, \
                                Codon_Status[self.start_codon_event], self.start_codon_status, Codon_Status[self.start_codon_status])
                elif (e.type.lower() == 'stop_codon'):
                    attr_tail = ' event "%i:%s"; status "%i:%s";' % (self.stop_codon_event, \
                                Codon_Status[self.stop_codon_event], self.stop_codon_status, Codon_Status[self.stop_codon_status])

            attr = attr_hdr + attr_tail

            ## Set GTF line
            if e.start > 0:
                gl = GTF_line( e.chr, GTF_SOURCE, e.type, e.start, e.end, '1000', c, '.', attr, \
                               self.gid, self.tid, self.gname, self.tname, self.biotype )
                gtf_lines.append(gl)
            
        return gtf_lines

    
    def get_fasta_lines_from_exons(self, exons_rgns, rgns_rgns, cds_rgns, genome, sel, \
                                   peptide = False, L_th_t = MIN_TR_LENGTH, L_th_p = MIN_PR_LENGTH):

        prefix = 'X'
        if self.grp_size == 1: prefix = 'T'
        elif self.grp_size > 1: prefix = 'I'
        # c = get_c_from_istrand(self.istrand)
        # c_or_n = get_str_from_icdng( self.icds )
        
        seq, aseq = self.tseq, self.aseq # self.get_seq_from_exons(exons_rgns, rgns_rgns, cds_rgns, genome, sel, peptide)
        
        '''
        t = Transcript(prefix, self.tid, self.grp_size, self.icnt, self.chr, self.begin, self.end, \
                       self.istrand, c_or_n, '', self.abn, self.tpm, self.iso_frac, \
                       len(exons_rgns), len(seq)*self.abn, 1)

        tname = get_tr_name([t])[0]
        hdr = '>' + tname + '\n'
        '''
        # hdr = '>' + self.tid + ' length:%i abn:%f strand:%s %s\n' % (len(seq), np.round(self.abn, 2), c, c_or_n)
        hdr = set_fa_header( self.tid, len(seq), np.round(self.abn, 2), self.istrand, self.icds )
        hdr = '>' + hdr + '\n'
        hdr_p = set_fa_header( self.tid, len(aseq), np.round(self.abn, 2), self.istrand, self.icds )
        hdr_p = '>' + hdr_p + '\n'

        bt = False
        if len(seq) >= L_th_t: bt = True
        bp = False
        if len(aseq) >= L_th_p: bp = True

        if bt & bp:
            return [hdr, seq+'\n'], [hdr_p, aseq+'\n']
        elif (bt) & ( not bp):
            return [hdr, seq+'\n'], []
        elif (not bt) & (bp):
            return [], [hdr, aseq+'\n']
        else: 
            return [], []

        '''
        if len(seq) >= L_th_t:
            if len(aseq) >= L_th_p:
                if peptide:
                    return [hdr, seq+'\n'], [hdr, aseq+'\n']
                else:
                    return [hdr, seq+'\n'], []
            else:
                return [hdr, seq+'\n'], []
        else:
            return [],[]
        '''
        
    def update_info(self, exons_rgns, rgns_rgns, cds_rgns, genome, sel, peptide):
        
        seq, aseq, cds, be = self.get_seq_from_exons(exons_rgns, rgns_rgns, cds_rgns, genome, sel, peptide)
        return seq, aseq, cds, be
        
    
    def get_seq_from_exons(self, exons_rgns, rgns_rgns, cds_rgns, genome, sel, peptide):
        
        features_non_exon = ['cds', 'start_codon', 'stop_codon', 'CDS', 'START_CODON', 'STOP_CODON']
        
        seq = ''
        aseq = ''
        cds = regions()
        be = False
        lof = location_finder()
        
        if sel == 0:
            rgns = rgns_rgns
            tgm = self.tr_to_gr_map
            
        else:
            rgns = exons_rgns
            tgm = self.te_to_ge_map
        
        if len(rgns) == 0:
            return seq, aseq, cds, be
        
        if genome is None:
            for k, m in enumerate(tgm):
                e = rgns[m]
                if e.type != 'insersion': 
                    lof.add( e.start, e.end, len(seq))
                if (e.type != 'deletion') & (e.type != 'D'):
                    seq = seq + e.seq # get_seq()
            if sel == 0:
                if len(seq) > 0:
                    self.cov = self.cov_len/len(seq)
        else:
            if sel < 2:
                for k, m in enumerate(tgm):
                    e = rgns[m]
                    lof.add( e.start, e.end, len(seq))
                    if e.type == 'exon':
                        if (e.cov_len == len(e.seq)): # seq_cur.count('N') == 0:
                            seq = seq + e.seq
                        else:
                            chrm = e.chr
                            start = e.start -1
                            end = e.end
                            org_seq = genome[chrm].seq[start:end]

                            if e.cov_len <= 0:
                                seq = seq + org_seq
                            else:
                                sc = list(e.seq)
                                for i, ltr in enumerate(e.seq):
                                    if ltr == 'N':
                                        sc[i] = org_seq[i]
                                seq = seq + ''.join(sc)
                    elif (e.type == 'deletion') | (e.type == 'D'):
                        pass
                    elif (e.type == 'insersion') | (e.type == 'I'):
                        seq = seq + e.seq # get_seq()
                if sel == 0:
                    if len(seq) > 0:
                        self.cov = self.cov_len/len(seq)
            else:
                for k, m in enumerate(tgm):
                    e = rgns[m]
                    lof.add( e.start, e.end, len(seq))
                    if e.type == 'exon':
                        chrm = e.chr
                        start = e.start -1
                        end = e.end
                        seq = genome[chrm].seq[start:end]

        self.lof = lof
        self.tseq = seq

        # find peptide seq.
        be = False
        if (peptide): # & 
            if (self.icds > 0) | ((self.icds < 0) & (GEN_AAS_UNSPEC)):
            
                entries = regions()
                if (len(cds_rgns) > 0) & (len(self.tc_to_gc_map) > 0):
                    tgm = self.tc_to_gc_map
                    for m in tgm:
                        e = cds_rgns[m]
                        r = region(e.chr, e.start, e.end, e.type, xs = -1)
                        entries.rgns.append( r )

                if self.istrand == 0:
                    aseq1, pseq1, cds1, ast1, asp1, sts1, sps1, be1 = self.get_coding_seq(seq, lof, entries.rgns, 1, self.icds)
                    aseq2, pseq2, cds2, ast2, asp2, sts2, sps2, be2 = self.get_coding_seq(seq, lof, entries.rgns, -1, self.icds)
                    if len(aseq1) > len(aseq2):
                        aseq = aseq1
                        pseq = pseq1
                        cds = cds1
                        ast = ast1
                        asp = asp1
                        sts = sts1
                        sps = sps1
                        self.istrand = 1
                        be = be1
                    else:
                        aseq = aseq2
                        pseq = pseq2
                        cds = cds2
                        ast = ast2
                        asp = asp2
                        sts = sts2
                        sps = sps2
                        self.istrand = -1
                        be = be2
                else:
                    aseq, pseq, cds, ast, asp, sts, sps, be = self.get_coding_seq(seq, lof, entries.rgns, self.istrand, self.icds)
                    
                self.pseq = pseq
                self.aseq = aseq
                if ast >= 0: self.start_codon_pos = (ast, ast+2)
                if asp >= 0: self.stop_codon_pos = (asp, asp+2)
                self.start_codon_status = sts
                self.stop_codon_status = sps
                    
        return seq, aseq, cds, be


    '''
    CODON_NOT_SPECIFIED = -1
    CODON_VALID = 0
    CODON_NOT_COVERED = 1
    CODON_WITH_VARIANT = 2
    CODON_WITH_INDEL = 3
    CODON_RELOCATED = 4
    CODON_NOT_IDENTIFIED = 5
    CODON_POS_ESTIMATED = 6
    '''

    def get_coding_seq(self, seq, lof, cds_rgns, istrand, icds):
        
        aseq = ''
        start_codon_pos_org = -1
        stop_codon_pos_org = -1
        start_codon_pos = -1
        stop_codon_pos = -1
        
        start_codon_status = -1
        stop_codon_status = -1
        abs_start = -1
        abs_stop = -1
        
        # istrand = self.istrand

        ## check start/stop codon available
        if (len(cds_rgns) > 0) & (len(self.tc_to_gc_map) > 0):
            for m, c in enumerate(cds_rgns):
                if c.type.lower() == 'start_codon':
                    start_codon_pos = lof.rel_pos(c.start)
                    if (istrand < 0) & (start_codon_pos >= 0):
                        start_codon_pos = len(seq) - (start_codon_pos+3)
                    start_codon_pos_org = start_codon_pos    
                    
                if c.type.lower() == 'stop_codon':
                    stop_codon_pos = lof.rel_pos(c.start)
                    if (istrand < 0) & (stop_codon_pos >= 0):
                        stop_codon_pos = len(seq) - (stop_codon_pos+3)
                    stop_codon_pos_org = stop_codon_pos    

        ## find initial candidates
        startp, stopp, ss_lst = check_orf_condition(seq, strand = istrand)

        #'''
        if (start_codon_pos < 0) & (stop_codon_pos < 0):
            start_codon_pos = startp
            stop_codon_pos = stopp
            
            if icds > 0:
                if start_codon_pos >= 0: 
                    start_codon_status = CODON_RELOCATED
                else:
                    start_codon_status = CODON_NOT_IDENTIFIED
                if stop_codon_pos >= 0: 
                    stop_codon_event = CODON_RELOCATED
                else:
                    stop_codon_status = CODON_NOT_IDENTIFIED
            elif icds < 0:
                if start_codon_pos >= 0:
                    start_codon_status = CODON_POS_ESTIMATED
                else:
                    start_codon_status = CODON_NOT_IDENTIFIED
                if stop_codon_pos >= 0: 
                    stop_codon_status = CODON_POS_ESTIMATED
                else:
                    stop_codon_status = CODON_NOT_IDENTIFIED
            
        elif (start_codon_pos >= 0) & (stop_codon_pos >= 0): # & ((stop_codon_pos-start_codon_pos)%3 == 0):
            # pass
            #'''
            ## check if they are still there
            b_start = -1
            b_stop = -1
            for m, ss in enumerate(ss_lst):
                if (ss[0] >= 0) & (ss[1] >= 0):
                    if start_codon_pos >= 0:
                        if ss[0] == start_codon_pos:
                            stop_codon_pos = ss[1]
                            b_start = m
                            start_codon_status = CODON_VALID
                            break
                    
            ## may occurres when start codon is not covered or relocated
            if b_start < 0:
                for m, ss in enumerate(ss_lst):
                    if (ss[0] >= 0) & (ss[1] >= 0):
                        if stop_codon_pos >= 0:
                            if ss[1] == stop_codon_pos:
                                start_codon_pos = ss[0]
                                b_stop = m
                            break
            ## may occurres when both start and stop codon are not covered or relocated
            if b_stop < 0:
                if (startp >= 0):
                    if (stopp >= 0):
                        start_codon_pos = startp
                        stop_codon_pos = stopp
                    else:
                        start_codon_pos = startp
                        stop_codon_pos = len(seq) - (len(seq) - start_codon_pos)%3
                        
                elif (stopp >= 0):
                    start_codon_pos = stopp%3
                    stop_codon_pos = stopp
                else:
                    pass
                    ## Both start and stop codon was annotated in GTF/GFF
                    ## but they didn't appear in the reconstructed sequence
                    '''
                    print('ERROR: cannot find valid ORF (A) for %s (%i): %i,%i - %i,%i ' % \
                           (self.tid, istrand, b_start, start_codon_pos, b_stop, stop_codon_pos))
                    #'''
            
            #'''
        else: ## either start_codon_pos >= 0 or stop_codon_pos >= 0
            
            b_start = -1
            b_stop = -1
            if (start_codon_pos >= 0):
                for m, ss in enumerate(ss_lst):
                    if (ss[0] >= 0) & (ss[1] >= 0):
                        if start_codon_pos >= 0:
                            if ss[0] == start_codon_pos:
                                stop_codon_pos = ss[1]
                                b_start = m
                                break
            elif (stop_codon_pos >= 0):
                for m, ss in enumerate(ss_lst):
                    if (ss[0] >= 0) & (ss[1] >= 0):
                        if stop_codon_pos >= 0:
                            if ss[1] == stop_codon_pos:
                                start_codon_pos = ss[0]
                                b_stop = m
                            break
                            
            if (b_start < 0) & (b_stop < 0): 
                if (startp >= 0):
                    if (stopp >= 0):
                        start_codon_pos = startp
                        stop_codon_pos = stopp
                    else:
                        start_codon_pos = startp
                        stop_codon_pos = len(seq) - (len(seq) - start_codon_pos)%3
                        
                elif (stopp >= 0):
                    start_codon_pos = stopp%3
                    stop_codon_pos = stopp
                else:
                    pass
                    ## Either start or stop codon was annotated in GTF/GFF
                    ## but they didn't appear in the reconstructed sequence
                    '''
                    print('ERROR: cannot find valid ORF (B) for %s (%i): %i,%i - %i,%i ' % \
                           (self.tid, istrand, b_start, start_codon_pos, b_stop, stop_codon_pos))
                    #'''
                
        
        if (start_codon_pos < 0) & (stop_codon_pos >= 0):
            start_codon_pos = stop_codon_pos%3
            
        if (start_codon_pos >= 0) & (stop_codon_pos >= 0):
            if istrand > 0:
                pseq = seq[start_codon_pos:(stop_codon_pos)]
                aseq = translate(pseq)
                
                abs_start = lof.abs_pos(start_codon_pos)
                # start_codon_pos_abs = (abs_start, abs_start+2)
                abs_stop = lof.abs_pos(stop_codon_pos)
                # stop_codon_pos_abs = (abs_stop, abs_stop+2)
                
            elif istrand < 0:
                start = len(seq) - stop_codon_pos
                stop = len(seq) - start_codon_pos
                # pseq2 = reverse_complement(pseq)
                pseq = reverse_complement(seq[start:stop])
                aseq = translate(pseq)
                
                abs_start = lof.abs_pos(len(seq) - (start_codon_pos+3))
                # start_codon_pos = (abs_start, abs_start+2)
                
                abs_stop = lof.abs_pos(len(seq) - (stop_codon_pos+3))
                # stop_codon_pos = (abs_stop, abs_stop+2)
            
            
            cds_new, be = lof.get_cds_regions( start_codon_pos, stop_codon_pos, len(seq), self.chr, istrand)
            
            if start_codon_pos == start_codon_pos_org:
                cds_new.rgns.append( region(self.chr, abs_start, abs_start+2, 'start_codon') )
            else:
                cds_new.rgns.append( region(self.chr, abs_start, abs_start+2, 'start_codon') )
                # cds_new.rgns.append( region(self.chr, abs_start, abs_start+2, 'START_CODON') )
                
            if stop_codon_pos == stop_codon_pos_org:
                cds_new.rgns.append( region(self.chr, abs_stop, abs_stop+2, 'stop_codon') )
            else:
                cds_new.rgns.append( region(self.chr, abs_stop, abs_stop+2, 'stop_codon') )
                # cds_new.rgns.append( region(self.chr, abs_stop, abs_stop+2, 'STOP_CODON') )
                
            # print('+++ %s +++' % self.tid )
            # cds_new.print_short()
                
        else:
            be = False
            pseq = ''
            aseq = ''
            cds_new = regions()

        #'''
        return aseq, pseq, cds_new, abs_start, abs_stop, start_codon_status, stop_codon_status, be
        
        
    def get_seq_from_genome(self, exons, cds, genome):
        
        tseq = ''
        pseq = ''
        start_seq = ''
        stop_seq = ''
        start_codon_pos = -1
        start_codon_pos_org = -1
        stop_codon_pos = -1
        stop_codon_pos_org = -1
        
        if cds is not None:
            for k, e in enumerate(cds.rgns):
                chrm = e.chr
                start = e.start -1
                end = e.end
                seq = genome[chrm].seq[start:end]

                if (e.type == 'CDS'):
                    pseq = pseq + seq

                elif (e.type == 'start_codon'):
                    start_seq = seq
                    start_codon_pos_org = e.start

                elif (e.type == 'stop_codon'):
                    stop_seq = seq
                    stop_codon_pos_org = e.start
                
        start_codon_ind = False
        pos_lst_all = []
        for k, e in enumerate(exons.rgns):
            chrm = e.chr
            start = e.start -1
            end = e.end
            seq = genome[chrm].seq[start:end]
            
            if (e.type == 'exon'):
                if (start_codon_pos_org >= e.start) & (start_codon_pos_org <= e.end):
                    start_codon_pos = len(tseq) + start_codon_pos_org - e.start
                if (stop_codon_pos_org >= e.start) & (stop_codon_pos_org <= e.end):
                    stop_codon_pos = len(tseq) + stop_codon_pos_org - e.start
                tseq = tseq + seq
                
        if self.istrand < 0:
            tseq = reverse_complement(tseq)
            if cds is not None:
                pseq = reverse_complement(pseq)
                start_seq = reverse_complement(start_seq)
                stop_seq = reverse_complement(stop_seq)
                if start_codon_pos_org >= 0:
                    start_codon_pos = len(tseq) - start_codon_pos -3
                if stop_codon_pos_org >= 0:
                    stop_codon_pos = len(tseq) - stop_codon_pos -3
                
        return self.icds, self.istrand, tseq, pseq, start_seq, stop_seq, \
                    start_codon_pos_org, start_codon_pos, stop_codon_pos_org, stop_codon_pos

            
    def get_span(self):
        
        span = region(self.chr, self.begin, self.end, 'M')
        return span
    
    def print_short(self):
        
        c_or_n = get_str_coding_status(self.icds)
        ss = get_c_from_istrand( self.istrand )
        
        print('%s, %s, (%s, %s)' % (self.id, self.name, c_or_n, ss) )
        print('TLen: %i, PLen: %i (%4.1f)' % (len(self.tseq), len(self.pseq), len(self.pseq)/3) )

    '''
    Transcript = collections.namedtuple('Transcript', \
                                    'prefix, gidx, grp_size, icnt, chr, start, end, \
                                     strand, cdng, seq, abn, tpm, iso_frac, prob, nexs, gvol')
    '''
    def set(self, rgns, tr_info, verbose = False):
 
        # self.gtf_lines = gtf_lines_of_a_tr        
        self.chr = tr_info.chr
        self.begin = tr_info.start      
        self.end = tr_info.end        
        
        self.gid = 'SFIX.%i' % (tr_info.gidx) 
        self.gname = 'SFIX.%i' % (tr_info.gidx)
        self.tid = 'SFIX.%i.%i' % (tr_info.gidx, tr_info.icnt)
        self.tname = 'SFIX.%i.%i' % (tr_info.gidx, tr_info.icnt)
        self.istrand = tr_info.strand
        self.icds = get_icdng_from_str( tr_info.cdng )       ## -1: unspecified, 0: non-coding, 1: coding
        
        ## used in td_and_ae
        # self.te_to_ge_map = []
        # self.tc_to_gc_map = []
        # self.tr_to_gr_map = []
        self.abn = tr_info.abn
        self.cov = 1
        self.tlen = len(tr_info.seq)
        # self.plen = -1
        
        # self.cov_len = 0
        # self.cov_ratio = 0

        ## Temporary variables
        self.prefix = tr_info.prefix
        self.gvol = tr_info.gvol
        self.prob = tr_info.prob
        self.nexons = tr_info.nexs
        # self.len_os = -1
        # self.pos_start = -1  ## 0-base
        # self.pos_stop = -1   ## 0-base
        
        ## Tr info
        self.tpm = tr_info.tpm
        self.icnt = tr_info.icnt
        self.grp_size = tr_info.grp_size
        self.iso_frac = tr_info.iso_frac

        ## Codon pos and status
        # self.start_codon_pos_org = (-1,-1)
        # self.stop_codon_pos_org = (-1,-1)
        
        # self.start_codon_event = -1
        # self.stop_codon_event = -1
        
        # self.start_codon_pos = (-1,-1)
        # self.stop_codon_pos = (-1,-1)

        # self.start_codon_status = -1
        # self.stop_codon_status = -1
        
        ## filled with get_seq_from_exons()
        # self.lof = None
        self.tseq = tr_info.seq
        # self.pseq = ''
        # self.aseq = ''
        

        
##################
## Gene descriptor
##################

def sort_descriptor_lst(d_lst, ref = 'chr'):
    
    if ref == 'chr':
        chrs = []
        for d in d_lst:
            chrs.append(d.chr)

        chr_set = list(set(chrs))
        chr_set.sort()
        chrs = np.array(chrs)

        d_lst_new = []
        for c in chr_set:
            wh = which(chrs == c)
            ps = np.array( [d_lst[w].begin for w in wh] )
            odr2 = ps.argsort()
            for o in odr2:
                w = wh[o]
                d_lst_new.append(d_lst[w])
    else:
        pos_lst = np.zeros(len(d_lst))
        for k, d in enumerate(d_lst):
            pos_lst[k] = d.begin
        odr = pos_lst.argsort()
        d_lst_new = []
        for k in odr:
            d_lst_new.append(d_lst[k])
        
    return d_lst_new

'''
class splice_graph:
    
    def __init__(self, read_len, cnt = 0):
        
        self.read_len = read_len
        self.gcnt = cnt
        
        self.n_nodes = 0
        self.nodes = regions()
        self.graph_fwd = {}
        self.graph_bwd = {}
        self.n_paths = 0
        self.path_lst = []

        self.n_edges = 0
        self.edges = regions_nd()
        self.graph_f = {}
        self.graph_b = {}
        self.n_p = 0
        self.p_lst = []
        self.s_lst = []
        self.c_lst = []
        self.cov_lst = []
        self.strand = 0
        
        self.cvgs = None
        self.lens = None
        self.abn = None
        
        self.y = None
        self.H = None
        self.z = None
        self.G = None
        
        ## Only FYI
        self.nodes_min = []
        self.n_nodes_min = 0
        self.n_edges_min = 0
        self.graph_f_min = {}
        self.graph_b_min = {}
        self.n_p_min = 0
        self.p_lst_min = []
        
        self.cvgs_min = None
        self.lens_min = None
        
        self.z_min = None
        self.G_min = None
                
        self.n_p_detected = 0
        self.p_lst_detected = []
        self.n_p_candidate = 0
        self.p_lst_candidate = []

        self.bistranded = False
        self.np_in = self.n_p
        self.np_out = self.n_p

SNV_info = collections.namedtuple('SNV_info', 'chr, pos_ref, pos_new, gene_id, gene_name, v_type, v_len, cvg_depth, cvg_frac, \
                                   ref_prev, ref_seq, ref_next, alt_prev, alt_seq, alt_next') # one-base
        
'''

'''
v_class: 
 '3_prime_UTR',
 '5_prime_UTR',
 'Frame_Shift_Del',
 'Frame_Shift_Ins',
 'In_Frame_Del',
 'In_Frame_Ins',
 'Missense_Mutation',
 'Nonsense_Mutation', # SNP -> stop earlier
 'Nonstop_Mutation',  # SNP -> stop later
 'Silent',
 'Start_Codon_Del',
 'Start_Codon_Ins',
 'Start_Codon_SNP',
 'Stop_Codon_Del',
 'Stop_Codon_Ins'

 '5_prime_Flank',
 'Splice_Site',
 'Intron',
 'De_novo_Start_OutOfFrame',
 'IGR',
'''

def sort_gtf_lines(gtf_lines):

    pos_lst = []
    for gtfl in gtf_lines:
        pos_lst.append(gtfl.start)
    pos_lst = np.array(pos_lst)
    odr = pos_lst.argsort()
    gtf_lines_sorted = []
    for o in odr:
        gtf_lines_sorted.append(gtf_lines[o])
    return gtf_lines_sorted


NV_info_ext = collections.namedtuple('NV_info_ext', 'chr, pos_ref, pos_new, gene_id, gene_name, v_type, v_len, cvg_depth, cvg_frac, \
                                      ref_prev, ref_seq, ref_next, alt_prev, alt_seq, alt_next, v_class, v_class_tr') # one-base

class gene_descriptor:

    def init(self, grp, verbose = False):

        self.gcnt = grp.gcnt
        self.read_len = grp.read_len
        
        '''
        self.icds = icds
        self.chr = ''
        self.begin = -1
        self.end = -1

        self.exons = regions()
        self.cds = regions()
        self.rgns = regions()
        
        self.ntr = 0
        self.td_lst = []
        self.te_to_ge_maps = []
        self.tc_to_gc_maps = []
        self.tr_to_gr_maps = []
        self.tr_info = []
        self.nv_info_lst = []
        
        self.t_abn = -1
        self.r_tpm = -1
        '''
        
        # set chr, begin, end
        for node in grp.nodes.rgns:
            if self.begin < 0: self.begin = node.start
            else: self.begin = min( node.start, self.begin )
            if self.end < 0: self.end = node.end
            else: self.end = max( node.end, self.end )
            if self.chr == '': self.chr = node.chr

        return


    def add_tr(self, nodes, edges, p_lst, tr_info_lst, verbose = False):

        n_p = len(p_lst)
        n_nodes = len(nodes.rgns)

        if n_p != len(tr_info_lst):
            print('%i != %i' % (n_p, len(tr_info_lst)))
        
        # set chr, begin, end
        for node in nodes.rgns:
            if self.begin < 0: self.begin = node.start
            else: self.begin = min( node.start, self.begin )
            if self.end < 0: self.end = node.end
            else: self.end = max( node.end, self.end )
            if self.chr == '': self.chr = node.chr

        for k in range(n_p):
            self.te_to_ge_maps.append([])
            self.tc_to_gc_maps.append([])
            self.tr_to_gr_maps.append([])

        for k in range(n_p):

            if n_p != len(tr_info_lst): print('k = %i' % k)
        
            path = p_lst[k]
            rgns = regions()
            rgns2 = regions_nd()
            flag = 0
            for n in path:
                if n < n_nodes:
                    rgns.rgns.append(nodes.rgns[n].copy(update = True))
                else:
                    e = n - n_nodes
                    rgns2.rgns.append(edges.rgns[e].copy(update = True))
                    if edges.rgns[e].type == 'D':
                        rgns.rgns.append(edges.rgns[e].copy(update = True))

            td = transcript_descriptor()
            td.set( rgns, tr_info_lst[k] )
            self.td_lst.append(td)
                        
            self.add_tr_rgns(self.ntr+k, rgns)
            self.td_lst[self.ntr+k].cov_len = rgns.count_valid_NT() # get_cov()
                    
        self.ntr += n_p
        
        return


    def check_nv_pos( self, nv_span ):
        res = 0
        b = True
        for m, cr in enumerate(self.cds.rgns):
            if cr.has_ext_intersection_with( nv_span ):
                if cr.type.lower() == 'start_codon':
                    res = 1
                    b = False
                    break
                elif cr.type.lower() == 'stop_codon':
                    res = 2
                    b = False
                    break

        if b:
            for m, cr in enumerate(self.cds.rgns):
                if cr.has_ext_intersection_with( nv_span ):
                    if cr.type.lower() == 'cds':
                        res = 3
                        b = False
                        break
                    
        if b:
            for m, cr in enumerate(self.cds.rgns):
                if cr.has_ext_intersection_with( nv_span ):
                    res = cr.type
                    b = False
                    break
                
        if b:
            gid = 'not_identified'
            gname = 'not_identified'
        else:
            g_ids = []
            g_names = []
            for k, tgm in enumerate(self.tc_to_gc_maps):
                #if len(self.td_lst[k].aseq) > 0:
                if m in tgm:
                    if self.td_lst[k].gid not in g_ids:
                        g_ids.append(self.td_lst[k].gid)
                        g_names.append(self.td_lst[k].gname)

            if len(g_ids) == 0:
                gid, gname = '', ''
            else:
                gid = g_ids[0]
                if len(g_ids) > 1:
                    for a in g_ids[1:]:
                        gid = gid + ';%s' % a

                gname = g_names[0]
                if len(g_names) > 1:
                    for a in g_names[1:]:
                        gname = gname + ';%s' % a
                    
        return res, gid, gname

    def check_nv_pos_exon( self, nv_span ):
        b = True
        res = ''
        for m, cr in enumerate(self.rgns.rgns):
            if cr.has_ext_intersection_with( nv_span ):
                res = cr.type
                b = False
                break
                
        if b:
            gid = 'not_identified_2'
            gname = 'not_identified_2'
        else:
            g_ids = []
            g_names = []
            for k, tgm in enumerate(self.tr_to_gr_maps):
                if m in tgm:
                    if self.td_lst[k].gid not in g_ids:
                        g_ids.append(self.td_lst[k].gid)
                        g_names.append(self.td_lst[k].gname)
            
            if len(g_ids) == 0:
                gid, gname = '', ''
            else:
                gid = g_ids[0]
                if len(g_ids) > 1:
                    for a in g_ids[1:]:
                        gid = gid + ';%s' % a

                gname = g_names[0]
                if len(g_names) > 1:
                    for a in g_names[1:]:
                        gname = gname + ';%s' % a
                    
        return res, gid, gname
    

    def get_gene_level_nv_info(self, cnt_e):
                   
        nv_info_lst = []
        if (len(self.nv_info_lst) > 0):
            
            g_ids = []
            g_names = []
            for k, td in enumerate(self.td_lst):
                if td.gid not in g_ids:
                    g_ids.append(td.gid)
                if td.gname not in g_names:
                    g_names.append(td.gname)
    
            gid = g_ids[0]
            if len(g_ids) > 1:
                for a in g_ids[1:]:
                    gid = gid + ';%s' % a

            gname = g_names[0]
            if len(g_names) > 1:
                for a in g_names[1:]:
                    gname = gname + ';%s' % a
                    
            if (len(self.cds.rgns) > 0): 

                for nv in self.nv_info_lst:
                    v_cls = 'not_classified'
                    span = region( nv.chr, nv.pos_ref, nv.pos_ref + nv.v_len-1, 'M' )
                    
                    res, gid, gname = self.check_nv_pos( span )

                    if isinstance(res,str) == True:

                        if nv.v_type == 'I':  
                            v_cls = 'ins_in_' + res
                        elif nv.v_type == 'D':  
                            v_cls = 'del_in_' + res
                        else:  
                            v_cls = 'np_in_' + res
                    else:
                        if res == 1:
                            if nv.v_type == 'V':  
                                v_cls = 'start_codon_snp'
                            elif nv.v_type == 'I':  
                                v_cls = 'start_codon_ins'
                            elif nv.v_type == 'D':  
                                v_cls = 'start_codon_del'
                            else:
                                pass                    
                        elif res == 2:
                            if nv.v_type == 'V':  
                                v_cls = 'stop_codon_snp'
                            elif nv.v_type == 'I':  
                                v_cls = 'stop_codon_ins'
                            elif nv.v_type == 'D':  
                                v_cls = 'stop_codon_del'
                            else:
                                pass                    
                        elif res == 3:
                            if nv.v_type == 'V':  
                                v_cls = 'missense_or_silent_mutation'
                            elif nv.v_type == 'I':  
                                if nv.v_len%3 == 0:
                                    v_cls = 'in_frame_ins'
                                else:
                                    v_cls = 'frame_shift_ins'
                            elif nv.v_type == 'D':  
                                if nv.v_len%3 == 0:
                                    v_cls = 'in_frame_del'
                                else:
                                    v_cls = 'frame_shift_del'
                            else:
                                pass                    
                        elif res == 0:
                            res, gid, gname = self.check_nv_pos_exon( span )
                            if len(res) == 0:
                                v_cls = 'not_identified'
                            else:
                                res = res + '(utr)'
                                if nv.v_type == 'I':  
                                    v_cls = 'ins_in_' + res
                                elif nv.v_type == 'D':  
                                    v_cls = 'del_in_' + res
                                else:  
                                    v_cls = 'np_in_' + res
                                
                        else:
                            if nv.v_type == 'I':  
                                v_cls = 'ins_in_' + res
                            elif nv.v_type == 'D':  
                                v_cls = 'del_in_' + res
                            else:  
                                v_cls = 'np_in_' + res

                    nv_info_lst.append( NV_info_ext(nv.chr, nv.pos_ref, nv.pos_new, gid, gname, nv.v_type, nv.v_len, nv.cvg_depth, \
                                          nv.cvg_frac, nv.ref_prev, nv.ref_seq, nv.ref_next, nv.alt_prev, nv.alt_seq, nv.alt_next, v_cls, 'NA') )
                    
            else:
                cnt = 0
                for td in self.td_lst:
                    if cnt == 0:
                        icds = td.icds
                        if td.icds > 0:
                            v_cls = 'CDS_unknown'
                        elif td.icds == 0:
                            v_cls = 'none_coding_gene'
                        else:
                            v_cls = 'CDS_unspecified'
                    else:
                        if icds != td.icds:
                            v_cls = 'CDS_unknown'
                            break
                    cnt += 1
                            
                for nv in self.nv_info_lst:
                    nv_info_lst.append( NV_info_ext(nv.chr, nv.pos_ref, nv.pos_new, nv.gene_id, nv.gene_name, nv.v_type, nv.v_len, nv.cvg_depth, \
                                          nv.cvg_frac, nv.ref_prev, nv.ref_seq, nv.ref_next, nv.alt_prev, nv.alt_seq, nv.alt_next, v_cls, 'NA') )

        nv_info_tr_lst = []
        if len(nv_info_lst) > 0:
            # self.nv_info_lst = nv_info_lst
            proc = np.full( len(nv_info_lst), False )

            ## Find mutations in coding region
            # cnt_e = 0
            for k, td in enumerate(self.td_lst):
                # td.tc_to_gc_map = self.tc_to_gc_maps[k]
                nv_info_tr, processed, cnt_e = td.get_cds_nv_info( nv_info_lst, self.cds.rgns, cnt_e )
                proc = proc | processed
                nv_info_tr_lst = nv_info_tr_lst + nv_info_tr

            if len(self.cds.rgns) == 0: # self.icds <= 0: # if Non-coding or Unspecified
                for k, nv in enumerate(nv_info_lst):
                    if not proc[k]:
                        nv_info = NV_info_ext_tr(nv.chr, nv.pos_ref, nv.pos_new, nv.gene_id, nv.gene_name, nv.v_type, \
                                                 nv.v_len, nv.cvg_depth, nv.cvg_frac, nv.ref_prev, nv.ref_seq, nv.ref_next, \
                                                 nv.alt_prev, nv.alt_seq, nv.alt_next, nv.v_class, \
                                                 nv.v_class, '', '', '', '', '') #, '' )
                                                 # '', get_str_from_icdng(self.icds), '', '', '', '', '' )
                        nv_info_tr_lst.append(nv_info)
            
            self.nv_info_lst = nv_info_tr_lst
                
        return nv_info_tr_lst, cnt_e

    '''
    SNV_info = collections.namedtuple('SNV_info', 'chr, pos_ref, pos_new, gene_id, gene_name, v_type, v_len, cvg_depth, cvg_frac, \
                                   ref_prev, ref_seq, ref_next, alt_prev, alt_seq, alt_next') # one-base
    '''
    def find_snp_from_rgns(self):
        
        snv_info_lst = []
        gin = ('NA', 'NA')

        for r in self.rgns.rgns:
            
            if (r.type == 'I') | (r.type == 'insersion'):
                sop = '-'
                soc = '-'
                son = '-'
                snp = '-'
                snc = r.seq
                snn = '-'
                si = SNV_info(r.chr, r.start, r.start, gin[0], gin[1], 'I', r.get_len(), \
                              np.round(r.ave_cvg_depth(),3), np.round(r.cvg_frac,3), sop, soc, son, snp, snc, snn )
                snv_info_lst.append(si)
            elif (r.type == 'D') | (r.type == 'deletion'):
                sop = '-'
                soc = '-'
                son = '-'
                snp = '-'
                snc = '-'
                snn = '-'
                si = SNV_info(r.chr, r.start, r.start, gin[0], gin[1], 'D', r.get_len(), \
                              np.round(r.ave_cvg_depth(),3), np.round(r.cvg_frac,3), sop, soc, son, snp, snc, snn )
                snv_info_lst.append(si)

        self.nv_info_lst = snv_info_lst
        return(snv_info_lst)


    def get_gid_n_gname_list(self):

        g_id_n_name = []
        gname = []

        for m, r in enumerate(self.exons.rgns):
            b = False
            for j in range(self.ntr):
                if m in self.te_to_ge_maps[j]:
                    b = True
                    g_id_n_name.append((self.td_lst[j].gid, self.td_lst[j].gname))
                    break
            if not b:
                g_id_n_name.append(('', ''))
                # print('ERROR in gene_descriptor::get_gid_n_gname_list ')
        return g_id_n_name
                    

    def set_cov_n_abn_th(self, Cov_th, Abn_th):
        self.cov_th = Cov_th
        self.abn_th = Abn_th
        

    def __init__(self, gtf_lines_of_a_gene = None, genome = None, icds = -1, fill = False, \
                 gcnt = 0, verbose = False, Cov_th = MIN_COV_TO_SEL, Abn_th = MIN_ABN_TO_SEL, read_len = 100):

        # self.gtf_lines = gtf_lines_of_a_gene  
        self.gtf = True
        if gtf_lines_of_a_gene is None: self.gtf = False
      
        self.gcnt = gcnt
        self.read_len = read_len
        
        # self.icds = icds
        self.chr = ''
        self.begin = -1
        self.end = -1
        self.exons = regions()
        self.cds = regions()
        self.rgns = regions()
        
        self.ntr = 0
        self.td_lst = []
        self.te_to_ge_maps = []
        self.tc_to_gc_maps = []
        self.tr_to_gr_maps = []
        self.tr_info = []
        self.nv_info_lst = []
        
        self.t_abn = -1
        self.r_tpm = -1

        self.cov_th = Cov_th
        self.abn_th = Abn_th

        if gtf_lines_of_a_gene is not None:

            self.begin = min(get_col(gtf_lines_of_a_gene, GSTART))
            self.end = max(get_col(gtf_lines_of_a_gene, GEND))
            
            chrs = get_col(gtf_lines_of_a_gene, CHR)
            chrs = list(set(chrs))
            if len(chrs) > 1:
                print('   WARNING in gene_descriptor::init: spans over %i chromosomes.' % len(chrs) )

            self.chr = chrs[0]
                    
            tr_gtf_lst = parse_gtf_lines_and_split_into_genes( gtf_lines_of_a_gene, 'transcript' )
            n_valid_trs = 0
            for k, gls_org in enumerate(tr_gtf_lst):
                
                gls = sort_gtf_lines(gls_org)
                
                td = transcript_descriptor(gls, self.exons.rgns, self.cds.rgns, genome, icds, fill)
                self.td_lst.append(td)
                self.te_to_ge_maps.append(td.te_to_ge_map)
                self.tc_to_gc_maps.append(td.tc_to_gc_map)
                if len(td.te_to_ge_map) > 0: n_valid_trs += 1
               
            if True: # not fill:
                exons = self.exons.copy(update = fill)

                N = len(exons.rgns)*2
                n_loop = 0
                # while True:
                for n in range(N):
                    elen = np.zeros(len(exons.rgns)) 
                    for k, e in enumerate(exons.rgns): elen[k] = e.start
                    odr = elen.argsort()
                    cnt_o = 0
                    to_del = []
                    for k in range(len(odr)):
                        if k < (len(odr)-1):
                            ep = exons.rgns[odr[k]]
                            for m in range(k+1,len(odr)):
                                en = exons.rgns[odr[m]]
                                if ep.type == en.type: # (ep.type == 'exon') & (en.type == 'exon'):
                                    if ep.has_ext_intersection_with(en):

                                        istart, iend = ep.get_intersection(en)

                                        if ep.start < istart:
                                            if ep.end == en.end:
                                                ep.end = istart-1
                                                Len = ep.end - ep.start + 1
                                                if len(ep.seq) > 0: ep.seq = ep.seq[:Len]
                                                if ep.cmat is not None: 
                                                    ep.cmat = ep.cmat[:,:Len]
                                                    ep.get_cvg()
                                                cnt_o += 1

                                            elif ep.end > en.end:
                                                e1 = region(ep.chr, iend+1, ep.end, ep.type)
                                                Len = e1.end - e1.start + 1
                                                if len(ep.seq) > 0: e1.seq = ep.seq[-Len:]
                                                if ep.cmat is not None: 
                                                    e1.cmat = ep.cmat[:,-Len:]
                                                    e1.get_cvg()
                                                exons.rgns.append(e1)

                                                ep.end = istart-1
                                                Len = ep.end - ep.start + 1
                                                if len(ep.seq) > 0: ep.seq = ep.seq[:Len]
                                                if ep.cmat is not None: 
                                                    ep.cmat = ep.cmat[:,:Len]
                                                    ep.get_cvg()
                                                cnt_o += 1

                                            elif ep.end < en.end:
                                                e1 = region(en.chr, iend+1, en.end, en.type)
                                                Len = e1.end - e1.start + 1
                                                if len(en.seq) > 0: e1.seq = en.seq[-Len:]
                                                if en.cmat is not None: 
                                                    e1.cmat = en.cmat[:,-Len:]
                                                    e1.get_cvg()
                                                exons.rgns.append(e1)

                                                if iend != ep.end: print('ERROR: %i, %i, %i ' % (ep.end, iend, en.end))
                                                en.end = iend
                                                Len = en.end - en.start + 1
                                                if len(en.seq) > 0: en.seq = en.seq[:Len]
                                                if en.cmat is not None: 
                                                    en.cmat = en.cmat[:,:Len]
                                                    en.get_cvg()

                                                ep.end = istart-1
                                                Len = ep.end - ep.start + 1
                                                if len(ep.seq) > 0: ep.seq = ep.seq[:Len]
                                                if ep.cmat is not None: 
                                                    ep.cmat = ep.cmat[:,:Len]
                                                    ep.get_cvg()
                                                cnt_o += 1

                                        elif ep.start == istart:
                                            if ep.end < en.end:
                                                en.start = ep.end+1
                                                Len = en.end - en.start + 1
                                                if len(en.seq) > 0: en.seq = en.seq[-Len:]
                                                if en.cmat is not None: 
                                                    en.cmat = en.cmat[:,-Len:]
                                                    en.get_cvg()
                                                cnt_o += 1
                     
                                            elif ep.end == en.end:
                                                # print('ERROR A: %i: %i,%i == %i: %i, %i in %i ' % (k, ep.start, ep.end, m, en.start, en.end, n_loop) )
                                                to_del.append(odr[m])
                                                cnt_o += 1
                                            elif ep.end > en.end:
                                                ep.start = en.end+1
                                                Len = ep.end - ep.start + 1
                                                if len(ep.seq) > 0: ep.seq = ep.seq[-Len:]
                                                if ep.cmat is not None: 
                                                    ep.cmat = ep.cmat[:,-Len:]
                                                    ep.get_cvg()
                                                cnt_o += 1

                                        else:
                                            print('ERROR B: %i > %i ' % (ep.start, istart) )

                                        if cnt_o > 0: break

                        if cnt_o > 0: break

                    if len(to_del) > 0:
                        to_del.sort()
                        for k in reversed(to_del): del exons.rgns[k]

                    if cnt_o == 0: break
                    n_loop += 1

                exons.update()
                '''
                if len(exons.rgns) > len(self.exons.rgns):
                    print('Exon correction: %i -> %i in %i' % (len(self.exons.rgns), len(exons.rgns), n_loop))
                '''
                for k, td in enumerate(self.td_lst):
                    tgm = self.te_to_ge_maps[k]
                    tgm_new = []
                    for m in tgm:
                        oe = self.exons.rgns[m]
                        for i, ne in enumerate(exons.rgns):
                            ne = exons.rgns[i]
                            if oe.has_ext_intersection_with(ne): 
                                tgm_new.append(i)
                                if oe.end == ne.end: break

                    self.te_to_ge_maps[k] = copy.deepcopy(tgm_new)
                    td.te_to_ge_map = copy.deepcopy(self.te_to_ge_maps[k])

                self.exons = exons.copy(update = fill)

            #'''
            ## reorder exons and cds
            for k, td in enumerate(self.td_lst):
                tgm = copy.deepcopy(self.te_to_ge_maps[k])
                if len(tgm) > 0:
                    pos = np.zeros(len(tgm))
                    for m in range(len(tgm)): pos[m] = self.exons.rgns[tgm[m]].start
                    odr = pos.argsort()
                    self.te_to_ge_maps[k] = [ tgm[m] for m in odr ]
                    td.te_to_ge_map = copy.deepcopy(self.te_to_ge_maps[k])
            
            for k, td in enumerate(self.td_lst):
                tgm = copy.deepcopy(self.tc_to_gc_maps[k])
                if len(tgm) > 0:
                    pos = np.zeros(len(tgm))
                    for m in range(len(tgm)): pos[m] = self.cds.rgns[tgm[m]].start
                    odr = pos.argsort()
                    self.tc_to_gc_maps[k] = [ tgm[m] for m in odr ]
                    td.tc_to_gc_map = copy.deepcopy(self.tc_to_gc_maps[k])
            #'''
               
            self.ntr = len(self.te_to_ge_maps)
            self.tr_to_gr_maps = [[] for k in range(self.ntr)]

            if self.ntr > n_valid_trs:
                print('WARNING: Ntrs %i > Nvalid %i' % (self.ntr, n_valid_trs))
                # print_gtf_lines(gtf_lines_of_a_gene)
                for td in self.td_lst:
                    if len(td.te_to_ge_map) == 0:
                        print_gtf_lines(td.gtf_lines)
                print('-----------------------')
                print_gtf_lines(gtf_lines_of_a_gene)
                print('=======================')

            '''
            self.rgns = self.exons.copy(update = False)
            for k, td in enumerate(self.td_lst):
                self.tr_to_gr_maps[k] = copy.deepcopy(self.te_to_ge_maps[k])
                td.tr_to_gr_map = self.tr_to_gr_maps[k]
            '''
                
            self.get_span()

        
    def add_tr_rgns(self, ki, rgns):
        
        tr_to_gr_map = []
        for k, r in enumerate(rgns.rgns):
            b = True
            for m,s in enumerate(self.rgns.rgns):
                if r.is_the_same_as(s):
                    tr_to_gr_map.append(m)
                    b = False
                    break
            if b: 
                m = len(self.rgns.rgns)
                tr_to_gr_map.append(m)
                self.rgns.rgns.append( r )
                
        self.td_lst[ki].tr_to_gr_map = tr_to_gr_map
        self.tr_to_gr_maps[ki] = copy.deepcopy( tr_to_gr_map )
        
        
    def get_td_exp_info(self):

        ti_lst = []
        for td in self.td_lst:
            ti = td.get_td_info()
            ti_lst.append(ti)
        return ti_lst
    

    def get_span(self):
        
        if len(self.te_to_ge_maps) > 0:
            cnt = 0
            for m in range(len(self.exons.rgns)):
                if cnt == 0:
                    if len(self.te_to_ge_maps[m]) > 0:
                        s = self.exons.rgns[m].start
                        e = self.exons.rgns[m].end
                        cnt += 1
                else:
                    s = min(s, self.exons.rgns[m].start)
                    e = max(e, self.exons.rgns[m].end)
            if cnt == 0:
                self.span = region(self.chr, 0, 0, 'M')
                return self.span
            else:
                self.span = region(self.chr, s, e, 'M')
                return self.span    
            
            for m, td in enumerate(self.td_lst):
                if len(self.te_to_ge_maps[m]):
                    cnt = 0
                    for i in self.te_to_ge_maps[m]:
                        if cnt == 0:
                            s = self.exons.rgns[i].start
                            e = self.exons.rgns[i].end
                        else:
                            s = min(s, self.exons.rgns[i].start)
                            e = max(e, self.exons.rgns[i].end)
                        cnt += 1
                    td.begin = s
                    td.end = e
                else:
                    td.begin = -1
                    td.end = -1
                
        else:
            self.span = region(self.chr, 0, 0, 'M')
            return self.span

        
    def get_td_span(self,n):
        if n < len(self.te_to_ge_maps):
            tgm = self.te_to_ge_maps[n]
            if len(tgm) > 0:
                cnt = 0
                for m in tgm:
                    if cnt == 0:
                        s = self.exons.rgns[m].start
                        e = self.exons.rgns[m].end
                        cnt += 1
                    else:
                        s = min(s, self.exons.rgns[m].start)
                        e = max(e, self.exons.rgns[m].end)
                if cnt == 0:
                    return region(self.chr, 0, 0, 'M')
                else:
                    return region(self.chr, s, e, 'M')    
            else:
                return region(self.chr, 0, 0, 'M')    
        else:
            return region(self.chr, 0, 0, 'M')

        
    def merge(self, gd):

        if (len(gd.exons.rgns) > 0) & (gd.ntr > 0):
            
            ## merge exons
            imap_e = {k: -1 for k in range(len(gd.exons.rgns))}

            ne = len(self.exons.rgns)
            new_cnt = 0
            for k, r in enumerate(gd.exons.rgns):
                imap_e[k] = ne + new_cnt
                for m, g in enumerate(self.exons.rgns):
                    if r.is_the_same_as(g):
                        imap_e[k] = m
                        break
                if imap_e[k] == (ne + new_cnt): 
                    new_cnt += 1
                    self.exons.rgns.append(r)

            ## merge cdss
            imap_c = {k: -1 for k in range(len(gd.cds.rgns))}

            nc = len(self.cds.rgns)
            new_cnt = 0
            for k, r in enumerate(gd.cds.rgns):
                imap_c[k] = nc + new_cnt
                for m, g in enumerate(self.cds.rgns):
                    if r.is_the_same_as(g):
                        imap_c[k] = m
                        break
                if imap_c[k] == (nc + new_cnt): 
                    new_cnt += 1
                    self.cds.rgns.append(r)

            for k, tgm_e in enumerate(gd.te_to_ge_maps):
                tgm_new_e = []
                for m in range(len(tgm_e)): tgm_new_e.append(imap_e[tgm_e[m]])

                tgm_c = gd.tc_to_gc_maps[k]
                tgm_new_c = []
                for m in range(len(tgm_c)): tgm_new_c.append(imap_c[tgm_c[m]])

                self.te_to_ge_maps.append(tgm_new_e)
                self.tc_to_gc_maps.append(tgm_new_c)
                gd.td_lst[k].te_to_ge_map = copy.deepcopy(tgm_new_e)
                gd.td_lst[k].tc_to_gc_map = copy.deepcopy(tgm_new_c)
                self.td_lst.append(gd.td_lst[k])

            ###
            self.ntr = len(self.te_to_ge_maps)
            self.tr_to_gr_maps = [[] for k in range(self.ntr)]

            n_chr_diff = 0
            for k, td in enumerate(gd.td_lst):
                if self.chr != gd.chr: n_chr_diff += 1

            if n_chr_diff > 0:
                print('ERROR in gene_descriptor::merge: multiple chrm detected in a chunk (%i)' % n_chr_diff)

    '''
    def order(self):
        
        sps = np.zeros(self.ntr)
        for n in range(self.ntr):
            span = self.get_td_span(n)
            sps[n] = span.start
            
        odr = sps.argsort()
        self.te_to_ge_maps = [self.te_to_ge_maps[k] for k in odr]
        self.tr_to_gr_maps = [self.tr_to_gr_maps[k] for k in odr]
        self.tc_to_gc_maps = [self.tc_to_gc_maps[k] for k in odr]
        
        self.td_lst = sort_descriptor_lst(self.td_lst, ref = 'pos')
        return
    '''

    def get_tids(self):
        tids = []
        for td in self.td_lst:
            tids.append(td.tid)
        return tids
        
    def get_total_abn( self ):
        
        t_abn = 0
        for td in self.td_lst: 
            if td.abn > 0: t_abn += td.abn
        return t_abn
    
    def set_tr_info( self, nf ):
        
        if len(self.td_lst) > 0:
            # nf = 1000000/t_abn
            tids = []
            for td in self.td_lst: 
                if td.abn >= 0: 
                    td.tpm = td.abn*nf
                    tids.append(td.tid)
                
            tids_unique = list(set(tids))
            if (len(tids_unique) == 1):
                if (tids_unique[0] == ''):
                    tids = []
                    for td in self.td_lst: 
                        if td.abn >= 0: 
                            tids.append(td.tname)
                
            tids = np.array(tids)
            for tid in tids_unique:
                wh = which( tids == tid )
                tpm_sum = 0
                for w in wh:
                    if self.td_lst[w].abn >= 0: tpm_sum += self.td_lst[w].tpm
                        
                if tpm_sum == 0: tpm_sum = 1
                for m, w in enumerate(wh):
                    if self.td_lst[w].abn >= 0: 
                        self.td_lst[w].iso_frac = self.td_lst[w].tpm/tpm_sum
                        self.td_lst[w].grp_size = len(wh)
                        self.td_lst[w].icnt = m
                
    
    def remove_indel_and_combine_frags(self):
        
        ## remove 'deletion' and
        ## rename 'insersion' to 'exon'
        for k in reversed(range(len(self.exons.rgns))):
            r = self.exons.rgns[k]
            if r.type == 'deletion':
                del self.exons.rgns[k]
                for m, tgm in enumerate(self.te_to_ge_maps):
                    if k in tgm:
                        tgm.remove(k)
                    tgm = np.array(tgm)
                    tgm[tgm > k] -= 1
                    self.te_to_ge_maps[m] = list(tgm)
            elif r.type == 'insersion':
                self.exons.rgns[k].type = 'exon' # 'EXON'
                
        ## optionally combine fragments
        
        return
    
    def update(self):
        
        for r in self.rgns.rgns:
            r.get_cvg()
            r.get_cov_len()
        
                
    '''
    Transcript = collections.namedtuple('Transcript', \
                                        'prefix, gidx, grp_size, icnt, chr, start, end, \
                                         strand, cdng, seq, abn, tpm, iso_frac, prob, nexs, gvol')

    def get_transcript_tuple(self):
        return Transcript(self.prefix, self.gid, self.grp_size, self.icnt, self.chr, self.begin, self.end, \
                          get_c_from_istrand(self.istrand), get_str_from_icdng(self.icds), self.tseq, \
                          self.abn, self.tpm, self.iso_frac, self.prob, self.nexons, self.gvol)

    '''
    def update_td_info(self, genome = None, sel = 0, peptide = False):

        if len(self.td_lst) > 0:
            
            gvol = 0
            if sel == 0: 
                self.rgns.set_cvg()
                fm = {'M': 'exon', 'I': 'insersion', 'D': 'deletion'}
                for r in self.rgns.rgns:
                    if r.type in fm.keys():
                        r.type = fm[r.type]
                tgms = self.tr_to_gr_maps

                for r in self.rgns.rgns:
                    gvol += np.sum(r.cvg)
                
            else: 
                if genome is None: self.exons.set_cvg()
                tgms = self.te_to_ge_maps
                    
            tc_to_gc_maps_new = [[] for k in range(self.ntr)]
            cds_new = regions()
            
            cnt_t = 0
            cnt_p = 0
            cnt_e = 0

            for k, td in enumerate(self.td_lst):
                if len(tgms[k]) > 0:  
                    
                    td.tr_to_gr_map = copy.deepcopy(self.tr_to_gr_maps[k])
                    td.te_to_ge_map = copy.deepcopy(self.te_to_ge_maps[k])
                    td.tc_to_gc_map = copy.deepcopy(self.tc_to_gc_maps[k])
                    
                    if len(td.te_to_ge_map) > 0:
                        tseq, aseq, cds, be = td.update_info(self.exons.rgns, self.rgns.rgns, self.cds.rgns, \
                                                    genome, sel = sel, peptide = peptide)
                    else:
                        tseq, aseq, cds, be = td.update_info(self.exons.rgns, self.rgns.rgns, self.cds.rgns, \
                                                    genome, sel = sel, peptide = peptide)

                    if td.prefix == 'X':
                        if self.ntr == 1:  td.prefix = 'T'
                        elif self.ntr > 1:  td.prefix = 'I'
                    if td.icnt < 0: td.icnt = k
                    if td.gvol <= 0: td.gvol = gvol
                    if td.grp_size <= 0: td.grp_size = self.ntr
                    if td.prob <= 0: td.prob = 1
                    if td.nexons <= 0: 
                        if sel == 0:
                            td.nexons = len(self.tr_to_gr_maps[k])
                        else:
                            td.nexons = len(self.te_to_ge_maps[k])
                    
                    if be: cnt_e += 1
                    if len(tseq) > 0: cnt_t += 1
                    if len(aseq) > 0: cnt_p += 1
                    

                    if ((sel > 0) & peptide): # | ((sel == 0) & (len(td.te_to_ge_map) == 0)):
                        if len(aseq) > 0:
                            for r in cds.rgns:
                                b = True
                                for m, c in enumerate(cds_new.rgns):
                                    if r.is_the_same_as(c):
                                        b = False
                                        tc_to_gc_maps_new[k].append(m)
                                        break
                                if b:
                                    m = len(cds_new.rgns)
                                    tc_to_gc_maps_new[k].append(m)
                                    cds_new.rgns.append(r)

                            td.tc_to_gc_map = tc_to_gc_maps_new[k]

            if ((sel > 0) & peptide): # | ((sel == 0) & (len(td.te_to_ge_map) == 0)):
                self.cds = cds_new
                self.tc_to_gc_maps = tc_to_gc_maps_new
                self.get_span()

            return cnt_t, cnt_p, cnt_e
        else:
            print('update_td_info: no transcripts')
            return 0, 0, 0
        
                                     
    def get_gtf_lines_from_exons(self, genome = None, sel = 0, add_seq = True, connect = False):
        
        line_lst = []
        cnt_none = 0
        if len(self.td_lst) > 0:
            
            fm = {'M': 'exon', 'I': 'insersion', 'D': 'deletion'}
            for r in self.rgns.rgns:
                if r.type in fm.keys():
                    r.type = fm[r.type]
                    
            if sel < 2:

                if sel == 0: tgm = self.tr_to_gr_maps
                else: tgm = self.te_to_ge_maps

                if (self.cov_th == 0): cov_th = -2
                else: cov_th = self.cov_th
                if (self.abn_th == 0): abn_th = -1
                else: abn_th = self.abn_th

                for k, td in enumerate(self.td_lst):
                    if (len(tgm[k]) > 0) & (td.cov >= cov_th): # & (td.abn >= abn_th):  
                        
                        td.tr_to_gr_map = copy.deepcopy(self.tr_to_gr_maps[k])
                        td.te_to_ge_map = copy.deepcopy(self.te_to_ge_maps[k])
                        td.tc_to_gc_map = copy.deepcopy(self.tc_to_gc_maps[k])
                        
                        if not self.gtf: # len(td.te_to_ge_map) == 0:
                            gls = td.get_gtf_lines_from_exons(self.exons.rgns, self.rgns.rgns, self.cds.rgns, \
                                                              genome, sel = sel, add_seq = add_seq, connect = connect)
                            if len(gls) <= 1:
                                cnt_none += 1
                                # print('ERROR in gd.get_gtf_lines_from_exons: Len(GTF lines) == %i L(%i,%i)' \
                                #        % (len(gls), len(td.te_to_ge_map), len(td.tr_to_gr_map)) )
                            else:
                                if TR_FILTER_SEL == 1:
                                    b = self.check_tr_1(td, frag_len = self.read_len, g_th = MIN_N_RDS_PER_GENE, abn_th_t = MIN_ABN_TO_SEL, \
                                                               abn_th_i = MIN_ABN_TO_SEL, iso_frac_th = MIN_ISO_FRAC, len_th = MIN_TR_LENGTH )
                                else:
                                    b = self.check_tr_2(td, frag_len = self.read_len, g_th = MIN_N_RDS_PER_GENE, abn_th_t = MIN_ABN_TO_SEL, \
                                                               abn_th_i = MIN_ABN_TO_SEL, iso_frac_th = MIN_ISO_FRAC, len_th = MIN_TR_LENGTH )
                                if b:
                                    line_lst = line_lst + gls
                                else:
                                    cnt_none += 1
                        else:
                            gls = td.get_gtf_lines_from_exons(self.exons.rgns, self.rgns.rgns, self.cds.rgns, \
                                                              genome, sel = sel, add_seq = add_seq, connect = connect)
                            if len(gls) <= 1:
                                cnt_none += 1
                                # print('ERROR in gd.get_gtf_lines_from_exons: Len(GTF lines) == %i L(%i,%i)' \
                                #        % (len(gls), len(td.te_to_ge_map), len(td.tr_to_gr_map)) )
                            else:
                                line_lst = line_lst + gls
                             
                    else:
                        '''
                        print('Exception (%i): Cov: %4.2f, %4.2f, %i, Lerc: %i, %i, %i - %i, %i, %i ' % (sel, cov_th, td.cov, td.cov_len, \
                                 len(self.te_to_ge_maps[k]), len(self.tr_to_gr_maps[k]), len(self.tc_to_gc_maps[k]), \
                                 len(self.exons.rgns), len(self.rgns.rgns), len(self.cds.rgns)) )
                        #'''
                        cnt_none += 1
                        pass

            else:
                for k, td in enumerate(self.td_lst):
                    if (len(self.te_to_ge_maps[k]) > 0): 
                        
                        td.tr_to_gr_map = copy.deepcopy(self.tr_to_gr_maps[k])
                        td.te_to_ge_map = copy.deepcopy(self.te_to_ge_maps[k])
                        td.tc_to_gc_map = copy.deepcopy(self.tc_to_gc_maps[k])
                        
                        gls = td.get_gtf_lines_from_exons(self.exons.rgns, self.rgns.rgns, self.cds.rgns, \
                                                          genome, sel = sel, add_seq = add_seq, \
                                                          connect = connect)
                        line_lst = line_lst + gls

            '''
            self.get_span()
            if (self.span.start > 0) & (self.span.end > 0):

                self.begin = self.span.start
                self.end = self.span.end

                attr_hdr = 'gene_id "%s"; gene_name "%s";' % (self.td_lst[0].gid, self.td_lst[0].gname)
                attr_tail = '' # ' cov "%3.1f"; abn "%3.1f";' % (self.cov, self.abn )
                attr = attr_hdr + attr_tail

                c = get_c_from_istrand(self.td_lst[0].istrand)
                gtf_line_hdr = GTF_line(self.chr, GTF_SOURCE, 'gene', self.span.start, self.span.end, '0', c, '0', attr, \
                                    self.td_lst[0].gid, self.td_lst[0].gname, '', '' )
                line_lst = [gtf_line_hdr] + line_lst
            #'''    
                
        return line_lst, cnt_none
            
                
    def get_fasta_lines_from_exons(self, genome = None, sel = 0, peptide = False, \
                                   L_th_t = MIN_TR_LENGTH, L_th_p = MIN_PR_LENGTH): 
        
        line_lst = []
        line_lst2 = []
        if len(self.td_lst) > 0:
            
            if sel == 0: self.rgns.set_cvg()
            else:
                if genome is None: self.exons.set_cvg()
            
            if sel < 2:

                if sel == 0: tgm = self.tr_to_gr_maps
                else: tgm = self.te_to_ge_maps

                if (self.cov_th == 0): cov_th = -1
                else: cov_th = self.cov_th
                if (self.abn_th == 0): abn_th = -1
                else: abn_th = self.abn_th

                cnt  = 0
                for k, td in enumerate(self.td_lst):
                    if (td.cov >= cov_th) & (len(tgm[k]) > 0) & (td.abn >= abn_th):  

                        td.tr_to_gr_map = copy.deepcopy(self.tr_to_gr_maps[k])
                        td.te_to_ge_map = copy.deepcopy(self.te_to_ge_maps[k])
                        td.tc_to_gc_map = copy.deepcopy(self.tc_to_gc_maps[k])
                        
                        if not self.gtf: # (len(td.te_to_ge_map) == 0:
                            fa_seq, fa_aseq = \
                                td.get_fasta_lines_from_exons(self.exons.rgns, self.rgns.rgns, self.cds.rgns, \
                                                              genome, sel, peptide, L_th_t = L_th_t, L_th_p = L_th_p)

                            if TR_FILTER_SEL == 1:
                                b = self.check_tr_1(td, frag_len = self.read_len, g_th = MIN_N_RDS_PER_GENE, abn_th_t = MIN_ABN_TO_SEL, \
                                                           abn_th_i = MIN_ABN_TO_SEL, iso_frac_th = MIN_ISO_FRAC, len_th = L_th_t )
                            else:
                                b = self.check_tr_2(td, frag_len = self.read_len, g_th = MIN_N_RDS_PER_GENE, abn_th_t = MIN_ABN_TO_SEL, \
                                                           abn_th_i = MIN_ABN_TO_SEL, iso_frac_th = MIN_ISO_FRAC, len_th = L_th_t )

                            if b:
                                line_lst = line_lst + fa_seq
                                line_lst2 = line_lst2 + fa_aseq
                        else:
                            fa_seq, fa_aseq = \
                                td.get_fasta_lines_from_exons(self.exons.rgns, self.rgns.rgns, self.cds.rgns, \
                                                              genome, sel, peptide, L_th_t = L_th_t, L_th_p = L_th_p)

                            line_lst = line_lst + fa_seq
                            line_lst2 = line_lst2 + fa_aseq
                    else:
                        # print('Abn th: %5.3f, Abn: %5.2f ' % (abn_th, td.abn))
                        cnt += 1
                
                # if cnt > 0: print('ERROR in get_fasta_lines_from_exons (A): %i ' % (cnt))

            else:
                for k, td in enumerate(self.td_lst):
                    
                    td.tr_to_gr_map = copy.deepcopy(self.tr_to_gr_maps[k])
                    td.te_to_ge_map = copy.deepcopy(self.te_to_ge_maps[k])
                    td.tc_to_gc_map = copy.deepcopy(self.tc_to_gc_maps[k])
                    
                    fa_seq, fa_aseq = \
                        td.get_fasta_lines_from_exons(self.exons.rgns, self.rgns.rgns, self.cds.rgns, \
                                                      genome, sel, peptide, L_th_t = L_th_t, L_th_p = L_th_p)
                    line_lst = line_lst + fa_seq
                    line_lst2 = line_lst2 + fa_aseq
                
        return line_lst, line_lst2
            

    def check_tr_1(self, tr, frag_len = 80, g_th = 10, abn_th_t = 1, abn_th_i = 1, iso_frac_th = 0.01, len_th = 200 ):

        b = False
        if tr.prefix == 'T':
            if tr.nexons <= 1:
                if (tr.gvol >= g_th*frag_len*1) & (tr.abn >= abn_th_t*4.5) & (len(tr.tseq) >= len_th):
                    b = True
            else:
                if (tr.nexons >= 4):
                    if (tr.gvol >= g_th*frag_len) & (tr.abn >= abn_th_t) & (len(tr.tseq) >= len_th): 
                        b = True
                else:
                    if (tr.gvol >= g_th*frag_len) & (tr.abn >= abn_th_t) & (len(tr.tseq) >= len_th): 
                        b = True
        else:
             if (tr.gvol >= g_th*frag_len) & (tr.abn >= abn_th_i) & (tr.iso_frac >= iso_frac_th) & (len(tr.tseq) >= len_th): 
                b = True
                    
        return b

                    
    def check_tr_2(self, tr, frag_len = 80, g_th = 10, abn_th_t = 1, abn_th_i = 1, iso_frac_th = 0.01, len_th = 200, ne_th = 4 ):

        b = False
        g_th = g_th * abn_th_i
        ref_th = ne_th*g_th*frag_len*abn_th_i
        met = min(tr.grp_size, 4)*min(tr.nexons,4)*min(tr.gvol, 400)
        thr = ref_th/met
        r = 1
        # if thr > 1: r = 1.5
        if tr.nexons == 1: thr *= 4
        if (tr.gvol > g_th*frag_len*thr) & (tr.abn >= abn_th_i*thr) & (tr.iso_frac >= iso_frac_th) & (len(tr.tseq) >= len_th*r): 
            if tr.prefix == 'T': 
                b = True
            else: 
                b = True
                
        return b

                    
    def get_seq_from_genome(self, n, genome):

        if self.chr in genome.keys():
            tgm = self.te_to_ge_maps
            rgns = self.exons

            td = self.td_lst[n]

            exons_tmp = regions()
            for m in tgm[k]: 
                exons_tmp.rgns.append(rgns.rgns[m])

            cds_tmp = None
            if len(self.cds.rgns) > 0:
                tgr = td.tc_to_gc_map
                cds_tmp = regions()
                for m in tgr:
                    cds_tmp.rgns.append(self.cds.rgns[m])
                    
            icds, istrand, ts, ps, start_s, stop_s, start_p_org, start_p, stop_p_org, stop_p = \
                        self.td_lst[n].get_seq_from_genome(exons_tmp, cds_tmp, genome)
            return icds, istrand, ts, ps, start_s, stop_s, start_p_org, start_p, stop_p_org, stop_p
        else:
            return -1, 0, '', '', '', '', -1, -1, -1, -1
    
        
        
    def compare_seqs(self, s1, s2, tid, verbose = False):
        
        if (len(s1) > 0) & (len(s2) > 0):
            if len(s1) != len(s2):
                e = []
                er_cnt = 0
                for k in range(min(len(s1), len(s2))):
                    if s1[k] == s2[k]:
                        e.append('_')
                    else:
                        e.append(s2[k])
                        er_cnt += 1
                if (verbose) & (er_cnt > 0):
                    eseq = ''.join(e)
                    print('====' + tid + '==== %i, %i' % (len(s1), len(s2)))
                    print(s1)
                    print(s2)
                    # print(eseq)

                return er_cnt

            else:
                e = []
                er_cnt = 0
                for k, c in enumerate(s1):
                    if c == s2[k]:
                        e.append('_')
                    else:
                        e.append(s2[k])
                        er_cnt += 1
                if (verbose) & (er_cnt > 0):
                    eseq = ''.join(e)
                    print('----' + tid + '---- %i, %i' % (len(s1), len(s2)))
                    print(s1)
                    print(s2)
                    # print(eseq)

                return er_cnt
        else:
            return 0
    

    def print_cds_info(self, chr_seq):
        
        print('=== %s:%i-%i ===' %(self.chr, self.begin, self.end))
        self.cds.print_short()
        print('--------------------------')
        for r in self.cds.rgns:
            seq = chr_seq[(r.start-1):r.end]
            if len(seq) > 100: seq = seq[:100]
            print(seq)
        print('--------------------------')
        print(self.tc_to_gc_maps)
        print('--------------------------')
        for td in self.td_lst:
            print('%s: %i - %i' % (td.tid, td.begin, td.end))
        print('--------------------------')

        
    def compare_seqs_from_cds_and_genome(self, chr_seq):

        n_er_total, n_total = 0, 0
        
        tgme = self.te_to_ge_maps
        tgmc = self.tc_to_gc_maps

        for k, td in enumerate(self.td_lst):
            if len(tgme[k]) > 0:
                tid = td.tid
                seq = ''
                for m in tgme[k]: 
                    if self.exons.rgns[m].type == 'exon':
                        seq = seq + chr_seq[(self.exons.rgns[m].start-1):self.exons.rgns[m].end]
                if len(seq) == 0:
                    print('ERROR(T): %s of len(%i) not detected' % (tid, len(td.tseq)))
                tseq = seq

            if len(tgmc[k]) > 0:
                tid = td.tid
                seq = ''
                cds_tmp = regions()
                for m in tgmc[k]: 
                    cds_tmp.rgns.append(self.cds.rgns[m])
                    if self.cds.rgns[m].type == 'CDS':
                        seq = seq + chr_seq[(self.cds.rgns[m].start-1):self.cds.rgns[m].end]
                if len(seq) > 0:
                    pseq = seq
                    if td.istrand < 0:
                        pseq = reverse_complement(seq)
                    aseq = translate(pseq)
                    n_er = self.compare_seqs( td.aseq, aseq, tid, verbose = False )

                    n_er_total += n_er
                    n_total += len(aseq)

                else:
                    print('ERROR(P): %s of len(%i) not detected' % (tid, len(td.aseq)))
                    
        # if n_er_total > 0: self.print_cds_info(chr_seq)

        return n_er_total, n_total
    

    def get_all_seq_from_genome(self, genome, abn_th = 0, cov_th = 0, len_th_t = 200, len_th_p = 50):

        tids = []
        tseq = []
        abnt = []

        pids = []
        pseq = []
        abnp = []

        if self.chr in genome.keys():
            
            tgms = self.te_to_ge_maps
            rgns = self.exons.rgns
            target = 'exon'

            for k, td in enumerate(self.td_lst):
                if len(tgms[k]) > 0:
                    tid = td.tid
                    rgns_tmp = regions()
                    for m in tgms[k]: 
                        if rgns[m].type == target:
                            rgns_tmp.rgns.append(rgns[m].copy(update = False))
                    rgns_tmp.order()

                    seq = ''
                    for r in rgns_tmp.rgns: 
                        seq = seq + genome[r.chr].seq[(r.start-1):r.end]
                    if (len(seq) >= len_th_t) & (td.abn >= abn_th) & (td.cov >= cov_th):
                        hdr = set_fa_header( tid, len(seq), np.round(td.abn, 2), td.istrand, td.icds )
                        tid = hdr
                        # tid = tid + ' length:%i strand:%s %s' % (len(seq), get_c_from_istrand(td.istrand), get_str_from_icdng( td.icds ))
                        if td.istrand < 0:
                            seq = reverse_complement(seq)
                        tids.append(tid)
                        tseq.append(seq)
                        abnt.append(td.abn)

            tgms = self.tc_to_gc_maps
            rgns = self.cds.rgns
            target = 'CDS'

            for k, td in enumerate(self.td_lst):
                if len(tgms[k]) > 0:
                    tid = td.tid

                    rgns_tmp = regions()
                    for m in tgms[k]: 
                        if rgns[m].type == target:
                            rgns_tmp.rgns.append(rgns[m].copy(update = False))
                    rgns_tmp.order()

                    seq = ''
                    for r in rgns_tmp.rgns: 
                        seq = seq + genome[r.chr].seq[(r.start-1):r.end]

                    if (len(seq) >= len_th_t) & (td.abn >= abn_th) & (td.cov >= cov_th):
                        # tid = tid + ' length:%i strand:%s %s' % (len(seq), get_c_from_istrand(td.istrand), get_str_from_icdng( td.icds ))
                        if td.istrand >= 0:
                            aseq = translate(seq)
                            if len(aseq) >= len_th_p:
                                tid = set_fa_header( tid, len(aseq), np.round(td.abn, 2), td.istrand, td.icds )
                                pids.append(tid)
                                pseq.append(aseq)
                                abnp.append(td.abn)
                        if td.istrand <= 0:
                            aseq = reverse_complement(seq)
                            aseq = translate(aseq)
                            if len(aseq) >= len_th_p:
                                tid = set_fa_header( tid, len(aseq), np.round(td.abn, 2), td.istrand, td.icds )
                                pids.append(tid)
                                pseq.append(aseq)
                                abnp.append(td.abn)
                        
        return tids, tseq, abnt, pids, pseq, abnp



    def get_fasta_lines_from_genome(self, genome, abn_th = 0, cov_th = 0, len_th_t = 200, len_th_p = 50):

        tids, tseq, abnt, pids, pseq, abnp = self.get_all_seq_from_genome(genome, abn_th, cov_th, len_th_t, len_th_p)

        fasta_lines_t = []
        for k, tid in enumerate(tids):
            fasta_lines_t.append( '>%s\n' % tid )
            fasta_lines_t.append( '%s\n' % tseq[k] )

        fasta_lines_p = []
        for k, tid in enumerate(pids):
            fasta_lines_p.append( '>%s\n' % tid )
            fasta_lines_p.append( '%s\n' % pseq[k] )
            
        return fasta_lines_t, fasta_lines_p
            
        
    def print_exon(self):
        
        self.exons.print_short()
        

##########################################################################
## Functions to initialize GD/TD from GTF
##########################################################################

def select_coding_genes_from_gtf_file(gtf_file):

    fns = gtf_file.split('.')[:-1]
    fname = ''
    for k, fn in enumerate(fns):
        if k > 0:
            fname = fname + '.'
        fname = fname + fn
    
    gtf_lines, hdr_lines = load_gtf(gtf_file, verbose = True)
    
    base_cds = get_base_cds_from_gtf_lines(gtf_lines)
    if base_cds < 0:
        print('INFO: No coding information available in the GTF/GFF.')
    
    gtf_lines_lst = parse_gtf_lines_and_split_into_genes( gtf_lines )

    gtf_lines_lst_new = []
    ccnt = 0
    gcnt = 0
    for k, lines in enumerate(gtf_lines_lst):
        b = False
        cnt = [0,0]
        for gtfline in lines:
            if gtfline.feature == 'start_codon':
                cnt[0] += 1
            if gtfline.feature == 'stop_codon':
                cnt[1] += 1
            if (cnt[0] > 0) & (cnt[1] > 0):
                b = True
                ccnt += 1
                break
        gcnt += 1
        if k%100 == 0: print('\rparsing .. %i/%i (%i/%i)' % (k, len(gtf_lines_lst), ccnt, gcnt), end='', flush = True )
        if b: gtf_lines_lst_new = gtf_lines_lst_new + lines

    fname = fname + '_cds.gtf'
    save_gtf( fname, gtf_lines_lst_new, hdr_lines )
    
    return fname
    


def combine_genes_per_chr( gd_lst, verbose = False ):
    
    g_lst = {k: [] for k in range(len(gd_lst))}
    ng = len(gd_lst)

    start_time1 = time.time()
    #'''
    
    n_gd = len(gd_lst)
    s_pos = np.zeros(n_gd)
    e_pos = np.zeros(n_gd)
    e_max = np.zeros(n_gd)
    end_max = 0
    for k, gd in enumerate(gd_lst): 
        s_pos[k] = gd.begin
        e_pos[k] = gd.end
        
    odr = s_pos.argsort()
    
    for kk in range(len(gd_lst)): 
        k = odr[kk]
        end_max = max(end_max, e_pos[k])
        e_max[k] = end_max
        
    #'''
    for kk in range(1,n_gd):
        if verbose:
            if kk%100 == 0:
                print('\rCombining genes %i/%i' % (kk,n_gd), end='    ' )
                
        k = odr[kk]
        
        if s_pos[k] > e_max[odr[kk-1]]:
            pass
        else:
            for mm in reversed(range(kk)):
                m = odr[mm]
                if s_pos[k] > e_max[m]: break
                if (gd_lst[k].chr == gd_lst[m].chr):
                    if (s_pos[k] < e_pos[m]):
                        if gd_lst[m].exons.has_ext_intersection_with(gd_lst[k].exons):
                            g_lst[k].append(m)
                            g_lst[m].append(k)
                
    elapsed_time1 = time.time() - start_time1
    if verbose: print('\rCombining genes %i ... done. %i(s) ' % (n_gd,elapsed_time1) )
    #'''

    '''
    kk = 0
    mm = kk+1
    k = odr[kk]
    m = odr[mm]
    
    while True:
        if e_pos[k] < s_pos[m]:
            if mm < kk: mm = kk + 1
            else: kk = mm + 1
            k = odr[kk]
            m = odr[mm]
            
        elif e_pos[m] < s_pos[k]:
            if mm < kk: mm = kk + 1
            else: kk = mm + 1
            k = odr[kk]
            m = odr[mm]
        else:
            if (gd_lst[k].chr == gd_lst[m].chr):
                if gd_lst[m].exons.has_ext_intersection_with(gd_lst[k].exons):
                    g_lst[k].append(m)
                    g_lst[m].append(k)

            if mm < kk: mm = kk + 1
            else: kk = mm + 1
            k = odr[kk]
            m = odr[mm]
            
        if verbose:
            if kk%100 == 0:
                print('\rCombining genes %i/%i' % (kk,n_gd), end='    ' )
                                
    elapsed_time1 = time.time() - start_time1
    if verbose: print('\rCombining genes %i ... done. %i(s) ' % (n_gd,elapsed_time1) )
    #'''

        
    
    bpg = np.ones(len(gd_lst))

    comb_lst = []
    for k in g_lst.keys():
        if (len(g_lst[k]) > 0):
            if (bpg[k] > 0): 
                gis = set(g_lst[k])
                n_prev = len(gis)
                cnt = 0
                while True:
                    for i in gis:
                        gis = gis.union( set(g_lst[i]) )
                        
                    if (len(gis) == n_prev): break
                    else: n_prev = len(gis)
                    cnt += 1
                        
                gis = list(set(list(gis) + [k]))
                for m in gis: bpg[m] = 0
                comb_lst.append((gis))

    if len(comb_lst) > 0:
        cnt = 0
        to_del_g = []
        for cl in comb_lst:
            
            if len(cl) > 1:
                cnt += len(cl)-1
                k = cl[0]
                for gi in cl[1:]:
                    gd_lst[k].merge(gd_lst[gi])
                    to_del_g.append(gi)

        if len(to_del_g) > 0:
            to_del_g = list(set(to_del_g))
            to_del_g.sort(reverse=True)
            for gi in to_del_g:
                del gd_lst[gi]
        # print(' %i -> %i' % (ng, len(gd_lst)) )
        del g_lst
        del comb_lst
    else:
        pass
        # print(' ')

    return gd_lst
#'''

def get_gene_descriptor(gtf_lines, genome = None, fill = False, cg = True, \
                        verbose = False, n_cores = 1):

    base_cds = get_base_cds_from_gtf_lines(gtf_lines)
    if base_cds < 0:
        print('   No coding information available in the GTF/GFF.')
    
    gtf_lines_lst = parse_gtf_lines_and_split_into_genes( gtf_lines )
    gd_lst = []
    tcnt = 0
    tcnt2 = 0
    gcnt = 0
    chrs = []    
    
    start_time1 = time.time()
    if True: # > 1:
        for k,g in enumerate(gtf_lines_lst):
            
            if verbose:
                if k%100 == 0:
                    print('\rParsing GTF %i/%i' % (k,len(gtf_lines_lst)), end='    ' )
                    
            gd = gene_descriptor(g, genome, base_cds, fill, Cov_th = MIN_COV_TO_SEL, Abn_th = MIN_ABN_TO_SEL)
            gd_lst.append(gd)
            chrs.append( gd.chr )
            tcnt += len(gd.td_lst)
            for td in gd.td_lst:
                if len(td.te_to_ge_map) > 0: tcnt2 += 1
    
        del gtf_lines_lst
    
    elapsed_time1 = time.time() - start_time1
    if verbose: print('\rParsing GTF ... done. %i/%i trs found from %i genes (%i) ' % (tcnt, tcnt2, len(gd_lst), elapsed_time1), end = ' ')
    # if verbose: print('\rParsing GTF ... done. %i/%i trs found from %i genes (%i) ' % (tcnt, tcnt2, len(gd_lst), elapsed_time1))

    return gd_lst, chrs


def mc_core_gen_descriptor(gx):
    
    return gene_descriptor(gx[0], gx[1], gx[2], gx[3], Cov_th = MIN_COV_TO_SEL, Abn_th = MIN_ABN_TO_SEL)
    
def mc_core_mapping( a ):
    
    g, rm, rnd, rsti, ng, nr, tdg, tdr = combine_genes_and_rgns_per_chr( a[0], a[1], \
                                                       a[2], a[3], \
                                                       verbose = False )
                
    return g, rm, rnd, rsti, ng, nr, [a[4][w] for w in tdg], [a[5][w] for w in tdr]


'''
        gd_lsts, chr_lst = get_gene_descriptor(gtf_lines, genome = None, fill = True, \
                                               cg = True, verbose = True)
'''

def pack_gene_descriptor( gd_lst, chrs ):
    
    chr_lst = list(set(chrs))
    chr_lst.sort()
    chrs = np.array(chrs)

    gd_lst_of_lst = []
    for chrm in chr_lst:
        wh = which(chrs == chrm)

        s_pos = np.zeros(len(wh))
        for k in range(len(wh)): 
            s_pos[k] = gd_lst[wh[k]].begin
        odr = s_pos.argsort()

        gd_sel_ordered = [gd_lst[wh[odr[k]]] for k in range(len(wh))]
        gd_lst_of_lst.append(gd_sel_ordered)
    
    for k, gd_sel_ordered in enumerate(gd_lst_of_lst):
        gd_sel_ordered = combine_genes_per_chr( gd_sel_ordered, verbose = False )
        gd_lst_of_lst[k] = gd_sel_ordered

    return gd_lst_of_lst, chr_lst


def parse_and_combine_genes_and_rgns( gd_lst_of_lst, chr_lst, rgns_lst_mi, rgns_lst_nd, rgns_lst_sti, \
                                     n_cores = 1, genome = None, verbose = False ):
    
    ## Mapping
        
    vol_total = 0
    rs_chrs = []
    for rs in rgns_lst_mi: 
        rs_chrs.append(rs.rgns[0].chr)
        vol_total += rs.get_volume()

    chrs = chr_lst # list(set(chr_lst+rs_chrs))
        
    rs_chrs = np.array(rs_chrs)
    
    gd_lst_out = []
    rs_m_lst_out = []
    rs_nd_lst_out = []
    rs_sti_lst_out = []
    gd_lst_unmapped = []

    start_time1 = time.time()
    
    ng_unmapped = 0
    nr_unmapped = 0

    to_del_g = []
    to_del_r = []

    if n_cores == 1:
        gcnt = 0

        rsm = { c: [] for c in chrs }
        rsnd = { c: [] for c in chrs }
        rssti = { c: [] for c in chrs }
        for k, c in enumerate(rs_chrs):
            if c in chrs:
                rsm[c].append(rgns_lst_mi[k])
                rsnd[c].append(rgns_lst_nd[k])
                rssti[c].append(rgns_lst_sti[k])
        
        del rgns_lst_mi
        del rgns_lst_nd
        del rgns_lst_sti

        for k, c in enumerate(chrs):

            gcnt += len(gd_lst_of_lst[k])
            if verbose:
                print('\rMapping %i/%i' % (k,len(chrs)), end='    ', flush = True )
                
            g, rm, rnd, rsti, ng, nr, tdg, tdr, g_um = mc_core_combine_genes_and_rgns_per_chr( (gd_lst_of_lst[k], rsm[c], \
                                                               rsnd[c], rssti[c], False) )
            # to_del_g = to_del_g + [gd_sel_idx[m] for m in tdg]
            # to_del_r = to_del_r + [rs_sel_idx[m] for m in tdr]

            for gd in g: 
                gd.gcnt = gcnt
                # gcnt += 1
                
            gd_lst_out = gd_lst_out + g
            rs_m_lst_out = rs_m_lst_out + rm
            rs_nd_lst_out = rs_nd_lst_out + rnd
            rs_sti_lst_out = rs_sti_lst_out + rsti
            gd_lst_unmapped = gd_lst_unmapped + g_um

            ng_unmapped += ng
            nr_unmapped += nr
    
        del gd_lst_of_lst
        
    else:
        if verbose:
            print('\rMapping ..', end='    ', flush = True )
            
        rsm = { c: [] for c in chrs }
        rsnd = { c: [] for c in chrs }
        rssti = { c: [] for c in chrs }
        for k, c in enumerate(rs_chrs):
            if c in chrs:
                rsm[c].append(rgns_lst_mi[k])
                rsnd[c].append(rgns_lst_nd[k])
                rssti[c].append(rgns_lst_sti[k])
        
        del rgns_lst_mi
        del rgns_lst_nd
        del rgns_lst_sti

        gcnt = 0
        rs_tuple = []
        for k, c in enumerate(chrs):
            rs_tuple.append( (gd_lst_of_lst[k], rsm[c], rsnd[c], rssti[c], verbose) )
            gcnt += len(gd_lst_of_lst[k])
            
        del gd_lst_of_lst

        num_core = min( n_cores, (cpu_count() - 1) )
        pool = Pool(num_core)
        m = 1
        # for g, rm, rnd, rsti, ng, nr, tdg, tdr in pool.map(mc_core_combine_genes_and_rgns_per_chr, rs_tuple):
        for g, rm, rnd, rsti, ng, nr, tdg, tdr, g_um in pool.imap_unordered(mc_core_combine_genes_and_rgns_per_chr, rs_tuple):
            
            if verbose:
                print('\rMapping %i/%i' % (m,len(chrs)), end='    ', flush = True )

            m += 1    
            for gd in g: 
                gd.gcnt = gcnt
                # gcnt += 1
                
            gd_lst_out = gd_lst_out + g
            rs_m_lst_out = rs_m_lst_out + rm
            rs_nd_lst_out = rs_nd_lst_out + rnd
            rs_sti_lst_out = rs_sti_lst_out + rsti
            gd_lst_unmapped = gd_lst_unmapped + g_um

            ng_unmapped += ng
            nr_unmapped += nr
    
        pool.close()
        pool.join()

        
    elapsed_time1 = time.time() - start_time1
    if verbose: print('\rMapping %i chrs ... done (%i) ' % (len(chrs),elapsed_time1) )

    vol_sel = 0
    for rs in rs_m_lst_out: 
        vol_sel += rs.get_volume()
        
    if ng > 0:
        print('   %i genes in the GTF/GFF do not have mapped reads.' % (ng_unmapped) )
    if nr > 0:
        print('   %i chunks are out of gene loci in GTF/GFF. (%i%% of total volume) ' % (nr_unmapped, int(100*(vol_total-vol_sel)/vol_total)) )
        
    '''
    if len(to_del_r) > 0:
        to_del_r.sort(reverse=True)
        for ri in to_del_r:
            del rgns_lst_mi[ri]
            del rgns_lst_nd[ri]
            del rgns_lst_sti[ri]
            
    if len(to_del_g) > 0:
        to_del_g.sort(reverse=True)
        for gi in to_del_g:
            del gd_lst[gi]
    '''
            
    return gd_lst_out, rs_m_lst_out, rs_nd_lst_out, rs_sti_lst_out, gd_lst_unmapped


def mc_core_combine_genes_and_rgns_per_chr( rs_tuple ):

    gd_lst, rgns_lst_mi, rgns_lst_nd, rgns_lst_sti, verbose = rs_tuple

    #'''
    n_gd = len(gd_lst)
    s_pos = np.zeros(n_gd)
    e_pos = np.zeros(n_gd)
    s_min = np.zeros(n_gd)
    e_max = np.zeros(n_gd)
    for k, gd in enumerate(gd_lst): 
        s_pos[k] = gd.begin
        e_pos[k] = gd.end
        if k == 0:
            em = e_pos[0]
        else:
            em = max(em, e_pos[k])
        e_max[k] = em
        
    for k in reversed(range(len(s_pos))):
        if k == (len(s_pos)-1):
            sm = s_pos[k]
        else:
            sm = min(sm,s_pos[k])
        s_min[k] = sm
        
    ####
    r_lst = {k: [] for k in range(len(rgns_lst_mi))}
    g_lst = {k: [] for k in range(len(gd_lst))}

    start_time1 = time.time()
    #'''

    for k, rs in enumerate(rgns_lst_mi):
        span = rs.get_span()
        wh = which( ((e_pos < span.start) | (s_pos > span.end)), False )
        for m in wh:
            if gd_lst[m].exons.has_ext_intersection_with(rs):
                r_lst[k].append(m)
                g_lst[m].append(k)
        '''
        for m in wh:
            r_lst[k].append(m)
            g_lst[m].append(k)
        '''
    elapsed_time1 = time.time() - start_time1
    # if verbose: print('\rMapping %i ... done (%i) ' % (len(rgns_lst_mi),elapsed_time1) )
    #'''

    '''
    n_ng = 0
    for k in g_lst.keys():
        if len(g_lst[k]) == 0:
            n_ng += 1
            print('==== Unmapped: %s (%i), %s ====' %
                  (gd_lst[k].td_lst[0].gid, gd_lst[k].ntr, gd_lst[k].td_lst[0].tid) )
            gd_lst[k].exons.print_minimal()        
    if n_ng > 0:
        print('Num unmapped genes in %s = %i ' % (gd_lst[0].chr, n_ng) )
    
    #'''
    '''
    m = 0

    for k, rs in enumerate(rgns_lst_mi):
        span = rs.get_span()
        if (k+1) < len(rgns_lst_mi):
            span2 = rgns_lst_mi[k+1].get_span()
        else:
            span2 = span

        m2 = m
        
        m1 = m
        if m1 < len(gd_lst):
            while True:
                if e_max[m1] < span.start:
                    break
                else:
                    if gd_lst[m1].exons.has_ext_intersection_with(rs):
                        r_lst[k].append(m1)
                        g_lst[m1].append(k)
                        
                if e_max[m1] < span2.start: m2 = m1
                m1 -= 1
                if m1 < 0: break
            
        if (m+1) < len(gd_lst):
            m1 = m+1
            while True:
                if s_min[m1] > span.end:
                    break
                else:
                    if gd_lst[m1].exons.has_ext_intersection_with(rs):
                        r_lst[k].append(m1)
                        g_lst[m1].append(k)

                if e_max[m1] < span2.start: m2 = m1
                m1 += 1
                if m1 >= len(gd_lst): break
                
        m = m2 + 1
        
        if verbose:
            if k%100 == 0:
                print('\rMapping %i/%i' % (k,len(rgns_lst_mi)), end='    ', flush = True )
                
    elapsed_time1 = time.time() - start_time1
    # if verbose: print('\rMapping %i ... done (%i) ' % (len(rgns_lst_mi),elapsed_time1) )
    #'''
    
    bpr = np.ones(len(rgns_lst_mi))
    bpg = np.ones(len(gd_lst))

    rg_lst = []
    for k in r_lst.keys():
        gis = r_lst[k]
        if bpr[k] > 0:
            ri = [k]
            git = []
            while True:
                git = set()
                for i in ri:
                    if bpr[i] > 0:
                        git = git.union(r_lst[i])
                    else:
                        print('ERROR %i,%i' % (k,i))
                if len(git) == 0:
                    # rg_lst.append((rit,[]))
                    break
                else:
                    rit = set()
                    for j in git:
                        if bpg[j] > 0:
                            rit = rit.union(g_lst[j])
                        else:
                            print('ERROR %i,%i' % (k,j))

                    if len(rit) == len(ri):
                        rg_lst.append((rit,git))
                        for i in rit: bpr[i] = 0
                        for i in git: bpg[i] = 0
                        break
                    else:
                        ri = rit
       
    map_r2g = [] # np.full(len(rg_lst), -1)
    to_del_r = []
    to_del_g = []
    for rg in rg_lst:
        ris = list(rg[0])
        tgt = ris[0]
        for ri in ris[1:]:
            rgns_lst_mi[tgt].merge(rgns_lst_mi[ri])
            rgns_lst_nd[tgt].merge(rgns_lst_nd[ri])
            rgns_lst_sti[tgt].merge(rgns_lst_sti[ri])
            to_del_r.append(ri)
            
        ri = tgt
        gis = list(rg[1])
        tgt = gis[0]
        for gi in gis[1:]:
            gd_lst[tgt].merge(gd_lst[gi])
            to_del_g.append(gi)
            
        gd_lst[tgt].get_span()
        map_r2g.append((ri, tgt))
        
    rgns_lst_mi_out = []
    rgns_lst_nd_out = [] 
    rgns_lst_sti_out = []
    gd_lst_out = []
    
    for ri, gi in map_r2g:
        rgns_lst_mi_out.append(rgns_lst_mi[ri])
        rgns_lst_nd_out.append(rgns_lst_nd[ri]) 
        rgns_lst_sti_out.append(rgns_lst_sti[ri])
        gd_lst_out.append(gd_lst[gi])
        
    ng = np.sum(bpg > 0)
    nr = np.sum(bpr > 0)

    wh = which(bpg > 0)
    if len(wh) > 0:
        gd_lst_unmapped = [gd_lst[w] for w in wh]
    else:
        gd_lst_unmapped = []
    
    '''
    wh = which(bpr > 0)
    rgns_lst_mi_out = rgns_lst_mi_out + [rgns_lst_mi[w] for w in wh]
    rgns_lst_nd_out = rgns_lst_nd_out + [rgns_lst_nd[w] for w in wh]
    rgns_lst_sti_out = rgns_lst_sti_out + [rgns_lst_sti[w] for w in wh]
    gd_lst_out = gd_lst_out + [None for w in wh]
    #'''
    
    to_del_r = to_del_r + which(bpr > 0)
    to_del_g = to_del_g + which(bpg > 0)
    '''
    if len(to_del_r) > 0:
        to_del_r.sort(reverse=True)
        for ri in to_del_r:
            del rgns_lst_mi[ri]
            del rgns_lst_nd[ri]
            del rgns_lst_sti[ri]
            
    if len(to_del_g) > 0:
        to_del_g.sort(reverse=True)
        for gi in to_del_g:
            del gd_lst[gi]
    #'''        
    del r_lst
    del g_lst
    del rg_lst
    
    for r in rgns_lst_mi_out: r.set_cvg()
    for r in rgns_lst_nd_out: r.set_cvg()
    for r in rgns_lst_sti_out: r.set_cvg()
                    
    return gd_lst_out, rgns_lst_mi_out, rgns_lst_nd_out, rgns_lst_sti_out, ng, nr, to_del_g, to_del_r, gd_lst_unmapped
#'''
    

def combine_genes_and_rgns_per_chr( gd_lst, rgns_lst_mi, rgns_lst_nd, rgns_lst_sti, verbose = False ):

    #'''
    n_gd = len(gd_lst)
    s_pos = np.zeros(n_gd)
    e_pos = np.zeros(n_gd)
    s_min = np.zeros(n_gd)
    e_max = np.zeros(n_gd)
    for k, gd in enumerate(gd_lst): 
        s_pos[k] = gd.begin
        e_pos[k] = gd.end
        if k == 0:
            em = e_pos[0]
        else:
            em = max(em, e_pos[k])
        e_max[k] = em
        
    for k in reversed(range(len(s_pos))):
        if k == (len(s_pos)-1):
            sm = s_pos[k]
        else:
            sm = min(sm,s_pos[k])
        s_min[k] = sm
        
    ####
    r_lst = {k: [] for k in range(len(rgns_lst_mi))}
    g_lst = {k: [] for k in range(len(gd_lst))}

    start_time1 = time.time()
    #'''

    for k, rs in enumerate(rgns_lst_mi):
        span = rs.get_span()
        wh = which( ((e_pos < span.start) | (s_pos > span.end)), False )
        for m in wh:
            if gd_lst[m].exons.has_ext_intersection_with(rs):
                r_lst[k].append(m)
                g_lst[m].append(k)

    elapsed_time1 = time.time() - start_time1
    # if verbose: print('\rMapping %i ... done (%i) ' % (len(rgns_lst_mi),elapsed_time1) )
    #'''
    
    '''
    m = 0

    for k, rs in enumerate(rgns_lst_mi):
        span = rs.get_span()
        if (k+1) < len(rgns_lst_mi):
            span2 = rgns_lst_mi[k+1].get_span()
        else:
            span2 = span

        m2 = m
        
        m1 = m
        if m1 < len(gd_lst):
            while True:
                if e_max[m1] < span.start:
                    break
                else:
                    if gd_lst[m1].exons.has_ext_intersection_with(rs):
                        r_lst[k].append(m1)
                        g_lst[m1].append(k)
                        
                if e_max[m1] < span2.start: m2 = m1
                m1 -= 1
                if m1 < 0: break
            
        if (m+1) < len(gd_lst):
            m1 = m+1
            while True:
                if s_min[m1] > span.end:
                    break
                else:
                    if gd_lst[m1].exons.has_ext_intersection_with(rs):
                        r_lst[k].append(m1)
                        g_lst[m1].append(k)

                if e_max[m1] < span2.start: m2 = m1
                m1 += 1
                if m1 >= len(gd_lst): break
                
        m = m2 + 1
        
        if verbose:
            if k%100 == 0:
                print('\rMapping %i/%i' % (k,len(rgns_lst_mi)), end='    ', flush = True )
                
    elapsed_time1 = time.time() - start_time1
    if verbose: print('\rMapping %i ... done (%i) ' % (len(rgns_lst_mi),elapsed_time1) )
    #'''
    
    bpr = np.ones(len(rgns_lst_mi))
    bpg = np.ones(len(gd_lst))

    rg_lst = []
    for k in r_lst.keys():
        gis = r_lst[k]
        if bpr[k] > 0:
            ri = [k]
            git = []
            while True:
                git = set()
                for i in ri:
                    if bpr[i] > 0:
                        git = git.union(r_lst[i])
                    else:
                        print('ERROR %i,%i' % (k,i))
                if len(git) == 0:
                    # rg_lst.append((rit,[]))
                    break
                else:
                    rit = set()
                    for j in git:
                        if bpg[j] > 0:
                            rit = rit.union(g_lst[j])
                        else:
                            print('ERROR %i,%i' % (k,j))

                    if len(rit) == len(ri):
                        rg_lst.append((rit,git))
                        for i in rit: bpr[i] = 0
                        for i in git: bpg[i] = 0
                        break
                    else:
                        ri = rit
       
    map_r2g = [] # np.full(len(rg_lst), -1)
    to_del_r = []
    to_del_g = []
    for rg in rg_lst:
        ris = list(rg[0])
        tgt = ris[0]
        for ri in ris[1:]:
            rgns_lst_mi[tgt].merge(rgns_lst_mi[ri])
            rgns_lst_nd[tgt].merge(rgns_lst_nd[ri])
            rgns_lst_sti[tgt].merge(rgns_lst_sti[ri])
            to_del_r.append(ri)
            
        ri = tgt
        gis = list(rg[1])
        tgt = gis[0]
        for gi in gis[1:]:
            gd_lst[tgt].merge(gd_lst[gi])
            to_del_g.append(gi)
            
        gd_lst[tgt].get_span()
        map_r2g.append((ri, tgt))
        
    rgns_lst_mi_out = []
    rgns_lst_nd_out = [] 
    rgns_lst_sti_out = []
    gd_lst_out = []
    
    for ri, gi in map_r2g:
        rgns_lst_mi_out.append(rgns_lst_mi[ri])
        rgns_lst_nd_out.append(rgns_lst_nd[ri]) 
        rgns_lst_sti_out.append(rgns_lst_sti[ri])
        gd_lst_out.append(gd_lst[gi])
        
    ng = np.sum(bpg > 0)
    nr = np.sum(bpr > 0)
    
    '''
    wh = which(bpr > 0)
    rgns_lst_mi_out = rgns_lst_mi_out + [rgns_lst_mi[w] for w in wh]
    rgns_lst_nd_out = rgns_lst_nd_out + [rgns_lst_nd[w] for w in wh]
    rgns_lst_sti_out = rgns_lst_sti_out + [rgns_lst_sti[w] for w in wh]
    gd_lst_out = gd_lst_out + [None for w in wh]
    #'''
    
    to_del_r = to_del_r + which(bpr > 0)
    to_del_g = to_del_g + which(bpg > 0)
    '''
    if len(to_del_r) > 0:
        to_del_r.sort(reverse=True)
        for ri in to_del_r:
            del rgns_lst_mi[ri]
            del rgns_lst_nd[ri]
            del rgns_lst_sti[ri]
            
    if len(to_del_g) > 0:
        to_del_g.sort(reverse=True)
        for gi in to_del_g:
            del gd_lst[gi]
    #'''        
    del r_lst
    del g_lst
    del rg_lst
    
    for r in rgns_lst_mi_out: r.set_cvg()
    for r in rgns_lst_nd_out: r.set_cvg()
    for r in rgns_lst_sti_out: r.set_cvg()
                    
    return gd_lst_out, rgns_lst_mi_out, rgns_lst_nd_out, rgns_lst_sti_out, ng, nr, to_del_g, to_del_r
#'''
    

def combine_genes_and_rgns( gd_lst, rgns_lst_mi, rgns_lst_nd, rgns_lst_sti, n_cores = 1, verbose = False ):
    
    gd_chrs = []
    for gd in gd_lst: gd_chrs.append(gd.chr)
        
    rs_chrs = []
    for rs in rgns_lst_mi: rs_chrs.append(rs.rgns[0].chr)

    chrs = list(set(gd_chrs+rs_chrs))
        
    gd_chrs = np.array(gd_chrs)
    rs_chrs = np.array(rs_chrs)
    
    gd_lst_out = []
    rs_m_lst_out = []
    rs_nd_lst_out = []
    rs_sti_lst_out = []

    start_time1 = time.time()
    
    ng_unmapped = 0
    nr_unmapped = 0

    to_del_g = []
    to_del_r = []
    
    if n_cores == 0:
        arg_lst = []
        for k, c in enumerate(chrs):
            gd_sel_idx = which(gd_chrs == c)
            rs_sel_idx = which(rs_chrs == c)

            gd_sel = [gd_lst[w] for w in gd_sel_idx]
            rsm_sel = [rgns_lst_mi[w] for w in rs_sel_idx]
            rsnd_sel = [rgns_lst_nd[w] for w in rs_sel_idx]
            rssti_sel = [rgns_lst_sti[w] for w in rs_sel_idx]

            arg_lst.append( (gd_sel, rsm_sel, rsnd_sel, rssti_sel, gd_sel_idx, rs_sel_idx) )

        del gd_lst
        del rgns_lst_mi
        del rgns_lst_nd
        del rgns_lst_sti
        
        num_core = min( n_cores, (cpu_count() - 1) )
        pool = Pool(num_core)
        print('num cores to use = %i' % n_cores)

        cnt = 0
        for g, rm, rnd, rsti, ng, nr, tdg, tdr in pool.imap_unordered(mc_core_mapping, arg_lst):

            to_del_g = to_del_g + tdg
            to_del_r = to_del_r + tdr

            gd_lst_out = gd_lst_out + g
            rs_m_lst_out = rs_m_lst_out + rm
            rs_nd_lst_out = rs_nd_lst_out + rnd
            rs_sti_lst_out = rs_sti_lst_out + rsti

            ng_unmapped += ng
            nr_unmapped += nr
            cnt += 1

            if verbose:
                print('\rMapping %i/%i' % (cnt,len(chrs)), end='    ', flush = True )

        del arg_lst
        
        pool.close()
        pool.join()
        
    else:
        for k, c in enumerate(chrs):
            gd_sel_idx = which(gd_chrs == c)
            rs_sel_idx = which(rs_chrs == c)

            gd_sel = [gd_lst[w] for w in gd_sel_idx]
            rsm_sel = [rgns_lst_mi[w] for w in rs_sel_idx]
            rsnd_sel = [rgns_lst_nd[w] for w in rs_sel_idx]
            rssti_sel = [rgns_lst_sti[w] for w in rs_sel_idx]

            g, rm, rnd, rsti, ng, nr, tdg, tdr = combine_genes_and_rgns_per_chr( gd_sel, rsm_sel, \
                                                               rsnd_sel, rssti_sel, \
                                                               verbose = False )
            to_del_g = to_del_g + [gd_sel_idx[m] for m in tdg]
            to_del_r = to_del_r + [rs_sel_idx[m] for m in tdr]

            gd_lst_out = gd_lst_out + g
            rs_m_lst_out = rs_m_lst_out + rm
            rs_nd_lst_out = rs_nd_lst_out + rnd
            rs_sti_lst_out = rs_sti_lst_out + rsti

            ng_unmapped += ng
            nr_unmapped += nr

            if verbose:
                print('\rMapping %i/%i' % (k,len(chrs)), end='    ', flush = True )
    
        del gd_lst
        del rgns_lst_mi
        del rgns_lst_nd
        del rgns_lst_sti
        
    elapsed_time1 = time.time() - start_time1
    if verbose: print('\rMapping %i chrs ... done. %i(s)' % (len(chrs),elapsed_time1) )
        
    if ng > 0:
        print('   %i genes in the GTF/GFF do not have mapped reads.' % ng_unmapped )
    if nr > 0:
        print('   %i chunks are out of gene loci in GTF/GFF.' % nr_unmapped )
        
    '''
    if len(to_del_r) > 0:
        to_del_r.sort(reverse=True)
        for ri in to_del_r:
            del rgns_lst_mi[ri]
            del rgns_lst_nd[ri]
            del rgns_lst_sti[ri]
            
    if len(to_del_g) > 0:
        to_del_g.sort(reverse=True)
        for gi in to_del_g:
            del gd_lst[gi]
    '''
            
    return gd_lst_out, rs_m_lst_out, rs_nd_lst_out, rs_sti_lst_out


##########################################################################
## Functions to find coding regions and to generate proteome
##########################################################################

BASES = 'TCAG' # "tcag"
CODONS = [a + b + c for a in BASES for b in BASES for c in BASES]
AMINO_ACIDS = 'FFLLSSSSYY**CC*WLLLLPPPPHHQQRRRRIIIMTTTTNNKKSSRRVVVVAAAADDEEGGGG'
codon_table = dict(zip(CODONS, AMINO_ACIDS))
START_CODON = 'ATG'
rc_START_CODON = 'CAT'
STOP_CODONS = ['TAA','TAG','TGA']
rc_STOP_CODONS = ['TTA','CTA','TCA']
rev_comp_table = {'A':'T', 'C': 'G', 'G':'C', 'T':'A', 'N': 'N'}

def translate(seq):
    seq = seq.upper().replace('\n', '').replace(' ', '')
    peptide = ''
    
    for i in range(0, len(seq), 3):
        codon = seq[i: i+3]
        '''
        if codon.count('N') == 0:
            amino_acid = codon_table.get(codon, '*')
        else:
            amino_acid = '*'
        '''
        #'''
        amino_acid = codon_table.get(codon, '*')
        #if amino_acid != '*':
        peptide += amino_acid
        # else: break
        #'''
                
    return peptide

def reverse_complement(seq):
    
    rc_seq = ''
    Keys = rev_comp_table.keys()
    for k in reversed(range(len(seq))):
        if seq[k] in Keys:
            rc_seq = rc_seq + rev_comp_table[seq[k]]
        else:
            rc_seq = rc_seq + 'N'
    return rc_seq
    
def find_all_s_in_str(str,s):
    
    pos_lst = []
    start = 0
    while True:
        pos = str.find(s, start)
        if pos < 0: break
        else:
            pos_lst.append(pos)
            start = pos+1
        if start+3 >= len(str): break
            
    return pos_lst

def check_orf_condition_forward_from_start(tseq):
    
    start = -1
    stop = -1
    ss_lst = []
    pos_lst = find_all_s_in_str(tseq, START_CODON)
    if len(pos_lst) == 0:
        return start, stop, ss_lst
    else:
        for pos_start in pos_lst:
            pos_stop = -1
            n_stops = 0
            for p in range(pos_start+3,len(tseq)-1, 3):
                endp = min(p+3,len(tseq))
                codon = tseq[p:(p+3)]
                if codon in STOP_CODONS:
                    n_stops += 1
                    if n_stops == 1:
                        pos_stop = p
                        break
                        
            if (pos_stop >= 0): # & (n_stops == 1):
                ss_lst.append((pos_start, pos_stop))
                #'''
                if (start >= 0) & (stop >= 0):
                    len_prev = stop - start
                    len_curr = pos_stop - pos_start
                    if len_curr > len_prev:
                        start = pos_start
                        stop = pos_stop
                else:
                    start = pos_start
                    stop = pos_stop
                    # break
                #'''
                
        return start, stop, ss_lst
            
def check_equal_range(ss_lst, ss):
    
    b = False
    for s in ss_lst:
        if (s[0]==ss[0]) & (s[1]==ss[1]): b = True
    return b
        
def check_orf_condition_forward_old(tseq):
    
    start = -1
    stop = -1
    ss_lst = [(-1,-1),(-1,-1),(-1,-1)]
    
    pos_lst1 = find_all_s_in_str(tseq, STOP_CODONS[0])
    pos_lst2 = find_all_s_in_str(tseq, STOP_CODONS[1])
    pos_lst3 = find_all_s_in_str(tseq, STOP_CODONS[2])
    pos_lst = pos_lst1 + pos_lst2 + pos_lst3
    pos_lst.sort()
    
    if len(pos_lst) == 0:
        return check_orf_condition_forward_from_start(tseq)
    else:
        pos_lst = np.array(pos_lst)
        for os in range(3):
            start = -1
            stop = -1
            wh = which( pos_lst%3 == os )
            if len(wh) > 0:
                for k,w in enumerate(wh):
                    pos_stop = pos_lst[w]
                    pos_start = -1

                    ss = 0
                    if k > 0: ss = pos_lst[wh[k-1]]
                        
                    ps = find_all_s_in_str(tseq[ss:pos_stop], START_CODON)
                    if len(ps) > 0:
                        ps = np.array(ps) + ss
                        wh2 = which(ps%3 == os)
                        if len(wh2) > 0:
                            pos_start =  np.min(ps[wh2])
                            #'''
                            if pos_start < pos_stop:
                                if (start >= 0) & (stop >= 0):
                                    len_prev = stop - start
                                    len_curr = pos_stop - pos_start
                                    if len_curr > len_prev:
                                        start = pos_start
                                        stop = pos_stop
                                else:
                                    start = pos_start
                                    stop = pos_stop
                                    # break
                                #'''
            ss_lst[os] = (start, stop)
            
        start = -1
        stop = -1
        for os in range(3):
            (pos_start, pos_stop) = ss_lst[os]
            if (start >= 0) & (stop >= 0):
                len_prev = stop - start
                len_curr = pos_stop - pos_start
                if len_curr > len_prev:
                    start = pos_start
                    stop = pos_stop
            else:
                start = pos_start
                stop = pos_stop
                    
        return start, stop, ss_lst
            

def check_orf_condition_forward(tseq):
    
    start = -1
    stop = -1
    ss_lst = [(-1,-1),(-1,-1),(-1,-1)]
    
    pos_lst1 = find_all_s_in_str(tseq, STOP_CODONS[0])
    pos_lst2 = find_all_s_in_str(tseq, STOP_CODONS[1])
    pos_lst3 = find_all_s_in_str(tseq, STOP_CODONS[2])
    pos_lst = pos_lst1 + pos_lst2 + pos_lst3
    pos_lst.sort()
    
    pos_lst_start = find_all_s_in_str(tseq, START_CODON)
    pos_lst_start = np.array(pos_lst_start)
    
    if len(pos_lst) > 0:
        pos_lst = np.array(pos_lst)
        for os in range(3):
            start = -1
            stop = -1
            wh = which( pos_lst%3 == os )
            if len(wh) > 0:
                for k,w in enumerate(wh):
                    pos_stop = pos_lst[w]
                    pos_start = -1

                    ss = 0
                    if k > 0: ss = pos_lst[wh[k-1]]
                        
                    ps = find_all_s_in_str(tseq[ss:pos_stop], START_CODON)
                    if len(ps) > 0:
                        ps = np.array(ps) + ss
                        wh2 = which(ps%3 == os)
                        if len(wh2) > 0:
                            pos_start =  np.min(ps[wh2])
                            #'''
                            if pos_start < pos_stop:
                                if (start >= 0) & (stop >= 0):
                                    len_prev = stop - start
                                    len_curr = pos_stop - pos_start
                                    if len_curr > len_prev:
                                        start = pos_start
                                        stop = pos_stop
                                else:
                                    start = pos_start
                                    stop = pos_stop
                                    # break
                                #'''
                if (start < 0):
                    stop = pos_lst[wh[0]]
            else:
                if len(pos_lst_start) > 0: 
                    wh = which(pos_lst_start%3 == os)
                    if len(wh) > 0:
                        start = pos_lst_start[wh[0]]
                        
            ss_lst[os] = (start, stop)
            
    elif len(pos_lst) == 0:
        if len(pos_lst_start) > 0:
            for os in range(3):
                start = -1
                wh = which(pos_lst_start%3 == os)
                if len(wh) > 0:
                    start = pos_lst_start[wh[0]]
                ss_lst[os] = (start, stop)
        else:
            return start, stop, ss_lst
            
            
    start = -1
    stop = -1
    for os in range(3):
        (pos_start, pos_stop) = ss_lst[os]
        if (pos_start >= 0) & (pos_stop >= 0):
            if (start >= 0) & (stop >= 0):
                len_prev = stop - start
                len_curr = pos_stop - pos_start
                if len_curr > len_prev:
                    start = pos_start
                    stop = pos_stop
            else:
                start = pos_start
                stop = pos_stop

    if (start < 0) & (stop < 0):
        for os in range(3):
            (pos_start, pos_stop) = ss_lst[os]
            if (pos_start >= 0):
                pos_stop = len(tseq) - (len(tseq) - pos_start)%3
            elif (pos_stop >= 0):
                pos_start = os

            if (start >= 0) & (stop >= 0):
                len_prev = stop - start
                len_curr = pos_stop - pos_start
                if len_curr > len_prev:
                    start = pos_start
                    stop = pos_stop
            else:
                start = pos_start
                stop = pos_stop
                                   
    return start, stop, ss_lst
            

def check_orf_condition(tseq, strand = 1):
    
    if strand > 0:
        start, stop, ss_lst = check_orf_condition_forward(tseq)
        return start, stop, ss_lst
    elif strand < 0:
        tseq_c = reverse_complement(tseq)
        start, stop, ss_lst = check_orf_condition_forward(tseq_c)
        return start, stop, ss_lst
    else:
        start = -1
        stop = -1
        ss_lst = []
        return start, stop, ss_lst    


def get_attrs_from_fa_header(str_attr):
    
    name = None
    Len = -1
    abn = -1
    istrand = None
    cdng = None
    
    items = str_attr.split(' ')
    if len(items) > 0: name = items[0]
    if len(items) > 1:
        for item in items[1:-1]:
            sub_item = item.split(':')
            if sub_item[0] == 'length':
                Len = int(sub_item[1])
            elif sub_item[0] == 'abn':
                try:
                    abn = np.float32(sub_item[1])
                except ValueError:
                    print('WARNING: %s not a number' % sub_item[1])
                    abn = 0
            elif sub_item[0] == 'strand':
                istrand = get_istrand_from_c(sub_item[1][0]) # get_c_from_istrand
            elif len(sub_item) == 1:
                cdng = get_icdng_from_str(sub_item[0])
    
    return name, Len, abn, istrand, cdng

'''
def set_fa_header(name, Len, abn, strand, cdng):
    
    hdr = '%s length:%i abn:%5.2f strand:%s %s' % (name, Len, abn, get_c_from_istrand(strand), get_str_from_icdng(cdng))
    return hdr
'''    

def gen_proteome_from_trascriptome(hdr_lst, tseq_lst, len_th = MIN_PR_LENGTH, verbose = True, mx_cnt = 0, trareco = False, ignore_s = False):
    
    cand_cnt = len(hdr_lst)
    if mx_cnt == 0: mx_cnt = cand_cnt
    lines = []

    if len(hdr_lst) > 0:

        name, Len, abn, istrand, icdng = get_attrs_from_fa_header( hdr_lst[0] )
        if (Len >= 0) & (abn >= 0) & (istrand is not None) & (icdng is not None):
        
            if verbose: print('Converting .. ', end = '', flush = True)
            p_cand_cnt = 0
            for k, tseq in enumerate(tseq_lst):
                name, Len, abn, istrand, icdng = get_attrs_from_fa_header( hdr_lst[k] )

                if icdng is None: icdng = -1
                if (istrand is None): istrand = 0

                if ((istrand >= 0) & (icdng != 0)) | (ignore_s):
                    strand = 1
                    start, stop, ss_lst = check_orf_condition(tseq, strand = strand)
                    if (start >= 0) & (stop >= 0):
                        aseq = translate(tseq[start:stop])
                        if len(aseq) >= len_th:
                            hdr = set_fa_header(name, len(aseq), abn, istrand, icdng)
                            lines.append( '>' + hdr + '\n' )
                            lines.append(aseq+'\n')
                            p_cand_cnt += 1

                if ((istrand <= 0) & (icdng != 0)) | (ignore_s):
                    strand = -1
                    start, stop, ss_lst = check_orf_condition(tseq, strand = strand)
                    if (start >= 0) & (stop >= 0):
                        pseq = reverse_complement(tseq)
                        aseq = translate(pseq[start:stop])
                        if len(aseq) >= len_th:
                            hdr = set_fa_header(name, len(aseq), abn, istrand, icdng)
                            lines.append( '>' + hdr + '\n' )
                            lines.append(aseq+'\n')
                            p_cand_cnt += 1

                if verbose: 
                    if k%500 == 0: print('\rConverting .. %i/%i   ' % (k,cand_cnt), end = '', flush = True)
                if k > mx_cnt: break
                    
            if verbose: 
                print('\rConverting done. %i AASeq candidates found from %i trs. ' % (p_cand_cnt,cand_cnt))
        else:
            strands = np.zeros(cand_cnt)
            icdngs = np.full(cand_cnt, -1) ## initially set unspecified
            if trareco:
                for k in range(cand_cnt):
                    items = hdr_lst[k].split('_')
                    strands[k] = get_istrand_from_c(items[2])
                    icdngs[k] = get_icdng_from_str( items[3] )

            else:
                hdr0 = hdr_lst[0]
                items = hdr0.split(' ')
                if len(items) > 3:
                    if len(items[3]) > 7:
                        if items[3][:7] == 'strand:':
                            for k in range(cand_cnt):
                                items = hdr_lst[k].split(' ')
                                strands[k] = get_istrand_from_c( items[3][7:] )
                                icdngs[k] = get_icdng_from_str( items[4] )
            
            if verbose: print('Converting .. ', end = '')
            lines = []
            p_cand_cnt = 0
            for k, tseq in enumerate(tseq_lst):
                if ((strands[k] >= 0) & (icdngs[k] != 0)) | (ignore_s):
                    strand = 1
                    start, stop, ss_lst = check_orf_condition(tseq, strand = strand)
                    if (start >= 0) & (stop >= 0):
                        aseq = translate(tseq[start:stop])
                        if len(aseq) >= len_th:
                            items = hdr_lst[k].split(' ')
                            if strand != 0:
                                lines.append('>' + hdr_lst[k].split(' ')[0] + ' length:%i strand:%s %s\n' % \
                                             (len(aseq), get_c_from_istrand(strand), get_str_from_icdng( icdngs[k] )) ) # +'_+\n')
                            else:
                                lines.append('>' + hdr_lst[k] + ' strand:%i\n' % strand )

                            lines.append(aseq+'\n')
                            p_cand_cnt += 1

                if ((strands[k] <= 0) & (icdngs[k] != 0)) | (ignore_s):
                    strand = -1
                    start, stop, ss_lst = check_orf_condition(tseq, strand = strand)
                    if (start >= 0) & (stop >= 0):
                        pseq = reverse_complement(tseq)
                        aseq = translate(pseq[start:stop])
                        if len(aseq) >= len_th:
                            if strand != 0:
                                lines.append('>' + hdr_lst[k].split(' ')[0] + ' length:%i strand:%s %s\n' % \
                                             (len(aseq), get_c_from_istrand(strand), get_str_from_icdng( icdngs[k] )) ) # +'_+\n')
                            else:
                                lines.append('>' + hdr_lst[k] + ' strand:%i\n' % strand )

                            lines.append(aseq+'\n')
                            p_cand_cnt += 1

                if verbose: 
                    if k%100 == 0: print('\rConverting .. %i/%i' % (k,cand_cnt), end = '')
                if k > mx_cnt: break
                    
            if verbose: 
                print('\rConverting done. %i AASeq candidates found from %i trs. ' % (p_cand_cnt,cand_cnt))
         
    return lines

    
def Generate_Proteome(tr_fa, len_th = MIN_PR_LENGTH, verbose = True, mx_cnt = 0, trareco = False, fname_out = None, ignore_s = False):
    
    file_name = tr_fa.split('/')[-1]
    fns = file_name.split('.')[:-1]
    fname = ''
    for k, fn in enumerate(fns):
        if k > 0:
            fname = fname + '.'
        fname = fname + fn
    
    hdr_lst, tseq_lst = load_fasta1(tr_fa, verbose = False)
    cand_cnt = len(tseq_lst)

    lines = gen_proteome_from_trascriptome(hdr_lst, tseq_lst, len_th = len_th, verbose = verbose, trareco = trareco, ignore_s = ignore_s)
    p_cand_cnt = len(lines)/2
            
    if fname_out is None: fname_out = fname + '_proteome.fa'
    f = open(fname_out,'w+')
    f.writelines(lines)
    f.close()
                
    if verbose: 
        print('AASeq saved to %s' % (fname_out))
        
    return fname_out

    
##########################################################################
## Functions for StringFix main (1)
##########################################################################

def get_max_cvg(rs):
    max_cvg = 0
    for rgn in rs.rgns:
        max_cvg = max( max_cvg, rgn.ave_cvg_depth() )
    return(max_cvg)

# Transcript = collections.namedtuple('Transcript', 'prefix, gidx, grp_size, icnt, chr, start, end, seq, abn, tpm, iso_frac, prob')

def save_transcripts( fname, tr_lst ):
    
    tr_names = get_tr_name(tr_lst)
    f = open(fname,'w+')
    for k, tr in enumerate(tr_lst):
        s = '>%s\n' % tr_names[k]
        seq = tr.seq + '\n'
        f.writelines(s)
        f.writelines(seq)
    f.close()

def save_transcripts2( fname, tr_lst ):
    
    tr_names = get_tr_name(tr_lst)
    f = open(fname,'w+')
    for k, tr in enumerate(tr_lst):
        # s = '>%s\n' % tr_names[k]
        tid = 'SFix.%s.%i' % (str(tr.gidx), tr.icnt+1)
        c = get_c_from_istrand(tr.strand)
        c_or_n = tr.cdng # get_str_from_icdng( tr.cdng )
        s = '>%s length:%i abn:%f strand:%s %s\n' % (tid, len(tr.seq), np.round(tr.abn, 2), c, c_or_n)
        seq = tr.seq + '\n'
        f.writelines(s)
        f.writelines(seq)
    f.close()

    
def get_c_from_istrand(istrand):
    
    if istrand > 0: strand = '+'
    elif istrand == 0: strand = '.'
    else: strand = '-'
    return strand
        
    
def get_istrand_from_c(strand_c):
    
    if strand_c == '+': strand = 1
    elif strand_c == '-': strand = -1
    else: strand = 0
    return strand
        
    
def get_str_from_icdng( cds ):
    
    if cds > 0: c_or_n = 'Coding'
    elif cds == 0: c_or_n = 'Non-coding'
    else: c_or_n = 'unspecified'
    return c_or_n


def get_icdng_from_str( c_or_n ):
    
    if c_or_n == 'Coding': icdng = 1
    elif c_or_n == 'Non-coding': icdng = 0
    else: icdng = -1
    return icdng


def convert_into_tr(header, seq):    
    
    items = header.split('_')
    
    prefix = items[0]
    
    cse = items[1] # [3:]
    ss = cse.split(':')
    chr = ss[0]
    se = ss[1].split('-')
    start = np.int(se[0])
    end = np.int(se[1])
    
    strand = get_istrand_from_c(items[2])
    cdng = items[3]
    gidx = np.int(items[4])
    grp_size = np.int(items[5])
    icnt = np.int(items[6])
    abn = np.float32(items[7][4:])
    tpm = np.float32(items[8][4:])
    iso_frac = np.float32(items[9][6:])
    prob = np.float32(items[10][2:])
    nexons = np.int(items[11][3:])
    vol = np.int(items[12][2:])
                
    tr = Transcript(prefix, gidx, grp_size, icnt, chr, start, end, strand, cdng, seq, abn, tpm, iso_frac, prob, nexons, vol)
        
    return(tr)
    
def load_transcripts(file_name, verbose = True):
    
    if verbose == True : print('Loading %s ... ' % file_name, end='' )
    f = open(file_name, 'r')
    cnt = 0
    trs = []
    for line in f :
        if line[0] == '>':
            if cnt > 0: 
                tr = convert_into_tr(header, seq_lst)
                trs.append(tr)
            cnt += 1
            header = line[1:-1]
            seq_lst = ''
        else :
            seq_lst = seq_lst + line[:-1]

    tr = convert_into_tr(header, seq_lst)
    trs.append(tr)

    f.close()
    
    if verbose == True : print('Num.Trs = ', cnt, ' loaded                             ')
    
    return(trs)


Ref_Tr = collections.namedtuple('Ref_Tr', 'name, cvg_frac, abn, rpkm, tpm, seq')

def load_ref_tr_sim(file_name, verbose = True):
    
    if verbose == True : print('Loading %s ... ' % file_name, end='' )
    f = open(file_name, 'r')
    cnt = 0
    ref_tr = []
    for line in f :
        if line[0] == '>':
            if cnt > 0: 
                tr = Ref_Tr(items[0], np.float32(items[1])*100, np.float32(items[2]), np.float32(items[3]), 0, seq_lst)
                ref_tr.append(tr)
            cnt += 1
            header = line[1:-1]
            items = header.split(':')
            seq_lst = ''
        else :
            seq_lst = seq_lst + line[:-1]

    tr = Ref_Tr(items[0], np.float32(items[1])*100, np.float32(items[2]), np.float32(items[3]), 0, seq_lst)
    ref_tr.append(tr)

    f.close()
    
    ref_tr2 = []
    abn_total = 0
    for tr in ref_tr:
        abn_total += tr.abn
    nf = 1000000/abn_total
    
    for t in ref_tr:
        tr = Ref_Tr(t.name, t.cvg_frac, t.abn, t.rpkm, t.abn*nf, t.seq )
        ref_tr2.append(tr)
    
    if verbose == True : print('Num.Trs = ', cnt, ' loaded                             ')
    
    return(ref_tr)


## Transcript = collections.namedtuple('Transcript', 'prefix, icnt, chr, start, end, seq, abn, tpm')    
def print_tr(tr_lst):
    for tr in tr_lst:
        print('%i, Len: %i, Abn: %4.1f' % (tr.icnt, len(tr.seq), tr.abn) )
    print('  ')

    
def check_rs_m(rs_m, hdr = '' ):
    cnt = 0
    for k in range(len(rs_m.rgns)):
        l1 = (rs_m.rgns[k].end-rs_m.rgns[k].start+1)
        l2 = rs_m.rgns[k].cmat.shape[1]
        if l1 != l2:
            if cnt == 0: 
                print('\n',end='')
                cnt += 1
            print('ERROR in check_rs_m() at %s: %i rgns obj is not consistent. %i != %i' % (hdr,k, l1, l2 ) )


def save_rgns( fname, rgns_lst, rd_len, num_rds, ho = False ):
    
    f = open(fname,'w+')
    
    line = '@FRAG_LEN=%i,NUM_READS=%i\n' % (rd_len, num_rds)
    f.writelines(line)
    
    for k in range(len(rgns_lst)):
        rgns_lst[k].order()
        if ho:
            lines = rgns_lst[k].convert_to_text_lines_ho(k)
            f.writelines(lines)
        else:
            lines = rgns_lst[k].convert_to_text_lines(k)
            f.writelines(lines)
    f.close()

    
def get_id_from_hdr(hdr):

    items = hdr.split()
    sn = int(items[0])
    N = int(items[1])
    n = int(items[2])
    return(sn,N,n)
    
def load_rgns( fname, mode, n_rgns = 0, verbose = False ):
    
    rgns_lst = []
    f = open(fname,'r')
    line_lst = f.readlines()
    f.close()
    
    if mode == 0: Lcnt = 7
    else: Lcnt = 2
        
    rd_len = 0
    num_rds = 0
    rcnt = 0
    lcnt = 0
    sdiv = 10
    step = np.ceil(len(line_lst)/(sdiv*Lcnt))
    
    for line in line_lst: # f :
        # print(line)
        if len(line) == 0: break
        else:
            if line[0] == '@':
                line_tmp = line[1:-1]
                items = line_tmp.split(',')
                rd_len = int(items[0][9:])
                num_rds = int(items[1][10:])
            else:
                if lcnt == 0:
                    lines_tmp = []
                    if line[0] == '>':
                        lines_tmp.append(line)
                        lcnt += 1
                        sn, N, n = get_id_from_hdr( line[1:-1] )
                    else:
                        print('ERROR in load_rgns(): 0')

                else:
                    if lcnt%Lcnt == 0:
                        if line[0] == '>':
                            lines_tmp.append(line)
                            lcnt += 1
                            sn, N, n = get_id_from_hdr( line[1:-1] )
                        else:
                            print('ERROR in load_rgns(): 1')

                    else:
                        lines_tmp.append(line)
                        lcnt += 1

                        if (lcnt%Lcnt == 0) & (N==n):

                            if mode == 0: rgns = regions()
                            else: rgns = regions_nd()

                            rgns.set_from_text_lines(lines_tmp)

                            if (n_rgns > 0) & ((sn-rcnt)>0):
                                if mode == 0:
                                    for m in range(sn-rcnt): rgns_lst.append(regions())
                                else:
                                    for m in range(sn-rcnt): rgns_lst.append(regions_nd())
                                rcnt += (sn-rcnt)

                            rgns_lst.append(rgns)
                            rcnt += 1
                            lcnt = 0
                            if verbose:
                                if rcnt%step == 0: print('.',end='')
                        
    if n_rgns > 0:
        if rcnt < n_rgns:
            if mode == 0:
                for m in range(n_rgns-rcnt): rgns_lst.append(regions())
            else:
                for m in range(n_rgns-rcnt): rgns_lst.append(regions_nd())
            rcnt += (n_rgns-rcnt)
            
    return(rgns_lst, rcnt, rd_len, num_rds)
        

def load_rgns_nd( fname, mode, n_rgns, verbose = False ):
    
    rgns_lst = []
    f = open(fname,'r')
    line_lst = f.readlines()
    f.close()
    
    rd_len = 0
    num_rds = 0
    rcnt = 0
    lcnt = 0
    sdiv = 10
    step = np.ceil(len(line_lst)/(sdiv))
    
    for line in line_lst: # f :
        # print(line)
        if len(line) == 0: break
        else:
            if line[0] == '@':
                line_tmp = line[1:-1]
                items = line_tmp.split(',')
                rd_len = int(items[0][9:])
                num_rds = int(items[1][10:])
            else:
                if lcnt == 0:
                    lines_tmp = []

                lines_tmp.append(line)
                lcnt += 1

                sn, N, n = get_id_from_hdr( line[1:-1] )

                if (N==n):

                    rgns = regions_nd()
                    rgns.set_from_text_lines(lines_tmp)

                    if (n_rgns > 0) & ((sn-rcnt)>0):
                        for m in range(sn-rcnt): rgns_lst.append(regions_nd())
                        rcnt += (sn-rcnt)

                    rgns_lst.append(rgns)
                    rcnt += 1
                    lcnt = 0
                    if verbose:
                        if rcnt%step == 0: print('.',end='')
                        
    if n_rgns > 0:
        if rcnt < n_rgns:
            for m in range(n_rgns-rcnt): rgns_lst.append(regions_nd())
            rcnt += (n_rgns-rcnt)
            
    return(rgns_lst, rcnt, rd_len, num_rds)
        

def trim_contigs( rgns_lst_m, rgns_lst_nd, rgns_lst_sti, verbose = 1, sdiv = 10 ):

    start_time = time.time()
    cntp = 0; cntn = 0; cnt0 = 0; cntf = 0; cntg = 0
    fp = 0; fn = 0; f0 = 0; ff = 0

    pos = np.zeros(len(rgns_lst_m))
    for k in range(len(rgns_lst_m)):
        rgn_t = rgns_lst_m[k].get_span()
        pos[k] = rgn_t.start

    pos = np.array(pos)
    odr = pos.argsort()
    n_tr = 0
    Tr_lst = []
    Is_lst = []

    gcnt = 0
    rs_mi_lst = []
    rs_nd_lst = []
    for n in range(len(rgns_lst_m)):

        k = odr[n]
        rs_m = rgns_lst_m[k]
        rs_nd = rgns_lst_nd[k]
        rs_sti = rgns_lst_sti[k]
           
        Vol = rs_m.get_volume() + rs_sti.get_volume()
                    
        max_dev_n = MAX_DEV_N
        max_dev_d = MAX_DEV_D
        max_dev_i = MAX_DEV_I

        vec_d = check_complte_overlap( rs_m, rs_nd, 'D' )
        rs_nd, cm = merge_nearby_ndi(rs_nd, max_dev_n, max_dev_d, max_dev_i, vec_d)
        # rs_nd, cm = merge_nearby_ndi(rs_nd, max_dev_n, max_dev_d, max_dev_i)
        rs_sti, ci = merge_nearby_ndi(rs_sti, max_dev_n, max_dev_d, max_dev_i)

        rs_nd, rs_m, b = rem_nm_2long_and_2thin( rs_nd, rs_m )
        # rs_m, rs_nd, rs_sti = rem_low_cvg_rgns( rs_m, rs_nd, rs_sti )
        
        if len(rs_m.rgns) > 0:
            rs_nd, rs_m, b = adj_nd( rs_nd, rs_m )
            
            rs_nd, rs_m, b = trim_m( rs_nd, rs_m, rs_sti, max_dev_n, max_dev_d )               
            rs_nd, rs_m, b = trim_d( rs_nd, rs_m )  ## n should be first, then d
            rs_nd, rs_m, b = split_m( rs_nd, rs_m, rs_sti )           
            rs_nd, rs_m, b = trim_n_short( rs_nd, rs_m )  
            rs_nd, rs_m, b = add_i( rs_nd, rs_m, rs_sti )
           
            rs_m.update()
            rs_m.set_cvg()
            rs_nd.update()
            rs_nd.set_cvg()
            
            rs_mi_lst.append(rs_m)
            rs_nd_lst.append(rs_nd)
              
    return(rs_mi_lst, rs_nd_lst) 


def rem_low_cvg_rgns( rs_m, rs_nd, rs_sti = None ):
    
    mx_cvg = 0
    for r in rs_m.rgns:
        mx_cvg = max( mx_cvg, r.ave_cvg_depth() )
    for r in rs_nd.rgns:
        mx_cvg = max( mx_cvg, r.ave_cvg_depth() )
    cvg_th = mx_cvg*R_VALID_CFRAC
        
    to_del = []
    for k, r in enumerate(rs_m.rgns):
        # if (r.ave_cvg_depth() < cvg_th): to_del.append(k)
        if (r.ave_cvg_depth() < cvg_th) & (r.ave_cvg_depth() < R_VALID_CVG): to_del.append(k)
    
    if len(to_del) > 0:
        to_del.sort(reverse=True)
        for k in to_del: del rs_m.rgns[k]
        
    to_del = []
    for k, r in enumerate(rs_nd.rgns):
        if (r.ave_cvg_depth() < cvg_th) & (r.ave_cvg_depth() < R_VALID_CVG): to_del.append(k)
    
    if len(to_del) > 0:
        to_del.sort(reverse=True)
        for k in to_del: del rs_nd.rgns[k]
    
    if rs_sti is None:
        return rs_m, rs_nd        
    else:
        to_del = []
        for k, r in enumerate(rs_sti.rgns):
            if (r.ave_cvg_depth() < cvg_th) & (r.ave_cvg_depth() < R_VALID_CVG): to_del.append(k)

        if len(to_del) > 0:
            to_del.sort(reverse=True)
            for k in to_del: del rs_sti.rgns[k]
    
        return rs_m, rs_nd, rs_sti

def trim_contigs_single( rs_m, rs_nd, rs_sti, gcnt = 0, rem_low_cvg = True, verbose = 1, sdiv = 10 ):

    Vol = rs_m.get_volume() + rs_sti.get_volume()

    max_dev_n = MAX_DEV_N
    max_dev_d = MAX_DEV_D
    max_dev_i = MAX_DEV_I

    vec_d = check_complte_overlap( rs_m, rs_nd, 'D' )
    rs_nd, cm = merge_nearby_ndi(rs_nd, max_dev_n, max_dev_d, max_dev_i, vec_d)
    # vec_i = check_complte_overlap( rs_m, rs_sti, 'I' )
    rs_sti, ci = merge_nearby_ndi(rs_sti, max_dev_n, max_dev_d, max_dev_i)

    if rem_low_cvg: 
        rs_nd, rs_m, b = rem_nm_2long_and_2thin( rs_nd, rs_m )
        rs_m, rs_nd, rs_sti = rem_low_cvg_rgns( rs_m, rs_nd, rs_sti )

    if len(rs_m.rgns) > 0:
        # rs_nd, rs_m, b = adj_nd( rs_nd, rs_m )

        rs_nd, rs_m, b = trim_m( rs_nd, rs_m, rs_sti, max_dev_n, max_dev_d )               
        rs_nd, rs_m, b = trim_d( rs_nd, rs_m )  ## n should be first, then d
        rs_nd, rs_m, b = split_m( rs_nd, rs_m, rs_sti )           
        rs_nd, rs_m, b = trim_n_short( rs_nd, rs_m )  
        rs_nd, rs_m, b = add_i( rs_nd, rs_m, rs_sti )
        
        rs_m.update()
        rs_m.set_cvg()
        rs_nd.update()
        rs_nd.set_cvg()
            
    return rs_m, rs_nd


def check_bistrand( r_mi, r_nd ):
    
    pos = 0
    neg = 0
    if len(r_mi.rgns) > 0:
        for rgn in r_mi.rgns:
            if rgn.xs > 0: pos += 1
            elif rgn.xs < 0: neg += 1

    if len(r_nd.rgns) > 0:
        for rgn in r_nd.rgns:
            if rgn.xs > 0: pos += 1
            elif rgn.xs < 0: neg += 1
            
    return pos, neg


NUM_CORES = 4

def find_kf_and_kb( exons, rs_m ):

    flag_f = True
    flag_b = True
    kf = 0
    kb = len(exons.rgns)-1
    for k in range(len(exons.rgns)):
        if flag_f:
            r = exons.rgns[k]
            if r.type.lower() == 'exon':
                if rs_m.has_ext_intersection_with(r):
                    kf = k
                    flag_f = False
                    break
                
    for k in reversed(range(len(exons.rgns))):
        if flag_b:
            r = exons.rgns[k]
            if r.type.lower() == 'exon':
                if rs_m.has_ext_intersection_with(r):
                    kb = k
                    flag_f = False
                    break
    return kf, kb
    

def mc_core_get_tr(rs_tuple):
    
    rs_m = rs_tuple[0]
    rs_nd = rs_tuple[1]
    rs_sti = rs_tuple[2]
    gcnt = rs_tuple[3]
    len_th = rs_tuple[4]
    method = rs_tuple[5]
    rd_len = rs_tuple[6]
    gd = rs_tuple[7]
    
    gsize = len(rs_m.rgns)
    gvol = rs_m.get_volume()

    #'''
    st = time.time()
    if gd is not None:
        ## merge gd.exons to rs_m -> update rs_m
        for k, r in enumerate(gd.exons.rgns):
            if r.type.lower() == 'exon':
                Len = r.end - r.start + 1
                rm = region(r.chr, r.start, r.end, 'M', seq_or_cmat = 'N'*Len, cvg_dep = CVG_DEPTH_TMP)
                # rm.get_cvg()
                rs_m.rgns.append(rm)
                # rs_m.update(rm)
        rs_m.update()
        rs_m.set_cvg()
        # for r in rs_m.rgns: r.get_cvg()
    #'''
    et1 = time.time() - st
        
    st = time.time()
    rs_m, rs_nd = trim_contigs_single( rs_m, rs_nd, rs_sti, gcnt, (gd is None) )
    et2 = time.time() - st

    #'''
    st = time.time()
    if gd is not None:
        to_del = []
        for k, r in enumerate(rs_m.rgns):
            if r.ave_cvg_depth() <= CVG_DEPTH_TMP:
                to_del.append(k)
        if len(to_del) > 0:
            # print('%i RS_M removed among %i' % (len(to_del), len(rs_m.rgns)))
            to_del.sort()
            for k in reversed(to_del): del rs_m.rgns[k]
            rs_m.update()
    et3 = time.time() - st
    #'''
    
    grp = splice_graph(rd_len, gcnt)
    
    b = True
    et6 = 0
    et5 = 0
    et4 = 0
    etx = 0
    if (len(rs_m.rgns) > 0): # & (len(rs_m.rgns) < 20):
        
        st = time.time()
        bg, rs_m, rs_nd = grp.build(rs_m, rs_nd, (gd is None), len_th = len_th)
        et4 = time.time() - st
        mn = 0
        cnt = 0

        tr_lst = []
        if_lst = []
        gtf_lines = []
        if gd is not None:
            st = time.time()
            gd, tr_lst, if_lst, gtf_lines, etx = grp.td_and_ae_using_annotation(gd, len_th, method = method)
            et6 = time.time() - st

        else: # if len(tr_lst+if_lst) == 0:
            st = time.time()
            b, mn, cnt, rs_m, rs_nd = grp.select_nodes_and_edges( ) # rs_m, rs_nd)
            et5 = time.time() - st
            st = time.time()
            if b:
                gd, tr_lst, if_lst, gtf_lines = grp.td_and_ae(len_th, method = method)

            p, n = check_bistrand( rs_m, rs_nd )
            if (p > 0) & (n > 0): grp.bistranded = True # pass
            else: grp.bistranded = False # grp = None
            et6 = time.time() - st
            
    del rs_m
    del rs_nd
    del rs_sti
    # del gd
            
    if not b:
        tr_lst = []
        if_lst = []
        gtf_lines = []
        mn = 0
        cnt = 0

    return tr_lst, if_lst, gtf_lines, gsize, gvol, mn, cnt, grp, gcnt, gd, np.array([et1,et2,et3,et4, et5, et6]), etx

def get_transcripts_mc( rgns_lst_mi, rgns_lst_nd, rgns_lst_st, read_len, annot = None, \
                        n_cores = NUM_CORES, len_th = MIN_TR_LENGTH, method = 'lasso', \
                        nrec = 0, start = 0, verbose = True, sdiv = 20 ):

    start_time = time.time()
    cntp = 0; cntn = 0; cnt0 = 0; cntf = 0; cntg = 0
    fp = 0; fn = 0; f0 = 0; ff = 0

    n_tr = 0
    GTF_lst = []
    Tr_lst = []
    Is_lst = []
    mn_lst = []
    grp_lst = []
    gd_lst = []
    cd_th = np.zeros(len(rgns_lst_mi), dtype=int)
    w_cnt = np.zeros(len(rgns_lst_mi), dtype=int)
    gsize = np.zeros(len(rgns_lst_mi), dtype=int)
    gvol = np.zeros(len(rgns_lst_mi), dtype=int)

    gcnt = 0
    start_time1 = time.time()
    if verbose: 
        if annot is None: print('\rSearch isoforms & est abundances ..... ', end='')
        else: print('\rRecovering isoforms & est abundances ..... ', end='')
        
    #'''
    gv = np.zeros(len(rgns_lst_nd))
    for k in range(len(rgns_lst_nd)):
        gv[k] = -len(rgns_lst_nd[k].rgns) # -rgns_lst_mi[k].get_volume()
    odr = gv.argsort()
    #'''
    
    rs_tuple_lst = []
    if start == 0:
        if nrec == 0: Nrec = len(rgns_lst_mi)
        else: Nrec = nrec
    else:
        Nrec = len(rgns_lst_mi)
        if start >= Nrec: start = Nrec-1

    for m in range(Nrec-start):
        k =  odr[m+start] # m + start
        gd = None
        if (annot is not None): 
            if k < len(annot): gd = annot[k]
        rs_tuple_lst.append( (rgns_lst_mi[k], rgns_lst_nd[k], rgns_lst_st[k], k, \
                              len_th, method, read_len, gd) )
    
    num_core = min( n_cores, (cpu_count() - 1) )
    # print("num cores to use = {}".format(num_core))
    pool = Pool(num_core)
    total_iteration = len(rs_tuple_lst)

    start_time1 = time.time()
    if verbose: 
        if annot is None: print('\rSearch isoforms & est abundances ..... ', end='')
        else: print('\rRecovering isoforms & est abundances ..... ', end='')
    m = 1
    ets_sum = 0
    etx_sum = 0
    for tlst, ilst, gtf_lines, gs, gv, mn, ct, grp, k, gd, ets, etx in \
        pool.imap_unordered(mc_core_get_tr, rs_tuple_lst):
        # tqdm.tqdm_notebook(pool.imap_unordered(mc_core_get_tr, rs_tuple_lst), total=total_iteration):

        ets_sum = ets_sum + ets
        etx_sum = etx_sum + etx

        Tr_lst = Tr_lst + tlst
        Is_lst = Is_lst + ilst
        GTF_lst = GTF_lst + gtf_lines
        gsize[k] = gs
        gvol[k] = gv
        cd_th[k] = mn
        w_cnt[k] = ct
        if grp is not None: 
            grp_lst.append(grp)
            
        if gd is not None: 
            gd_lst.append(gd)

        if verbose: 
            elapsed_time = time.time() - start_time1
            t_time = elapsed_time*len(rs_tuple_lst)/m
            r_time = t_time - elapsed_time
            if (m%100 == 0) | (m < 100):
                if annot is None:
                    print('\rSearch isoforms & est abundances ..... %i/%i   ' \
                           % (m, len(rs_tuple_lst)), end='')
                else:
                    print('\rRecovering isoforms & est abundances ..... %i/%i   ' \
                           % (m, len(rs_tuple_lst)), end='')
            m += 1
            
    pool.close()
    pool.join()
    
    if verbose: 

        n_cov_eh = 0
        # if gd is not None:
        if len(gd_lst) > 0:
            for gd in gd_lst:
                for td in gd.td_lst:
                    if td.cov > 1.1: n_cov_eh += 1

        elapsed_time1 = time.time() - start_time1
        if annot is None: 
            print('\rSearch isoforms & est abundances ..... done (%i)                 ' % (int(elapsed_time1)))
        else:
            print('\rRecovering isoforms & est abundances ..... done (%i, %i)                 ' % (int(elapsed_time1), n_cov_eh))
    
    d = {'gsize': gsize, 'gvol': gvol, 'cd_th': cd_th, 'w_cnt': w_cnt }
    df = pd.DataFrame(data = d)
    
    return Tr_lst, Is_lst, GTF_lst, df, grp_lst, gd_lst, ets_sum, etx_sum # mn_lst


def get_transcripts( rgns_lst_mi, rgns_lst_nd, rgns_lst_st, read_len, annot = None, len_th = MIN_TR_LENGTH, \
                     method = 'lasso', nrec = 0, start = 0, verbose = True, sdiv = 20 ):

    start_time = time.time()
    cntp = 0; cntn = 0; cnt0 = 0; cntf = 0; cntg = 0
    fp = 0; fn = 0; f0 = 0; ff = 0

    n_tr = 0
    GTF_lst = []
    Tr_lst = []
    Is_lst = []
    mn_lst = []
    grp_lst = []
    gd_lst = []
    cd_th = np.zeros(len(rgns_lst_mi), dtype=int)
    w_cnt = np.zeros(len(rgns_lst_mi), dtype=int)
    gsize = np.zeros(len(rgns_lst_mi), dtype=int)
    gvol = np.zeros(len(rgns_lst_mi), dtype=int)

    gcnt = 0
    start_time1 = time.time()
    if verbose: 
        if annot is None: print('\rSearch isoforms & est abundances ..... ', end='')
        else: print('\rRecovering isoforms & est abundances ..... ', end='')
        
    #'''
    gv = np.zeros(len(rgns_lst_nd), dtype=np.float32)
    for k in range(len(rgns_lst_nd)):
        gv[k] = -len(rgns_lst_nd[k].rgns) # -rgns_lst_mi[k].get_volume()
    odr = gv.argsort()
    #'''
    
    rs_tuple_lst = []
    if start == 0:
        if nrec == 0: Nrec = len(rgns_lst_mi)
        else: Nrec = nrec
    else:
        Nrec = len(rgns_lst_mi)
        if start >= Nrec: start = Nrec-1

    for m in range(Nrec-start):
        k = odr[m+start]
        gd = None
        if (annot is not None): 
            if k < len(annot): gd = annot[k]
        rs_tuple_lst.append( (rgns_lst_mi[k], rgns_lst_nd[k], rgns_lst_st[k], k, \
                              len_th, method, read_len, gd) )

    ets_sum = 0        
    etx_sum = 0        
    for m in range(len(rs_tuple_lst)):
        
        tlst, ilst, gtf_lines, gs, gv, mn, ct, grp, k, gd, ets, etx = mc_core_get_tr(rs_tuple_lst[m])
        
        ets_sum = ets_sum + ets
        etx_sum = etx_sum + etx

        Tr_lst = Tr_lst + tlst
        Is_lst = Is_lst + ilst
        GTF_lst = GTF_lst + gtf_lines
        gsize[k] = gs
        gvol[k] = gv
        cd_th[k] = mn
        w_cnt[k] = ct
        if grp is not None: 
            grp_lst.append(grp)
            gd_lst.append(gd)

        if verbose: 
            if m > 0:
                elapsed_time = time.time() - start_time1
                t_time = elapsed_time*len(rs_tuple_lst)/m
                r_time = t_time - elapsed_time
                if m%100 == 0:
                    if annot is None:
                        print('\rSearch isoforms & est abundances ..... %i/%i   ' \
                               % (int(r_time), m, len(rs_tuple_lst)), end='')
                    else:
                        print('\rRecovering isoforms & est abundances ..... %i/%i   ' \
                               % (m, len(rs_tuple_lst)), end='')
    
    if verbose: 
        elapsed_time1 = time.time() - start_time1
        if annot is None: 
            print('\rSearch isoforms & est abundances ..... done (%i)               ' % (int(elapsed_time1)))
        else:
            print('\rRecovering isoforms & est abundances ..... done (%i)               ' % (int(elapsed_time1)))
    
    d = {'gsize': gsize, 'gvol': gvol, 'cd_th': cd_th, 'w_cnt': w_cnt }
    df = pd.DataFrame(data = d)
    
    return Tr_lst, Is_lst, GTF_lst, df, grp_lst, gd_lst, ets_sum, etx_sum # mn_lst


############################
#### StringFix main ########

def get_tpm(tr_lst):
    
    abn_total = 0
    for tr in tr_lst:
        abn_total += tr.abn
    nf = 1000000/abn_total

    tr_lst_out = []
    for t in tr_lst:
        TPM = t.tpm*nf
        tr = Transcript(t.prefix,t.gidx,t.grp_size,t.icnt,t.chr,t.start,t.end,t.strand, t.cdng, \
                        t.seq,t.abn, TPM, t.iso_frac, t.prob, t.nexs, t.gvol)
        tr_lst_out.append(tr)
        
    return(tr_lst_out)

def filter_rgns( r_lst_m, r_lst_nd, r_lst_sti, vol_th, s_th = 0.9 ):
    
    to_del = []
    for k, r in enumerate(r_lst_m):
        vol = r.get_volume() # + r.get_volume()
        if (vol < vol_th):
            to_del.append(k)
        else:
            if r.cnt_r > 0:
                if r.cnt_s/r.cnt_r > s_th: to_del.append(k)
            
    if len(to_del) > 0:
        to_del.sort(reverse=True)
        for k in to_del: 
            del r_lst_m[k]
            del r_lst_nd[k]
            del r_lst_sti[k]
    
    return(r_lst_m, r_lst_nd, r_lst_sti)


def filter_rgns_old( r_lst_m, r_lst_nd, vol_th ):
    
    to_del = []
    for k in range(len(r_lst_m)):
        vol = r_lst_m[k].get_volume()
        if vol < vol_th:
            to_del.append(k)
            
    if len(to_del) > 0:
        to_del.sort(reverse=True)
        for k in to_del: 
            del r_lst_m[k]
            del r_lst_nd[k]
    
    return(r_lst_m, r_lst_nd)


### Default Trs Filter parameters
def check_rgns( rgns_lst_mi, rgns_lst_nd ):

    cnt = 0
    v_tot = 0
    v_hyb = 0
    for k in range(len(rgns_lst_mi)):
        cvol = rgns_lst_mi[k].get_volume()
        v_tot += cvol
        cp = 0
        cn = 0
        for m in range(len(rgns_lst_nd[k].rgns)):
            if rgns_lst_nd[k].rgns[m].xs < 0: cn += 1
            elif rgns_lst_nd[k].rgns[m].xs > 0: cp += 1
        if (cp > 0) & (cn > 0):
            v_hyb += cvol
            cnt += 1
            # print('=== %i ===' % k)
            # rgns_lst_mi[k].print_short()
            # rgns_lst_nd[k].print_short()
            
    return cnt, v_hyb, v_tot
    

'''
LINE_VALID = 0
NO_MORE_LINE = 4
LINE_INVALID = 2

CONTINUED = 0
NEW_CHRM = 1
# LINE_INVALID = 2
NOT_SORTED = 3
'''

def check_strand( r_m_lst, r_nd_lst ):
    
    pos = 0
    neg = 0
    for r in r_nd_lst:
        if len(r.rgns) > 0:
            if r.rgns[0].xs > 0: pos += 1
            elif r.rgns[0].xs < 0: neg += 1
            
    for r in r_m_lst:
        if len(r.rgns) > 0:
            if r.rgns[0].xs > 0: pos += 1
            elif r.rgns[0].xs < 0: neg += 1
            
    return pos, neg


def mc_core_build_cntg(sam_lst_n_sa):
    
    b = True
    sam_lst, sa = sam_lst_n_sa[:-1], sam_lst_n_sa[-1]        
    if (len(sam_lst) >= MIN_N_RDS_PER_GENE): # MIN_RD_NUM_PER_GENE): # & ((cp==0) | (cn==0)):

        r_lst_m, r_lst_nd, r_lst_sti, rgn_idx = \
            get_regions_all_from_sam( sam_lst, sa = sa )
        b = False
        sam_lst = None # []
            
    if b:
        r_lst_m = []
        r_lst_nd = []
        r_lst_sti = []
    
    return r_lst_m, r_lst_nd, r_lst_sti


def build_contigs(s_lst_of_lst, title = ''):
    
    rgns_lst_mi = []
    rgns_lst_nd = []
    rgns_lst_st = []
    
    for k, s_lst in enumerate(s_lst_of_lst):
        
        r_lst_mi, r_lst_nd, r_lst_st = mc_core_build_cntg(s_lst)
        rgns_lst_mi = rgns_lst_mi + r_lst_mi
        rgns_lst_nd = rgns_lst_nd + r_lst_nd
        rgns_lst_st = rgns_lst_st + r_lst_st

        if k%100 == 0:
            # print('\rBuilding loci & CMat ... (%i/%ig)                        ' \
            #       % (k, len(s_lst_of_lst)), end='')
            print('\r' + ' '*100, end='', flush = True)
            if len(title) == 0:
                print('\rBuilding loci & CMat ... (%i/%ic) ' \
                      % (k, len(s_lst_of_lst)), end='', flush = True)
            else:
                print('\r   processing %s (%i/%ic) ' \
                      % (title, k, len(s_lst_of_lst)), end='', flush = True)
    
    # print('\rBuilding loci & CMat ... done (%ig)                        ' % (len(s_lst_of_lst)), end='')
    return rgns_lst_mi, rgns_lst_nd, rgns_lst_st


def build_contigs_mc(s_lst_of_lst, n_cores = NUM_CORES, title = ''):
    
    rgns_lst_mi = []
    rgns_lst_nd = []
    rgns_lst_st = []
    
    num_core = max( min( n_cores, (cpu_count() - 1) ), 1)
    pool = Pool(num_core)
    total_iteration = len(s_lst_of_lst)
    
    if True: # not TQDM:
        
        s_lst_of_lst.sort(reverse = True, key=len)

        print('\r' + ' '*100, end='', flush = True)
        if len(title) == 0:
            print('\rBuilding loci & CMat ...  ', end='', flush = True)
        else:
            print('\r   processing %s ... ' % (title), end='', flush = True)
        k = 0
        for r_lst_mi, r_lst_nd, r_lst_st in pool.imap_unordered(mc_core_build_cntg, s_lst_of_lst):
            rgns_lst_mi = rgns_lst_mi + r_lst_mi
            rgns_lst_nd = rgns_lst_nd + r_lst_nd
            rgns_lst_st = rgns_lst_st + r_lst_st    
            
            k += 1
            if k%100 == 0:
                print('\r' + ' '*100, end='', flush = True)
                if len(title) == 0:
                    print('\rBuilding loci & CMat ... (%i/%ic) ' \
                          % (k, total_iteration), end='', flush = True)
                else:
                    print('\r   processing %s ... (%i/%ic) ' \
                          % (title, k, total_iteration), end='', flush = True)
            
    pool.close()
    pool.join()
    
    return rgns_lst_mi, rgns_lst_nd, rgns_lst_st


def proc_read_sam( sam_obj, q ):
    
    while True:
        er_code, sam_lst, num_reads = sam_obj.get_one_overlaped_sam()        
        q.put( (er_code, sam_lst, sam_obj.num_reads) )
        if er_code == NO_MORE_LINE: break
        

def save_rgns_obj(filename, rgns_lst_m, rgns_lst_nd, rgns_lst_sti, rd_len, n_rds, med_frag_len ):
    
    with open(filename, 'wb') as f:
        pickle.dump( (rgns_lst_m, rgns_lst_nd, rgns_lst_sti, rd_len, n_rds, med_frag_len), f )
        
def load_rgns_obj(filename):
    
    with open(filename, 'rb') as f:
        data = pickle.load( f )
        # rgns_lst_m, rgns_lst_nd, rgns_lst_sti, rd_len, n_rds, med_frag_len = pickle.load( f )
    # return rgns_lst_m, rgns_lst_nd, rgns_lst_sti, rd_len, n_rds, med_frag_len
    return data
 
def save_obj(filename, obj ):
    
    with open(filename, 'wb') as f:
        pickle.dump( (obj), f )
        
def load_obj(filename):
    
    with open(filename, 'rb') as f:
        obj = pickle.load( f )
    return obj


##########################################################################
## StringFix-Analysis
##########################################################################

def filter_trs_len( fa_lines_list, min_len = 0 ):

    Len  = len(fa_lines_list)
    if Len%2 != 0:
        print('ERROR in filter_trs_len: Num lines = %i ' % Len )
        return []
    else:
        fa_lines_out = []
        Num = np.int(Len/2)
        for k in range(Num):
            if len(fa_lines_list[ k*2+1 ]) > min_len: # including '\n'
                fa_lines_out.append( fa_lines_list[ k*2 ] )
                fa_lines_out.append( fa_lines_list[ k*2+1 ] )
        return fa_lines_out


def filter_trs_1(trs, frag_len = 80, g_th = 10, abn_th_t = 1, abn_th_i = 1, \
               iso_frac_th = 0.01, len_th = 200, verbose = True ):
    
    if verbose == True : print('Filtering ... ', end='' )
    trs_out = []
    isfm_out = []
    nti = 0
    nii = 0
    nto = 0
    nio = 0
    for tr in trs:
        if tr.prefix == 'T':
            nti += 1
            if tr.nexs == 1:
                if (tr.gvol >= g_th*frag_len*1) & (tr.abn >= abn_th_t*4.5) & (len(tr.seq) >= len_th): 
                    nto += 1
                    trs_out.append(tr)
            else:
                if (tr.nexs >= 4):
                    if (tr.gvol >= g_th*frag_len) & (tr.abn >= abn_th_t) & (len(tr.seq) >= len_th): 
                        nto += 1
                        trs_out.append(tr)
                else:
                    if (tr.gvol >= g_th*frag_len) & (tr.abn >= abn_th_t) & (len(tr.seq) >= len_th): 
                        nto += 1
                        trs_out.append(tr)
        else:
            nii += 1
            if (tr.gvol >= g_th*frag_len) & (tr.abn >= abn_th_i) & (tr.iso_frac >= iso_frac_th) & (len(tr.seq) >= len_th): 
                # isfm_out.append(tr)
                trs_out.append(tr)
                nio += 1
                
    if verbose == True : print('Num.Trs = %i %i (%i) -> %i, %i (%i) ' % (nti,nii,nti+nii,nto,nio,nto+nio))
    # return(trs_out, isfm_out)
    return(trs_out)


def filter_trs_2(trs, frag_len = 80, g_th = 10, abn_th_t = 1, abn_th_i = 1, \
               iso_frac_th = 0.01, len_th = 200, ne_th = 4, verbose = True):
    
    if verbose == True : print('Filtering ... ', end='' )
    trs_out = []
    isfm_out = []
    nti = 0
    nii = 0
    nto = 0
    nio = 0
    g_th = g_th * abn_th_i
    ref_th = ne_th*g_th*frag_len*abn_th_i
    min_abn = 10000000
    min_gvol = 10000000
    min_isf = 2
    for tr in trs:
        met = min(tr.grp_size, 4)*min(tr.nexs,4)*min(tr.gvol, 400)
        thr = ref_th/met
        r = 1
        # if thr > 1: r = 1.5
        if tr.nexs == 1: thr *= 4
        if (tr.gvol > g_th*frag_len*thr) & (tr.abn >= abn_th_i*thr) & (tr.iso_frac >= iso_frac_th) & (len(tr.tseq) >= len_th*r): 
            if tr.prefix == 'T': 
                trs_out.append(tr)
                nto += 1
            else: 
                # isfm_out.append(tr)
                trs_out.append(tr)
                nio += 1
                
            min_abn = min(min_abn,tr.abn)
            min_gvol = min(min_gvol,tr.gvol)
            min_isf = min(min_isf,tr.iso_frac)
            
        if tr.prefix == 'T': nti += 1
        else: nii += 1
            
    if verbose == True : 
        print('Num.Trs = %i %i (%i) -> %i, %i (%i)' % (nti,nii,nti+nii,nto,nio,nto+nio) )
        print('Min.Abn = %f, Min.IsoFrac = %f, Min.GVol = %4.1f' % (min_abn, min_isf, min_gvol) )
        
     # return(trs_out, isfm_out)
    return(trs_out)


def get_file_name( path_file_name ):

    file_names = path_file_name.split('/')[-1]
    fns = file_names.split('.')
    ext = fns[-1]
    fns = fns[:-1]
    fname = ''
    for k, fn in enumerate(fns):
        if k > 0:
            fname = fname + '.'
        fname = fname + fn

    return fname, ext


def get_path_name( path_file_name ):

    fns = path_file_name.split('.')
    ext = fns[-1]
    fns = fns[:-1]
    fname = ''
    for k, fn in enumerate(fns):
        if k > 0:
            fname = fname + '.'
        fname = fname + fn

    return fname, ext


def mc_core_get_gtf_and_fasta_pf(gd):

    ne = 0
    # ntr, npr, ne = gd.update_td_info()
    gtf_line, cn = gd.get_gtf_lines_from_exons()
    lt, lp = gd.get_fasta_lines_from_exons(peptide = False)

    '''
    if len(lt) != ntr*2:
        print('ERROR in mc_core_get_gtf_and_fasta_pf: %i != %i ' % (ntr, len(lt)/2) )
    if len(lp) != npr*2:
        print('ERROR in mc_core_get_gtf_and_fasta_pf: %i != %i ' % (npr, len(lp)/2) )
    #'''
    return gtf_line, lt, lp, ne, cn


def StringFix_analysis(sam_file, gtf = None, genome_file = None, suffix = None, jump = 0, sa = 2, cbyc = False, \
                       n_cores = 1, min_frags_per_gene = 2, len_th = MIN_TR_LENGTH, out_tr = False,
                       sav_rgn = False, out_dir = None ):
    '''
    if gtf is None:
        print('ERROR: No GTF/GFF file provided.')
        return
    #'''
    
    method = 'lasso'
    Nrec = 0
    Start = 0
    
    file_names = sam_file.split('/')[-1]
    fns = file_names.split('.')[:-1]
    fname = ''
    for k, fn in enumerate(fns):
        if k > 0:
            fname = fname + '.'
        fname = fname + fn

    if out_dir is not None:
        if out_dir[-1] == '/':
            fname = out_dir + fname
        else:
            fname = out_dir + '/' + fname

    if suffix is not None:    
        fname = fname + '_' + suffix

    if jump > 1: return fname, None, None

    NUM_CORES = n_cores
    start_time1 = time.time()
    start_time2 = time.time()
    if jump%2 == 0:

        GTF_lst = []
        rgns_lst_mi = []
        rgns_lst_nd = []
        rgns_lst_st = []

        cnt = 0
        mx_len = 12
        er_code = 0
        
        print('StringFix started ', datetime.datetime.now())
        so = sam_obj(sam_file, sa = sa)
        
        if n_cores == 1: num_parallel_chunks = 4
        else: num_parallel_chunks = NUM_PARALLEL_CHUNKS
        
        b_cnt = 0
        r_lst_of_lst = []
        
        ########################################################
        
        med_frag_len = 0
        if cbyc:
            
            print('\rBuilding loci & CMat ') # , end='')
            cnt_c = 0
            while True:

                start_time = time.time()
                er_code, sam_lst, num_reads = so.get_one_overlaped_sam()

                if er_code == NOT_SORTED:
                    break
                else:
                    if b_cnt == 0: r_lst_of_lst = []
                    b_cnt += len(sam_lst)

                    sam_lst.append(sa)
                    r_lst_of_lst.append( sam_lst ) # (sam_lst, sa) )
                    # r_lst_of_lst.append( (sam_lst, sa) )

                    if n_cores == 1: 
                        if (b_cnt == num_parallel_chunks) | (er_code == NO_MORE_LINE): b_cnt = 0
                    else: 
                        # if (er_code == NEW_CHRM) | (er_code == NO_MORE_LINE): b_cnt = 0
                        if ((b_cnt > num_parallel_chunks) & (er_code == NEW_CHRM)) | (er_code == NO_MORE_LINE): b_cnt = 0

                    #'''
                    if b_cnt == 0:

                        tlen = []
                        for r_lst in r_lst_of_lst:
                            for sl in r_lst[:-1]:
                                tlen.append(sl.tlen)
                                if len(tlen) > 100000: break
                        mfl = np.median(tlen)
                        med_frag_len += mfl 

                        if n_cores == 1:
                            # chr_name = sam_lst[0].rname
                            chr_lst = []
                            chr_name = ''
                            for r_lst in r_lst_of_lst:
                                if r_lst[0].rname not in chr_lst:
                                    chr_lst.append(r_lst[0].rname)
                                    chr_name = chr_name + '%s ' % (r_lst[0].rname)
                            if len(chr_name) > 50: 
                                if (cnt_c == 0) & (er_code == NO_MORE_LINE): chr_name = ' '
                                else: chr_name = 'others'
                            r_mi_lst, r_nd_lst, r_st_lst = build_contigs(r_lst_of_lst, chr_name)
                        else:
                            chr_name = ''
                            # if (cnt_c > 0) | (er_code != NO_MORE_LINE):
                            chr_lst = []
                            chr_name = ''
                            for r_lst in r_lst_of_lst:
                                if r_lst[0].rname not in chr_lst:
                                    chr_lst.append(r_lst[0].rname)
                                    chr_name = chr_name + '%s ' % (r_lst[0].rname)
                            if len(chr_name) > 50: 
                                if (cnt_c == 0) & (er_code == NO_MORE_LINE): chr_name = ' '
                                else: chr_name = 'others'
                            # if cnt_c == 0: print(' ')

                            start_time3 = time.time()
                            r_mi_lst, r_nd_lst, r_st_lst = build_contigs_mc(r_lst_of_lst, n_cores, chr_name)

                            # if (cnt_c > 0) | (er_code != NO_MORE_LINE):
                            elapsed_time3 = time.time() - start_time3
                            print('\r' + ' '*100, end='', flush = True)
                            print('\r   processing %s... done. (%i) (%ir, %ic, %i)' \
                                  % (chr_name, elapsed_time3, int(so.num_reads), len(r_lst_of_lst), mfl), flush = True) #, end='')

                        rgns_lst_mi = rgns_lst_mi + r_mi_lst
                        rgns_lst_nd = rgns_lst_nd + r_nd_lst
                        rgns_lst_st = rgns_lst_st + r_st_lst
        
                        if er_code == NO_MORE_LINE: break
                        else:
                            cnt_c += 1
                    #'''

                    cnt += 1
                    # if cnt_c > 0:
                    if cnt%100 == 0:
                        print('\r' + ' '*100, end='', flush = True)
                        print('\r   loading (%ir, %ic, %s) ' \
                              % (int(so.num_reads), cnt, sam_lst[0].rname), end='', flush = True)

                    if er_code == NO_MORE_LINE: break

            med_frag_len = np.int(med_frag_len/(cnt_c+1))

            elapsed_time1 = time.time() - start_time2
            print('\rBuilding loci & CMat ... done (%i). (%ir, %ic, %i) ' \
                  % (int(elapsed_time1), int(so.num_reads), cnt, med_frag_len) )

        else:
        
            print('\rLoading SAM lines ......  ', end='')        
            while True:

                start_time = time.time()
                er_code, sam_lst, num_reads = so.get_one_overlaped_sam()

                if er_code == NOT_SORTED:
                    break
                else:
                    sam_lst.append(sa)
                    r_lst_of_lst.append( sam_lst ) # (sam_lst, sa) )
                    # r_lst_of_lst.append( (sam_lst, sa) )

                    cnt += 1
                    if cnt%100 == 0:
                        print('\r' + ' '*100, end='', flush = True)
                        print('\rLoading SAM lines ...... (%ir, %ic) ' % (int(so.num_reads), cnt), end='', flush = True)

                    if er_code == NO_MORE_LINE: break

            tlen = []
            for r_lst in r_lst_of_lst:
                for sl in r_lst[:-1]:
                    tlen.append(sl.tlen)
                    if len(tlen) > 100000:
                        break
            med_frag_len = np.median(tlen)

            #'''
            elapsed_time1 = time.time() - start_time1
            print('\r' + ' '*100, end='', flush = True)
            print('\rLoading SAM lines ...... done (%i). (%ir, %ic) ' \
                  % (int(elapsed_time1), int(so.num_reads), cnt), flush = True )
            start_time2 = time.time()

            if n_cores == 1:
                print('Building loci & CMat ... ', end='')
                r_mi_lst, r_nd_lst, r_st_lst = build_contigs(r_lst_of_lst)
            else:
                print('Building loci & CMat ... ', end='')
                r_mi_lst, r_nd_lst, r_st_lst = build_contigs_mc(r_lst_of_lst, n_cores)

            rgns_lst_mi = rgns_lst_mi + r_mi_lst
            rgns_lst_nd = rgns_lst_nd + r_nd_lst
            rgns_lst_st = rgns_lst_st + r_st_lst
            #''' 
           
            elapsed_time1 = time.time() - start_time2
            print('\rBuilding loci & CMat ... done (%i). %ir, %ic, med.frag.len = %i ' \
                  % (int(elapsed_time1), int(so.num_reads), cnt, med_frag_len) )
            
        ########################################################
        
        del r_lst_of_lst
        '''
        cnt_i = 0
        cnt_s = 0
        cnt_t = 0
        for rgns in rgns_lst_st: 
            for r in rgns.rgns:
                if r.type == 'I': cnt_i += 1
                elif r.type == 'S': cnt_s += 1
                elif r.type == 'T': cnt_t += 1
        print( 'Cnt I/S/T = %i, %i, %i ' % (cnt_i, cnt_s, cnt_t) )
        '''                                        
        for r in rgns_lst_mi: r.set_cvg()
        for r in rgns_lst_nd: r.set_cvg()
        for r in rgns_lst_st: r.set_cvg()
            
        so.close()
        n_reads, n_bases, rd_len = so.num_reads, so.num_bases, so.read_len
        rd_len = so.read_len
        elapsed_time1 = time.time() - start_time2

        #'''
        if sav_rgn:
            print('Saving loci & consensus matrices .....', end='', flush = True)
            save_rgns_obj(fname + '.rgns', rgns_lst_mi, rgns_lst_nd, rgns_lst_st, so.read_len, so.num_reads, med_frag_len )
            print(' done')

        # print('.', end='')
        """
        save_rgns( fname + '_rgns_mi_%i.txt' % sa, rgns_lst_mi, so.read_len, so.num_reads )
        print('.', end='')
        """
        # save_rgns( fname + '_rgns_nd_%i.txt' % sa, rgns_lst_nd, so.read_len, so.num_reads )
        # print('.', end='')
        # save_rgns( fname + '_rgns_i_%i_ho.txt' % sa, rgns_lst_st, so.read_len, so.num_reads, ho = True )
        # print('.', end='')
        
        # save_rgns( fname + '_rgns_m_%i_ho.txt' % sa, rgns_lst_mi, so.read_len, so.num_reads, ho = True )
        # print('.', end='')
        # gtf_line_lst = get_gtf_lines( rgns_lst_mi, rgns_lst_nd )
        # save_gtf( fname+'_regions.gtf', gtf_line_lst )
        # print(' done')
        #'''
    
    else:
        print('StringFix started ', datetime.datetime.now())
        print('Loading loci & consensus matrices ...', end='')
        
        data = load_rgns_obj(fname + '.rgns')
        if len(data) == 5:
            rgns_lst_mi, rgns_lst_nd, rgns_lst_st, rd_len, n_reads = data
            med_frag_len = 300
            del data
        else:
            rgns_lst_mi, rgns_lst_nd, rgns_lst_st, rd_len, n_reads, med_frag_len = data
            del data
        print(' done.')
        
        for r in rgns_lst_mi: r.set_cvg()
        for r in rgns_lst_nd: r.set_cvg()
        for r in rgns_lst_st: r.set_cvg()
        er_code = NO_MORE_LINE
                
        elapsed_time1 = time.time() - start_time1
            
    if er_code != NO_MORE_LINE:
        print('ERROR: input alignments were NOT sorted.')
    else:
        gds = None
        if jump < 2:
            
            v_th = rd_len*min_frags_per_gene
            # if gtf is None:
            #     rgns_lst_mi, rgns_lst_nd, rgns_lst_st = filter_rgns(rgns_lst_mi, rgns_lst_nd, rgns_lst_st, v_th, s_th = MAX_PERCENT_SEC)

            gds_unmapped = None
            if gtf is not None:
                
                if genome_file is None:
                    genome = None
                else:
                    genome = load_genome(genome_file, verbose = True)

                if os.path.isfile(gtf + '.gtx'):
                    print('Loading GTFx .. ', end = ' ', flush = True)
                    with open(gtf + '.gtx', 'rb') as f:
                        (gd_lst, chrs) = pickle.load( f )
                    print('done. ')
                else:
                    gtf_lines, hdr_lines = load_gtf(gtf, verbose = True)
                    gd_lst, chrs = get_gene_descriptor(gtf_lines, genome = genome, fill = False, \
                                                                 verbose = True, n_cores = n_cores)
                    del gtf_lines
                    print('Saving GTFx .. ', end = ' ', flush = True)
                    with open(gtf + '.gtx', 'wb') as f:
                        pickle.dump( (gd_lst, chrs), f )
                    print('done. ')

                gd_lst_of_lst, chr_lst = pack_gene_descriptor( gd_lst, chrs )                   
                gds, rgns_lst_mi, rgns_lst_nd, rgns_lst_st, gds_unmapped = \
                    parse_and_combine_genes_and_rgns(gd_lst_of_lst, chr_lst, rgns_lst_mi, rgns_lst_nd, rgns_lst_st, \
                                                     n_cores = n_cores, genome = genome, verbose = True )

                #'''
                Ntrs = 0
                Ntrs2 = 0
                for gd in gds:
                    Ntrs += gd.ntr
                    for td in gd.td_lst:
                        if len(td.te_to_ge_map) > 0: Ntrs2 += 1
                print('Ntrs = %i, %i ' % (Ntrs, Ntrs2) )
                #'''
            else:
                gds = None
                gds_unmapped = None
            
            # if sav_rgn:
            #     save_rgns_obj(fname + '_selected.rgns', rgns_lst_mi, rgns_lst_nd, rgns_lst_st, rd_len, n_reads )
            
            if n_cores == 1:
                Tr_lst, Is_lst, GTF_lst, mn_lst, grp_lst, gds, ets, etx = \
                        get_transcripts( rgns_lst_mi, rgns_lst_nd, rgns_lst_st, rd_len, \
                                         gds, len_th, method, Nrec, start = Start, verbose=True )
            else:
                Tr_lst, Is_lst, GTF_lst, mn_lst, grp_lst, gds, ets, etx = \
                        get_transcripts_mc( rgns_lst_mi, rgns_lst_nd, rgns_lst_st, rd_len, \
                                            gds, n_cores, len_th, method, Nrec, start = Start, verbose=True )
            
            ets = np.array(ets, dtype = int)
            etx = np.array(etx, dtype = int)
            # print('Elapaed times: ', ets, etx)
            elapsed_time2 = time.time() - start_time1
            n_chunks = len(rgns_lst_mi)

            del rgns_lst_mi
            del rgns_lst_nd
            del rgns_lst_st

            #'''
            if gtf is not None:
                Ntrs = 0
                Ntrs2 = 0
                Ntrs3 = 0
                for gd in gds:
                    Ntrs += gd.ntr
                    for td in gd.td_lst:
                        if len(td.te_to_ge_map) > 0: Ntrs2 += 1
                        if len(td.tr_to_gr_map) > 0: Ntrs3 += 1

                    n_neg = 0
                    for td in gd.td_lst:
                        if td.abn < 0: n_neg += 1

                print('   %i, %i, %i (%i) trs from %i chuncks/genes (%i)' % (Ntrs, Ntrs2, Ntrs3, n_neg, n_chunks, int(elapsed_time2)) )

            # fname = fname + '_sa%i' % sa
            fname_tr = fname + '_transcriptome.fa'
            fname_pr = fname + '_proteome.fa'
            fname_gff = fname + '.gff'
            fname_exp = fname + '_exp_profile.tsv'
            fname_snv = fname + '_snv_summary.tsv'

            if gds is not None:
                
                t_abn = 0
                for gd in gds:
                    gd.set_cov_n_abn_th( MIN_COV_TO_SEL, MIN_ABN_TO_SEL )
                    ntr, npr, ne = gd.update_td_info()
                    t_abn += gd.get_total_abn()
                if t_abn == 0:
                    t_abn = 1
                    print('Total volume = %i' % t_abn)
                    
                nf = 1000000/t_abn
                for gd in gds:
                    gd.set_tr_info( nf )

                if gds_unmapped is not None:
                    if (MIN_COV_TO_SEL == 0) & (len(gds_unmapped) > 0): 
                        ntr = 0
                        for gd in gds_unmapped:
                            ntr += gd.ntr
                            gd.set_cov_n_abn_th( MIN_COV_TO_SEL, MIN_ABN_TO_SEL )
                            gd.update_td_info()
                        gds = gds + gds_unmapped
                        print('   %i,%i unmapped genes/trs were added.' % (len(gds_unmapped), ntr) )
                    
                gds = sort_descriptor_lst(gds)

                #'''
                start_time = time.time()
                print('Generating intermediate GFF and Transcriptome .. ', end='    ')
                gtf_lines = []
                fasta_lines = []
                fasta_lines2 = []
                cnt_none = 0

                hdr_lines = []
                hdr_lines.append('StringFix version %s' % StringFix_version )
                hdr_lines.append('Input SAM/BAM: %s' % sam_file)
                if gtf is not None: hdr_lines.append('Ref. GTF/GFF: %s' % gtf)
                hdr_lines.append('Read length: %i' % rd_len)
                
                f_gtf = save_gtf2(fname_gff, gtf_line_lst = None, hdr = hdr_lines)
                if out_tr:
                    start_time = time.time()
                    f_t = open(fname_tr, 'w+')
                    # if (gtf is None): f_p = open(fname_pr, 'w+')

                if n_cores == 1:
                    for m, gd in enumerate(gds):
                        if m%100 == 0: print('\rGenerating intermediate GTF and transcriptome .. %i/%i' % (m, len(gds)), end = '   ')
                        # ntr, npr, ne = gd.update_td_info()
                        gtfl, cn = gd.get_gtf_lines_from_exons()
                        f_gtf = save_gtf2(fname_gff, gtf_line_lst = gtfl, fo = f_gtf)

                        cnt_none += cn
                        if out_tr:
                            l1, l2 = gd.get_fasta_lines_from_exons(peptide = False)
                            f_t.writelines(''.join(l1))
                            # if (gtf is None): f_p.writelines(''.join(l2))
                else:
                    num_core = min( n_cores, (cpu_count() - 1) )
                    pool = Pool(num_core)
                    m = 1
                    for gtfl, l1, l2, ne, cn in pool.map(mc_core_get_gtf_and_fasta_pf, gds):
                        
                        if m%100 == 0: print('\rGenerating intermediate GTF and transcriptome .. %i/%i' % (m, len(gds)), end = '   ')
                        m += 1
                        f_gtf = save_gtf2(fname_gff, gtf_line_lst = gtfl, fo = f_gtf)

                        cnt_none += cn
                        if out_tr:
                            f_t.writelines(''.join(l1))
                            
                    pool.close()
                    pool.join()
            
                save_gtf2(fname_gff, gtf_line_lst = None, fo = f_gtf, close = True)
                
                if out_tr:
                    f_t.close()
                    # if (gtf is None): f_p.close()
                    
                elapsed_time2 = time.time() - start_time
                print('\rGenerating intermediate GTF and transcriptome .. %i, %i, %i done (%i)  ' \
                       % (len(fasta_lines)/2, len(gds), cnt_none, elapsed_time2))
                
                elapsed_time3 = time.time() - start_time

                print('   %s (%i)' % (fname_gff, elapsed_time3) )

                if True: # (genome_file is None) & (gtf is None)

                    nv_lst = []
                    cnt_e = 0
                    for gd in gds:
                        gd.find_snp_from_rgns()
                        nv_lst_tmp, cnt_e = gd.get_gene_level_nv_info(cnt_e)
                        nv_lst = nv_lst + nv_lst_tmp

                    if len(nv_lst) > 0:
                        df = pd.DataFrame(nv_lst)
                        df_snv = df[['chr', 'pos_ref', 'ref_seq', 'alt_seq', 'cvg_depth', 'cvg_frac', 'v_type', 'v_len', 'v_class', 'v_class_tr']]
                        df_snv.to_csv(fname_snv, sep='\t')
                        print('SNV summary saved to (PE %i) \n   %s' % (cnt_e, fname_snv))
                    else:
                        print('No SNVs found. ')
                
                td_exp_info = []
                for m, gd in enumerate(gds):
                    tis = gd.get_td_exp_info()
                    td_exp_info = td_exp_info + tis
        
                    
                df_td_exp_info = pd.DataFrame(td_exp_info)
                abn_sum = df_td_exp_info['abn'].sum()
                if abn_sum > 0:
                    nf = 1000000/abn_sum
                    df_td_exp_info['tpm'] = df_td_exp_info['abn']*nf
                
                df_td_exp_info.to_csv(fname_exp, sep='\t')
                print('Transcript expression profile saved to \n   %s' % fname_exp)

            if (gtf is None):

                Tr_lst = Tr_lst + Is_lst
                tr_sel = []
                if len(Tr_lst) > 0:
                    for tr in Tr_lst: 
                        if (len(tr.seq) >= len_th):
                            tr_sel.append(tr)

                    tr_sel = get_tpm(tr_sel)

                if len(tr_sel) > 0:

                    if TR_FILTER_SEL == 1:
                        tr_sel = filter_trs_1( tr_sel, rd_len, g_th = MIN_N_RDS_PER_GENE, abn_th_t = MIN_ABN_TO_SEL, \
                                               abn_th_i = MIN_ABN_TO_SEL, iso_frac_th = MIN_ISO_FRAC, len_th = MIN_TR_LENGTH)
                    else:
                        tr_sel = filter_trs_2( tr_sel, rd_len, g_th = MIN_N_RDS_PER_GENE, abn_th_t = MIN_ABN_TO_SEL, \
                                               abn_th_i = MIN_ABN_TO_SEL, iso_frac_th = MIN_ISO_FRAC, len_th = MIN_TR_LENGTH)

                    fname_tr = fname + '_transcriptome.fa'
                    fname_pr = fname + '_proteome.fa'
            
                    print('Saving .. ', end = '', flush = True)
                    save_transcripts2( fname_tr, tr_sel )

                    hdr_lst, tseq_lst = load_fasta1( fname_tr, verbose = False)
                    cand_cnt = len(tseq_lst)

                    lines = gen_proteome_from_trascriptome(hdr_lst, tseq_lst, len_th = MIN_PR_LENGTH, verbose = False, trareco = False)
                    p_cand_cnt = len(lines)/2
                            
                    f = open(fname_pr,'w+')
                    f.writelines(lines)
                    f.close()

                    print(' done.')
                    print('   %s' % (fname_tr) )
                    print('   %s' % (fname_pr) )
                    print('   %s' % (fname_gff) )

    # print('StringFix_analysis finished ', datetime.datetime.now())
    return fname, gds 


Gene_Tr_info = collections.namedtuple('Gene_Tr_info', 'tr_id, tr_name, gene_id, gene_name, biotype, chr, start, end, strand, coding, num_exons, tr_len' )

def build_gene_transcript_table( gtf_file ):

    gtf_lines, hdr_lines = load_gtf( gtf_file, verbose = True)
    gd_lst, chrs = get_gene_descriptor(gtf_lines, genome = None, fill = False, \
                                                              verbose = True, n_cores = 1)
    del gtf_lines

    chr_lst = list(set(chrs))
    chr_lst.sort()
    chrs = np.array(chrs)

    gt_lst = []
    for chrm in chr_lst:
        wh = which(chrs == chrm)

        s_pos = np.zeros(len(wh))
        for k in range(len(wh)): 
            s_pos[k] = gd_lst[wh[k]].begin
        odr = s_pos.argsort()

        gd_sel_ordered = [gd_lst[wh[odr[k]]] for k in range(len(wh))]

        for k, gd in enumerate(gd_sel_ordered):
            for m, td in enumerate(gd.td_lst):
                tid = td.tid
                tname = td.tname
                gid = td.gid
                gname = td.gname
                biotype = td.biotype
                start = td.begin
                end = td.end
                n_ex = td.nexons
                tlen = td.tlen
                strand = get_c_from_istrand( td.istrand )
                cds = get_str_from_icdng( td.icds )

                gte = Gene_Tr_info( tid, tname, gid, gname, biotype, chrm, start, end, strand, cds, n_ex, tlen )
                gt_lst.append(gte)

    print('\nSaving ..  ', end = '')
    df = pd.DataFrame(gt_lst)
    file_out = gtf_file + '.transcript_info.tsv'
    df.to_csv(file_out, sep = '\t')
    print('done.')

    print('Transcript info. saved to %s' % file_out)

    return gt_lst

'''
def Generate_Proteome(tr_fa, len_th = MIN_PR_LENGTH, verbose = True, mx_cnt = 0, trareco = False, fname_out = None):
    
    file_name = tr_fa.split('/')[-1]
    fns = file_name.split('.')[:-1]
    fname = ''
    for k, fn in enumerate(fns):
        if k > 0:
            fname = fname + '.'
        fname = fname + fn
    
    hdr_lst, tseq_lst = load_fasta1(tr_fa, verbose = False)
    cand_cnt = len(tseq_lst)

    lines = gen_proteome_from_trascriptome(hdr_lst, tseq_lst, len_th = len_th, verbose = verbose, trareco = trareco)
    p_cand_cnt = len(lines)/2
            
    if fname_out is None: fname_out = fname + '_proteome.fa'
    f = open(fname_out,'w+')
    f.writelines(lines)
    f.close()
                
    if verbose: 
        print('AASeq saved to %s' % (fname_out))
        
    return fname_out
'''

##########################################################################
## StringFix addon's
##########################################################################

def trim_header(fname_fa):
    
    f = open(fname_fa, 'r')
    lines = []
    cnt = 0
    for line in f:
        if line[0] == '>':
            hdr = line.split(' ')
            lines.append(hdr[0]+'\n')
        else:
            lines.append(line)
    f.close()
    
    f = open(fname_fa, 'w+')
    f.writelines(lines)
    f.close()
    
    
def trim_header_and_add_strand_info(fname_fa, gff_file):
    
    gtf_lines, hdr_lines = load_gtf(gff_file, verbose = True)
    gtf_lines_lst = parse_gtf_lines_and_split_into_genes( gtf_lines, g_or_t = 'transcript', verbose = False )    
    td_lst = []
    for lines in gtf_lines_lst:
        td = transcript_descriptor(lines)
        td_lst.append(td)
            
    f = open(fname_fa, 'r')
    lines = []
    cnt = 0
    for line in f:
        if line[0] == '>':
            hdr = line.split(' ')
            lines.append(hdr[0]+' strand:%i\n' % td_lst[cnt].strand )
            cnt += 1
        else:
            lines.append(line)
    f.close()
    
    f = open(fname_fa, 'w+')
    f.writelines(lines)
    f.close()

    if cnt == len(td_lst):
        print('FASTA file generated successfully')
    else:
        print('WARNING: %i ~= %i' % (cnt, len(td_lst)) )
        
        
def StringFix_GFFRead(gtf_file, genome_file, n_cores = 1):
    
    file_names = gtf_file.split('.')
    fname = ''.join(st for st in file_names[:-1] )
    
    gtf_lines, hdr_lines = load_gtf(gtf_file, verbose = True)
    gd_lst, chrs = get_gene_descriptor(gtf_lines, genome = None, fill = False, verbose = True, n_cores = 1)
    gd_lsts, chr_lst = pack_gene_descriptor( gd_lst, chrs )

    if genome_file is None: genome = None
    else: genome = load_genome(genome_file, verbose = True)

    fasta_lines2 = []
    fasta_lines = []
    gds = []
    for gdl in gd_lsts: gds = gds + gdl
        
    start_time = time.time()
    print('Generating transcriptome .. ', end='    ')
    cnt_tr = 0
    cnt_pr = 0
    for m, gd in enumerate(gds):
        cnt_t, cnt_p, cnt_e = gd.update_td_info(genome, sel = 2, peptide = True)
        cnt_tr += cnt_t
        cnt_pr += cnt_p
        # gd.order()
        l1, l2 = gd.get_fasta_lines_from_exons(genome, sel = 2, peptide = True)
        fasta_lines = fasta_lines + l1
        fasta_lines2 = fasta_lines2 + l2
        if m%100 == 0: print('\rGenerating transcriptome .. %i/%i (%i,%i)' % (m, len(gds), cnt_tr, cnt_pr), end='    ')
    elapsed_time = time.time() - start_time
    print('\rGenerating transcriptome .. %i done in %i(s) (%i,%i)' % (len(gds), elapsed_time, cnt_tr, cnt_pr))

    print('Saving .. %i trs, %i prs' % (len(fasta_lines)/2, len(fasta_lines2)/2) , end = '', flush = True)
    fname_tr = fname + '_transcriptome.fa'
    f = open(fname_tr, 'w+')
    f.writelines(fasta_lines)
    f.close()

    fname_pr = fname + '_proteome.fa'
    f = open(fname_pr, 'w+')
    f.writelines(fasta_lines2)
    f.close()

    print(' done.')
    print('   %s' % (fname_tr) )
    print('   %s' % (fname_pr) )

    return(fname)


##########################################################################
## StringFix-synthesis
##########################################################################

SNV_info = collections.namedtuple('SNV_info', 'chr, pos_ref, pos_new, gene_id, gene_name, v_type, v_len, cvg_depth, cvg_frac, \
                                   ref_prev, ref_seq, ref_next, alt_prev, alt_seq, alt_next') # one-base

NWIN = 3
def find_snp_old(sg, sr, cr, chrm, pos_abs, os, gin):
    
    snv_info_lst = []
    len_to_test = min(len(sr),len(sg))

    start = 0
    end = min( 100, len_to_test )
    N = int(np.ceil( len_to_test/100 ))
    #'''
    for n in range(N):
        
        if sg[start:end] != sr[start:end]:

            p = 0
            pos_lst = []
            len_lst = []
            cvg_lst = []
            snp_lst = []
            snp_org_lst = []
            
            for k in range(start, end):
                if sr[k] != sg[k]:
                    if p == 0: pos = k
                    p += 1
                else:
                    if p > 0:
                        # cvg_lst.append(np.mean( cr[pos:(pos+p)] ) )
                        # snp_lst.append(sr[pos:(pos+p)])
                        pos_lst.append(pos)
                        len_lst.append(p)
                        # snp_org_lst.append(sg[pos:(pos+p)])
                        p = 0
                    
            for k in range(len(pos_lst)):
                
                p1 = max(0,(pos_lst[k]-NWIN))
                p2 = min(len_to_test,(pos_lst[k]+len_lst[k]+NWIN))
                
                sop = sg[p1:pos_lst[k]]
                soc = sg[pos_lst[k]:(pos_lst[k]+len_lst[k])]
                son = sg[(pos_lst[k]+len_lst[k]):p2]
                
                snp = sr[p1:pos_lst[k]]
                snc = sr[pos_lst[k]:(pos_lst[k]+len_lst[k])]
                snn = sr[(pos_lst[k]+len_lst[k]):p2]
                
                si = SNV_info(chrm, pos_lst[k]+pos_abs, pos_lst[k]+pos_abs+os, gin[0], gin[1], 'V', len_lst[k], \
                              int(cr[pos_lst[k]]), 1, sop, soc, son, snp, snc, snn )
                snv_info_lst.append(si)

        start = end
        end = min( end + 100, len_to_test )
    #'''         
    return(snv_info_lst)


def find_snp(sg, sr, cmat, chrm, pos_abs, os, gin):
    
    snv_info_lst = []
    len_to_test = min(len(sr),len(sg))

    cr = cmat.sum(axis = 0)
    ns = np.argmax( cmat, axis=0 )
    pr = cmat[ns,np.arange(len(ns))]/cr

    p = 0
    pos_lst = []
    len_lst = []
    cvg_lst = []
    cfr_lst = []
    snp_lst = []
    snp_org_lst = []
    
    for k in range(len_to_test):
        if sr[k] != sg[k]:
            if p == 0: pos = k
            p += 1
        else:
            if p > 0:
                # cvg_lst.append(np.mean( cr[pos:(pos+p)] ) )
                # snp_lst.append(sr[pos:(pos+p)])
                pos_lst.append(pos)
                len_lst.append(p)
                # snp_org_lst.append(sg[pos:(pos+p)])
                p = 0
            
    for k in range(len(pos_lst)):
        
        p1 = max(0,(pos_lst[k]-NWIN))
        p2 = min(len_to_test,(pos_lst[k]+len_lst[k]+NWIN))
        
        sop = sg[p1:pos_lst[k]]
        soc = sg[pos_lst[k]:(pos_lst[k]+len_lst[k])]
        son = sg[(pos_lst[k]+len_lst[k]):p2]
        
        snp = sr[p1:pos_lst[k]]
        snc = sr[pos_lst[k]:(pos_lst[k]+len_lst[k])]
        snn = sr[(pos_lst[k]+len_lst[k]):p2]
        
        si = SNV_info(chrm, pos_lst[k]+pos_abs, pos_lst[k]+pos_abs+os, gin[0], gin[1], 'V', len_lst[k], \
                      int(cr[pos_lst[k]]), np.round(pr[pos_lst[k]],3), sop, soc, son, snp, snc, snn )
        snv_info_lst.append(si)

    return(snv_info_lst)


def compare_seq2( s1, s2 ):
    cnt = 0
    for i in range(min(len(s1),len(s2))):
        cnt += (s1[i] != s2[i])
    # if len(s1) != len(s2): print('WARNING in compare_seq2: %i != %i' % (len(s1),len(s2)) )
    return cnt


OS_info = collections.namedtuple('OS_info', 'os, start, end') # one-base

class offset_finder:
    
    def __init__(self):
        self.osi_lst = []
        self.os_map = None
        self.os_prev = 0
        
    def add( self, os, start, end):
        self.osi_lst.append( OS_info(os, start, end) )
        
    def find_os( self, pos ):
        os = 0
        for osi in self.osi_lst:
            if (pos >= osi.start) & (pos < osi.end): 
                os = osi.os
                break
        return os

    
    def find_os_seq( self, pos, prev_i, mark = '' ):
        os = None
        next_i = 0
        for k, osi in enumerate(self.osi_lst[prev_i:]):
            if (pos >= osi.start) & (pos < osi.end): 
                os = osi.os
                next_i = k + prev_i 
                break
        if os is None:
            for k, osi in enumerate(self.osi_lst[:prev_i]):
                if (pos >= osi.start) & (pos < osi.end): 
                    os = osi.os
                    next_i = k
                    break

        if os is None:
            os = self.os_prev
            # print('ERROR in find_os_seq: os is None %s' % mark )
        else:
            self.os_prev = os
            
        return os, next_i
    
    
    def make_it_compact( self ):

        for k in reversed(range(1,len(self.osi_lst))):
            if self.osi_lst[k].os == self.osi_lst[k-1].os:
                self.osi_lst[k-1] = OS_info( self.osi_lst[k-1].os, self.osi_lst[k-1].start, self.osi_lst[k].end )
                del self.osi_lst[k]
        
    def get_bndry( self, pos ):
        os = 0
        for osi in self.osi_lst:
            if (pos >= osi.start): 
                os = osi.start
                break
        return os
    
    def get_bndry_seq( self, pos, prev_i ):
        os = None
        next_i = 0
        for k, osi in enumerate(self.osi_lst[prev_i:]):
            if (pos >= osi.start) & (pos < osi.end): 
                os = osi.start
                next_i = k + prev_i 
                break
        if os is None:
            for k, osi in enumerate(self.osi_lst[:prev_i]):
                if (pos >= osi.start) & (pos < osi.end): 
                    os = osi.start
                    next_i = k
                    break
            
        if os is None:
            os = 0
            next_i = 0
            print('ERROR in get_bndry_seq: os is None')
            # self.print()
            
        return os, next_i
    
    
    def print(self):
        for osi in self.osi_lst:
            print('%i - %i: %i' % (osi.start, osi.end, osi.os))

            
def Generate_Reference(gtf_file, genome_file, peptide = True, out_dir = None, suffix = None):

    genome = load_genome(genome_file, verbose = True)

    gtf_lines, hdr_lines = load_gtf(gtf_file, verbose = True)
    gd_lst, chrs = get_gene_descriptor(gtf_lines, genome = None, fill = False, \
                                           cg = False, verbose = True, n_cores = 1)
    gd_lsts, chr_lst = pack_gene_descriptor( gd_lst, chrs )
    

    # file_name = gtf_file.split('/')[-1]
    # fns = file_name.split('.')[:-1]
    fns = gtf_file.split('.')[:-1]
    fname = ''
    for k, fn in enumerate(fns):
        if k > 0:
            fname = fname + '.'
        fname = fname + fn
    if out_dir is not None:
        if out_dir[-1] == '/':
            fname = out_dir + fname
        else:
            fname = out_dir + '/' + fname

    if suffix is None:    
        fa_file_tr = fname + '_transcriptome.fa'
        fa_file_pr = fname + '_proteome.fa'
    else:
        fa_file_tr = fname + '_%s_transcriptome.fa' % suffix
        fa_file_pr = fname + '_%s_proteome.fa' % suffix

    fa_tr = []
    fa_pr = []
    
    start_time = time.time()
    ntr = 0

    max_abn = 0
    max_cov = 0
    for kk, chrm in enumerate(chr_lst):
        for gd in gd_lsts[kk]:
            for td in gd.td_lst:
                if td.abn > 0: max_abn = max( max_abn, td.abn )
                if td.cov > 0: max_cov = max( max_cov, td.cov )

    if max_abn > 0: abn_th = MIN_ABN_TO_SEL
    else: abn_th = 0
    if max_cov > 0: cov_th = MIN_COV_TO_SEL
    else: cov_th = 0
    print('Cutoff: A = %5.2f, C = %5.2f ' % (abn_th, cov_th))

    for kk, chrm in enumerate(chr_lst):

        print('\r' + ' '*100, end='', flush = True)
        print('\rGenerating references .. %s  ' % (chrm), end = '', flush = True)

        for gd in gd_lsts[kk]:
            # gd.order()
            ntr += gd.ntr
            fa_t, fa_p = gd.get_fasta_lines_from_genome(genome, abn_th = abn_th, cov_th = cov_th, len_th_t= MIN_TR_LENGTH, len_th_p = MIN_PR_LENGTH)
            
            # fa_t = filter_trs_len(fa_t, min_len = MIN_TR_LENGTH)
            # fa_p = filter_trs_len(fa_p, min_len = MIN_PR_LENGTH)
            
            fa_tr = fa_tr + fa_t
            fa_pr = fa_pr + fa_p
            
    
    if (len(fa_pr) == 0) & (peptide):
        hdr_lst, tseq_lst = [], []
        for line in fa_tr:
            if line[0] == '>': hdr_lst.append(line[1:-1])
            else: tseq_lst.append(line[0:-1])

        fa_pr = gen_proteome_from_trascriptome(hdr_lst, tseq_lst, len_th = MIN_PR_LENGTH, verbose = True, trareco = False)
        p_cand_cnt = len(fa_pr)/2

        print('\rGenerating references .. done. %i -> %i,%i' % (ntr, len(fa_tr)/2, p_cand_cnt))
    else:
        print('\rGenerating references .. done. %i -> %i' % (ntr, len(fa_tr)/2))

    print('Saving FASTA ..', end = '', flush = True)
    f = open(fa_file_tr, 'w+')
    f.writelines(fa_tr)
    f.close()

    if peptide:
        print('.', end='')
        f = open(fa_file_pr, 'w+')
        f.writelines(fa_pr)
        f.close()

    elapsed_time = time.time() - start_time
    print(' done. (%i) ' % (elapsed_time))
    print('   %s' % fa_file_tr )
    if peptide: print('   %s' % fa_file_pr )
    
    return fa_file_tr, fa_file_pr
    

def mc_core_reconstruction(ggc_tuple):
    
    gd_sel = ggc_tuple[0]
    seq_org = ggc_tuple[1]
    chrm = ggc_tuple[2]
    
    # gd_sel = sort_descriptor_lst(gd_sel)
    n_gd = len(gd_sel)

    ###################################
    ## collect rgns and mark their pos
    
    start_time = time.time()
    loc_os = np.zeros(n_gd,dtype=np.float32)
    num_os = np.zeros(n_gd,dtype=np.float32)
    rall = regions()
    Gene_id_name = []
    gd_idx_of_rgn = []
    os_cur = 0
    r_pos = []
    for k, gd in enumerate(gd_sel):

        ## check if any D or I lies within an exon
        for e in gd.exons.rgns:
            if e.type == 'deletion':
                b = False
                for c in gd.exons.rgns:
                    if (c.type == 'exon'):
                        if e.has_ext_intersection_with(c):
                            b = True
                            break
                '''
                if b:
                    print('WARNING: D(%s:%i-%i) overlaps with E(%s:%i-%i)' % \
                          (e.chr, e.start, e.end, c.chr, c.start, c.end))
                '''    
            elif e.type == 'insersion':
                b = False
                for c in gd.exons.rgns:
                    if (c.type == 'exon'):
                        if (e.start > c.start) & (e.start < c.end):
                            b = True
                            break
                '''    
                if b:
                    print('WARNING: I(%s:%i-%i) overlaps with E(%s:%i-%i)' % \
                          (e.chr, e.start, e.end, c.chr, c.start, c.end))
                '''    

        loc_os[k] = os_cur
        num_os[k] = len(gd.exons.rgns)
        rall.rgns = rall.rgns + gd.exons.rgns
        g_id_n_name_lst = gd.get_gid_n_gname_list()
        Gene_id_name = Gene_id_name + g_id_n_name_lst
        gd_idx_of_rgn = gd_idx_of_rgn + [k]*len(gd.exons.rgns)
        os_cur += len(gd.exons.rgns)

        for r in gd.exons.rgns:
            # r_pos.append(r.end)
            r_pos.append(r.start)

    ###################################
    ## get order according to location
    r_pos = np.array(r_pos)
    odr = r_pos.argsort()

    for k, o in enumerate(odr):
        r = rall.rgns[o]
        if r.type == 'insersion':
            rp = rall.rgns[odr[k-1]]
            if (r.start == rp.start) & (rp.type == 'exon'):
                op = odr[k-1]
                odr[k-1] = odr[k]
                odr[k] = op
            else:
                rn = rall.rgns[odr[k+1]]
                if (rn.start == r.start) & (rn.type == 'exon'):
                    pass
                else:
                    print('ERROR %i: No connection found for I %i,%s-%i,%s-%i,%s' % \
                          (k, rp.start,rp.type, r.start,r.type, rn.start, rn.type) )

    elapsed_time = time.time() - start_time
    # print('   1. done (%i)  ' % (elapsed_time), flush = True)
    #'''

    #'''
    #########################################
    ## get  offset_finder and new genome seq
    
    start_time = time.time()
    of = offset_finder()
    os_cur = 0
    prev_pos = 1 # one-base
    last_pos = 1 # one-base

    seq_lst = []

    for m, k in enumerate(odr):
        r = rall.rgns[k]

        if r.type == 'exon':
            if (r.start) < (prev_pos):
                if r.end < prev_pos:
                    # print('%i WARNING (EA): %s, %i-%i <= %i, %i/%i' % (m, r.chr, r.start, r.end, prev_pos, m, len(odr)) )
                    s_org = seq_org[(r.start-1):(r.end)]
                    r.compare_and_replace_N(s_org)
                    pass
                else:
                    # print('%i WARNING (EB): %s, %i-%i <= %i' % (m, r.chr, r.start, r.end, prev_pos) )
                    s_org = seq_org[(r.start-1):(r.end)]
                    r.compare_and_replace_N(s_org)
                    sp = (prev_pos-r.start)
                    seq_lst.append(r.seq[sp:])

                    of.add( os_cur, prev_pos, r.end+1 )
                    prev_pos = r.end+1

            else:               
                s_org = seq_org[(r.start-1):(r.end)]
                #if len(s_org) == len(r.seq):
                r.compare_and_replace_N(s_org)
                # else:  print( 'WARNING: %i-%i in %i ~= %i' % (r.start, r.end, len(s_org), len(r.seq)) )

                if r.start > prev_pos:
                    seq_lst.append(seq_org[(prev_pos-1):(r.start-1)])
                    
                seq_lst.append(r.seq)
                    
                of.add( os_cur, prev_pos, r.end+1 )
                prev_pos = r.end+1
                    
                if len(r.seq) != len(s_org):
                    # print( 'WARNING: %s: %i-%i in %i ~= %i' % (r.chr, r.start, r.end, len(s_org), len(r.seq)) )
                    # seq_lst.append(s_org)
                    # r.seq = region(r.chr, r.start, r.end, r.type, s_org, cvg_dep = CVG_DEPTH_TMP )
                    # r.get_cvg()
                    pass
                    

        elif (r.type == 'insersion') | (r.type == 'I' ):
            if (r.start) < (prev_pos):
                # print('WARNING (I): %i - %s, %i < %i' % (m, r.chr, r.start, prev_pos) )
                pass
            else:
                of.add( os_cur, prev_pos, r.start )
                os_cur += (r.end - r.start + 1)

                if r.start > prev_pos:
                    seq_lst.append(seq_org[(prev_pos-1):(r.start-1)])
                seq_lst.append(r.seq)

                prev_pos = r.start

        elif (r.type == 'deletion') | (r.type == 'D' ):
            if (r.start) < (prev_pos):
                # print('WARNING (D): %i - %s, %i <= %i' % (m, r.chr, r.start, prev_pos) )
                pass
            else:
                of.add( os_cur, prev_pos, r.start )
                os_cur -= (r.end - r.start + 1)
                prev_pos = r.start

                of.add( os_cur, prev_pos, r.end+1 )
                prev_pos = r.end+1

        last_pos = r.end

    seq_lst.append(seq_org[(prev_pos-1):])
    seq_new = ''.join(seq_lst)

    # if last_pos > prev_pos:
    of.add( os_cur, prev_pos, len(seq_org) + 100000 )

    elapsed_time = time.time() - start_time
    # print('   2. done (%i)  ' % (elapsed_time), flush = True)
    #'''

    ########################################################
    ## Use offset_finder to correct positions in GTF entries
    ## also get rgns fragments when split is required

    of.make_it_compact()
    
    start_time = time.time()
    r_to_add = []
    pos_to_add = []
    snv_info_chr = []

    for gd in gd_sel:
        gd.nv_info_lst = []

    prev_ofi = 0
    v_cnt = 0
    #for k, r in enumerate(rall.rgns):
    for m, k in enumerate(odr):
        r = rall.rgns[k]
        gin = Gene_id_name[k]
        
        oss, prev_of1 = of.find_os_seq(r.start, prev_ofi)
        # ose = oss
        ose, prev_of2 = of.find_os_seq(r.end, prev_ofi)
 
        r.get_cvg()
        # if r.cvg is None: r.cvg = np.ones(len(r.seq))

        if r.type == 'exon':
            
            if (oss == ose):

                # si_lst = find_snp(seq_org[(r.start-1):r.end], r.seq, r.get_cvg(), chrm, r.start, oss)
                si_lst = find_snp(seq_org[(r.start-1):r.end], r.seq, r.cmat, chrm, r.start, oss, gin)
                snv_info_chr = snv_info_chr + si_lst
                gd_idx = gd_idx_of_rgn[k]
                gd_sel[gd_idx].nv_info_lst = gd_sel[gd_idx].nv_info_lst + si_lst

                r.start += oss
                r.end += ose
                rall.rgns[k] = r # .copy()


            elif (oss < ose): # Insersion in between

                print('   %i oss < ose' % k)
                # r.print_short()
                p, prev_of2 = of.get_bndry_seq(ose, prev_ofi)

                ## split
                Lr = r.end - r.start +1
                Ln = r.end - p + 1
                rgn_new = region( r.chr, p+ose, r.end+ose, r.type, r.cmat[:,-Ln:], xs = r.xs)
                rgn_new.get_cvg()
                r_to_add.append(rgn_new)
                pos_to_add.append(k+1)

                # si_lst = find_snp(seq_org[(p-1):r.end], rgn_new.seq, rgn_new.get_cvg(), chrm, p, ose)
                si_lst = find_snp(seq_org[(p-1):r.end], rgn_new.seq, rgn_new.cmat, chrm, p, ose, gin)
                snv_info_chr = snv_info_chr + si_lst
                gd_idx = gd_idx_of_rgn[k]
                gd_sel[gd_idx].nv_info_lst = gd_sel[gd_idx].nv_info_lst + si_lst

                r.end = p-1+oss
                r.start += oss
                Ln = r.end - r.start +1
                r.cmat = r.cmat[:,:Ln]
                r.seq = r.seq[:Ln]
                r.cvg = r.cvg[:Ln]
                # r.get_cvg()
                rall.rgns[k] = r # .copy()

                # si_lst = find_snp(seq_org[(r.start-oss-1):p], r.seq, r.get_cvg(), chrm, r.start-oss, oss)
                si_lst = find_snp(seq_org[(r.start-oss-1):p], r.seq, r.cmat, chrm, r.start-oss, oss, gin)
                snv_info_chr = snv_info_chr + si_lst
                gd_idx = gd_idx_of_rgn[k]
                gd_sel[gd_idx].nv_info_lst = gd_sel[gd_idx].nv_info_lst + si_lst

            elif (oss > ose): # deletion in between

                print('   %i oss > ose' % k)
                # r.print_short()
                p, prev_of2 = of.get_bndry_seq(ose, prev_ofi)
                Ld = oss - ose

                ## split (for CDS only)
                Lr = r.end - r.start +1
                Ln = r.end - p + 1 - Ld
                rgn_new = region( r.chr, p+Ld+ose, r.end+ose, r.type, r.cmat[:,-Ln:], xs = r.xs)
                rgn_new.get_cvg()
                r_to_add.append(rgn_new)
                pos_to_add.append(k+1)

                # si_lst = find_snp(seq_new[(rgn_new.start-1):rgn_new.end], rgn_new.seq, rgn_new.get_cvg(), chrm, p, ose)
                si_lst = find_snp(seq_new[(rgn_new.start-1):rgn_new.end], rgn_new.seq, rgn_new.cmat, chrm, p, ose, gin)
                snv_info_chr = snv_info_chr + si_lst
                gd_idx = gd_idx_of_rgn[k]
                gd_sel[gd_idx].nv_info_lst = gd_sel[gd_idx].nv_info_lst + si_lst

                r.end = p-1+oss
                r.start += oss
                Ln = r.end - r.start +1
                r.cmat = r.cmat[:,:Ln]
                r.seq = r.seq[:Ln]
                r.cvg = r.cvg[:Ln]
                # r.get_cvg()
                rall.rgns[k] = r # .copy()

                # si_lst = find_snp(seq_org[(r.start-oss-1):p], r.seq, r.get_cvg(), chrm, r.start-oss, oss)
                si_lst = find_snp(seq_org[(r.start-oss-1):p], r.seq, r.cmat, chrm, r.start-oss, oss, gin)
                snv_info_chr = snv_info_chr + si_lst
                gd_idx = gd_idx_of_rgn[k]
                gd_sel[gd_idx].nv_info_lst = gd_sel[gd_idx].nv_info_lst + si_lst
                
        elif r.type == 'insersion':

            ossp, prev_of1 = of.find_os_seq(r.start-1, prev_ofi, mark = 'I')

            sop = seq_org[int(r.start-(NWIN+1)):int(r.start-1)]
            soc = '-'
            son = seq_org[int(r.start-1):int(r.start+(NWIN-1))]
            
            snp = seq_new[int(r.start+ossp-(NWIN+1)):int(r.start+ossp-1)]
            snc = r.seq
            snn = seq_new[int(r.start+oss-1):int(r.start+oss+(NWIN-1))]
            si = SNV_info(chrm, r.start, r.start+oss, gin[0], gin[1], 'I', r.get_len(), int(r.ave_cvg_depth()), r.cvg_frac, sop, soc, son, snp, snc, snn )
            snv_info_chr.append(si)
            gd_idx = gd_idx_of_rgn[k]
            gd_sel[gd_idx].nv_info_lst.append(si)

            r.start += ossp
            r.end += ossp  
            rall.rgns[k] = r # .copy()

        elif r.type == 'deletion':

            ossp, prev_of1 = of.find_os_seq(r.start-1, prev_ofi, mark = 'D')

            sop = seq_org[int(r.start-(NWIN+1)):int(r.start-1)]
            soc = seq_org[int(r.start-1):int(r.end)]
            son = seq_org[int(r.end):int(r.end+(NWIN))]
            
            # sop = rall.rgns[odr[m-1]].seq[-NWIN:]
            snp = seq_new[int(r.start+ossp-(NWIN+1)):int(r.start+ossp-1)]
            snc = '-'
            # son = rall.rgns[odr[m+1]].seq[:NWIN]
            snn = seq_new[int(r.start+ossp-1):int(r.start+ossp+(NWIN-1))]
            si = SNV_info(chrm, r.start, r.start+oss, gin[0], gin[1], 'D', r.get_len(), int(r.ave_cvg_depth()), r.cvg_frac, sop, soc, son, snp, snc, snn )
            snv_info_chr.append(si)
            gd_idx = gd_idx_of_rgn[k]
            gd_sel[gd_idx].nv_info_lst.append(si)

            r.start += ossp
            r.end += ossp   
            rall.rgns[k] = r # .copy()

        prev_ofi = prev_of1

    elapsed_time = time.time() - start_time
    # print('   3. done (%i)  %i' % (elapsed_time, len(of.osi_lst)), flush = True)
    
    nv_lst = []
    cnt_e = 0
    for gd in gd_sel:
        for td in gd.td_lst:
            td.get_org_coding_seq( gd.cds.rgns, seq_org )
        nv_lst_tmp, cnt_e = gd.get_gene_level_nv_info(cnt_e)
        nv_lst = nv_lst + nv_lst_tmp
    snv_info_chr = nv_lst
                
    ##########################
    ## put rgns back to gd_sel
    ## and also add new rgns 

    start_time = time.time()
    pos_to_add = np.array(pos_to_add)
    for k, gd in enumerate(gd_sel): 

        p1 = int(loc_os[k])
        p2 = int(p1 + num_os[k])
        # gd.exons.rgns = rall.rgns[p1:p2]
        gd.exons.rgns = [rall.rgns[p1+m] for m in range(p2-p1)]
        wh = which( (pos_to_add >= p1) & (pos_to_add < p2) )
        if len(wh) > 0:
            for w in wh: gd.exons.rgns.append(r_to_add[w])

    #######################
    ## remove ideletion 
    ## combine tiled exons
    
    for gd in gd_sel:
        gd.remove_indel_and_combine_frags()

    #'''
    elapsed_time = time.time() - start_time
    # print('   3b. done (%i)  ' % (elapsed_time), flush = True)
    

    ########################
    ########################
    ## coding region update

    start_time = time.time()
    
    ## collect rgns and mark their pos
    loc_os = np.zeros(n_gd)
    num_os = np.zeros(n_gd,dtype=np.float32)
    call = regions()
    os_cur = 0
    c_pos = []
    for k, gd in enumerate(gd_sel):
        loc_os[k] = os_cur
        num_os[k] = len(gd.cds.rgns)
        call.rgns = call.rgns + gd.cds.rgns
        os_cur += len(gd.cds.rgns)

        for r in gd.cds.rgns:
            c_pos.append(r.start)

    ## get order according to location
    c_pos = np.array(c_pos)
    odr = c_pos.argsort()

    ########################################################
    ## Use offset_finder to correct positions in GTF entries
    ## also get rgns fragments when split is required

    c_to_add = []
    pos_to_add = []

    prev_ofi = 0
    # for k, r in enumerate(call.rgns):
    for m, k in enumerate(odr):
        r = call.rgns[k]
        
        # oss = of.find_os(r.start)
        # ose = of.find_os(r.end)
        oss, prev_of1 = of.find_os_seq(r.start, prev_ofi, mark = 'B')
        ose, prev_of2 = of.find_os_seq(r.end, prev_ofi, mark = 'C')
        prev_ofi = prev_of1

        if (r.type.lower() == 'start_codon') | (r.type.lower() == 'stop_codon'):
            r.start += oss
            r.end += oss   
            call.rgns[k] = r.copy(update=False)

        else:  # CDS, five_prime_utr, three_prime_utr, ...
            if (oss == ose):
                r.start += oss
                r.end += ose
                call.rgns[k] = r.copy(update=False)

            elif (oss < ose): # Insersion or deletion in between

                # print('   %i oss < ose' % k)
                p, prev_of2 = of.get_bndry_seq(r.end, prev_ofi)

                ## split
                rgn_new = region( r.chr, p+ose, r.end+ose, r.type, xs = r.xs)
                c_to_add.append(rgn_new)
                pos_to_add.append(k+1)

                r.end = p-1+oss
                r.start += oss
                call.rgns[k] = r.copy(update=False)

            elif (oss > ose): # deletion in between

                # print('   %i oss > ose' % k)
                p, prev_of2 = of.get_bndry_seq(r.end, prev_ofi)
                Ld = oss - ose

                ## split (for CDS only)
                rgn_new = region( r.chr, p+Ld+ose, r.end+ose, r.type, xs = r.xs)
                c_to_add.append(rgn_new)
                pos_to_add.append(k+1)

                r.end = p-1+oss
                r.start += oss
                call.rgns[k] = r.copy(update=False)

    ##########################
    ## put rgns back to gd_sel
    ## and also add new rgns 

    pos_to_add = np.array(pos_to_add)
    for k, gd in enumerate(gd_sel): 

        p1 = int(loc_os[k])
        p2 = int(p1 + num_os[k])
        gd.cds.rgns = [call.rgns[p1+m] for m in range(p2-p1)]
        wh = which( (pos_to_add >= p1) & (pos_to_add < p2) )
        if len(wh) > 0:
            for w in wh: gd.cds.rgns.append(c_to_add[w])

    elapsed_time = time.time() - start_time
    # print('   4. done (%i)  ' % (elapsed_time), flush = True)
    
    ########################
    ## coding region update
    ########################

    ########################
    ## Integrity check
    
    start_time = time.time()
    n_bases_total = 0
    n_er_bases = 0
    n_blk_total = 0
    n_er_blk = 0
    npe = 0
    npt = 0
    for gd in gd_sel:
        for r in gd.exons.rgns:
            if r.type != 'deletion':
                s1 = r.seq
                s2 = seq_new[(r.start-1):r.end] # genome[r.chr].seq[(r.start-1):r.end]
                n_er = compare_seq2( s1, s2 )
                # if n_er > 0: print('\nS1: %s\nS2: %s' % (s1,s2))
                    
                n_bases_total += len(s1)
                n_er_bases += n_er
                n_blk_total += 1
                if n_er > 0: n_er_blk += 1
                    
        ntr, npr, ner = gd.update_td_info(sel = 1, peptide = True)
        ne, nt = gd.compare_seqs_from_cds_and_genome(seq_new) # genome[gd.chr].seq)
        npe += ne
        npt += nt

        # if ner > 0: print('Integrity check error A in %s: %i - %i/%i, %i/%i, %i/%i' % (chrm, ner, n_er_bases, n_bases_total, n_er_blk, n_blk_total, npe, npt) )
        # if n_er > 0: print('Integrity check error in %s: %i - %i/%i, %i/%i, %i/%i' % (chrm, n_er, n_er_bases, n_bases_total, n_er_blk, n_blk_total, npe, npt) )

    elapsed_time = time.time() - start_time
    # print('   5. done (%i)  ' % (elapsed_time), flush = True)
    
    estat = (n_bases_total, n_er_bases, n_blk_total, n_er_blk, npt, npe)
    
    return gd_sel, seq_new, snv_info_chr, of, chrm, estat

'''
NV_info_ext_tr = collections.namedtuple('NV_info_ext_tr', 'chr, pos_ref, pos_new, gene_id, gene_name, v_type, v_len, cvg_depth, cvg_frac, \
                                  ref_prev, ref_seq, ref_next, alt_prev, alt_seq, alt_next, v_class, \
                                  v_class_tr, strand, cDNA_change, Codon_change, Protein_change, Protein_change2, Check')  # one-base

def write_to_vcf( snv_info_lst, file_name ):

    if len(snv_info_lst) == 0:
        return
    
    if len(snv_info_lst[0]) <= 20:
        pass
    else:
        f = open( fname_vcf, 'wt+' )

        lines = ['#CHROM\tPOS\tID\tREF\tALT\tQUAL\tFILTER\tINFO']
        for ni in snv_info_lst:
            mid =
            Qual =
            Filter =
            info = 'AC=%i;AF'
            '%s\t%i\t%s\t%s\t%s\t%i\t%s\t%s\n' % (ni.chr, ni.pos_ref, mid, ni.ref_seq, ni.alt_seq, Qual, info)

        f.close()
        
    return
'''

def mc_core_get_gtf_and_fasta_pt(gd):
    
    ntr, npr, ner = gd.update_td_info(sel = 1, peptide = True)
    gtf_line, cn = gd.get_gtf_lines_from_exons(sel = 1, add_seq = False, connect = True)
    lt, lp = gd.get_fasta_lines_from_exons(sel = 1, peptide = True)
    return gtf_line, lt, lp, gd.chr, ner, cn


'''
NV_info_ext_tr = collections.namedtuple('NV_info_ext_tr', 'chr, pos_ref, pos_new, gene_id, gene_name, v_type, v_len, cvg_depth, cvg_frac, \
                                  ref_prev, ref_seq, ref_next, alt_prev, alt_seq, alt_next, v_class, \
                                  v_class_tr, strand, cDNA_change, Codon_change, Protein_change, Protein_change2') #, Check')  # one-base
'''

NV_info_tr = collections.namedtuple('NV_info_ext_tr', 'chr, pos_ref, gene_name, gene_id, v_type, v_len, \
                                  cvg_depth, cvg_frac, ref_seq, alt_seq, \
                                  strand, cDNA_change, Codon_change, Protein_change, Protein_change2, v_class') 

def to_nv_simple( nv ):

    nvi = NV_info_tr( nv.chr, nv.pos_ref, nv.gene_name, nv.gene_id, nv.v_type, nv.v_len, \
                                nv.cvg_depth, nv.cvg_frac, nv.ref_seq, nv.alt_seq, \
                                nv.strand, nv.cDNA_change, nv.Codon_change, \
                                nv.Protein_change, nv.Protein_change2, nv.v_class_tr )
    return nvi

def StringFix_synthesis(gtf_file, genome_file, rev = True, n_cores = 1, out_dir = None, gds = None):

    # print('StringFix_synthesis started ', datetime.datetime.now())
    
    if isinstance(genome_file, str):
        genome = load_genome(genome_file, verbose = True)
    else:
        genome = genome_file

    if gds is None:
        gtf_lines, hdr_lines = load_gtf(gtf_file, verbose = True)
        gd_lst, chrs = get_gene_descriptor(gtf_lines, genome = None, fill = True, \
                                               cg = True, verbose = True, n_cores = 1)
        gd_lsts, chr_lst = pack_gene_descriptor( gd_lst, chrs )
        
        for gdl in gd_lsts: 
            for m, gd in enumerate(gdl):
                gd.set_cov_n_abn_th( MIN_COV_TO_SEL, MIN_ABN_TO_SEL )

        ntr_valid = 0
        ggc_tuple = []
        chr_lst_new = []
        for kk, chrm in enumerate(chr_lst):
            if chrm in genome.keys():
                chr_lst_new.append(chrm)
                ggc_tuple.append( (gd_lsts[kk], genome[chrm].seq, chrm) )
                for gd in gd_lsts[kk]:
                    ntr_valid += gd.ntr
        # print('N_trs valid = %i' % ntr_valid)
        del gd_lsts

    else:
        gtf_lines, hdr_lines = load_gtf(gtf_file, verbose = False, ho = True)

        fm = {'M': 'exon', 'I': 'insersion', 'D': 'deletion'}
        for m, gd in enumerate(gds):
            gd.set_cov_n_abn_th( MIN_COV_TO_SEL, MIN_ABN_TO_SEL )
            if (len(gd.rgns.rgns) > 0):
                gd.exons.rgns, gd.rgns.rgns = gd.rgns.rgns, gd.exons.rgns
                gd.te_to_ge_maps, gd.tr_to_gr_maps = gd.tr_to_gr_maps, gd.te_to_ge_maps
                
            for r in gd.exons.rgns:
                if r.type in fm.keys():
                    r.type = fm[r.type]

        chrs = []
        for gd in gds: 
            chrs.append(gd.chr)

        chr_lst = list(set(chrs))
        chr_lst.sort()
        chrs = np.array(chrs)

        ntr_valid = 0
        ggc_tuple = []
        chr_lst_new = []
        for kk, chrm in enumerate(chr_lst):
            if chrm in genome.keys():
                wh = which(chrs == chrm)
                if len(wh) > 0:
                    s_pos = np.zeros(len(wh),dtype=np.float32)
                    for k in range(len(wh)): 
                        s_pos[k] = gds[wh[k]].begin
                        ntr_valid += gd.ntr
                    odr = s_pos.argsort()

                    chr_lst_new.append(chrm)
                    ggc_tuple.append( ([ gds[wh[odr[k]]] for k in range(len(wh)) ], genome[chrm].seq, chrm) )

        # print('N_trs valid = %i' % ntr_valid)
        del gds


    file_name = gtf_file.split('/')[-1]
    # fname = file_name.split('.')[0]
    fns = file_name.split('.')[:-1]
    fname = ''
    for k, fn in enumerate(fns):
        if k > 0:
            fname = fname + '.'
        fname = fname + fn

    if out_dir is not None:
        if out_dir[-1] == '/':
            fname = out_dir + fname
        else:
            fname = out_dir + '/' + fname

    genome_file_new = fname + '_customized_genome.fa'
    gtf_file_new = fname + '_customized.gtf'
    fa_file_tr_new = fname + '_transcriptome.fa'
    fa_file_pr_new = fname + '_proteome.fa'
    fname_snv = fname + '_snv_summary.tsv'
    fname_vcf = fname + '_snv_summary.vcf'

    ######################################################
    chr_lst = chr_lst_new

    of_dict = {}
    # gds_lst = []
    # snv_lst = []
    gds_new = []
    snv_info_lst = []

    n_bases_total = 0
    n_er_bases = 0
    n_blk_total = 0
    n_er_blk = 0
    npt = 0
    npe = 0
    
    start_time = time.time()
    if (n_cores == 1) | (len(chr_lst) == 1):
        for kk in range(len(chr_lst)):
            print('\r' + ' '*100, end='', flush = True)
            print('\rReconstructing .. %i/%i (%s) ' % (kk+1, len(chr_lst), chr_lst[kk]), end = '', flush = True)
            gd_sel, seq_new, snv_info_chr, of, chrm, estat = mc_core_reconstruction(ggc_tuple[kk])
            ##########################
            genome[chrm].seq = seq_new
            of_dict[chrm] = of
            # gds_lst.append(gd_sel)
            # snv_lst.append(snv_info_chr)
            gds_new = gds_new + gd_sel
            snv_info_lst = snv_info_lst + snv_info_chr

            nbt, nbe, nlt, nle, nt, ne= estat
            n_bases_total += nbt
            n_er_bases += nbe
            n_blk_total += nlt
            n_er_blk += nle
            npt += nt
            npe += ne
            ##########################
    else:
        num_core = min( n_cores, (cpu_count() - 1) )
        # print("num cores to use = {}".format(num_core))
        pool = Pool(num_core)
        cnt = 1
        for gd_sel, seq_new, snv_info_chr, of, chrm, estat in \
            pool.imap_unordered(mc_core_reconstruction, ggc_tuple):
            # tqdm.tqdm_notebook(pool.imap_unordered(mc_core_reconstruction, ggc_tuple), total=len(ggc_tuple)):
            ##########################
            genome[chrm].seq = seq_new
            of_dict[chrm] = of
            # gds_lst.append(gd_sel)
            # snv_lst.append(snv_info_chr)
            gds_new = gds_new + gd_sel
            snv_info_lst = snv_info_lst + snv_info_chr
            
            nbt, nbe, nlt, nle, nt, ne= estat
            n_bases_total += nbt
            n_er_bases += nbe
            n_blk_total += nlt
            n_er_blk += nle
            npt += nt
            npe += ne
            ##########################
            cnt += 1
            print('\rReconstructing (%i) .. %i/%i (%s)            ' % (num_core, cnt, len(ggc_tuple), chrm), end = '                     ')
            
        pool.close()
        pool.join()
        
    '''
    gds_new = []
    snv_info_lst = []
    for kk, chrm in enumerate(chr_lst):
        gds_new = gds_new + gds_lst[kk]
        snv_info_lst = snv_info_lst + snv_lst[kk]

    del gds_lst
    #'''
     
    elapsed_time2 = time.time() - start_time
    print('\rReconstruction .. done. (%i)            ' % (elapsed_time2), flush = True)
    print('Integrity check:  %i/%i, %i/%i, %i/%i' % \
          (n_er_bases, n_bases_total, n_er_blk, n_blk_total, npe, npt), flush = True )
      
    '''  
    Ntr_all = 0
    for gd in gds_new: Ntr_all += gd.ntr
    print('N_tr (after) = %i' % Ntr_all)

    n_tr = 0
    n_neg_cov = 0
    n_pos_cov = 0
    for gd in gds_new:
        n_tr += gd.ntr
        for td in gd.td_lst:
            if td.cov <= 0: n_neg_cov += 1
            elif td.cov > 0: n_pos_cov += 1
    print('N_trs = %i, %i, %i' % (n_tr, n_neg_cov, n_pos_cov))
    #'''
        
    start_time = time.time()
    gtf_lines = []
    fa_lines_tr = []
    fa_lines_pr = []

    # save_gtf2( fname, gtf_line_lst = None, hdr = None, fo = None close = False )
    
    if rev: 
        hdr_lines.append('Ref. genome: %s' % genome_file)
        f_gtf = save_gtf2( gtf_file_new, gtf_line_lst = None, hdr = hdr_lines )

    ft = open(fa_file_tr_new, 'w+')
    fp = open(fa_file_pr_new, 'w+')

    gds_new = sort_descriptor_lst(gds_new)
    cnt_none = 0
    print('Generating GTF and Transcriptome/Proteome .. ', end='    ')

    if n_cores == 1:
        cnt_t = 0
        cnt_p = 0
        for m, gd in enumerate(gds_new):
            
            if (m+1)%100 == 0: print('\rGenerating GTF and Transcriptome/Proteome .. %i/%i' % (m, len(gds_new)), end = '   ', flush = True)
            ntr, npr, ner = gd.update_td_info(sel = 1, peptide = True)            
            gtfl, cn = gd.get_gtf_lines_from_exons(sel = 1, add_seq = False, connect = True)
            cnt_none += cn
            lt, lp = gd.get_fasta_lines_from_exons(sel = 1, peptide = True)
            lt = filter_trs_len(lt, min_len = MIN_TR_LENGTH)
            lp = filter_trs_len(lp, min_len = MIN_PR_LENGTH)
            if rev:
                f_gtf = save_gtf2( gtf_file_new, gtf_line_lst = gtfl, fo = f_gtf ) 
                # gtf_lines = gtf_lines + gtfl
        
            ft.writelines(lt)
            fp.writelines(lp)
            # fa_lines_tr = fa_lines_tr + lt
            # fa_lines_pr = fa_lines_pr + lp
            cnt_t += len(lt)
            cnt_p += len(lp)
            
        elapsed_time2 = time.time() - start_time
        print('\rGenerating GTF and Transcriptome/Proteome .. %i, %i done. (%i) ' % (len(gds_new), cnt_none, elapsed_time2), flush = True)

    else:
        num_core = min( n_cores, (cpu_count() - 1) )
        # print("num cores to use = {}".format(num_core))
        pool = Pool(num_core)
        cnt = 1
        cnt_t = 0
        cnt_p = 0
        for gtfl, lt, lp, chrm, ne, cn in pool.map(mc_core_get_gtf_and_fasta_pt, gds_new):
            
            cnt_none += cn
            if (cnt+1)%100 == 0:
                print('\rGenerating GTF and Transcriptome/Proteome .. %i/%i' % (cnt, len(gds_new)), end = '   ')
                pass
            cnt += 1
            
            lt = filter_trs_len(lt, min_len = MIN_TR_LENGTH)
            lp = filter_trs_len(lp, min_len = MIN_PR_LENGTH)
            if rev:
                f_gtf = save_gtf2( gtf_file_new, gtf_line_lst = gtfl, fo = f_gtf )  
                # gtf_lines = gtf_lines + gtfl

            ft.writelines(lt)
            fp.writelines(lp)
            # fa_lines_tr = fa_lines_tr + lt
            # fa_lines_pr = fa_lines_pr + lp
            cnt_t += len(lt)
            cnt_p += len(lp)
            
        pool.close()
        pool.join()

        elapsed_time2 = time.time() - start_time
        print('\rGenerating GTF and Transcriptome/Proteome .. done. %i, %i, %i (%i) ' % \
              (cnt_none, int(cnt_t/2), int(cnt_p/2), elapsed_time2))
        
    if rev: save_gtf2( gtf_file_new, gtf_line_lst = None, fo = f_gtf, close = True )
    ft.close()
    fp.close()

    # del gds_new

    '''    
    start_time = time.time()
    print('Saving FASTA (%i, %i / %i) ..' % (len(fa_lines_tr)/2, len(fa_lines_pr)/2, n_tr), end = '', flush = True)
    f = open(fa_file_tr_new, 'w+')
    f.writelines(fa_lines_tr)
    f.close()

    print('.', end='')
    f = open(fa_file_pr_new, 'w+')
    f.writelines(fa_lines_pr)
    f.close()

    elapsed_time = time.time() - start_time
    print(' done. (%i)' % (elapsed_time))
    '''

    print('   %s' % fa_file_tr_new )
    print('   %s' % fa_file_pr_new )
    if rev: print('   %s' % gtf_file_new)

    snv_lst = []
    for snv in snv_info_lst:
        nvi = to_nv_simple( snv )
        snv_lst.append(nvi)

    if len(snv_lst) > 0:
        df_snv = pd.DataFrame(snv_lst)
        df_snv.to_csv(fname_snv, sep = '\t')
        print('SNV summary saved to \n   %s' % fname_snv)
    else:
        print('No SNVs found. ')
        
    # write_to_vcf( snv_info_lst, fname_vcf )

    #'''    
    if rev:
        start_time = time.time()
        '''
        print('Saving customized genome .. ', end = '', flush = True)
        
        # hdr_lines.append('Ref. genome: %s' % genome_file)
        # save_gtf(gtf_file_new, gtf_lines, hdr_lines)
        
        elapsed_time = time.time() - start_time
        print(' done. %i(s) \n   %s' % (elapsed_time, gtf_file_new))
        '''
        ## Save genome corrected
        print('You are almost done. \nLast step is to save the fixed genome. ')
        save_genome( genome_file_new, genome, verbose = True, title = 'Genome-rev' )
        print('   %s' % genome_file_new )

    print('StringFix finished ', datetime.datetime.now())

    return fname, genome_file_new #, gds_new
    #'''    

def StringFix_assemble( Input = None, genome_fa = None, annot_gtf = None, out_dir = 'SFix_out', \
                        n_cores = 4, out_custom_genome = False, suffix = None, \
                        mcv = 0.5, mcd = 1, mtl = 200, mpl = 50, mdi = 2, mdd = 2, mdp = 3, \
                        mdf = 0.2, n_p = 16, xsa = True, jump_to = 0 ):

    print('+------------------------------+')
    print('|      Stringfix v.%s       |' % StringFix_version)
    print('+------------------------------+')

    if Input is None:
        print('Usage:')
        print('%12s: ' % 'argument', 'description' )
        print('%12s: ' % 'Input', 'Input SAM or BAM file. pybam.py is required for BAM input.' )
        print('%12s: ' % 'genome_fa', end = '')
        print(' Genome fasta file used to generate the input SAM/BAM. ' )
        print('%12s   It is used to correct sequences not covered by reads, ' % '')
        print('%12s   to identify SNPs and to generate customized genome. '  % '')
        print('%12s: ' % 'annot_gtf', 'GTF/GFF file to be used for guide annotation' )
        print('%12s: ' % 'out_dir', 'Output directory' )
        print('%12s: ' % 'n_cores', 'Number of cores to use' )
        print('%12s: ' % 'suffix', 'Suffix to be used for output file names' )
        print('%12s: ' % 'mcv', 'Minimum read coverage for inclusion in the output GTF/GFF' )
        print('%12s   and transcriptome/proteome [0~1]. For a length L transcript, ' % '')
        print('%12s   it will be included in the output if at least mcv*L bases are covered by reads '  % '')
        print('%12s: ' % 'mcd', 'Minimum base coverage depth for inclusion in the output' )
        print('%12s: ' % 'mtl', 'Minimum transcript length in bases' )
        print('%12s: ' % 'mpl', 'Minimum protein (amino acid sequence) length' )
        print('%12s: ' % 'mdi', 'Minimum coverage depth for an insersion to be considered valid [>=1.0]' )
        print('%12s: ' % 'mdd', 'Minimum coverage depth for a deletion to be considered valid [>=1.0]' )
        print('%12s: ' % 'mdp', 'Minimum coverage depth for SNP correction [>=1.0]' )
        print('%12s: ' % 'mdf', 'Minimum coverage depth fraction for insersion and deletion to be considered valid (0~1)' )
        print('%12s: ' % 'jump_to', 'Jump to step j [0 or 1 or 2]' )
        return

    sam_file = Input
    gtf_file = annot_gtf

    if PYBAM_ERR:
        print('StringFix WARNING: pybam not available. Accept SAM file only.')

    if (genome_fa is not None) & (gtf_file is not None):
        print('StringFix is running in annotation guided mode with sequence correction.')
    elif (genome_fa is not None) & (gtf_file is None):
        print('StringFix is running in genome guided mode with sequence correction.')
    elif (genome_fa is None) & (gtf_file is None):
        print('StringFix is running in genome guided mode without sequence correction.')
    else:
        print('StringFix is running in annotation guided mode without sequence correction.')
    

    # rev = False
    rev = out_custom_genome
    cbyc = True 
    sa = 2
    if xsa: sa = 0

    MIN_CVG_FOR_SNP_CORRECTION = int(mdp)
    I_VALID_CVG = max(1, np.float(mdi))
    D_VALID_CVG = max(1, np.float(mdd))
    I_VALID_CFRAC = float(mdf)
    D_VALID_CFRAC = float(mdf)
    MIN_COV_TO_SEL = np.float(mcv)
    MIN_ABN_TO_SEL = np.float(mcd)
    MIN_TR_LENGTH = int(mtl)
    MIN_PR_LENGTH = int(mpl)
    MAX_NUM_PATHS = int(n_p)
    GEN_AAS_UNSPEC = True

    if gtf_file is None:
        MAX_NUM_PATHS = 20
        MIN_N_RDS_PER_GENE = 30
        TR_FILTER_SEL = 2

    if out_dir is not None: 
        if not os.path.exists(out_dir): os.mkdir(out_dir)

    file_out, gds, genome = StringFix_analysis(sam_file, gtf = gtf_file, genome_file = genome_fa, jump = jump_to, \
            n_cores=n_cores, out_tr = True, cbyc = cbyc, suffix = suffix, out_dir = out_dir, sa = sa ) 

    if (gds is not None) & (jump_to < 2):
        print('Saving gene descriptor .. ', end = ' ', flush = True)
        with open(file_out + '.gds', 'wb') as f:
            pickle.dump( (gds), f )
        print('done. ')
    else:
        print('StringFix started ', datetime.datetime.now())
        print('Loading gene descriptor .. ', end = ' ', flush = True)
        with open(file_out + '.gds', 'rb') as f:
            gds = pickle.load( f )
        genome = genome_fa
        print('done. ')
    
    if (genome_fa is None):
        print('StringFix finished ', datetime.datetime.now())
    else:
        file_out, file_out_genome = StringFix_synthesis( file_out + '.gff', genome, \
                n_cores=n_cores, rev = rev, out_dir = out_dir, gds = gds )
        
    return file_out
        

#########################################################
## StringFix-addon                                                                              ##
## developed by Seokhyun Yoon (syoon@dku.edu) Oct. 04, 2020   ##
#########################################################

def which( ai, value = True ) :
    wh = []
    a = list(ai)
    for k in range(len(a)): 
        if a[k] == value: 
            wh.append(k) 
    return(wh)

def get_info_from_tr_name( tns ):
    
    abn_e = []
    tpm_e = []
    ifrac = []
    sidx = []
    g_size = []
    n_exons = []
    g_vol = []
    icnt = []
    t_len = []
    strnd = []
    cdng = []
    for k, tn in enumerate(tns):
        hdr = tn.split(' ')
        items = hdr[0].split('_')
        strnd.append( items[2])
        cdng.append( items[3])
        sidx.append( (items[4]) )
        g_size.append( int(items[5]) )
        icnt.append( int(items[6]) )
        val = items[7].split(':')
        abn_e.append( float(val[1]) )
        val = items[8].split(':')
        tpm_e.append( float(val[1]) )
        val = items[9].split(':')
        ifrac.append( float(val[1]) )
        val = items[11].split(':')
        n_exons.append( int(val[1]) )
        val = items[12].split(':')
        g_vol.append( int(val[1]) )
        val = items[13].split(':')
        t_len.append( int(val[1]) )
    
    df = pd.DataFrame()
    
    df['tr_name'] = tns
    df['abn_est'] = abn_e
    df['tpm_est'] = tpm_e
    df['gidx'] = sidx
    df['iidx'] = icnt
    df['g_size'] = g_size
    df['iso_frac'] = ifrac
    df['n_exons'] = n_exons
    df['g_vol'] = g_vol
    df['length'] = t_len
    df['strand'] = strnd
    df['C_or_N'] = cdng
    
    df = df.set_index('tr_name')
    
    return df

def get_performance(trinfo, cvg_th = [80,90,95], f_to_save = None, ref = 0, verbose = False):
    
    #'''
    if ref == 0:
        q_cvg = 'qcvg'
        q_len = 'qlen'
        q_id = 'qid'
        s_start = 'sstart'
        s_end = 'send'
        s_id = 'sid'
    else:
        q_cvg = 'scvg'
        q_len = 'slen'
        q_id = 'sid'
        s_start = 'qstart'
        s_end = 'qend'
        s_id = 'qid'
    #'''
    
    qids = pd.unique(trinfo[q_id])
    sids = pd.unique(trinfo[s_id])
    wgt = np.zeros([len(qids),len(sids)])
    if verbose: print('Matching (%i,%i) ' % (wgt.shape), end='')

    qidx = np.full(trinfo.shape[0],-1,dtype=int)
    for k in range(len(qids)) :
        qid = qids[k]
        wh = which( trinfo[q_id] == qid )
        qidx[wh] = k
        
    if verbose: print('.', end='')
    sidx = np.full(trinfo.shape[0],-1,dtype=int)
    for k in range(len(sids)) :
        sid = sids[k]
        wh = which( trinfo[s_id] == sid )
        sidx[wh] = k
        
    if verbose: print('.', end='')
    for w in range(len(qidx)):
        wgt[int(qidx[w]), int(sidx[w])] = -trinfo[q_cvg][w]

    if verbose: print('_', end='')
    # print(wgt.shape)
    row_idx, col_idx = optimize.linear_sum_assignment(wgt)
    
    if verbose: print('.', end='')
    df_lst = []
    for k in range(len(col_idx)) :
        si = col_idx[k]
        wh = which(sidx == si)
        w = which( qidx[wh] == row_idx[k] )
        if len(w) > 0:
            if len(w) > 1: print('ERROR in get_performance(): Len(w) = %i' % len(w) )
            idx = wh[w[0]]
            df_lst.append(trinfo.iloc[idx])
        
    df_sel = pd.DataFrame(df_lst)
    if f_to_save is not None:
        fname = '%s_blast_result.tsv' % f_to_save
        df_sel.to_csv(fname, header=True, index=False, sep='\t')
        # if verbose: print(' %s.' % fname, end='' )
    
    if verbose: print('.', end='')
    cnt = np.zeros(len(cvg_th))
    for k in range(len(cvg_th)):
        th = cvg_th[k]
        wh = which( df_sel[q_cvg]*100 >= th )
        cnt[k] = np.int(len(wh))
        
    if verbose: print(' done.')

    d = {'cvg_th': cvg_th, 'N_recovered': cnt.astype(int), 'precision': np.round(100*cnt/len(sids),1)}
    df_perf = pd.DataFrame(data = d) #, columns = ['cvg_th','n_recovered','precision'])
    
    return(df_perf, df_sel)

    
def run_blast( inpt_fa, ref_fa, path_to_blast = None, trareco = False, ref_info = False, \
                 dbtype = 'nucl', ref = 0, sdiv = 10, mx_ncand = 6, verbose = False):

    #'''
    if ref == 0:
        ref_tr = ref_fa
        inpt_tr = inpt_fa
        
        q_cvg = 'qcvg'
        q_len = 'qlen'
        q_id = 'qid'
        s_start = 'sstart'
        s_end = 'send'
        s_id = 'sid'
    else:
        ref_tr = inpt_fa
        inpt_tr = ref_fa
        
        q_cvg = 'scvg'
        q_len = 'slen'
        q_id = 'sid'
        s_start = 'qstart'
        s_end = 'qend'
        s_id = 'qid'
    #'''
    
    file_names = inpt_tr.split('.')
    fname = ''.join(st for st in file_names[:-1] )

    tn_in = []
    f = open(inpt_tr,'r')
    cand_cnt = 0
    for line in f:
        if line[0] == '>':
            tn_in.append(line[1:-1])
            cand_cnt += 1
    f.close()
    
    tn_ref = []
    f = open(ref_tr,'r')
    ref_cnt = 0
    for line in f:
        if line[0] == '>':
            tn_ref.append(line[1:-1])
            ref_cnt += 1
    f.close()
    # print('Len: %i, Nu= %i' % (len(tn), len(pd.unique(tn))), end='' )
    
    if ref == 0:
        tn = tn_in
        n_max_cands = 1
    else:
        tn = tn_ref
        n_max_cands =  mx_ncand
        tmp = cand_cnt
        cand_cnt = ref_cnt
        ref_cnt = tmp
    
    ## make blast db with input_tr
    if path_to_blast is None:
        cmd = 'makeblastdb -in %s -dbtype %s' % (inpt_tr, dbtype)
    else:
        cmd = '%s/makeblastdb -in %s -dbtype %s' % (path_to_blast, inpt_tr, dbtype)
    res = subprocess.check_output(cmd, shell=True)
    # print(res.decode('windows-1252'))
 
    str_option = '-outfmt "6 qseqid sseqid qlen length slen qstart qend sstart send nident mismatch gapopen qcovs qcovhsp bitscore" -num_threads 4 -max_target_seqs %i' % n_max_cands

    if dbtype == 'nucl': prfx = 'n'
    else: prfx = 'p'
        
    if path_to_blast is None:
        cmd = 'blast%s %s -db %s -query %s -out %s.tblst' % (prfx, str_option, inpt_tr, ref_tr, fname)
    else:
        cmd = '%s/blast%s %s -db %s -query %s -out %s.tblst' % (path_to_blast, prfx, str_option, inpt_tr, ref_tr, fname)
        
    if verbose: print("Running Blast-%s with %i cand. %i ref. ... " % (dbtype[0].upper(),cand_cnt, ref_cnt), end='', flush=True);
    res = subprocess.check_output(cmd, shell=True)
    # print(res.decode('windows-1252'))
    if verbose: print('done.')
    
    os.remove( '%s.%shr' % (inpt_tr, prfx) )
    os.remove( '%s.%sin' % (inpt_tr, prfx) )
    os.remove( '%s.%ssq' % (inpt_tr, prfx) )
   
    colnames = ['qid', 'sid', 'qlen', 'alen', 'slen', 'qstart', 'qend', 'sstart', 'send', \
                'nident', 'mismatch', 'gapopen', 'qcovs', 'qcovhsp', 'bitscore']
    tblst = '%s.tblst' % fname
    df = pd.read_csv(tblst, header = 'infer', names = colnames, sep='\t')
    
    os.remove( '%s' % (tblst) )
    
    if verbose: print('N.cand: %i, N.subject.unique: %i' % (len(tn), len(pd.unique(df['sid']))) )

    df['scvg'] = df['alen']/df['slen']
    df['qcvg'] = df['alen']/df['qlen']
        
    if trareco == True:
        abn_e = []
        tpm_e = []
        ifrac = []
        sidx = []
        g_size = []
        n_exons = []
        g_vol = []
        icnt = []
        strnd = []
        cdng = []
        for k in range(df.shape[0]):
            # s = '>%s_Chr%s:%i-%i_%i_%i_%i_Abn:%4.3f_TPM:%4.2f_IFrac:%3.2f\n' 
            # % (tr.prefix, tr.chr, tr.start, tr.end, tr.gidx, tr.grp_size, tr.icnt, tr.abn, tr.tpm, tr.iso_frac)
            hdr = df[s_id][k].split(' ')
            items = hdr[0].split('_')
            strnd.append( items[2])
            cdng.append( items[3])
            sidx.append( (items[4]) )
            g_size.append( int(items[5]) )
            icnt.append( int(items[6]) )
            val = items[7].split(':')
            abn_e.append( float(val[1]) )
            val = items[8].split(':')
            tpm_e.append( float(val[1]) )
            val = items[9].split(':')
            ifrac.append( float(val[1]) )
            val = items[11].split(':')
            n_exons.append( int(val[1]) )
            val = items[12].split(':')
            g_vol.append( int(val[1]) )
    else:
        abn_e = np.zeros(df.shape[0])
        tpm_e = np.zeros(df.shape[0])
        ifrac = np.zeros(df.shape[0])
        sidx = np.full(df.shape[0], '')
        g_size = np.zeros(df.shape[0])
        n_exons = np.zeros(df.shape[0])
        g_vol = np.zeros(df.shape[0])
        icnt = np.zeros(df.shape[0])
        strnd = np.zeros(df.shape[0])
        cdng = np.zeros(df.shape[0])
        
    #'''
    ref_info = False
    if len(df[q_id][0].split(':')) == 4: 
        ref_info = True
        # print('Ref_info is true')
        
    if ref_info == True:
        gid = []
        cvg = []
        abn_t = []
        tpm_t = []
        for k in range(df.shape[0]):
            items = df[q_id][k].split(':')
            gid.append( items[0] )
            cvg.append( float(items[1]) )
            abn_t.append( float(items[2]) )
            tpm_t.append( float(items[3]) )
    else:
        gid = np.zeros(df.shape[0])
        cvg = np.zeros(df.shape[0])
        abn_t = np.zeros(df.shape[0])
        tpm_t = np.zeros(df.shape[0])

    #'''
    df['exp_cvg'] = cvg
    df['abn_true'] = abn_t
    df['abn_est'] = abn_e
    df['tpm_true'] = tpm_t
    df['tpm_est'] = tpm_e
    df['gidx'] = sidx
    df['iidx'] = icnt
    df['g_size'] = g_size
    df['iso_frac'] = ifrac
    df['n_exons'] = n_exons
    df['g_vol'] = g_vol
    df['strand'] = strnd
    df['C_or_N'] = cdng
        
    b = df[q_cvg] >= 0.8
    df_new = df.loc[b,:]
    df = df_new
    
    full_names = df[q_id] + df[s_id]
    fns = pd.unique(full_names)
    k = 0
    df_lst = []
    for fn in fns:
        wh = which(full_names == fn)
        df_tmp = df.iloc[wh]
        qcvg = np.array( df_tmp[q_cvg] )
        odr = qcvg.argsort()
        df_lst.append(df_tmp.iloc[odr[-1]]) 
        k += 1

    if len(df_lst) > 0:
        df_sel = pd.DataFrame(df_lst)
        #'''
        trinfo = '%s_blast_result.tsv' % fname
        df_sel.to_csv(trinfo, header=True, index=False, sep='\t')
        # if verbose: print('Transcriptome Info. written to \n   %s.' % trinfo )

        df_sel = pd.read_csv(trinfo, sep='\t')
        #'''

        df_perf, df_sel = get_performance(df_sel, f_to_save=fname, ref = ref, verbose=verbose)
        df_perf['precision'] = round(df_perf['N_recovered']*100/cand_cnt,1)
        df_perf['sensitivity'] = round(df_perf['N_recovered']*100/ref_cnt,1)
        # if verbose: print(df_perf)
           
        if trareco == True:
            df_tr = get_info_from_tr_name( tn )
            df_tr['detected'] = False
            df_tr.loc[list(df_sel[s_id]),'detected'] = True 
            df_tr[q_len] = 0
            for m, sid in enumerate(df_sel[s_id]):
                df_tr.loc[sid,q_len] = np.round(df_sel.iloc[m].qlen)
            df_tr[s_start] = 0
            # df_tr.loc[list(df_sel['sid']),'scvg'] = df_sel.loc[:,'scvg'] 
            for m, sid in enumerate(df_sel[s_id]):
                df_tr.loc[sid,s_start] = np.round(df_sel.iloc[m].sstart)
            df_tr[s_end] = 0
            # df_tr.loc[list(df_sel['sid']),'scvg'] = df_sel.loc[:,'scvg'] 
            for m, sid in enumerate(df_sel[s_id]):
                df_tr.loc[sid,s_end] = np.round(df_sel.iloc[m].send)
            df_tr = df_tr.reset_index()
        else:
            df_tr = None
            
        return(df_perf, df_sel, df_tr)
    
    else:
        if verbose: print('No tr found. ')
        return(None,None,None)
    

##################################################################################
## Functions to (1) select specific chrm and (2) only coding genes in a GTF
##################################################################################

def sort_gtf_lines_lst(gtf_lines_lst):
    
    chrs = []
    for lines in gtf_lines_lst:
        first_line = lines[0]
        chrs.append(first_line.chr)

    chr_set = list(set(chrs))
    chr_set.sort()
    chrs = np.array(chrs)

    gtf_lst_new = []
    for c in chr_set:
        wh = which(chrs == c)
        ps = np.array( [gtf_lines_lst[w][0].start for w in wh] )
        odr2 = ps.argsort()
        for o in odr2:
            w = wh[o]
            gtf_lst_new.append(gtf_lines_lst[w])
        
    return gtf_lst_new


def select_coding_genes_from_gtf_file(gtf_file, genome_file):

    fns = gtf_file.split('.')[:-1]
    fname = ''
    for k, fn in enumerate(fns):
        if k > 0:
            fname = fname + '.'
        fname = fname + fn
    
    gtf_lines, hdr_lines = load_gtf(gtf_file, verbose = True)
    
    base_cds = get_base_cds_from_gtf_lines(gtf_lines)
    if base_cds < 0:
        print('INFO: No coding information provided in the GTF/GFF.')
    
    gtf_lines_lst = parse_gtf_lines_and_split_into_genes( gtf_lines )
    genome = load_genome(genome_file)
    chrs = genome.keys()

    gtf_lines_lst_new = []
    ccnt = 0
    gcnt = 0
    for k, glines in enumerate(gtf_lines_lst):

        if  glines[0].chr in chrs:
            tr_lines_lst = parse_gtf_lines_and_split_into_genes( glines, 'transcript' )
            lines_new = []

            for lines in tr_lines_lst:
                b = False
                cnt = [0,0]
                for gtfline in lines:
                    if gtfline.feature == 'start_codon':
                        cnt[0] += 1
                    if gtfline.feature == 'stop_codon':
                        cnt[1] += 1
                    if (cnt[0] > 0) & (cnt[1] > 0):
                        b = True
                        ccnt += 1
                        break
                        
                if b: lines_new = lines_new + lines
                gcnt += 1
            
            if len(lines_new) > 0:
                gtf_lines_lst_new.append(lines_new)
            
        if k%100 == 0: print('\rparsing .. %i/%i (%i/%i)' % (k, len(gtf_lines_lst), ccnt, gcnt), end='', flush = True )

    print('\rparsing .. %i/%i (%i/%i)' % (k, len(gtf_lines_lst), ccnt, gcnt), flush = True )
    print('Sorting .. ', end='')
    gtf_lines_lst_new = sort_gtf_lines_lst(gtf_lines_lst_new)
    print('\rSorting .. done')
            
    gtf_lines_new = []
    for lines in gtf_lines_lst_new:
        gtf_lines_new = gtf_lines_new + lines
        
    fname = fname + '_cds.gtf'
    print('Saving .. ', end='')
    save_gtf( fname, gtf_lines_new, hdr_lines )
    print('\rSaving .. done')
    
    return fname
    

def select_chr_from_gtf_file(gtf_file, chrms = []):

    fns = gtf_file.split('.')[:-1]
    fname = ''
    for k, fn in enumerate(fns):
        if k > 0:
            fname = fname + '.'
        fname = fname + fn
    
    gtf_lines, hdr_lines = load_gtf(gtf_file, verbose = True)
    
    gtf_lines_lst = parse_gtf_lines_and_split_into_genes( gtf_lines )

    gtf_lines_lst_new = []
    ccnt = 0
    gcnt = 0
    if isinstance(chrms, str):
        for k, lines in enumerate(gtf_lines_lst):
            b = False
            if lines[0].chr == chrm: 
                b = True
                ccnt += 1
            gcnt += 1
            
            if k%100 == 0: print('\rparsing .. %i/%i (%i/%i)' % (k, len(gtf_lines_lst), ccnt, gcnt), end='', flush = True )
            if b: 
                gtf_lines_lst_new.append(lines)
    else:
        for chrm in chrms:
            for k, lines in enumerate(gtf_lines_lst):
                b = False
                if lines[0].chr == chrm: 
                    b = True
                    ccnt += 1
                gcnt += 1
                
                if k%100 == 0: print('\rparsing .. %i/%i (%i/%i)' % (k, len(gtf_lines_lst), ccnt, gcnt), end='', flush = True )
                if b: 
                    gtf_lines_lst_new.append(lines)
        chrm = chrms[0]
        for c in chrms[1:]:
            chrm = chrm + ',%s' % c
            
    print('\rparsing .. done %i/%i (%i/%i)' % (k, len(gtf_lines_lst), ccnt, gcnt), flush = True )
    
    print('Sorting .. ', end='')
    gtf_lines_lst_new = sort_gtf_lines_lst(gtf_lines_lst_new)
    print('\rSorting .. done')
            
    gtf_lines_new = []
    for lines in gtf_lines_lst_new:
        gtf_lines_new = gtf_lines_new + lines
    
    print('Saving .. ', end='')
    fname = fname + '_sel_%s.gtf' % chrm
    save_gtf( fname, gtf_lines_new, hdr_lines )
    print('\rSaving .. done')
    
    return fname
    

##################################################################################
## Functions to handle simulated reads (add trareco header, split fastQ)
##################################################################################

def fasta_add_trareco_header( ref_tr, sim_profile, read_len, suffix = None, cov_th = 0.8 ):
    
    colnames = ['loc', 'tid', 'coding', 'length', 'exp_frac', 'exp_num', 'lib_frac', 'lib_num', \
                'seq_frac', 'seq_num', 'cov_frac', 'chi2', 'Vcoef']
    df_pro = pd.read_csv(sim_profile, sep='\t', header = None, index_col = 1, names = colnames)

    ref = load_fasta(ref_tr)

    df_pro['abn'] = df_pro['seq_num']*read_len/df_pro['length']
    df_pro['tpm'] = df_pro['abn']*1000000/(df_pro['abn'].sum())

    df_idx = np.array(df_pro.index.values.tolist())
    cnt_dup = 0
    for key in list(ref.keys()):
        if (key in df_idx) & (np.sum(df_idx == key) == 1):
            if df_pro.loc[key].cov_frac >= cov_th:
                ref[key].header = '%s cov_frac:%f abn:%f tpm:%f' % (ref[key].header, df_pro.loc[key].cov_frac, df_pro.loc[key].abn, df_pro.loc[key].tpm)
            else:
                ref.pop(key)
        else:
            if df_pro.loc[key].shape[0] > 1: cnt_dup += 1
            ref.pop(key)

    fname, ext = get_file_name(ref_tr)
    if suffix is None:
        fname = fname + '_cov%i.' % int(cov_th*100) + ext
    else:
        fname = fname + '_%s_cov%i.' % (suffix, int(cov_th*100)) + ext

    save_fasta(fname, ref, title = fname)
    

def load_fastq(file_genome, verbose = False ):

    genome = dict()
    f = open(file_genome, 'r')
    scnt = 0
    print('\rLoading fastQ .. ', end='', flush=True)
    cnt = 0
    for line in f :
        if line[0] == '@':
            if cnt == 4:
                genome[scnt] = Genome(hdr, seq, qual)
                scnt += 1
            cnt = 0
            hdr = line[1:-1]
            cnt += 1
        else:
            if cnt == 1:
                seq = line[:-1]
                cnt += 1
            elif cnt == 2:
                if line[0] == '+':
                    idr = line[1:-1]
                    cnt += 1
                else:
                    print('ERROR in fastQ file')
                    break
            elif cnt == 3:
                qual = line[:-1]
                cnt += 1
    if cnt > 0:
        genome[scnt] = Genome(hdr, seq, qual)
        scnt += 1
                
    print('\rLoading fastQ .. done.  Num.Seq = ', scnt, '   ', flush=True)
    f.close()
    return(genome)


def save_fastq( file_genome, genome_dict, verbose = False, title = 'fastQ' ):

    print('Saving %s ..' % title, end='', flush=True)
    # for g in genome_lst :
    Keys = genome_dict.keys()
    f = open(file_genome, 'wt+')
    line_lst = []
    for key in Keys:
        # print('\rSaving %s .. %s' % (title, key), end='                    ')
        g = genome_dict[key]
        s = '@%s\n' % g.header
        line_lst.append(s)
        line_lst.append(g.seq.upper() + '\n')
        line_lst.append('+\n')
        line_lst.append(g.qual + '\n')
        
        if verbose: print('.', end='', flush=True)

    f.writelines(''.join(line_lst))
        
    print('\rSaving %s .. done. (%i)                ' % (title, len(Keys)), flush=True)
    f.close()
    

    
def fasta_sim_read_split( sim_read, dsr = 1 ):
    
    fname, ext = get_path_name(sim_read)

    fa_all = load_fastq(sim_read)
    
    fa1 = {}
    fa2 = {}
    cnt = 0
    cnt_1 = 0
    cnt_2 = 0
    for key in fa_all.keys():
        fa_all[key].header = fa_all[key].header[:-4]
        if cnt%2 == 0:
            if cnt_1%dsr == 0:
                fa_all[key].header = fa_all[key].header.split(' ')[0] + '/1'
                fa1[key] = fa_all[key]
            cnt_1 += 1
        else:
            if cnt_2%dsr == 0:
                fa_all[key].header = fa_all[key].header.split(' ')[0] + '/2'
                fa2[key] = fa_all[key]
            cnt_2 += 1

        cnt += 1

    if dsr == 1:
        fn1 = fname + '_1.' + ext
        fn2 = fname + '_2.' + ext
    else:
        fn1 = fname + ('_ds%i' % dsr) + '_1.' + ext
        fn2 = fname + ('_ds%i' % dsr) + '_2.' + ext
    save_fastq(fn1, fa1)
    save_fastq(fn2, fa2)
    

def fasta_sim_read_downsample( sim_read, dsr = 1 ):
    
    fname, ext = get_path_name(sim_read)

    fa_all = load_fastq(sim_read)
    
    fa = {}
    cnt = 0
    for key in fa_all.keys():
        # fa_all[key].header = fa_all[key].header[:-4]
        if cnt%dsr == 0:
            # fa_all[key].header = fa_all[key].header
            fa[key] = fa_all[key]
        cnt += 1

    fn = fname + ('_ds%i.' % dsr) + ext
    save_fastq(fn, fa)
    
    
##################################################################################
## Functions to add SNV into a genome
##################################################################################

SNV = collections.namedtuple('SNV', 'chr, pos_new, pos_org, type, len, seq_new, seq_org, ex_start, ex_end')

def get_snv_type(pi, pd):
    
    rn = np.random.uniform(100)
    if rn < (pi*100):
        return(1)
    elif rn < (pi+pi)*100:
        return(2)
    else:
        return(0)
    
def rand_nucleotide_except(nts):
    
    nts_out = ''
    for nt in nts:
        while True:
            rn = np.random.randint(0,4,1)[0]
            nt_new = NT_lst[int(rn)]
            if nt_new != nt: 
                nts_out = nts_out + nt_new
                break
                    
    return(nts_out)
        
def rand_nucleotides(num):
    
    num_seq = np.random.randint(0,4,num)
    nt_str = ''.join([NT_lst[n] for n in num_seq])
    return(nt_str)


def save_snv_info_old( file_name, snv_lst, verbose = False ):
    
    f = open(file_name, 'wt+')
    print('Saving SNV info. ', end='')
    step = np.ceil(len(snv_lst)/20)
    for k in range(len(snv_lst)) :
        snv = snv_lst[k]
        s = '%s,%i,%i,%s,%i,%s,%s\n' % \
        (snv.chr, snv.pos_new, snv.pos_org, snv.type, snv.len, snv.seq_new, snv.seq_org )
        f.writelines(s)
        if k%step == 0: print('.',end='')
        
    print(' done. %i snvs.' % len(snv_lst) )
    f.close()

    
def save_snv_info( file_name, snv_lst, verbose = False ):

    df = pd.DataFrame(snv_lst)
    df.to_csv(file_name, index=False, sep='\t')

    
def generate_snv_with_gtf( genome, gtf_lines_sorted, mu = 200, li = 3, ld = 3, lv = 2, pi = 0.1, pd = 0.1 ):
    
    pv = 1 - pi - pd
    print(genome.name, end=' ')
    snv_lst = []
    cur_pos_org = 0
    cur_pos_new = cur_pos_org
    seq_new = ''
    seq_lst = []
    Margin = max(li,max(ld,lv))
    
    step = np.ceil(genome.len/mu/200)
    
    cnt = 0
    for line in gtf_lines_sorted:
        
        # diff = cur_pos_new - cur_pos_org
        Start = line.start
        End = line.end
        L = np.random.randint(0,mu/2,1)[0]
        if cur_pos_org < (line.start-1+L):
            next_pos_org = line.start-1+L
            seq_lst.append(genome.seq[int(cur_pos_org):int(next_pos_org)])
            cur_pos_new += (next_pos_org-cur_pos_org)
            cur_pos_org = next_pos_org
        
        while (cur_pos_org < (line.end-Margin)) & (cur_pos_org > (line.start+Margin)):

            snv_type = get_snv_type(pi, pv)

            if snv_type == 1: # Insertion
                n = np.random.randint(0,li, 1)[0]+1
                seq_frag = rand_nucleotides(n)
                # seq_new = seq_new + seq_frag
                seq_lst.append(seq_frag)
                snv = SNV( genome.name, cur_pos_new+1, cur_pos_org+1, 'I', n, seq_frag, '-', Start, End ) # make it one-base position
                snv_lst.append(snv)
                cur_pos_new += len(seq_frag)

            elif snv_type == 2: # Deletion
                n = np.random.randint(0,ld, 1)[0]+1
                seq_frag = genome.seq[int(cur_pos_org):int(cur_pos_org+n)]
                snv = SNV( genome.name, cur_pos_new+1, cur_pos_org+1, 'D', n, '-', seq_frag, Start, End ) # make it one-base position
                snv_lst.append(snv)
                cur_pos_org += n

            else: # SNP
                n = np.random.randint(0,lv, 1)[0]+1        
                seq_tmp = genome.seq[int(cur_pos_org):int(cur_pos_org+n)]
                seq_frag = rand_nucleotide_except(seq_tmp)
                # seq_new = seq_new + seq_frag
                seq_lst.append(seq_frag)
                snv = SNV( genome.name, cur_pos_new+1, cur_pos_org+1, 'V', n, seq_frag, seq_tmp, Start, End ) # make it one-base position
                snv_lst.append(snv)
                cur_pos_new += n
                cur_pos_org += n

            L = np.random.randint(20,mu,1)[0] # separate SNV at least 20 bases
            next_pos_org = cur_pos_org + L
            if next_pos_org >= line.end: # (genome.len-100):
                # seq_new = seq_new + genome.seq[int(cur_pos_org):]
                seq_lst.append(genome.seq[int(cur_pos_org):(line.end+1)])
                cur_pos_new += ((line.end+1)-cur_pos_org)
                cur_pos_org = (line.end+1)
                break
            else:
                # seq_new = seq_new + genome.seq[int(cur_pos_org):int(next_pos_org)]
                seq_lst.append(genome.seq[int(cur_pos_org):int(next_pos_org)])
                cur_pos_new += (next_pos_org-cur_pos_org)
                cur_pos_org = next_pos_org
            cnt += 1
            if cnt%step == 0: 
                print('\r%s - %i, %i, %i ' % (genome.name, cur_pos_org, genome.len, cur_pos_new), end='')
       
    if cur_pos_org < genome.len:
        seq_lst.append(genome.seq[int(cur_pos_org):])
    
    seq_new = ''.join(seq_lst)
    # suffix = '-L%i-I%i-D%i-V%i' % (mu,li,ld,lv)
    # genome_new = Genome( genome.header + suffix, seq_new )
    genome_new = Genome( genome.header, seq_new )
    print(' done.')
            
    return(genome_new, snv_lst)
    
################################
## Parameters for SNV generation

P_INS = 0.15
P_DEL = 0.15
P_SNP = 1 - P_INS - P_DEL

LI = 3
LD = 3
LV = 2
L_INTER_SNV = 200

################################

def generate_snv(genome, gtf_lines, l_inter_snv = L_INTER_SNV, \
                 li = LI, ld = LD, lv = LV, pi = P_INS, pd = P_DEL):
    
    pv = 1 - pi - pd
    np.random.seed(0)
    print('Generating SNV ',end='')
    Features = get_col(gtf_lines, 2)
    wh = which( Features, 'exon' )
    gtf_exons = [gtf_lines[w] for w in wh] 

    # print(len(Features))
    Chrs = get_col(gtf_exons, 0)
    Chr_names = sorted(set(Chrs))

    snv_lst_all = []
    genome_new = {}
    for Chr in Chr_names:
        
        if Chr in genome.keys():
            wh = which( Chrs, Chr )
            gtf_chr = [gtf_exons[w] for w in wh]
            Pos_start = np.array( get_col(gtf_chr, 3) )
            odr = Pos_start.argsort()

            gtf_chr_sorted = []
            pp = 0
            for k in range(len(gtf_chr)):
                line = gtf_chr[odr[k]]
                gtf_chr_sorted.append(line)
                if line.start < pp: print(line)
                pp = line.start

            gnm, snv_lst = generate_snv_with_gtf( genome[Chr], gtf_chr_sorted, mu = l_inter_snv, \
                                                  li = li, ld = ld, lv = lv, pi = pi, pd = pd )
            snv_lst_all = snv_lst_all + snv_lst
            genome_new[Chr] = gnm
     
    return(genome_new, snv_lst_all, Features)
    
##################################################################################
## Functions for evaluation of SNV detection
##################################################################################

def get_span_lst(rgns_lst_mi, Type = 'M'):
    
    span_lst = []
    for r_m in rgns_lst_mi:
        spn = r_m.get_span()
        spn.type = Type
        span_lst.append( spn )
    return(span_lst)

## Select SNV's that falls within the covered region
def select_snvs( df_snv, span_lst, rgns_lst_mi, Type = 'M', mdev = 12 ):
    
    print('Checking intersection .. ', end='')
    step = np.ceil(df_snv.shape[0]/20)
    
    df_snv['start'] = df_snv['pos_org'] - mdev
    df_snv['end'] = df_snv['pos_org'] + df_snv['len'] + mdev
    df_snv['cvg'] = 0

    b_proc = np.full(df_snv.shape[0], False)
    for k, span in enumerate(span_lst):
        b0 = df_snv['chr'] == span.chr
        b1 = (df_snv['start'] >= span.start) & ((df_snv['start'] <= span.end))
        b2 = (df_snv['end'] >= span.start) & ((df_snv['end'] <= span.end))
        b = b0 & (b1 | b2) & (b_proc == False)
        df_snv_tmp = df_snv[b]
        for m, row in df_snv_tmp.iterrows():
            rgn = region( row.chr, row.start, row.end, Type )
            bb, cc = rgns_lst_mi[k].get_intersection_cvg(rgn) 
            if bb: 
                b_proc[m] = True
                df_snv.loc[m,'cvg'] = cc
                
        # if k%step == 0: print('.',end='')
        if k%10 == 0:    
            print('\rChecking intersection .. %i/%i (%i)' % (k, len(span_lst), np.sum(b_proc)), end='' )

    print('\rChecking intersection .. done. %i -> %i' % (df_snv.shape[0], np.sum(b_proc)) )
    
    df_snv_sel = (df_snv.iloc[b_proc]).copy(deep = True)
    
    return(df_snv_sel)


def matching_snvs( df_snv_sel, df_detected, dev_tol = 3 ):
    
    ## the dataframes mush be sorted according to the position (pos_new, start)
    df_t_all = df_snv_sel
    df_d_all = df_detected

    cnt = 0
    chrms = df_t_all['chr']
    chr_lst = list(set(chrms))
    chr_lst.sort()

    cnt = 0
    N_t = 0
    N_d = 0
    for n, chrm in enumerate(chr_lst):
        
        b1 = (df_t_all['chr'] == chrm)
        b2 = (df_d_all['chr'] == chrm)
    
        if (np.sum(b1) == 0) | (np.sum(b2) == 0):        
            pass
        else:
            
            df_t = df_t_all.loc[b1,:].copy(deep = True)
            df_d = df_d_all.loc[b2,:].copy(deep = True)
            
            n_target = df_t.shape[0]
            n_detected = df_d.shape[0]
            
            N_t += n_target
            N_d += n_detected
            
            # print('\rMatching %s ' % (chrm) , end='')
            cnt_t = 0
            cnt_d = 0
            match = np.full(n_target, -1)
            dist = np.full(n_target, 0)
            
            while True:
                
                if (cnt_d >= n_detected) | (cnt_t >= n_target): break
                print('\rMatching %s, %i/%i .. %i/%i, %i/%i ' % \
                      (chrm, n, len(chr_lst), cnt_t, n_target, cnt_d, n_detected) , end='')

                p_t = df_t.iloc[cnt_t].pos_org
                p_d = df_d.iloc[cnt_d].pos_org
                t_t = df_t.iloc[cnt_t].type
                t_d = df_d.iloc[cnt_d].type
                L_t = max(len(df_t.iloc[cnt_t].seq_org), len(df_t.iloc[cnt_t].seq_new))
                L_d = max(len(df_d.iloc[cnt_d].seq_org), len(df_d.iloc[cnt_d].seq_new))

                if (p_t) > (p_d + L_d + dev_tol):
                    cnt_d += 1
                    if cnt_d >= n_detected: break
                elif (p_t + L_t + dev_tol) < (p_d):
                    cnt_t += 1
                    if cnt_t >= n_target: break
                else:
                    b = True
                    if (t_t == 'V') & (t_d == 'V'):
                        if len(df_t.iloc[cnt_t].seq_new) == len(df_d.iloc[cnt_d].seq_new):
                            if (p_t == p_d) & (df_t.iloc[cnt_t].seq_new == df_d.iloc[cnt_d].seq_new):
                                match[cnt_t] = cnt_d
                                dist[cnt_t] = p_t - p_d
                                cnt_t += 1
                                cnt_d += 1
                                b = False
                            else:
                                pass
                                '''
                                match[cnt_t] = cnt_d
                                dist[cnt_t] = p_t - p_d
                                cnt_t += 1
                                cnt_d += 1
                                b = False
                                '''
                        else:
                            pass
                        
                        if b:
                            cnt_t += 1
                            cnt_d += 1
                            
                    elif (t_t == 'I') & (t_d == 'D'):
                        match[cnt_t] = cnt_d
                        dist[cnt_t] = p_t - p_d
                        cnt_t += 1
                        cnt_d += 1
                        b = False

                    elif (t_t == 'D') & (t_d == 'I'):
                        match[cnt_t] = cnt_d
                        dist[cnt_t] = p_t - p_d
                        cnt_t += 1
                        cnt_d += 1
                        b = False
                    else:
                        # cnt_t += 1
                        # cnt_d += 1
                        if (cnt_d >= n_detected) | (cnt_t >= n_target): break
                        

            b = match >= 0
            wh_t = which(b)
            wh_d = match[wh_t]
            
            if len(wh_t) > 0:
                if cnt == 0:
                    df_t['dist'] = dist
                    df1 = df_t.iloc[wh_t].copy(deep = True)
                    df2 = df_d.iloc[wh_d].copy(deep = True)
                    cnt += 1
                else:
                    df_t['dist'] = dist
                    df1 = pd.concat([df1, df_t.iloc[wh_t].copy(deep = True)])
                    df2 = pd.concat([df2, df_d.iloc[wh_d].copy(deep = True)])
                    cnt += 1
           
    print('\rMatching .. done. ', end = '')
    if cnt > 0:
        df2 = df2.rename( columns = {'chr': 'chr_d', 'type': 'type_d', 'pos_org': 'pos_org_d', \
                                'seq_org': 'seq_org_d', 'seq_new': 'seq_new_d'} )
        sel_col_t = ['chr', 'type', 'pos_org', 'seq_org', 'seq_new', 'dist']
        sel_col_d = ['id', 'chr_d', 'type_d', 'pos_org_d', 'seq_org_d', 'seq_new_d']
        df1.index = pd.Index([k for k in range(df1.shape[0])])
        df2.index = pd.Index([k for k in range(df2.shape[0])])
        df = pd.concat( [df1[sel_col_t], df2[sel_col_d]], axis = 1, sort=False )        
            
        sens = 100*df.shape[0]/N_t
        prec = 100*df.shape[0]/N_d
        print(' N_t: %i, N_d: %i -> %i (sens: %4.1f, prec: %4.1f) ' % \
              (N_t, N_d, df.shape[0], sens, prec))
        return df, prec, sens, df.shape[0], N_d, N_t
    else:
        print(' ')
        return None, 0, 0, 0, 0, 0
            
##########################################################################
## Seokhyun Yoon (syoon@dku.edu) Oct. 04, 2020
##########################################################################




        

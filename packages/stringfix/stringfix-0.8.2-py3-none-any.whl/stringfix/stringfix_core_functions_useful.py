##################################################################################
## StringFix - an annotation-quided genome-reconstruction and proteome assember ##
## developed by Seokhyun Yoon (syoon@dku.edu) Oct. 04, 2020                     ##
##################################################################################

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

def load_genome(file_genome, verbose = False ):
def save_genome( file_genome, genome_dict, verbose = False, title = 'genome' ):
def load_fasta(file_genome, verbose = False ):
def save_fasta( file_genome, genome_dict, verbose = False, title = 'seq.' ):

##########################################################################
## Object for loading SAM/BAM
##########################################################################

class sam_obj:
    def __init__(self, file_name, n_max = 0, sa = 1 ):
    def close(self):
    def get_sam_lines_for_one_chrm(self):
    def get_one_overlaped_sam(self):

##########################################################################
## Functions and objects to handle GTF file
##########################################################################

def print_gtf(line):
def print_gtf_lines(lines):
def print_gtf_lines_to_str(lines):
def load_gtf( fname, verbose = True, ho = False ):
def save_gtf( fname, gtf_line_lst, hdr = None ):
def save_gff( fname, gtf_line_lst ):

##########################################################################
## Functions to find coding regions and to generate proteome
##########################################################################

def translate(seq):
def reverse_complement(seq):
def gen_proteome_from_trascriptome(hdr_lst, tseq_lst, len_th = MIN_PR_LENGTH, verbose = True, mx_cnt = 0, trareco = False, ignore_s = False):
def Generate_Proteome(tr_fa, len_th = MIN_PR_LENGTH, verbose = True, mx_cnt = 0, trareco = False, fname_out = None, ignore_s = False):
    
##########################################################################
#### StringFix main ########
##########################################################################

def StringFix_analysis(sam_file, gtf = None, genome_file = None, suffix = None, jump = 0, sa = 2, cbyc = False, \
                       n_cores = 1, min_frags_per_gene = 2, len_th = MIN_TR_LENGTH, out_tr = False, sav_rgn = False, out_dir = None ):

def StringFix_synthesis(gtf_file, genome_file, rev = True, n_cores = 1, out_dir = None, gds = None):

def StringFix_assemble( Input = None, genome_fa = None, annot_gtf = None, out_dir = 'SFix_out', \
                        n_cores = 4, out_custom_genome = False, suffix = None, \
                        mcv = 0.5, mcd = 1, mtl = 200, mpl = 50, mdi = 2, mdd = 2, mdp = 3, \
                        mdf = 0.2, n_p = 16, xsa = True, jump_to = 0 ):

##########################################################################
## StringFix addon's
##########################################################################

def build_gene_transcript_table( gtf_file ):
def StringFix_GFFRead(gtf_file, genome_file, n_cores = 1):
def Generate_Reference(gtf_file, genome_file, peptide = True, out_dir = None, suffix = None):
    
def get_performance(trinfo, cvg_th = [80,90,95], f_to_save = None, ref = 0, verbose = False):
def run_blast( inpt_fa, ref_fa, path_to_blast = None, trareco = True, ref_info = False, \
                 dbtype = 'nucl', ref = 0, sdiv = 10, mx_ncand = 6, verbose = False):

## Functions to (1) select specific chrm and (2) only coding genes in a GTF

def sort_gtf_lines_lst(gtf_lines_lst):
def select_coding_genes_from_gtf_file(gtf_file, genome_file):
def select_chr_from_gtf_file(gtf_file, chrm = '1'):

## Functions to handle simulated reads (add trareco header, split fastQ)

def load_fastq(file_genome, verbose = False ):
def save_fastq( file_genome, genome_dict, verbose = False, title = 'fastQ' ):
def fasta_sim_read_split( sim_read, dsr = 1 ):
def fasta_sim_read_downsample( sim_read, dsr = 1 ):
    
## Functions to add SNV into a genome

def save_snv_info( file_name, snv_lst, verbose = False ):
def generate_snv_with_gtf( genome, gtf_lines_sorted, mu = 200, li = 3, ld = 3, lv = 2, pi = 0.1, pd = 0.1 ):
def generate_snv(genome, gtf_lines, l_inter_snv = L_INTER_SNV, li = LI, ld = LD, lv = LV, pi = P_INS, pd = P_DEL):
    
##########################################################################
## Seokhyun Yoon (syoon@dku.edu) Oct. 04, 2020
##########################################################################




        

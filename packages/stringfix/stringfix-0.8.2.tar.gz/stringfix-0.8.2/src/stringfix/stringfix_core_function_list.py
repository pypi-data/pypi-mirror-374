##################################################################################
## StringFix - an annotation-quided genome-reconstruction and proteome assember ##
## developed by Seokhyun Yoon (syoon@dku.edu) Oct. 04, 2020                     ##
##################################################################################

## Configuration Parameters

#####################
# Contig build param.
StringFix_version = '0.6.4'
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
SAM_line = collections.namedtuple('SAM_line', 'qname, flag_str, rname, pos, mapq, cigar, rnext, pnext, tlen, seq, qual, xs')
QNAME, FLAG_STR, RNAME, POS, MAPQ, CIGAR, RNEXT, PNEXT, TLEN, SEQ, QUAL, XS = [i for i in range(12)]

Transcript = collections.namedtuple('Transcript',  'prefix, gidx, grp_size, icnt, chr, start, end, strand, cdng, seq, abn, tpm, iso_frac, prob, nexs, gvol')

PREFIX, GIDX, GSIZE, ICNT, CHR, TSTART, TEND, TSTRAND, TCDNG, TSEQ, ABN, TPM, ISO_FRAC, PROB, NEXS = [i for i in range(15)]

def get_flag(values, bpos ):
def get_col(nt_lst, n):
def fline_cnt( fname ):
def load_fasta1(file_genome, verbose = False ):
class Genome:
    def get_attr(self):

def load_genome(file_genome, verbose = False ):
def save_genome( file_genome, genome_dict, verbose = False, title = 'genome' ):
def load_fasta(file_genome, verbose = False ):
def save_fasta( file_genome, genome_dict, verbose = False, title = 'seq.' ):
def load_sam_lst( fname, n_rd_max = None, verbose = False, sdiv = 10 ):
def which( ai, value = True ) :
def parse_cigar( cigar_str ):
def compare_seq( s1, s2 ):
def get_error_seq( s1, s2 ):
def get_seq_from_genome_o2(genome, sam_line):

##########################################################################
## Functions to handle Cmat
##########################################################################

NT_lst = 'ACGTN'
NT_dict = { 'A':0, 'C':1, 'G':2, 'T':3, 'N':4, 'U': 3, '*':4 }

def NTstr2NumSeq( nt_str ) :
def NumSeq2NTstr( num_seq ) :
def NTstr2CMat_old( nt_str ) :
def NTstr2CMat( nt_str ) :
def CMat2NTstr( cmat ) :
def CMat2NTstr_with_CVG( cmat ) :
def get_cvg( cmat ) :
def get_majority_cnt( cmat ) :
def merge_seq_to_cmat( cm1, pos, nt_str ) :
def merge_cmat( cm1, pos, cm2 ) :
def merge_cmat2( cm1, pos, cm2 ) :
def merge_cvg( cvg1, pos, cvg2 ) :

##########################################################################
## regions objects
##########################################################################

class Region:
    def print(self):
    def copy(self):
    def isempty(self):
    def get_seq(self):
    def does_contain(self, rgn):
    def contain(self,pos):
    def contain_i(self,pos):
    def get_len(self):
    def has_intersection_with(self, a_rng, max_dev = 0):
    def has_ext_intersection_with(self, a_rng, max_dev = 0):
    def is_the_same_as(self, a_rng): # assume intersection
    def get_union(self, a_rng): # assume intersection
    def get_intersection(self, a_rng): # assume intersection
    def get_overlap_len(self, a_rng): # assume intersection
    def update(self, a_rng):
            
class Region_ext(Region):
    def convert_to_text_lines(self, sn, N, n ):
    def set_from_text_lines(self, lines ):
    def get_volume(self):
    def get_cov(self):
    def set_ave_cvg_depth(self):
    def med_cvg_depth(self):
    def ave_cvg_depth(self):
    def cvg_depth_start(self):
    def cvg_depth_end(self):
    def get_cov_len(self):
    def get_seq(self):
    def get_seq2(self):
    def get_cvg(self):
    def get_seq_n_cvg(self):
    def print(self):
    def print_short(self):
    def print_minimal(self):
    def print_short2(self):
    def print_cvg(self):
    def copy(self, update = True):
    def update(self, a_rng, cm=True):
    def get_portion(self, s, e):
    def set_portion(self, s, e, cmat):
    def update_intersection(self, a_rng, cm=True):
    def alloc_cm(self):
    def set_cm(self):
    def concatenate(self, a_rng, update=True):
    def cut(self, pos):
    def compare_and_replace_N_old( self, seq_to_compare ):
    def compare_and_replace_N_old2( self, seq_to_compare ):
    def compare_and_replace_N( self, seq_to_compare ):

#######################################

class regions:
    def set_r_cnt(self, cr, cs):
    def convert_to_text_lines_ho(self, sn = 0):
    def convert_to_text_lines(self, sn = 0):
    def set_from_text_lines(self,lines):
    def print(self):
    def print_short(self):
    def print_compact(self, sel = 0):
    def print_minimal(self):
    def copy(self, update = True):
    def isempty(self):
    def set_rgn(self, rgn, cm, si):
    def get_span( self ):               
    def get_span2( self ):               
    def get_span3( self ):               
    def get_volume(self):
    def get_cvgs_and_lens(self, path = None):
    def get_seq_of_path(self, path):
    def set_cvg(self):
    def get_length( self ):               
    def count_valid_NT(self):
    def get_cov( self ):               
    def get_coverage( self ):               
    def merge( self, rgns ): 
    def get_idx_of_type(self,type_in):
    def order(self):
    def has_intersection_with(self, rgn):
    def has_ext_intersection_with(self, rgn):
    def get_intersection_cvg(self, rgn):
    def get_overlap_length(self, rgn):
    def update(self, rgn = None, xc = True, cm = True, si = 0):
    def update_intersection(self, rgn = None, xc = True, cm = True, si = 0):
    def alloc_cm(self):    
    def check_rgns(self):   
    def get_cvg_stat(self):    
    def remove_rgns_num(self, max_num):
    def remove_rgns_cvg(self, min_cvg):

#######################################
                        
class region_nd(Region):
    def convert_to_text_lines(self, sn, N, n ):
    def set_from_text_lines(self, line ):
    def print(self):
    def print_short(self):
    def set_ave_cvg_depth(self):
    def get_cvg(self):
    def ave_cvg_depth(self):
    def copy(self, update = True):
    def update(self, a_rng, cm = True):
    def update_intersection(self, a_rng, cm=True):

#######################################
            
class regions_nd:
    def convert_to_text_lines(self, sn = 0):
    def set_from_text_lines(self,lines):
    def print(self):
    def print_short(self):
    def copy(self, update = True):
    def isempty(self):
    def set_rgn(self, rgn):
    def get_span( self ):               
    def get_span2( self ):               
    def get_length( self ):               
    def get_cvgs_and_lens(self):
    def set_cvg(self):
    def order(self):
    def merge( self, rgns ): 
    def get_intersection_cvg(self, rgn):
    def has_intersection_with(self, rgn):
    def update(self, rgn = None, xc=True, cm = True):
    def update_intersection(self, rgn = None, xc=True, cm = True):
    def alloc_cm(self):    
    def get_cvg_stat(self):    
    def remove_rgns_num(self, max_num):
    def remove_rgns_cvg(self, min_cvg):
    def check_bistrand(self):

##########################################################################
## Object for loading SAM/BAM
##########################################################################

def get_sam_end_pos( sam_line ): 

LINE_VALID = 0
NO_MORE_LINE = 4
LINE_INVALID = 2

CONTINUED = 0
NEW_CHRM = 1
# LINE_INVALID = 2
NOT_SORTED = 3

class sam_obj:
    def close(self):
    def get_lines(self):
    def read_line(self):
    def get_sam_line(self):
    def get_sam_lines_for_one_chrm(self):
    def get_rgns_for_one_chrm(self):
    def get_one_overlaped_rgns(self):
    def get_one_overlaped_sam(self):

##########################################################################
## Functions to build contigs
##########################################################################

def gen_seq(nt_char,Len):
def get_rgns_from_sam_line_ext( sam_line, cm = True, wgt = 1 ): # , max_intron_len = MAX_INTRON_LENGTH ):
#### For building

def get_rows( lst, wh ):
def find_pair(qname_lst):
def get_weight(sam_line_lst):
def find_closest( rgns_m1, rgns_m2, min_dist = MAX_DIST_UC ):
def get_regions_all_from_sam( sam_line_lst, verbose = 1, sdiv = 10, cm = True, sa = 0 ):

class my_sparse_mat:
    def set(self,r,c,v):
    def get(self,r,c):
    def add(self,r,c,v):
    def n_entries(self):
    def get_keys(self):
    def print(self):

def connect_regions( rgns_lst_m, rgns_lst_nd, rgns_lst_sti, rgn_idx, my_pair, verbose = 1, sdiv = 10 ):

##########################################################################
## Functions for contigs trimming
##########################################################################

def check_connection( r_m, r_n, max_dev, max_dev_d = 0  ):
def check_connection_m( r_m, rs_nd, max_dev, max_dev_d = 0 ):
def check_connection_nd( rs_m, r_nd, max_dev = MAX_DEV_NM ):
def rem_nm_2long_and_2thin( rs_nd, rs_m, verbose = False, sdiv = 10 ):
def adj_nd( rs_nd, rs_m, verbose = False, sdiv = 10 ):
def get_connection_mat(rs_nd, max_dev_n, max_dev_d, max_dev_i):
def arg_max(vec):
def arg_min(vec):
def check_complte_overlap( rs_m, rs_nd_or_sti, target_type ): 
def merge_nearby_ndi(rs_nd, max_dev_n, max_dev_d, max_dev_i, no_ovlp_ind_vec = None ):
def trim_m( rs_nd, rs_m, rs_sti, max_dev, max_dev_d, verbose = False ):
def trim_d( rs_nd, rs_m, verbose = False, sdiv = 10 ):
def trim_n_short( rs_nd, rs_m, verbose = False, sdiv = 10 ):
def split_m( rs_nd, rs_m, rs_sti, verbose = False ):
def add_i( rs_nd, rs_m, rs_sti, verbose = False ):

##########################################################################
## Functions to handle splice-graph
##########################################################################

def BFS(graph,start,end):
def BFS1(graph,start,end, max_num_hops = 10):
def BFS2(graph,start,end, max_num_paths = 1000):
def BFS3(graph,start,end, max_num_hops = 10):
def BFS_all(graph,start, end_nodes):
def BFS_all2(graph,start,end_nodes, max_num_paths = 1000):
def get_start_nodes(grp):
def get_end_nodes(grp):
def get_ambiguous_nodes(grp_f, grp_b, nodes, edges):
def get_all_paths(grp_f, grp_b = None, nodes = None, edges = None):
def try_to_get_all_paths(grp_f, grp_b = None, nodes = None, edges = None, max_n_paths = 1000):
def get_initial_graph( rs_m, rs_nd ):
def get_graph( rs_m, rs_nd ):

##############################
## Functions to run ElasticNet

def run_ElasticNet( X, y, l1r = 0.5, alpha = 1 ):
def run_ElasticNet_path( X, y, l1r = 0.5, n_alphas = 100 ):

###############################
## functions for graph handling

def group_nodes(grp_f):
def minimize_graph(g_f_in, g_b_in):
def get_partial_path(g_f, g_b, start):
def check_new_start( g_f, g_b, nidx ):
def get_minimal_graph(g_f, g_b, n_nodes, n_edges, nodes, wgt_edge = None, ga = None):
def get_org_path( p_lst, nodes_ext ):
def find_closest_from( rs_m, k, b_proc, gf, gb ):
def compare_path(p1, p2):
def get_eq_path_idx(plst, p):

##########################################################################
## Functions and objects to handle GTF file
##########################################################################

# GTF_line = collections.namedtuple('GTF_line', 'chr, src, feature, start, end, score, strand, frame, attr')
GTF_line = collections.namedtuple('GTF_line', 'chr, src, feature, start, end, score, strand, frame, attr, gid, gname, tid, tname')
CHR, SRC, FEATURE, GSTART, GEND, SCORE, STRAND, FRAME, ATTR, GID, GNAME, TID, TNAME = [i for i in range(13)]

def print_gtf(line):
def print_gtf_lines(lines):
def print_gtf_lines_to_str(lines):
def get_gtf_lines_from_rgns( r_lst_m, r_lst_nd ):
def get_id_and_name_from_gtf_attr(str_attr):
def get_other_attrs_from_gtf_attr(str_attr):
def load_gtf( fname, verbose = True, ho = False ):
def save_gtf( fname, gtf_line_lst, hdr = None ):
def save_gtf2( fname, gtf_line_lst = None, hdr = None, fo = None, close = False ):
def save_gff( fname, gtf_line_lst ):

##########################################################################
## Functions and objects to build splice-graph
##########################################################################

def get_strand_char(strand):
def get_tr_name( tr_lst ):
def get_gtf_lines_from_transcripts(tlst, path_lst, nodes, edges, strand = 0 ):

class splice_graph:
    def revise_graphs( self, to_del_nodes, to_del_edges ):
    def get_splice_graphs(self, rs_m, rs_nd):
    def get_all_paths(self):
    def get_cvgs_and_lens(self):
    def get_stuffs(self, rs_m, rs_nd):
    def revise_stuffs(self, to_del_nodes, to_del_edges):
        
    def rem_edge_start(self):
    def rem_unconnected(self, len_th = 100, cvg_th = 2):
    def rem_low_cvg(self, ath = 0, c_th = None):
    def connect_closest_unconnected_nodes(self):
    def build( self, rs_m, rs_nd, trim = True, len_th = 100 ): 
    def select_nodes_and_edges(self, len_th = 200, cvg_th = 0.01):
    def select_path_and_remove_nodes_and_edges(self, n_sel_max, psel = 0.5, len_th = 200):
    def convert_to_text_lines(self, sel = None):
    def print_minimal(self):
    def print_short(self):
    def print_full(self):
    def get_paths_over_minimal_graph(self):
    def dconv(self, v, abn_norm = 'log'):
    def get_z_and_G_using(self, cvg_node_n_edge, len_node_n_edge, n_nodes, graph_f, graph_b, p_lst, abn_norm = 'lin'):
    def get_valid_volume(self, cvg_node_n_edge, len_node_n_edge, n_nodes, graph_f, graph_b, p_lst, abn_norm = 'lin'):
    def naive_sic_ext(self, z, G, cvgs, lens, p_lst, ntr = 0):
    def lasso_sic_ext(self, z, G, cvgs, lens, p_lst, ntr = 0):
    def isolasso_ext(self, z, G, cvgs, lens, ntr = 0, n_alphas = 100):
    def get_abundance_for_single_tr_gene(self):
    def get_trs_from_abn(self, Abn, strands = [], coding_ind = []):
    def select_edges_to_del( self, edges, strand ):
    def select_edges_and_nodes_to_del( self, edges, nodes, strand, len_th = 200 ):
    def td_and_ae(self, len_th = 50, method = 'lasso', g_ret = False):
    def td_and_ae_using_annotation(self, gd, len_th = MIN_TR_LENGTH, method = 'lasso', g_ret = False, verbose = True):

##########################################################################
## Gene/Transcript descriptor
##########################################################################

def find_possible_ss_codon_pos_in(tseq, target = 'start', c = False):
def gtf_line_to_str(gtf_line):
def parse_gtf_lines_and_split_into_genes_old( gtf_lines, g_or_t = 'gene', verbose = False ):
def parse_gtf_lines_and_split_into_genes( gtf_lines, g_or_t = 'gene', verbose = False ):
def get_base_cds_from_gtf_lines(gtf_lines):
def set_fa_header(name, Len, abn, strand, cdng):
     
POS_info = collections.namedtuple('POS_info', 'abs_start, abs_end, start, end') # one-base

class location_finder:
    def add( self, abs_start, abs_end, start):
    def abs_pos( self, loc ):
    def rel_pos( self, abs_loc ):
    def get_cds_regions( self, rel_start_pos, rel_stop_pos, tlen, chrm, istrand):
    def print(self):

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

NV_info_ext_tr = collections.namedtuple('NV_info_ext_tr', 'chr, pos_ref, pos_new, gene_id, gene_name, v_type, v_len, cvg_depth, cvg_frac, \
                                  ref_prev, ref_seq, ref_next, alt_prev, alt_seq, alt_next, v_class, \
                                  v_class_tr, strand, cDNA_change, Codon_change, Protein_change, Protein_change2') #, Check')  # one-base

def get_nv_info_tr( pseq_in, istrand, rel_pos_in, nv, tid ):

class transcript_descriptor:

    def __init__(self, gtf_lines_of_a_tr = None, exon_rgns = None, cds_rgns = None, genome = None, cds = -1, fill = False, verbose = False):
    def get_cds_nv_info( self, nv_info_lst_from_gene, cds_rgns ):
    def get_org_coding_seq(self, cds_rgns, genome_seq):
    def get_transcript_tuple(self):
 
    def check_start_stop_codon_pos(self, exons, verbose = False):
    def get_td_cov_ratio(self, exons, rgns, sel):
    def get_td_cov(self, exons, rgns):
    def get_td_info(self):
    def check_if_start_stop_codon_is_covered(self, rgns, cds, target = 'start_codon'):
    def get_gtf_lines_from_exons(self, exons_rgns, rgns_rgns, cds_rgns, genome, sel, add_seq, connect = False):
    def get_fasta_lines_from_exons(self, exons_rgns, rgns_rgns, cds_rgns, genome, sel, \
                                   peptide = False, L_th_t = MIN_TR_LENGTH, L_th_p = MIN_PR_LENGTH):
    def update_info(self, exons_rgns, rgns_rgns, cds_rgns, genome, sel, peptide):
    def get_seq_from_exons(self, exons_rgns, rgns_rgns, cds_rgns, genome, sel, peptide):
    def get_coding_seq(self, seq, lof, cds_rgns, istrand, icds):
    def get_seq_from_genome(self, exons, cds, genome):
    def get_span(self):
    def print_short(self):
    def set(self, rgns, tr_info, verbose = False):
        
##################
## Gene descriptor
##################

def sort_descriptor_lst(d_lst, ref = 'chr'):
def sort_gtf_lines(gtf_lines):

NV_info_ext = collections.namedtuple('NV_info_ext', 'chr, pos_ref, pos_new, gene_id, gene_name, v_type, v_len, cvg_depth, cvg_frac, \
                                      ref_prev, ref_seq, ref_next, alt_prev, alt_seq, alt_next, v_class, v_class_tr') # one-base

class gene_descriptor:

    def __init__(self, gtf_lines_of_a_gene = None, genome = None, icds = -1, fill = False, \
                 gcnt = 0, verbose = False, Cov_th = MIN_COV_TO_SEL, Abn_th = MIN_ABN_TO_SEL, read_len = 100):
    def init(self, grp, verbose = False):
    def add_tr(self, nodes, edges, p_lst, tr_info_lst, verbose = False):
    def check_nv_pos( self, nv_span ):
    def check_nv_pos_exon( self, nv_span ):
    def get_gene_level_nv_info(self):
    def find_snp_from_rgns(self):
    def get_gid_n_gname_list(self):
    def set_cov_n_abn_th(self, Cov_th, Abn_th):

    def add_tr_rgns(self, ki, rgns):
    def get_td_exp_info(self):
    def get_span(self):
    def get_td_span(self,n):
    def merge(self, gd):
    def get_tids(self):
    def get_total_abn( self ):
    def set_tr_info( self, nf ):
    def remove_indel_and_combine_frags(self):
    def update(self):
    def update_td_info(self, genome = None, sel = 0, peptide = False):
    def get_gtf_lines_from_exons(self, genome = None, sel = 0, add_seq = True, connect = False):
    def get_fasta_lines_from_exons(self, genome = None, sel = 0, peptide = False, \
                                   L_th_t = MIN_TR_LENGTH, L_th_p = MIN_PR_LENGTH): 
    def check_tr_1(self, tr, frag_len = 80, g_th = 10, abn_th_t = 1, abn_th_i = 1, iso_frac_th = 0.01, len_th = 200 ):
    def check_tr_2(self, tr, frag_len = 80, g_th = 10, abn_th_t = 1, abn_th_i = 1, iso_frac_th = 0.01, len_th = 200, ne_th = 4 ):
    def get_seq_from_genome(self, n, genome):
    def compare_seqs(self, s1, s2, tid, verbose = False):
    def print_cds_info(self, chr_seq):
    def compare_seqs_from_cds_and_genome(self, chr_seq):
    def get_all_seq_from_genome(self, genome, abn_th = 0, cov_th = 0, len_th_t = 200, len_th_p = 50):
    def get_fasta_lines_from_genome(self, genome, abn_th = 0, cov_th = 0, len_th_t = 200, len_th_p = 50):
    def print_exon(self):

##########################################################################
## Functions to initialize GD/TD from GTF
##########################################################################

def select_coding_genes_from_gtf_file(gtf_file):
def combine_genes_per_chr( gd_lst, verbose = False ):
def get_gene_descriptor(gtf_lines, genome = None, fill = False, cg = True, verbose = False, n_cores = 1):
def mc_core_gen_descriptor(gx):
def mc_core_mapping( a ):
def pack_gene_descriptor( gd_lst, chrs ):
def parse_and_combine_genes_and_rgns( gd_lst_of_lst, chr_lst, rgns_lst_mi, rgns_lst_nd, rgns_lst_sti, \
                                     n_cores = 1, genome = None, verbose = False ):
def mc_core_combine_genes_and_rgns_per_chr( rs_tuple ):
def combine_genes_and_rgns_per_chr( gd_lst, rgns_lst_mi, rgns_lst_nd, rgns_lst_sti, verbose = False ):
def combine_genes_and_rgns( gd_lst, rgns_lst_mi, rgns_lst_nd, rgns_lst_sti, n_cores = 1, verbose = False ):

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
def reverse_complement(seq):
def find_all_s_in_str(str,s):
def check_orf_condition_forward_from_start(tseq):
def check_equal_range(ss_lst, ss):
def check_orf_condition_forward(tseq):
def check_orf_condition(tseq, strand = 1):
def get_attrs_from_fa_header(str_attr):
def gen_proteome_from_trascriptome(hdr_lst, tseq_lst, len_th = MIN_PR_LENGTH, verbose = True, mx_cnt = 0, trareco = False, ignore_s = False):
def Generate_Proteome(tr_fa, len_th = MIN_PR_LENGTH, verbose = True, mx_cnt = 0, trareco = False, fname_out = None, ignore_s = False):
    
##########################################################################
## Functions for StringFix main (1)
##########################################################################

def get_max_cvg(rs):
def save_transcripts( fname, tr_lst ):
def save_transcripts2( fname, tr_lst ):
def get_c_from_istrand(istrand):
def get_istrand_from_c(strand_c):
def get_str_from_icdng( cds ):
def get_icdng_from_str( c_or_n ):
def convert_into_tr(header, seq):    
def load_transcripts(file_name, verbose = True):
def load_ref_tr_sim(file_name, verbose = True):
def print_tr(tr_lst):

def check_rs_m(rs_m, hdr = '' ):
def save_rgns( fname, rgns_lst, rd_len, num_rds, ho = False ):
def get_id_from_hdr(hdr):
def load_rgns( fname, mode, n_rgns = 0, verbose = False ):
def load_rgns_nd( fname, mode, n_rgns, verbose = False ):
def trim_contigs( rgns_lst_m, rgns_lst_nd, rgns_lst_sti, verbose = 1, sdiv = 10 ):
def rem_low_cvg_rgns( rs_m, rs_nd, rs_sti = None ):
def trim_contigs_single( rs_m, rs_nd, rs_sti, gcnt = 0, rem_low_cvg = True, verbose = 1, sdiv = 10 ):
def check_bistrand( r_mi, r_nd ):
def find_kf_and_kb( exons, rs_m ):
def mc_core_get_tr(rs_tuple):
def get_transcripts_mc( rgns_lst_mi, rgns_lst_nd, rgns_lst_st, read_len, annot = None, \
                        n_cores = NUM_CORES, len_th = MIN_TR_LENGTH, method = 'lasso', \
                        nrec = 0, start = 0, verbose = True, sdiv = 20 ):
def get_transcripts( rgns_lst_mi, rgns_lst_nd, rgns_lst_st, read_len, annot = None, len_th = MIN_TR_LENGTH, \
                     method = 'lasso', nrec = 0, start = 0, verbose = True, sdiv = 20 ):

############################
#### StringFix main ########

def get_tpm(tr_lst):
def filter_rgns( r_lst_m, r_lst_nd, r_lst_sti, vol_th, s_th = 0.9 ):
def check_rgns( rgns_lst_mi, rgns_lst_nd ):
def check_strand( r_m_lst, r_nd_lst ):
def mc_core_build_cntg(sam_lst_n_sa):
def build_contigs(s_lst_of_lst, title = ''):
def build_contigs_mc(s_lst_of_lst, n_cores = NUM_CORES, title = ''):
def proc_read_sam( sam_obj, q ):
def save_rgns_obj(filename, rgns_lst_m, rgns_lst_nd, rgns_lst_sti, rd_len, n_rds, med_frag_len ):
def load_rgns_obj(filename):
def save_obj(filename, obj ):
def load_obj(filename):

##########################################################################
## StringFix-Analysis
##########################################################################

def filter_trs_len( fa_lines_list, min_len = 0 ):
def filter_trs_1(trs, frag_len = 80, g_th = 10, abn_th_t = 1, abn_th_i = 1, \
               iso_frac_th = 0.01, len_th = 200, verbose = True ):
def filter_trs_2(trs, frag_len = 80, g_th = 10, abn_th_t = 1, abn_th_i = 1, \
               iso_frac_th = 0.01, len_th = 200, ne_th = 4, verbose = True):
def get_file_name( path_file_name ):
def get_path_name( path_file_name ):
def mc_core_get_gtf_and_fasta_pf(gd):

def StringFix_analysis(sam_file, gtf = None, genome_file = None, suffix = None, jump = 0, sa = 2, cbyc = False, \
                       n_cores = 1, min_frags_per_gene = 2, len_th = MIN_TR_LENGTH, out_tr = False, sav_rgn = False, out_dir = None ):

Gene_Tr_info = collections.namedtuple('Gene_Tr_info', 'tr_id, tr_name, gene_id, gene_name, chr, start, end, strand, coding, num_exons, tr_len' )

##########################################################################
## StringFix addon's
##########################################################################

def build_gene_transcript_table( gtf_file ):
def trim_header(fname_fa):
def trim_header_and_add_strand_info(fname_fa, gff_file):
def StringFix_GFFRead(gtf_file, genome_file, n_cores = 1):
def Generate_Reference(gtf_file, genome_file, peptide = True, out_dir = None, suffix = None):
    
##########################################################################
## StringFix-synthesis
##########################################################################

SNV_info = collections.namedtuple('SNV_info', 'chr, pos_ref, pos_new, gene_id, gene_name, v_type, v_len, cvg_depth, cvg_frac, \
                                   ref_prev, ref_seq, ref_next, alt_prev, alt_seq, alt_next') # one-base
OS_info = collections.namedtuple('OS_info', 'os, start, end') # one-base

def find_snp(sg, sr, cmat, chrm, pos_abs, os, gin):
def compare_seq2( s1, s2 ):

class offset_finder:
    def __init__(self):
    def add( self, os, start, end):
    def find_os( self, pos ):
    def find_os_seq( self, pos, prev_i, mark = '' ):
    def make_it_compact( self ):
    def get_bndry( self, pos ):
    def get_bndry_seq( self, pos, prev_i ):
    def print(self):
            
def mc_core_reconstruction(ggc_tuple):
def mc_core_get_gtf_and_fasta_pt(gd):
def to_nv_simple( nv ):

def StringFix_synthesis(gtf_file, genome_file, rev = True, n_cores = 1, out_dir = None, gds = None):

def StringFix_assemble( Input = None, genome_fa = None, annot_gtf = None, out_dir = 'SFix_out', \
                        n_cores = 4, out_custom_genome = False, suffix = None, \
                        mcv = 0.5, mcd = 1, mtl = 200, mpl = 50, mdi = 2, mdd = 2, mdp = 3, \
                        mdf = 0.2, n_p = 16, xsa = True, jump_to = 0 ):


#########################################################
## StringFix-addon                                                                              ##
## developed by Seokhyun Yoon (syoon@dku.edu) Oct. 04, 2020   ##
#########################################################

def which( ai, value = True ) :
def get_info_from_tr_name( tns ):
def get_performance(trinfo, cvg_th = [80,90,95], f_to_save = None, ref = 0, verbose = False):
def run_blast( inpt_fa, ref_fa, path_to_blast = None, trareco = True, ref_info = False, \
                 dbtype = 'nucl', ref = 0, sdiv = 10, mx_ncand = 6, verbose = False):

##################################################################################
## Functions to (1) select specific chrm and (2) only coding genes in a GTF
##################################################################################

def sort_gtf_lines_lst(gtf_lines_lst):
def select_coding_genes_from_gtf_file(gtf_file, genome_file):
def select_chr_from_gtf_file(gtf_file, chrm = '1'):

##################################################################################
## Functions to handle simulated reads (add trareco header, split fastQ)
##################################################################################

def fasta_add_trareco_header( ref_tr, sim_profile, read_len, suffix = None, cov_th = 0.8 ):
def load_fastq(file_genome, verbose = False ):
def save_fastq( file_genome, genome_dict, verbose = False, title = 'fastQ' ):
def fasta_sim_read_split( sim_read, dsr = 1 ):
def fasta_sim_read_downsample( sim_read, dsr = 1 ):
    
##################################################################################
## Functions to add SNV into a genome
##################################################################################

SNV = collections.namedtuple('SNV', 'chr, pos_new, pos_org, type, len, seq_new, seq_org, ex_start, ex_end')

def get_snv_type(pi, pd):
def rand_nucleotide_except(nts):
def rand_nucleotides(num):
def save_snv_info( file_name, snv_lst, verbose = False ):
def generate_snv_with_gtf( genome, gtf_lines_sorted, mu = 200, li = 3, ld = 3, lv = 2, pi = 0.1, pd = 0.1 ):
def generate_snv(genome, gtf_lines, l_inter_snv = L_INTER_SNV, li = LI, ld = LD, lv = LV, pi = P_INS, pd = P_DEL):
    
##################################################################################
## Functions for evaluation of SNV detection
##################################################################################

def get_span_lst(rgns_lst_mi, Type = 'M'):
def select_snvs( df_snv, span_lst, rgns_lst_mi, Type = 'M', mdev = 12 ):
def matching_snvs( df_snv_sel, df_detected, dev_tol = 3 ):
            
##########################################################################
## Seokhyun Yoon (syoon@dku.edu) Oct. 04, 2020
##########################################################################




        

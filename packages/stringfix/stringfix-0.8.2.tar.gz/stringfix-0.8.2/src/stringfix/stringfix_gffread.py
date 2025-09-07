#!/usr/bin/python3

import numpy as np
import argparse
import numpy as np
import argparse, time, os, pickle, datetime, sys

try:    
    import StringFix.stringfix_core as sf
    from StringFix.stringfix_core  import StringFix_analysis, StringFix_synthesis, Generate_Reference, StringFix_GFFRead
    from StringFix.stringfix_core import run_blast
    SFIX_ERR = 0
except ImportError:
    SFIX_ERR = 1
    try:
        import stringfix_core as sf
        from stringfix_core  import StringFix_analysis, StringFix_synthesis, Generate_Reference, StringFix_GFFRead
        from stringfix_core import run_blast
    except ImportError:
        SFIX_ERR = 2

## file_name_wo_ext = StringFix_analysis(sam_file, gtf = None, suffix = 'stringfix', jump = 0, sa = 2, cbyc = False, \
##                    n_cores = 1, min_frags_per_gene = 2, len_th = 200, out_tr = False )
## file_name_wo_ext, file_name_genome = StringFix_synthesis(gtf_file, genome_file, rev = True, n_cores = 1)
## file_name_ref_tr, file_name_ref_pr = Generate_Reference(gtf_file, genome_file)
## file_name_wo_ext = StringFix_GFFRead(gtf_file, genome_file = None, n_cores = 1)
## df, dft, df_sel = run_blast( inpt_fa, ref_fa, path_to_blast = None, trareco = True, ref_info = False, \
##            dbtype = 'nucl', ref = 0, sdiv = 10, mx_ncand = 6, verbose = False)

def get_args():
    parser = argparse.ArgumentParser(description='', formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser._action_groups.pop()
    required = parser.add_argument_group('REQUIRED PARAMETERS')
    optional = parser.add_argument_group('OPTIONAL PARAMETERS')

    required.add_argument('-gtf', type=str, metavar='',
                          help='GTF/GFF file to generate transcriptome and proteome FASTA file. Genome fasta file must be provided')
    required.add_argument('-gnm', type=str, metavar='',
                          help='Genome fasta files to be used for transcriptome/proteome generation')
    # optional.add_argument('-p', type=str,  metavar='',
    #                    help='Number of cores to use', default="6")
    optional.add_argument('-sfx', type=str,  metavar='',
                        help='Suffix to be used for output files. Output file names will be input_file_name_Suffix_types.extension', default= None)
    optional.add_argument('-mcv', type=str,  metavar='',
                        help='Minimum read coverage for inclusion in the output GTF/GFF and transcriptome/proteome [0~1]. For a length L transcript, \
                              it will be included in the output if at least mcv*L bases are covered by reads', default="0.5")
    optional.add_argument('-mcd', type=str,  metavar='',
                        help='Minimum base coverage depth.', default="1")
    optional.add_argument('-mtl', type=str,  metavar='',
                        help='Minimum transcript length in bases.', default="200")
    optional.add_argument('-mpl', type=str,  metavar='',
                        help='Minimum protein (amino acid sequence) length.', default="50")
    args = parser.parse_args()
    return args, parser


def main():

    print('+-------------------------------+')
    print('|   StringFix add-on: gffread   |')
    print('+-------------------------------+')

    args, parser = get_args()
    if (args.gtf is None) | (args.gnm is None):
        parser.print_help()
        return
    else:
        if SFIX_ERR > 1:
            print('StringFix ERROR: StringFix not found.')
            sys.exit(1)
        elif SFIX_ERR == 1:
            print('StringFix not installed. Loaded from local directory.')

        genome_fa = args.gnm
        gtf_file = args.gtf
        # n_cores = int(args.p)
        sf.MIN_TR_LENGTH = int(args.mtl)
        sf.MIN_PR_LENGTH = int(args.mpl)
        sf.MIN_ABN_TO_SEL = np.float(args.mcd)
        sf.MIN_COV_TO_SEL = np.float(args.mcv)

        # file_name_wo_ext = StringFix_GFFRead(gtf_file, genome_file = genome_fa, n_cores = 1)
        fa_file_tr, fa_file_pr = Generate_Reference(gtf_file, genome_file = genome_fa, peptide = True, suffix = args.sfx )

if __name__=="__main__":
    main()


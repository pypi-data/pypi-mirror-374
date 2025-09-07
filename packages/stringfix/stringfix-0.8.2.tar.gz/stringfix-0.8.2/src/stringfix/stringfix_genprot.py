#!/usr/bin/python3

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

    required.add_argument('-tr', type=str, metavar='',
                          help='FASTA file containing transcriptome')
    optional.add_argument('-out', type=str,  metavar='',
                        help='Output path/file_name.ext', default="None")
    optional.add_argument('-mpl', type=str,  metavar='',
                        help='Minimum protein (amino acid sequence) length.', default="0")
    optional.add_argument('-i', action = 'store_true',
                        help='Set this option to ignore strand info.')
    args = parser.parse_args()
    return args, parser


def main():

    print('+-------------------------------+')
    print('|   StringFix add-on: gen_prot  |')
    print('+-------------------------------+')

    args, parser = get_args()
    if (args.tr is None):
        parser.print_help()
        return
    else:
        if SFIX_ERR > 1:
            print('StringFix ERROR: StringFix not found.')
            sys.exit(1)
        elif SFIX_ERR == 1:
            print('StringFix not installed. Loaded from local directory.')

        fa_file_tr = args.tr
        sf.MIN_PR_LENGTH = int(args.mpl)

        print(args.i)
        sf.Generate_Proteome(fa_file_tr, len_th = sf.MIN_PR_LENGTH, verbose = True, mx_cnt = 0, trareco = False, fname_out = args.out, ignore_s = args.i)

if __name__=="__main__":
    main()


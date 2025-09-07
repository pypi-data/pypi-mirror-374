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

## df, dft, df_sel = run_blast( inpt_fa, ref_fa, path_to_blast = None, trareco = True, ref_info = False, \
##            dbtype = 'nucl', ref = 0, sdiv = 10, mx_ncand = 6, verbose = False)

def get_args():
    parser = argparse.ArgumentParser(description='', formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser._action_groups.pop()
    required = parser.add_argument_group('REQUIRED PARAMETERS')
    optional = parser.add_argument_group('OPTIONAL PARAMETERS')

    required.add_argument('-input', type=str, metavar='',
                          help='Input transcriptome/proteome FASTA file')
    required.add_argument('-ref', type=str, metavar='',
                          help='Reference transcriptome/proteome FASTA file')
    required.add_argument('-dbtype', type=str, metavar='',
                          help='nucl or prot')
    optional.add_argument('-n', type=str,  metavar='',
                        help='Maximum number of candidates to match', default="1")
    optional.add_argument('-s', type=str,  metavar='',
                        help='[y/n] Stringfix header line availability', default='n')
    optional.add_argument('-v', type=str,  metavar='',
                        help='[y/n] Verbosity', default="y")
    args = parser.parse_args()
    return args, parser


def main():

    print('+-------------------------------+')
    print('|  StringFix add-on: Run Blast  |')
    print('+-------------------------------+')

    args, parser = get_args()
    if (args.input is None) | (args.ref is None) | (args.dbtype is None):
        parser.print_help()
        return
    else:

        if SFIX_ERR > 1:
            print('StringFix ERROR: StringFix not found.')
            sys.exit(1)
        elif SFIX_ERR == 1:
            print('StringFix not installed. Loaded from local directory.')

        tr_fa = args.input
        ref_fa = args.ref
        dbtype = args.dbtype
        mx_ncand = args.n

        verbose = True
        if (args.v == 'n'): verbose = False

        info = True
        if (args.s == 'n'): info = False

        run_blast( inpt_fa = tr_fa, ref_fa = ref_fa, trareco = info, dbtype = dbtype, ref = 0, mx_ncand = mx_ncand, verbose = verbose)
if __name__=="__main__":
    main()


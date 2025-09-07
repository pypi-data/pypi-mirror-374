#!/usr/bin/python3

import argparse

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

def get_args():
    parser = argparse.ArgumentParser(description='', formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser._action_groups.pop()
    required = parser.add_argument_group('REQUIRED PARAMETERS')

    required.add_argument('-gtf', type=str, metavar='',
                          help='GTF/GFF file where transcript info. is to be extracted.')
    args = parser.parse_args()
    return args, parser

def main():

    args, parser = get_args()
    if (args.gtf is None):
        parser.print_help()
        return
    else:
        if SFIX_ERR > 1:
            print('StringFix ERROR: StringFix not found.')
            sys.exit(1)
        elif SFIX_ERR == 1:
            print('StringFix not installed. Loaded from local directory.')

        gt_lst = sf.build_gene_transcript_table( args.gtf )

if __name__=="__main__":
    main()


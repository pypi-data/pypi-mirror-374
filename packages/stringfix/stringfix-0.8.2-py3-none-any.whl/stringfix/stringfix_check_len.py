#!/usr/bin/python3

import numpy as np
import argparse, time, os, pickle, datetime, sys

try:    
    import StringFix.stringfix_core as sf
    from StringFix.stringfix_core  import StringFix_analysis, StringFix_synthesis, Generate_Reference, StringFix_GFFRead
    from StringFix.stringfix_core import run_blast
except ImportError:
    print('StringFix not installed. Try to load from local directory')
    try:
        import stringfix_core as sf
        from stringfix_core  import StringFix_analysis, StringFix_synthesis, Generate_Reference, StringFix_GFFRead
        from stringfix_core import run_blast
    except ImportError:
        print('ERROR: StringFix not found.')
        sys.exit(1)

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

    required.add_argument('-fa', type=str, metavar='', help='FASTA file')
    optional.add_argument('-min_len', type=str, metavar='', help='Minimum Length', default='0')
    args = parser.parse_args()
    return args, parser


def main():

    args, parser = get_args()
    min_len = int(args.min_len)
    if (args.fa is None):
        parser.print_help()
        return
    else:
        hdr_lst, seq_lst = sf.load_fasta1(args.fa)
        Len = np.zeros(len(seq_lst))
        for k, seq in enumerate(seq_lst): 
            Len[k] = len(seq)

        if min_len == 0:
            print('%s: N.seq= %i, Mn/MxLen= %i,%i' % (args.fa, len(seq_lst), Len.min(), Len.max()))    
        else:
            print('%s: N.seq= %i, Mn/MxLen= %i,%i' % (args.fa, len(seq_lst), Len.min(), Len.max()), end = '')    
            fa_lines = []
            for k in range(len(Len)):
                if len(seq_lst[k]) >= min_len:
                    fa_lines.append( '>' + hdr_lst[k] + '\n' )
                    fa_lines.append( seq_lst[k] + '\n' )

            f = open(args.fa, 'wt+')
            f.writelines(fa_lines)
            f.close()

            hdr_lst, seq_lst = sf.load_fasta1(args.fa)
            Len = np.zeros(len(seq_lst))
            for k, seq in enumerate(seq_lst): 
                Len[k] = len(seq)

            print(' -> N.seq: %i, MnLen: %i' % (len(seq_lst), Len.min()))    

if __name__=="__main__":
    main()


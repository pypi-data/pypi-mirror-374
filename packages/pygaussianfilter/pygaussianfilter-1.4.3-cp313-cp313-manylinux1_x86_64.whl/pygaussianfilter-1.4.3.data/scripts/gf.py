#!python
from gaussianfilter import gaussianfilter
from sys import argv
from os.path import exists, dirname
import re

def usage():
    print("USAGE:", argv[0], " <iotag> <tracein> <ff> <fw> <traceout>")
    print('     [iotag] choose among a2s, s2a, s2s, a2a (ascii2sac, sac2ascii...)')
    print('     [tracein] depends on iotag, if ascii needs 2 columns real array')
    print('     [ff] value for central frequency filter in Hz')
    print('     [fw] gaussian filter width in Hz')
    print('     [traceout] output filter trace, depends on iotag')

if '__main__' == __name__:
    if len(argv) < 6:
        usage();
        exit(1);
    else:
        iotag = argv[1]
        if iotag not in ['s2s', 'a2a', 's2a', 'a2s']:
            raise Exception("iotag must be in 's2s', 'a2a', 's2a', 'a2s'")
        tracein = argv[2]
        if not exists(tracein):
            raise Exception(tracein+" doesn't exist.")
        traceout = argv[5]
        if dirname(traceout) != "" and not exists(dirname(traceout)):
            raise Exception(dirname(traceout)+" doesn't exist.")
        ff = argv[3]
        fw = argv[4]
        float_regex = '([0-9]+(\.[0-9]+)?)|(\.[0-9]+)'
        if not re.match(float_regex, ff):
            raise Exception("ff must be a floating point number.")
        ff = float(ff)
        if not re.match(float_regex, fw):
            raise Exception("fw must be a floating point number.")
        fw = float(fw)
#        print("iotag=",iotag)
#        print("tracein=", tracein)
#        print("traceout=", traceout)
#        print("ff=", ff)
#        print("fw=", fw)
        gaussianfilter(iotag, tracein, traceout, ff, fw) 

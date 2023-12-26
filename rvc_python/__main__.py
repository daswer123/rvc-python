import argparse
import sys
from argparse import ArgumentParser

from rvc_python.infer import infer_file

# Set current folder as main

parser = ArgumentParser(description="RVC inference")
# pitch=sys.argv[1]
# input_path=sys.argv[2]
# index_path=sys.argv[3]
# method=sys.argv[4]#harvest or pm
# output_path=sys.argv[5]
# model_path=sys.argv[6]
# index_rate=float(sys.argv[7])
# device=sys.argv[8]
# filter_radius=int(sys.argv[9])
# resample_sr=int(sys.argv[10])
# rms_mix_rate=float(sys.argv[11])
# protect=float(sys.argv[12])

parser.add_argument("-pi","--pitch", default=0, type=int, help="Transpose (integer, number of semitones, raise by an octave: 12, lower by an octave: -12)")
parser.add_argument("-i","--input", type=str, help="Path to input file")
parser.add_argument("-ip","--index", type=str, nargs='?', default="-", help="Path to index file (optional)")
parser.add_argument("-me","--method", type=str, default="harvest", choices=['harvest',"crepe","rmvpe",'pm'], help="pitch extraction algorithm ('rmvpe' is the best, 'pm': faster extraction but lower-quality speech; 'harvest': better bass but extremely slow; 'crepe': better quality but GPU intensive)")
parser.add_argument("-v","--version", type=str, default="v2", choices=['v1',"v2"], help="v1 or v2")
parser.add_argument("-o","--output", type=str, nargs='?', default="out.wav", help="Output path for results")
parser.add_argument("-mp","--model", type=str, help="Path to model file")
parser.add_argument("-ir","--index_rate", type=float, default=0.5, help="Search feature ratio")
parser.add_argument("-d","--device", type=str, default="cuda:0", help="device to use (e.g., cpu:0, cuda:0)")
parser.add_argument("-fr","--filter_radius", type=int, default=3, help="If >=3: apply median filtering to the harvested pitch results. The value represents the filter radius and can reduce breathiness")
parser.add_argument("-rsr","--resample_sr", type=int, default=0, help="Resample the output audio in post-processing to the final sample rate. Set to 0 for no resampling")
parser.add_argument("-rmr","--rms_mix_rate", type=float,default=0.25 ,help="Use the volume envelope of the input to replace or mix with the volume envelope of the output. The closer the ratio is to 1, the more the output envelope is used")
parser.add_argument("-pr",'--protect' ,type=float,default=0.33 ,help='Protect voiceless consonants and breath sounds to prevent artifacts such as tearing in electronic music. Set to 0.5 to disable. Decrease the value to increase protection, but it may reduce indexing accuracy')


if __name__ == "__main__":
    args = parser.parse_args()
    infer_file(
        input_path=args.input,
        model_path=args.model,
        index_path=args.index,
        device=args.device,
        f0method=args.method,
        f0up_key=args.pitch,
        opt_path=args.output,
        index_rate=args.index_rate,
        filter_radius=args.filter_radius,
        resample_sr=args.resample_sr,
        rms_mix_rate=args.rms_mix_rate,
        protect=args.protect,
        version=args.version
        )

# infer_file(input_path,model_path,index_path,device,method,output_path,index_rate,filter_radius,resample_sr,rms_mix_rate,protect,pitch)
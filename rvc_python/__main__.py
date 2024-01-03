import argparse
import sys
import os
from argparse import ArgumentParser

from rvc_python.infer import infer_file,infer_files

parser = ArgumentParser(description="RVC inference")
# Create a mutually exclusive group for input - only one of them can be provided
input_group = parser.add_mutually_exclusive_group(required=True)
input_group.add_argument("-i", "--input", type=str, help="Path to input file")
input_group.add_argument("-d", "--dir", type=str, help="Directory path containing audio files")

parser.add_argument("-pi","--pitch", default=0, type=int, help="Transpose (integer, number of semitones)")
parser.add_argument("-ip","--index", type=str, nargs='?', default="", help="Path to index file (optional)")
parser.add_argument("-me","--method", type=str, default="harvest", choices=['harvest', "crepe", "rmvpe", 'pm'], help="Pitch extraction algorithm")
parser.add_argument("-v","--version", type=str, default="v2", choices=['v1', "v2"], help="Model version")
parser.add_argument("-o","--output", type=str, nargs='?', default="out.wav", help="Output path for single file, or output directory for multiple files")
parser.add_argument("-mp","--model", type=str, required=True, help="Path to model file")
parser.add_argument("-ir","--index_rate", type=float, default=0.5, help="Search feature ratio")
parser.add_argument("-de","--device", type=str, default="cuda:0", help="Device to use (e.g., cpu:0, cuda:0)")
parser.add_argument("-fr","--filter_radius", type=int, default=3, help="Apply median filtering to the pitch results")
parser.add_argument("-rsr","--resample_sr", type=int, default=0, help="Resample rate for the output audio")
parser.add_argument("-rmr","--rms_mix_rate", type=float,default=0.25 ,help="Volume envelope mix rate")
parser.add_argument("-pr",'--protect' ,type=float,default=0.33 ,help='Protect voiceless consonants and breath sounds')

args = parser.parse_args()

if args.input:
    # Single file processing
    inferred_path = infer_file(
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
elif args.dir:
    # Directory processing
    processed_files = infer_files(
        dir_path=args.dir,
        model_path=args.model,
        index_path=args.index,
        device=args.device,
        f0method=args.method,
        opt_dir=os.path.abspath(os.path.dirname(args.output)),
        index_rate=args.index_rate,
        filter_radius=args.filter_radius,
        resample_sr=args.resample_sr,
        rms_mix_rate=args.rms_mix_rate,
        protect=args.protect,
        version=args.version
    )

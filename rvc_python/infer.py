import os,sys,pdb,torch
now_dir = os.getcwd()
sys.path.append(now_dir)
import argparse
import glob
import sys
import torch
from loguru import logger
from multiprocessing import cpu_count

from download_model import download_rvc_models

# Set current folder as main
this_dir = os.path.dirname(os.path.abspath(__file__))

download_rvc_models(this_dir)

f0up_key=sys.argv[1]
input_path=sys.argv[2]
index_path=sys.argv[3]
f0method=sys.argv[4]#harvest or pm
opt_path=sys.argv[5]
model_path=sys.argv[6]
index_rate=float(sys.argv[7])
device=sys.argv[8]
is_half=bool(sys.argv[9])
filter_radius=int(sys.argv[10])
resample_sr=int(sys.argv[11])
rms_mix_rate=float(sys.argv[12])
protect=float(sys.argv[13])

rmvpe_onxx = "base_models/rmvpe.onnx"
print(sys.argv)

now_dir=os.getcwd()
sys.path.append(now_dir)
from rvc_python.modules.vc.modules import VC
from rvc_python.configs.config import Config
from scipy.io import wavfile

file_dir = os.path.dirname(os.path.abspath(__file__))

config = Config(file_dir,device,is_half)
vc = VC(config)


vc.get_vc(model_path)
wav_opt = vc.vc_single(
    sid=1,
    input_audio_path=input_path,
    f0_up_key=f0up_key,
    f0_method=f0method,
    file_index=index_path,
    index_rate=index_rate,
    filter_radius=filter_radius,
    resample_sr=resample_sr,
    rms_mix_rate=rms_mix_rate,
    protect=protect,
    f0_file="",
    file_index2=""
)
wavfile.write(opt_path, vc.tgt_sr, wav_opt)


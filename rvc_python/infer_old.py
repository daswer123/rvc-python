
from rvc_python.modules.vc.modules import VC
from rvc_python.configs.config import Config
from scipy.io import wavfile
import os

from glob import glob
import soundfile as sf

from rvc_python.modules.vc.modules import VC
from rvc_python.download_model import download_rvc_models

def infer_file(
    input_path,
    model_path,
    index_path = "",
    device = "cpu:0",
    f0method = "harvest",
    opt_path = "out.wav",
    index_rate = 0.5,
    filter_radius = 3,
    resample_sr = 0,
    rms_mix_rate = 1,
    protect = 0.33,
    f0up_key = 0,
    version = "v2"
):
    lib_dir = os.path.dirname(os.path.abspath(__file__))

    download_rvc_models(lib_dir)
    config = Config(lib_dir,device)
    vc = VC(lib_dir,config)

    vc.get_vc(model_path,version)
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
    return opt_path

def infer_files(
    dir_path,
    model_path,
    paths=[],
    index_path="",
    device="cuda:0",
    f0method="harvest",
    opt_dir="out/",
    index_rate=0.5,
    filter_radius=3,
    resample_sr=0,
    rms_mix_rate=1,
    protect=0.33,
    f0up_key=0,
    version="v2",
    out_format="wav"
):
    # Create output directory if it does not exist
    os.makedirs(opt_dir, exist_ok=True)

    # Determine the files to process
    audio_files = paths if paths else glob(os.path.join(dir_path, '*.*'))

    # Initialize some common VC-related variables outside of loop
    lib_dir = os.path.dirname(os.path.abspath(__file__))
    download_rvc_models(lib_dir)

    config = Config(lib_dir, device)

    vc = VC(lib_dir, config)
    vc.get_vc(model_path, version)

    processed_files = []

    for input_audio_path in audio_files:
        output_filename = os.path.splitext(os.path.basename(input_audio_path))[0] + '.' + out_format
        opt_path = os.path.join(opt_dir, output_filename)

        wav_opt = vc.vc_single(
            sid=1,
            input_audio_path=input_audio_path,
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
        processed_files.append(opt_path)

    return processed_files

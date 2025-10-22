# infer.py

import os
from glob import glob
import soundfile as sf
from scipy.io import wavfile
from rvc_python.modules.vc.modules import VC
from rvc_python.configs.config import Config
from rvc_python.download_model import download_rvc_models

class RVCInference:
    def __init__(self, models_dir="rvc_models", device="cpu:0", model_path=None, index_path="", version="v2"):
        self.models_dir = models_dir
        self.device = device
        self.lib_dir = os.path.dirname(os.path.abspath(__file__))
        self.config = Config(self.lib_dir, self.device)
        self.vc = VC(self.lib_dir, self.config)
        self.current_model = None
        self.models = {}

        # Default parameters
        self.f0method = "harvest"
        self.f0up_key = 0
        self.index_rate = 0.5
        self.filter_radius = 3
        self.resample_sr = 0
        self.rms_mix_rate = 1
        self.protect = 0.33

        # Download Models (if necessary)
        download_rvc_models(self.lib_dir)

        # Load available models
        self.models = self._load_available_models()

        # Load model if model_path is provided
        if model_path:
            self.load_model(model_path, version=version, index_path=index_path)

    def _load_available_models(self):
        """Loads a list of available models from the directory."""
        models = {}
        for model_dir in glob(os.path.join(self.models_dir, "*")):
            if os.path.isdir(model_dir):
                model_name = os.path.basename(model_dir)
                pth_file = glob(os.path.join(model_dir, "*.pth"))
                index_file = glob(os.path.join(model_dir, "*.index"))
                if pth_file:
                    models[model_name] = {
                        "pth": pth_file[0],
                        "index": index_file[0] if index_file else None
                    }
        return models

    def set_models_dir(self, new_models_dir):
        """Sets a new directory for models and reloads available models."""
        if not os.path.isdir(new_models_dir):
            raise ValueError(f"Directory {new_models_dir} does not exist")
        self.models_dir = new_models_dir
        self.models = self._load_available_models()

    def list_models(self):
        """Returns a list of available models."""
        return list(self.models.keys())

    def load_model(self, model_path_or_name, version="v2", index_path=""):
        """Loads a model into memory.

        Args:
            model_path_or_name (str): Path to the model file or model name if in models_dir.
            version (str): Version of the model ('v1' or 'v2').
            index_path (str): Path to the index file (optional).
        """
        # If model_path_or_name is a name in self.models, load from models_dir
        if model_path_or_name in self.models:
            model_info = self.models[model_path_or_name]
            model_path = model_info["pth"]
            index_path = model_info.get("index", "")
            model_name = model_path_or_name
        else:
            # Else, assume it's a direct path
            model_path = model_path_or_name
            model_name = os.path.basename(model_path)
            if index_path and not os.path.isfile(index_path):
                raise ValueError(f"Index file {index_path} not found.")
            # Update models dict
            self.models[model_name] = {"pth": model_path, "index": index_path}

        if not os.path.isfile(model_path):
            raise ValueError(f"Model file {model_path} not found.")

        self.vc.get_vc(model_path, version)
        self.current_model = model_name
        print(f"Model {model_name} loaded.")

    def unload_model(self):
        """Unloads the current model from memory."""
        if self.current_model:
            self.vc = VC(self.lib_dir, self.config)
            self.current_model = None
            print("Model unloaded from memory.")
        else:
            print("No model loaded.")

    def set_params(self, **kwargs):
        """Sets parameters for generation."""
        valid_params = [
            "index_rate", "filter_radius", "resample_sr",
            "rms_mix_rate", "protect", "f0up_key", "f0method"
        ]
        for key, value in kwargs.items():
            if key in valid_params:
                setattr(self, key, value)
            else:
                print(f"Warning: parameter {key} not recognized and will be ignored.")

    def infer_file(self, input_path, output_path):
        """Processes a single file.

        Args:
            input_path (str): Path to the input audio file.
            output_path (str): Path to save the output audio file.
        """
        if not self.current_model:
            raise ValueError("Please load a model first.")

        model_info = self.models[self.current_model]
        file_index = model_info.get("index", "")

        result = self.vc.vc_single(
            sid=0,
            input_audio_path=input_path,
            f0_up_key=self.f0up_key,
            f0_method=self.f0method,
            file_index=file_index,
            index_rate=self.index_rate,
            filter_radius=self.filter_radius,
            resample_sr=self.resample_sr,
            rms_mix_rate=self.rms_mix_rate,
            protect=self.protect,
            f0_file="",
            file_index2=""
        )

        # Handle error case where vc_single returns a tuple (info, (times, wav_opt))
        if isinstance(result, tuple) and len(result) == 2:
            info, audio_data = result
            if isinstance(audio_data, tuple):
                times, wav_opt = audio_data
                if wav_opt is None:
                    raise RuntimeError(f"Voice conversion failed: {info}")
            else:
                wav_opt = audio_data
        else:
            wav_opt = result
        
        wavfile.write(output_path, self.vc.tgt_sr, wav_opt)
        return output_path

    def infer_dir(self, input_dir, output_dir):
        """Processes all files in a directory.

        Args:
            input_dir (str): Path to the input directory containing audio files.
            output_dir (str): Path to the output directory to save processed files.
        """
        if not self.current_model:
            raise ValueError("Please load a model first.")

        os.makedirs(output_dir, exist_ok=True)
        audio_files = glob(os.path.join(input_dir, '*.*'))
        processed_files = []

        for input_audio_path in audio_files:
            output_filename = os.path.splitext(os.path.basename(input_audio_path))[0] + '.wav'
            output_path = os.path.join(output_dir, output_filename)
            self.infer_file(input_audio_path, output_path)
            processed_files.append(output_path)

        return processed_files

    def set_device(self, device):
        """Sets the device for computations.

        Args:
            device (str): Device identifier (e.g., 'cpu:0', 'cuda:0').
        """
        self.device = device
        self.config.device = device
        self.vc.device = device

# Usage example:
if __name__ == "__main__":
    rvc = RVCInference(
        device="cuda:0",
        model_path="path/to/model.pth",
        index_path="path/to/index.index",
        version="v2"
    )
    rvc.set_params(f0up_key=2, protect=0.5)

    rvc.infer_file("input.wav", "output.wav")
    rvc.infer_dir("input_dir", "output_dir")

    rvc.unload_model()

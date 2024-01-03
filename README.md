# RVC Python

Using RVC via console or python scripts

Feel free to make PRs or use the code for your own needs

## Changelog

You can keep track of all changes on the [release page](https://github.com/daswer123/rvc-python/releases)

## TODO
- [x] Batch generation via console
- [x] Possibility to use inference import through code

## Installation

Simple installation :

```bash
pip install rvc-python
```

This will install all the necessary dependencies, including a **CPU support only** version of PyTorch

I recommend that you install the **GPU version** to improve processing speed ( up to 3 times faster )

### Windows
```bash
python -m venv venv
venv\Scripts\activate
pip install rvc-python
pip install torch==2.1.1+cu118 torchaudio==2.1.1+cu118 --index-url https://download.pytorch.org/whl/cu118
```

### Linux
```bash
python -m venv venv
source venv\bin\activate
pip install rvc-python
pip install torch==2.1.1+cu118 torchaudio==2.1.1+cu118 --index-url https://download.pytorch.org/whl/cu118
```

## Usage

```bash
python -m rvc_python [-h] -i INPUT or -d INPUT_DIR -mp MODEL [-pi PITCH]
                     [-ip INDEX] [-me METHOD] [-v VERSION]
                     [-o OUTPUT] [-ir INDEX_RATE]
                     [-d DEVICE]  [-fr FILTER_RADIUS]
                     [-rsr RESAMPLE_SR]
                     [-rmr RMS_MIX_RATE][-pr PROTECT]
```

### Options

- `-h`, `--help`:
     Show this help message and exit.

- `-i INPUT`, `--input INPUT` (mandatory):
     Path to input file.

- `-d INPUT_DIR`, `--dir` (mandatory)
     Path to dir with input files

- `-mp MODEL`, `--model MODEL` (mandatory):
    Path to model file.

The following options are optional:

- `-pi PITCH`, `--pitch PITCH`:
     Transpose integer; number of semitones. Raise by an octave with +12 or lower by an octave with -12.

- `-ip INDEX`, `--index INDEX`:
     Path to index file.

- `-me METHOD`, `--method METHOD`:
     Pitch extraction algorithm choices: ['harvest', 'crepe', 'rmvpe', 'pm'].

- `-v VERSION`, `--version VERSION`:
     Version of the software or model ('v1' or 'v2').

- `-o OUTPUT`, `--output OUTPUT`:
     Output path for results (default is "out.wav").
     If you specify -d, you need to specify the path to the folder where the files will be saved.

- `-ir INDEX_RATE`, `--index_rate INDEX_RATE`:
   Search feature ratio.

- `-d DEVICE`, `--device DEVICE`:
   Device to use for processing (e.g., 'cpu' or 'cuda:0').

- `-fr FILTER_RADIUS`, `--filter_radius FILTER_RADIUS`:
   Apply median filtering to pitch results. A larger value can reduce breathiness.

- `-rsr RESAMPLE_SR `,  ` --resample_sr RESAMPLE_SR`:
  Resample output audio in post-processing. Set "0" for no resampling.

- `-rmr RMS_MIX_RATE`, `--rms_mix_rate RMS_MIX_RATE`:
      Mix rate between input volume envelope and output volume envelope. Closer to "1" uses more from the output.

- `-pr PROTECT `, `--protect PROTECT`:
      Protects voiceless consonants and breath sounds from artifacts such as tearing in electronic music. Decrease value for increased protection but may affect indexing accuracy.



### Example Command via console

**Single file**
```bash
python -m rvc_python -i .\test\test.wav -mp .\test\art_lebedev\artemiy_lebedev.pth
```

**Batch**
```bash
python -m rvc_python -d ./test -o "./out_dir" -mp ./test/art_lebedev/artemiy_lebedev.pth
```

This example will process the audio file located at ".\test\test.wav" using the model file ".\test\art_lebedev\artemiy_lebedev.pth". All other settings will be default unless additional flags are provided.

### Example via python

```python
from rvc_python.infer import infer_file, infer_files

# To process a single file:
result = infer_file(
    input_path="./path_to_file",
    model_path="./model/path_to_model.pth",
    index_path="",  # Optional: specify path to index file if available
    device="cuda:0", # Use cpu or cuda
    f0method="harvest",  # Choose between 'harvest', 'crepe', 'rmvpe', 'pm'
    pitch=0,  # Transpose setting
    output="out.wav",  # Output file path
    index_rate=0.5,
    filter_radius=3,
    resample_sr=0,  # Set to desired sample rate or 0 for no resampling.
    rms_mix_rate=0.25,
    protect=0.33,
    version="v2"
)

print("Inference completed. Output saved to:", result)

# To process multiple files in a directory:
results = infer_files(
    dir_path="./input_dir/",  # Directory containing input audio files
    paths=[], # You can specify each file separately, then files from dir_path files will not be counted
    opt_dir="./output_dir/",  # Directory where output files will be saved
    model_path="./model/path_to_model.pth",
    index_path="",  # Optional: specify path to index file if available
    device="cuda:0", # Use cpu or cuda
    f0method="harvest",  # Choose between 'harvest', 'crepe', 'rmvpe', 'pm'
    pitch=0,  # Transpose setting
    index_rate=0.5,
    filter_radius=3,
    resample_sr=0,  # Set to desired sample rate or 0 for no resampling.
    rms_mix_rate=0.25,
    protect=0.33,
    version="v2"
    out_format="wav"
)

print(f"Inference completed for batch processing. Check the '{results}' directory for output files.")
```


### Demo

https://github.com/daswer123/rvc-python/assets/22278673/6ecb590e-8a71-46aa-8ade-ba3fcfd75009


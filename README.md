# RVC Python

Using RVC via console or python scripts

Feel free to make PRs or use the code for your own needs

## Changelog

You can keep track of all changes on the [release page](https://github.com/daswer123/rvc-python/releases)

## TODO
- [ ] Batch generation via console
- [ ] Possibility to use inference import through code

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
python -m rvc_python [-h] -i INPUT -mp MODEL [-pi PITCH]
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

- `-ir INDEX_RATE`, `--index_rate INDEX_RATE`:
   Search feature ratio.

- `-d DEVICE`, `--device DEVICE`:
   Device to use for processing (e.g., 'cpu' or 'cuda:0').

- `-fr FILTER_RADIUS`, `--filter_radius FILTER_RADIUS`:
   Apply median filtering to pitch results. A larger value can reduce breathiness.

- `-rsr RESAMPLE_SR `,  ` --resample_sr RESAMPLE_SR`:
  Resample output audio in post-processing. Set "0" for no resampling.

 - 	`-rmr RMS_MIX_RATE`, 	 `--rms_mix_rate RMS_MIX_RATE`:
      Mix rate between input volume envelope and output volume envelope. Closer to "1" uses more from the output.

 - 	`-pr PROTECT `, 	  `--protect PROTECT`:
      Protects voiceless consonants and breath sounds from artifacts such as tearing in electronic music. Decrease value for increased protection but may affect indexing accuracy.



### Example Command

```bash
python -m rvc_python -i .\test\test.wav -mp .\test\art_lebedev\artemiy_lebedev.pth
```

This example will process the audio file located at ".\test\test.wav" using the model file ".\test\art_lebedev\artemiy_lebedev.pth". All other settings will be default unless additional flags are provided.


### Demo

https://github.com/daswer123/rvc-python/assets/22278673/6ecb590e-8a71-46aa-8ade-ba3fcfd75009


# RVC Python

A Python implementation for using RVC (Retrieval-based Voice Conversion) via console, Python scripts, or API.

## Table of Contents
- [Features](#features)
- [Installation](#installation)
- [Usage](#usage)
  - [Command Line Interface](#command-line-interface)
  - [Python Module](#python-module)
  - [API](#api)
- [Model Management](#model-management)
- [Options](#options)
- [Advanced Setup (GPU Acceleration)](#advanced-setup-gpu-acceleration)
- [Changelog](#changelog)
- [Contributing](#contributing)

## Demo

https://github.com/daswer123/rvc-python/assets/22278673/6ecb590e-8a71-46aa-8ade-ba3fcfd75009

## Features

- Console interface for single file or batch processing
- Python module for integration into other projects
- API server for remote processing
- Support for both CPU and GPU acceleration

## Installation

### Basic Installation (CPU only)

```bash
pip install rvc-python
```

### Recommended Installation (with GPU support)

For Windows:
```bash
python -m venv venv
venv\Scripts\activate
pip install rvc-python
pip install torch==2.1.1+cu118 torchaudio==2.1.1+cu118 --index-url https://download.pytorch.org/whl/cu118
```

For Linux:
```bash
python -m venv venv
source venv/bin/activate
pip install rvc-python
pip install torch==2.1.1+cu118 torchaudio==2.1.1+cu118 --index-url https://download.pytorch.org/whl/cu118
```

## Usage

### Command Line Interface

The CLI supports two modes: `cli` for direct file processing and `api` for starting an API server.

```bash
python -m rvc_python [-h] {cli,api} ...
```

#### CLI Mode
Process a single file or batch of files:

```bash
python -m rvc_python cli -i INPUT -o OUTPUT -mp MODEL [options]
```

Example:
```bash
python -m rvc_python cli -i input.wav -o output.wav -mp path/to/model.pth -de cuda:0
```

#### API Mode
Start the API server:

```bash
python -m rvc_python api -mp MODEL [-p PORT] [-l] [options]
```

Example:
```bash
python -m rvc_python api -mp path/to/model.pth -p 5050 -l
```

### Python Module

```python
from rvc_python.infer import RVCInference

rvc = RVCInference(device="cuda:0")
rvc.load_model("path/to/model.pth")
rvc.infer_file("input.wav", "output.wav")
```

### API

The API server provides several endpoints for voice conversion and model management. Here's a detailed breakdown of each endpoint:

#### 1. Convert Audio
- **Endpoint**: `POST /convert`
- **Description**: Converts an audio file using the currently loaded model.
- **Request Body**:
  ```json
  {
    "audio_data": "base64_encoded_audio"
  }
  ```
- **Response**: The converted audio file (WAV format)
- **Example**:
  ```python
  import requests
  import base64

  url = "http://localhost:5050/convert"
  with open("input.wav", "rb") as audio_file:
      audio_data = base64.b64encode(audio_file.read()).decode()

  response = requests.post(url, json={"audio_data": audio_data})

  with open("output.wav", "wb") as output_file:
      output_file.write(response.content)
  ```

#### 2. List Available Models
- **Endpoint**: `GET /models`
- **Description**: Returns a list of all available models.
- **Response**: JSON array of model names
- **Example**:
  ```python
  response = requests.get("http://localhost:5050/models")
  models = response.json()
  print("Available models:", models)
  ```

#### 3. Load a Model
- **Endpoint**: `POST /models/{model_name}`
- **Description**: Loads a specific model for use in conversions.
- **Response**: Confirmation message
- **Example**:
  ```python
  response = requests.post("http://localhost:5050/models/my_model")
  print(response.json())
  ```

#### 4. Get Current Parameters
- **Endpoint**: `GET /params`
- **Description**: Retrieves the current parameter settings.
- **Response**: JSON object with current parameters
- **Example**:
  ```python
  response = requests.get("http://localhost:5050/params")
  print("Current parameters:", response.json())
  ```

#### 5. Set Parameters
- **Endpoint**: `POST /params`
- **Description**: Updates the parameters for voice conversion.
- **Request Body**:
  ```json
  {
    "params": {
      "f0method": "harvest",
      "f0up_key": 0,
      "index_rate": 0.5,
      "filter_radius": 3,
      "resample_sr": 0,
      "rms_mix_rate": 0.25,
      "protect": 0.33
    }
  }
  ```
- **Response**: Confirmation message
- **Example**:
  ```python
  params = {
    "f0method": "harvest",
    "f0up_key": 2,
    "protect": 0.5
  }
  response = requests.post("http://localhost:5050/params", json={"params": params})
  print(response.json())
  ```

#### 6. Upload a New Model
- **Endpoint**: `POST /upload_model`
- **Description**: Uploads a new model (as a zip file) to the server.
- **Request**: Multipart form data with a zip file
- **Response**: Confirmation message
- **Example**:
  ```python
  with open("new_model.zip", "rb") as zip_file:
      files = {"file": ("new_model.zip", zip_file)}
      response = requests.post("http://localhost:5050/upload_model", files=files)
  print(response.json())
  ```

#### 7. Set Computation Device
- **Endpoint**: `POST /set_device`
- **Description**: Sets the device (CPU/GPU) for computations.
- **Request Body**:
  ```json
  {
    "device": "cuda:0"
  }
  ```
- **Response**: Confirmation message
- **Example**:
  ```python
  response = requests.post("http://localhost:5050/set_device", json={"device": "cuda:0"})
  print(response.json())
  ```

## Model Management

Models are stored in the `rvc_models` directory by default. Each model should be in its own subdirectory and contain:

- A `.pth` file (required): The main model file.
- An `.index` file (optional): For improved voice conversion quality.

Example structure:
```
rvc_models/
├── model1/
│   ├── model1.pth
│   └── model1.index
└── model2/
    └── model2.pth
```

You can add new models by:
1. Manually placing them in the `rvc_models` directory.
2. Using the `/upload_model` API endpoint to upload a zip file containing the model files.

## Options

### Input/Output Options
- `-i`, `--input`: Input audio file (CLI mode)
- `-d`, `--dir`: Input directory for batch processing (CLI mode)
- `-o`, `--output`: Output file or directory

### Model Options
- `-mp`, `--model`: Path to the RVC model file
- `-md`, `--models_dir`: Directory containing RVC models (default: `rvc_models` in the current directory)
- `-ip`, `--index`: Path to the index file (optional)
- `-v`, `--version`: Model version (v1 or v2)

### Processing Options
- `-de`, `--device`: Computation device (e.g., "cpu", "cuda:0")
- `-me`, `--method`: Pitch extraction method (harvest, crepe, rmvpe, pm)
- `-pi`, `--pitch`: Pitch adjustment in semitones
- `-ir`, `--index_rate`: Feature search ratio
- `-fr`, `--filter_radius`: Median filtering radius for pitch
- `-rsr`, `--resample_sr`: Output resampling rate
- `-rmr`, `--rms_mix_rate`: Volume envelope mix rate
- `-pr`, `--protect`: Protection for voiceless consonants

### API Server Options
- `-p`, `--port`: API server port (default: 5050)
- `-l`, `--listen`: Allow external connections to API server

## Changelog

For a detailed list of changes and updates, please see the [Releases page](https://github.com/daswer123/rvc-python/releases).

## Contributing

Contributions are welcome! Feel free to submit pull requests or open issues for bugs and feature requests.

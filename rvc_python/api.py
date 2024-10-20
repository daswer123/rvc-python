# api.py

from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response, JSONResponse
from loguru import logger
from pydantic import BaseModel
import edge_tts
import tempfile
import base64
import shutil
import zipfile
import os

class SetDeviceRequest(BaseModel):
    device: str

class ConvertAudioRequest(BaseModel):
    audio_data: str  # Base64 encoded audio data

class SetParamsRequest(BaseModel):
    params: dict

class SetModelsDirRequest(BaseModel):
    models_dir: str

class TTSRequest(BaseModel):
    text: str
    voice: str | None = "Microsoft Server Speech Text to "
    rate: str | None = "+0%"
    volume: str | None = "+0%"
    pitch: str | None = "+0Hz"

def setup_routes(app: FastAPI):
    @app.post("/convert")
    async def rvc_convert(request: ConvertAudioRequest):
        """
        Converts audio data using the currently loaded model.
        Accepts a base64 encoded audio data in WAV format.
        Returns the converted audio as WAV data.
        """
        if not app.state.rvc.current_model:
            raise HTTPException(status_code=400, detail="No model loaded. Please load a model first.")

        with tempfile.NamedTemporaryFile(delete=False) as tmp_input:
            input_path = tmp_input.name
            try:
                logger.info("Received request to convert audio")
                audio_data = base64.b64decode(request.audio_data)
                tmp_input.write(audio_data)
            except Exception as e:
                logger.error(f"Error decoding audio data: {e}")
                raise HTTPException(status_code=400, detail="Invalid audio data")

        with tempfile.NamedTemporaryFile(delete=False) as tmp_output:
            output_path = tmp_output.name

        try:
            app.state.rvc.infer_file(input_path, output_path)

            with open(output_path, "rb") as f:
                output_data = f.read()
            return Response(content=output_data, media_type="audio/wav")
        except Exception as e:
            logger.error(e)
            raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")
        finally:
            os.unlink(input_path)
            os.unlink(output_path)

    @app.post("/convert_file")
    async def rvc_convert_file(file: UploadFile = File(...)):
        """
        Converts an uploaded audio file using the currently loaded model.
        Accepts an audio file in WAV format.
        Returns the converted audio as WAV data.
        """
        if not app.state.rvc.current_model:
            raise HTTPException(status_code=400, detail="No model loaded. Please load a model first.")

        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp_input:
            input_path = tmp_input.name
            try:
                logger.info("Received file to convert")
                contents = await file.read()
                tmp_input.write(contents)
            except Exception as e:
                logger.error(f"Error reading uploaded file: {e}")
                raise HTTPException(status_code=400, detail="Invalid file")

        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp_output:
            output_path = tmp_output.name

        try:
            app.state.rvc.infer_file(input_path, output_path)

            with open(output_path, "rb") as f:
                output_data = f.read()
            return Response(content=output_data, media_type="audio/wav")
        except Exception as e:
            logger.error(e)
            raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")
        finally:
            os.unlink(input_path)
            os.unlink(output_path)

    @app.get("/models")
    def list_models():
        """
        Lists available models.
        Returns a JSON response with the list of model names.
        """
        return JSONResponse(content={"models": app.state.rvc.list_models()})

    @app.post("/models/{model_name}")
    def load_model(model_name: str):
        """
        Loads a model by name.
        The model must be available in the models directory.
        """
        try:
            app.state.rvc.load_model(model_name)
            return JSONResponse(content={"message": f"Model {model_name} loaded successfully"})
        except Exception as e:
            raise HTTPException(status_code=400, detail=str(e))

    @app.get("/params")
    def get_params():
        """
        Retrieves current parameters used for inference.
        Returns a JSON response with the parameters.
        """
        return JSONResponse(content={
            "f0method": app.state.rvc.f0method,
            "f0up_key": app.state.rvc.f0up_key,
            "index_rate": app.state.rvc.index_rate,
            "filter_radius": app.state.rvc.filter_radius,
            "resample_sr": app.state.rvc.resample_sr,
            "rms_mix_rate": app.state.rvc.rms_mix_rate,
            "protect": app.state.rvc.protect
        })

    @app.post("/params")
    def set_params(request: SetParamsRequest):
        """
        Sets parameters for inference.
        Accepts a JSON object with parameter names and values.
        """
        try:
            app.state.rvc.set_params(**request.params)
            return JSONResponse(content={"message": "Parameters updated successfully"})
        except Exception as e:
            raise HTTPException(status_code=400, detail=str(e))

    @app.post("/upload_model")
    async def upload_models(file: UploadFile = File(...)):
        """
        Uploads and extracts a ZIP file containing models.
        The models are extracted to the models directory.
        """
        try:
            with tempfile.NamedTemporaryFile(delete=False) as tmp_file:
                contents = await file.read()
                tmp_file.write(contents)

            with zipfile.ZipFile(tmp_file.name, 'r') as zip_ref:
                zip_ref.extractall(app.state.rvc.models_dir)

            os.unlink(tmp_file.name)

            # Update the list of models after upload
            app.state.rvc.models = app.state.rvc._load_available_models()

            return JSONResponse(content={"message": "Models uploaded and extracted successfully"})
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    @app.post("/set_device")
    def set_device(request: SetDeviceRequest):
        """
        Sets the device for inference (e.g., 'cpu:0' or 'cuda:0').
        """
        try:
            device = request.device
            app.state.rvc.set_device(device)
            return JSONResponse(content={"message": f"Device set to {device}"})
        except Exception as e:
            raise HTTPException(status_code=400, detail=str(e))

    @app.post("/set_models_dir")
    def set_models_dir(request: SetModelsDirRequest):
        """
        Sets a new directory for models.
        The directory must exist and contain valid models.
        """
        try:
            new_models_dir = request.models_dir
            app.state.rvc.set_models_dir(new_models_dir)
            return JSONResponse(content={"message": f"Models directory set to {new_models_dir}"})
        except Exception as e:
            raise HTTPException(status_code=400, detail=str(e))

    @app.get("/voices")
    async def list_voices():
        return JSONResponse(content={"voices": await edge_tts.list_voices()})

    @app.post("/tts")
    async def tts(request: TTSRequest):
        if not app.state.rvc.current_model:
            raise HTTPException(status_code=400, detail="No model loaded. Please load a model first.")

        tmp_input = tempfile.NamedTemporaryFile(delete=False, suffix=".wav")
        tmp_output = tempfile.NamedTemporaryFile(delete=False, suffix=".wav")
        try:
            logger.info("Received request to generate audio by tts")
            input_path = tmp_input.name
            output_path = tmp_output.name
            
            communicate = edge_tts.Communicate(
                text=request.text,
                voice=request.voice,
                rate=request.rate,
                volume=request.volume,
                pitch=request.pitch
            )
            await communicate.save(input_path)

            app.state.rvc.infer_file(input_path, output_path)

            output_data = tmp_output.read()
            return Response(content=output_data, media_type="audio/wav")
        except Exception as e:
            logger.error(e)
            raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")
        finally:
            tmp_input.close()
            tmp_output.close()
            os.unlink(tmp_input.name)
            os.unlink(tmp_output.name)

def create_app():
    app = FastAPI()

    # Add CORS middleware
    origins = ["*"]
    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    setup_routes(app)
    return app

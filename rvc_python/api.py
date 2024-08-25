from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response, JSONResponse
from loguru import logger
from pydantic import BaseModel
import tempfile
import base64
import shutil
import zipfile
import os

class ConvertAudioRequest(BaseModel):
    audio_data: str

class SetParamsRequest(BaseModel):
    params: dict

def setup_routes(app: FastAPI):
    @app.post("/convert")
    def rvc_convert(request: ConvertAudioRequest):
        tmp_input = tempfile.NamedTemporaryFile(delete=False, suffix=".wav")
        tmp_output = tempfile.NamedTemporaryFile(delete=False, suffix=".wav")
        try:
            logger.info("Received request to convert audio")
            audio_data = base64.b64decode(request.audio_data)
            tmp_input.write(audio_data)
            input_path = tmp_input.name
            output_path = tmp_output.name

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

    @app.get("/models")
    def list_models():
        return JSONResponse(content={"models": app.state.rvc.list_models()})

    @app.post("/models/{model_name}")
    def load_model(model_name: str):
        try:
            app.state.rvc.load_model(model_name)
            return JSONResponse(content={"message": f"Model {model_name} loaded successfully"})
        except Exception as e:
            raise HTTPException(status_code=400, detail=str(e))

    @app.get("/params")
    def get_params():
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
        try:
            app.state.rvc.set_params(**request.params)
            return JSONResponse(content={"message": "Parameters updated successfully"})
        except Exception as e:
            raise HTTPException(status_code=400, detail=str(e))

    @app.post("/upload_model")
    async def upload_models(file: UploadFile = File(...)):
        try:
            with tempfile.NamedTemporaryFile(delete=False) as tmp_file:
                shutil.copyfileobj(file.file, tmp_file)

            with zipfile.ZipFile(tmp_file.name, 'r') as zip_ref:
                zip_ref.extractall(app.state.rvc.models_dir)

            os.unlink(tmp_file.name)

            # Update the list of models after upload
            app.state.rvc.models = app.state.rvc._load_available_models()

            return JSONResponse(content={"message": "Models uploaded and extracted successfully"})
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    @app.post("/set_device")
    def set_device(device: str):
        try:
            app.state.rvc.set_device(device)
            return JSONResponse(content={"message": f"Device set to {device}"})
        except Exception as e:
            raise HTTPException(status_code=400, detail=str(e))

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

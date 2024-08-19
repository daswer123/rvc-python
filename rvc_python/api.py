from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response
from loguru import logger
from pydantic import BaseModel
import uvicorn
import tempfile
import base64

from infer import infer_file

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

class ConvertAudioRequest(BaseModel):
    model_path: str
    audio_data: str
    index_path: str = ""
    device: str = "cpu:0"
    f0method: str = "harvest"
    f0up_key: float = 0
    index_rate: float = 0.5
    filter_radius: float = 3
    resample_sr: float = 0
    rms_mix_rate: float = 1
    protect: float = 0.33
    version: str = "v2"

def start_server(port: int = 5050, listen: bool = False):
    """Start the API server"""
    host_ip = "0.0.0.0" if listen else "127.0.0.1"
    uvicorn.run(app, host=host_ip, port=port)

@app.post("/rvc_convert")
def rvc_convert(request: ConvertAudioRequest):
    tmp_input = tempfile.NamedTemporaryFile(delete=True, suffix=".wav")
    tmp_output = tempfile.NamedTemporaryFile(delete=True, suffix=".wav")
    try:
        logger.info("Received request to convert audio")
        audio_data = base64.b64decode(request.audio_data)
        tmp_input.write(audio_data)
        input_path = tmp_input.name
        output_path = tmp_output.name

        infer_file(
            input_path=input_path,
            opt_path=output_path,
            model_path=request.model_path,
            device=request.device,
            f0method=request.f0method,
            index_path=request.index_path,
            f0up_key=request.f0up_key,
            index_rate=request.index_rate,
            filter_radius=request.filter_radius,
            resample_sr=request.resample_sr,
            rms_mix_rate=request.rms_mix_rate,
            protect=request.protect,
            version=request.version
        )

        # Read all bytes from the output file
        output_data = tmp_output.read()

        return Response(content=output_data, media_type="audio/wav")
    except Exception as e:
        logger.error(e)
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")
    finally:
        tmp_input.close()
        tmp_output.close()

if __name__ == "__main__":
    start_server()
import argparse
import sys
import os
from argparse import ArgumentParser
import uvicorn
from rvc_python.infer import RVCInference
from rvc_python.api import create_app

def main():
    # Set up the argument parser
    parser = ArgumentParser(description="RVC inference - CLI and API")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # CLI parser
    cli_parser = subparsers.add_parser("cli", help="Run CLI inference")
    cli_parser.add_argument("-i", "--input", type=str, help="Path to input file")
    cli_parser.add_argument("-d", "--dir", type=str, help="Directory path containing audio files")
    cli_parser.add_argument("-o", "--output", type=str, default="out.wav", help="Output path for single file, or output directory for multiple files")
    cli_parser.add_argument("-mp", "--model", type=str, required=True, help="Path to model file")

    # API parser
    api_parser = subparsers.add_parser("api", help="Start API server")
    api_parser.add_argument("-p", "--port", type=int, default=5050, help="Port number for the API server")
    api_parser.add_argument("-l", "--listen", action="store_true", help="Listen to external connections")
    api_parser.add_argument("-pm", "--preload-model", type=str, help="Preload model on startup (optional)")

    # Common arguments for both CLI and API
    for subparser in [cli_parser, api_parser]:
        subparser.add_argument("-md", "--models_dir", type=str, default="rvc_models", help="Directory to store models")
        subparser.add_argument("-ip", "--index", type=str, default="", help="Path to index file (optional)")
        subparser.add_argument("-de", "--device", type=str, default="cpu:0", help="Device to use (e.g., cpu:0, cuda:0)")
        subparser.add_argument("-me", "--method", type=str, default="rmvpe", choices=['harvest', "crepe", "rmvpe", 'pm'], help="Pitch extraction algorithm")
        subparser.add_argument("-v", "--version", type=str, default="v2", choices=['v1', "v2"], help="Model version")
        subparser.add_argument("-ir", "--index_rate", type=float, default=0.6, help="Search feature ratio")
        subparser.add_argument("-fr", "--filter_radius", type=int, default=3, help="Apply median filtering to the pitch results")
        subparser.add_argument("-rsr", "--resample_sr", type=int, default=0, help="Resample rate for the output audio")
        subparser.add_argument("-rmr", "--rms_mix_rate", type=float, default=0.25, help="Volume envelope mix rate")
        subparser.add_argument("-pr", '--protect', type=float, default=0.5, help='Protect voiceless consonants and breath sounds')
        subparser.add_argument("-pi", "--pitch", default=0, type=int, help="Transpose (integer, number of semitones)")

    args = parser.parse_args()

    # Initialize RVCInference
    rvc = RVCInference(models_dir=args.models_dir, device=args.device)
    rvc.set_params(
        f0method=args.method,
        f0up_key=args.pitch,
        index_rate=args.index_rate,
        filter_radius=args.filter_radius,
        resample_sr=args.resample_sr,
        rms_mix_rate=args.rms_mix_rate,
        protect=args.protect
    )

    # Handle CLI command
    if args.command == "cli":
        rvc.load_model(args.model)
        if args.input:
            # Process single file
            rvc.infer_file(args.input, args.output)
            print(f"Processed file saved to: {args.output}")
        elif args.dir:
            # Process directory
            output_files = rvc.infer_dir(args.dir, args.output)
            print(f"Processed {len(output_files)} files. Output directory: {args.output}")
        else:
            print("Error: Either --input or --dir must be specified for CLI mode.")
            sys.exit(1)

    # Handle API command
    elif args.command == "api":
        # Create and configure FastAPI app
        app = create_app()
        app.state.rvc = rvc

        if args.preload_model:
            rvc.load_model(args.preload_model)

        # Set up server options
        host = "0.0.0.0" if args.listen else "127.0.0.1"
        print(f"Starting API server on {host}:{args.port}")

        # Run the server
        uvicorn.run(app, host=host, port=args.port)

    else:
        print("Error: Invalid command. Use 'cli' or 'api'.")
        sys.exit(1)

if __name__ == "__main__":
    main()

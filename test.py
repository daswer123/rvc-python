from rvc_python.infer import RVCInference


if __name__ == "__main__":
    rvc = RVCInference(models_dir="./models",device="cuda:0")
    print("Доступные модели:", rvc.list_models())

    rvc.load_model("zaluz")
    rvc.set_params(f0up_key=2, protect=0.5)

    rvc.infer_file("2.mp3", "output.wav")
    rvc.infer_file("2.mp3", "output1.wav")
    rvc.infer_file("2.mp3", "output2.wav")
    # rvc.infer_dir("input_dir", "output_dir")

    rvc.unload_model()

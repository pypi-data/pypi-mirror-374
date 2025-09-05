
import os
from misaki import zh, en
from kokoro_onnx import Kokoro
import soundfile as sf

script_path = os.path.realpath(__file__)
script_dir = os.path.dirname(script_path)
project_dir = os.path.dirname(os.path.dirname(script_dir))

# https://github.com/thewh1teagle/kokoro-onnx/blob/main/examples/chinese.py
DOWN_FILE = '''Download these files
https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.1/kokoro-v1.1-zh.onnx
https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.1/voices-v1.1-zh.bin
https://huggingface.co/hexgrad/Kokoro-82M-v1.1-zh/raw/main/config.json'''


# default_voice_for_lang = {
#     'en-us': 'af_nicole',
#     'cmn': 'zm_yunjian',
# }

# Misaki G2P with espeak-ng fallback
en_g2p = en.G2P(trf=False, british=False)
def en_callable(text: str) -> str:
    return en_g2p(text)[0]
g2p = zh.ZHG2P(version="1.1", en_callable=en_callable)

def check_exist(model_folder, name):
    path = os.path.join(model_folder, name)
    if not os.path.exists(path):
        print(f"Please download kokoro model file {name} to {model_folder}! Or set env var MD2VIDEO_KOKORO_MODEL_FOLDER.\n{DOWN_FILE}\n")
    return path

def text_to_speech(text, output_path, lang=None, speed=1.0):
    voice = "zf_001"
    model_folder = os.environ.get("MD2VIDEO_KOKORO_MODEL_FOLDER", kokoro, os.path.join(project_dir, "models"))
    onnx_path = check_exist(model_folder, "kokoro-v1.1-zh.onnx")
    bin_path = check_exist(model_folder, "voices-v1.1-zh.bin")
    vocab_config = check_exist(model_folder, "config.json")
    for p in [onnx_path, bin_path, vocab_config]:
        assert os.path.exists(p), "TTS model does not exists."
    kokoro = Kokoro(onnx_path, bin_path, vocab_config=vocab_config)
    phonemes, _ = g2p(text)
    samples, sample_rate = kokoro.create(phonemes, voice=voice, lang=lang, speed=speed, is_phonemes=True)
    sf.write(output_path, samples, sample_rate)
    assert os.path.exists(output_path)

# def text_to_speech(text, output_path, lang=None):
#     assert type(text) is str
#     if lang is None:
#         lang = os.environ.get("MD2VIDEO_LANG", 'cmn')
#     import tempfile
#     assert(output_path.endswith('.wav'))
    
#     temp_text = tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False)
#     temp_text_path = temp_text.name
#     try:
#         temp_text.write(text)
#         temp_text.close()  # Close file before subprocess uses it
        
#         # Run kokoro-tts command
#         kokoro_path = os.environ.get("MD2VIDEO_KOKORO", os.path.join(project_dir, 'kokoro-tts', 'kokoro-tts'))
#         voice = os.environ.get("MD2VIDEO_KOKORO_VOICE", default_voice_for_lang[lang])
#         assert kokoro_path is not None and os.path.exists(kokoro_path), "Please set path to kokoro-tts in MD2VIDEO_KOKORO"
#         sub = subprocess.run([sys.executable, kokoro_path, os.path.abspath(temp_text_path), os.path.abspath(output_path), '--voice', voice], 
#                       cwd=os.path.dirname(kokoro_path), check=True)
#         assert os.path.exists(output_path)
#     finally:
#         # Clean up temp file
#         if os.path.exists(temp_text_path):
#             os.unlink(temp_text_path)

import os
import edge_tts
import asyncio
from flask import Flask, render_template, request, send_from_directory, jsonify
app = Flask(__name__)
AUDIO_DIR = os.path.join(os.getcwd(), 'generated_audio')
os.makedirs(AUDIO_DIR, exist_ok=True)

voices = {
    'English': {
        'Emma': {'voice_id': 'en-US-EmmaNeural', 'styles': ['default', 'cheerful', 'sad']},
        'Jenny': {'voice_id': 'en-US-JennyNeural', 'styles': ['default', 'assistant']},
        'Tony': {'voice_id': 'en-US-TonyNeural', 'styles': ['default', 'formal']},
        'Guy': {'voice_id': 'en-US-GuyNeural', 'styles': ['default', 'newscast']},
        'Aria': {'voice_id': 'en-US-AriaNeural', 'styles': ['default', 'cheerful', 'chat']},
        'Davis': {'voice_id': 'en-US-DavisNeural', 'styles': ['default', 'calm']}
    },
    'Spanish': {
        'Alvaro': {'voice_id': 'es-ES-AlvaroNeural', 'styles': ['default']},
        'Elena': {'voice_id': 'es-ES-ElenaNeural', 'styles': ['default']},
        'Jorge': {'voice_id': 'es-MX-JorgeNeural', 'styles': ['default']},
        'Dalia': {'voice_id': 'es-MX-DaliaNeural', 'styles': ['default']}
    },
    'French': {
        'Henri': {'voice_id': 'fr-FR-HenriNeural', 'styles': ['default']},
        'Denise': {'voice_id': 'fr-FR-DeniseNeural', 'styles': ['default']},
        'Jerome': {'voice_id': 'fr-FR-JeromeNeural', 'styles': ['default']},
        'Alain': {'voice_id': 'fr-CA-AlainNeural', 'styles': ['default']}
    },
    'German': {
        'Katja': {'voice_id': 'de-DE-KatjaNeural', 'styles': ['default']},
        'Conrad': {'voice_id': 'de-DE-ConradNeural', 'styles': ['default']},
        'Amala': {'voice_id': 'de-DE-AmalaNeural', 'styles': ['default', 'cheerful']},
        'Klaus': {'voice_id': 'de-DE-KlausNeural', 'styles': ['default']}
    },
    'Italian': {
        'Diego': {'voice_id': 'it-IT-DiegoNeural', 'styles': ['default']},
        'Elsa': {'voice_id': 'it-IT-ElsaNeural', 'styles': ['default']},
        'Isabella': {'voice_id': 'it-IT-IsabellaNeural', 'styles': ['default', 'cheerful']}
    },
    'Japanese': {
        'Nanami': {'voice_id': 'ja-JP-NanamiNeural', 'styles': ['default', 'cheerful']},
        'Keita': {'voice_id': 'ja-JP-KeitaNeural', 'styles': ['default']},
        'Shiori': {'voice_id': 'ja-JP-ShioriNeural', 'styles': ['default']}
    },
    'Chinese': {
        'Xiaoxiao': {'voice_id': 'zh-CN-XiaoxiaoNeural', 'styles': ['default', 'cheerful']},
        'Yunyang': {'voice_id': 'zh-CN-YunyangNeural', 'styles': ['default', 'narration']},
        'Xiaoyi': {'voice_id': 'zh-CN-XiaoyiNeural', 'styles': ['default']}
    },
    'Korean': {
        'SunHi': {'voice_id': 'ko-KR-SunHiNeural', 'styles': ['default', 'cheerful']},
        'InJoon': {'voice_id': 'ko-KR-InJoonNeural', 'styles': ['default']},
    },
    'Russian': {
        'Dmitry': {'voice_id': 'ru-RU-DmitryNeural', 'styles': ['default']},
        'Svetlana': {'voice_id': 'ru-RU-SvetlanaNeural', 'styles': ['default']},
    },
    'Portuguese': {
        'Antonio': {'voice_id': 'pt-PT-AntonioNeural', 'styles': ['default']},
        'Francisca': {'voice_id': 'pt-PT-FranciscaNeural', 'styles': ['default']},
        'Manuela': {'voice_id': 'pt-BR-ManuelaNeural', 'styles': ['default', 'cheerful']}
    },
    'Multilingual': {
        'Emma (Multi)': {'voice_id': 'en-US-EmmaMultilingualNeural', 'styles': ['default']},
        'Guy (Multi)': {'voice_id': 'fr-FR-VivienneMultilingualNeural', 'styles': ['default']},
        'Serafina (Multi)': {'voice_id': 'de-DE-SeraphinaMultilingualNeural', 'styles': ['default']},
        'Florian (Multi)': {'voice_id': 'de-DE-FlorianMultilingualNeural', 'styles': ['default']},
        'Remy (Multi)': {'voice_id': 'fr-FR-RemyMultilingualNeural', 'styles': ['default']},
        'Ava (Multi)': {'voice_id': 'en-US-AvaMultilingualNeural', 'styles': ['default']},
        'Andrew (Multi)': {'voice_id': 'en-US-AndrewMultilingualNeural', 'styles': ['default']},
        'Brian (Multi)': {'voice_id': 'en-US-caBrianMultilingualNeural', 'styles': ['default']}
    }
}

@app.route('/')
def index():
    return render_template('index.html', voices=voices)

@app.route('/get_voice_info', methods=['GET'])
def get_voice_info():
    voice_id = request.args.get('voice_id')
    language = request.args.get('language')
    if language in voices and voice_id in voices[language]:
        return jsonify(voices[language][voice_id])
    return jsonify({'error': 'Voice not found'})

@app.route('/generate_audio', methods=['POST'])
async def generate_audio():
    text = request.form.get('text')
    language = request.form.get('language')
    voice = request.form.get('voice')
    style = request.form.get('style', 'default')
    
    # Format rate properly with % symbol
    rate_value = request.form.get('rate', '0')
    rate = f"{'+' if int(rate_value) >= 0 else ''}{rate_value}%"
    
    # Format volume properly with % symbol
    volume_value = request.form.get('volume', '0')
    volume = f"{'+' if int(volume_value) >= 0 else ''}{volume_value}%"
    
    # Format pitch properly with Hz
    pitch_value = request.form.get('pitch', '0')
    pitch = f"{'+' if int(pitch_value) >= 0 else ''}{pitch_value}Hz"

    if not all([text, language, voice]):
        return jsonify({'error': 'Missing required parameters', 'success': False})

    try:
        voice_info = voices[language][voice]
        voice_id = voice_info['voice_id']
        
        if style != 'default':
            voice_id = f"{voice_id}(Style={style})"

        communicate = edge_tts.Communicate(
            text,
            voice_id,
            rate=rate,
            volume=volume,
            pitch=pitch
        )

        audio_filename = f"{language}_{voice}_{hash(text)}.mp3"
        audio_filepath = os.path.join(AUDIO_DIR, audio_filename)
        
        await communicate.save(audio_filepath)
        
        return jsonify({
            'success': True,
            'audio_path': f'/generated_audio/{audio_filename}',
            'filename': audio_filename
        })
    except Exception as e:
        return jsonify({'error': str(e), 'success': False})

@app.route('/generated_audio/<filename>')
def serve_audio(filename):
    return send_from_directory(AUDIO_DIR, filename)

@app.route('/download_audio/<filename>')
def download_audio(filename):
    return send_from_directory(AUDIO_DIR, filename, as_attachment=True)

if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0')

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
    },
    'Spanish': {
        'Alvaro': {'voice_id': 'es-ES-AlvaroNeural', 'styles': ['default']},
        'Elena': {'voice_id': 'es-ES-ElenaNeural', 'styles': ['default']},
    },
    'French': {
        'Henri': {'voice_id': 'fr-FR-HenriNeural', 'styles': ['default']},
        'Denise': {'voice_id': 'fr-FR-DeniseNeural', 'styles': ['default']},
    },
    'German': {
        'Katja': {'voice_id': 'de-DE-KatjaNeural', 'styles': ['default']},
        'Conrad': {'voice_id': 'de-DE-ConradNeural', 'styles': ['default']},
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

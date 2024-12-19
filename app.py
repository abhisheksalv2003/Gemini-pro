import os
import edge_tts
import asyncio
from flask import Flask, render_template, request, send_from_directory, jsonify

app = Flask(__name__)

# Configure static folder for generated audio
AUDIO_DIR = os.path.join(os.getcwd(), 'generated_audio')
os.makedirs(AUDIO_DIR, exist_ok=True)

# Your existing voices dictionary remains the same
voices = {
    'United States': {
        'Emma (US)': {
            'voice_id': 'en-US-EmmaNeural',
            'styles': ['default', 'cheerful', 'sad', 'excited']
        },
        'Jenny (US)': {
            'voice_id': 'en-US-JennyNeural',
            'styles': ['default', 'chat', 'customerservice']
        },
        'Guy (US)': {
            'voice_id': 'en-US-GuyNeural',
            'styles': ['default']
        },
        'Aria (US)': {
            'voice_id': 'en-US-AriaNeural',
            'styles': ['default']
        },
        'Davis (US)': {
            'voice_id': 'en-US-DavisNeural',
            'styles': ['default']
        }
    }
}  # ... rest of your voices dictionary

@app.route('/')
def index():
    flat_voices = {}
    for category, voice_group in voices.items():
        flat_voices.update(voice_group)
    return render_template('index.html', voices=flat_voices)

@app.route('/generate_audio', methods=['POST'])
async def generate_audio():
    text = request.form.get('text')
    selected_voice = request.form.get('voice')
    selected_style = request.form.get('style', 'default')
    
    if not text or not selected_voice:
        return jsonify({
            'error': 'Please provide text and select a voice.',
            'success': False
        })
    
    try:
        voice_id = None
        for category in voices.values():
            if selected_voice in category:
                voice_info = category[selected_voice]
                voice_id = voice_info['voice_id']
                break
        
        if not voice_id:
            return jsonify({
                'error': 'Selected voice not found.',
                'success': False
            })
        
        if selected_style != 'default':
            voice_id = f"{voice_id}(Style:{selected_style})"
        
        audio_filename = f"{selected_voice.replace(' ', '_')}_{selected_style}_{hash(text)}.mp3"
        audio_filepath = os.path.join(AUDIO_DIR, audio_filename)
        
        communicate = edge_tts.Communicate(text, voice_id)
        await communicate.save(audio_filepath)
        
        return jsonify({
            'success': True,
            'audio_path': f'/generated_audio/{audio_filename}',
            'filename': audio_filename
        })
    
    except Exception as e:
        return jsonify({
            'error': str(e),
            'success': False
        })

@app.route('/generated_audio/<filename>')
def serve_audio(filename):
    return send_from_directory(AUDIO_DIR, filename)

@app.route('/download_audio/<filename>')
def download_audio(filename):
    try:
        return send_from_directory(AUDIO_DIR, filename, as_attachment=True)
    except Exception as e:
        return str(e), 404

if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0')

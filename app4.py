import os
import edge_tts
import asyncio
from flask import Flask, render_template, request, send_from_directory, jsonify

app = Flask(__name__)

# Configure static folder for generated audio
if os.environ.get('RENDER'):
    AUDIO_DIR = '/opt/render/project/src/generated_audio'
else:
    AUDIO_DIR = 'generated_audio'

os.makedirs(AUDIO_DIR, exist_ok=True)

# Comprehensive voice dictionary with categorization
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
    },
    'United Kingdom': {
        'Jane (UK)': {
            'voice_id': 'en-GB-SoniaNeural',
            'styles': ['default']
        },
        'Ryan (UK)': {
            'voice_id': 'en-GB-RyanNeural',
            'styles': ['default']
        }
    },
    'Australia': {
        'Libby (AU)': {
            'voice_id': 'en-AU-NatashaNeural',
            'styles': ['default']
        },
        'William (AU)': {
            'voice_id': 'en-AU-WilliamNeural',
            'styles': ['default']
        }
    },
    'Canada': {
        'Linda (CA)': {
            'voice_id': 'en-CA-LiamNeural',
            'styles': ['default']
        },
        'Liam (CA)': {
            'voice_id': 'en-CA-ClaraNeural',
            'styles': ['default']
        }
    },
    'Ireland': {
        'Connor (IE)': {
            'voice_id': 'en-IE-ConnorNeural',
            'styles': ['default']
        },
        'Emily (IE)': {
            'voice_id': 'en-IE-EmilyNeural',
            'styles': ['default']
        }
    },
    'India': {
        'Rosa (IN)': {
            'voice_id': 'en-IN-NeerjaNeural',
            'styles': ['default']
        },
        'Ravi (IN)': {
            'voice_id': 'en-IN-PrabhatNeural',
            'styles': ['default']
        }
    }
}

@app.route('/')
def index():
    # Flatten the nested dictionary for template rendering
    flat_voices = {}
    for category, voice_group in voices.items():
        flat_voices.update(voice_group)
    return render_template('index.html', voices=voices)

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
        # Find the voice ID in the nested dictionary
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
        
        # Modify voice ID to include style if applicable
        if selected_style != 'default':
            voice_id = f"{voice_id}(Style:{selected_style})"
        
        audio_filename = f"{selected_voice.replace(' ', '_')}_{selected_style}_{hash(text)}.mp3"
        audio_filepath = os.path.join(AUDIO_DIR, audio_filename)
        
        # Use edge_tts to generate the speech
        communicate = edge_tts.Communicate(text, voice_id)
        await communicate.save(audio_filepath)
        
        # Return the generated audio file path
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

# Add static folder route
@app.route('/static/<path:path>')
def serve_static(path):
    return send_from_directory('static', path)

if __name__ == '__main__':
    app.run(debug=True)

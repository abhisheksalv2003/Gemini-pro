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
    # English Voices (Categorized by Region)
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
    },
    
    # Indian Regional Languages
    'Hindi': {
        'Swara (HI)': {
            'voice_id': 'hi-IN-SwaraNeural',
            'styles': ['default']
        },
        'Madhur (HI)': {
            'voice_id': 'hi-IN-MadhurNeural',
            'styles': ['default']
        }
    },
    'Tamil': {
        'Pallavi (TA)': {
            'voice_id': 'ta-IN-PallaviNeural',
            'styles': ['default']
        },
        'Valluvar (TA)': {
            'voice_id': 'ta-IN-ValluvarNeural',
            'styles': ['default']
        }
    },
    'Telugu': {
        'Mohan (TE)': {
            'voice_id': 'te-IN-MohanNeural',
            'styles': ['default']
        },
        'Shruti (TE)': {
            'voice_id': 'te-IN-ShrutiNeural',
            'styles': ['default']
        }
    },
    'Malayalam': {
        'Sobhana (ML)': {
            'voice_id': 'ml-IN-SobhanaNeural',
            'styles': ['default']
        },
        'Midhun (ML)': {
            'voice_id': 'ml-IN-MidhunNeural',
            'styles': ['default']
        }
    },
    'Kannada': {
        'Gagan (KN)': {
            'voice_id': 'kn-IN-GaganNeural',
            'styles': ['default']
        },
        'Sapna (KN)': {
            'voice_id': 'kn-IN-SapnaNeural',
            'styles': ['default']
        }
    },
    'Gujarati': {
        'Dhwani (GU)': {
            'voice_id': 'gu-IN-DhwaniNeural',
            'styles': ['default']
        },
        'Niranjan (GU)': {
            'voice_id': 'gu-IN-NiranjanNeural',
            'styles': ['default']
        }
    },
    'Marathi': {
        'Aarohi (MR)': {
            'voice_id': 'mr-IN-AarohiNeural',
            'styles': ['default']
        },
        'Manohar (MR)': {
            'voice_id': 'mr-IN-ManoharNeural',
            'styles': ['default']
        }
    },
    'Bengali': {
        'Tanishaa (BN)': {
            'voice_id': 'bn-IN-TanishaaNeural',
            'styles': ['default']
        },
        'Bashkar (BN)': {
            'voice_id': 'bn-IN-BashkarNeural',
            'styles': ['default']
        }
    },
    'Punjabi': {
        'Amala (PA)': {
            'voice_id': 'pa-IN-AmaraNeural',
            'styles': ['default']
        },
        'Gurdeep (PA)': {
            'voice_id': 'pa-IN-GurdeepNeural',
            'styles': ['default']
        }
    },
    'Odia': {
        'Prachi (OR)': {
            'voice_id': 'or-IN-PrachiNeural',
            'styles': ['default']
        },
        'Manish (OR)': {
            'voice_id': 'or-IN-ManishNeural',
            'styles': ['default']
        }
    },
    'Assamese': {
        'Nabanita (AS)': {
            'voice_id': 'as-IN-NabanitaNeural',
            'styles': ['default']
        },
        'Manish (AS)': {
            'voice_id': 'as-IN-ManishNeural',
            'styles': ['default']
        }
    },
    
    # Multilingual Models
    'Multilingual': {
        'Emma (Multi)': {
            'voice_id': 'en-US-EmmaMultilingualNeural',
            'styles': ['default']
        },
        'Guy (Multi)': {
            'voice_id': 'fr-FR-VivienneMultilingualNeural',
            'styles': ['default']
        },
        'Serafina (Multi)': {
            'voice_id': 'de-DE-SeraphinaMultilingualNeural',
            'styles': ['default']
        },
        'Florian (Multi)': {
            'voice_id': 'de-DE-FlorianMultilingualNeural',
            'styles': ['default']
        },
        'Remy (Multi)': {
            'voice_id': 'fr-FR-RemyMultilingualNeural',
            'styles': ['default']
        },
        'Ava (Multi)': {
            'voice_id': 'en-US-AvaMultilingualNeural',
            'styles': ['default']
        },
        'Andrew (Multi)': {
            'voice_id': 'en-US-AndrewMultilingualNeural',
            'styles': ['default']
        },
        'Brian (Multi)': {
            'voice_id': 'en-US-caBrianMultilingualNeural',
            'styles': ['default']
        }
    }
}

@app.route('/')
def index():
    flat_voices = {}
    for category, voice_group in voices.items():
        flat_voices.update(voice_group)
    return render_template('index.html', voices=flat_voices)

@app.route('/generate_audio', methods=['POST'])
async def generate_audio():
    # Get basic parameters
    text = request.form.get('text')
    selected_voice = request.form.get('voice')
    selected_style = request.form.get('style', 'default')
    
    # Get additional TTS parameters
    rate = request.form.get('rate', '+0%')  # Default: normal speed
    volume = request.form.get('volume', '+0%')  # Default: normal volume
    pitch = request.form.get('pitch', '+0Hz')  # Default: normal pitch
    
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
        
        # Apply style if selected
        if selected_style != 'default':
            voice_id = f"{voice_id}(Style:{selected_style})"
        
        # Create unique filename based on parameters
        audio_filename = f"{selected_voice.replace(' ', '_')}_{selected_style}_{hash(text)}_{rate}_{volume}_{pitch}.mp3"
        audio_filepath = os.path.join(AUDIO_DIR, audio_filename)
        
        # Create communicate instance with all parameters
        communicate = edge_tts.Communicate(
            text=text,
            voice=voice_id,
            rate=rate,      # e.g., '+50%', '-20%'
            volume=volume,  # e.g., '+50%', '-20%'
            pitch=pitch     # e.g., '+50Hz', '-20Hz'
        )
        
        await communicate.save(audio_filepath)
        
        return jsonify({
            'success': True,
            'audio_path': f'/generated_audio/{audio_filename}',
            'filename': audio_filename,
            'parameters': {
                'rate': rate,
                'volume': volume,
                'pitch': pitch
            }
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

# New endpoint to get available voice features
@app.route('/voice_features/<voice_name>')
def get_voice_features(voice_name):
    for category in voices.values():
        if voice_name in category:
            voice_info = category[voice_name]
            return jsonify({
                'voice_id': voice_info['voice_id'],
                'styles': voice_info['styles'],
                'rate_range': {'min': '-100%', 'max': '+100%', 'default': '+0%'},
                'volume_range': {'min': '-100%', 'max': '+100%', 'default': '+0%'},
                'pitch_range': {'min': '-100Hz', 'max': '+100Hz', 'default': '+0Hz'}
            })
    return jsonify({'error': 'Voice not found'}), 404

if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0')

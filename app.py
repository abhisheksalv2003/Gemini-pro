import os
import edge_tts
import asyncio
from flask import Flask, render_template, request, send_from_directory, jsonify
app = Flask(__name__)
AUDIO_DIR = os.path.join(os.getcwd(), 'generated_audio')
os.makedirs(AUDIO_DIR, exist_ok=True)

voices = {
    'Multilingual': {
        'Andrew': {'voice_id': 'en-US-AndrewMultilingualNeural', 'styles': ['default']},
        'Ava': {'voice_id': 'en-US-AvaMultilingualNeural', 'styles': ['default']},
        'Brian': {'voice_id': 'en-US-BrianMultilingualNeural', 'styles': ['default']},
        'Emma': {'voice_id': 'en-US-EmmaMultilingualNeural', 'styles': ['default']},
        'Florian': {'voice_id': 'de-DE-FlorianMultilingualNeural', 'styles': ['default']},
        'Giuseppe': {'voice_id': 'it-IT-GiuseppeMultilingualNeural', 'styles': ['default']},
        'Hyunsu': {'voice_id': 'ko-KR-HyunsuMultilingualNeural', 'styles': ['default']},
        'Remy': {'voice_id': 'fr-FR-RemyMultilingualNeural', 'styles': ['default']},
        'Seraphina': {'voice_id': 'de-DE-SeraphinaMultilingualNeural', 'styles': ['default']},
        'Thalita': {'voice_id': 'pt-BR-ThalitaMultilingualNeural', 'styles': ['default']},
        'Vivienne': {'voice_id': 'fr-FR-VivienneMultilingualNeural', 'styles': ['default']}
    },
    'Arabic': {
        'Fatima': {'voice_id': 'ar-AE-FatimaNeural', 'styles': ['default']},
        'Hamdan': {'voice_id': 'ar-AE-HamdanNeural', 'styles': ['default']},
        'Ali': {'voice_id': 'ar-BH-AliNeural', 'styles': ['default']},
        'Laila': {'voice_id': 'ar-BH-LailaNeural', 'styles': ['default']},
        'Salma': {'voice_id': 'ar-EG-SalmaNeural', 'styles': ['default']},
        'Shakir': {'voice_id': 'ar-EG-ShakirNeural', 'styles': ['default']}
    },
    'Chinese': {
        'Xiaoxiao': {'voice_id': 'zh-CN-XiaoxiaoNeural', 'styles': ['default']},
        'Xiaoyi': {'voice_id': 'zh-CN-XiaoyiNeural', 'styles': ['default']},
        'Yunjian': {'voice_id': 'zh-CN-YunjianNeural', 'styles': ['default']},
        'Yunxi': {'voice_id': 'zh-CN-YunxiNeural', 'styles': ['default']},
        'Yunxia': {'voice_id': 'zh-CN-YunxiaNeural', 'styles': ['default']},
        'Yunyang': {'voice_id': 'zh-CN-YunyangNeural', 'styles': ['default']}
    },
    'English': {
        'Ana': {'voice_id': 'en-US-AnaNeural', 'styles': ['default']},
        'Andrew': {'voice_id': 'en-US-AndrewNeural', 'styles': ['default']},
        'Aria': {'voice_id': 'en-US-AriaNeural', 'styles': ['default']},
        'Ava': {'voice_id': 'en-US-AvaNeural', 'styles': ['default']},
        'Brian': {'voice_id': 'en-US-BrianNeural', 'styles': ['default']},
        'Christopher': {'voice_id': 'en-US-ChristopherNeural', 'styles': ['default']},
        'Emma': {'voice_id': 'en-US-EmmaNeural', 'styles': ['default']},
        'Eric': {'voice_id': 'en-US-EricNeural', 'styles': ['default']},
        'Guy': {'voice_id': 'en-US-GuyNeural', 'styles': ['default']},
        'Jenny': {'voice_id': 'en-US-JennyNeural', 'styles': ['default']},
        'Michelle': {'voice_id': 'en-US-MichelleNeural', 'styles': ['default']},
        'Roger': {'voice_id': 'en-US-RogerNeural', 'styles': ['default']},
        'Steffan': {'voice_id': 'en-US-SteffanNeural', 'styles': ['default']}
    },
    'French': {
        'Denise': {'voice_id': 'fr-FR-DeniseNeural', 'styles': ['default']},
        'Eloise': {'voice_id': 'fr-FR-EloiseNeural', 'styles': ['default']},
        'Henri': {'voice_id': 'fr-FR-HenriNeural', 'styles': ['default']},
        'Charline': {'voice_id': 'fr-BE-CharlineNeural', 'styles': ['default']},
        'Gerard': {'voice_id': 'fr-BE-GerardNeural', 'styles': ['default']},
        'Antoine': {'voice_id': 'fr-CA-AntoineNeural', 'styles': ['default']},
        'Jean': {'voice_id': 'fr-CA-JeanNeural', 'styles': ['default']},
        'Sylvie': {'voice_id': 'fr-CA-SylvieNeural', 'styles': ['default']},
        'Thierry': {'voice_id': 'fr-CA-ThierryNeural', 'styles': ['default']}
    },
    'German': {
        'Amala': {'voice_id': 'de-DE-AmalaNeural', 'styles': ['default']},
        'Conrad': {'voice_id': 'de-DE-ConradNeural', 'styles': ['default']},
        'Katja': {'voice_id': 'de-DE-KatjaNeural', 'styles': ['default']},
        'Killian': {'voice_id': 'de-DE-KillianNeural', 'styles': ['default']}
    },
    'Hindi': {
        'Madhur': {'voice_id': 'hi-IN-MadhurNeural', 'styles': ['default']},
        'Swara': {'voice_id': 'hi-IN-SwaraNeural', 'styles': ['default']}
    },
    'Italian': {
        'Diego': {'voice_id': 'it-IT-DiegoNeural', 'styles': ['default']},
        'Elsa': {'voice_id': 'it-IT-ElsaNeural', 'styles': ['default']},
        'Isabella': {'voice_id': 'it-IT-IsabellaNeural', 'styles': ['default']}
    },
    'Japanese': {
        'Keita': {'voice_id': 'ja-JP-KeitaNeural', 'styles': ['default']},
        'Nanami': {'voice_id': 'ja-JP-NanamiNeural', 'styles': ['default']}
    },
    'Korean': {
        'InJoon': {'voice_id': 'ko-KR-InJoonNeural', 'styles': ['default']},
        'SunHi': {'voice_id': 'ko-KR-SunHiNeural', 'styles': ['default']}
    },
    'Portuguese': {
        'Antonio': {'voice_id': 'pt-BR-AntonioNeural', 'styles': ['default']},
        'Francisca': {'voice_id': 'pt-BR-FranciscaNeural', 'styles': ['default']},
        'Duarte': {'voice_id': 'pt-PT-DuarteNeural', 'styles': ['default']},
        'Raquel': {'voice_id': 'pt-PT-RaquelNeural', 'styles': ['default']}
    },
    'Russian': {
        'Dmitry': {'voice_id': 'ru-RU-DmitryNeural', 'styles': ['default']},
        'Svetlana': {'voice_id': 'ru-RU-SvetlanaNeural', 'styles': ['default']}
    },
    'Spanish': {
        'Alvaro': {'voice_id': 'es-ES-AlvaroNeural', 'styles': ['default']},
        'Elvira': {'voice_id': 'es-ES-ElviraNeural', 'styles': ['default']},
        'Ximena': {'voice_id': 'es-ES-XimenaNeural', 'styles': ['default']},
        'Dalia': {'voice_id': 'es-MX-DaliaNeural', 'styles': ['default']},
        'Jorge': {'voice_id': 'es-MX-JorgeNeural', 'styles': ['default']},
        'Alonso': {'voice_id': 'es-US-AlonsoNeural', 'styles': ['default']},
        'Paloma': {'voice_id': 'es-US-PalomaNeural', 'styles': ['default']}
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

from flask import Flask, request, jsonify, render_template, send_from_directory
from datetime import datetime
from dsChat import *
from srt import convert_srt, translate_srt
import os

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/subtitle_translate')
def subtitle_translate():
    return render_template('subtitle_translate.html')

@app.route('/dialogue_chat')
def dialogue_chat():
    return render_template('dialogue_chat.html')

@app.route('/translate')
def translate():
    return render_template('translate.html')

@app.route('/translate_text', methods=['POST'])
def translate_text():
    data = request.json
    user_message = data.get('message', '')
    lang = data.get('lang', 'zh-CN')

    if not user_message:
        return jsonify({"error": "No message provided"}), 400

    translated_text = get_deepseek().deepseek_to_chat(user_message, msTranslate, lang)
    return jsonify({"translated_text": translated_text})

@app.route('/dialogue', methods=['POST'])
def dialogue():
    data = request.json
    user_message = data.get('message', '')

    if not user_message:
        return jsonify({"error": "No message provided"}), 400

    dialogue_text = get_deepseek().deepseek_to_chat(user_message, msCHAT)
    return jsonify({"dialogue_text": dialogue_text})

@app.route('/translate_subtitle', methods=['POST'])
def translate_subtitle():
    if 'subtitle-file' not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    file = request.files['subtitle-file']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400

    # 保存文件
    srt_file_path = os.path.join('uploads', file.filename)
    file.save(srt_file_path)

    # 翻译
    datetime_str = datetime.now().strftime("%Y%m%d%H%M%S")
    dst_file_path = os.path.join('uploads', f'convert_{datetime_str}.srt')
    translate_file_path = os.path.join('uploads', f'translate_{datetime_str}.srt')

    convert_srt(srt_file_path, dst_file_path)
    translate_srt(dst_file_path, translate_file_path)

    # 返回下载链接
    return jsonify({"download_link": f"/{translate_file_path}"})

@app.route('/clear', methods=['POST'])
def clear():
    # 清空对话
    get_deepseek().clear()
    return jsonify({"status": "success"})

@app.route('/uploads/<path:filename>')
def download_file(filename):
    return send_from_directory('uploads', filename)

if __name__ == "__main__":
    app.run(debug=True)

from flask import Flask, jsonify, request
from flask_cors import CORS
import threading
import subprocess
import os
import signal
import json

app = Flask(__name__)
CORS(app)

recording_status = {
    "is_recording": False,
    "last_result": None
}

def run_recording_program():
    try:
        global recording_status
        recording_status["is_recording"] = True
        
        print("▶Запуск программы записи...")
        
        result = subprocess.run(
            ['python3', '/home/pi/android_project/record_program.py'],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        recording_status["last_result"] = {
            "success": result.returncode == 0,
            "stdout": result.stdout,
            "stderr": result.stderr,
            "returncode": result.returncode
        }
        
        if result.returncode == 0:
            print("Программа записи выполнена успешно")
            print(result.stdout)
        else:
            print("Ошибка выполнения:")
            print(result.stderr)
            
    except subprocess.TimeoutExpired:
        recording_status["last_result"] = {
            "success": False,
            "error": "Таймаут выполнения"
        }
        print("Таймаут выполнения программы")
        
    except Exception as e:
        recording_status["last_result"] = {
            "success": False,
            "error": str(e)
        }
        print(f"Исключение: {e}")
        
    finally:
        recording_status["is_recording"] = False

@app.route('/api/start-recording', methods=['POST'])
def start_recording():
    try:
        if recording_status["is_recording"]:
            return jsonify({
                "status": "error",
                "message": "Запись уже выполняется"
            }), 409
        
        thread = threading.Thread(target=run_recording_program)
        thread.start()
        
        return jsonify({
            "status": "success",
            "message": "Запись запущена",
            "data": {
                "recording_time": 3,  # секунд
                "led_pins": [14, 15, 23, 24, 21]
            }
        }), 200
        
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

@app.route('/api/status', methods=['GET'])
def get_status():
    return jsonify({
        "status": "running",
        "service": "Raspberry Pi Recording Server",
        "recording": recording_status["is_recording"],
        "last_result": recording_status["last_result"]
    }), 200

@app.route('/api/stop', methods=['POST'])
def stop_recording():
    return jsonify({
        "status": "success",
        "message": "Команда остановки отправлена"
    }), 200

if __name__ == '__main__':
    print("=" * 50)
    print("Flask сервер запущен")
    print("API Endpoints:")
    print("   POST /api/start-recording - запуск записи")
    print("   GET  /api/status - статус сервера")
    print("   POST /api/stop - остановка записи")
    print("=" * 50)
    print("Сервер доступен по адресу: http://0.0.0.0:5000")
    print("=" * 50)
    
    app.run(
        host='0.0.0.0',  # Доступ со всех интерфейсов
        port=5000,
        debug=False,     # В продакшене debug=False
        threaded=True    # Поддержка многопоточности
    )
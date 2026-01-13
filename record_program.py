import pyaudio
import wave
from gpiozero import LED
import random
import time
import os

LED_PINS = [14, 15, 23, 24, 21]
leds = [LED(pin) for pin in LED_PINS]

FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100
CHUNK = 4096
RECORD_SECONDS = 3
WAVE_OUTPUT_FILENAME = "/tmp/output.wav"

def record_audio():
    try:
        audio = pyaudio.PyAudio()
        
        stream = audio.open(format=FORMAT,
                           channels=CHANNELS,
                           rate=RATE,
                           input=True,
                           frames_per_buffer=CHUNK)
        
        print("Запись началась...")
        frames = []
        
        for i in range(0, int(RATE / CHUNK * RECORD_SECONDS)):
            data = stream.read(CHUNK)
            frames.append(data)
        
        print("Запись завершена")
        
        stream.stop_stream()
        stream.close()
        audio.terminate()
        
        with wave.open(WAVE_OUTPUT_FILENAME, 'wb') as wf:
            wf.setnchannels(CHANNELS)
            wf.setsampwidth(audio.get_sample_size(FORMAT))
            wf.setframerate(RATE)
            wf.writeframes(b''.join(frames))
        
        print(f"Файл сохранен: {WAVE_OUTPUT_FILENAME}")
        return True
        
    except Exception as e:
        print(f"Ошибка записи: {e}")
        return False

def control_leds():
    try:
        random_led = random.choice(leds)
        random_led.on()
        print(f"Светодиод {random_led.pin.number} включен")
        
        time.sleep(2)
        
        random_led.off()
        print("Светодиод выключен")
        return True
        
    except Exception as e:
        print(f"Ошибка со светодиодами: {e}")
        return False

def main():
    print("=" * 50)
    print("Запуск программы записи с Raspberry Pi 5")
    print("=" * 50)
    
    if record_audio():
        # Управляем светодиодами
        control_leds()
    
    print("Программа завершена успешно!")

if __name__ == "__main__":
    main()
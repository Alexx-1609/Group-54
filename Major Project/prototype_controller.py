import os
import time
import json
import subprocess
import urllib.parse
import urllib.request
import spidev

# ---------- Configuration ----------

MIC_SOURCE = "83"       # Realme Buds microphone
AUDIO_OUTPUT = "56"     # Wired earphones

WHISPER = os.path.expanduser(
    "~/whisper.cpp/build/bin/whisper-cli"
)
MODEL = os.path.expanduser(
    "~/whisper.cpp/models/ggml-tiny.bin"
)

RECORD_FILE = os.path.expanduser(
    "~/translator_recording.wav"
)
TRANSCRIPT_BASE = "/tmp/translator_whisper"
SPEECH_FILE = "/tmp/translator_speech.wav"

SOURCE_LANG = "en"
TARGET_LANG = "hi"

LANG_NAMES = {
    "en": "English",
    "hi": "Hindi",
}

# Arduino button events
EVENT_CODES = {
    ord("F"), ord("T"), ord("P"), ord("p"), ord("R")
}
SPI_ACK = ord("A")

# OLED status codes — must match the Arduino sketch
STATUS_READY = "1"
STATUS_LISTENING = "2"
STATUS_PROCESSING = "3"
STATUS_SPEAKING = "4"
STATUS_DONE = "5"
STATUS_ERROR = "6"
STATUS_FROM_EN = "7"
STATUS_TO_HI = "8"
STATUS_FROM_HI = "9"
STATUS_TO_EN = "0"

recording = None

# ---------- SPI setup ----------

spi = spidev.SpiDev()
spi.open(0, 0)
spi.max_speed_hz = 100000
spi.mode = 0
spi.bits_per_word = 8


def send_oled_status(status_code):
    """Send one status code to the Arduino OLED."""
    try:
        spi.xfer2([ord(status_code)])
    except Exception as error:
        print("OLED status communication error:", error)


def show_language_status():
    """Display the current source and target languages."""
    if SOURCE_LANG == "en":
        send_oled_status(STATUS_FROM_EN)
    else:
        send_oled_status(STATUS_FROM_HI)

    if TARGET_LANG == "hi":
        send_oled_status(STATUS_TO_HI)
    else:
        send_oled_status(STATUS_TO_EN)


def poll_spi():
    """Read an Arduino event and acknowledge it."""
    event = spi.xfer2([0x00])[0]

    if event in EVENT_CODES:
        spi.xfer2([SPI_ACK])
        spi.xfer2([0x00])
        return event

    return None


# ---------- Audio recording ----------

def start_recording():
    global recording

    if recording is not None:
        print("Already recording.")
        return False

    if not os.path.isfile(WHISPER):
        print("Whisper executable not found:", WHISPER)
        send_oled_status(STATUS_ERROR)
        return False

    if not os.path.isfile(MODEL):
        print("Whisper model not found:", MODEL)
        send_oled_status(STATUS_ERROR)
        return False

    if os.path.exists(RECORD_FILE):
        os.remove(RECORD_FILE)

    command = [
        "pw-record",
        "--target", MIC_SOURCE,
        "--rate", "16000",
        "--channels", "1",
        "--format", "s16",
        RECORD_FILE,
    ]

    try:
        recording = subprocess.Popen(command)
        time.sleep(0.5)

        if recording.poll() is not None:
            recording = None
            print("Recording failed. Check microphone source.")
            send_oled_status(STATUS_ERROR)
            return False

        send_oled_status(STATUS_LISTENING)
        print("Recording started. Speak now.")
        return True

    except Exception as error:
        recording = None
        print("Could not start recording:", error)
        send_oled_status(STATUS_ERROR)
        return False


def stop_recording():
    global recording

    if recording is None:
        print("No recording is active.")
        return False

    try:
        recording.terminate()

        try:
            recording.wait(timeout=5)
        except subprocess.TimeoutExpired:
            recording.kill()
            recording.wait()

    except Exception as error:
        print("Error stopping recording:", error)
        send_oled_status(STATUS_ERROR)
        return False

    finally:
        recording = None

    print("Recording stopped.")

    if not os.path.exists(RECORD_FILE):
        print("Recording file was not created.")
        send_oled_status(STATUS_ERROR)
        return False

    if os.path.getsize(RECORD_FILE) < 1000:
        print("Recording is empty or too short.")
        send_oled_status(STATUS_ERROR)
        return False

    return True


# ---------- Transcription ----------

def transcribe_audio():
    output_txt = TRANSCRIPT_BASE + ".txt"

    if os.path.exists(output_txt):
        os.remove(output_txt)

    command = [
        WHISPER,
        "-m", MODEL,
        "-f", RECORD_FILE,
        "-l", SOURCE_LANG,
        "-nt",
        "-otxt",
        "-of", TRANSCRIPT_BASE,
    ]

    print("Transcribing audio...")

    try:
        result = subprocess.run(command)

        if result.returncode != 0:
            print("Whisper transcription failed.")
            return ""

        if not os.path.exists(output_txt):
            print("Whisper did not create a transcript.")
            return ""

        with open(output_txt, "r", encoding="utf-8") as file:
            return file.read().strip()

    except Exception as error:
        print("Transcription error:", error)
        return ""


# ---------- Translation ----------

def translate_text(text):
    if not text:
        return ""

    params = urllib.parse.urlencode({
        "q": text,
        "langpair": f"{SOURCE_LANG}|{TARGET_LANG}",
    })

    url = "https://api.mymemory.translated.net/get?" + params

    try:
        request = urllib.request.Request(
            url,
            headers={"User-Agent": "TranslatorPrototype/1.0"},
        )

        with urllib.request.urlopen(request, timeout=20) as response:
            data = json.loads(response.read().decode("utf-8"))

        translated = data.get("responseData", {}).get(
            "translatedText", ""
        )

        return translated.strip()

    except Exception as error:
        print("Translation failed:", error)
        return ""


# ---------- Speech output ----------

def speak_text(text):
    if not text:
        return False

    voice = "hi" if TARGET_LANG == "hi" else "en"

    command = [
        "espeak-ng",
        "-v", voice,
        "-s", "140",
        "-w", SPEECH_FILE,
        text,
    ]

    try:
        result = subprocess.run(command)

        if result.returncode != 0:
            print("Speech synthesis failed.")
            return False

        send_oled_status(STATUS_SPEAKING)
        print("Playing translated speech...")

        result = subprocess.run([
            "pw-play",
            "--target", AUDIO_OUTPUT,
            SPEECH_FILE,
        ])

        if result.returncode != 0:
            print("Audio playback failed.")
            return False

        return True

    except Exception as error:
        print("Speech output error:", error)
        return False


# ---------- Complete translation workflow ----------

def process_recording():
    send_oled_status(STATUS_PROCESSING)

    if not stop_recording():
        send_oled_status(STATUS_ERROR)
        return

    # Keep PROCESSING displayed during recognition and translation.
    transcript = transcribe_audio()

    if not transcript:
        print("No speech recognized.")
        send_oled_status(STATUS_ERROR)
        return

    print("Recognized:", transcript)

    translated = translate_text(transcript)

    if not translated:
        print("No translation received.")
        send_oled_status(STATUS_ERROR)
        return

    print("Translation:", translated)

    if not speak_text(translated):
        send_oled_status(STATUS_ERROR)
        return

    send_oled_status(STATUS_DONE)
    print("Translation completed.")

    time.sleep(1)
    send_oled_status(STATUS_READY)


# ---------- Button event handling ----------

def handle_event(event):
    global SOURCE_LANG, TARGET_LANG

    if event == ord("F"):
        SOURCE_LANG = "en"
        print("FROM:", LANG_NAMES[SOURCE_LANG])
        send_oled_status(STATUS_FROM_EN)

    elif event == ord("T"):
        TARGET_LANG = "hi"
        print("TO:", LANG_NAMES[TARGET_LANG])
        send_oled_status(STATUS_TO_HI)

    elif event == ord("P"):
        start_recording()

    elif event == ord("p"):
        process_recording()

    elif event == ord("R"):
        SOURCE_LANG, TARGET_LANG = TARGET_LANG, SOURCE_LANG
        print("FROM:", LANG_NAMES[SOURCE_LANG])
        print("TO:", LANG_NAMES[TARGET_LANG])
        show_language_status()


# ---------- Main program ----------

def main():
    global recording

    print("TRANSLATOR PROTOTYPE")
    print("FROM:", LANG_NAMES[SOURCE_LANG])
    print("TO:", LANG_NAMES[TARGET_LANG])
    print("Microphone source:", MIC_SOURCE)
    print("Audio output:", AUDIO_OUTPUT)
    print("Waiting for Arduino button events...")

    send_oled_status(STATUS_READY)
    show_language_status()
    send_oled_status(STATUS_READY)

    try:
        while True:
            event = poll_spi()

            if event is not None:
                print("SPI event:", chr(event))
                handle_event(event)

            time.sleep(0.02)

    except KeyboardInterrupt:
        print("\nStopping translator...")

    finally:
        if recording is not None:
            recording.terminate()

            try:
                recording.wait(timeout=5)
            except subprocess.TimeoutExpired:
                recording.kill()
                recording.wait()

            recording = None

        spi.close()
        print("Translator stopped.")


if __name__ == "__main__":
    main()


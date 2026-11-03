import speech_recognition as sr

recognizer = sr.Recognizer()

print("Speech-to-text test")
print("Speak into your Bluetooth earbuds microphone.")
print("Say something...")

with sr.Microphone() as source:
    recognizer.adjust_for_ambient_noise(source, duration=1)

    print("Listening...")
    audio = recognizer.listen(source)

print("Processing...")

try:
    text = recognizer.recognize_google(audio)
    print("You said:", text)

except sr.UnknownValueError:
    print("Could not understand the speech.")

except sr.RequestError as e:
    print("Speech recognition service error:", e)

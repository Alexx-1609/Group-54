import json
import urllib.parse
import urllib.request

text = "Hello, how are you?"

params = urllib.parse.urlencode({
    "q": text,
    "langpair": "en|hi"
})

url = "https://api.mymemory.translated.net/get?" + params

try:
    request = urllib.request.Request(
        url,
        headers={"User-Agent": "RaspberryPiTranslator/1.0"}
    )

    with urllib.request.urlopen(request, timeout=15) as response:
        data = json.loads(response.read().decode("utf-8"))

    if data.get("responseStatus") == 200:
        print("English:", text)
        print("Hindi:", data["responseData"]["translatedText"])
    else:
        print("Translation failed:", data.get("responseDetails"))

except Exception as e:
    print("Translation failed:", e)

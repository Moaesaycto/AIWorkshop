import speech_recognition as sr
import pyttsx3
import pyjokes
import math

# -----------------------------------------------------------------------------
# PLEASE READ BEFORE YOU EDIT!
# This code has been written for a course in AI. Try not to change anything
# except for the parameters listed below. If you know what you're doing, then
# feel free to change the rest of the code!
# -----------------------------------------------------------------------------
# To add a new command:
# 1. Define a new keyword group in COMMAND_KEYWORDS.
#    Example: "weather": ["weather", "forecast"]
# 2. Add a corresponding condition in `handle_command`.
#    Example:
#    elif any(keyword in command for keyword in COMMAND_KEYWORDS["weather"]):
#        # Add your custom functionality here
# -----------------------------------------------------------------------------

engine = pyttsx3.init()

COMMAND_KEYWORDS = {
    "joke": ["joke", "gag"],
    "calculate": ["calculate", "evaluate", "what is", "what's"],
    "exit": ["exit", "quit", "goodbye"]
}

def speak(text):
    engine.say(text)
    engine.runAndWait()

def listen():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print("Listening...")
        speak("I am listening.")
        recognizer.adjust_for_ambient_noise(source)
        try:
            # Capture audio input with timeout and phrase limits
            audio = recognizer.listen(source, timeout=10, phrase_time_limit=15)
            command = recognizer.recognize_google(audio)
            print(f"You said: {command}")
            return command.lower()
        except sr.UnknownValueError:
            speak("Sorry, I didn't understand that.")
        except sr.RequestError:
            speak("There seems to be an issue with my speech recognition service.")
        except sr.WaitTimeoutError:
            speak("You took too long to respond.")
        return ""


def interpret_math_expression(command):
    try:
        replacements = {
            "plus": "+", "minus": "-", "times": "*", "multiplied by": "*",
            "x": "*", "divided by": "/", "over": "/",
            "zero": "0", "one": "1", "two": "2", "three": "3", "four": "4",
            "five": "5", "six": "6", "seven": "7", "eight": "8", "nine": "9",
        }

        for word, symbol in replacements.items():
            command = command.replace(word, symbol)

        if not all(char.isdigit() or char in "()+-*/. mathsqrt" for char in command):
            return "Sorry, I can't evaluate that."

        result = eval(command)

        if isinstance(result, float):
            return round(result, 3)
        return result
    except Exception:
        return "Sorry, I couldn't calculate that."


def handle_command(command):
    if any(keyword in command for keyword in COMMAND_KEYWORDS["joke"]):
        joke = pyjokes.get_joke()
        print(f"Joke: {joke}")
        speak(joke)

    elif any(keyword in command for keyword in COMMAND_KEYWORDS["calculate"]):
        result = interpret_math_expression(command)
        print(f"Result: {result}")
        speak(f"The result is {result}")
    
    elif any(keyword in command for keyword in COMMAND_KEYWORDS["exit"]):
        speak("Goodbye!")
        exit()

    else:
        speak("Sorry, I didn't understand that.")


if __name__ == "__main__":
    speak("Hello! I am your assistant. How can I help you?")
    while True:
        user_command = listen()
        if user_command:
            handle_command(user_command)

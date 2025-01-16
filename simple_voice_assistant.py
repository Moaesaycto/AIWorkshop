import speech_recognition as sr
import pyttsx3
import pyjokes
import math

# Initialize the text-to-speech engine
engine = pyttsx3.init()

# Define keywords for different commands
COMMAND_KEYWORDS = {
    "joke": ["joke", "gag"],
    "calculate": ["calculate", "evaluate", "what is", "what's"],
    "exit": ["exit", "quit", "goodbye"]
}

# Function: Makes the assistant speak
def speak(text):
    engine.say(text)
    engine.runAndWait()

# Function: Captures voice input from the user
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

# Function: Interprets and evaluates math expressions from text
def interpret_math_expression(command):
    try:
        # Map words to math symbols or numbers
        replacements = {
            "plus": "+", "minus": "-", "times": "*", "multiplied by": "*",
            "x": "*", "divided by": "/", "over": "/",
            "zero": "0", "one": "1", "two": "2", "three": "3", "four": "4",
            "five": "5", "six": "6", "seven": "7", "eight": "8", "nine": "9",
        }

        # Replace words with symbols in the command
        for word, symbol in replacements.items():
            command = command.replace(word, symbol)

        # Allow only valid characters in the math expression
        if not all(char.isdigit() or char in "()+-*/. mathsqrt" for char in command):
            return "Sorry, I can't evaluate that."

        # Evaluate the math expression safely
        result = eval(command)

        # Return the result, rounded if necessary
        if isinstance(result, float):
            return round(result, 3)
        return result
    except Exception:
        return "Sorry, I couldn't calculate that."

# Function: Handles commands based on recognized keywords
def handle_command(command):
    # Check if the command matches a "joke" keyword
    if any(keyword in command for keyword in COMMAND_KEYWORDS["joke"]):
        joke = pyjokes.get_joke()
        print(f"Joke: {joke}")
        speak(joke)

    # Check if the command matches a "calculate" keyword
    elif any(keyword in command for keyword in COMMAND_KEYWORDS["calculate"]):
        result = interpret_math_expression(command)
        print(f"Result: {result}")
        speak(f"The result is {result}")

    # Check if the command matches an "exit" keyword
    elif any(keyword in command for keyword in COMMAND_KEYWORDS["exit"]):
        speak("Goodbye!")
        exit()

    # If no known command is found
    else:
        speak("Sorry, I didn't understand that.")

# === Adding Your Own Commands ===
# To add a new command:
# 1. Define a new keyword group in COMMAND_KEYWORDS.
#    Example: "weather": ["weather", "forecast"]
# 2. Add a corresponding condition in `handle_command`.
#    Example:
#    elif any(keyword in command for keyword in COMMAND_KEYWORDS["weather"]):
#        # Add your custom functionality here

# Main program loop
if __name__ == "__main__":
    speak("Hello! I am your simple assistant. How can I help you?")
    while True:
        user_command = listen()
        if user_command:
            handle_command(user_command)

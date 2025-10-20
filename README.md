# AI Workshop Demonstrations

**Type:** Python Scripts · **Tech Stack:** Python, OpenCV, PyAudio, Pygame, SpeechRecognition, NumPy · **Year:** 2025

## **Overview**

A collection of interactive Python demos showcasing AI concepts applied to small, creative projects. These scripts highlight real-time perception, decision-making, and user interaction using simple yet effective AI techniques.

## **Key Demonstrations**

* **Red Light, Green Light:** Camera-based motion detection game that eliminates players who move when they should not.
* **Smart Enemy AI:** A simulated opponent with visual awareness and pathfinding abilities that chases the player.
* **Voice Assistant:** A minimal speech-controlled assistant capable of responding to spoken commands.

## **Purpose**

This project demonstrates my ability to integrate computer vision, audio processing, and game logic into interactive prototypes — bridging AI concepts with practical, engaging applications.

---

## Setup Instructions

### 1. Install Python

1. **Go to the Python website**: [https://www.python.org/downloads/](https://www.python.org/downloads/)
2. **Download Python**:
   - **Windows**: Download the latest version (e.g., Python 3.x) installer (usually the `.exe` file).
   - **macOS**: Download the `.pkg` file for the latest version.
   - **Linux**: You may already have Python installed, or you can install it via your package manager (e.g., `sudo apt-get install python3` on Ubuntu/Debian).

3. **Install Python**:
   - **Windows**: Double-click the downloaded installer. 
     - **Important**: Check the box that says **"Add Python to PATH"** before clicking "Install".
   - **macOS**: Double-click the downloaded `.pkg` file and follow the instructions.
   - **Linux**: Use your package manager or follow instructions from the Python website.

Once Python is successfully installed, you can verify by opening a terminal (or Command Prompt on Windows) and typing:

```bash
python --version
```

If it shows something like `Python 3.x.x`, you’re good to go!

---

### 2. Set Up a Virtual Environment

A **virtual environment** allows you to create a separate, isolated space on your computer just for this project’s dependencies. This way, you don’t clutter your main system with project-specific packages.

1. **Open a terminal** (or Command Prompt if you’re on Windows).
2. **Navigate to the folder** where this repository is located. For example:
   ```bash
   cd path/to/this/repository
   ```
3. **Create the virtual environment**:
   ```bash
   python -m venv venv
   ```
   - Here, `venv` is the name of the folder that will store the virtual environment files.

4. **Activate the virtual environment**:
   - **Windows** (Command Prompt):
     ```bash
     venv\Scripts\activate
     ```
   - **Windows (PowerShell)**:
     ```powershell
     .\venv\Scripts\activate
     ```
   - **macOS/Linux**:
     ```bash
     source venv/bin/activate
     ```

When the virtual environment is activated, you’ll usually see `(venv)` (or similar) at the beginning of your terminal prompt.

---

### 3. Install Dependencies

In this repository, there should be a file named `requirements.txt`. This file lists all the additional Python packages you need to run the included programs.

1. **Ensure your virtual environment is activated** (see above step).
2. **Install the requirements**:
   ```bash
   pip install -r requirements.txt
   ```
3. **Wait for the installation to complete**. After this, all necessary packages should be installed in your virtual environment.

---

### 4. Run the Programs

There are three Python scripts in this repository:

1. `game_with_ai.py`
2. `red_light_green_light.py`
3. `simple_voice_assistant.py`

To run any of these scripts:

1. **Ensure your virtual environment is still activated**.
2. **Use the `python` command** followed by the script name. For example:
   ```bash
   python game_with_ai.py
   ```
   or
   ```bash
   python red_light_green_light.py
   ```
   or
   ```bash
   python simple_voice_assistant.py
   ```

Each script may have different functionality. Check the documentation (if provided) or follow any on-screen instructions once you run the scripts.

---

## 5. Deactivate the Virtual Environment

When you’re done working on this project, you can **deactivate** the virtual environment by simply typing:

```bash
deactivate
```

---

### 6. Troubleshooting

- If you type `python` and get an error like **`command not found`**, Python may not be installed correctly or may not be on your system’s PATH. See the instructions below.
- If you’re on Windows and the `activate` command fails, ensure you are using the correct path (`venv\Scripts\activate`) and not `venv/bin/activate`.
- If `pip install -r requirements.txt` fails, verify that you spelled the filename correctly and that `requirements.txt` is in the same directory you are in.

---

### 7. PATH Variable Issue

You may have some trouble when running the `python` command on Windows. If this is applies to you, follow the instructions below.

Certainly! Handling the PATH variable issue is crucial for making sure Python and its tools work correctly on your system. Here's a detailed explanation on how to resolve PATH-related problems:

---

### What is the PATH Variable?

The **PATH** variable is a system setting that tells your operating system where to look for executable programs. If Python is not added to the PATH during installation, your terminal/command prompt won’t know where to find the `python` or `pip` commands.

---

### How to Fix PATH Variable Issues

#### 1. **Verify if Python is in PATH**
   - Open a terminal (or Command Prompt on Windows).
   - Type:
     ```bash
     python --version
     ```
     or
     ```bash
     python3 --version
     ```
   - If you see something like `command not found` or an error, it means Python is not in your PATH.

---

#### 2. **Adding Python to PATH on Windows**

If you forgot to check the "Add Python to PATH" box during installation, you can manually add it:

1. **Locate Python Installation Directory**:
   - Python is usually installed in a folder like:
     ```
     C:\Users\<YourUsername>\AppData\Local\Programs\Python\Python3x\
     ```
     Replace `<YourUsername>` with your username, and `Python3x` with the version you installed (e.g., `Python39` for Python 3.9).

2. **Find the `Scripts` Folder**:
   - Inside the Python installation directory, there should be a subfolder named `Scripts`. The full path will look something like:
     ```
     C:\Users\<YourUsername>\AppData\Local\Programs\Python\Python3x\Scripts
     ```

3. **Add to PATH**:
   - Press `Win + R` to open the Run dialog.
   - Type `sysdm.cpl` and press Enter to open the **System Properties** window.
   - Go to the **Advanced** tab and click **Environment Variables**.
   - Under "System variables" or "User variables", find the variable named `Path` and click **Edit**.
   - Click **New** and add the following paths:
     ```
     C:\Users\<YourUsername>\AppData\Local\Programs\Python\Python3x\
     C:\Users\<YourUsername>\AppData\Local\Programs\Python\Python3x\Scripts
     ```
   - Click **OK** to close all dialogs.

4. **Test the PATH**:
   - Open a new Command Prompt and type:
     ```bash
     python --version
     ```
   - If it shows the Python version, it’s now correctly added to PATH.

---

#### 3. **Adding Python to PATH on macOS or Linux**

1. **Find Python Installation Path**:
   - Open a terminal and type:
     ```bash
     which python3
     ```
   - This will show the path where Python is installed, like `/usr/local/bin/python3`.

2. **Add to PATH**:
   - Open your shell configuration file. Depending on your shell, it could be one of these:
     - `~/.bashrc` (for Bash)
     - `~/.zshrc` (for Zsh)
     - `~/.bash_profile` (for older macOS systems)
   - Edit the file with a text editor, for example:
     ```bash
     nano ~/.bashrc
     ```
   - Add this line to include Python in your PATH:
     ```bash
     export PATH="/usr/local/bin:$PATH"
     ```
   - Save the file and exit.

3. **Apply Changes**:
   - Run the following command to reload the configuration:
     ```bash
     source ~/.bashrc
     ```
   - Test by typing:
     ```bash
     python3 --version
     ```
   - If it shows the Python version, it’s now correctly added to PATH.

---

### Other Tips

- **Use `python3` Instead of `python`**: Some systems (e.g., macOS and Linux) might require you to type `python3` instead of `python` due to differences in default Python versions.
- **Reinstall Python**: If adding to PATH manually is too complex, you can simply reinstall Python and ensure the "Add Python to PATH" box is checked during the installation process.

---

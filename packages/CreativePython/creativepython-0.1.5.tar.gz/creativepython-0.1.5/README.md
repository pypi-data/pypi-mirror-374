# CreativePython

CreativePython is a Python-based software environment for learning and developing algorithmic art projects.  It mirrors the [JythonMusic API](https://jythonmusic.me/api-reference/), and is powered by [PySide6](https://wiki.qt.io/Qt_for_Python) and [portaudio](http://portaudio.com/).

CreativePython is distributed under the MIT License.

- [Homepage](https://jythonmusic.me/)
- [Download All Examples [ZIP]](https://www.dropbox.com/scl/fo/rvc8m8pt4m0281qn0t4oi/AO2Y0W2qOrOcurlQmLa7M54?rlkey=0sf80bmov135tc85dk9k7ats6&dl=1)

This package is still under development.

# Requirements

Before installing CreativePython, you will need:

- **Python3**, version 3.9 or greater [[Download](https://www.python.org/downloads/)]
- **A C++ compiler** (see **Troubleshooting - CMake configuration failed** below)

# Beginner Installation (Windows/MacOS)

1. Download the [CreativePython Setup Script](https://www.dropbox.com/scl/fi/253bvfqsf0ij3rmza88q5/_creativepythonSetup.py?rlkey=iu4y4u8pujltgfx6kbjmodu9m&dl=1).

2. Open `creativePythonSetup.py` with IDLE, Python's Integrated Development Learning Environment.

3. From the IDLE toolbar, select `Run`, then `Run Module`.

4. CreativePython will check for its requirements on your system, download any missing requirements, and install its libraries.

5. If you see `[CreativePython Setup]: CreativePython installed successfully.`, you're all done!  You're ready to start using CreativePython in your Python code.

- To test the installation, download [playNote.py](https://www.dropbox.com/scl/fi/z6rkjy4xnofmg0t899se3/playNote.py?rlkey=o3t8c91ne6agj2lqf2aupl8m5&dl=1) and run it in IDLE.  You should hear a single C4 half-note.

**NOTE**: You can use the setup script in any Python3 environment - not just IDLE!

# Custom Installation

If you're familiar with Python development, we recommend installing CreativePython through the Command Prompt/Terminal.

## Windows

Install CreativePython using `pip`:

```
python -m pip install CreativePython
```

## MacOS

Use [Homebrew](https://brew.sh/) to install the prerequisite [portaudio](http://portaudio.com/) library, then install CreativePython using `pip`:

```
brew install portaudio
pip install CreativePython
```

## Linux

Use apt, or your preferred package manager, to install the prerequisite [portaudio](http://portaudio.com/) library, then install CreativePython using `pip`:

```
sudo apt-get portaudio
pip install CreativePython
```

# Using CreativePython

## Importing Libraries

CreativePython's core modules are the `music`, `gui`, `image`, `timer`, `osc`, and `midi` libraries.  You can import these libraries into your python code using:

```
import music
from music import *
from music import Note, Play, C4, HN
```

Or a similar statement.  CreativePython includes a number of useful constants, so we recommend using wildcard imports like `from music import *`.

**NOTE**: The first time you import `music`, CreativePython will ask permission to download a high-quality soundfont (FluidR3 G2-2.sf2) for you.  You should only have to do this once.

## Running CreativePython programs

CreativePython is designed for use in Python's Interactive Mode.  To use Interactive Mode, enter a command like:

```
python -i <filename>.py
```

## Example

Download [playNote.py](https://www.dropbox.com/scl/fi/z6rkjy4xnofmg0t899se3/playNote.py?rlkey=o3t8c91ne6agj2lqf2aupl8m5&dl=1):

```
# playNote.py
# Demonstrates how to play a single note.
 
from music import *        # import music library
 
note = Note(C4, HN)        # create a middle C half note
Play.midi(note)            # and play it!
```

In a terminal, run the code in interactive mode:

```
python -i playNote.py
```

If this is the first time you've used CreativePython, it will ask to download a soundfont.

After you do, you should hear a single C4 half-note.

## Troubleshooting

### CMake configuration failed

Some of CreativePython's libraries need to compile C++ code during installation.

- On Windows, download and install [Visual Studio Build Tools 2022](https://visualstudio.microsoft.com/downloads/).  In the Visual Studio installer, make sure "C++ Build Tools" is checked.

- On MacOS, you can download and install [XCode from the App Store](https://apps.apple.com/us/app/xcode/id497799835?mt=12).

Restart your computer, then try installing CreativePython again.
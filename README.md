# Clingonia by MadMotion (Early Access)

![Flatland animation](https://i.imgur.com/9cNtWjs.gif)

## 🚆 Flatland
Flatland is a [railway scheduling challenge](https://flatland.aicrowd.com/intro.html) hosted by AICrowd to address the problem of multi-agent pathfinding for trains in large railway networks. This repository provides the GUI-based software "Clingonia" to generate, build, modify, load, and save environments, run simulations, and review results.

<br>

## 🏡 Repository structure

- 📁 `asp` is where YOU can put your asp files. Contains working `lp` files.
- 📁 `code` contains python source codes.
- 📁 `data` contains images and saved parameters.
- 📁 `help_texts` provide information inside the program.
- 📝 `main.py` is the only python file YOU have to care about. Its execution starts the program.
- 📝 `README.md` is what you are reading right now.

<br>

## ⚙️ Please note:

⚠️ This software is optimized for Windows platforms; however, it runs on macOS.

<br>

## 🌱 Getting started: Flatland and Clingo

### 📜 Prerequisites

It is recommended to install [Anaconda](https://www.anaconda.com/distribution/) and create a new conda environment:
```
conda create python=3.7 --name flatland
conda activate flatland
```

📦 Then, install the stable release of Flatland:
```
pip install flatland-rl
```

📦 To have access to clingo, install the required package:
```
conda install -c potassco clingo
```

📦 Make sure that you also have installed the following required packages:
```
pip show pillow
pip show imageio
```

<br>

### 🖥️ Installation

To use this repository locally, clone it:
```
git clone git@github.com:M4X-VOGEL/Flatland-ASP-GUI.git
```

<br>

# 🏛️ Our Program

### 🐣 Initial development

First of all, individual developers are responsible for writing encodings in clingo that are capable of solving Flatland problems.  During the development phase, the `lp` representation of the environment may be beneficial for initial testing and debugging of the encoding or encodings.  Keep in mind that several encodings can be called simulatenously by clingo, for example:
```
clingo env.lp example1.lp example2.lp
```

The order is not important.  What will ultimately be necessary is that the output be appropriately formatted in the following manner:
`action(train(ID), Action, Time).` 

The `Action` variable must be one of the following:
- `move_forward`
- `move_left`
- `move_right`
- `wait`

Once an encoding or set of encodings has been developed that produces valid paths in the form of the appropriate `action(...)` output, developers can initialize the program.

<br>

### 🗺️ Custom environment encodings

Valid predicates are:
- `train(ID).`
- `start(ID,(X,Y),Dep,Dir).`
- `end(ID,(X,Y),Arr).`
- `cell((X,Y),Track).`

Keep in mind:
- `row=X`
- `col=Y`
- There are no spaces inbetween the variables.

<br>

## 🚀 Program initialization

1. It is optional to put your `lp` files into the 📁 `asp` folder. They can be in any directory.
2. Ensure that you are in the directory of your cloned repository with 📝 `main.py` and type the following:
```
python main.py
```
This will launch the program.

<br>

### 🛠️ Troubleshooting

If you encounter unexpected issues, it may be due to any number of reasons. This is still an early version and we are hard at work at MadMotion to get our program to the next level. Feel free to report any issues to us so we can address them promptly.

<br>

### ⚠️ Known issues

- The software will crash while building your own environment as soon as you place too many tracks and trains. Suggestion: Keep it small for now (max. 12x12).
- The displaying of the `GIF` may be distorted. 
- You cannot set the parameters after loading a custom environement into the program, yet.

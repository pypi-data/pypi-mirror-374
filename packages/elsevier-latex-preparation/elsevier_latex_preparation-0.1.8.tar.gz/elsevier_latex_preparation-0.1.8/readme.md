# LaTeX File Merger and Resource Copier for Elsevier Submission ✨📄

This Python tool processes a main LaTeX file and its included resources, 
preparing it for submission to **Elsevier Editorial Manager**. 
Elsevier requires manuscripts to be uploaded as a **single `.tex` file** 
with all references (images, bibliography files, etc.) in a **single folder** 
without subfolders. 🚫🗂

This script merges all `\input` and `\include` commands into the main LaTeX file 
and copies all referenced files into a flat destination folder. 🗂️️

## Features 🌟
- Resolves `\input` and `\include` commands recursively 🔄  
- Copies all referenced resources (images 🖼️, bibliography files 📚, and others) into a single folder  
- Updates LaTeX file paths to point to the new flat folder 🛣️  
- Ignores commands that do not reference external files 🚫  
- Optional callbacks for progress ⏱️ and file counters 🔢  
- **Tkinter GUI interface** with:  
  - File selection dialogs 📂  
  - Progress bar 📊  
  - Counters for images, bibliography, and other files  
  - Clickable counters that open a window showing copied files 👀  
- Designed to produce a folder ready for **Elsevier Editorial Manager** ✅

## Installation ️
Can be installed via pip:

```bash 
pip install elsevier-latex-preparation
```

## Usage (GUI) 🖱️

Run the GUI:

```python
from elsevier_latex_preparation import run_gui

run_gui()
```

## Usage (Programmatic) 💻

```python
from elsevier_latex_preparation import merge_latex_and_move_ref

# Path to the main LaTeX file
main_file = "path/to/main.tex"

# Destination folder where the single-file LaTeX package will be created
destination_folder = "path/to/destination"

# Optional callbacks for progress and file tracking
def progress_callback(percent):
    print(f"Progress: {percent:.2f}% ⏳")

def files_counter(files_list):
    print(f"Copied files: {len(files_list)} 📂")
    
def merger_callback(merged_list):
    print(f"Merged files: {len(merged_list)} 📂")

# Merge LaTeX file and copy resources
merge_latex_and_move_ref(
    main_file,
    destination_folder,
    progress_callback=progress_callback,
    files_copied_counter_callback=files_counter,
    merge_tracker_callback=merger_callback
)
```

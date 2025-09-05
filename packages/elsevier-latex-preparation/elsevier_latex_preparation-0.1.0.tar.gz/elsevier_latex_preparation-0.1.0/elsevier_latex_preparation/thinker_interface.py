from .latex_coversion_code import merge_latex_and_move_ref
from tkinter import filedialog, messagebox
from tkinter import ttk, font as tkfont
from ttkthemes import ThemedTk
import tkinter as tk
import threading
import os


# -------------------- File selection functions --------------------
def __select_main_file():
    """Open file dialog to select main LaTeX file."""
    file_path = filedialog.askopenfilename(filetypes=[("LaTeX files", "*.tex")])
    if file_path:
        main_file_entry.delete(0, tk.END)
        main_file_entry.insert(0, file_path)


def __select_destination_folder():
    """Open directory dialog to select destination folder."""
    folder_path = filedialog.askdirectory()
    if folder_path:
        destination_folder_entry.delete(0, tk.END)
        destination_folder_entry.insert(0, folder_path)


# -------------------- GUI callbacks --------------------
def __update_progress(value):
    """Update the progress bar and percentage label."""
    progress['value'] = value
    progress_label.config(text=f"{int(value)}%")
    root.update_idletasks()


def __update_counters(files_copied):
    """Update counters for images, bibliography, and other files."""
    counter_img = 0
    counter_bib = 0
    counter_other = 0

    global copied_png_files, copied_bib_files, copied_other_files
    copied_png_files = []
    copied_bib_files = []
    copied_other_files = []

    for files in files_copied:
        file_base_name, file_extension = os.path.splitext(files)
        if file_extension.lower() in ['.png', '.jpg', '.jpeg']:
            counter_img += 1
            copied_png_files.append(files)
        elif file_extension.lower() == '.bib':
            counter_bib += 1
            copied_bib_files.append(files)
        else:
            counter_other += 1
            copied_other_files.append(files)

    png_label.config(text="Images: " + str(counter_img))
    bib_label.config(text="Bibliography: " + str(counter_bib))
    other_label.config(text="Other: " + str(counter_other))
    root.update_idletasks()


def __update_mergers(merged_files):
    """Update merged_files counters"""
    for f in merged_files:
        if f not in merged_files_list:
            merged_files_list.append(f)

    merged_label.config(text="Latex files: " + str(len(merged_files_list)))
    root.update_idletasks()


def __show_info(title, message):
    """Show info message box safely from threads."""
    root.after(0, lambda: messagebox.showinfo(title, message))


def __show_error(title, message):
    """Show error message box safely from threads."""
    root.after(0, lambda: messagebox.showerror(title, message))


# -------------------- Conversion --------------------
def __convert_threaded():
    """Run the LaTeX merge/conversion in a separate thread for UI responsiveness."""
    main_file = main_file_entry.get()
    destination_folder = destination_folder_entry.get()

    if not os.path.isfile(main_file):
        __show_error("Error", "Please select a valid main file.")
        return
    if not os.path.isdir(destination_folder):
        __show_error("Error", "Please select a valid destination folder.")
        return

    def task():
        try:
            merge_latex_and_move_ref(
                main_file, destination_folder,
                progress_callback=__update_progress,
                files_copied_counter_callback=__update_counters,
                merge_tracker_callback=__update_mergers
            )
            __update_progress(100)
            __show_info("Success", "Conversion completed successfully!")
        except Exception as e:
            __show_error("Error", f"An error occurred: {e}")
        finally:
            __update_progress(0)

    threading.Thread(target=task).start()


# -------------------- Open file list windows --------------------
def __open_file_list(title, file_list):
    """Open a new window displaying the list of copied files."""
    new_window = tk.Toplevel(root)
    new_window.title(title)
    new_window.geometry("400x300")
    new_window.resizable(True, True)

    text_widget = tk.Text(new_window, wrap="none")
    text_widget.pack(expand=True, fill="both", padx=5, pady=5)

    for f in file_list:
        text_widget.insert("end", f"{f}\n")
    text_widget.config(state="disabled")  # read-only


# -------------------- GUI Setup --------------------
def run_gui(ttk_theme="Breeze"):
    """Initialize and run the Tkinter GUI."""

    global root, main_file_entry, destination_folder_entry
    global progress, progress_label, bold_font, italic_font
    global png_label, bib_label, other_label, title_label, merged_label
    global copied_png_files, copied_bib_files, copied_other_files, merged_files_list

    root = ThemedTk(theme=ttk_theme)
    root.title("Elsevier Submission - LaTeX Preparation")
    root.resizable(False, False)

    bold_font = tkfont.Font(size=12, weight="bold")
    italic_font = tkfont.Font(size=12, slant="italic")

    # Main file selection
    tk.Label(root, text="Main file:", font=italic_font, anchor="e").grid(row=0, column=0, padx=5, pady=5, sticky="e")
    main_file_entry = ttk.Entry(root, width=50)
    main_file_entry.grid(row=0, column=1, padx=5, pady=5)
    ttk.Button(root, text="Browse", command=__select_main_file).grid(row=0, column=2, padx=5, pady=5)

    # Destination folder selection
    tk.Label(
        root,
        text="Destination\nFolder:",
        font=italic_font,
        anchor="e",
        justify="right"
    ).grid(row=1, column=0, padx=5, pady=5, sticky="e")
    destination_folder_entry = ttk.Entry(root, width=50)
    destination_folder_entry.grid(row=1, column=1, padx=5, pady=5)
    ttk.Button(root, text="Browse", command=__select_destination_folder).grid(row=1, column=2, padx=5, pady=5)

    # -------------------- File counter --------------------
    counter_frame = tk.Frame(root)
    counter_frame.grid(row=3, column=1, padx=10, ipadx=50, pady=(5, 5))
    counter_frame.grid_columnconfigure((0, 1, 2), weight=1)

    merged_files_list = []
    merged_label = tk.Label(counter_frame, text="Latex files: 0", font=italic_font, anchor="center", cursor="hand2")
    merged_label.grid(row=0, column=0)
    merged_label.bind("<Button-1>", lambda e: __open_file_list("Merged Files", merged_files_list))

    copied_png_files = []
    png_label = tk.Label(counter_frame, text="Images: 0", font=italic_font, anchor="center", cursor="hand2")
    png_label.grid(row=0, column=1)
    png_label.bind("<Button-1>", lambda e: __open_file_list("Copied Images", copied_png_files))

    copied_bib_files = []
    bib_label = tk.Label(counter_frame, text="Bibliography: 0", font=italic_font, anchor="center", cursor="hand2")
    bib_label.grid(row=0, column=2)
    bib_label.bind("<Button-1>", lambda e: __open_file_list("Copied Bibliography", copied_bib_files))

    copied_other_files = []
    other_label = tk.Label(counter_frame, text="Other: 0", font=italic_font, anchor="center", cursor="hand2")
    other_label.grid(row=0, column=3)
    other_label.bind("<Button-1>", lambda e: __open_file_list("Copied Other", copied_other_files))

    # Progress bar
    style = ttk.Style()
    style.configure("TProgressbar", thickness=20)
    progress = ttk.Progressbar(root, orient="horizontal", mode="determinate", style="TProgressbar")
    progress.grid(row=4, column=1, padx=5, pady=5, sticky="ew")

    progress_label = tk.Label(root, text="0%", font=italic_font)
    progress_label.grid(row=4, column=2, padx=5, pady=5, sticky="w")

    # Convert button
    ttk.Button(root, text="Convert", command=__convert_threaded).grid(row=5, column=0, columnspan=3, pady=10)

    root.mainloop()

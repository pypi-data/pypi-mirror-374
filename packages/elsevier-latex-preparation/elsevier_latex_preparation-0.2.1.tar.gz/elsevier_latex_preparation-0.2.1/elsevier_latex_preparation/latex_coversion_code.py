import shutil
import os
import re

# Global ignore extensions
IGNORE_EXTENSIONS = {".bst", ".ins", ".cls", ".dtx", ".tex"}


def merge_latex_text(content, main_file_dir, merge_updater_callback: callable, is_main=False):
    """
    Merges a LaTeX file content by resolving \input and \include commands recursively.
    If not the main file, removes preamble and postamble if present.

    Parameters:
    - content: str, LaTeX content
    - main_file_dir: str, directory of the main LaTeX file
    - is_main: bool, whether this is the main file (skip preamble removal for main file)
    - merge_updater_callback: function, optional callback to track merged files

    Returns:
    - str: merged LaTeX content
    """
    if not is_main:
        if "\\begin{document}" in content:
            content = content.split("\\begin{document}", 1)[1]
        if "\\end{document}" in content:
            content = content.split("\\end{document}", 1)[0]

    # Regex to find \input or \include commands
    regex_input_include = re.compile(r"\\(?:input|include){(.+?)}")

    # Recursively resolve included files
    for match in regex_input_include.finditer(content):
        relative_path = match.group(1).replace("/", os.sep)

        # Add .tex extension if missing
        if not relative_path.endswith(".tex"):
            relative_path += ".tex"

        absolute_path = os.path.join(main_file_dir, relative_path)

        if os.path.exists(absolute_path):
            merge_updater_callback(relative_path)

            with open(absolute_path, "r", encoding="utf-8") as included_file:
                included_content = merge_latex_text(

                    included_file.read(), main_file_dir,
                    merge_updater_callback=merge_updater_callback

                )

            # Replace \input with actual file content
            content = content.replace(match.group(0), included_content)

    return content.strip()


def find_file(base_dir, file_ref, allow_broad_search=False):
    """
    Search for a file in base_dir. Returns the absolute path if found, else None.

    Parameters:
    - base_dir: str, the root directory to start searching from
    - file_ref: str, the filename or path referenced in LaTeX
    - allow_broad_search: bool, if True, search recursively through all subdirectories

    Returns:
    - str or None: Absolute path to the file if found, otherwise None
    """

    # Remove leading/trailing whitespace from the file reference
    file_ref = file_ref.strip()

    # Replace forward slashes with OS-specific separator
    base_name = file_ref.replace("/", os.sep)

    # Split the filename and extension
    file_name, ext = os.path.splitext(os.path.basename(base_name))
    has_extension = ext != ""  # Flag if the file reference includes an extension

    if not allow_broad_search:
        # Direct search: check the path relative to base_dir
        candidate_path = os.path.join(base_dir, base_name)

        # If the exact file exists and is not in ignored extensions, return it
        if os.path.isfile(candidate_path) and ext not in IGNORE_EXTENSIONS:
            return candidate_path

        # If no extension is provided, search in the directory for a matching base name
        elif not has_extension and os.path.isdir(os.path.dirname(candidate_path)):
            for f in os.listdir(os.path.dirname(candidate_path)):
                f_base, f_ext = os.path.splitext(f)
                # Match base name, but skip ignored extensions
                if f_base == file_name and f_ext not in IGNORE_EXTENSIONS:
                    return os.path.join(os.path.dirname(candidate_path), f)

    else:
        # Broad search: recursively walk the directory tree
        for root, _, files in os.walk(base_dir):
            for f in files:
                f_base, f_ext = os.path.splitext(f)
                # Match the file based on whether extension is specified
                if (has_extension and f == os.path.basename(base_name) or
                    not has_extension and f_base == file_name) and f_ext not in IGNORE_EXTENSIONS:
                    return os.path.join(root, f)

    # Return None if file not found
    return None


def merge_latex_and_move_ref(
    main_file, destination_folder,
    allow_broad_search: bool = False,
    progress_callback: callable = None,
    files_copied_counter_callback: callable = None,
    merge_tracker_callback: callable = None
):
    """
    Merge a main LaTeX file with all its \input included files, copying all referenced resources.

    Parameters:
    - main_file: str, path to main .tex file
    - destination_folder: str, path to copy files into
    - progress_callback: function, optional callback to report progress (0-100)
    - files_copied_counter_callback: function, optional callback to report list of copied files
    - merge_tracker_callback: function, optional callback to track merged files

    Returns:
    - list of copied files
    """
    if not os.path.exists(destination_folder):
        os.makedirs(destination_folder)

    with open(main_file, "r", encoding="utf-8") as f:
        content = f.read()

    merged_files = []

    def merge_updater_callback(file_path):
        if merge_tracker_callback and file_path not in merged_files:
            merged_files.append(file_path)
            merge_tracker_callback(merged_files)

    content = merge_latex_text(
        content, os.path.dirname(main_file),
        is_main=True, merge_updater_callback=merge_updater_callback
    )

    regex_paths = re.compile(r"\\(\w+)(?:\[(.*?)\])?(?<![_^]){(.+?)}")

    ignore_command_list = [
        'documentclass', 'usepackage', 'newcommand', 'renewcommand', 'setlength',
        'nompreamble', 'nompostamble', 'color', 'begin', 'title', 'author',
        'cortext', 'ead', 'textsubscript', 'EUR', 'end', 'section', 'subsection',
        'subsubsection', 'paragraph', 'chapter', 'cite', 'ref', 'caption', 'label',
        'textbf', 'textit', 'vspace', 'hspace', 'item', 'maketitle', 'footnote',
    ]

    files_copied = []
    base_dir = os.path.dirname(main_file)
    matches = list(regex_paths.finditer(content))
    total_matches = len(matches)

    for idx, match in enumerate(matches, 1):
        command = match.group(1)
        file_ref = match.group(3).strip()
        if command in ignore_command_list:
            continue

        absolute_path = find_file(base_dir, file_ref, allow_broad_search)

        if absolute_path:
            dest_file_name = os.path.basename(absolute_path)
            destination_path = os.path.join(destination_folder, dest_file_name)

            # Avoid overwriting
            i = 1
            orig_base, orig_ext = os.path.splitext(dest_file_name)
            while os.path.isfile(destination_path):
                dest_file_name = f"{orig_base}_{i}{orig_ext}"
                destination_path = os.path.join(destination_folder, dest_file_name)
                i += 1

            shutil.copy(absolute_path, destination_path)
            files_copied.append(dest_file_name)
            if files_copied_counter_callback:
                files_copied_counter_callback(files_copied)

            # Update LaTeX content
            content = content.replace(file_ref, dest_file_name)

        if progress_callback:
            progress_callback(idx / total_matches * 100)

    new_main_file = os.path.join(destination_folder, os.path.basename(main_file))
    with open(new_main_file, "w", encoding="utf-8") as f:
        f.write(content)

    print(f"LaTeX files merged and resources moved to {destination_folder}.")
    return files_copied


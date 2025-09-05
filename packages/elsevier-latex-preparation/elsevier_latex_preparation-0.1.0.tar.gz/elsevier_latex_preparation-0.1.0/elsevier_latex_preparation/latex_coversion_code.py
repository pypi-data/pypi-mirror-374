import shutil
import os
import re


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


def merge_latex_and_move_ref(

        main_file, destination_folder,
        progress_callback: callable=None,
        files_copied_counter_callback: callable=None,
        merge_tracker_callback: callable=None

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

    # Read main LaTeX file
    with open(main_file, "r", encoding="utf-8") as f:
        content = f.read()

    merged_files = []

    def merge_updater_callback(file_path):

        if merge_tracker_callback and file_path not in merged_files:
            merged_files.append(file_path)
            merge_tracker_callback(merged_files)

    # Resolve \input commands recursively
    content = merge_latex_text(

        content, os.path.dirname(main_file),
        is_main=True, merge_updater_callback=merge_updater_callback

    )

    # Regex to find LaTeX file references (e.g., \includegraphics, bibliography)
    regex_paths = re.compile(r"\\(\w+)(?:\[(.*?)\])?(?<![_^]){(.+?)}")

    # Ignore these LaTeX commands (no external file)
    ignore_command_list = [
        'documentclass', 'usepackage', 'newcommand', 'renewcommand', 'setlength',
        'nompreamble', 'nompostamble', 'color', 'begin', 'title', 'author',
        'cortext', 'ead', 'textsubscript', 'EUR', 'end', 'section', 'subsection',
        'subsubsection', 'paragraph', 'chapter', 'cite', 'ref', 'caption', 'label',
        'textbf', 'textit', 'vspace', 'hspace', 'item', 'maketitle', 'footnote',
    ]

    ignore_extensions = {".bst", ".ins", ".cls", ".dtx", ".tex"}  # do not copy these

    controlled_commands = []
    controlled_options = []
    controlled_content = []
    ignored_commands = []

    files_copied = []
    base_dir = os.path.dirname(main_file)

    matches = list(regex_paths.finditer(content))
    total_matches = len(matches)

    # Iterate over all LaTeX commands referencing files
    for idx, match in enumerate(matches, 1):
        command = match.group(1)
        ignore_command = command in ignore_command_list

        if ignore_command:
            if command not in ignored_commands:
                ignored_commands.append(command)
        else:
            # Keep track of controlled commands and content
            if command not in controlled_commands:
                controlled_commands.append(command)
                controlled_content.append([match.group(3)])
                controlled_options.append([match.group(2)])
            else:
                index = controlled_commands.index(command)
                controlled_content[index].append(match.group(3))
                controlled_options[index].append(match.group(2))

            # Determine file path
            base_name = match.group(3).replace("/", os.sep)
            file_name, ext = os.path.splitext(os.path.basename(base_name))
            has_extension = ext != ""

            # Search in directory tree
            for __root, _, files in os.walk(base_dir):
                for file in files:
                    file_base_name, file_extension = os.path.splitext(file)

                    if has_extension:
                        found = os.path.basename(base_name) == file and file_extension not in ignore_extensions
                    else:
                        found = file_base_name == os.path.basename(base_name) and file_extension not in ignore_extensions

                    if found:
                        absolute_path = os.path.join(__root, file)
                        destination_path = os.path.join(destination_folder, file)
                        files_copied.append(file)

                        # Copy file if exists
                        if os.path.isfile(absolute_path):
                            shutil.copy(absolute_path, destination_path)

                            # Optional callback with current copied files
                            if files_copied_counter_callback:
                                files_copied_counter_callback(files_copied)

                            # Update LaTeX content to new path
                            if has_extension:
                                content = content.replace(match.group(3), os.path.basename(file))
                            else:
                                content = content.replace(match.group(3), file_base_name)
                        break

            # Update progress callback
            if progress_callback:
                progress_callback(idx / total_matches * 100)

    # Write new main file to destination
    new_file_name = os.path.join(destination_folder, os.path.basename(main_file))
    with open(new_file_name, "w", encoding="utf-8") as f:
        f.write(content)

    print(f"LaTeX files merged and resources moved to {destination_folder}.")
    return files_copied

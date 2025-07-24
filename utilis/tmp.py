import os
import re

def collapse_multiple_spaces(folder_path):
    """
    Iterates through .txt files in a folder and replaces
    sequences of more than one space with a single space.
    """
    if not os.path.isdir(folder_path):
        print(f"Error: Folder not found at path: {folder_path}")
        return

    print(f"Scanning folder: {folder_path}")

    # The regex pattern ' {2,}' finds any sequence of two or more space characters
    space_pattern = re.compile(r' {2,}')

    for filename in os.listdir(folder_path):
        if filename.endswith(".txt"):
            filepath = os.path.join(folder_path, filename)
            
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    text = f.read()

                # Replace all found sequences with a single space
                modified_text = space_pattern.sub(' ', text)

                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(modified_text)
                
                print(f"Cleaned whitespace in: {filename}")

            except Exception as e:
                print(f"An error occurred while processing {filename}: {e}")

if __name__ == '__main__':
    # --- CONFIGURATION ---
    # Set the path to the folder where your .txt files are located.
    TARGET_FOLDER = r'C:\Users\Jakub\IncunabuLM\data\KorpusSt_Out'
    # --------------------
    
    collapse_multiple_spaces(TARGET_FOLDER)
    print("Processing finished.")
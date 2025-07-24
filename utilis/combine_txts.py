import os

def combine_txt_files(root_folder, output_filepath):
    if not os.path.isdir(root_folder):
        print(f"Error: Root folder not found at path: {root_folder}")
        return

    all_text_content = []
    file_count = 0
    
    print(f"Starting search in: {root_folder}")

    # os.walk recursively goes through the directory tree
    for dirpath, _, filenames in os.walk(root_folder):
        for filename in filenames:
            if filename.endswith(".txt"):
                file_path = os.path.join(dirpath, filename)
                
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        all_text_content.append(f.read())
                        file_count += 1
                        print(f"Adding file: {file_path}")
                except Exception as e:
                    print(f"Could not read file {file_path}: {e}")

    if not all_text_content:
        print("No .txt files were found. Output file will not be created.")
        return

    # Join the content of all files, separated by a special token
    separator = "\n\n<|endoftext|>\n\n"
    final_text = separator.join(all_text_content)

    try:
        # Get the directory for the output file and create it if it doesn't exist
        output_dir = os.path.dirname(output_filepath)
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
            print(f"Created output directory: {output_dir}")

        with open(output_filepath, 'w', encoding='utf-8') as f_out:
            f_out.write(final_text)
        
        print(f"\nSuccessfully combined {file_count} files.")
        print(f"Output saved to: {output_filepath}")

    except Exception as e:
        print(f"An error occurred while writing the output file: {e}")


if __name__ == '__main__':
    ROOT_FOLDER = r'C:\Users\Jakub\IncunabuLM\data'
    
    OUTPUT_FILEPATH = r'C:\Users\Jakub\IncunabuLM\data_train\data_final.txt'
    
    combine_txt_files(ROOT_FOLDER, OUTPUT_FILEPATH)
import os
import xml.etree.ElementTree as ET
import re

def get_text_recursively(element):
    """
    (FIX for Bug #1)
    Recursively walks through an XML element to extract all text, correctly
    joining words split by inline tags (like <corr>) and treating <lb/> as a newline.
    """
    if element is None:
        return ""
    
    text_parts = []
    
    # Add the text that comes before any child elements
    if element.text:
        text_parts.append(element.text)

    # Process all child elements
    for child in element:
        # Get the clean tag name (without namespace)
        clean_tag = re.sub(r'\{.*\}', '', child.tag)
        
        # If the tag is a line break, append a newline character
        if clean_tag == 'lb':
            text_parts.append('\n')
        
        # Recursively process the child element to get its text
        text_parts.append(get_text_recursively(child))
        
        # IMPORTANT: Append the tail text of the child element
        # This is the text that comes *after* an inline tag
        if child.tail:
            text_parts.append(child.tail)

    return "".join(text_parts)

def post_process_text(text):
    """
    Applies all the requested formatting rules to the extracted text.
    """
    # (FIX for Bug #5) Split words on internal uppercase letters
    # Example: excelsisChwała -> excelsis Chwała
    processed_text = re.sub(r'([a-ząćęłńóśźż])([A-ZĄĆĘŁŃÓŚŹŻ])', r'\1 \2', text)

    # (FIX for Bug #4) Remove Roman numerals
    # This pattern matches Roman numerals as whole words
    roman_numeral_pattern = r'\b(M{0,4}(CM|CD|D?C{0,3})(XC|XL|L?X{0,3})(IX|IV|V?I{0,3}))\b'
    processed_text = re.sub(roman_numeral_pattern, '', processed_text, flags=re.IGNORECASE)

    # (FIX for Bug #3) Ensure space after period and capitalize the next letter
    # Example: by\u0142y.podstawkowie -> by\u0142y. Podstawkowie
    def capitalize_after_period(match):
        return '. ' + match.group(1).upper()
    processed_text = re.sub(r'\.\s*([a-ząćęłńóśźż])', capitalize_after_period, processed_text)
    
    # Also ensure a space if the letter is already uppercase
    processed_text = re.sub(r'\.([A-ZĄĆĘŁŃÓŚŹŻ])', r'. \1', processed_text)

    # (FIX for Bug #2) Remove periods at the beginning of any line
    processed_text = re.sub(r'^\.\s*', '', processed_text, flags=re.MULTILINE)
    
    # Final cleanup of excessive whitespace and empty lines
    lines = [line.strip() for line in processed_text.split('\n') if line.strip()]
    return "\n".join(lines)


def extract_and_clean_xml_folder(input_folder, output_folder):
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
        print(f"Output folder created: {output_folder}")

    for filename in os.listdir(input_folder):
        if filename.endswith(".xml"):
            input_filepath = os.path.join(input_folder, filename)
            
            try:
                tree = ET.parse(input_filepath)
                root = tree.getroot()
                
                # We need the namespace for finding the body initially
                namespace_match = re.match(r'\{.*\}', root.tag)
                ns = {'tei': namespace_match.group(0)[1:-1]} if namespace_match else {}

                body = root.find('.//tei:body', ns) if ns else root.find('.//body')

                if body is None:
                    print(f"Warning: <body> tag not found in {filename}. Skipping.")
                    continue

                # Use the robust recursive function to extract raw text
                raw_text = get_text_recursively(body)
                
                # Apply all post-processing fixes
                final_text = post_process_text(raw_text)

                if not final_text:
                    print(f"Warning: No text content found after processing {filename}. Output file may be empty.")

                base_filename = os.path.splitext(filename)[0]
                output_filename = f"{base_filename}.txt"
                output_filepath = os.path.join(output_folder, output_filename)

                with open(output_filepath, 'w', encoding='utf-8') as f_out:
                    f_out.write(final_text)
                
                print(f"Processed: {filename} -> {output_filename}")

            except ET.ParseError:
                print(f"Error: {filename} is not a valid XML file. Skipping.")
            except Exception as e:
                print(f"An unexpected error occurred while processing {filename}: {e}")

if __name__ == '__main__':
    INPUT_FOLDER = r'C:\Users\Jakub\IncunabuLM\data\KorpusSt'
    OUTPUT_FOLDER = r'C:\Users\Jakub\IncunabuLM\data\KorpusSt_Out'
    
    print("Processing started...")
    extract_and_clean_xml_folder(INPUT_FOLDER, OUTPUT_FOLDER)
    print("Processing finished.")
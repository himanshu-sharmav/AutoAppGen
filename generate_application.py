import os
import zipfile
import google.generativeai as genai
# import json

# Set up your Gemini API key
genai.configure(api_key='AIzaSyDbXU8x7EKRGrHa6LiuBKhBk8AsV0m_d7E')  # Replace with your Gemini API key

FILE_LIMIT = 20

def get_user_input():
    application_description = input("Describe the application you want to build: ")
    return application_description

def call_gemini_engineer(application_description):
    response = genai.generate_text(
        model="models/text-bison-001",
        prompt=f"Generate a file structure and code for the following application: {application_description}"
    )
    ai_output = response.candidates[0]['output']
    print("AI Output:", ai_output)  # Debugging: Print the AI output to understand its format
    return ai_output

def parse_ai_output(ai_output):
    file_structure = {}
    current_file = None
    current_content = []

    for line in ai_output.split('\n'):
        if line.startswith('```'):
            if current_file is None:
                # Start of a new file
                current_file = line[3:].strip()
                current_content = []
            else:
                # End of the current file
                file_structure[current_file] = '\n'.join(current_content)
                current_file = None
                current_content = []
        elif current_file is not None:
            current_content.append(line)
    
    # Debugging: Print parsed file structure
    for key, value in file_structure.items():
        print(f"File: {key}, Content: {value[:100]}...")  # Print first 100 characters of each file for inspection

    return file_structure
def generate_files_from_structure(file_structure, base_dir="output"):
    os.makedirs(base_dir, exist_ok=True)

    file_count = 0
    for filepath, content in file_structure.items():
        if file_count >= FILE_LIMIT:
            print(f"File limit of {FILE_LIMIT} reached, stopping file generation.")
            break

        file_path = os.path.join(base_dir, filepath)
        if not os.path.splitext(file_path)[1]:  # Skip directories
            os.makedirs(file_path, exist_ok=True)
            continue

        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with open(file_path, 'w') as file:
            file.write(content)
            print(f"Wrote to {file_path} ({len(content)} bytes)")

        file_count += 1


def create_zip_file(source_dir, output_filename):
    with zipfile.ZipFile(output_filename, 'w') as zipf:
        for root, dirs, files in os.walk(source_dir):
            for file in files:
                file_path = os.path.join(root, file)
                print(f"Adding {file_path} to zip file")  # Debugging: Print the file path being added to the zip
                zipf.write(file_path, os.path.relpath(file_path, source_dir))

def main():
    application_description = get_user_input()
    ai_output = call_gemini_engineer(application_description)
    print("AI Output String:", ai_output)  # Debugging: Print the AI output string

    try:
        file_structure = parse_ai_output(ai_output)
        print("Parsed File Structure:", file_structure)  # Debugging: Print parsed file structure
    except Exception as e:
        print(f"Failed to parse AI output: {e}. Please try again.")
        return

    generate_files_from_structure(file_structure)
    create_zip_file('output', 'generated_application.zip')
    print("Application generated and zipped successfully.")

if __name__ == "__main__":
    main()

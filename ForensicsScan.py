import os
import shutil
import logging
from tqdm import tqdm
import asyncio
import chardet
from PIL import Image
import fitz
import docx

lock = asyncio.Lock()

async def is_text_file(filepath):
    """Checks if the file can be successfully decoded as text."""
    try:
        with open(filepath, 'rb') as file:
            raw_data = file.read()
            result = chardet.detect(raw_data)
            encoding = result['encoding']
            confidence = result['confidence']

            # Increase the confidence threshold to 0.9 (optional, adjust cautiously)
            if confidence > 0.9 and encoding.lower() == 'utf-8':
                return True
            else:
                return False

    except Exception as e:
        logging.error(f"Error checking if {filepath} is a text file: {e}")
        return False

async def is_png_corrupted(filepath):
    """Checks if a PNG file is corrupted."""
    try:
        Image.open(filepath).verify()
        return False
    except Exception as e:
        logging.error(f"Error checking if {filepath} is a corrupted PNG file: {e}")
        return True

async def is_jpg_corrupted(filepath):
    """Checks if a JPG file is corrupted."""
    try:
        with open(filepath, 'rb') as f:
            data = f.read()
            offset = data.find(b'\xff\xd9') + 2
            Image.frombytes('RGB', (1, 1), data[:offset])
        return False
    except Exception as e:
        logging.error(f"Error checking if {filepath} is a corrupted JPG file: {e}")
        return True

async def is_pdf_corrupted(filepath):
    """Checks if a PDF file is corrupted."""
    try:
        fitz.open(filepath)
        return False
    except Exception as e:
        logging.error(f"Error checking if {filepath} is a corrupted PDF file: {e}")
        return True

async def is_docx_corrupted(filepath):
    """Checks if a DOCX file is corrupted."""
    try:
        docx.Document(filepath)
        return False
    except Exception as e:
        logging.error(f"Error checking if {filepath} is a corrupted DOCX file: {e}")
        return True

async def process_file(filepath, mismatched_files, mismatched_folder, non_text_folder, allowed_extensions):
    """Processes a single file asynchronously."""
    try:
        print(f"Processing file: {filepath}")  # Add this line for debugging
        _, file_extension = os.path.splitext(filepath)
        print(f"File extension: {file_extension}")  # Add this line for debugging

        if file_extension.lower() in allowed_extensions:
            # Text file handling
            if file_extension.lower() == '.txt':
                is_text = await is_text_file(filepath)
                if not is_text:
                    async with lock:
                        destination_path = os.path.join(mismatched_folder, os.path.basename(filepath))
                        if not os.path.exists(destination_path):
                            shutil.move(filepath, destination_path)
                            mismatched_files.append(destination_path)
                        else:
                            print(f"File '{os.path.basename(filepath)}' already exists in destination.")
                else:
                    print(f"Text file '{os.path.basename(filepath)}' detected. No action needed.")

            # Non-text file handling
            else:
                # Check if the non-text file is corrupted
                is_corrupted = False
                if file_extension.lower() == '.png':
                    is_corrupted = await is_png_corrupted(filepath)
                elif file_extension.lower() == '.jpg':
                    is_corrupted = await is_jpg_corrupted(filepath)
                elif file_extension.lower() == '.pdf':
                    is_corrupted = await is_pdf_corrupted(filepath)
                elif file_extension.lower() == '.docx':
                    is_corrupted = await is_docx_corrupted(filepath)

                # Move corrupted non-text files to the mismatched folder
                if is_corrupted:
                    async with lock:
                        destination_path = os.path.join(mismatched_folder, os.path.basename(filepath))
                        if not os.path.exists(destination_path):
                            shutil.move(filepath, destination_path)
                            mismatched_files.append(destination_path)
                        else:
                            print(f"File '{os.path.basename(filepath)}' already exists in destination.")
                else:
                    print(f"Non-text file '{os.path.basename(filepath)}' is not corrupted. Keeping in testing area.")

    except Exception as e:
        print(f"Error processing {filepath}: {e}")

async def main():
    """Entry point for asynchronous file processing."""
    root_directory = os.getcwd()  # Get the directory where the script is being executed
    mismatched_files = []
    mismatched_folder = os.path.join(os.path.expanduser("~"), "Desktop", "Mismatched Files")
    non_text_folder = os.path.join(os.path.expanduser("~"), "Desktop", "Non-Text Files")
    os.makedirs(mismatched_folder, exist_ok=True)
    os.makedirs(non_text_folder, exist_ok=True)

    text_extensions = ['.txt']
    non_text_extensions = ['.png', '.jpg', '.pdf', '.docx']  # Include non-text extensions
    allowed_extensions = text_extensions + non_text_extensions

    total_files = sum(len(files) for _, _, files in os.walk(root_directory))
    with tqdm(total=total_files, desc="Scanning Directory") as pbar:
        tasks = [
            asyncio.create_task(process_file(filepath, mismatched_files, mismatched_folder, non_text_folder, allowed_extensions))
            for root, dirs, files in os.walk(root_directory)
            for file in files
            for filepath in [os.path.join(root, file)]
        ]

        await asyncio.gather(*tasks)

    if not mismatched_files:
        print("No mismatched files found.")
    else:
        print(f"Mismatched files moved to: {mismatched_folder}")

# Run the main function
if __name__ == "__main__":
    logging.basicConfig(filename='error_log.txt', level=logging.ERROR)
    asyncio.run(main())

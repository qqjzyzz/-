import os
import zipfile
import shutil
import tempfile
import logging # Import the logging module

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

def extract_and_flatten_folder(source_folder):
    """
    Extracts all files from a source folder, including files within zip archives,
    and moves them to the root of the source folder. Empty subdirectories
    and original zip files are removed.

    Args:
        source_folder (str): The path to the folder to process.
    """
    if not os.path.isdir(source_folder):
        logging.error(f"Source folder \'{source_folder}\' does not exist or is not a directory.")
        return

    logging.info(f"Processing folder: {source_folder}")

    # Phase 1: Iteratively unzip all archives and extract their contents to the root
    zips_found_in_iteration = True
    while zips_found_in_iteration:
        zips_found_in_iteration = False
        zip_files_in_this_pass = []

        # Find all zip files in the current state of the source_folder
        for root, _, files in os.walk(source_folder):
            for file in files:
                if file.endswith('.zip'):
                    zip_files_in_this_pass.append(os.path.join(root, file))

        if zip_files_in_this_pass:
            zips_found_in_iteration = True
            for zip_file_path in zip_files_in_this_pass:
                temp_extract_dir = None
                try:
                    logging.info(f"  Unzipping: {zip_file_path}")
                    
                    # Create a temporary directory for extraction within the source_folder
                    temp_extract_dir = tempfile.mkdtemp(dir=source_folder)
                    logging.info(f"    Created temporary extraction directory: {temp_extract_dir}")
                    
                    with zipfile.ZipFile(zip_file_path, 'r') as zip_ref:
                        zip_ref.extractall(temp_extract_dir)
                        logging.info(f"    Extracted contents to temporary location: {temp_extract_dir}")
                    
                    # Now, move all files from the temporary extraction directory to the source_folder root
                    for root_temp, _, files_temp in os.walk(temp_extract_dir):
                        for file_temp in files_temp:
                            original_file_path = os.path.join(root_temp, file_temp)
                            target_file_name = os.path.basename(original_file_path)
                            target_path = os.path.join(source_folder, target_file_name)

                            # Handle filename conflicts by renaming
                            if os.path.exists(target_path):
                                base, ext = os.path.splitext(target_file_name)
                                counter = 1
                                while os.path.exists(os.path.join(source_folder, f"{base}_{counter}{ext}")):
                                    counter += 1
                                target_path = os.path.join(source_folder, f"{base}_{counter}{ext}")
                                logging.warning(f"    Filename conflict: \'{target_file_name}\' exists. Renamed to \'{os.path.basename(target_path)}\'")

                            try:
                                shutil.move(original_file_path, target_path)
                                logging.info(f"    Moved extracted file: {original_file_path} -> {target_path}")
                            except shutil.Error as e:
                                logging.error(f"    Error moving extracted file \'{original_file_path}\' to \'{target_path}\': {e}")
                    
                    # Clean up the temporary extraction directory
                    if os.path.exists(temp_extract_dir):
                        shutil.rmtree(temp_extract_dir)
                        logging.info(f"    Removed temporary extraction directory: {temp_extract_dir}")

                    # Delete the original zip file
                    os.remove(zip_file_path)
                    logging.info(f"  Removed zip file: {zip_file_path}")

                except zipfile.BadZipFile:
                    logging.warning(f"  \'{zip_file_path}\' is not a valid zip file. Skipping.")
                except Exception as e:
                    logging.error(f"  Error processing zip \'{zip_file_path}\': {e}")
                    if temp_extract_dir and os.path.exists(temp_extract_dir):
                        shutil.rmtree(temp_extract_dir)


    # Phase 2: Move any remaining files from subdirectories to the root folder
    logging.info("\nMoving remaining files to root folder...")
    for root, _, files in os.walk(source_folder):
        if root == source_folder:
            continue
        for file in files:
            file_path = os.path.join(root, file)
            target_path = os.path.join(source_folder, file)

            # Handle potential filename conflicts by renaming
            if os.path.exists(target_path):
                base, ext = os.path.splitext(file)
                counter = 1
                while os.path.exists(os.path.join(source_folder, f"{base}_{counter}{ext}")):
                    counter += 1
                target_path = os.path.join(source_folder, f"{base}_{counter}{ext}")
                logging.warning(f"  Filename conflict: \'{file}\' exists. Renamed to \'{os.path.basename(target_path)}\'")

            try:
                shutil.move(file_path, target_path)
                logging.info(f"  Moved file: {file_path} -> {target_path}")
            except shutil.Error as e:
                logging.error(f"  Error moving file \'{file_path}\' to \'{target_path}\': {e}")

    # Phase 3: Clean up empty directories
    logging.info("\nCleaning up empty directories...")
    for root, dirs, _ in os.walk(source_folder, topdown=False):
        for dir_name in dirs:
            dir_path = os.path.join(root, dir_name)
            if not os.listdir(dir_path):
                try:
                    os.rmdir(dir_path)
                    logging.info(f"  Removed empty directory: {dir_path}")
                except OSError as e:
                    logging.error(f"  Error removing directory \'{dir_path}\': {e}")

    logging.info(f"\nFinished processing folder: {source_folder}")

if __name__ == "__main__":
    folder_path = input("请输入您要处理的文件夹路径： ")
    extract_and_flatten_folder(folder_path) 

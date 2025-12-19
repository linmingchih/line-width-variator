import zipfile
import os
import shutil

def package_app():
    # Define the output directory and filename
    dist_dir = "dist"
    zip_filename = "line-width-variator.zip"
    zip_path = os.path.join(dist_dir, zip_filename)

    # Create dist directory if it doesn't exist
    if not os.path.exists(dist_dir):
        os.makedirs(dist_dir)

    # Files and directories to include
    include_files = [
        "app.py",
        "run.bat",
        "pyproject.toml",
        "uv.lock",
        ".python-version",
        "README.md",
        "README_zh-TW.md",
    ]

    include_dirs = {
        "backend": "backend",
        "frontend/dist": "frontend/dist"
    }

    print(f"Creating {zip_path}...")

    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        # Add individual files
        for file in include_files:
            if os.path.exists(file):
                print(f"Adding {file}")
                zipf.write(file, file)
            else:
                print(f"Warning: {file} not found!")

        # Add directories
        for src_dir, dest_dir in include_dirs.items():
            if os.path.exists(src_dir):
                print(f"Adding directory {src_dir} -> {dest_dir}")
                for root, dirs, files in os.walk(src_dir):
                    # Exclude __pycache__
                    if "__pycache__" in dirs:
                        dirs.remove("__pycache__")
                    
                    for file in files:
                        # Ignore .DS_Store or other junk if needed
                        if file == ".DS_Store":
                            continue
                            
                        file_path = os.path.join(root, file)
                        # Calculate relative path for zip
                        # We want backend/foo.py -> backend/foo.py
                        # frontend/dist/index.html -> frontend/dist/index.html
                        # So simply writing with arcname=file_path works if we run from root.
                        
                        zipf.write(file_path, file_path)
            else:
                print(f"Warning: Directory {src_dir} not found!")

    print("Packaging complete.")

if __name__ == "__main__":
    package_app()

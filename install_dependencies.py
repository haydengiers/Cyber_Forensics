import subprocess

# List of dependencies to install
dependencies = [
    "tqdm",
    "chardet",
    "Pillow",
    "PyMuPDF",
    "python-docx"
]

def install_dependencies():
    for dependency in dependencies:
        try:
            # Use subprocess to run pip install command
            subprocess.check_call(["pip3", "install", dependency])
            print(f"Successfully installed {dependency}")
        except subprocess.CalledProcessError as e:
            print(f"Error installing {dependency}: {e}")
            continue

if __name__ == "__main__":
    install_dependencies()

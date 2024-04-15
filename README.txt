Forensics Scan Application

Overview:
The Forensics Scan Application is a tool designed to automate the verification of file integrity in cyber forensics investigations. It provides functionality to analyze both text and non-text files commonly encountered during investigations, ensuring their integrity for admissibility in legal proceedings.

Installation:
Before running the application, ensure that you have Python installed on your system. Additionally, it's recommended to install the required dependencies using the provided install_dependencies.py script. Navigate to the directory containing the script and run it using the following command:
python install_dependencies.py

Usage:
Once the dependencies are installed, you can execute the ForensicsScan.py script to run the application. This script scans the current directory and its subdirectories for files, performs integrity checks, and automatically moves corrupted files to a designated folder for further analysis.

To run the application, use the following command:
python ForensicsScan.py

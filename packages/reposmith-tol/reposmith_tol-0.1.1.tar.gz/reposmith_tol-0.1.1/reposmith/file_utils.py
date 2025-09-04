import os

def create_requirements_file(path):
    print("\n[3] Checking requirements.txt")
    if not os.path.exists(path):
        print("Creating empty requirements.txt...")
        os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            f.write("# Add your dependencies here\n")
        print("requirements.txt created.")
    else:
        print("requirements.txt already exists.")

def create_app_file(app_file_path):
    print("\n[7] Checking app.py")
    if not os.path.exists(app_file_path):
        print(f"Creating {app_file_path} with a welcome message...")
        os.makedirs(os.path.dirname(app_file_path) or ".", exist_ok=True)
        welcome_code = 'print("Welcome! This is your app.py file.")\nprint("You can now start writing your application code here.")\n'
        with open(app_file_path, "w", encoding="utf-8") as f:
            f.write(welcome_code)
        print(f"{app_file_path} created.")
    else:
        print(f"{app_file_path} already exists.")

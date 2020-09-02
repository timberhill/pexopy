import os

def ensurePathExists(folder):
    if not os.path.exists(folder):
        os.makedirs(folder)

module_path = os.path.dirname(os.path.abspath(__file__))
temp_storage = os.path.relpath(os.path.join(module_path, "pexopy-temp"), ".") # temporary file storage path
ensurePathExists(temp_storage)

if __name__ == "__main__":
    raise Exception("This is a settings file, no point in running it.")

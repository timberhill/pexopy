import os

def _ensurePathExists(folder):
    if not os.path.exists(folder):
        os.makedirs(folder)

module_path = os.path.dirname(os.path.abspath(__file__))
temp_storage = os.path.normpath(os.path.join(module_path, "../tmp")) # temporary file storage path

_ensurePathExists(temp_storage)

if __name__ == "__main__":
    raise Exception("This is a settings file, no point in running it.")

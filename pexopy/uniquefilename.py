import os
import hashlib
from .settings import temp_storage

class UniqueFile(str):
   """
   Generates an MD5 hash from the `contents` (<str>) and returns a string in a format f'{prepend}{md5}{append}'
   """
   def __new__(cls, contents, prepend="", append="", folder=None, *args, **kwargs):
      if folder is None:
         folder = temp_storage

      md5 = hashlib.md5(contents.encode("utf-8")).hexdigest()
      name = "{}{}{}".format(prepend, md5, append)
      path = os.path.join(folder, name)

      with open(path, "w") as f:
            f.write(contents)
      
      return str.__new__(cls, path)

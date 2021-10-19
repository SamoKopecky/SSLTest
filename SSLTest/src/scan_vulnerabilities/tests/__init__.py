import os
import importlib

# Import these classes to the sys.modules list so that they can be extracted later in TestRunner class
_, _, files = next(os.walk("./src/scan_vulnerabilities/tests"))
[importlib.import_module(__package__ + "." + file[:-3]) for file in files if file != "__init__.py"]

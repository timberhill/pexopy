import os
import numbers
from collections.abc import Iterable

from .uniquefilename import UniqueFile
from .parfile import ParFile
from .settings import temp_storage


class PexoArguments(object):
    """
    Pexo arguments handler.
    """
    def __init__(self, args_dict):
        self._list = {}
        for key in args_dict:
            argument = Argument(key, args_dict[key])
            self._list[argument.key] = argument
            self._list[argument.shortkey] = argument
        
        self._ensure_output_specified()


    def _ensure_output_specified(self):
        if "o" not in self._list and "out" not in self._list:
            append = ".txt"
            if self._list["mode"].value == "fit":
                append = ".Robj"

            filename = UniqueFile(str(self), append=append, create=False)
            argument = Argument("out", filename)
            self._list[argument.key] = argument
            self._list[argument.shortkey] = argument


    def __getattr__(self, property_name):
        if property_name not in self._list:
            return None
        return self._list[property_name].value


    def  __str__(self):
        output_string = ""
        for key in self._list:
            if len(key) == 1: # only use the short representations
                output_string += " -{} {}".format(self._list[key].shortkey, self._list[key].value)

        return output_string


    def clear_temp(self, nuke=False):
        """
        Removes temporary file created by the argument handlers (e.g. timing files that are generated when an array is provided as a --tim argument).

        nuke, bool: removes ALL files in the temp folder, whether creted by current instnce or not. Use with caution when running multiple instnces in parallel.
        """
        if nuke:
            tempfiles = [
                f for f in os.listdir(temp_storage)
                if os.path.isfile(os.path.join(temp_storage, f)) and f.startswith(Argument._temp_file_prefix)
            ]
        else:
            tempfiles = []
            args = [self._list[key] for key in self._list]
            for key in self._list:
                for tempfile in self._list[key]._temp_files:
                    tempfiles.append(tempfile)

        for f in tempfiles:
            path = os.path.join(temp_storage, f)
            if os.path.isfile(path):
                os.remove(path)


class Argument(object):
    """
    Pexo individual argument handler, normalizes the names and values to make them appropriate as command-line arguments.
    """
    _temp_file_prefix = "pexopy-temp-"

    def __init__(self, key, value):
        self._init_values = (key, value)
        self._normalised_value = None
        self._handler = self._argument_handler(key)
        self._temp_files = []


    @property
    def shortkey(self):
        return self._handler["variations"][0]

    @property
    def key(self):
        return self._handler["variations"][1]

    @property
    def value(self):
        if self._normalised_value is None:
            self._normalised_value = self._handler["handler"](self._init_values[1])
        return self._normalised_value


    # LIST OF ARGUMENTS

    def _argument_handler(self, key):
        handlers = [
            dict(variations=["m", "mode"],      handler=self._normalise_argument_mode),
            dict(variations=["c", "component"], handler=self._normalise_argument_component),
            dict(variations=["i", "ins"],       handler=self._normalise_argument_ins),
            dict(variations=["P", "par"],       handler=self._normalise_argument_par),
            dict(variations=["N", "Niter"],     handler=self._normalise_argument_Niter),
            dict(variations=["C", "Companion"], handler=self._normalise_argument_companion),
            dict(variations=["g", "geometry"],  handler=self._normalise_argument_geometry),
            dict(variations=["n", "ncore"],     handler=self._normalise_argument_ncore),
            dict(variations=["t", "time"],      handler=self._normalise_argument_time),
            dict(variations=["p", "primary"],   handler=self._normalise_argument_primary),
            dict(variations=["s", "secondary"], handler=self._normalise_argument_secondary),
            dict(variations=["M", "mass"],      handler=self._normalise_argument_mass),
            dict(variations=["d", "data"],      handler=self._normalise_argument_data),
            dict(variations=["v", "var"],       handler=self._normalise_argument_var),
            dict(variations=["o", "out"],       handler=self._normalise_argument_out),
            dict(variations=["f", "figure"],    handler=self._normalise_argument_figure),
            dict(variations=["V", "verbose"],   handler=self._normalise_argument_verbose)
        ]

        for handler in handlers:
            if key in handler["variations"]:
                return handler

        raise KeyError("Unknown argument: {}".format(key))


    # VALIDATION helpers
    
    def _assert_type(self, value, *types):
        if not isinstance(value, types):
            raise ValueError(self._value_error_message(value))

    def _assert_positive(self, value, zero_allowed=False):
        if value < 0 or (zero_allowed==False and value == 0):
            raise ValueError(self._value_error_message(value))

    def _assert_in_set(self, value, *allowed):
        if value not in allowed:
            raise ValueError(self._value_error_message(value))

    def _value_error_message(self, value):
        return "Incorrect value for the '{}' argument: {}".format(self.key, value)


    # NORMALISE functions

    def _normalise_argument_mode(self, value):
        self._assert_type(value, str)
        self._assert_in_set(value.lower(), "emulate", "fit")
        return value.lower()


    def _normalise_argument_ins(self, value):
        self._assert_type(value, str)
        return value


    def _normalise_argument_Niter(self, value):
        self._assert_type(value, int, float)
        self._assert_positive(value)
        return int(value)


    def _normalise_argument_par(self, value):
        par = ParFile(value)
        if par.temporary: # file was generated from a dictionary
            self._temp_files.append(par.path)

        if os.path.isfile(par.path):
            return par.path
        else:
            raise FileNotFoundError("Path provided in the --data argument does not exist: {}".format(par.path))


    def _normalise_argument_geometry(self, value):
        self._assert_type(value, bool)
        return value


    def _normalise_argument_ncore(self, value):
        self._assert_type(value, int, float)
        self._assert_positive(value)
        return int(value)


    def _normalise_argument_component(self, value):
        self._assert_type(value, str)
        [self._assert_in_set(x, "t", "a", "r") for x in value.lower()]
        return value.upper()


    def _normalise_argument_time(self, value):
        self._assert_type(value, Iterable, str, tuple)

        if isinstance(value, str) and os.path.isfile(value):
            # this is a path to a timing file
            return value

        if isinstance(value, str) and value.replace(" ", "").isnumeric() and len(value.split(" ")) == 3:
            # this is a "from to step" format
            return f"\"{value}\""

        if isinstance(value, tuple) and len(value) == 3:
            # this is a (from, to, step) format
            return " ".join(value)

        if isinstance(value, Iterable):
            # must be a list of JDs -- create a file and return a path
            contents = ""
            for jd in value:
                if isinstance(jd, numbers.Number):
                    contents += "{}\n".format(jd)
                elif len(jd) == 2:
                    contents += "{} {}\n".format(jd[0], jd[1])
                else:
                    raise ValueError("`tim` argument should be a list of numbers, a list of tuples of numbers, or a path to a .tim file")

            path = UniqueFile(contents, prepend=Argument._temp_file_prefix, append=".tim")
            self._temp_files.append(path)

            return path


    def _normalise_argument_primary(self, value):
        self._assert_type(value, str)
        return value


    def _normalise_argument_secondary(self, value):
        self._assert_type(value, str)
        return value


    def _normalise_argument_mass(self, value):
        self._assert_type(value, int, float)
        self._assert_positive(value)
        return value


    def _normalise_argument_data(self, value):
        self._assert_type(value, str)
        if not os.path.isdir(value):
            raise NotADirectoryError("Path provided in the --data argument does not exist: {}".format(value))

        return value


    def _normalise_argument_companion(self, value):
        self._assert_type(value, int)
        self._assert_positive(value, zero_allowed=True)
        return value


    def _normalise_argument_var(self, value):
        self._assert_type(value, Iterable, str)

        ###########
        ### TODO : validate the actual values to be one of the output arguments in PEXO
        ###########

        if isinstance(value, str):
            return value

        [self._assert_type(x, str) for x in value]
        return value


    def _normalise_argument_out(self, value):
        self._assert_type(value, str)

        value = os.path.abspath(value)
        folder, filename = os.path.split(value)
        if not os.path.isdir(folder):
            raise FileNotFoundError("Path provided in the --out argument does not exist: {}".format(value))

        return value


    def _normalise_argument_figure(self, value):
        self._assert_type(value, bool)
        return value


    def _normalise_argument_verbose(self, value):
        self._assert_type(value, bool)
        return value

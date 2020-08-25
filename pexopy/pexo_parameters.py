from collections.abc import Iterable


class PexoParameters(object):
    """
    Pexo parameters handler.
    """
    def __init__(self, params_dict):
        self._list = {}
        for p in params_dict:
            self._list[pp.key] = PexoParameter(p, params_dict[p])

    def __getattr__(self, property_name):
        if property_name not in self._list:
            return None
        return self._list[property_name].value

    def  __str__(self):
        output_string = ""
        for key in self._list:
            if len(key) == 1: # only use the short representations
                output_string += "-{} {}".format(self._list[key].shortkey, self._list[key].value)

    @staticmethod
    def clear_cache():
        raise NotImplementedError("PexoParameter.clear_cache() is not yet implemented.")
        # from .settings import out_storage, par_storage, tim_storage
        # count = 0
        # for folder in [par_storage, tim_storage, out_storage]:
        #     filenames = os.listdir(folder)
        #     for filename in filenames:
        #         os.remove(os.path.join(folder, filename))
        #         count += 1
        # if verbose:
        #     self._print("{} files removed.".format(count), verbose=verbose)



class PexoParameter(object):
    """
    Pexo individual parameter handler, normalizes the names and values to make them appropriate as command-line arguments.
    """
    def __init__(self, key, value):
        self._init_values = (key, value)
        self._normalised_value = None
        self._handler = self._parameter_handler(key)


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


    def _parameter_handler(self, key):
        handlers = [
            dict(variations=["m", "mode"],      handler=self._normalise_parameter_mode),
            dict(variations=["i", "ins"],       handler=self._normalise_parameter_ins),
            dict(variations=["N", "Niter"],     handler=self._normalise_parameter_Niter),
            dict(variations=["P", "Planet"],    handler=self._normalise_parameter_Planet),
            dict(variations=["O", "orbit"],     handler=self._normalise_parameter_orbit),
            dict(variations=["g", "geometry"],  handler=self._normalise_parameter_geometry),
            dict(variations=["n", "ncore"],     handler=self._normalise_parameter_ncore),
            dict(variations=["c", "component"], handler=self._normalise_parameter_component),
            dict(variations=["t", "time"],      handler=self._normalise_parameter_time),
            dict(variations=["p", "primary"],   handler=self._normalise_parameter_primary),
            dict(variations=["s", "secondary"], handler=self._normalise_parameter_secondary),
            dict(variations=["M", "mass"],      handler=self._normalise_parameter_mass),
            dict(variations=["d", "data"],      handler=self._normalise_parameter_data),
            dict(variations=["C", "companion"], handler=self._normalise_parameter_companion),
            dict(variations=["v", "var"],       handler=self._normalise_parameter_var),
            dict(variations=["o", "out"],       handler=self._normalise_parameter_out),
            dict(variations=["f", "figure"],    handler=self._normalise_parameter_figure),
            dict(variations=["V", "verbose"],   handler=self._normalise_parameter_verbose),
        ]

        for handler in handlers:
            if key in handler["variations"]:
                return handler

        raise KeyError("Unknown parameter: {}".format(key))


    # ERROR helpers
    
    def _assert_type(self, value, *types):
        if not isinstance(value, types):
            raise ValueError(self._value_error_message(value))
    
    def _assert_positive(self, value, zero_allowed=False):
        if value < 0 or (zero_allowed==False and value == 0):
            raise ValueError(self._value_error_message(value))
    
    def _assert_in_set(self, value, *allowed):
        if value not in allowed:
            raise ValueError(self._value_error_message(value))

    def _value_error_message(self, key, value):
        return "Incorrect value for the '{}' parameter: {}".format(self.key, value)


    # NORMALISE functions

    def _normalise_parameter_mode(self, value):
        self._assert_type(value, str)
        self._assert_in_set(value.lower(), "emulate", "fit")
        return value.lower()


    def _normalise_parameter_ins(self, value):
        self._assert_type(value, str)
        return value


    def _normalise_parameter_Niter(self, value):
        self._assert_type(value, int, float)
        self._assert_positive(value)
        return int(value)


    def _normalise_parameter_Planet(self, value):
        self._assert_type(value, int, float)
        self._assert_positive(value)
        return int(value)


    def _normalise_parameter_orbit(self, value):
        ###########
        ### TODO : clarify this argument
        ###########
        raise NotImplementedError


    def _normalise_parameter_geometry(self, value):
        self._assert_type(value, bool)
        return value


    def _normalise_parameter_ncore(self, value):
        self._assert_type(value, int, float)
        self._assert_positive(value)
        return int(value)


    def _normalise_parameter_component(self, value):
        self._assert_type(value, str)
        [self._assert_in_set(x, "t", "a", "r") for x in value.lower()]
        return value.upper()


    def _normalise_parameter_time(self, value):
        self._assert_type(value, str)
        ###########
        ### TODO : handle timing file path or "from to step" format
        ###########
        return []


    def _normalise_parameter_primary(self, value):
        self._assert_type(value, str)
        return value


    def _normalise_parameter_secondary(self, value):
        self._assert_type(value, str)
        return value


    def _normalise_parameter_mass(self, value):
        self._assert_type(value, int, float)
        self._assert_positive(value)
        return value


    def _normalise_parameter_data(self, value):
        ###########
        ### TODO : validate actual path to data folder
        ###########
        self._assert_type(value, str)
        return value


    def _normalise_parameter_companion(self, value):
        ###########
        ### TODO : validate actual path to companion data folder
        ###########
        self._assert_type(value, str)
        return value


    def _normalise_parameter_var(self, value):
        self._assert_type(value, Iterable)
        [self._assert_type(x, str) for x in value]
        ###########
        ### TODO : validate the actual values to be one of the output parameters in PEXO
        ###########
        return value


    def _normalise_parameter_out(self, value):
        ###########
        ### TODO : validate actual output path
        ###########
        self._assert_type(value, str)
        return value


    def _normalise_parameter_figure(self, value):
        self._assert_type(value, bool)
        return value


    def _normalise_parameter_verbose(self, value):
        self._assert_type(value, bool)
        return value

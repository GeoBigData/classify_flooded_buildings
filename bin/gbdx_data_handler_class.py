import os
import json
import glob
import rasterio
import fiona
from fiona.crs import from_epsg


class GBDXDataHandler(object):
    def __init__(self, input_dir='/mnt/work/input', output_dir='/mnt/work/output'):
        self._input_dir = input_dir
        self._output_dir = output_dir
        self._supported_vector_extensions = ('.shp', '.geojson', '.json')
        self._supported_raster_extensions = ('.tif',)

        # create output directory
        if os.path.exists(output_dir) is False:
            os.makedirs(output_dir)

    def _get_input_filepath(self, input_port, extensions, optional):
        # define the full path to the input directory
        port_path = os.path.join(self._input_dir, input_port)

        # establish if it exists (if it's optional and not specified in the workflow, this will be false)
        path_exists = os.path.exists(port_path)

        # # get the first vector or raster filename from input port
        # if path_exists:
        #     try:
        #         filepath = next(
        #             os.path.join(port_path, filename)
        #             for filename in os.listdir(port_path)
        #             if os.path.splitext(filename)[1].lower() in extensions
        #             )
        #     except StopIteration as err:
        #         raise StopIteration("Could not find file with specified extension.")

        # # get the first vector or raster filename from input port
        if path_exists:
            filenames = glob.glob1(port_path, '*.shp')

            filepaths = []
            for filename in filenames:
                filepath = os.path.join(port_path, filename)
                filepaths.append(filepath)

            # this needs to balk
            if not filenames:
                print("List is empty, did not find files of specified type.")

        # raise an error if it's a required port and no files were found
        elif not path_exists and not optional:
            err = "Input directory not found"
            raise IOError(err)

        # input port is optional, return None
        else:
            # filepath = None
            filepaths = None

        # return filepath
        return filepaths

    def get_vector_filepath(self, input_port, optional=False):
        vector_filepath = self._get_input_filepath(input_port=input_port,
                                                   extensions=self._supported_vector_extensions,
                                                   optional=optional)

        return vector_filepath

    def get_raster_filepath(self, input_port, optional=False):
        raster_filepath = self._get_input_filepath(input_port=input_port,
                                                   extensions=self._supported_raster_extensions,
                                                   optional=optional)

        return raster_filepath

    def return_ports_json(self):
        ports_path = os.path.join(self._input_dir, 'ports.json')

        path_exists = os.path.exists(ports_path)

        if path_exists:
            with open(ports_path) as ports:
                str_inputs = json.load(ports)

        else:
            err = "ports.json not found"
            raise IOError(err)

        return str_inputs

    def create_output_raster(self, output_port, filename, raster_src):
        port_dir = os.path.join(self._output_dir, output_port)
        if os.path.exists(port_dir) is False:
            os.makedirs(port_dir)

        outfile = os.path.join(port_dir, filename)

        # check if file already exists, and if so remove it (this is just necessary for local testing)
        if os.path.exists(outfile):
            os.unlink(outfile)

        new_profile = raster_src.profile

        out_raster = rasterio.open(outfile,
                                   'w+',
                                   **new_profile)

        return out_raster

    def create_output_vector(self, output_port, filename, driver, epsg_code=4326):
        port_dir = os.path.join(self._output_dir, output_port)
        if os.path.exists(port_dir) is False:
            os.makedirs(port_dir)

        outfile = os.path.join(port_dir, filename)

        # check if file already exists, and if so remove it (this is just necessary for local testing)
        if os.path.exists(outfile):
            os.unlink(outfile)

        schema = {'geometry': 'Polygon',
                  'properties': {'id': 'int'}}

        # use fiona to write out the geometries to the inferred flooding output geojson
        out_vector = fiona.open(outfile,
                                'w',
                                driver=driver,
                                schema=schema,
                                crs=from_epsg(epsg_code)
                                )

        return out_vector

    @staticmethod
    def convert_dtype(str_input, dtype):
        if dtype is 'str':
            return str_input
        elif dtype is 'int':
            valid = int(str_input)
        elif dtype is 'float':
            valid = float(str_input)
        elif dtype is 'bool':
            valid = str_input == "true"
        else:
            # TODO: return a message to status json
            err = "Please select a valid dtype: 'str', 'int', 'float', 'bool'"
            raise ValueError(err)

        return valid

    @staticmethod
    def validate_string_input(str_input, valid_str_list):
        if str_input in valid_str_list:
            return str_input
        else:
            err = "Invalid input for input string port '{string_input}'. Must be one of {validation_list}".format(
                string_input=str_input,
                validation_list=valid_str_list)
            raise ValueError(err)

    @staticmethod
    def validate_int_input(int_input, valid_range_list):
        if valid_range_list[0] <= int_input <= valid_range_list[1]:
            return int_input
        else:
            err = "Invalid input for input string port {input}. Must be an integer within the range {range}".format(
                input=int_input,
                range=valid_range_list
            )
            raise ValueError(err)

    @property
    def input_dir(self):
        return self._input_dir

    @input_dir.setter
    def input_dir(self, value):
        self._input_dir = value

    @property
    def output_dir(self):
        return self._output_dir

    @output_dir.setter
    def output_dir(self, value):
        self._output_dir = value

    @property
    def supported_vector_extensions(self):
        return self._supported_vector_extensions

    @supported_vector_extensions.setter
    def supported_vector_extensions(self, value):
        self._supported_vector_extensions = value

    @property
    def supported_raster_extensions(self):
        return self._supported_raster_extensions

    @supported_raster_extensions.setter
    def supported_raster_extensions(self, value):
        self._supported_raster_extensions = value




#!/usr/bin/env python

import json
import jsonschema
import os
import time
import unittest
from gladier.tools.dials.funcx_functions import validate_json, funcx_create_phil, funcx_stills_process, funcx_plot_ssx, funcx_pilot
from jsonschema.exceptions import ValidationError


class DialsTests(unittest.TestCase):

    @classmethod
    def setUpClass(self):
        testdir = os.path.dirname(os.path.realpath(__file__))
        with open(os.path.join(testdir, 'funcx_functions.json')) as f:
            self.json = json.load(f)
        with open(os.path.join(testdir, 'schema.json')) as f:
            self.schema = json.load(f)


    def test_valid_json(self):
        validate_json(self.json, self.schema)


    def test_invalid_json(self):
        with self.assertRaises(jsonschema.exceptions.ValidationError):
            validate_json({}, self.schema)


    def test_funcx_create_phil(self):
        funcx_create_phil(self.json)


    def test_funcx_stills_process(self):
        funcx_stills_process(self.json)


    def test_funcx_plot_ssx(self):
        fname = funcx_plot_ssx(self.json)
        plot_path = os.path.join(os.path.dirname(self.json["input_files"]), fname)
        assert(os.path.exists(plot_path))
        assert(time.time() - os.path.getmtime(plot_path) < 60)


    def test_funcx_pilot(self):
        funcx_pilot(self.json)


if __name__ == '__main__':
    unittest.main()

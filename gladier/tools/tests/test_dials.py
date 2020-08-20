#!/usr/bin/env python

import json
import os
import time
import unittest
from gladier.tools import dials


class DialsTests(unittest.TestCase):

    @classmethod
    def setUpClass(self):
        testdir = os.path.dirname(os.path.realpath(__file__))
        with open(os.path.join(testdir, 'dials.json')) as f:
            self.json = json.load(f)
        with open(os.path.join(testdir, 'schema.json')) as f:
            self.schema = json.load(f)


    def test_valid_json(self):
        dials.validate_json(self.json, self.schema)


    def test_invalid_json(self):
        dials.validate_json({}, self.schema)
        assertRaises(Exception)


    def test_funcx_create_phil(self):
        dials.funcx_create_phil(self.json)


    def test_funcx_stills_process(self):
        dials.funcx_stills_process(self.json)


    def test_funcx_plot_ssx(self):
        fname = dials.funcx_plot_ssx(self.json)
        plot_path = os.path.join(os.path.dirname(self.json["input_files"]), fname)
        assert(os.path.exists(plot_path))
        assert(time.time() - os.path.getmtime(plot_path) < 60)


    def test_funcx_pilot(self):
        dials.funcx_pilot(self.json)


if __name__ == '__main__':
    unittest.main()

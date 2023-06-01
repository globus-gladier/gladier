from __future__ import annotations

import functools

from gladier import float_range_iterator, templated_flow_input_generator


def test_templated_flow_input_generator():
    template = {}
    value_json_path = "$.the_value"
    generator = functools.partial(range, 3)
    generated_vals = templated_flow_input_generator(
        generator(), template, value_json_path
    )

    expected_vals = [{"the_value": val} for val in generator()]

    for gen, expected in zip(generated_vals, expected_vals):
        assert gen == expected


def test_float_range_iterator():
    template = {}
    value_json_path = "$.the_value"
    start, stop, step = 0, 1, 0.1
    generated_vals = float_range_iterator(start, stop, step, template, value_json_path)

    vals_list = list(generated_vals)
    assert len(vals_list) == int((stop - start) / step)

from pypgfplots._options import dict_to_pgf, kwargs_to_pgf, merge_opts


def test_kwargs_underscore_to_space():
    assert kwargs_to_pgf({"axis_lines": "center"}) == "axis lines=center"


def test_kwargs_bool_true():
    assert kwargs_to_pgf({"grid": True}) == "grid"


def test_kwargs_bool_false_omitted():
    assert kwargs_to_pgf({"grid": False}) == ""


def test_kwargs_multiple():
    result = kwargs_to_pgf({"color": "red", "domain": "-2:2"})
    assert result == "color=red,domain=-2:2"


def test_dict_no_transformation():
    assert dict_to_pgf({"/tikz/color": "red"}) == "/tikz/color=red"


def test_dict_bool_true():
    assert dict_to_pgf({"mark": True}) == "mark"


def test_merge_opts_skips_empty():
    assert merge_opts("a=1", "", "b=2") == "a=1,b=2"


def test_merge_opts_all_empty():
    assert merge_opts("", "") == ""

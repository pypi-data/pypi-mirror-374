from src.easy_config_hub import Setting
import pytest


def test_init():
    s = Setting[int](69)


def test_type_init_error():
    with pytest.raises(TypeError):
        s = Setting(69)


def test_strict_type():
        s = Setting[int](69, strongly_typed=True)


def test_strict_type_error():
    with pytest.raises(TypeError):
        s = Setting[str](69, strongly_typed=True)
        

def test_parse_type():
    s = Setting[str](69, strongly_typed=False)


def test_parse_type_error():
    with pytest.raises(TypeError):
        s = Setting[int]("69 sixty nine", strongly_typed=False)


def test_union_strict_type():
    s = Setting[int | float](69.69)


def test_union_strict_type_error():
    with pytest.raises(TypeError):
        s = Setting[int | float]("69 sixty nine")


def test_union_parse_type():
    s = Setting[int | float]("69", strongly_typed=False)
    assert s() == 69
    assert type(s()) is int


def test_union_parse_type_error():
    with pytest.raises(TypeError):
        s = Setting[int | float]("69 sixty nine", strongly_typed=False)


def test_union_parse_right_second_type():
    s = Setting[str | int](69, strongly_typed=False)
    assert type(s()) is int


def test_list_strict_type():
    s = Setting[list[str]](["sdkfj", "sdfjs"])


def test_list_strict_type_error():
    with pytest.raises(TypeError):
        s = Setting[list[str]](["sdkfj", "sdfjs", 69, "asdf"])


def test_list_parse_type():
    s = Setting[list[float]](["420", "69"], strongly_typed=False)
    assert s() == [420.0, 69.0]
    assert type(s()[0]) is float
    assert type(s()[1]) is float


def test_list_parse_type_error():
    with pytest.raises(TypeError):
        s = Setting[list[int]](["420", "69 sixty nine", "1"], strongly_typed=False)


def test_dict_strict_type():
    s = Setting[dict[str, int]]({"sdkfj": 69, "sdfjs": 420})


def test_dict_strict_type_error():
    with pytest.raises(TypeError):
        s = Setting[dict[str, int]]({"sdkfj": 420, 69: 96, "asdf": 23})

def test_dict_parse_type():
    s = Setting[dict[float, int]]({"420": "024", "69": "96"}, strongly_typed=False)
    assert s() == {420.0: 24, 69.0: 96}
    assert type(list(s().keys())[0]) is float
    assert type(list(s().values())[0]) is int
    assert type(list(s().keys())[1]) is float
    assert type(list(s().values())[1]) is int


def test_dict_parse_type_error():
    with pytest.raises(TypeError):
        s = Setting[dict[int, int]](
            {"420": "024", "69 sixty nine": "96", "1": 1}, strongly_typed=False
        )


def test_really_complex_union_strict_type():
    s = Setting[list[dict[str, list[int | str]]] | int | float](
        [{"lol": [69, "69"], "kek": [420]}, {"lol": [69, 69], "kek": ["420"]}]
    )


# def test_complex_parse_type_after_error():
#     try:
#         s = Setting[list[int]](['420', '69 sixty nine', '1'], strongly_typed=False, try_parse_after_failure=True)
#     except TypeError:
#         pass
#     finally:
#         assert s()[0] == 420
#         assert s()[1] == 2
#         assert s()[2] == 1

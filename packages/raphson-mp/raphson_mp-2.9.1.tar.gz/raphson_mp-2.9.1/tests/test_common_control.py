from raphson_mp.common.control import COMMMANDS


def test_unique_name():
    names: set[str] = set()
    for command in COMMMANDS:
        assert command.name not in names
        names.add(command.name)

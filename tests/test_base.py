import pytest

from interface.base import Interface


def test_interface_cannot_be_instantiated_directly():
    with pytest.raises(TypeError):
        Interface()


@pytest.mark.asyncio
async def test_subclass_implementing_run_can_be_instantiated_and_called():
    calls = []

    class ConcreteInterface(Interface):
        async def run(self, application):
            calls.append(application)

    instance = ConcreteInterface()
    await instance.run("fake_application")

    assert calls == ["fake_application"]


def test_subclass_missing_run_cannot_be_instantiated():
    class IncompleteInterface(Interface):
        pass

    with pytest.raises(TypeError):
        IncompleteInterface()
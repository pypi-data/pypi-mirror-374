"""Tests for `Diagram` class."""

from os import chdir

import pytest

from pyrbd import Diagram, Block
from pyrbd.diagram import TEX_PREAMBLE, TEX_END


@pytest.fixture(name="diagram")
def diagram_fixture() -> Diagram:
    """Diagram pytest fixture."""

    block = Block("block", "white")
    return Diagram("test_diagram", [block], "Fire")


def test_diagram_init(diagram: Diagram) -> None:
    """Test __init__ of `Diagram` class."""

    assert diagram.filename == "test_diagram"
    assert isinstance(diagram.head, Block)


def test_diagram_wo_hazard() -> None:
    """Test __init__ of `Diagram` class without `hazard` specified."""

    head = Block("block1", "white")
    blocks = [head, Block("block2", "blue"), Block("block3", "green")]
    diagram = Diagram("test_diagram", blocks)

    # When hazard is not specified, blocks[0] is set as head of diagram
    assert diagram.head is head
    assert len(diagram.blocks) == 2


def test_diagram_write(tmp_path, diagram: Diagram) -> None:
    """Test `Diagram` `write` method."""

    temp_dir = tmp_path / "test_diagram"
    temp_dir.mkdir()

    chdir(temp_dir)

    diagram.write()

    tmp_file = temp_dir / f"{diagram.filename}.tex"

    assert TEX_PREAMBLE in tmp_file.read_text()
    assert TEX_END in tmp_file.read_text()
    assert diagram.head.text in tmp_file.read_text()

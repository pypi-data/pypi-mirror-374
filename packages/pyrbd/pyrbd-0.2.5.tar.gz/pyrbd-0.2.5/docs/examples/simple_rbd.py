"""Simple RBD example."""

from os import path, chdir

from pyrbd import Block, Diagram

chdir(path.dirname(__file__))

start_block = Block("Start", "blue!30", parent=None)
parallel = 2 * Block("Parallel blocks", "gray", parent=start_block)
end_block = Block("End", "green!50", parent=parallel)

diagram = Diagram(
    "simple_RBD",
    blocks=[start_block, parallel, end_block],
)
diagram.write()
diagram.compile(["pdf", "svg"])

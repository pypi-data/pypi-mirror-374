"""Simple RBD example."""

from os import path, chdir

from pyrbd import Block, Group, Series, Diagram

chdir(path.dirname(__file__))

start_block = Block("Start", "blue!30", parent=None)
parallel = 2 * Block("Parallel blocks", "gray", parent=start_block)
block_1 = Block(r"Block 1", "yellow!50")
block_2 = Block(r"Block 2", "yellow!50")
block_3 = Block(r"Block 3", "yellow!50")
block_4 = Block(r"Block 4", "yellow!50")
group = Group(
    [block_1 + block_2, block_3 + block_4],
    parent=parallel,
    text="Group",
    color="yellow",
)
block_a = Block(r"Block A", "orange!50")
block_b = Block(r"Block B", "orange!50")
series = Series([block_a, block_b], "Series", "orange", parent=group)
end_block = Block("End", "green!50", parent=series)


diag = Diagram(
    "example_RBD",
    blocks=[start_block, parallel, group, series, end_block],
    hazard="Hazard",
)
diag.write()
diag.compile(["svg", "png"])

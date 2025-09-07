"""Simple RBD example.

Code comments:
1.  Here, a `Group` block is made by simply multiplying a `Block` instance by an integer
2.  To group different blocks vertically and set a title and color, use the `Group` class
3.  Adding `Block` instances creates a `Series` instance
4.  To group different blocks horizontally and set a title and color, use the `Series` class
5.  Custom color `myblue` used in first block is defined here

"""

from os import path, chdir

from pyrbd import Block, Group, Series, Diagram

chdir(path.dirname(__file__))

# Define all the blocks in the diagram
start_block = Block("Start", "myblue", parent=None)
parallel = 2 * Block("Parallel blocks", "gray", parent=start_block)  # (1)
block_1 = Block(r"Block 1", "yellow!50")
block_2 = Block(r"Block 2", "yellow!50")
block_3 = Block(r"Block 3", "yellow!50")
block_4 = Block(r"Block 4", "yellow!50")
group = Group(  # (2)
    [block_1 + block_2, block_3 + block_4],  # (3)
    parent=parallel,
    text="Group",
    color="yellow",
)
block_a = Block(r"Block A", "orange!50")
block_b = Block(r"Block B", "orange!50")
series = Series([block_a, block_b], "Series", "orange", parent=group)  # (4)
end_block = Block("End", "green!50", parent=series)

# Add blocks to Diagram class instance and compile diagram
diag = Diagram(
    "example_RBD",
    blocks=[start_block, parallel, group, series, end_block],
    hazard="Hazard",
    colors={"myblue": "8888ff"},  # (5)
)
diag.write()
diag.compile(["svg", "png"])

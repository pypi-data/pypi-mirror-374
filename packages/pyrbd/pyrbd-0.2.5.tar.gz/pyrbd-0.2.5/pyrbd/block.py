"""Module containing Block, Series and Group class definitions."""

from typing import Optional
from itertools import combinations
from copy import deepcopy


class Block:
    """Block entering a reliability block diagram.

    Parameters
    ----------
    text : str
        block text string
    color : str
        block color
    parent : Optional[Block]
        parent `Block` instance
    shift : tuple[float, float], optional
        additional position shift `(x, y)` relative to `parent` `Block` instance

    Attributes
    ----------
    tikz_options : str
        TikZ node formatting options


    Examples
    --------
    >>> block_1 = Block("Start", "green")
    >>> block_1.id
    '1'
    >>> block_2 = Block("End", "red", parent=block_1)
    >>> block_2.id
    '2'
    """

    tikz_options: str = ", ".join(
        [
            "anchor=west",
            "align=center",
            "fill={fill_color}",
            "draw=black",
            "minimum height=1cm",
            "rounded corners=0.3mm",
            "inner sep=4pt",
            "outer sep=0pt",
        ]
    )

    def __init__(
        self,
        text: str,
        color: str,
        parent: Optional["Block"] = None,
        shift: tuple[float, float] = (0.0, 0.0),
    ) -> None:
        self.text = text
        self.color = color
        self.parent = parent
        self.shift = shift
        self.id: str = str(int(self.parent.id) + 1) if self.parent is not None else "1"

    @property
    def position(self) -> str:
        """Block position TikZ string."""

        if self.parent is None:
            return ""

        return f"[right={0.5 + self.shift[0]}cm of {self.parent.id}, yshift={self.shift[1]}cm]"

    def arrow(self, connector_position: float) -> str:
        """Get TikZ arrow string.


        Parameters
        ----------
        connector_position : float
            distance in cm to right angle bend in connector

        Returns
        -------
        str
            TikZ string for arrow from `parent` to `self` or empty string if `parent` is `None`
        """

        if self.parent is None:
            return ""

        return "".join(
            [
                f"\\draw[thick, rectangle connector={connector_position}cm]",
                f"({self.parent.id}.east) to ({self.id}.west);\n\n",
            ]
        )

    def get_node(self, connector_position: float = 0.25) -> str:
        """Get TikZ node string.

        Parameters
        ----------
        connector_position : float, default: 0.25
            distance in cm to right angle bend in connector

        Returns
        -------
        str
            TikZ string for rendering block
        """

        node = "".join(
            [
                "% Block\n",
                f"\\node[{self.tikz_options.format(fill_color=self.color)}] ",
                f"({self.id}) ",
                self.position,
                f"{{{self.text}}};\n",
                self.arrow(connector_position),
            ]
        )
        return node

    def __add__(self, block: "Block") -> "Series":
        """Add two `Block` instances to make a `Series` instance.

        Parameters
        ----------
        block : Block
            another `Block` instance

        Returns
        -------
        Series
            `Series` instance with `blocks = [self, block]`

        Raises
        ------
        TypeError
            If `block` is not an instance of `Block`
        """

        if not isinstance(block, Block):
            raise TypeError(
                f"cannot add object of type {type(block)=} to Block instance."
            )

        return Series([self, block], parent=self.parent)

    def __mul__(self, value: int) -> "Group":
        """Multiply `Block` instance by `value` to make `Group` with repeated blocks.

        Parameters
        ----------
        value : int
            multiplicative factor

        Returns
        -------
        Group
            `Group` instance with `value` copies of block

        Raises
        ------
        ValueError
            If `value` is not a positive integer
        """

        if not isinstance(value, int) or value <= 0:
            raise ValueError("Multiplicative factor `value` must be a positive integer")

        blocks: list[Block] = [deepcopy(self) for _ in range(value)]

        return Group(blocks, parent=self.parent)

    __rmul__ = __mul__


class Series(Block):
    """Series configuration of `Block` instances for horisontal grouping.

    Parameters
    ----------
    blocks : list[Block]
        list of `Block` instances
    text: str, optional
        series label text
    color: str, optional
        series color
    parent : Optional[Block]
        parent `Block` instance

    Attributes
    ----------
    tikz_options : str
        TikZ node options

    """

    tikz_options: str = ", ".join(
        [
            "anchor=west",
            "align=center",
            "inner sep=0pt",
            "outer sep=0pt",
        ]
    )

    def __init__(
        self,
        blocks: list[Block],
        text: str = "",
        color: str = "",
        parent: Optional[Block] = None,
    ) -> None:
        Block.__init__(self, text, color, parent)

        self.blocks = blocks
        self.blocks[0].id = f"{self.id}+0"
        for i, (block, new_parent) in enumerate(
            zip(self.blocks[1::], self.blocks[0:-1]), start=1
        ):
            block.parent = new_parent
            block.id = f"{self.id}+{i}"

    @property
    def background(self) -> str:
        """Background rectangle TikZ string."""

        if self.color in ("white", ""):
            return ""

        return "".join(
            [
                "\\begin{pgfonlayer}{background}\n",
                f"\\coordinate (sw) at ($({self.id}.south west)+(-1mm, -1mm)$);\n",
                f"\\coordinate (ne) at ($({self.id}.north east)+(1mm, 1mm)$);\n",
                f"\\draw[{self.color}, thick] (sw) rectangle (ne);\n",
                "\\end{pgfonlayer}\n",
            ]
        )

    @property
    def label(self) -> str:
        """Series label string."""

        if len(self.text) == 0:
            return ""

        return "".join(
            [
                f"\\coordinate (nw) at ($({self.id}.north west)+(-1mm, 1mm)$);\n",
                f"\\coordinate (ne) at ($({self.id}.north east)+(1mm, 1mm)$);\n",
                f"\\coordinate (n) at ($({self.id}.north)+(0mm, 1mm)$);\n",
                f"\\draw[{self.color}, fill={self.color}!50, thick] (nw) ",
                "rectangle ($(ne)+(0, 0.5cm)$);\n",
                f"\\node[anchor=south] at (n) {{{self.text}}};\n",
            ]
        )

    def get_node(self, connector_position: float = 0.25) -> str:
        """Get TikZ node string.

        Parameters
        ----------
        connector_position : float, default: 0.25
            distance in cm to right angle bend in connector

        Returns
        -------
        str
            TikZ string for rendering series

        """

        block_nodes = "\n".join(
            block.get_node(connector_position) for block in self.blocks
        )
        series_node = "".join(
            [
                f"\\node[{self.tikz_options}]",
                f"({self.id})",
                self.position,
                "{\\begin{tikzpicture}\n",
                block_nodes,
                "\\end{tikzpicture}};\n\n",
                self.arrow(connector_position),
                self.background,
                self.label,
            ]
        )
        return series_node


class Group(Block):
    """Group of `Block` instances for vertical stacking.

    Parameters
    ----------
    blocks : list[Block]
        list of `Block` instances
    text : str, optional
        group label text
    color : str, optional
        group color
    parent : Optional[Block]
        parent `Block` instance

    Attributes
    ----------
    shift_scale : float
        scaling factor for vertical shifts of blocks
    tikz_options : str
        TikZ node options
    """

    shift_scale: float = 1.2
    tikz_options: str = ", ".join(
        [
            "anchor=west",
        ]
    )

    def __init__(
        self,
        blocks: list[Block],
        text: str = "",
        color: str = "",
        parent: Optional[Block] = None,
    ) -> None:
        Block.__init__(self, text, color, parent)

        self.blocks = blocks
        for i, (block, shift) in enumerate(zip(self.blocks, self.shifts)):
            block.shift = (0, shift)
            block.parent = self
            block.id = f"{self.id}-{i}"

    @property
    def shifts(self) -> list[float]:
        """List of vertical position shifts for each `Block` instance in group.

        Returns
        -------
        list[float]
            list of vertical position shifts for each `Block` instance in group
        """

        n_blocks = len(self.blocks)

        return list(-self.shift_scale * n for n in range(n_blocks))

    @property
    def background(self) -> str:
        """Background rectangle TikZ string."""

        if self.color in ("white", ""):
            return ""

        return "".join(
            [
                "\\begin{pgfonlayer}{background}\n",
                f"\\coordinate (sw) at ($({self.id}.south west)+(-1mm, -1mm)$);\n",
                f"\\coordinate (ne) at ($({self.id}.north east)+(1mm, 1mm)$);\n",
                f"\\draw[{self.color}, thick] (sw) rectangle (ne);\n",
                "\\end{pgfonlayer}\n",
            ]
        )

    @property
    def label(self) -> str:
        """Series label string."""

        if len(self.text) == 0:
            return ""

        return "".join(
            [
                f"\\coordinate (nw) at ($({self.id}.north west)+(-1mm, 1mm)$);\n",
                f"\\coordinate (ne) at ($({self.id}.north east)+(1mm, 1mm)$);\n",
                f"\\coordinate (n) at ($({self.id}.north)+(0mm, 1mm)$);\n",
                f"\\draw[{self.color}, fill={self.color}!50, thick] (nw) ",
                "rectangle ($(ne)+(0, 0.5cm)$);\n",
                f"\\node[anchor=south] at (n) {{{self.text}}};\n",
            ]
        )

    def arrow(self, connector_position: float) -> str:
        """Get TikZ arrow string.

        Parameters
        ----------
        connector_position : float
            distance in cm to right angle bend in connector (not used in `Group` class)

        Returns
        -------
        str
            TikZ string for arrow from `parent` to `self` or empty string if `parent` is `None`
        """

        if self.parent is None:
            return ""

        return f"\\draw[thick] ({self.parent.id}.east) to ({self.id}.west);\n"

    @property
    def arrows(self) -> str:
        """Get TikZ string for arrow connecting stacked blocks."""

        return "\n".join(
            [
                " ".join(
                    [
                        "\\draw[thick, rectangle line]",
                        f"({block1.id}.east) to ({block2.id}.east);\n",
                    ]
                )
                for (block1, block2) in combinations(self.blocks, 2)
            ]
        )

    def get_node(self, connector_position: float = 0.0) -> str:
        """Get TikZ node string.

        Parameters
        ----------
        connector_position : float, default: 0.0
            distance in cm to right angle bend in connector

        Returns
        -------
        str
            TikZ string for rendering group
        """

        block_nodes = "\n".join(
            block.get_node(connector_position) for block in self.blocks
        )

        group_node = "".join(
            [
                f"\\node[anchor=west, outer sep=0pt, inner sep=0pt, align=center] ({self.id}) ",
                self.position,
                "{\\begin{tikzpicture}\n",
                f"\\coordinate ({self.id}) at (0, 0);\n",
                block_nodes,
                self.arrows,
                "\\end{tikzpicture}};\n\n",
                self.arrow(connector_position),
                self.background,
                self.label,
            ]
        )

        return group_node

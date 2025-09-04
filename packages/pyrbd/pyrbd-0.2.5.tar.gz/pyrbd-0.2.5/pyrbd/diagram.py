"""Module containing Diagram class definition."""

import subprocess

import pymupdf

from .block import Block


class Diagram:
    """Reliability block diagram class definition.

    Parameters
    ----------
    name : str
        name of diagram
    blocks : list[Block]
        list of `Block` instances
    hazard : str, optional
        string defining the `hazard` block text
    """

    def __init__(self, name: str, blocks: list[Block], hazard: str = "") -> None:
        self.filename = name
        if hazard:
            self.head = Block(hazard, "red!60")
        else:
            self.head = blocks.pop(0)

        self.head.id = "0"
        self.blocks = blocks
        self.blocks[0].parent = self.head

    def write(self) -> None:
        """Write diagram to .tex file."""

        with open(f"{self.filename}.tex", mode="w", encoding="utf-8") as file:
            file.write(TEX_PREAMBLE)
            for block in [self.head, *self.blocks]:
                file.write(block.get_node())
            file.write(TEX_END)

    def _to_svg(self) -> str:
        """Convert diagram file from pdf to svg.

        Returns
        -------
        str
            filename of .svg file
        """

        pdf_document = pymupdf.open(f"{self.filename}.pdf")
        page = pdf_document[0]

        # Get and convert page to svg image
        svg_content = page.get_svg_image()

        # Save to file
        with open(output_file := f"{self.filename}.svg", "w", encoding="utf-8") as file:
            file.write(svg_content)

        pdf_document.close()

        return output_file

    def _to_png(self) -> str:
        """Convert diagram file from pdf to png.

        Returns
        -------
        str
            filename of .png file
        """

        pdf_document = pymupdf.open(f"{self.filename}.pdf")
        page = pdf_document[0]

        # Get image
        image = page.get_pixmap(dpi=300)  # type: ignore

        # Save to file
        image.save(output_file := f"{self.filename}.png")

        pdf_document.close()

        return output_file

    def compile(
        self, output: str | list[str] = "pdf", clear_source: bool = True
    ) -> list[str]:
        """Compile diagram .tex file.

        Parameters
        ----------
        output : str | list[str], default: 'pdf'
            output format string or list of output formats for diagram. Valid output formats are

            - `'pdf'` (default)
            - `'svg'`
            - `'png'`

        clear_source : bool, default: True
            .tex source file is deleted after compilation if `True`

        Returns
        -------
        list[str]
            list of output filenames

        Raises
        ------
        FileNotFoundError
            If .tex file is not found, e.g. because `Diagram.write()` has not been called
            before `Diagram.compile()`.
        """

        try:
            subprocess.check_call(["latexmk", f"{self.filename}.tex", "--silent"])
            subprocess.check_call(["latexmk", "-c", f"{self.filename}.tex"])
            if clear_source:
                subprocess.check_call(["rm", f"{self.filename}.tex"])
        except subprocess.CalledProcessError as err:
            if err.returncode == 11:
                raise FileNotFoundError(
                    (
                        f"File {self.filename} not found. "
                        + "Check if call to Class method write() is missing."
                    )
                ) from err

        output_files: list[str] = []

        if not isinstance(output, list):
            output = [output]

        if "svg" in output:
            output_files.append(self._to_svg())
        if "png" in output:
            output_files.append(self._to_png())
        if "pdf" not in output:
            subprocess.check_call(["rm", f"{self.filename}.pdf"])
        else:
            output_files.append(f"{self.filename}.pdf")

        return output_files


TEX_PREAMBLE = "\n".join(
    [
        r"\documentclass{standalone}",
        r"\usepackage{tikz}",
        r"\usetikzlibrary{shapes,arrows,positioning,calc}",
        r"\pgfdeclarelayer{background}",
        r"\pgfsetlayers{background, main}",
        r"\tikzset{",
        r"connector/.style={",
        r"-latex,",
        r"font=\scriptsize},",
        r"line/.style={",
        r"font=\scriptsize},",
        r"rectangle connector/.style={",
        r"connector,"
        r"to path={(\tikztostart) -- ++(#1,0pt) \tikztonodes |- (\tikztotarget) },",
        r"pos=0.5},"
        r"rectangle connector/.default=0.5cm,",
        r"rectangle line/.style={",
        r"line,"
        r"to path={(\tikztostart) -- ++(#1,0pt) \tikztonodes |- (\tikztotarget) },",
        r"pos=0.5},"
        r"rectangle line/.default=0.5cm,",
        r"straight connector/.style={",
        r"connector,",
        r"to path=--(\tikztotarget) \tikztonodes}",
        r"}",
        r"\begin{document}",
        r"\begin{tikzpicture}",
        "",
    ]
)

TEX_END = "\n".join(
    [
        r"\end{tikzpicture}",
        r"\end{document}",
    ]
)

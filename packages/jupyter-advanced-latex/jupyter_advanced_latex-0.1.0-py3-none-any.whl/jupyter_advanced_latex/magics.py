import os
from shutil import rmtree

from plasTeX.TeX import TeX
from plasTeX.Renderers import HTML5
from plasTeX.Config import defaultConfig

from IPython.display import display, HTML
from IPython.core.magic import register_line_magic, register_cell_magic
from IPython.core.magic_arguments import argument, magic_arguments, parse_argstring


@magic_arguments()
@argument(
    "--debug",
    action="store_true",
    default=False,
    help="Show warnings and logging information from plasTex.",
)
@register_cell_magic
def plasTeX(line, cell=None):
    """
    A magic function to render LaTeX documents as HTML in Jupyter notebooks.
    Use `%%tex --hide-warning` to suppress warnings.
    """

    # Parse arguments
    args = parse_argstring(plasTeX, line)

    # Silence plasTeX logging (uses Python logging)
    if not args.debug:
        TeX.disableLogging()

    doc = TeX().input(cell).parse()

    #
    # Force plasTex to use the output directory
    #
    os.makedirs("./out", exist_ok=True)
    os.chdir("./out")  # Make the output in the right folder
    renderer = HTML5.Renderer()
    renderer.render(doc)
    os.chdir("./..")  # Come back

    display(HTML(open("./out/index.html", "r").read()))
    # Clean up by removing all temporary files
    rmtree("./out")


@register_line_magic
def texfile(line):
    """
    A magic function to render Tex files as HTML in Jupyter notebooks.
    """

    # Check file exists
    if os.path.exists(line):
        input = open(line, "r").read()
        plasTeX("", input)
    else:
        raise (ValueError("File does not exist"))


def load_ipython_extension(ipython):
    """
    Called by %load_ext texmagic.magics
    (Nothing to do here because decorators already registered the magics.)
    """
    pass


def unload_ipython_extension(ipython):
    pass


def register_ipython_extension(ipython):
    """
    Called by %load_ext texmagic.magics
    (Nothing to do here because decorators already registered the magics.)
    """
    pass

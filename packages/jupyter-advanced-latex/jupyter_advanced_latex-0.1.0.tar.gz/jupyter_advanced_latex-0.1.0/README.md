# Advanced LaTeX Rendering for Jupyter Notebooks

**jupyter-advanced-latex** provides new IPython magic commands for high-quality LaTeX rendering in Jupyter, powered by [plasTeX](https://github.com/plastex/plastex). It enables publication-ready tables, figures, and math directly as HTML within your notebook.

## Installation

```bash
pip install jupyter-advanced-latex
```

## Demo

<https://github.com/jiboncom/jupyter-advanced-latex/blob/demo/usage.ipynb>

## Usage

Import the package once to register the magic commands:

```python
import jupyter_advanced_latex
```

### Render a LaTeX file

```python
%texfile document.tex
```

### Render LaTeX code inline

```python
%%plasTeX
\documentclass{article}
\begin{document}
Hello, \LaTeX!
\end{document}
```

## License

This project is licensed under the [Apache 2.0 License](LICENSE).

from docutils import nodes

from pytdi import TDICombination


def standard_combinations(app, what, name, obj, options, lines):

    # Tweak documentation for pre-defined TDI combinations
    if what == "data" and isinstance(obj, TDICombination):

        lines.append("")
        delays = ", ".join(f"``{d}``" for d in sorted(obj.delays))
        lines.append(f":Delays: {delays}.")

        lines.append("")
        measurements = ", ".join(f"``{m}``" for m in sorted(obj.measurements))
        lines.append(f":Measurements: {measurements}.")

        lines.append(":Components:")
        lines.append("  .. code-block:: python")
        lines.append("")
        lines.append(f"    {obj.components}")


def setup(app):
    app.connect("autodoc-process-docstring", standard_combinations)

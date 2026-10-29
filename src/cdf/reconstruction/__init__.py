"""Local-graph -> global-graph reconstruction from vehicle-local recordings.

Modules, in data-flow order:

- ``tracking``  radar returns -> anonymous local tracks (Kalman + RTS)
- ``local``     vehicles/<X>/ -> local trace (10 Hz) -> local event graph
- ``alignment`` matched collision nodes -> clock offsets between graphs
- ``fusion``    identity association -> global graph -> global trace
- ``render``    JSON, JSONL, Markdown, DOT
- ``pipeline``  one run directory in, ``reconstruction/`` out

Nothing in this package reads ``ground_truth/`` or imports the simulator.
"""

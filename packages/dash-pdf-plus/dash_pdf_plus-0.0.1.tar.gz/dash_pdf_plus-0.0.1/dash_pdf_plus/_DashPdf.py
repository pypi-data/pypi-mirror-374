# AUTO GENERATED FILE - DO NOT EDIT

import typing  # noqa: F401
from typing_extensions import TypedDict, NotRequired, Literal # noqa: F401
from dash.development.base_component import Component, _explicitize_args

ComponentType = typing.Union[
    str,
    int,
    float,
    Component,
    None,
    typing.Sequence[typing.Union[str, int, float, Component, None]],
]

NumberType = typing.Union[
    typing.SupportsFloat, typing.SupportsInt, typing.SupportsComplex
]


class _DashPdf(Component):
    """A _DashPdf component.
_DashPdf is a component that renders a PDF with annotation capabilities.

Keyword arguments:

- id (string; optional):
    Unique identifier for the component.

- annotations (list of dicts; optional):
    Array of annotation objects containing position, type, and content
    data.

- data (string; required):
    PDF data source - can be a URL string, ArrayBuffer, or Uint8Array.

- enableAnnotations (boolean; default False):
    Whether annotation functionality is enabled.

- numPages (number; optional):
    Total number of pages in the PDF document.

- pageNumber (number; default 1):
    Current page number to display (1-based indexing).

- scale (number; default 1.0):
    Zoom scale factor for the PDF display (default: 1.0).

- selectedAnnotationTool (a value equal to: 'none', 'comment', 'rectangle', 'highlight'; default 'none'):
    Currently selected annotation tool type."""
    _children_props = []
    _base_nodes = ['children']
    _namespace = 'dash_pdf_plus'
    _type = '_DashPdf'


    def __init__(
        self,
        id: typing.Optional[typing.Union[str, dict]] = None,
        data: typing.Optional[typing.Union[str, typing.Any]] = None,
        scale: typing.Optional[NumberType] = None,
        pageNumber: typing.Optional[NumberType] = None,
        numPages: typing.Optional[NumberType] = None,
        enableAnnotations: typing.Optional[bool] = None,
        annotations: typing.Optional[typing.Sequence[dict]] = None,
        selectedAnnotationTool: typing.Optional[Literal["none", "comment", "rectangle", "highlight"]] = None,
        onAnnotationAdd: typing.Optional[typing.Any] = None,
        onAnnotationDelete: typing.Optional[typing.Any] = None,
        onAnnotationUpdate: typing.Optional[typing.Any] = None,
        **kwargs
    ):
        self._prop_names = ['id', 'annotations', 'data', 'enableAnnotations', 'numPages', 'pageNumber', 'scale', 'selectedAnnotationTool']
        self._valid_wildcard_attributes =            []
        self.available_properties = ['id', 'annotations', 'data', 'enableAnnotations', 'numPages', 'pageNumber', 'scale', 'selectedAnnotationTool']
        self.available_wildcard_properties =            []
        _explicit_args = kwargs.pop('_explicit_args')
        _locals = locals()
        _locals.update(kwargs)  # For wildcard attrs and excess named props
        args = {k: _locals[k] for k in _explicit_args}

        for k in ['data']:
            if k not in args:
                raise TypeError(
                    'Required argument `' + k + '` was not specified.')

        super(_DashPdf, self).__init__(**args)

setattr(_DashPdf, "__init__", _explicitize_args(_DashPdf.__init__))

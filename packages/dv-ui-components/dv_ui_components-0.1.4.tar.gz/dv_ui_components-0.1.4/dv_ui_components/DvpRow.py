# AUTO GENERATED FILE - DO NOT EDIT

from dash.development.base_component import Component, _explicitize_args


class DvpRow(Component):
    """A DvpRow component.
An Antd Design Row component
https://ant.design/components/grid

Keyword arguments:

- children (a list of or a singular dash component, string or number; optional):
    The content.

- id (string; optional):
    Id of the row.

- align (a value equal to: 'top', 'middle', 'bottom', 'stretch'; default 'middle'):
    Vertical alignment: top | middle | bottom | stretch.

- className (string | dict; optional):
    CSS classname of the row.

- gutter (dict; optional):
    Spacing between grids, could be a number or a object like { xs: 8,
    sm: 16, md: 24}. Or you can use array to make horizontal and
    vertical spacing work at the same time [horizontal, vertical].

    `gutter` is a number | list of numbers | dict with keys:

    - lg (number; optional)

    - md (number; optional)

    - sm (number; optional)

    - xl (number; optional)

    - xs (number; optional)

    - xxl (number; optional)

- justify (a value equal to: 'start', 'end', 'center', 'space-around', 'space-between'; optional):
    Horizontal arrangement.

- style (dict; optional):
    CSS style of the row.

- wrap (boolean; optional):
    Auto wrap line."""
    _children_props = []
    _base_nodes = ['children']
    _namespace = 'dv_ui_components'
    _type = 'DvpRow'
    @_explicitize_args
    def __init__(self, children=None, id=Component.UNDEFINED, className=Component.UNDEFINED, style=Component.UNDEFINED, align=Component.UNDEFINED, gutter=Component.UNDEFINED, justify=Component.UNDEFINED, wrap=Component.UNDEFINED, **kwargs):
        self._prop_names = ['children', 'id', 'align', 'className', 'gutter', 'justify', 'style', 'wrap']
        self._valid_wildcard_attributes =            []
        self.available_properties = ['children', 'id', 'align', 'className', 'gutter', 'justify', 'style', 'wrap']
        self.available_wildcard_properties =            []
        _explicit_args = kwargs.pop('_explicit_args')
        _locals = locals()
        _locals.update(kwargs)  # For wildcard attrs and excess named props
        args = {k: _locals[k] for k in _explicit_args if k != 'children'}

        super(DvpRow, self).__init__(children=children, **args)

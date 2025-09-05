# AUTO GENERATED FILE - DO NOT EDIT

from dash.development.base_component import Component, _explicitize_args


class DvpDivider(Component):
    """A DvpDivider component.
An Ant Design Divder component
See https://ant.design/components/divider
Adapted from feffery-antd-components

Keyword arguments:

- children (a list of or a singular dash component, string or number; optional):
    Text content of the inline text.

- id (string; optional):
    Component id.

- className (string | dict; optional):
    CSS class name.

- direction (a value equal to: 'horizontal', 'vertical'; default 'horizontal'):
    Direction of the divider. Possible values are 'horizontal' and
    'vertical'. Default is 'horizontal'.

- fontColor (string; optional):
    Color of the inline text. Accepts valid color values in CSS.

- fontFamily (string; optional):
    Font family of the inline text. Accepts valid font-family values
    in CSS.

- fontSize (string; optional):
    Font size of the inline text. Accepts valid font-size values in
    CSS.

- fontStyle (string; optional):
    Font style of the inline text. Accepts valid font-style values in
    CSS.

- fontWeight (number; optional):
    Font weight of the inline text. Accepts valid font-weight values
    in CSS.

- innerTextOrientation (a value equal to: 'left', 'center', 'right'; default 'left'):
    Text alignment of the inline text. Possible values are 'left',
    'center', and 'right'. Default is 'center'.

- isDashed (boolean; default False):
    Whether to render the divider as dashed line. True for dashed
    line, False for solid line. Default is False.

- lineColor (string; default 'lightgrey'):
    Color of the divider. Accepts valid color values in CSS.

- style (dict; optional):
    CSS style."""
    _children_props = []
    _base_nodes = ['children']
    _namespace = 'dv_ui_components'
    _type = 'DvpDivider'
    @_explicitize_args
    def __init__(self, children=None, id=Component.UNDEFINED, style=Component.UNDEFINED, className=Component.UNDEFINED, innerTextOrientation=Component.UNDEFINED, isDashed=Component.UNDEFINED, direction=Component.UNDEFINED, fontSize=Component.UNDEFINED, lineColor=Component.UNDEFINED, fontStyle=Component.UNDEFINED, fontWeight=Component.UNDEFINED, fontFamily=Component.UNDEFINED, fontColor=Component.UNDEFINED, **kwargs):
        self._prop_names = ['children', 'id', 'className', 'direction', 'fontColor', 'fontFamily', 'fontSize', 'fontStyle', 'fontWeight', 'innerTextOrientation', 'isDashed', 'lineColor', 'style']
        self._valid_wildcard_attributes =            []
        self.available_properties = ['children', 'id', 'className', 'direction', 'fontColor', 'fontFamily', 'fontSize', 'fontStyle', 'fontWeight', 'innerTextOrientation', 'isDashed', 'lineColor', 'style']
        self.available_wildcard_properties =            []
        _explicit_args = kwargs.pop('_explicit_args')
        _locals = locals()
        _locals.update(kwargs)  # For wildcard attrs and excess named props
        args = {k: _locals[k] for k in _explicit_args if k != 'children'}

        super(DvpDivider, self).__init__(children=children, **args)

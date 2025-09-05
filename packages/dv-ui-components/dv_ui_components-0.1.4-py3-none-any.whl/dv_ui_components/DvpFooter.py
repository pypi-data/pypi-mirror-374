# AUTO GENERATED FILE - DO NOT EDIT

from dash.development.base_component import Component, _explicitize_args


class DvpFooter(Component):
    """A DvpFooter component.
An Ant Design Sider component
See https://ant.design/components/layout

Keyword arguments:

- children (a list of or a singular dash component, string or number; optional):
    Child components inside the layout.

- className (string; optional):
    CSS classes to be added to the component.

- style (dict; optional):
    Inline CSS style.

- textAlign (a value equal to: 'start', 'center', 'end', 'justify'; default 'center'):
    textAlign, in start|center|end|justify."""
    _children_props = []
    _base_nodes = ['children']
    _namespace = 'dv_ui_components'
    _type = 'DvpFooter'
    @_explicitize_args
    def __init__(self, children=None, className=Component.UNDEFINED, style=Component.UNDEFINED, textAlign=Component.UNDEFINED, **kwargs):
        self._prop_names = ['children', 'className', 'style', 'textAlign']
        self._valid_wildcard_attributes =            []
        self.available_properties = ['children', 'className', 'style', 'textAlign']
        self.available_wildcard_properties =            []
        _explicit_args = kwargs.pop('_explicit_args')
        _locals = locals()
        _locals.update(kwargs)  # For wildcard attrs and excess named props
        args = {k: _locals[k] for k in _explicit_args if k != 'children'}

        super(DvpFooter, self).__init__(children=children, **args)

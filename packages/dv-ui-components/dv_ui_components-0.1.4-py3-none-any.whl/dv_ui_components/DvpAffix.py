# AUTO GENERATED FILE - DO NOT EDIT

from dash.development.base_component import Component, _explicitize_args


class DvpAffix(Component):
    """A DvpAffix component.
An Ant Design Affix component
See https://ant.design/components/affix

Keyword arguments:

- children (a list of or a singular dash component, string or number; optional):
    Child components inside the layout.

- id (string; optional):
    The ID used to identify this component.

- className (string; optional):
    CSS classes to be added to the component.

- offsetBottom (number; optional):
    Offset from the bottom of the viewport (in pixels).

- offsetTop (number; default 0):
    Offset from the top of the viewport (in pixels).

- style (dict; optional):
    Inline CSS style.

- target (string; optional):
    Specifies the scrollable area DOM node."""
    _children_props = []
    _base_nodes = ['children']
    _namespace = 'dv_ui_components'
    _type = 'DvpAffix'
    @_explicitize_args
    def __init__(self, children=None, id=Component.UNDEFINED, className=Component.UNDEFINED, style=Component.UNDEFINED, offsetBottom=Component.UNDEFINED, offsetTop=Component.UNDEFINED, target=Component.UNDEFINED, **kwargs):
        self._prop_names = ['children', 'id', 'className', 'offsetBottom', 'offsetTop', 'style', 'target']
        self._valid_wildcard_attributes =            []
        self.available_properties = ['children', 'id', 'className', 'offsetBottom', 'offsetTop', 'style', 'target']
        self.available_wildcard_properties =            []
        _explicit_args = kwargs.pop('_explicit_args')
        _locals = locals()
        _locals.update(kwargs)  # For wildcard attrs and excess named props
        args = {k: _locals[k] for k in _explicit_args if k != 'children'}

        super(DvpAffix, self).__init__(children=children, **args)

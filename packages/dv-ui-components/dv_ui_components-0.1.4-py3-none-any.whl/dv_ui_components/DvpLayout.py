# AUTO GENERATED FILE - DO NOT EDIT

from dash.development.base_component import Component, _explicitize_args


class DvpLayout(Component):
    """A DvpLayout component.
An Ant Design Layout component
See https://ant.design/components/layout

Keyword arguments:

- children (a list of or a singular dash component, string or number; optional):
    Child components inside the layout.

- id (string; optional):
    The ID used to identify this component in Dash callbacks.

- className (string; default 'center'):
    CSS classes to be added to the component.

- hasSider (boolean; default False):
    Whether contain Sider in children, don't have to assign it
    normally. Useful in ssr avoid style flickering.

- loading_state (dict; optional):
    Loading state.

    `loading_state` is a dict with keys:

    - component_name (string; optional):
        Holds the name of the component that is loading.

    - is_loading (boolean; optional):
        Determines if the component is loading or not.

    - prop_name (string; optional):
        Holds which property is loading.

- style (dict; optional):
    Inline CSS style."""
    _children_props = []
    _base_nodes = ['children']
    _namespace = 'dv_ui_components'
    _type = 'DvpLayout'
    @_explicitize_args
    def __init__(self, children=None, id=Component.UNDEFINED, className=Component.UNDEFINED, style=Component.UNDEFINED, hasSider=Component.UNDEFINED, loading_state=Component.UNDEFINED, **kwargs):
        self._prop_names = ['children', 'id', 'className', 'hasSider', 'loading_state', 'style']
        self._valid_wildcard_attributes =            []
        self.available_properties = ['children', 'id', 'className', 'hasSider', 'loading_state', 'style']
        self.available_wildcard_properties =            []
        _explicit_args = kwargs.pop('_explicit_args')
        _locals = locals()
        _locals.update(kwargs)  # For wildcard attrs and excess named props
        args = {k: _locals[k] for k in _explicit_args if k != 'children'}

        super(DvpLayout, self).__init__(children=children, **args)

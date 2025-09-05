# AUTO GENERATED FILE - DO NOT EDIT

from dash.development.base_component import Component, _explicitize_args


class DvpHeader(Component):
    """A DvpHeader component.
An Ant Design Header component
See https://ant.design/components/layout

Keyword arguments:

- children (a list of or a singular dash component, string or number; optional):
    Child components inside the layout.

- id (string; optional):
    The ID used to identify this component.

- backgroundColor (string; default '#fff'):
    Background color.

- className (string; optional):
    CSS classes to be added to the component.

- collapseBtnId (string; optional):
    ID of the collapase button if applicable.

- collapsed (boolean; default False):
    If the sider is collapsed.

- collapsible (boolean; default False):
    Whether the sider is collapsible if applicable.

- isClicked (boolean; optional):
    Whether the sider collapsed button is clicked.

- style (dict; optional):
    Inline CSS style."""
    _children_props = []
    _base_nodes = ['children']
    _namespace = 'dv_ui_components'
    _type = 'DvpHeader'
    @_explicitize_args
    def __init__(self, children=None, id=Component.UNDEFINED, backgroundColor=Component.UNDEFINED, className=Component.UNDEFINED, style=Component.UNDEFINED, collapseBtnId=Component.UNDEFINED, collapsible=Component.UNDEFINED, collapsed=Component.UNDEFINED, isClicked=Component.UNDEFINED, **kwargs):
        self._prop_names = ['children', 'id', 'backgroundColor', 'className', 'collapseBtnId', 'collapsed', 'collapsible', 'isClicked', 'style']
        self._valid_wildcard_attributes =            []
        self.available_properties = ['children', 'id', 'backgroundColor', 'className', 'collapseBtnId', 'collapsed', 'collapsible', 'isClicked', 'style']
        self.available_wildcard_properties =            []
        _explicit_args = kwargs.pop('_explicit_args')
        _locals = locals()
        _locals.update(kwargs)  # For wildcard attrs and excess named props
        args = {k: _locals[k] for k in _explicit_args if k != 'children'}

        super(DvpHeader, self).__init__(children=children, **args)

# AUTO GENERATED FILE - DO NOT EDIT

from dash.development.base_component import Component, _explicitize_args


class DvpDescriptionItem(Component):
    """A DvpDescriptionItem component.
https://ant.design/components/descriptions/

Keyword arguments:

- children (a list of or a singular dash component, string or number; optional):
    The content of the tab - will only be displayed if this tab is
    selected.

- id (string; optional):
    ID.

- className (string; optional):
    CSS classname.

- contentStyle (dict; optional):
    Content style.

- key (string; optional):
    Key.

- label (string; optional):
    Label.

- labelStyle (dict; optional):
    Label style.

- loading_state (dict; optional):
    Loading state.

    `loading_state` is a dict with keys:

    - component_name (string; optional):
        Holds the name of the component that is loading.

    - is_loading (boolean; optional):
        Determines if the component is loading or not.

    - prop_name (string; optional):
        Holds which property is loading.

- span (number; optional):
    Span.

- style (dict; optional):
    CSS STYLE."""
    _children_props = []
    _base_nodes = ['children']
    _namespace = 'dv_ui_components'
    _type = 'DvpDescriptionItem'
    @_explicitize_args
    def __init__(self, children=None, id=Component.UNDEFINED, className=Component.UNDEFINED, style=Component.UNDEFINED, key=Component.UNDEFINED, label=Component.UNDEFINED, span=Component.UNDEFINED, labelStyle=Component.UNDEFINED, contentStyle=Component.UNDEFINED, loading_state=Component.UNDEFINED, **kwargs):
        self._prop_names = ['children', 'id', 'className', 'contentStyle', 'key', 'label', 'labelStyle', 'loading_state', 'span', 'style']
        self._valid_wildcard_attributes =            []
        self.available_properties = ['children', 'id', 'className', 'contentStyle', 'key', 'label', 'labelStyle', 'loading_state', 'span', 'style']
        self.available_wildcard_properties =            []
        _explicit_args = kwargs.pop('_explicit_args')
        _locals = locals()
        _locals.update(kwargs)  # For wildcard attrs and excess named props
        args = {k: _locals[k] for k in _explicit_args if k != 'children'}

        super(DvpDescriptionItem, self).__init__(children=children, **args)

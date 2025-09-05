# AUTO GENERATED FILE - DO NOT EDIT

from dash.development.base_component import Component, _explicitize_args


class DvpIcon(Component):
    """A DvpIcon component.
An Ant Design Icon component
See https://ant.design/components/icon

Keyword arguments:

- id (string; optional):
    The ID used to identify this component in Dash callbacks.

- className (string; optional):
    CSS classes to be added to the component.

- icon (string; optional):
    Specifies the icon type.

- style (dict; optional):
    Inline CSS style."""
    _children_props = []
    _base_nodes = ['children']
    _namespace = 'dv_ui_components'
    _type = 'DvpIcon'
    @_explicitize_args
    def __init__(self, id=Component.UNDEFINED, className=Component.UNDEFINED, style=Component.UNDEFINED, icon=Component.UNDEFINED, **kwargs):
        self._prop_names = ['id', 'className', 'icon', 'style']
        self._valid_wildcard_attributes =            []
        self.available_properties = ['id', 'className', 'icon', 'style']
        self.available_wildcard_properties =            []
        _explicit_args = kwargs.pop('_explicit_args')
        _locals = locals()
        _locals.update(kwargs)  # For wildcard attrs and excess named props
        args = {k: _locals[k] for k in _explicit_args}

        super(DvpIcon, self).__init__(**args)

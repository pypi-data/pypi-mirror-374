# AUTO GENERATED FILE - DO NOT EDIT

from dash.development.base_component import Component, _explicitize_args


class ExecuteJs(Component):
    """An ExecuteJs component.
An feffery-utils-components components

Keyword arguments:

- id (string; optional):
    The ID used to identify this component in Dash callbacks.

- jsString (string; optional):
    JS in string."""
    _children_props = []
    _base_nodes = ['children']
    _namespace = 'dv_ui_components'
    _type = 'ExecuteJs'
    @_explicitize_args
    def __init__(self, id=Component.UNDEFINED, jsString=Component.UNDEFINED, **kwargs):
        self._prop_names = ['id', 'jsString']
        self._valid_wildcard_attributes =            []
        self.available_properties = ['id', 'jsString']
        self.available_wildcard_properties =            []
        _explicit_args = kwargs.pop('_explicit_args')
        _locals = locals()
        _locals.update(kwargs)  # For wildcard attrs and excess named props
        args = {k: _locals[k] for k in _explicit_args}

        super(ExecuteJs, self).__init__(**args)

# AUTO GENERATED FILE - DO NOT EDIT

from dash.development.base_component import Component, _explicitize_args


class DvpCheckbox(Component):
    """A DvpCheckbox component.
An Ant Design Checkbox component
See https://ant.design/components/checkbox
Adapted from feffery-antd-components

Keyword arguments:

- children (a list of or a singular dash component, string or number; optional):
    Text content of the inline text.

- id (string; optional):
    Component id.

- checked (boolean; default False):
    If the box is checked.

- className (string | dict; optional):
    CSS class name.

- disabled (boolean; default False):
    If disable checkbox.

- indeterminate (boolean; default False):
    The indeterminate checked state of checkbox.

- label (a list of or a singular dash component, string or number; optional):
    Label of the checkbox.

- persisted_props (list of a value equal to: 'checked's; default ['checked']):
    Properties whose user interactions will persist after refreshing
    the component or the page. Since only `value` is allowed this prop
    can normally be ignored.

- persistence (boolean | string | number; optional):
    Used to allow user interactions in this component to be persisted
    when the component - or the page - is refreshed. If `persisted` is
    truthy and hasn't changed from its previous value, a `value` that
    the user has changed while using the app will keep that change, as
    long as the new `value` also matches what was given originally.
    Used in conjunction with `persistence_type`.

- persistence_type (a value equal to: 'local', 'session', 'memory'; default 'local'):
    Where persisted user changes will be stored: memory: only kept in
    memory, reset on page refresh. local: window.localStorage, data is
    kept after the browser quit. session: window.sessionStorage, data
    is cleared once the browser quit.

- style (dict; optional):
    Inline CSS style."""
    _children_props = ['label']
    _base_nodes = ['label', 'children']
    _namespace = 'dv_ui_components'
    _type = 'DvpCheckbox'
    @_explicitize_args
    def __init__(self, children=None, id=Component.UNDEFINED, className=Component.UNDEFINED, style=Component.UNDEFINED, disabled=Component.UNDEFINED, label=Component.UNDEFINED, checked=Component.UNDEFINED, indeterminate=Component.UNDEFINED, persistence=Component.UNDEFINED, persisted_props=Component.UNDEFINED, persistence_type=Component.UNDEFINED, **kwargs):
        self._prop_names = ['children', 'id', 'checked', 'className', 'disabled', 'indeterminate', 'label', 'persisted_props', 'persistence', 'persistence_type', 'style']
        self._valid_wildcard_attributes =            []
        self.available_properties = ['children', 'id', 'checked', 'className', 'disabled', 'indeterminate', 'label', 'persisted_props', 'persistence', 'persistence_type', 'style']
        self.available_wildcard_properties =            []
        _explicit_args = kwargs.pop('_explicit_args')
        _locals = locals()
        _locals.update(kwargs)  # For wildcard attrs and excess named props
        args = {k: _locals[k] for k in _explicit_args if k != 'children'}

        super(DvpCheckbox, self).__init__(children=children, **args)

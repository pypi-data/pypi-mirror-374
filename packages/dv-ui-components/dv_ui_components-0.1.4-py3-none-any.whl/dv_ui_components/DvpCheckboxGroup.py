# AUTO GENERATED FILE - DO NOT EDIT

from dash.development.base_component import Component, _explicitize_args


class DvpCheckboxGroup(Component):
    """A DvpCheckboxGroup component.
An Ant Design Checkbox component
See https://ant.design/components/checkbox
Adapted from feffery-antd-components

Keyword arguments:

- children (a list of or a singular dash component, string or number; optional):
    Text content of the inline text.

- id (string; optional):
    Component id.

- className (string | dict; optional):
    CSS class name.

- disabled (boolean; default False):
    Whether to disable the checkbox group.

- includeSelectAll (boolean; optional):
    Whether include select all.

- loading_state (dict; optional):
    loading state.

    `loading_state` is a dict with keys:

    - component_name (string; optional):
        Holds the name of the component that is loading.

    - is_loading (boolean; optional):
        Determines if the component is loading or not.

    - prop_name (string; optional):
        Holds which property is loading.

- options (list of dicts; optional):
    Checkbox options.

    `options` is a list of dicts with keys:

    - disabled (boolean; optional)

    - label (a list of or a singular dash component, string or number; optional)

    - value (string | number; optional)

- persisted_props (list of a value equal to: 'value's; default ['value']):
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

- selectAll (boolean; default True):
    Whether select all.

- value (list of string | numbers; optional):
    Selected value."""
    _children_props = ['options[].label']
    _base_nodes = ['children']
    _namespace = 'dv_ui_components'
    _type = 'DvpCheckboxGroup'
    @_explicitize_args
    def __init__(self, children=None, id=Component.UNDEFINED, className=Component.UNDEFINED, disabled=Component.UNDEFINED, options=Component.UNDEFINED, value=Component.UNDEFINED, includeSelectAll=Component.UNDEFINED, selectAll=Component.UNDEFINED, persistence=Component.UNDEFINED, persisted_props=Component.UNDEFINED, persistence_type=Component.UNDEFINED, loading_state=Component.UNDEFINED, **kwargs):
        self._prop_names = ['children', 'id', 'className', 'disabled', 'includeSelectAll', 'loading_state', 'options', 'persisted_props', 'persistence', 'persistence_type', 'selectAll', 'value']
        self._valid_wildcard_attributes =            []
        self.available_properties = ['children', 'id', 'className', 'disabled', 'includeSelectAll', 'loading_state', 'options', 'persisted_props', 'persistence', 'persistence_type', 'selectAll', 'value']
        self.available_wildcard_properties =            []
        _explicit_args = kwargs.pop('_explicit_args')
        _locals = locals()
        _locals.update(kwargs)  # For wildcard attrs and excess named props
        args = {k: _locals[k] for k in _explicit_args if k != 'children'}

        super(DvpCheckboxGroup, self).__init__(children=children, **args)

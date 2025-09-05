# AUTO GENERATED FILE - DO NOT EDIT

from dash.development.base_component import Component, _explicitize_args


class DvpInputNumber(Component):
    """A DvpInputNumber component.
An Ant Design InputNumber component
See https://ant.design/components/input-number
Adapted from feffery-antd-components

Keyword arguments:

- id (string; optional):
    The ID used to identify this component in Dash callbacks.

- addonAfter (a list of or a singular dash component, string or number; optional):
    The label text displayed after (on the right side of) the input
    field.

- addonBefore (a list of or a singular dash component, string or number; optional):
    The label text displayed before (on the left side of) the input
    field.

- bordered (boolean; default True):
    Whether has border style.

- className (string | dict; optional):
    CSS classes to be added to the component.

- controls (boolean; default True):
    Whether to show +- controls, or set custom arrows icon.

- debounceValue (number | string; optional):
    Debounce value.

- debounceWait (number; default 200):
    Debounce waiting time.

- defaultValue (number | string; optional):
    The initial value.

- disabled (boolean; default False):
    If disable the input.

- keyboard (boolean; default True):
    If enable keyboard behavior.

- loading_state (dict; optional):
    loading state.

    `loading_state` is a dict with keys:

    - component_name (string; optional):
        Holds the name of the component that is loading.

    - is_loading (boolean; optional):
        Determines if the component is loading or not.

    - prop_name (string; optional):
        Holds which property is loading.

- max (number | string; optional):
    The min value.

- min (number | string; optional):
    The max value.

- nSubmit (number; default 0):
    No. of times submitted.

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

- placeholder (string; optional):
    Placeholder.

- precision (number; optional):
    The precision of input value. Will use formatter when config of
    formatter.

- prefix (a list of or a singular dash component, string or number; optional):
    The prefix icon for the Input.

- readOnly (boolean; optional):
    Read only.

- size (a value equal to: 'small', 'middle', 'large'; default 'middle'):
    The height of input box.

- status (a value equal to: 'error', 'warning'; optional):
    Status.

- step (number | string; optional):
    The number to which the current value is increased or decreased.
    It can be an integer or decimal.

- stringMode (boolean; default False):
    Set value as string to support high precision decimals. Will
    return string value by onChange.

- style (dict; optional):
    Inline CSS style.

- value (number | string; optional):
    The current value."""
    _children_props = ['addonBefore', 'addonAfter', 'prefix']
    _base_nodes = ['addonBefore', 'addonAfter', 'prefix', 'children']
    _namespace = 'dv_ui_components'
    _type = 'DvpInputNumber'
    @_explicitize_args
    def __init__(self, id=Component.UNDEFINED, className=Component.UNDEFINED, style=Component.UNDEFINED, addonBefore=Component.UNDEFINED, addonAfter=Component.UNDEFINED, prefix=Component.UNDEFINED, controls=Component.UNDEFINED, keyboard=Component.UNDEFINED, min=Component.UNDEFINED, max=Component.UNDEFINED, step=Component.UNDEFINED, precision=Component.UNDEFINED, stringMode=Component.UNDEFINED, disabled=Component.UNDEFINED, size=Component.UNDEFINED, bordered=Component.UNDEFINED, placeholder=Component.UNDEFINED, value=Component.UNDEFINED, defaultValue=Component.UNDEFINED, debounceValue=Component.UNDEFINED, debounceWait=Component.UNDEFINED, nSubmit=Component.UNDEFINED, status=Component.UNDEFINED, readOnly=Component.UNDEFINED, persistence=Component.UNDEFINED, persisted_props=Component.UNDEFINED, persistence_type=Component.UNDEFINED, loading_state=Component.UNDEFINED, **kwargs):
        self._prop_names = ['id', 'addonAfter', 'addonBefore', 'bordered', 'className', 'controls', 'debounceValue', 'debounceWait', 'defaultValue', 'disabled', 'keyboard', 'loading_state', 'max', 'min', 'nSubmit', 'persisted_props', 'persistence', 'persistence_type', 'placeholder', 'precision', 'prefix', 'readOnly', 'size', 'status', 'step', 'stringMode', 'style', 'value']
        self._valid_wildcard_attributes =            []
        self.available_properties = ['id', 'addonAfter', 'addonBefore', 'bordered', 'className', 'controls', 'debounceValue', 'debounceWait', 'defaultValue', 'disabled', 'keyboard', 'loading_state', 'max', 'min', 'nSubmit', 'persisted_props', 'persistence', 'persistence_type', 'placeholder', 'precision', 'prefix', 'readOnly', 'size', 'status', 'step', 'stringMode', 'style', 'value']
        self.available_wildcard_properties =            []
        _explicit_args = kwargs.pop('_explicit_args')
        _locals = locals()
        _locals.update(kwargs)  # For wildcard attrs and excess named props
        args = {k: _locals[k] for k in _explicit_args}

        super(DvpInputNumber, self).__init__(**args)

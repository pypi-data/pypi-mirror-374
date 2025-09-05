# AUTO GENERATED FILE - DO NOT EDIT

from dash.development.base_component import Component, _explicitize_args


class DvpRadioGroup(Component):
    """A DvpRadioGroup component.
An Ant Design Divder component
See https://ant.design/components/radio
Adapted from feffery-antd-components

Keyword arguments:

- id (string; optional):
    The ID used to identify this component in Dash callbacks.

- buttonStyle (a value equal to: 'outline', 'solid'; default 'outline'):
    The style type of radio button, outline | solid.

- className (string; optional):
    CSS classes to be added to the component.

- defaultValue (string | number; optional):
    Default selected value.

- direction (a value equal to: 'horizontal', 'vertical'; default 'horizontal'):
    Direction of the radio group.

- disabled (boolean; default False):
    Disable the radio group.

- loading_state (dict; optional):
    Loading state.

    `loading_state` is a dict with keys:

    - component_name (string; optional):
        Holds the name of the component that is loading.

    - is_loading (boolean; optional):
        Determines if the component is loading or not.

    - prop_name (string; optional):
        Holds which property is loading.

- optionType (a value equal to: 'default', 'button', 'image', 'image-link'; default 'default'):
    Set Radio optionType.

- options (list of dicts; optional):
    Array of options.

    `options` is a list of dicts with keys:

    - disabled (boolean; optional)

    - label (dict; optional)

        `label` is a a list of or a singular dash component, string or
        number

      Or dict with keys:

        - height (number; optional)

        - src (string; optional)

              Or dict with keys:

        - height (number; optional)

        - link (string; optional)

        - src (string; optional)

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

- size (a value equal to: 'large', 'middle', 'small'; default 'small'):
    Size of the radio group.

- style (dict; optional):
    Inline CSS style.

- value (string | number; optional):
    Selected value."""
    _children_props = ['options[].label']
    _base_nodes = ['children']
    _namespace = 'dv_ui_components'
    _type = 'DvpRadioGroup'
    @_explicitize_args
    def __init__(self, id=Component.UNDEFINED, className=Component.UNDEFINED, style=Component.UNDEFINED, direction=Component.UNDEFINED, options=Component.UNDEFINED, disabled=Component.UNDEFINED, size=Component.UNDEFINED, value=Component.UNDEFINED, defaultValue=Component.UNDEFINED, optionType=Component.UNDEFINED, buttonStyle=Component.UNDEFINED, persistence=Component.UNDEFINED, persisted_props=Component.UNDEFINED, persistence_type=Component.UNDEFINED, loading_state=Component.UNDEFINED, **kwargs):
        self._prop_names = ['id', 'buttonStyle', 'className', 'defaultValue', 'direction', 'disabled', 'loading_state', 'optionType', 'options', 'persisted_props', 'persistence', 'persistence_type', 'size', 'style', 'value']
        self._valid_wildcard_attributes =            []
        self.available_properties = ['id', 'buttonStyle', 'className', 'defaultValue', 'direction', 'disabled', 'loading_state', 'optionType', 'options', 'persisted_props', 'persistence', 'persistence_type', 'size', 'style', 'value']
        self.available_wildcard_properties =            []
        _explicit_args = kwargs.pop('_explicit_args')
        _locals = locals()
        _locals.update(kwargs)  # For wildcard attrs and excess named props
        args = {k: _locals[k] for k in _explicit_args}

        super(DvpRadioGroup, self).__init__(**args)

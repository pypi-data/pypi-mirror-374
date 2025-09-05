# AUTO GENERATED FILE - DO NOT EDIT

from dash.development.base_component import Component, _explicitize_args


class DvpSlider(Component):
    """A DvpSlider component.
An Ant Design slider component
See https://ant.design/components/slider
Adapted from feffery-antd-components

Keyword arguments:

- id (string; optional):
    The ID used to identify this component in Dash callbacks.

- className (string; optional):
    CSS classes to be added to the component.

- defaultValue (number | list of numbers; optional):
    Default value.

- disabled (boolean; default False):
    Disable the component.

- fixedMax (boolean; default False):
    Whether fix the max value.

- inputNumberBox (boolean; default False):
    Add inputnumber box.

- inputStyle (dict; optional):
    CSS Style of the input box if applicable.

- loading_state (dict; optional):
    loading state.

    `loading_state` is a dict with keys:

    - component_name (string; optional):
        Holds the name of the component that is loading.

    - is_loading (boolean; optional):
        Determines if the component is loading or not.

    - prop_name (string; optional):
        Holds which property is loading.

- marks (dict with strings as keys and values of type string; optional):
    Tick mark of Slider, type of key must be number, and must in
    closed interval [min, max], each mark can declare its own style.

- max (number; default 100):
    The minimum value the slider can slide to.

- min (number; default 0):
    The maximum value the slider can slide to.

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

- popupContainer (a value equal to: 'parent', 'body'; default 'body'):
    The DOM container of the Tooltip, the default behavior is to
    create a div element in body.

- railStyle (dict; optional):
    The style of slider rail (the background).

- range (boolean; default False):
    Dual thumb mode.

- reverse (boolean; optional):
    Reverse.

- step (number; default 1):
    The granularity the slider can step through values. Must greater
    than 0, and be divided by (max - min) . When marks no None, step
    can be None.

- style (dict; optional):
    Inline CSS style.

- tooltipPosition (a value equal to: 'top', 'bottom'; default 'top'):
    tooltipPosition.

- tooltipPrefix (string; default ''):
    Tooltip prefix.

- tooltipSuffix (string; default ''):
    Tooltip suffix.

- tooltipVisible (boolean; optional):
    Whether to display tooltop.

- value (number | list of numbers; optional):
    Value.

- vertical (boolean; default False):
    Vertical mode."""
    _children_props = []
    _base_nodes = ['children']
    _namespace = 'dv_ui_components'
    _type = 'DvpSlider'
    @_explicitize_args
    def __init__(self, id=Component.UNDEFINED, className=Component.UNDEFINED, style=Component.UNDEFINED, inputStyle=Component.UNDEFINED, railStyle=Component.UNDEFINED, vertical=Component.UNDEFINED, range=Component.UNDEFINED, min=Component.UNDEFINED, max=Component.UNDEFINED, step=Component.UNDEFINED, marks=Component.UNDEFINED, tooltipVisible=Component.UNDEFINED, tooltipPrefix=Component.UNDEFINED, tooltipSuffix=Component.UNDEFINED, inputNumberBox=Component.UNDEFINED, disabled=Component.UNDEFINED, fixedMax=Component.UNDEFINED, value=Component.UNDEFINED, defaultValue=Component.UNDEFINED, popupContainer=Component.UNDEFINED, reverse=Component.UNDEFINED, persistence=Component.UNDEFINED, tooltipPosition=Component.UNDEFINED, persisted_props=Component.UNDEFINED, persistence_type=Component.UNDEFINED, loading_state=Component.UNDEFINED, **kwargs):
        self._prop_names = ['id', 'className', 'defaultValue', 'disabled', 'fixedMax', 'inputNumberBox', 'inputStyle', 'loading_state', 'marks', 'max', 'min', 'persisted_props', 'persistence', 'persistence_type', 'popupContainer', 'railStyle', 'range', 'reverse', 'step', 'style', 'tooltipPosition', 'tooltipPrefix', 'tooltipSuffix', 'tooltipVisible', 'value', 'vertical']
        self._valid_wildcard_attributes =            []
        self.available_properties = ['id', 'className', 'defaultValue', 'disabled', 'fixedMax', 'inputNumberBox', 'inputStyle', 'loading_state', 'marks', 'max', 'min', 'persisted_props', 'persistence', 'persistence_type', 'popupContainer', 'railStyle', 'range', 'reverse', 'step', 'style', 'tooltipPosition', 'tooltipPrefix', 'tooltipSuffix', 'tooltipVisible', 'value', 'vertical']
        self.available_wildcard_properties =            []
        _explicit_args = kwargs.pop('_explicit_args')
        _locals = locals()
        _locals.update(kwargs)  # For wildcard attrs and excess named props
        args = {k: _locals[k] for k in _explicit_args}

        super(DvpSlider, self).__init__(**args)

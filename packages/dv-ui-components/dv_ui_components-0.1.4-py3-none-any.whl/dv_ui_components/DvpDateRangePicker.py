# AUTO GENERATED FILE - DO NOT EDIT

from dash.development.base_component import Component, _explicitize_args


class DvpDateRangePicker(Component):
    """A DvpDateRangePicker component.
An Ant Date Picker component
See https://ant.design/components/date-picker
Adapted from feffery-antd-components

Keyword arguments:

- id (string; optional):
    The ID used to identify this component in Dash callbacks.

- allowClear (boolean; default True):
    Allow clear.

- bordered (boolean; default True):
    Whether the box should be bordered.

- className (string; optional):
    CSS classes to be added to the component.

- defaultPickerValue (string; optional):
    Default picker value.

- defaultValue (list of strings; optional):
    Default data values.

- disabled (list of booleans; default [False, False]):
    Disable the component.

- disabledDatesStrategy (list of dicts; optional):
    Disable date strategy.

    `disabledDatesStrategy` is a list of dicts with keys:

    - mode (a value equal to: 'eq', 'ne', 'le', 'lt', 'ge', 'gt', 'in', 'not-in', 'in-enumerate-dates', 'not-in-enumerate-dates'; optional)

    - target (a value equal to: 'day', 'month', 'quarter', 'year', 'dayOfYear', 'dayOfWeek', 'specific-date'; optional)

    - value (number | string | list of numbers | list of strings; optional)

- firstDayOfWeek (number; optional):
    Define first day of week.

- format (string; optional):
    Date format.

- open (boolean; optional):
    Whether it is open.

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

- picker (a value equal to: 'date', 'week', 'month', 'quarter', 'year'; default 'date'):
    Precision.

- placeholder (list of strings; optional):
    Placeholder.

- placement (a value equal to: 'bottomLeft', 'bottomRight', 'topLeft', 'topRight'; default 'bottomLeft'):
    The position where the selection box pops up.

- popupContainer (a value equal to: 'parent', 'body'; default 'body'):
    To set the container of the floating layer, while the default is
    to create a div element in body.

- readOnly (boolean; optional):
    To set the container of the floating layer, while the default is
    to create a div element in body.

- showTime (dict; default False):
    Allow time display.

    `showTime` is a boolean | dict with keys:

    - defaultValue (list of strings; optional)

    - format (string; optional)

- size (a value equal to: 'small', 'middle', 'large'; default 'middle'):
    Size.

- status (a value equal to: 'error', 'warning'; optional):
    Status.

- style (dict; optional):
    Inline CSS style.

- value (list of strings; optional):
    Select date trange."""
    _children_props = []
    _base_nodes = ['children']
    _namespace = 'dv_ui_components'
    _type = 'DvpDateRangePicker'
    @_explicitize_args
    def __init__(self, id=Component.UNDEFINED, className=Component.UNDEFINED, style=Component.UNDEFINED, format=Component.UNDEFINED, picker=Component.UNDEFINED, firstDayOfWeek=Component.UNDEFINED, disabled=Component.UNDEFINED, showTime=Component.UNDEFINED, size=Component.UNDEFINED, bordered=Component.UNDEFINED, placeholder=Component.UNDEFINED, placement=Component.UNDEFINED, value=Component.UNDEFINED, defaultValue=Component.UNDEFINED, defaultPickerValue=Component.UNDEFINED, disabledDatesStrategy=Component.UNDEFINED, open=Component.UNDEFINED, status=Component.UNDEFINED, allowClear=Component.UNDEFINED, readOnly=Component.UNDEFINED, popupContainer=Component.UNDEFINED, persistence=Component.UNDEFINED, persisted_props=Component.UNDEFINED, persistence_type=Component.UNDEFINED, **kwargs):
        self._prop_names = ['id', 'allowClear', 'bordered', 'className', 'defaultPickerValue', 'defaultValue', 'disabled', 'disabledDatesStrategy', 'firstDayOfWeek', 'format', 'open', 'persisted_props', 'persistence', 'persistence_type', 'picker', 'placeholder', 'placement', 'popupContainer', 'readOnly', 'showTime', 'size', 'status', 'style', 'value']
        self._valid_wildcard_attributes =            []
        self.available_properties = ['id', 'allowClear', 'bordered', 'className', 'defaultPickerValue', 'defaultValue', 'disabled', 'disabledDatesStrategy', 'firstDayOfWeek', 'format', 'open', 'persisted_props', 'persistence', 'persistence_type', 'picker', 'placeholder', 'placement', 'popupContainer', 'readOnly', 'showTime', 'size', 'status', 'style', 'value']
        self.available_wildcard_properties =            []
        _explicit_args = kwargs.pop('_explicit_args')
        _locals = locals()
        _locals.update(kwargs)  # For wildcard attrs and excess named props
        args = {k: _locals[k] for k in _explicit_args}

        super(DvpDateRangePicker, self).__init__(**args)

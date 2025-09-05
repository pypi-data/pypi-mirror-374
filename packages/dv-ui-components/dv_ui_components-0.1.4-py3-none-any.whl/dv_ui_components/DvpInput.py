# AUTO GENERATED FILE - DO NOT EDIT

from dash.development.base_component import Component, _explicitize_args


class DvpInput(Component):
    """A DvpInput component.
An Ant Design input component
See https://ant.design/components/input
Adapted from feffery-antd-components

Keyword arguments:

- id (string; optional):
    The ID used to identify this component in Dash callbacks.

- addonAfter (a list of or a singular dash component, string or number; optional):
    Ojbect (e.g, icon) after.

- addonBefore (a list of or a singular dash component, string or number; optional):
    Ojbect (e.g, icon) before.

- allowClear (boolean; default False):
    Auto clear.

- autoComplete (a value equal to: 'off', 'on'; default 'on'):
    Autocomplete.

- autoSize (dict; default False):
    Autosize.

    `autoSize` is a boolean | dict with keys:

    - maxRows (number; optional)

    - minRows (number; optional)

- bordered (boolean; default True):
    Whether to show the border of the input box.

- className (string; optional):
    CSS classes to be added to the component.

- countFormat (string; optional):
    Mode of showcount.

- debounceValue (string; optional):
    debounce value.

- debounceWait (number; default 200):
    debounce wait.

- defaultValue (string; optional):
    Default value.

- disabled (boolean; default False):
    Disable the input object.

- emptyAsNone (boolean; default False):
    Differentiate '' and None.

- loading_state (dict; optional):
    Loading state.

    `loading_state` is a dict with keys:

    - component_name (string; optional):
        Holds the name of the component that is loading.

    - is_loading (boolean; optional):
        Determines if the component is loading or not.

    - prop_name (string; optional):
        Holds which property is loading.

- maxLength (number; optional):
    Max lenghth of the entry.

- md5Value (string; optional):
    md5 value.

- mode (a value equal to: 'default', 'search', 'text-area', 'password'; default 'default'):
    Mode of the input.

- nClicksSearch (number; default 0):
    Record the number of times the search button is clicked.

- nSubmit (number; default 0):
    Record the number of times the submit button is clicked.

- passwordUseMd5 (boolean; default False):
    Passowrd mode to use md5 value.

- persisted_props (list of a value equal to: 'value', 'md5Value's; default ['value', 'md5Value']):
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
    Placehoder of the inputbox.

- prefix (a list of or a singular dash component, string or number; optional):
    Prefix inside the input box.

- readOnly (boolean; optional):
    Read only mode.

- redirect (boolean; default False):
    if redirect to another page.

- redirectURL (string; optional):
    url to redirect if applicable.

- showCount (boolean; default False):
    Whether to show character count.

- size (a value equal to: 'small', 'middle', 'large'; default 'middle'):
    Size of the input box.

- status (a value equal to: 'error', 'warning'; optional):
    Set validation status.

- style (dict; optional):
    Inline CSS style.

- suffix (a list of or a singular dash component, string or number; optional):
    suffix inside the input box.

- value (string; optional):
    Value entered."""
    _children_props = ['addonBefore', 'addonAfter', 'prefix', 'suffix']
    _base_nodes = ['addonBefore', 'addonAfter', 'prefix', 'suffix', 'children']
    _namespace = 'dv_ui_components'
    _type = 'DvpInput'
    @_explicitize_args
    def __init__(self, id=Component.UNDEFINED, className=Component.UNDEFINED, style=Component.UNDEFINED, mode=Component.UNDEFINED, autoComplete=Component.UNDEFINED, disabled=Component.UNDEFINED, size=Component.UNDEFINED, bordered=Component.UNDEFINED, placeholder=Component.UNDEFINED, value=Component.UNDEFINED, defaultValue=Component.UNDEFINED, md5Value=Component.UNDEFINED, redirect=Component.UNDEFINED, redirectURL=Component.UNDEFINED, debounceValue=Component.UNDEFINED, passwordUseMd5=Component.UNDEFINED, debounceWait=Component.UNDEFINED, addonBefore=Component.UNDEFINED, addonAfter=Component.UNDEFINED, prefix=Component.UNDEFINED, suffix=Component.UNDEFINED, maxLength=Component.UNDEFINED, showCount=Component.UNDEFINED, countFormat=Component.UNDEFINED, autoSize=Component.UNDEFINED, nSubmit=Component.UNDEFINED, nClicksSearch=Component.UNDEFINED, status=Component.UNDEFINED, allowClear=Component.UNDEFINED, readOnly=Component.UNDEFINED, emptyAsNone=Component.UNDEFINED, persistence=Component.UNDEFINED, persisted_props=Component.UNDEFINED, persistence_type=Component.UNDEFINED, loading_state=Component.UNDEFINED, **kwargs):
        self._prop_names = ['id', 'addonAfter', 'addonBefore', 'allowClear', 'autoComplete', 'autoSize', 'bordered', 'className', 'countFormat', 'debounceValue', 'debounceWait', 'defaultValue', 'disabled', 'emptyAsNone', 'loading_state', 'maxLength', 'md5Value', 'mode', 'nClicksSearch', 'nSubmit', 'passwordUseMd5', 'persisted_props', 'persistence', 'persistence_type', 'placeholder', 'prefix', 'readOnly', 'redirect', 'redirectURL', 'showCount', 'size', 'status', 'style', 'suffix', 'value']
        self._valid_wildcard_attributes =            []
        self.available_properties = ['id', 'addonAfter', 'addonBefore', 'allowClear', 'autoComplete', 'autoSize', 'bordered', 'className', 'countFormat', 'debounceValue', 'debounceWait', 'defaultValue', 'disabled', 'emptyAsNone', 'loading_state', 'maxLength', 'md5Value', 'mode', 'nClicksSearch', 'nSubmit', 'passwordUseMd5', 'persisted_props', 'persistence', 'persistence_type', 'placeholder', 'prefix', 'readOnly', 'redirect', 'redirectURL', 'showCount', 'size', 'status', 'style', 'suffix', 'value']
        self.available_wildcard_properties =            []
        _explicit_args = kwargs.pop('_explicit_args')
        _locals = locals()
        _locals.update(kwargs)  # For wildcard attrs and excess named props
        args = {k: _locals[k] for k in _explicit_args}

        super(DvpInput, self).__init__(**args)

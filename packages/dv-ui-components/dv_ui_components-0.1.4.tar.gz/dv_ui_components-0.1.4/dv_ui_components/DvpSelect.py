# AUTO GENERATED FILE - DO NOT EDIT

from dash.development.base_component import Component, _explicitize_args


class DvpSelect(Component):
    """A DvpSelect component.
An Ant Design Select component
See https://ant.design/components/select
Adapted from feffery-antd-components

Keyword arguments:

- id (string; optional):
    The ID used to identify this component in Dash callbacks.

- allowClear (boolean; default True):
    Allow content to be cleared.

- autoClearSearchValue (boolean; default True):
    Whether the current search will be cleared on selecting an item.
    Only applies when mode is set to multiple or tags.

- autoSpin (boolean; default False):
    Auto spin.

- bordered (boolean; default True):
    Border of the select box.

- className (string; optional):
    CSS classes to be added to the component.

- debounceSearchValue (string; optional):
    Debounce search value.

- debounceWait (number; default 200):
    Debounce wait.

- defaultValue (string | number | list of string | numbers; optional):
    Initial selected option.

- disabled (boolean; default False):
    If disable the select component.

- dropdownAfter (a list of or a singular dash component, string or number; optional):
    Ojbect (e.g, icon) after the dropdown.

- dropdownBefore (a list of or a singular dash component, string or number; optional):
    Ojbect (e.g, icon) before the dropdown.

- emptyContent (a list of or a singular dash component, string or number; optional):
    Empty contnet.

- listHeight (number; default 256):
    List height.

- loadingEmptyContent (a list of or a singular dash component, string or number; default <div style={{display: 'flex', justifyContent: 'center'}}>    <Spin /></div>):
    Load empty content.

- loading_state (dict; optional):
    loading state.

    `loading_state` is a dict with keys:

    - component_name (string; optional):
        Holds the name of the component that is loading.

    - is_loading (boolean; optional):
        Determines if the component is loading or not.

    - prop_name (string; optional):
        Holds which property is loading.

- maxTagCount (number | a value equal to: 'responsive'; optional):
    Max tag count.

- mode (a value equal to: 'multiple', 'tags'; optional):
    Selection mode.

- optionFilterMode (a value equal to: 'case-insensitive', 'case-sensitive', 'regex'; default 'case-insensitive'):
    Option filter mode.

- optionFilterProp (a value equal to: 'value', 'label'; default 'label'):
    Which prop value of option will be used for filter if filterOption
    is True. If options is set, it should be set to label.

- options (list of dicts; optional):
    Options.

    `options` is a list of dicts with keys:

    - disabled (boolean; optional)

    - label (a list of or a singular dash component, string or number; required)

    - value (string

      Or number; required) | dict with keys:

    - group (string; optional)

    - options (list of dicts; optional)

        `options` is a list of dicts with keys:

        - disabled (boolean; optional)

        - label (a list of or a singular dash component, string or number; required)

        - value (string | number; required)

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
    Placeholder text.

- placement (a value equal to: 'bottomLeft', 'bottomRight', 'topLeft', 'topRight'; default 'bottomLeft'):
    The position where the selection box pops up.

- popupContainer (a value equal to: 'parent', 'body'; default 'body'):
    Continer of the popup.

- readOnly (boolean; optional):
    Readonly.

- searchValue (string; optional):
    The current input \"search\" text.

- size (a value equal to: 'small', 'middle', 'large'; default 'middle'):
    Sice of the component.

- status (a value equal to: 'error', 'warning'; optional):
    Set validation status.

- style (dict; optional):
    Inline CSS style.

- tagColor (string; default '#f1f3ff'):
    Tag color.

- value (string | number | list of string | numbers; optional):
    Selected value."""
    _children_props = ['options[].label', 'options[].options[].label', 'emptyContent', 'loadingEmptyContent', 'dropdownBefore', 'dropdownAfter']
    _base_nodes = ['emptyContent', 'loadingEmptyContent', 'dropdownBefore', 'dropdownAfter', 'children']
    _namespace = 'dv_ui_components'
    _type = 'DvpSelect'
    @_explicitize_args
    def __init__(self, id=Component.UNDEFINED, className=Component.UNDEFINED, style=Component.UNDEFINED, options=Component.UNDEFINED, listHeight=Component.UNDEFINED, mode=Component.UNDEFINED, disabled=Component.UNDEFINED, size=Component.UNDEFINED, bordered=Component.UNDEFINED, tagColor=Component.UNDEFINED, placeholder=Component.UNDEFINED, placement=Component.UNDEFINED, value=Component.UNDEFINED, defaultValue=Component.UNDEFINED, maxTagCount=Component.UNDEFINED, status=Component.UNDEFINED, optionFilterProp=Component.UNDEFINED, searchValue=Component.UNDEFINED, optionFilterMode=Component.UNDEFINED, debounceSearchValue=Component.UNDEFINED, debounceWait=Component.UNDEFINED, autoSpin=Component.UNDEFINED, autoClearSearchValue=Component.UNDEFINED, emptyContent=Component.UNDEFINED, loadingEmptyContent=Component.UNDEFINED, dropdownBefore=Component.UNDEFINED, dropdownAfter=Component.UNDEFINED, allowClear=Component.UNDEFINED, readOnly=Component.UNDEFINED, popupContainer=Component.UNDEFINED, persistence=Component.UNDEFINED, persisted_props=Component.UNDEFINED, persistence_type=Component.UNDEFINED, loading_state=Component.UNDEFINED, **kwargs):
        self._prop_names = ['id', 'allowClear', 'autoClearSearchValue', 'autoSpin', 'bordered', 'className', 'debounceSearchValue', 'debounceWait', 'defaultValue', 'disabled', 'dropdownAfter', 'dropdownBefore', 'emptyContent', 'listHeight', 'loadingEmptyContent', 'loading_state', 'maxTagCount', 'mode', 'optionFilterMode', 'optionFilterProp', 'options', 'persisted_props', 'persistence', 'persistence_type', 'placeholder', 'placement', 'popupContainer', 'readOnly', 'searchValue', 'size', 'status', 'style', 'tagColor', 'value']
        self._valid_wildcard_attributes =            []
        self.available_properties = ['id', 'allowClear', 'autoClearSearchValue', 'autoSpin', 'bordered', 'className', 'debounceSearchValue', 'debounceWait', 'defaultValue', 'disabled', 'dropdownAfter', 'dropdownBefore', 'emptyContent', 'listHeight', 'loadingEmptyContent', 'loading_state', 'maxTagCount', 'mode', 'optionFilterMode', 'optionFilterProp', 'options', 'persisted_props', 'persistence', 'persistence_type', 'placeholder', 'placement', 'popupContainer', 'readOnly', 'searchValue', 'size', 'status', 'style', 'tagColor', 'value']
        self.available_wildcard_properties =            []
        _explicit_args = kwargs.pop('_explicit_args')
        _locals = locals()
        _locals.update(kwargs)  # For wildcard attrs and excess named props
        args = {k: _locals[k] for k in _explicit_args}

        super(DvpSelect, self).__init__(**args)

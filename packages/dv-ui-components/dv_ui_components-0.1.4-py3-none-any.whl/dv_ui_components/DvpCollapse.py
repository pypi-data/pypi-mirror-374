# AUTO GENERATED FILE - DO NOT EDIT

from dash.development.base_component import Component, _explicitize_args


class DvpCollapse(Component):
    """A DvpCollapse component.
An Ant Design collapse component
See https://ant.design/components/collapse
Adapted from feffery-antd-components

Keyword arguments:

- children (a list of or a singular dash component, string or number; optional):
    Children of the collapose item.

- id (string; optional):
    The ID used to identify this component in Dash callbacks.

- bodyPadding (default '12px'):
    bodyPadding.

- bordered (boolean; default True):
    Whether to display the border of the collapse item.

- className (string; optional):
    CSS classes to be added to the component.

- collapsible (a value equal to: 'header', 'disabled', 'icon'; optional):
    Whether the object is collapsible.

- forceRender (boolean; default False):
    Whether to render when the object is collpased.

- ghost (boolean; default False):
    Ghost mode of the collapse item.

- headBgColor (string; default 'transparent'):
    Head: background color.

- headColor (string; default '#424245e0'):
    Head: text color.

- isOpen (boolean; default True):
    If it is open.

- loading_state (dict; optional):
    Loading state.

    `loading_state` is a dict with keys:

    - component_name (string; optional):
        Holds the name of the component that is loading.

    - is_loading (boolean; optional):
        Determines if the component is loading or not.

    - prop_name (string; optional):
        Holds which property is loading.

- persisted_props (list of a value equal to: 'isOpen's; default ['isOpen']):
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

- showArrow (boolean; default True):
    If False, panel will not show arrow icon. If False, collapsible
    can't be set as icon.

- style (dict; optional):
    Inline CSS style.

- title (a list of or a singular dash component, string or number; optional):
    Title of the panel."""
    _children_props = ['title']
    _base_nodes = ['title', 'children']
    _namespace = 'dv_ui_components'
    _type = 'DvpCollapse'
    @_explicitize_args
    def __init__(self, children=None, id=Component.UNDEFINED, className=Component.UNDEFINED, style=Component.UNDEFINED, headColor=Component.UNDEFINED, headBgColor=Component.UNDEFINED, title=Component.UNDEFINED, isOpen=Component.UNDEFINED, bordered=Component.UNDEFINED, showArrow=Component.UNDEFINED, ghost=Component.UNDEFINED, collapsible=Component.UNDEFINED, forceRender=Component.UNDEFINED, bodyPadding=Component.UNDEFINED, persistence=Component.UNDEFINED, persisted_props=Component.UNDEFINED, persistence_type=Component.UNDEFINED, loading_state=Component.UNDEFINED, **kwargs):
        self._prop_names = ['children', 'id', 'bodyPadding', 'bordered', 'className', 'collapsible', 'forceRender', 'ghost', 'headBgColor', 'headColor', 'isOpen', 'loading_state', 'persisted_props', 'persistence', 'persistence_type', 'showArrow', 'style', 'title']
        self._valid_wildcard_attributes =            []
        self.available_properties = ['children', 'id', 'bodyPadding', 'bordered', 'className', 'collapsible', 'forceRender', 'ghost', 'headBgColor', 'headColor', 'isOpen', 'loading_state', 'persisted_props', 'persistence', 'persistence_type', 'showArrow', 'style', 'title']
        self.available_wildcard_properties =            []
        _explicit_args = kwargs.pop('_explicit_args')
        _locals = locals()
        _locals.update(kwargs)  # For wildcard attrs and excess named props
        args = {k: _locals[k] for k in _explicit_args if k != 'children'}

        super(DvpCollapse, self).__init__(children=children, **args)

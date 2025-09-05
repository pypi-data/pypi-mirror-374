# AUTO GENERATED FILE - DO NOT EDIT

from dash.development.base_component import Component, _explicitize_args


class DvpMenu(Component):
    """A DvpMenu component.
An Ant Design Menu Component
https://ant.design/components/menu
Adapted form https://github.com/CNFeffery/feffery-antd-components/blob/main/src/lib/components/AntdMenu.react.js

Keyword arguments:

- id (string; optional):
    The ID used to identify this component.

- className (string | dict; optional):
    CSS classes to be added to the component.

- currentKey (string; optional):
    Key of currently the selected menu item.

- defaultOpenKeys (list of strings; optional):
    Array with the keys of default opened sub-menus.

- defaultSelectedKey (string; optional):
    Key of default selected menu item.

- domain (string; optional):
    Domain to complete the url.

- inlineCollapsed (boolean; default False):
    Whether the inline menu is collapsed.

- isSubNav (boolean; default False):
    Whether it is a sub menu.

- isTopNav (boolean; default False):
    Whether it is a top menu.

- key (string; optional):
    Unique ID of the menu item.

- loading_state (dict; optional):
    Loading state.

    `loading_state` is a dict with keys:

    - component_name (string; optional):
        Holds the name of the component that is loading.

    - is_loading (boolean; optional):
        Determines if the component is loading or not.

    - prop_name (string; optional):
        Holds which property is loading.

- menuItems (list; optional):
    Menu items.

- mode (a value equal to: 'vertical', 'horizontal', 'inline'; default 'vertical'):
    Type of menu: vertical | horizontal | inline.

- openKeys (list of strings; optional):
    Array with the keys of currently opened sub-menus.

- persisted_props (list of a value equal to: 'currentKey', 'openKeys's; default ['currentKey', 'openKeys']):
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
    Popup menu.

- renderCollapsedButton (boolean; default False):
    Render collapsed button.

- style (dict; optional):
    Inline CSS style.

- theme (a value equal to: 'light', 'dark'; default 'light'):
    Color theme of the menu: light | dark."""
    _children_props = []
    _base_nodes = ['children']
    _namespace = 'dv_ui_components'
    _type = 'DvpMenu'
    @_explicitize_args
    def __init__(self, id=Component.UNDEFINED, className=Component.UNDEFINED, style=Component.UNDEFINED, key=Component.UNDEFINED, menuItems=Component.UNDEFINED, domain=Component.UNDEFINED, mode=Component.UNDEFINED, theme=Component.UNDEFINED, currentKey=Component.UNDEFINED, openKeys=Component.UNDEFINED, defaultOpenKeys=Component.UNDEFINED, defaultSelectedKey=Component.UNDEFINED, renderCollapsedButton=Component.UNDEFINED, popupContainer=Component.UNDEFINED, inlineCollapsed=Component.UNDEFINED, persistence=Component.UNDEFINED, persisted_props=Component.UNDEFINED, persistence_type=Component.UNDEFINED, isTopNav=Component.UNDEFINED, isSubNav=Component.UNDEFINED, loading_state=Component.UNDEFINED, **kwargs):
        self._prop_names = ['id', 'className', 'currentKey', 'defaultOpenKeys', 'defaultSelectedKey', 'domain', 'inlineCollapsed', 'isSubNav', 'isTopNav', 'key', 'loading_state', 'menuItems', 'mode', 'openKeys', 'persisted_props', 'persistence', 'persistence_type', 'popupContainer', 'renderCollapsedButton', 'style', 'theme']
        self._valid_wildcard_attributes =            []
        self.available_properties = ['id', 'className', 'currentKey', 'defaultOpenKeys', 'defaultSelectedKey', 'domain', 'inlineCollapsed', 'isSubNav', 'isTopNav', 'key', 'loading_state', 'menuItems', 'mode', 'openKeys', 'persisted_props', 'persistence', 'persistence_type', 'popupContainer', 'renderCollapsedButton', 'style', 'theme']
        self.available_wildcard_properties =            []
        _explicit_args = kwargs.pop('_explicit_args')
        _locals = locals()
        _locals.update(kwargs)  # For wildcard attrs and excess named props
        args = {k: _locals[k] for k in _explicit_args}

        super(DvpMenu, self).__init__(**args)

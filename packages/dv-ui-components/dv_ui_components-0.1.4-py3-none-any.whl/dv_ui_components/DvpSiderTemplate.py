# AUTO GENERATED FILE - DO NOT EDIT

from dash.development.base_component import Component, _explicitize_args


class DvpSiderTemplate(Component):
    """A DvpSiderTemplate component.
An Ant Design Sider component
See https://ant.design/components/layout

Keyword arguments:

- children (a list of or a singular dash component, string or number; optional):
    children.

- id (string; optional):
    The ID used to identify this component in Dash callbacks.

- contentStyle (dict; optional):
    CSS style of content container.

- defaultCollapseWidth (number; default 768):
    defaultCollapseWidth.

- footerContent (string; default ''):
    Content of the footer if applicable.

- headerBgColor (string; optional):
    Header Background Color.

- headerContent (a list of or a singular dash component, string or number; optional):
    Children of the header.

- headerJustify (a value equal to: 'start', 'end', 'center', 'space-around', 'space-between'; default 'space-between'):
    Horizontal arrangement of header.

- headerStyle (dict; optional):
    CSS style of header.

- loading_state (dict; optional):
    loading state.

    `loading_state` is a dict with keys:

    - component_name (string; optional):
        Holds the name of the component that is loading.

    - is_loading (boolean; optional):
        Determines if the component is loading or not.

    - prop_name (string; optional):
        Holds which property is loading.

- siderCollapsedWidth (number | string; default 0):
    Width of the collapsed sidebar, by setting to 0 a special trigger
    will appear.

- siderContent (a list of or a singular dash component, string or number; optional):
    children of the sider.

- siderStyle (dict; optional):
    CSS style of sider.

- siderTheme (a value equal to: 'light', 'dark'; default 'light'):
    theme of sider.

- siderWidth (number | string; default 300):
    Width of the sidebar.

- wrapperStyle (dict; default {minHeight: '100vh'}):
    CSS style of wrapper."""
    _children_props = ['headerContent', 'siderContent']
    _base_nodes = ['headerContent', 'siderContent', 'children']
    _namespace = 'dv_ui_components'
    _type = 'DvpSiderTemplate'
    @_explicitize_args
    def __init__(self, children=None, id=Component.UNDEFINED, headerContent=Component.UNDEFINED, headerJustify=Component.UNDEFINED, siderContent=Component.UNDEFINED, siderTheme=Component.UNDEFINED, siderStyle=Component.UNDEFINED, defaultCollapseWidth=Component.UNDEFINED, headerStyle=Component.UNDEFINED, contentStyle=Component.UNDEFINED, wrapperStyle=Component.UNDEFINED, headerBgColor=Component.UNDEFINED, siderCollapsedWidth=Component.UNDEFINED, siderWidth=Component.UNDEFINED, footerContent=Component.UNDEFINED, loading_state=Component.UNDEFINED, **kwargs):
        self._prop_names = ['children', 'id', 'contentStyle', 'defaultCollapseWidth', 'footerContent', 'headerBgColor', 'headerContent', 'headerJustify', 'headerStyle', 'loading_state', 'siderCollapsedWidth', 'siderContent', 'siderStyle', 'siderTheme', 'siderWidth', 'wrapperStyle']
        self._valid_wildcard_attributes =            []
        self.available_properties = ['children', 'id', 'contentStyle', 'defaultCollapseWidth', 'footerContent', 'headerBgColor', 'headerContent', 'headerJustify', 'headerStyle', 'loading_state', 'siderCollapsedWidth', 'siderContent', 'siderStyle', 'siderTheme', 'siderWidth', 'wrapperStyle']
        self.available_wildcard_properties =            []
        _explicit_args = kwargs.pop('_explicit_args')
        _locals = locals()
        _locals.update(kwargs)  # For wildcard attrs and excess named props
        args = {k: _locals[k] for k in _explicit_args if k != 'children'}

        super(DvpSiderTemplate, self).__init__(children=children, **args)

# AUTO GENERATED FILE - DO NOT EDIT

from dash.development.base_component import Component, _explicitize_args


class DvpSider(Component):
    """A DvpSider component.
An Ant Design Sider component
See https://ant.design/components/layout

Keyword arguments:

- children (a list of or a singular dash component, string or number; optional):
    Child components inside the layout.

- id (string; optional):
    The ID used to identify this component.

- backgroundColor (string; optional):
    Background color.

- breakpoint (a value equal to: 'xs', 'sm', 'md', 'lg', 'xl', 'xxl'; optional):
    Breakpoints of the responsive layout.

- className (string; optional):
    CSS classes to be added to the component.

- collapsed (boolean; default False):
    To set the current status.

- collapsedWidth (number; default 0):
    Width of the collapsed sidebar, by setting to 0 a special trigger
    will appear.

- collapsible (boolean; default False):
    Whether can be collapsed.

- defaultCollapsed (boolean; default False):
    To set the initial status.

- isFixed (boolean; optional):
    Whether the sider is fixed.

- offsetTop (number; optional):
    Offset from the top of the viewport (in pixels) if the sider is
    fixed.

- reverseArrow (boolean; default False):
    Reverse direction of arrow, for a sider that expands from the
    right.

- style (dict; optional):
    Inline CSS style.

- theme (a value equal to: 'light', 'dark'; default 'light'):
    Color theme of the sidebar.

- width (number | string; default 300):
    Width of the sidebar."""
    _children_props = []
    _base_nodes = ['children']
    _namespace = 'dv_ui_components'
    _type = 'DvpSider'
    @_explicitize_args
    def __init__(self, children=None, id=Component.UNDEFINED, className=Component.UNDEFINED, backgroundColor=Component.UNDEFINED, style=Component.UNDEFINED, collapsed=Component.UNDEFINED, defaultCollapsed=Component.UNDEFINED, collapsedWidth=Component.UNDEFINED, collapsible=Component.UNDEFINED, reverseArrow=Component.UNDEFINED, theme=Component.UNDEFINED, width=Component.UNDEFINED, breakpoint=Component.UNDEFINED, isFixed=Component.UNDEFINED, offsetTop=Component.UNDEFINED, **kwargs):
        self._prop_names = ['children', 'id', 'backgroundColor', 'breakpoint', 'className', 'collapsed', 'collapsedWidth', 'collapsible', 'defaultCollapsed', 'isFixed', 'offsetTop', 'reverseArrow', 'style', 'theme', 'width']
        self._valid_wildcard_attributes =            []
        self.available_properties = ['children', 'id', 'backgroundColor', 'breakpoint', 'className', 'collapsed', 'collapsedWidth', 'collapsible', 'defaultCollapsed', 'isFixed', 'offsetTop', 'reverseArrow', 'style', 'theme', 'width']
        self.available_wildcard_properties =            []
        _explicit_args = kwargs.pop('_explicit_args')
        _locals = locals()
        _locals.update(kwargs)  # For wildcard attrs and excess named props
        args = {k: _locals[k] for k in _explicit_args if k != 'children'}

        super(DvpSider, self).__init__(children=children, **args)

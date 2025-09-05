# AUTO GENERATED FILE - DO NOT EDIT

from dash.development.base_component import Component, _explicitize_args


class Theme(Component):
    """A Theme component.
An Ant Design ConfigProvider
See https://ant.design/docs/react/customize-theme

Keyword arguments:

- children (a list of or a singular dash component, string or number; optional):
    Child components inside the space.

- colorBgContainer (string; default '#ffffff'):
    Container background color.

- colorBgLayout (string; default '#f0f2f5'):
    Layout background color.

- colorInfo (string; default '#6366f1'):
    Info color.

- colorPrimary (string; default '#6366f1'):
    Primary color.

- colorSuccess (string; default '#13c2b7'):
    Success color.

- colorTextBase (string; default '#424245'):
    Text color.

- colorWarning (string; default '#faad14'):
    Warning color.

- fontFamily (string; default "-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, 'Noto Sans', sans-serif, 'Apple Color Emoji', 'Segoe UI Emoji', 'Segoe UI Symbol', 'Noto Color Emoji'"):
    Font family.

- fontSize (number; default 12):
    Font size.

- wireframe (boolean; default False):
    Wireframe."""
    _children_props = []
    _base_nodes = ['children']
    _namespace = 'dv_ui_components'
    _type = 'Theme'
    @_explicitize_args
    def __init__(self, children=None, colorPrimary=Component.UNDEFINED, colorSuccess=Component.UNDEFINED, colorWarning=Component.UNDEFINED, colorInfo=Component.UNDEFINED, colorTextBase=Component.UNDEFINED, colorBgLayout=Component.UNDEFINED, colorBgContainer=Component.UNDEFINED, fontSize=Component.UNDEFINED, fontFamily=Component.UNDEFINED, wireframe=Component.UNDEFINED, **kwargs):
        self._prop_names = ['children', 'colorBgContainer', 'colorBgLayout', 'colorInfo', 'colorPrimary', 'colorSuccess', 'colorTextBase', 'colorWarning', 'fontFamily', 'fontSize', 'wireframe']
        self._valid_wildcard_attributes =            []
        self.available_properties = ['children', 'colorBgContainer', 'colorBgLayout', 'colorInfo', 'colorPrimary', 'colorSuccess', 'colorTextBase', 'colorWarning', 'fontFamily', 'fontSize', 'wireframe']
        self.available_wildcard_properties =            []
        _explicit_args = kwargs.pop('_explicit_args')
        _locals = locals()
        _locals.update(kwargs)  # For wildcard attrs and excess named props
        args = {k: _locals[k] for k in _explicit_args if k != 'children'}

        super(Theme, self).__init__(children=children, **args)

# AUTO GENERATED FILE - DO NOT EDIT

from dash.development.base_component import Component, _explicitize_args


class DvpTimeline(Component):
    """A DvpTimeline component.
An Ant Design Timeline component
See https://ant.design/components/timeline

Keyword arguments:

- id (string; optional):
    The ID used to identify this component in Dash callbacks.

- className (string | dict; optional):
    CSS classname.

- items (list of dicts; required):
    Items.

    `items` is a list of dicts with keys:

    - color (string; optional):
        Set the circle's color to blue, red, green, gray or other
        custom colors.

    - content (a list of or a singular dash component, string or number; optional):
        Content of the node.

    - icon (string; optional):
        Icon.

    - iconStyle (dict; optional):
        Icon style.

    - label (string | number; optional):
        Label.

    - position (a value equal to: 'left', 'right'; optional):
        Position.

- key (string; optional):
    Key.

- loading_state (dict; optional):
    Loading state.

    `loading_state` is a dict with keys:

    - component_name (string; optional):
        Holds the name of the component that is loading.

    - is_loading (boolean; optional):
        Determines if the component is loading or not.

    - prop_name (string; optional):
        Holds which property is loading.

- mode (a value equal to: 'left', 'alternate', 'right'; default 'left'):
    By sending alternate the timeline will distribute the nodes to the
    left and right.

- pending (a list of or a singular dash component, string or number; optional):
    Set the last ghost node's existence or its content.

- pendingDot (a list of or a singular dash component, string or number; optional):
    Set the dot of the last ghost node when pending is True.

- reverse (boolean; default False):
    Whether reverse nodes or not.

- style (dict; optional):
    CSS style."""
    _children_props = ['items[].content', 'pending', 'pendingDot']
    _base_nodes = ['pending', 'pendingDot', 'children']
    _namespace = 'dv_ui_components'
    _type = 'DvpTimeline'
    @_explicitize_args
    def __init__(self, id=Component.UNDEFINED, className=Component.UNDEFINED, style=Component.UNDEFINED, key=Component.UNDEFINED, items=Component.REQUIRED, mode=Component.UNDEFINED, pending=Component.UNDEFINED, pendingDot=Component.UNDEFINED, reverse=Component.UNDEFINED, loading_state=Component.UNDEFINED, **kwargs):
        self._prop_names = ['id', 'className', 'items', 'key', 'loading_state', 'mode', 'pending', 'pendingDot', 'reverse', 'style']
        self._valid_wildcard_attributes =            []
        self.available_properties = ['id', 'className', 'items', 'key', 'loading_state', 'mode', 'pending', 'pendingDot', 'reverse', 'style']
        self.available_wildcard_properties =            []
        _explicit_args = kwargs.pop('_explicit_args')
        _locals = locals()
        _locals.update(kwargs)  # For wildcard attrs and excess named props
        args = {k: _locals[k] for k in _explicit_args}

        for k in ['items']:
            if k not in args:
                raise TypeError(
                    'Required argument `' + k + '` was not specified.')

        super(DvpTimeline, self).__init__(**args)

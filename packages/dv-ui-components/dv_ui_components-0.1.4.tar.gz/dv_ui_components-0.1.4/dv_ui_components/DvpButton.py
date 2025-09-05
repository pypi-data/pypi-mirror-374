# AUTO GENERATED FILE - DO NOT EDIT

from dash.development.base_component import Component, _explicitize_args


class DvpButton(Component):
    """A DvpButton component.
An Ant Design Button component
See https://ant.design/components/button

Keyword arguments:

- children (a list of or a singular dash component, string or number; optional):
    Content to be displayed on the button.

- id (string | dict; optional):
    The ID used to identify this component in Dash callbacks.

- className (string; optional):
    CSS classes to be added to the component.

- danger (boolean; default False):
    Set the danger status of button.

- debounceWait (number; default 200):
    Used to set the debounce waiting duration (in milliseconds) for
    nClicks listener update; default is 0.

- disabled (boolean; default False):
    Setting whether the button should be rendered as a disabled state,
    default is False.

- href (string; optional):
    href if the button is set to a link.

- icon (a list of or a singular dash component, string or number; optional):
    Embedded icon.

- info (boolean; optional):
    if the button is an info button (blue).

- loading_state (dict; optional):
    Loading state.

    `loading_state` is a dict with keys:

    - component_name (string; optional):
        Holds the name of the component that is loading.

    - is_loading (boolean; optional):
        Determines if the component is loading or not.

    - prop_name (string; optional):
        Holds which property is loading.

- nClicks (number; default 0):
    Recording the number of times the button has been clicked since
    rendering, default is 0.

- pink (boolean; optional):
    if the button is in pink.

- shape (a value equal to: 'circle', 'round'; optional):
    Setting the shape of the button (circle: circle, round: rounded
    rectangle; default is not set, i.e., normal rectangle).

- size (a value equal to: 'small', 'middle', 'large'; default 'small'):
    Setting the size of the button, available options are 'small',
    'middle', and 'large'; default is 'middle'.

- style (dict; optional):
    Inline CSS style.

- success (boolean; default False):
    Set the success status of button, green.

- target (string; default '_blank'):
    target of the link, e.g., \"_blank\".

- type (a value equal to: 'primary', 'ghost', 'dashed', 'link', 'text', 'default'; default 'primary'):
    Setting the overall style of the button (optional options are
    primary, ghost dashed, link, text, default; default is default)."""
    _children_props = ['icon']
    _base_nodes = ['icon', 'children']
    _namespace = 'dv_ui_components'
    _type = 'DvpButton'
    @_explicitize_args
    def __init__(self, children=None, id=Component.UNDEFINED, className=Component.UNDEFINED, style=Component.UNDEFINED, type=Component.UNDEFINED, danger=Component.UNDEFINED, success=Component.UNDEFINED, pink=Component.UNDEFINED, info=Component.UNDEFINED, href=Component.UNDEFINED, target=Component.UNDEFINED, disabled=Component.UNDEFINED, shape=Component.UNDEFINED, size=Component.UNDEFINED, icon=Component.UNDEFINED, nClicks=Component.UNDEFINED, debounceWait=Component.UNDEFINED, loading_state=Component.UNDEFINED, **kwargs):
        self._prop_names = ['children', 'id', 'className', 'danger', 'debounceWait', 'disabled', 'href', 'icon', 'info', 'loading_state', 'nClicks', 'pink', 'shape', 'size', 'style', 'success', 'target', 'type']
        self._valid_wildcard_attributes =            []
        self.available_properties = ['children', 'id', 'className', 'danger', 'debounceWait', 'disabled', 'href', 'icon', 'info', 'loading_state', 'nClicks', 'pink', 'shape', 'size', 'style', 'success', 'target', 'type']
        self.available_wildcard_properties =            []
        _explicit_args = kwargs.pop('_explicit_args')
        _locals = locals()
        _locals.update(kwargs)  # For wildcard attrs and excess named props
        args = {k: _locals[k] for k in _explicit_args if k != 'children'}

        super(DvpButton, self).__init__(children=children, **args)

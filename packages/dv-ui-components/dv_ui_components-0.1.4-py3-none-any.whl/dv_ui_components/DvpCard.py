# AUTO GENERATED FILE - DO NOT EDIT

from dash.development.base_component import Component, _explicitize_args


class DvpCard(Component):
    """A DvpCard component.
An Ant Design Card component
See https://ant.design/components/card

Keyword arguments:

- children (a list of or a singular dash component, string or number; optional):
    Content to be displayed on the card.

- id (string; optional):
    The ID used to identify this component in Dash callbacks.

- bodyStyle (dict; optional):
    Inline CSS style of card body.

- className (string; optional):
    CSS classes to be added to the component.

- coverHeight (number; optional):
    Cover Height.

- coverImgSrc (string; optional):
    Url of the cover image if applicable. The extra link is not
    avaialbe when a cover image is used.

- extraLinkHref (string; optional):
    Extra link to be displayed on the top right corner - href.

- extraLinkStyle (dict; optional):
    Extra link to be displayed on the top right corner - CSS style.

- extraLinkText (string; optional):
    Extra link to be displayed on the top right corner - text. It will
    not be displayed if the title is missing or a cover image is
    enabled.

- headStyle (dict; optional):
    Inline CSS style of card header.

- hoverable (boolean; default False):
    Lift up when hovering card.

- loading_state (dict; optional):
    Loading state.

    `loading_state` is a dict with keys:

    - component_name (string; optional):
        Holds the name of the component that is loading.

    - is_loading (boolean; optional):
        Determines if the component is loading or not.

    - prop_name (string; optional):
        Holds which property is loading.

- metaStyle (dict; default {    fontSize: '0.9rem',    textAlign: 'left',}):
    Meta Style.

- size (a value equal to: 'small', 'default'; default 'small'):
    Size of card. default | small.

- style (dict; optional):
    Inline CSS style.

- theme (a value equal to: 'light', 'dark'; default 'light'):
    Theme.

- title (string | a list of or a singular dash component, string or number; optional):
    Title of the card.

- type (string; optional):
    Card style type, can be set to inner or not set."""
    _children_props = ['title']
    _base_nodes = ['title', 'children']
    _namespace = 'dv_ui_components'
    _type = 'DvpCard'
    @_explicitize_args
    def __init__(self, children=None, id=Component.UNDEFINED, type=Component.UNDEFINED, className=Component.UNDEFINED, style=Component.UNDEFINED, coverHeight=Component.UNDEFINED, headStyle=Component.UNDEFINED, bodyStyle=Component.UNDEFINED, metaStyle=Component.UNDEFINED, size=Component.UNDEFINED, title=Component.UNDEFINED, extraLinkText=Component.UNDEFINED, extraLinkHref=Component.UNDEFINED, extraLinkStyle=Component.UNDEFINED, hoverable=Component.UNDEFINED, coverImgSrc=Component.UNDEFINED, theme=Component.UNDEFINED, loading_state=Component.UNDEFINED, **kwargs):
        self._prop_names = ['children', 'id', 'bodyStyle', 'className', 'coverHeight', 'coverImgSrc', 'extraLinkHref', 'extraLinkStyle', 'extraLinkText', 'headStyle', 'hoverable', 'loading_state', 'metaStyle', 'size', 'style', 'theme', 'title', 'type']
        self._valid_wildcard_attributes =            []
        self.available_properties = ['children', 'id', 'bodyStyle', 'className', 'coverHeight', 'coverImgSrc', 'extraLinkHref', 'extraLinkStyle', 'extraLinkText', 'headStyle', 'hoverable', 'loading_state', 'metaStyle', 'size', 'style', 'theme', 'title', 'type']
        self.available_wildcard_properties =            []
        _explicit_args = kwargs.pop('_explicit_args')
        _locals = locals()
        _locals.update(kwargs)  # For wildcard attrs and excess named props
        args = {k: _locals[k] for k in _explicit_args if k != 'children'}

        super(DvpCard, self).__init__(children=children, **args)

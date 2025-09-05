# AUTO GENERATED FILE - DO NOT EDIT

from dash.development.base_component import Component, _explicitize_args


class DvpBreadcrumb(Component):
    """A DvpBreadcrumb component.
Antd Breadcrumb
https://ant.design/components/breadcrumb

Keyword arguments:

- id (string; optional):
    The ID used to identify this component.

- className (string | dict; optional):
    CSS classes to be added to the component.

- clickedItem (dict; optional):
    Clicked Item.

    `clickedItem` is a dict with keys:

    - itemTitle (string; optional):
        Item title.

    - timestamp (number; optional):
        Timestamp.

- items (list of dicts; optional):
    Items.

    `items` is a list of dicts with keys:

    - href (string; optional):
        URL.

    - icon (string; optional):
        Icon.

    - menuItems (list of dicts; optional):
        Menu items.

        `menuItems` is a list of dicts with keys:

        - disabled (boolean; optional):

            Disabled.

        - href (string; optional):

            URL.

        - icon (string; optional):

            Icon.

        - target (string; optional):

            Target.

        - title (string; optional):

            Title.

    - target (string; optional):
        Target.

    - title (string; optional):
        Title.

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

- separator (a list of or a singular dash component, string or number; default '/'):
    Separator.

- style (dict; optional):
    Inline CSS style."""
    _children_props = ['separator']
    _base_nodes = ['separator', 'children']
    _namespace = 'dv_ui_components'
    _type = 'DvpBreadcrumb'
    @_explicitize_args
    def __init__(self, id=Component.UNDEFINED, className=Component.UNDEFINED, style=Component.UNDEFINED, key=Component.UNDEFINED, items=Component.UNDEFINED, separator=Component.UNDEFINED, clickedItem=Component.UNDEFINED, loading_state=Component.UNDEFINED, **kwargs):
        self._prop_names = ['id', 'className', 'clickedItem', 'items', 'key', 'loading_state', 'separator', 'style']
        self._valid_wildcard_attributes =            []
        self.available_properties = ['id', 'className', 'clickedItem', 'items', 'key', 'loading_state', 'separator', 'style']
        self.available_wildcard_properties =            []
        _explicit_args = kwargs.pop('_explicit_args')
        _locals = locals()
        _locals.update(kwargs)  # For wildcard attrs and excess named props
        args = {k: _locals[k] for k in _explicit_args}

        super(DvpBreadcrumb, self).__init__(**args)

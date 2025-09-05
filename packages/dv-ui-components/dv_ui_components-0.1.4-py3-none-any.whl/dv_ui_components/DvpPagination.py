# AUTO GENERATED FILE - DO NOT EDIT

from dash.development.base_component import Component, _explicitize_args


class DvpPagination(Component):
    """A DvpPagination component.
An Ant Design Pagination component
See https://ant.design/components/pagination

Keyword arguments:

- id (string | dict; optional):
    The ID used to identify this component in Dash callbacks.

- className (string; optional):
    CSS classes to be added to the component.

- current (number; default 1):
    Current page number.

- disabled (boolean; default False):
    Disable pagination.

- hideOnSinglePage (boolean; default True):
    Whether to hide pager on single page.

- key (string; optional):
    Key of the component.

- loading_state (dict; optional):
    Loading state.

    `loading_state` is a dict with keys:

    - component_name (string; optional):
        Holds the name of the component that is loading.

    - is_loading (boolean; optional):
        Determines if the component is loading or not.

    - prop_name (string; optional):
        Holds which property is loading.

- pageSize (number; default 20):
    Number of data items per page.

- persisted_props (list of a value equal to: 'current', 'pageSize's; optional):
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

- persistence_type (a value equal to: 'local', 'session', 'memory'; optional):
    Where persisted user changes will be stored: memory: only kept in
    memory, reset on page refresh. local: window.localStorage, data is
    kept after the browser quit. session: window.sessionStorage, data
    is cleared once the browser quit.

- redirectURL (string; default ''):
    Redirect to page based on onChange if applicable.

- showTotal (boolean; optional):
    Whether to show total items.

- simple (boolean; default False):
    Whether to use simple mode.

- size (a value equal to: 'default', 'small'; default 'default'):
    Specify the size of Pagination, can be set to small.

- style (dict; optional):
    Inline CSS style.

- total (number; optional):
    Total number of data items."""
    _children_props = []
    _base_nodes = ['children']
    _namespace = 'dv_ui_components'
    _type = 'DvpPagination'
    @_explicitize_args
    def __init__(self, key=Component.UNDEFINED, id=Component.UNDEFINED, className=Component.UNDEFINED, style=Component.UNDEFINED, total=Component.UNDEFINED, showTotal=Component.UNDEFINED, pageSize=Component.UNDEFINED, current=Component.UNDEFINED, disabled=Component.UNDEFINED, size=Component.UNDEFINED, simple=Component.UNDEFINED, hideOnSinglePage=Component.UNDEFINED, redirectURL=Component.UNDEFINED, persistence=Component.UNDEFINED, persisted_props=Component.UNDEFINED, persistence_type=Component.UNDEFINED, loading_state=Component.UNDEFINED, **kwargs):
        self._prop_names = ['id', 'className', 'current', 'disabled', 'hideOnSinglePage', 'key', 'loading_state', 'pageSize', 'persisted_props', 'persistence', 'persistence_type', 'redirectURL', 'showTotal', 'simple', 'size', 'style', 'total']
        self._valid_wildcard_attributes =            []
        self.available_properties = ['id', 'className', 'current', 'disabled', 'hideOnSinglePage', 'key', 'loading_state', 'pageSize', 'persisted_props', 'persistence', 'persistence_type', 'redirectURL', 'showTotal', 'simple', 'size', 'style', 'total']
        self.available_wildcard_properties =            []
        _explicit_args = kwargs.pop('_explicit_args')
        _locals = locals()
        _locals.update(kwargs)  # For wildcard attrs and excess named props
        args = {k: _locals[k] for k in _explicit_args}

        super(DvpPagination, self).__init__(**args)

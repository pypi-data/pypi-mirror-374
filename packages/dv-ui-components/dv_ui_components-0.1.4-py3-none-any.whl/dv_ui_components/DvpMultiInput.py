# AUTO GENERATED FILE - DO NOT EDIT

from dash.development.base_component import Component, _explicitize_args


class DvpMultiInput(Component):
    """A DvpMultiInput component.
A customized multi search box

Keyword arguments:

- id (string; optional):
    The ID used to identify this component in Dash callbacks.

- className (string | dict; optional):
    CSS classname.

- defaultValues (list; optional):
    default values.

- key (string; optional):
    Key.

- loading_state (dict; optional):
    loading state.

    `loading_state` is a dict with keys:

    - component_name (string; optional):
        Holds the name of the component that is loading.

    - is_loading (boolean; optional):
        Determines if the component is loading or not.

    - prop_name (string; optional):
        Holds which property is loading.

- maxRowNum (number; default 5):
    Max number of rows.

- nSubmit (number; default 0):
    Record the number of times the submit button is clicked.

- placeholder (string; optional):
    Placeholder in the first row.

- queries (list; optional):
    queries.

- reset (boolean; default False):
    Reset.

- rowItems (a list of or a singular dash component, string or number; optional):
    row items, placeholder.

- style (dict; optional):
    CSS style."""
    _children_props = ['rowItems']
    _base_nodes = ['rowItems', 'children']
    _namespace = 'dv_ui_components'
    _type = 'DvpMultiInput'
    @_explicitize_args
    def __init__(self, id=Component.UNDEFINED, className=Component.UNDEFINED, reset=Component.UNDEFINED, style=Component.UNDEFINED, key=Component.UNDEFINED, defaultValues=Component.UNDEFINED, placeholder=Component.UNDEFINED, rowItems=Component.UNDEFINED, queries=Component.UNDEFINED, nSubmit=Component.UNDEFINED, maxRowNum=Component.UNDEFINED, loading_state=Component.UNDEFINED, **kwargs):
        self._prop_names = ['id', 'className', 'defaultValues', 'key', 'loading_state', 'maxRowNum', 'nSubmit', 'placeholder', 'queries', 'reset', 'rowItems', 'style']
        self._valid_wildcard_attributes =            []
        self.available_properties = ['id', 'className', 'defaultValues', 'key', 'loading_state', 'maxRowNum', 'nSubmit', 'placeholder', 'queries', 'reset', 'rowItems', 'style']
        self.available_wildcard_properties =            []
        _explicit_args = kwargs.pop('_explicit_args')
        _locals = locals()
        _locals.update(kwargs)  # For wildcard attrs and excess named props
        args = {k: _locals[k] for k in _explicit_args}

        super(DvpMultiInput, self).__init__(**args)

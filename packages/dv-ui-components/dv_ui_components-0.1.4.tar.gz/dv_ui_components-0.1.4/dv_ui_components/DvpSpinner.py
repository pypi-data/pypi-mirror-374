# AUTO GENERATED FILE - DO NOT EDIT

from dash.development.base_component import Component, _explicitize_args


class DvpSpinner(Component):
    """A DvpSpinner component.
An Ant Design Spin component
See https://ant.design/components/spin

Keyword arguments:

- children (a list of or a singular dash component, string or number; optional):
    Children.

- id (string; optional):
    The ID used to identify this component in Dash callbacks.

- className (string; optional):
    CSS classes to be added to the component.

- debug (boolean; default False):
    Whether to turn on debug mode.

- delay (number; optional):
    Specifies a delay in milliseconds for loading state (prevent
    flush).

- fullScreen (boolean; optional):
    Whether it is a full-screen spinner.

- includeProps (list of strings; optional):
    Components to listen.

- loading_state (dict; optional):
    Loading state.

    `loading_state` is a dict with keys:

    - component_name (string; optional):
        Holds the name of the component that is loading.

    - is_loading (boolean; optional):
        Determines if the component is loading or not.

    - prop_name (string; optional):
        Holds which property is loading.

- size (a value equal to: 'small', 'middle', 'large'; default 'large'):
    Size The size of Spin, options: small, default and large.

- spinning (boolean; default False):
    Whether Spin is visible.

- style (dict; optional):
    Inline CSS style.

- tip (string; default 'Loading'):
    Customize description content when Spin has children.

- wrapperClassName (string; optional):
    The className of wrapper when Spin has children."""
    _children_props = []
    _base_nodes = ['children']
    _namespace = 'dv_ui_components'
    _type = 'DvpSpinner'
    @_explicitize_args
    def __init__(self, children=None, id=Component.UNDEFINED, className=Component.UNDEFINED, wrapperClassName=Component.UNDEFINED, style=Component.UNDEFINED, tip=Component.UNDEFINED, size=Component.UNDEFINED, spinning=Component.UNDEFINED, delay=Component.UNDEFINED, fullScreen=Component.UNDEFINED, includeProps=Component.UNDEFINED, debug=Component.UNDEFINED, loading_state=Component.UNDEFINED, **kwargs):
        self._prop_names = ['children', 'id', 'className', 'debug', 'delay', 'fullScreen', 'includeProps', 'loading_state', 'size', 'spinning', 'style', 'tip', 'wrapperClassName']
        self._valid_wildcard_attributes =            []
        self.available_properties = ['children', 'id', 'className', 'debug', 'delay', 'fullScreen', 'includeProps', 'loading_state', 'size', 'spinning', 'style', 'tip', 'wrapperClassName']
        self.available_wildcard_properties =            []
        _explicit_args = kwargs.pop('_explicit_args')
        _locals = locals()
        _locals.update(kwargs)  # For wildcard attrs and excess named props
        args = {k: _locals[k] for k in _explicit_args if k != 'children'}

        super(DvpSpinner, self).__init__(children=children, **args)

# AUTO GENERATED FILE - DO NOT EDIT

from dash.development.base_component import Component, _explicitize_args


class DvpFormItem(Component):
    """A DvpFormItem component.
An Ant Design form component
See https://ant.design/components/from
Adapted from feffery-antd-components

Keyword arguments:

- children (a list of or a singular dash component, string or number; optional):
    The content of the tab - will only be displayed if this tab is
    selected.

- id (string; optional):
    The ID used to identify this component in Dash callbacks.

- className (string | dict; optional):
    CSS classname.

- colon (boolean; optional):
    Colon after label.

- extra (a list of or a singular dash component, string or number; optional):
    Extra info.

- help (a list of or a singular dash component, string or number; optional):
    help info.

- hidden (boolean; default False):
    whether hide input.

- key (string; optional):
    Key.

- label (a list of or a singular dash component, string or number; optional):
    Label.

- labelAlign (a value equal to: 'left', 'right'; optional):
    Label alignment.

- labelCol (dict; optional):
    label column.

    `labelCol` is a dict with keys:

    - flex (string | number; optional)

    - offset (number; optional)

    - span (number; optional)

- loading_state (dict; optional):
    loading state.

    `loading_state` is a dict with keys:

    - component_name (string; optional):
        Holds the name of the component that is loading.

    - is_loading (boolean; optional):
        Determines if the component is loading or not.

    - prop_name (string; optional):
        Holds which property is loading.

- required (boolean; default False):
    Whether the input is required.

- style (dict; optional):
    CSS style.

- tooltip (a list of or a singular dash component, string or number; optional):
    Tooltip.

- validateStatus (a value equal to: 'success', 'warning', 'error', 'validating'; optional):
    validation status.

- wrapperCol (dict; optional):
    Wrapper column.

    `wrapperCol` is a dict with keys:

    - flex (string | number; optional)

    - offset (number; optional)

    - span (number; optional)"""
    _children_props = ['label', 'tooltip', 'extra', 'help']
    _base_nodes = ['label', 'tooltip', 'extra', 'help', 'children']
    _namespace = 'dv_ui_components'
    _type = 'DvpFormItem'
    @_explicitize_args
    def __init__(self, children=None, id=Component.UNDEFINED, className=Component.UNDEFINED, style=Component.UNDEFINED, key=Component.UNDEFINED, required=Component.UNDEFINED, labelCol=Component.UNDEFINED, colon=Component.UNDEFINED, wrapperCol=Component.UNDEFINED, label=Component.UNDEFINED, labelAlign=Component.UNDEFINED, tooltip=Component.UNDEFINED, extra=Component.UNDEFINED, validateStatus=Component.UNDEFINED, help=Component.UNDEFINED, hidden=Component.UNDEFINED, loading_state=Component.UNDEFINED, **kwargs):
        self._prop_names = ['children', 'id', 'className', 'colon', 'extra', 'help', 'hidden', 'key', 'label', 'labelAlign', 'labelCol', 'loading_state', 'required', 'style', 'tooltip', 'validateStatus', 'wrapperCol']
        self._valid_wildcard_attributes =            []
        self.available_properties = ['children', 'id', 'className', 'colon', 'extra', 'help', 'hidden', 'key', 'label', 'labelAlign', 'labelCol', 'loading_state', 'required', 'style', 'tooltip', 'validateStatus', 'wrapperCol']
        self.available_wildcard_properties =            []
        _explicit_args = kwargs.pop('_explicit_args')
        _locals = locals()
        _locals.update(kwargs)  # For wildcard attrs and excess named props
        args = {k: _locals[k] for k in _explicit_args if k != 'children'}

        super(DvpFormItem, self).__init__(children=children, **args)

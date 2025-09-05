# AUTO GENERATED FILE - DO NOT EDIT

from dash.development.base_component import Component, _explicitize_args


class DvpEntryForm(Component):
    """A DvpEntryForm component.
An Ant Design From component
See https://ant.design/components/form

Keyword arguments:

- id (string; optional):
    The ID used to identify this component in Dash callbacks.

- buttonPosition (a value equal to: 'start', 'end'; default 'end'):
    Position of button group.

- buttonSize (a value equal to: 'small', 'middle', 'large'; default 'middle'):
    Button size.

- className (string | dict; optional):
    CSS classname.

- includeButtons (boolean; default False):
    Include submit buttons.

- items (list; optional):
    Children in array.

- key (string; optional):
    Key.

- labelCol (dict; optional):
    LabelCol.

    `labelCol` is a dict with keys:

    - flex (string | number; optional)

    - offset (number; optional)

    - span (number; optional)

- labelPosition (a value equal to: 'left', 'top'; optional):
    Label position.

- layout (a value equal to: 'horizontal', 'vertical', 'inline'; optional):
    Layout.

- loading_state (dict; optional):
    loading state.

    `loading_state` is a dict with keys:

    - component_name (string; optional):
        Holds the name of the component that is loading.

    - is_loading (boolean; optional):
        Determines if the component is loading or not.

    - prop_name (string; optional):
        Holds which property is loading.

- nClickReset (number; default 0):
    nClicks to record reset.

- nClickSubmit (number; default 0):
    nClicks to record submit.

- resetURL (string; optional):
    Click reset to redirect if applicable.

- resetValues (dict; optional):
    Default values for reset use.

- style (dict; optional):
    CSS style.

- tagColor (string; default '#f1f3ff'):
    Tag color.

- values (dict; optional):
    Values.

- wrapperCol (dict; optional):
    Wrapper col.

    `wrapperCol` is a dict with keys:

    - flex (string | number; optional)

    - offset (number; optional)

    - span (number; optional)"""
    _children_props = []
    _base_nodes = ['children']
    _namespace = 'dv_ui_components'
    _type = 'DvpEntryForm'
    @_explicitize_args
    def __init__(self, items=Component.UNDEFINED, key=Component.UNDEFINED, id=Component.UNDEFINED, includeButtons=Component.UNDEFINED, className=Component.UNDEFINED, buttonPosition=Component.UNDEFINED, style=Component.UNDEFINED, resetValues=Component.UNDEFINED, values=Component.UNDEFINED, labelPosition=Component.UNDEFINED, labelCol=Component.UNDEFINED, wrapperCol=Component.UNDEFINED, tagColor=Component.UNDEFINED, layout=Component.UNDEFINED, nClickSubmit=Component.UNDEFINED, nClickReset=Component.UNDEFINED, resetURL=Component.UNDEFINED, buttonSize=Component.UNDEFINED, loading_state=Component.UNDEFINED, **kwargs):
        self._prop_names = ['id', 'buttonPosition', 'buttonSize', 'className', 'includeButtons', 'items', 'key', 'labelCol', 'labelPosition', 'layout', 'loading_state', 'nClickReset', 'nClickSubmit', 'resetURL', 'resetValues', 'style', 'tagColor', 'values', 'wrapperCol']
        self._valid_wildcard_attributes =            []
        self.available_properties = ['id', 'buttonPosition', 'buttonSize', 'className', 'includeButtons', 'items', 'key', 'labelCol', 'labelPosition', 'layout', 'loading_state', 'nClickReset', 'nClickSubmit', 'resetURL', 'resetValues', 'style', 'tagColor', 'values', 'wrapperCol']
        self.available_wildcard_properties =            []
        _explicit_args = kwargs.pop('_explicit_args')
        _locals = locals()
        _locals.update(kwargs)  # For wildcard attrs and excess named props
        args = {k: _locals[k] for k in _explicit_args}

        super(DvpEntryForm, self).__init__(**args)

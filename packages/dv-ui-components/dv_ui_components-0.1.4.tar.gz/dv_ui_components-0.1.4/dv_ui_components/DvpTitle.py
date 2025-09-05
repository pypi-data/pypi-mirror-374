# AUTO GENERATED FILE - DO NOT EDIT

from dash.development.base_component import Component, _explicitize_args


class DvpTitle(Component):
    """A DvpTitle component.
An Ant Design Title component
See https://ant.design/components/typography

Keyword arguments:

- children (a list of or a singular dash component, string or number; optional):
    Child components inside the layout.

- id (string; optional):
    The ID used to identify this component.

- className (string; optional):
    CSS classes to be added to the component.

- italic (boolean; optional):
    Sets whether the content should be italic.

- level (number; default 1):
    Sets the level of the title. Possible values are integers between
    1 and 5, corresponding to h1 to h5. Default is 1.

- strikethrough (boolean; optional):
    Sets whether to render the content with strikethrough mode.

- strong (boolean; optional):
    Sets whether the content should be bold.

- style (dict; optional):
    Inline CSS style.

- type (a value equal to: 'secondary', 'success', 'warning', 'danger'; optional):
    Sets the text status type for rendering. Possible options are
    'secondary', 'success', 'warning', and 'danger'. Default is no
    status.

- underline (boolean; optional):
    Sets whether to add underline."""
    _children_props = []
    _base_nodes = ['children']
    _namespace = 'dv_ui_components'
    _type = 'DvpTitle'
    @_explicitize_args
    def __init__(self, children=None, id=Component.UNDEFINED, className=Component.UNDEFINED, style=Component.UNDEFINED, level=Component.UNDEFINED, strikethrough=Component.UNDEFINED, strong=Component.UNDEFINED, italic=Component.UNDEFINED, underline=Component.UNDEFINED, type=Component.UNDEFINED, **kwargs):
        self._prop_names = ['children', 'id', 'className', 'italic', 'level', 'strikethrough', 'strong', 'style', 'type', 'underline']
        self._valid_wildcard_attributes =            []
        self.available_properties = ['children', 'id', 'className', 'italic', 'level', 'strikethrough', 'strong', 'style', 'type', 'underline']
        self.available_wildcard_properties =            []
        _explicit_args = kwargs.pop('_explicit_args')
        _locals = locals()
        _locals.update(kwargs)  # For wildcard attrs and excess named props
        args = {k: _locals[k] for k in _explicit_args if k != 'children'}

        super(DvpTitle, self).__init__(children=children, **args)

# AUTO GENERATED FILE - DO NOT EDIT

from dash.development.base_component import Component, _explicitize_args


class DvpTag(Component):
    """A DvpTag component.
An Ant Design Tag component
See https://ant.design/components/tag

Keyword arguments:

- children (a list of or a singular dash component, string or number; optional):
    Content to be displayed on the tag.

- id (string; optional):
    The ID used to identify this component in Dash callbacks.

- className (string; optional):
    CSS classes to be added to the component.

- color (string; optional):
    Color of the tag.

- href (string; optional):
    href if the tag is set to a link.

- style (dict; optional):
    Inline CSS style.

- target (string; default '_blank'):
    target of the link, e.g., \"_blank\"."""
    _children_props = []
    _base_nodes = ['children']
    _namespace = 'dv_ui_components'
    _type = 'DvpTag'
    @_explicitize_args
    def __init__(self, children=None, id=Component.UNDEFINED, color=Component.UNDEFINED, className=Component.UNDEFINED, style=Component.UNDEFINED, href=Component.UNDEFINED, target=Component.UNDEFINED, **kwargs):
        self._prop_names = ['children', 'id', 'className', 'color', 'href', 'style', 'target']
        self._valid_wildcard_attributes =            []
        self.available_properties = ['children', 'id', 'className', 'color', 'href', 'style', 'target']
        self.available_wildcard_properties =            []
        _explicit_args = kwargs.pop('_explicit_args')
        _locals = locals()
        _locals.update(kwargs)  # For wildcard attrs and excess named props
        args = {k: _locals[k] for k in _explicit_args if k != 'children'}

        super(DvpTag, self).__init__(children=children, **args)

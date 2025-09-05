# AUTO GENERATED FILE - DO NOT EDIT

from dash.development.base_component import Component, _explicitize_args


class DvpSpace(Component):
    """A DvpSpace component.
An Ant Design Space component
See https://ant.design/components/space

Keyword arguments:

- children (a list of or a singular dash component, string or number; optional):
    Child components inside the space.

- id (string; optional):
    The ID used to identify this component in Dash callbacks.

- align (a value equal to: 'start', 'end', 'center', 'baseline'; default 'start'):
    Config item align. start | end |center |baseline.

- className (string; optional):
    CSS classes to be added to the component.

- direction (a value equal to: 'vertical', 'horizontal'; default 'horizontal'):
    The space direction vertical | horizontal.

- size (a value equal to: 'small', 'middle', 'large' | number; default 'small'):
    Space Size, large, middle and small or an integer.

- style (dict; optional):
    Inline CSS style.

- wrap (boolean; default False):
    Auto wrap line, when horizontal effective."""
    _children_props = []
    _base_nodes = ['children']
    _namespace = 'dv_ui_components'
    _type = 'DvpSpace'
    @_explicitize_args
    def __init__(self, children=None, id=Component.UNDEFINED, className=Component.UNDEFINED, style=Component.UNDEFINED, size=Component.UNDEFINED, align=Component.UNDEFINED, direction=Component.UNDEFINED, wrap=Component.UNDEFINED, **kwargs):
        self._prop_names = ['children', 'id', 'align', 'className', 'direction', 'size', 'style', 'wrap']
        self._valid_wildcard_attributes =            []
        self.available_properties = ['children', 'id', 'align', 'className', 'direction', 'size', 'style', 'wrap']
        self.available_wildcard_properties =            []
        _explicit_args = kwargs.pop('_explicit_args')
        _locals = locals()
        _locals.update(kwargs)  # For wildcard attrs and excess named props
        args = {k: _locals[k] for k in _explicit_args if k != 'children'}

        super(DvpSpace, self).__init__(children=children, **args)

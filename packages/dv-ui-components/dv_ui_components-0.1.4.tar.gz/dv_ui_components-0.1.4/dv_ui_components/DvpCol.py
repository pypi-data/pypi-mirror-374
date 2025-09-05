# AUTO GENERATED FILE - DO NOT EDIT

from dash.development.base_component import Component, _explicitize_args


class DvpCol(Component):
    """A DvpCol component.
An Antd Design Col component
https://ant.design/components/grid

Keyword arguments:

- children (a list of or a singular dash component, string or number; optional):
    The content.

- id (string; optional):
    Id of the col.

- className (string | dict; optional):
    CSS classname of the col.

- flex (string | number; optional):
    Flex layout style.

- lg (dict | number; optional):
    screen ≥ 992px, could be a span value or an object containing
    above props.

- md (dict | number; optional):
    screen ≥ 768px, could be a span value or an object containing
    above props.

- offset (number; default 0):
    The number of cells to offset Col from the left.

- order (number; default 0):
    Raster order.

- sm (dict | number; optional):
    screen ≥ 576px, could be a span value or an object containing
    above props.

- span (number; optional):
    Raster number of cells to occupy, 0 corresponds to.

- style (dict; optional):
    CSS style of the col.

- xl (dict | number; optional):
    screen ≥ 1200px, could be a span value or an object containing
    above props.

- xs (dict | number; optional):
    screen < 576px and also default setting, could be a span value or
    an object containing above props.

- xxl (dict | number; optional):
    screen ≥ 1600px, could be a span value or an object containing
    above props."""
    _children_props = []
    _base_nodes = ['children']
    _namespace = 'dv_ui_components'
    _type = 'DvpCol'
    @_explicitize_args
    def __init__(self, children=None, id=Component.UNDEFINED, className=Component.UNDEFINED, style=Component.UNDEFINED, span=Component.UNDEFINED, offset=Component.UNDEFINED, order=Component.UNDEFINED, flex=Component.UNDEFINED, xs=Component.UNDEFINED, sm=Component.UNDEFINED, md=Component.UNDEFINED, lg=Component.UNDEFINED, xl=Component.UNDEFINED, xxl=Component.UNDEFINED, **kwargs):
        self._prop_names = ['children', 'id', 'className', 'flex', 'lg', 'md', 'offset', 'order', 'sm', 'span', 'style', 'xl', 'xs', 'xxl']
        self._valid_wildcard_attributes =            []
        self.available_properties = ['children', 'id', 'className', 'flex', 'lg', 'md', 'offset', 'order', 'sm', 'span', 'style', 'xl', 'xs', 'xxl']
        self.available_wildcard_properties =            []
        _explicit_args = kwargs.pop('_explicit_args')
        _locals = locals()
        _locals.update(kwargs)  # For wildcard attrs and excess named props
        args = {k: _locals[k] for k in _explicit_args if k != 'children'}

        super(DvpCol, self).__init__(children=children, **args)

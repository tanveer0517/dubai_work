# -*- coding: utf-8 -*-
# from odoo import _, api, models, fields
# from odoo.models import BaseModel
from lxml import etree
import itertools


from odoo.models import BaseModel
from odoo import api ,_
from odoo.exceptions import UserError, Warning

_logger = logging.getLogger(__name__)

@api.v8

def new_fields_view_get(self, view_id=None, view_type='form', toolbar=False,
                        submenu=False):

#your code goes here

BaseModel.read = my_read

from openerp import models, api
class BaseModelExtend(models.AbstractModel):
    _name = 'basemodel.extend'

    def _register_hook(self, cr):
        @api.cr_uid_context
        def user_has_groups(self, cr, uid, groups, context=None):
        #My code
        models.BaseModel.user_has_groups = user_has_groups
        return super(BaseModelExtend, self)._register_hook(cr)






@api.model
def new_fields_view_get(self, view_id=None, view_type='form', toolbar=False,
                        submenu=False):
    print ')))))))))))))))))))))))))))))))))))))))))))))'
    """ fields_view_get([view_id | view_type='form'])

    Get the detailed composition of the requested view like fields, model, view architecture

    :param view_id: id of the view or None
    :param view_type: type of the view to return if view_id is None ('form', 'tree', ...)
    :param toolbar: true to include contextual actions
    :param submenu: deprecated
    :return: dictionary describing the composition of the requested view (including inherited views and extensions)
    :raise AttributeError:
                        * if the inherited view has unknown position to work with other than 'before', 'after', 'inside', 'replace'
                        * if some tag other than 'position' is found in parent view
    :raise Invalid ArchitectureError: if there is view type other than form, tree, calendar, search etc defined on the structure
    """
    View = self.env['ir.ui.view']

    result = {
        'model': self._name,
        'field_parent': False,
    }

    # try to find a view_id if none provided
    if not view_id:
        # <view_type>_view_ref in context can be used to overrride the default view
        view_ref_key = view_type + '_view_ref'
        view_ref = self._context.get(view_ref_key)
        if view_ref:
            if '.' in view_ref:
                module, view_ref = view_ref.split('.', 1)
                query = "SELECT res_id FROM ir_model_data WHERE model='ir.ui.view' AND module=%s AND name=%s"
                self._cr.execute(query, (module, view_ref))
                view_ref_res = self._cr.fetchone()
                if view_ref_res:
                    view_id = view_ref_res[0]
            else:
                _logger.warning(
                    '%r requires a fully-qualified external id (got: %r for model %s). '
                    'Please use the complete `module.view_id` form instead.',
                    view_ref_key, view_ref,
                    self._name)

        if not view_id:
            # otherwise try to find the lowest priority matching ir.ui.view
            view_id = View.default_view(self._name, view_type)

    # context for post-processing might be overriden
    if view_id:
        # read the view with inherited views applied
        root_view = View.browse(view_id).read_combined(
            ['id', 'name', 'field_parent', 'type', 'model', 'arch'])
        result['arch'] = root_view['arch']
        result['name'] = root_view['name']
        result['type'] = root_view['type']
        result['view_id'] = root_view['id']
        result['field_parent'] = root_view['field_parent']
        # override context from postprocessing
        if root_view['model'] != self._name:
            View = View.with_context(base_model_name=root_view['model'])
    else:
        # fallback on default views methods if no ir.ui.view could be found
        try:
            arch_etree = getattr(self, '_get_default_%s_view' % view_type)()
            result['arch'] = etree.tostring(arch_etree, encoding='utf-8')
            result['type'] = view_type
            result['name'] = 'default'
        except AttributeError:
            raise UserError(
                _("No default view of type '%s' could be found !") % view_type)

    # Apply post processing, groups and modifiers etc...
    xarch, xfields = View.postprocess_and_fields(self._name, etree.fromstring(
        result['arch']), view_id)
    result['arch'] = xarch
    result['fields'] = xfields

    # Add related action information if aksed
    if toolbar:
        toclean = (
            'report_sxw_content', 'report_rml_content', 'report_sxw', 'report_rml',
            'report_sxw_content_data', 'report_rml_content_data')

        def clean(x):
            x = x[2]
            for key in toclean:
                x.pop(key, None)
            return x

        IrValues = self.env['ir.values']
        resprint = IrValues.get_actions('client_print_multi', self._name)
        resaction = IrValues.get_actions('client_action_multi', self._name)
        resrelate = IrValues.get_actions('client_action_relate', self._name)
        resprint = [clean(print_)
                    for print_ in resprint
                    if view_type == 'tree' or not print_[2].get('multi')]
        resaction = [clean(action)
                     for action in resaction
                     if view_type == 'tree' or not action[2].get('multi')]
        # When multi="True" set it will display only in More of the list view
        resrelate = [clean(action)
                     for action in resrelate
                     if (action[2].get('multi') and view_type == 'tree') or (
                         not action[2].get('multi') and view_type == 'form')]

        for x in itertools.chain(resprint, resaction, resrelate):
            x['string'] = x['name']

        result['toolbar'] = {
            'print': resprint,
            'action': resaction,
            'relate': resrelate,
        }
    return result

BaseModel.fields_view_get = new_fields_view_get

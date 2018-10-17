# -*- coding: utf-8 -*-


def uninstall_hook(cr, registry):
    cr.execute("""SELECT id FROM ir_act_window
               WHERE res_model = 'mass.editing.wizard'""")
    for res in cr.dictfetchall():
        value = 'ir.actions.act_window,%s' % res.get('id')
        cr.execute("DELETE FROM ir_values WHERE value = %s", (value, ))
    return True

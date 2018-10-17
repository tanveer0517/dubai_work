# -*- coding: utf-8 -*-
import MySQLdb
import requests
import logging
_logger = logging.getLogger(__name__)


from odoo import models, fields, api, _
from odoo.exceptions import Warning, except_orm, UserError
from unidecode import unidecode


class Update_WP_Database(models.Model):
    _name = 'update.wp_db'

    @api.multi
    def create_update_data(self, rec = False, result= False, unlink=False):
        try:
            connection = self.get_mysql_connection_data()
            if not connection:
                return True
            db_con, cur = self.get_db_connection(connection)
            if not (db_con or cur):
                return True
            table = False
            table_name = False
            feature_ids = []
            list_ids = []
            if not (rec and result):
                return True
            if result and result[0].keys()[0] == 'feature_id' and result[
                0].keys()[1] == \
                    'list_id':
                for res in result:
                    list_ids.append(res.values()[1])
                table = 'feature_list_rel'
            if result and result[0].keys()[0] == 'feature_id' and result[
                0].keys()[1] == \
                    'server_id':
                for res in result:
                    feature_ids.append(res.values()[0])
                table = 'server_feature_rel'
            rec_ids = rec.ids or False
            if rec_ids and not table:
                table_name = (rec._name).replace('.', '_')
            if rec_ids and result and not unlink:
                try:
                    columns = False
                    values_num = False
                    values_list = []
                    for rec in result:
                        if 'create_date' in rec :
                            rec.pop('create_date', None)
                        if 'write_date' in rec :
                            rec.pop('write_date', None)
                        if not (columns and values_num):
                            keys = rec.keys()
                            values_num = '%s, '*len(keys)
                            values_num = values_num[:-2]
                            columns = ', '.join(keys)
                        list_values = rec.values()
                        values = [str(x) if isinstance(x,unicode) else x for x in
                                  list_values]
                        values_list.append(values)
                    rec_ids = tuple(rec_ids)
                    if len(list_ids) == 1 or len(feature_ids) == 1 or \
                                    len(rec_ids) == 1:
                        operator = "="
                        new_rec_ids = rec_ids[0]
                    if len(list_ids) > 1 or len(feature_ids) > 1 or \
                                    len(rec_ids) > 1:
                        operator = "in"
                        new_rec_ids = str(rec_ids)
                    if table_name and rec_ids:
                        query = "SELECT * FROM " + table_name + " where id " + operator + " %s" % new_rec_ids
                        wp_rec = cur.execute(query)
                        if wp_rec == 0 :
                            self.insert_data(db_con, cur, table_name, columns,
                                             values_num,
                                             values_list)
                        if wp_rec >= 1 :
                            self.delete_data(db_con, cur, table_name, rec_ids)
                            self.insert_data(db_con, cur, table_name, columns,
                                             values_num, values_list)
                    if table and list_ids:
                        if len(list_ids) > 1:
                            new_list_ids = str(tuple(list_ids))
                        if len(list_ids) == 1:
                            new_list_ids = list_ids[0]
                        query = "SELECT * FROM " + table + " where  list_id " + \
                                operator + " %s" % new_list_ids
                        wp_rec = cur.execute(query)
                        if wp_rec == 0 :
                            self.insert_data(db_con, cur, table, columns,
                                             values_num, values_list)
                        if wp_rec >= 1 :
                            self.delete_data(db_con, cur, table, rec_ids, list_ids)
                            self.insert_data(db_con, cur, table, columns,
                                             values_num, values_list)
                    if table and feature_ids:
                        if len(feature_ids) > 1:
                            new_feature_ids = str(tuple(feature_ids))
                        if len(feature_ids) == 1:
                            new_feature_ids = list_ids[0]
                        query = "SELECT * FROM " + table + " where  feature_id " \
                                + operator + " %s" % new_feature_ids
                        wp_rec = cur.execute(query)
                        if wp_rec == 0:
                            self.insert_data(db_con, cur, table, columns, values_num,
                                             values_list)
                        if wp_rec >= 1:
                            self.delete_data(db_con, cur, table , rec_ids, feature_ids)
                            self.insert_data(db_con, cur, table, columns, values_num,
                                             values_list)
                    return
                except Exception as e:
                    _logger.warning(
                        "Something went Wrong in inserting data in WP")
                    raise UserError(_("Error:\n %s")% (e))
            if unlink and rec_ids:
                if table_name:
                    self.delete_data(db_con, cur, table_name, rec_ids)
                if table and list_ids:
                    self.delete_data(db_con, cur, table, rec_ids, list_ids)
                if table and feature_ids:
                    self.delete_data(db_con, cur, table, rec_ids, feature_ids)
                return
            return
        except Exception as e :
            _logger.warning(
                "Something went wrong in creating or updating data in WP")
            raise UserError(_("Error : %s") % (e))

    @api.multi
    def get_db_connection(self, connection=False):
        try:
            db_con = MySQLdb.connect(host = connection.host,
                                     port = connection.port,
                                     user = connection.user,
                                     passwd = connection.password,
                                     db = connection.db)
            cur = db_con.cursor()
            return db_con, cur
        except:
            _logger.warning(
                "Connection not establish or something wrong in "
                "MySQL Connection------------------------------")
            return False, False

    @api.multi
    def get_mysql_connection_data(self) :
        wp_obj = self.env['wp_connection.config']
        record = wp_obj.search([('con_active', '=', True)], limit=1)
        return record

    @api.multi
    def insert_data(self, db_con = False, cur = False, table_name = False,
                    columns = False, values_num = False, values_list = False):
        if cur and table_name and columns and values_num:
            query = "INSERT INTO " + table_name + " (" + columns + ") VALUES (" + values_num + ")"
            if len(values_list) == 1 :
                res = cur.execute(query, values_list[0])
            if len(values_list) > 1:
                new_values = []
                for rec in values_list:
                    new_values.append(tuple(rec))
                res = cur.executemany(query, new_values)
            db_con.commit()
            return True

    @api.multi
    def delete_data(self, db_con = False, cur = False, table_name = False,
                    rec_ids = False, child_ids = False) :
        if table_name and not child_ids:
            if len(rec_ids) == 1:
                rec_ids = tuple(rec_ids)
                query = "DELETE FROM " + table_name + " WHERE id = %s"
                res = cur.execute(query % rec_ids)
            if len(rec_ids) > 1:
                rec_ids = str(tuple(rec_ids))
                query = "DELETE FROM " + table_name + " WHERE id in %s"
                res = cur.execute(query % rec_ids)
        if table_name and child_ids:
            if table_name == 'feature_list_rel' :
                query_form = "DELETE FROM " + table_name + " WHERE list_id "
            if table_name == 'server_feature_rel' :
                query_form = "DELETE FROM " + table_name + " WHERE feature_id "
            if len(child_ids) == 1:
                child_ids = tuple(child_ids)
                query = query_form + " = %s"
                res = cur.execute(query % child_ids)
            if len(child_ids) > 1:
                child_ids = str(tuple(child_ids))
                query = query_form  + " in %s"
                res = cur.execute(query % child_ids)
        db_con.commit()
        return True


class WP_Connection_Config(models.Model):
    _name = 'wp_connection.config'
    _inherit = 'update.wp_db'

    @api.multi
    @api.constrains('con_active')
    def check_connection_validation(self) :
        # Check if more then one active connection is there then raise
        for rec in self :
            check_active_rec = rec.search_count([('con_active', '=', True)])
            if check_active_rec > 1 :
                raise Warning(_('You Cannot have more then 1 '
                                'Active MySQL db Connections. '
                                'Uncheck Active field in another Connection '
                                'Record if you want to make this '
                                'Connection Active.'))

    name = fields.Char('Name', required=True)
    host = fields.Char('Host', required='True', help="""Enter the Host name 
        of your Wordpress that is Server-IP. Hit the 'Test Connection' 
        button to test whether the connection is successful or not. 
        If you are sure that the details are entered correctly then no need.
        """)
    port = fields.Integer('Port', default=3306, required=True,
                          help="""Provide Port number of your PhpMyAdmin 
                          where you have kept.""")
    user = fields.Char('Database User', required=True, help="""PhpMyAdmin 
        db User name required in this field""")
    password = fields.Char('Database Password', required=True,
                           help="""PhpMyAdmin db password required for this 
                           field
                           """)
    db = fields.Char('DB', required=True,
                     help="""Enter the PhpMyAdmin DB Name""")
    connection = fields.Selection([
        ('successfull', 'Successfull'), ('unsuccessfull', 'Un-Successfull')
    ], string='Connection Status')
    con_active = fields.Boolean('Active', default=True, help=""" You can 
    keep this checked if you want to make this connection active. Only one 
    connection can be active.""")

    @api.one
    def test_host(self):
        try:
            host = self.host
            has_http = host.startswith('http://')
            has_https = host.startswith('https://')
            if host and not (has_https or has_http):
                host = 'http://' + host
            response = requests.get(host)
            connection = self
            self.get_db_connection(connection)
        except Exception as e :
            self.update_query('unsuccessfull')
            raise UserError(_(
                "Connection Test Failed! Here is what we got instead:\n %s") % (
                                e))

        if response.status_code == 200 :
            self.update_query('successfull')
            raise Warning(_('Connection Test Successful.'))
        else :
            self.update_query('unsuccessfull')
            raise Warning(_("Connection Test UnSuccessful. WE got this "
                            "response '%s'") % (response.status_code))

    @api.one
    def update_query(self, status=False):
        if status:
            query = """update wp_connection_config set connection = 
                        '%s' where id = %s""" % (status,self.id)
            self.env.cr.execute(query)
            self.env.cr.commit()
            return

    @api.multi
    def get_db_connection(self, connection = False) :
        db_con = MySQLdb.connect(host = connection.host,
                                 port = connection.port,
                                 user = connection.user,
                                 passwd = connection.password,
                                 db = connection.db)
        cur = db_con.cursor()
        return db_con, cur

    @api.multi
    def get_mysql_connection_data(self) :
        wp_obj = self.env['wp_connection.config']
        record = wp_obj.search([('con_active', '=', True)], limit = 1)
        return record

    @api.multi
    def sync_data_to_mysql(self):
        context = self.env.context
        model_name = str(context.get('table_name'))
        table_name = model_name.replace('.', '_')
        conn = self
        if conn.con_active and conn.connection == 'successfull':
            db_con, cur = self.get_db_connection(conn)
            if not (db_con or cur) :
                _logger.warning(
                    "Connection not establish or something wrong in "
                    "MySQL Connection------------------------------")
                return True

            if model_name == 'saas_portal.server':
                try:
                    saas_portal_server_table_name = table_name
                    server_feature_rel_table_name = 'server_feature_rel'
                    server_feature_description_table_name = 'saas_portal_feature_description'

                    # ========Delete the existing data from MySQL table ==============
                    self.delete_data_from_table(server_feature_description_table_name, db_con, cur)
                    self.delete_data_from_table(saas_portal_server_table_name, db_con, cur)
                    self.delete_data_from_table(server_feature_rel_table_name, db_con, cur)

                    # =======Get all recordset for a particular model ================
                    portal_server_rec = self.env[model_name].sudo().search([])
                    server_feature_description = self.env['saas_portal.feature_description'].sudo().search([])

                    # ========Query to fetch the data in Array format ===============
                    query_portal_server = """select id, server_name, name, create_uid, 
                    write_uid, active, description, terms_conditons, short_desc,
                    server_image, server_image_icon 
                    from saas_portal_server"""
                    query_server_feature_desc = 'select * from saas_portal_feature_description'
                    query_server_feature_rel = 'select * from server_feature_rel'

                    # =====Execute the query and get data and send to MySQL to
                    # create Data there ====================
                    self.env.cr.execute(query_portal_server)
                    query_portal_server_data = self._cr.dictfetchall()
                    for rec in query_portal_server_data :
                        description = unidecode(rec.get('description'))
                        terms_and_conditions = unidecode(rec.get('terms_conditons'))
                        rec.update({
                            'description' : description,
                            'terms_conditons' : terms_and_conditions,
                        })
                    self.create_update_data(portal_server_rec, query_portal_server_data)

                    self.env.cr.execute(query_server_feature_desc)
                    query_server_feature_desc_data = self._cr.dictfetchall()
                    self.create_update_data(server_feature_description, query_server_feature_desc_data)

                    self.env.cr.execute(query_server_feature_rel)
                    query_server_feature_rel_data = self._cr.dictfetchall()
                    self.create_update_data(portal_server_rec, query_server_feature_rel_data)

                    return True
                except:
                    _logger.warning('========Something went wrong while syncing '
                                    'Server Data into MySQL ===================')
                    return True
            elif model_name == 'saas_portal.plan':
                try:
                    saas_portal_plan_table_name = table_name
                    plan_feature_table_name = 'plan_features_master'
                    plan_feature_list_table_name = 'plan_feature_list'

                    # ========Delete the existing data from MySQL table ==============
                    self.delete_data_from_table(saas_portal_plan_table_name, db_con, cur)
                    self.delete_data_from_table(plan_feature_table_name, db_con, cur)
                    self.delete_data_from_table(plan_feature_list_table_name, db_con, cur)

                    # =======Get all recordset for a particular model ================
                    plan_feature_list_rec = self.env['plan.feature.list'].sudo().search([])
                    plan_feature_rec = self.env['plan.features.master'].sudo().search([])
                    portal_plan_rec = self.env[model_name].sudo().search([])

                    # ========Query to fetch the data in Array format ===============
                    query_plan_feature_list = """select id, name, plan_feature_id, 
                                pfeature_list_id, checked, is_there, description,
                                write_uid, create_uid from plan_feature_list"""
                    query_plan_feature_master =  """select *
                                   from plan_features_master"""
                    query_portal_plan = """select id, sequence,plan_price, name, 
                    create_uid, write_uid, server_id, state, website_description, 
                    summary, total_storage_limit, plan_type, sub_period, 
                    recurring_rule_type, button_text, active from 
                    saas_portal_plan"""

                    # =====Execute the query and get data and send to MySQL to
                    # create Data there ====================
                    self.env.cr.execute(query_portal_plan)
                    query_portal_plan_data = self._cr.dictfetchall()
                    for rec in query_portal_plan_data:
                        button_text = str(rec.get('button_text'))
                        if button_text == 'select_plan' :
                            rec['button_text'] = 'Select Plan'
                        if button_text == 'select_free_trial' :
                            rec['button_text'] = 'Select Free Trial'
                    self.create_update_data(portal_plan_rec, query_portal_plan_data)

                    self.env.cr.execute(query_plan_feature_master)
                    query_plan_feature_master_data = self._cr.dictfetchall()
                    self.create_update_data(plan_feature_rec, query_plan_feature_master_data)

                    self.env.cr.execute(query_plan_feature_list)
                    query_plan_feature_list_data = self._cr.dictfetchall()
                    for rec in query_plan_feature_list_data:
                        rec['checked'] = str(rec.get('checked'))
                    self.create_update_data(plan_feature_list_rec, query_plan_feature_list_data)

                    return True
                except:
                    _logger.warning('========Something went wrong while syncing '
                                    'PLan Data into MySQL ===================')
                    return True
            elif model_name == 'saas_portal.server.features':
                try:
                    feature_child_table_name = 'server_feature_list'
                    feature_master_table_name = table_name
                    feature_list_rel_table_name = 'feature_list_rel'
                    # ========Delete the existing data from MySQL table ==============
                    self.delete_data_from_table(feature_child_table_name, db_con, cur)
                    self.delete_data_from_table(feature_master_table_name, db_con, cur)
                    self.delete_data_from_table(feature_list_rel_table_name, db_con, cur)

                    # =======Get all recordset for a particular model ================
                    server_feature_list_rec = self.env['server.feature.list'].sudo().search([])
                    server_feature_rec = self.env[model_name].sudo().search([])
                    # feature_list_rel_rec = self.env['feature.list.rel'].sudo().search([])

                    # ========Query to fetch the data in Array format ===============
                    query_feature_list = 'select * from server_feature_list'
                    query_feature_master = 'select * from saas_portal_server_features'
                    query_feature_list_rel = 'select * from feature_list_rel'

                    # =====Execute the query and get data and send to MySQL to
                    # create Data there ====================
                    self.env.cr.execute(query_feature_list)
                    query_feature_list_data = self._cr.dictfetchall()
                    self.create_update_data(server_feature_list_rec, query_feature_list_data)

                    self.env.cr.execute(query_feature_master)
                    query_feature_master_data = self._cr.dictfetchall()
                    self.create_update_data(server_feature_rec, query_feature_master_data)

                    self.env.cr.execute(query_feature_list_rel)
                    query_feature_list_rel_data = self._cr.dictfetchall()
                    self.create_update_data(server_feature_rec, query_feature_list_rel_data)

                    return True
                except:
                    _logger.warning('========Something went wrong while syncing '
                                    'Feature master Data into MySQL '
                                    '===================')
                    return True
            elif model_name == 'business.type':
                try:
                    self.delete_data_from_table(table_name, db_con, cur)
                    rec = self.env[model_name].sudo().search([])
                    query = 'select id, name, active from business_type'
                    self.env.cr.execute(query)
                    business_master_data = self._cr.dictfetchall()
                    self.create_update_data(rec, business_master_data)
                    return  True
                except:
                    _logger.warning('========Something went wrong while syncing '
                                    'Business Type Data into MySQL '
                                    '===================')
                    return True
            elif model_name == 'res.bank':
                try:
                    self.delete_data_from_table(table_name, db_con, cur)
                    rec = self.env[model_name].sudo().search([])
                    query = 'select id, name, bic, active from res_bank'
                    self.env.cr.execute(query)
                    res_bank_data = self._cr.dictfetchall()
                    self.create_update_data(rec, res_bank_data)
                    return True
                except:
                    _logger.warning('========Something went wrong while syncing '
                                    'Bank Data into MySQL ===================')
                    return True
            else:
                _logger.warning("No Table Name Found ----------")
                return True
        else:
            _logger.warning(
                "Connection not establish ------------------------------")
            return True

    @api.multi
    def delete_data_from_table(self, table_name = False, db_con = False,
                               cur = False):
        try :
            if table_name and db_con and cur:
                query_form = "DELETE FROM " + table_name
                res = cur.execute(query_form)
                db_con.commit()
            else:
                _logger.warning(
                    "Table name not found or connection is not successfull or "
                    "not active")
            return True
        except:
            _logger.warning("-----------Something went wrong in deleting the "
                            "data from MySQL DB-----------------")

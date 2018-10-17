# -*- coding: utf-8 -*-
{
    'name': "saas_server_backup_ftp",
    'author': "Bista Solutions",
    'license': 'GPL-3',
    'category': 'SaaS',
    "support": "support@bistasolutions.com",
    'website': 'http://www.bistasolutions.com',
    'category': 'SaaS',
    'version': '1.0.0',
    'depends': ['saas_server'],
    "external_dependencies": {"python": ['pysftp'], "bin": []},
    'data': [
        'views/res_config.xml',
        'data/ir_cron.xml',
    ],
}

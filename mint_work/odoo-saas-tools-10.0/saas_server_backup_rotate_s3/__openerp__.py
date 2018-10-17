# -*- coding: utf-8 -*-
{
    'name': 'SaaS Server Rotate Backup S3',
    'version': '1.0.0',
    'author': 'Bista Solutions',
    'license': 'GPL-3',
    'category': 'SaaS',
    "support": "support@bistasolutions.com",
    'website': 'http://www.bistasolutions.com',
    'depends': ['saas_server', 'saas_server_backup_s3', 'saas_server_backup_rotate'],
    "external_dependencies": {"python": ['boto', 'rotate_backups_s3'], "bin": []},
    'data': [
    ],
    'installable': True,
}

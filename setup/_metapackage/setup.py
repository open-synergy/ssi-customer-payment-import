import setuptools

with open('VERSION.txt', 'r') as f:
    version = f.read().strip()

setuptools.setup(
    name="odoo14-addons-open-synergy-ssi-customer-payment-import",
    description="Meta package for open-synergy-ssi-customer-payment-import Odoo addons",
    version=version,
    install_requires=[
        'odoo14-addon-ssi_customer_payment_import',
        'odoo14-addon-ssi_customer_payment_import_operating_unit',
        'odoo14-addon-ssi_customer_payment_import_partner_identification',
    ],
    classifiers=[
        'Programming Language :: Python',
        'Framework :: Odoo',
        'Framework :: Odoo :: 14.0',
    ]
)

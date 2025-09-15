import setuptools

with open('VERSION.txt', 'r') as f:
    version = f.read().strip()

setuptools.setup(
    name="odoo14-addons-oca-crowdfunding",
    description="Meta package for oca-crowdfunding Odoo addons",
    version=version,
    install_requires=[
        'odoo14-addon-crowdfunding',
        'odoo14-addon-crowdfunding_claim',
        'odoo14-addon-crowdfunding_demo',
    ],
    classifiers=[
        'Programming Language :: Python',
        'Framework :: Odoo',
        'Framework :: Odoo :: 14.0',
    ]
)

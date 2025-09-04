{
    "version": "16.0.1.0.0",
    "name": "La Directa",
    "summary": """
    """,
    "depends": [
        "contacts",
        "contract",
        "api_common_base",
        "base_rest_datamodel",
    ],
    "author": """
        Coopdevs Treball SCCL,
    """,
    "category": "Shipments management",
    "website": "https://git.coopdevs.org/talaios/addons/odoo-directa#",
    "license": "AGPL-3",
    "data": [
        "views/contract.xml",
        "views/correos_shipment_code.xml",
        "views/product_template.xml",
        "views/res_company.xml",
        "views/res_partner.xml",
        "wizards/print_shipment_tags/print_shipment_tags.xml",
        "reports/shipment_tag.xml",
        "security/ir.model.access.csv",
    ],
    "demo": [],
    "application": False,
    "installable": True,
}

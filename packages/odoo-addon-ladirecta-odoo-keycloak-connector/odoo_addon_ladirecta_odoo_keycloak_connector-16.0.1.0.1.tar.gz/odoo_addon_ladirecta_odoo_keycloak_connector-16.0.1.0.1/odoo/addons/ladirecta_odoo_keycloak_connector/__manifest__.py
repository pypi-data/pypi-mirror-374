{
    "version": "16.0.1.0.1",
    "name": "La Directa Keycloak Connector",
    "summary": """
    """,
    "depends": [
        "component_event",
        "contract",
    ],
    "author": """
        Coopdevs Treball SCCL,
    """,
    "category": "SSO integration",
    "website": "https://git.coopdevs.org/talaios/addons/odoo-directa#",
    "license": "AGPL-3",
    "data": [
        "views/res_company.xml",
    ],
    "external_dependencies": {"python": ["python-keycloak"]},
    "demo": [],
    "application": False,
    "installable": True,
}

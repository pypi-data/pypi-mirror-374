# Copyright 2018 ACSONE SA/NV
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

{
    "name": "Graphql Base",
    "summary": """
        Base GraphQL/GraphiQL controller""",
    "version": "16.0.1.0.2",
    "license": "LGPL-3",
    "author": "ACSONE SA/NV,Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/rest-framework",
    "depends": ["base"],
    "data": ["views/graphiql.xml"],
    # We place an upper bound on graphql-server because it has undergone a major
    # change in 3.0.0b8 in Aug 2025. When graphql-server 3 has stabilized we'll need
    # to update this module to make it compatible with it.
    "external_dependencies": {"python": ["graphene", "graphql-server<3.0.0b8"]},
    "development_status": "Production/Stable",
    "maintainers": ["sbidoul"],
    "installable": True,
}

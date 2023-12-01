from flask import Blueprint, jsonify
from ..dao.organizations_dao import OrganizationsDao

bp = Blueprint('organizations', __name__, url_prefix='/organizations')

@bp.route('', methods=['GET'])
def get_organizations():
    organization_dao = OrganizationsDao()
    organizations = organization_dao.find_all()

    return jsonify(organizations)

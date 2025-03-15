
from flask import jsonify, request
from app import app
from models import Domains
from app import db
from datetime import datetime


@app.route('/<did>', methods=['DELETE'])
def delete_domain(did):
    domain = Domains.query.filter(Domains.id == did).first()
    if domain is None:
        return jsonify({'error': 'Not found'}), 404
    
    db.session.delete(domain)
    db.session.commit()
    return jsonify({'done': True, 'message': f'{domain.domain_name} deleted successfully!'})


@app.route('/<domain_name>', methods=['PUT'])
def update_domain(domain_name):
    domain = Domains.query.filter(Domains.domain_name == domain_name).one_or_404()

    data = request.json
    # domain_name = data.get('domain_name')
    domain.price = data.get('price') or domain.price
    domain.status = data.get('status') or domain.status

    new_date = data.get('expiry_date')
    if new_date is not None:
        domain.expiry_date =  datetime.strptime(new_date, "%Y/%m/%d")

    db.session.commit()
    return jsonify({'done': True, 'message': f'{domain_name} updated successfully.'})


@app.route('/<domain_name>')
def get_domain(domain_name):
    domain = Domains.query.filter(Domains.domain_name == domain_name).first()
    
    if domain is None:
        return jsonify({'error': 'Not found'}), 404
    
    domain_data = {
        "id": domain.id,
        "domain_name": domain.domain_name,
        "reg_date": domain.registration_date,
        "expiry_date": domain.expiry_date,
        "price": domain.price,
        "status": domain.status
    }
    return jsonify(domain_data)


@app.route('/')
def list_domains():
    domains = Domains.query.all()
    amount_of_domains = Domains.query.count()
    all_domains = []
    for item in domains:
        domain_data = {
            "id": item.id,
            "domain_name": item.domain_name,
            "reg_date": item.registration_date,
            "expiry_date": item.expiry_date,
            "price": item.price,
            "status": item.status
        }
        all_domains.append(domain_data)
    
    return jsonify({'total':amount_of_domains, 'domains': all_domains})


@app.route('/register', methods=['POST'])
def register_domain():
    data = request.json
    domain_name = data.get('domain_name')
    price = data['price']
    expiry_date = data.get('expiry_date')
    status = data.get('status')

    if domain_name is None or price is None or price is None or status is None:
        return jsonify({'done': False, 'message': 'All fields are required'}), 400
    
    # format date
    ex_date = datetime.strptime(expiry_date, "%Y/%m/%d")
    
    new_domain = Domains(domain_name=domain_name, price=price, 
                         expiry_date=ex_date, status=status)
    db.session.add(new_domain)
    db.session.commit()

    return jsonify({'done': True, 'message': 'Domain name registered successfully.'}), 200

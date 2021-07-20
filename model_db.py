from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import json
from flask import Flask, request

app = Flask(__name__)
DB_URL = 'postgresql://postgres:postgresdb@localhost:5432/order_service_db'
app.config['SQLALCHEMY_DATABASE_URI'] = DB_URL
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


class Department(db.Model):
    department_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    department_name = db.Column(db.String(25))


class Employee(db.Model):
    employees_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    fio = db.Column(db.String(100))
    position = db.Column(db.String(25))
    department_id = db.Column(db.Integer, db.ForeignKey('department.department_id'), nullable=False)


class Customers(db.Model):
    customer_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    fio = db.Column(db.String(100))
    number_phone = db.Column(db.Integer)
    email = db.Column(db.String(100))
    is_subscribed = db.Column(db.Boolean, default=False)


class Order(db.Model):
    order_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    created_dt = db.Column(db.DateTime, nullable=False, default=datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    update_dt = db.Column(db.DateTime, nullable=True)
    order_type = db.Column(db.String(20))
    description = db.Column(db.String(100))
    status = db.Column(db.String(15))
    serial_no = db.Column(db.Integer)
    creator_id = db.Column(db.Integer, db.ForeignKey('employee.employees_id'))
    customer_id = db.Column(db.Integer, db.ForeignKey('customers.customer_id'))

    def __str__(self):
        return f"Order_id: {self.order_id}\n" \
               f"Created_dt: {self.created_dt}\n" \
               f"Order_type: {self.order_type}\n" \
               f"Description: {self.description}\n" \
               f"Status: {self.status}\n" \
               f"Serial_no: {self.serial_no}\n" \
               f"Creator_id: {self.creator_id}\n"


class BotInfo(db.Model):
    id_message = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nickname = db.Column(db.String(20))
    id_chat = db.Column(db.Integer)
    message = db.Column(db.String(100))
    dt_message = db.Column(db.DateTime, default=datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

@app.route("/ping")
def ping():
    return f'OK {datetime.now()}'


@app.route('/insert_order', methods=['POST'])
def insert_db():
    if request.method == 'POST':
        data_order = json.loads(request.data)
        order_profile = Order(order_type=data_order['order_type'],
                              description=data_order['description'],
                              status=data_order['status'],
                              serial_no=data_order['serial_no'],
                              creator_id=data_order['creator_id'])
        db.session.add(order_profile)
        db.session.flush()
        db.session.commit()
        return 'Create'


@app.route('/insert_employee', methods=['POST'])
def insert_employee():
    if request.method == 'POST':
        data_employee = json.loads(request.data)
        employee_profile = Employee(fio=data_employee['fio'],
                                    position=data_employee['position'],
                                    department_id=data_employee['department_id'])
        db.session.add(employee_profile)
        db.session.flush()
        db.session.commit()
        return 'Create'


@app.route('/insert_department', methods=['POST'])
def insert_department():
    if request.method == 'POST':
        data_department = json.loads(request.data)
        department_profile = Department(department_name=data_department['department_name'])
        db.session.add(department_profile)
        db.session.flush()
        db.session.commit()
        return 'Create'


@app.route('/change_status', methods=['PATCH'])
def change_status():
    if request.method == 'PATCH':
        data_status = json.loads(request.data)
        get_id = Order.query.filter_by(order_id=data_status['order_id']).first()
        get_id.status = data_status['new_status']
        get_id.update_dt = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        db.session.commit()
        return f'Change_status'


@app.route('/delete_order/<string:delete_id>', methods=['DELETE'])
def delete_order(delete_id):
    del_id = Order.query.filter_by(order_id=delete_id).first()
    db.session.delete(del_id)
    db.session.commit()
    return f'Ok - delete_order_id: {delete_id}'


@app.route('/search_order_id/<string:search_id>', methods=['GET'])
def search_order_id(search_id):
    search_order = Order.query.filter_by(order_id=search_id).first()
    return f'{search_order}'


if __name__ == '__main__':
    app.run(debug=True)


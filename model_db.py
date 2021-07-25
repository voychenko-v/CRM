from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from flask import Flask, request, render_template, url_for, redirect

app = Flask(__name__)
DB_URL = 'postgresql://postgres:postgresdb@localhost:5432/order_service_db'
app.config['SQLALCHEMY_DATABASE_URI'] = DB_URL
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


class Department(db.Model):
    department_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    department_name = db.Column(db.String(25), unique=True)


class Employee(db.Model):
    employees_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    fio = db.Column(db.String(100))
    position = db.Column(db.String(25))
    department_id = db.Column(db.Integer, db.ForeignKey('department.department_id'), nullable=False)

    def __str__(self):
        return f"Employees_id: {self.employees_id}\n" \
               f"Fio: {self.fio}\n" \
               f"Position: {self.position}\n" \
               f"department_id: {self.department_id}\n"


class Customers(db.Model):
    customer_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    fio = db.Column(db.String(100))
    number_phone = db.Column(db.Integer)
    email = db.Column(db.String(100))
    is_subscribed = db.Column(db.Boolean, default=False)


class Order(db.Model):
    order_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    created_dt = db.Column(db.DateTime, nullable=False, default=datetime.now().strftime("%y.%m.%d %H:%M"))
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


@app.route("/")
def index():
    return render_template('index.html')


# Блок роутов "Департамент" - вывод, добавление, редактирование, удаление
@app.route('/create_department', methods=['POST', 'GET'])
def create_department():
    if request.method == 'POST':
        data_department = request.form['department']
        if data_department == '':
            return render_template('base.html', content='Ошибка: Вы ничего не ввели')
        department_profile = Department(department_name=data_department)
        try:
            db.session.add(department_profile)
            db.session.commit()
            return redirect('/show_dep')
        except:
            return render_template('base.html', content='Департамент существует')
    else:
        return render_template('create_department.html')


@app.route('/show_dep')
def show_dep():
    return render_template('show_dep.html', department_list=Department.query.all())


@app.route('/edit_department/<int:id>', methods=['POST', 'GET'])
def edit_department(id):
    department = Department.query.get(id)
    if request.method == 'POST':
        department.department_name = request.form['department_name']
        try:
            db.session.commit()
            return redirect('/show_dep')
        except:
            return 'При редактировании произошла ошибка'
    else:
        return render_template('edit_department.html', department=department)


@app.route('/delete_department/<int:id>')
def delete_department(id):
    department = Department.query.get_or_404(id)
    try:
        db.session.delete(department)
        db.session.commit()
        return redirect('/show_dep')
    except:
        return render_template('base.html', content='При удалении произошла ошибка')


# Блок роутов "Сотрудники" - вывод, добавление, редактирование, удаление
@app.route('/show_emp')
def show_emp():
    return render_template('show_emp.html', employees_list=Employee.query.all())


@app.route('/create_emp', methods=['POST', 'GET'])
def create_emp():
    if request.method == 'POST':
        fio = request.form['fio']
        position = request.form['position']
        department_id = request.form['department_id']
        employee_profile = Employee(fio=fio, position=position, department_id=department_id)
        try:
            db.session.add(employee_profile)
            db.session.commit()
            return redirect('/show_emp')
        except:
            return render_template('base.html', content='При добавлении сотретрудника произошла ошибка')
    else:
        return render_template('create_emp.html')


@app.route('/edit_emp/<int:id>', methods=['POST', 'GET'])
def edit_emp(id):
    employee = Employee.query.get(id)
    if request.method == 'POST':
        employee.fio = request.form['fio']
        employee.position = request.form['position']
        employee.department_id = request.form['department_id']
        try:
            db.session.commit()
            return redirect('/show_emp')
        except:
            return 'При редактировании сотрудника произошла ошибка'
    else:
        return render_template('edit_emp.html', employee=employee)


@app.route('/delete_emp/<int:id>')
def delete_emp(id):
    employee = Employee.query.get_or_404(id)
    try:
        db.session.delete(employee)
        db.session.commit()
        return redirect('/show_emp')
    except:
        return render_template('base.html', content='При удалении произошла ошибка')


# Блок роутов "Заявок" - вывод, добавление, редактирование, удаление
@app.route('/show_order')
def show_order():
    order_list = Order.query.join(Employee, Order.creator_id == Employee.employees_id)\
        .add_columns(Order.order_id, Order.created_dt, Order.update_dt, Order.order_type,
                     Order.description, Order.status, Order.serial_no, Employee.fio)
    return render_template('show_order.html', order_list=order_list)


@app.route('/create_order', methods=['POST', 'GET'])
def create_order():
    if request.method == 'POST':
        order_type = 'Сайт'
        status = 'Новая'
        description = request.form['description']
        serial_no = request.form['serial_no']
        creator_id = request.form['creator_id']
        order_profile = Order(order_type=order_type, description=description, status=status,
                              serial_no=serial_no, creator_id=creator_id)
        try:
            db.session.add(order_profile)
            db.session.commit()
            return redirect('/show_order')
        except :
            return render_template('base.html', content='При добавлении заявки произошла ошибка')
    else:
        return render_template('create_order.html')


@app.route('/edit_order/<int:id>', methods=['POST', 'GET'])
def edit_order(id):
    order = Order.query.get(id)
    if request.method == 'POST':
        order.order_type = request.form['order_type']
        order.description = request.form['description']
        order.status = request.form['status']
        order.serial_no = request.form['serial_no']
        order.creator_id = request.form['creator_id']
        order.update_dt = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        try:
            db.session.commit()
            return redirect('/show_order')
        except:
            return 'При редактировании сотрудника произошла ошибка'
    else:
        return render_template('edit_order.html', order=order)


@app.route('/delete_order/<int:id>')
def delete_order(id):
    order = Order.query.get_or_404(id)
    try:
        db.session.delete(order)
        db.session.commit()
        return redirect('/show_order')
    except:
        return render_template('base.html', content='При удалении произошла ошибка')


# Блок роутов "Клиентов" - вывод, добавление, редактирование, удаление
@app.route('/show_cus')
def show_cus():
    return render_template('show_cus.html', customers_list=Customers.query.all())


@app.route('/create_cus', methods=['POST', 'GET'])
def create_cus():
    if request.method == 'POST':
        fio = request.form['fio']
        number_phone = request.form['number_phone']
        email = request.form['email']
        customer_profile = Customers(fio=fio, number_phone=number_phone, email=email)
        try:
            db.session.add(customer_profile)
            db.session.commit()
            return redirect('/show_cus')
        except:
            return render_template('base.html', content='При добавлении клиента произошла ошибка')
    else:
        return render_template('create_cus.html')


@app.route('/edit_cus/<int:id>', methods=['POST', 'GET'])
def edit_cus(id):
    customer = Customers.query.get(id)
    if request.method == 'POST':
        customer.fio = request.form['fio']
        customer.number_phone = request.form['number_phone']
        customer.email = request.form['email']
        try:
            db.session.commit()
            return redirect('/show_cus')
        except:
            return 'При редактировании сотрудника произошла ошибка'
    else:
        return render_template('edit_cus.html', customer=customer)


@app.route('/delete_cus/<int:id>')
def delete_cus(id):
    customer = Customers.query.get_or_404(id)
    try:
        db.session.delete(customer)
        db.session.commit()
        return redirect('/show_cus')
    except:
        return render_template('base.html', content='При удалении произошла ошибка')


# Блок роутов "Клиентов" - вывод, добавление, редактирование, удаление
@app.route('/show_tel')
def show_tel():
    return render_template('show_tel.html', telegram_list=BotInfo.query.all())


@app.route('/edit_tel/<int:id>', methods=['POST', 'GET'])
def edit_tel(id):
    telegram = BotInfo.query.get(id)
    if request.method == 'POST':
        telegram.nickname = request.form['nickname']
        telegram.id_chat = request.form['id_chat']
        telegram.message = request.form['message']
        try:
            db.session.commit()
            return redirect('/show_tel')
        except:
            return 'При редактировании сотрудника произошла ошибка'
    else:
        return render_template('edit_tel.html', telegram=telegram)


@app.route('/delete_tel/<int:id>')
def delete_tel(id):
    telegram = BotInfo.query.get_or_404(id)
    try:
        db.session.delete(telegram)
        db.session.commit()
        return redirect('/show_tel')
    except:
        return render_template('base.html', content='При удалении произошла ошибка')


if __name__ == '__main__':
    app.run(debug=True)


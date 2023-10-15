from flask import Flask, request, make_response
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from flask_migrate import Migrate

from utils.creat_grafic import create_grafic
import calendar

app = Flask(__name__)
app.debug = True

user_name = 'test_server_user'
password = '123456'
db_name = 'postgres'
app.config['SQLALCHEMY_DATABASE_URI'] = f'postgresql+psycopg2://{user_name}:{password}@localhost/{db_name}'

db = SQLAlchemy(app)

migrate = Migrate(app, db)

days_graph_employees = db.Table(
    'days_graph_employees',
    db.Column('days_graph_id', db.Integer, db.ForeignKey('days_graphs.id')),
    db.Column('employee_id', db.Integer, db.ForeignKey('employees.id'))
)

days_graph_months = db.Table(
    'days_graph_months',
    db.Column('days_graph_id', db.Integer, db.ForeignKey('days_graphs.id')),
    db.Column('month_id', db.Integer, db.ForeignKey('months.id'))
)


class Employee(db.Model):
    __tablename__ = 'employees'
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    dge = db.relationship('DaysGraph', secondary=days_graph_employees, backref='employee')


class Month(db.Model):
    __tablename__ = 'months'
    id = db.Column(db.Integer(), primary_key=True)
    num = db.Column(db.Integer(), nullable=False)
    year = db.Column(db.Integer(), nullable=False)
    days = db.Column(db.Integer(), nullable=False)
    # date = db.Column(db.Date(), nullable=False)
    dgm = db.relationship('DaysGraph', secondary=days_graph_months, backref='month')


class DaysGraph(db.Model):
    __tablename__ = 'days_graphs'
    id = db.Column(db.Integer(), primary_key=True)
    employee_id = db.Column(db.Integer(), db.ForeignKey('employees.id'))
    month_id = db.Column(db.Integer(), db.ForeignKey('months.id'))
    # date = db.Column(db.Date(), nullable=False)
    day = db.Column(db.Integer(), nullable=False)
    # week_day = db.Column(db.String(255), nullable=False)
    status = db.Column(db.String(255), nullable=False)

    updated_on = db.Column(db.DateTime(), default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return "<{}:{}>".format(self.id,  self.title[:10])




@app.route('/get_grafic_by_month', methods=['GET'])
def get_grafic_by_month():
    month = request.json['month']
    year = request.json['year']
    days_in_month = calendar.monthrange(year, month)[1]
    workers_now = [i for i in db.session.query(Employee).all()]
    if len(workers_now) == 0:
        return make_response("нет работников")
    if db.session.query(Month).filter(Month.num == month, Month.year == year).first() is None:
        m_y = Month(num=month, year=year, days=days_in_month)
        db.session.add(m_y)
        db.session.commit()
        workers_name_list = [i.name for i in workers_now]
        ans = create_grafic(workers_name_list, month, year)
        for worker_i in range(len(ans)):
            emp_id = workers_now[worker_i].id
            for j in range(1, len(ans[worker_i])):
                worker_grafic = DaysGraph(employee_id=emp_id, month_id=m_y.id, day=j, status=ans[worker_i][j])
                db.session.add(worker_grafic)
        db.session.commit()
    else:
        m_y = db.session.query(Month).filter(Month.num == month, Month.year == year).first()
        ans = []
        for worker_i in range(len(workers_now)):
            ans.append([workers_now[worker_i].name])
            for day in range(1, days_in_month+1):
                ans[worker_i].append(db.session.query(DaysGraph.status).filter(
                    DaysGraph.employee_id == workers_now[worker_i].id,
                    DaysGraph.month_id == m_y.id,
                    DaysGraph.day == day
                ).first()[0])

            # ans[worker_i].append(db.session.query(DaysGraph.status).filter(
            #     DaysGraph.employee_id == workers_now[worker_i].id,
            #     DaysGraph.month_id == m_y.id
            # ).all())
    return make_response(ans)


@app.route('/add_workers', methods=['PUT'])
def add_workers():
    workers_list = request.json['workers']
    workers_now = [i[0] for i in db.session.query(Employee.name).all()]
    workers_to_db = [Employee(name=i) for i in workers_list if i not in workers_now]
    db.session.add_all(workers_to_db)
    db.session.commit()
    return make_response('db is updated with unsame workers')


@app.route('/add_to_db_list_give_graph', methods=['POST'])
def add_to_db_list_give_graph():
    workers_list = request.json['workers']
    workers_now = [i[0] for i in db.session.query(Employee.name).all()]
    workers_to_db = [Employee(name=i) for i in workers_list if i not in workers_now]
    db.session.add_all(workers_to_db)

    month = request.json['month']
    year = request.json['year']
    if not (month in [i[0] for i in db.session.query(Month.num).all()]) and not (year in [i[0] for i in db.session.query(Month.year).all()]):
        days_in_month = calendar.monthrange(year, month)[1]
        m_y = Month(num=month, year=year, days=days_in_month)
        db.session.add_all(m_y)
    db.session.commit()
    return make_response(create_grafic(workers_list, month, year))


@app.route('/get_workers', methods=['GET'])
def get_workers():
    # print(db.session.query(Employee.name).all())
    ans = [i[0] for i in db.session.query(Employee.name).all()]
    print(ans)
    return make_response(ans)


@app.route('/get_grafic', methods=['POST'])
def get_grafic():
    month = request.json['month']
    year = request.json['year']
    print(db.session.query(Employee.name).all())
    workers_list = db.session.query(Employee).all()

    return make_response(create_grafic(workers_list, month, year))


if __name__ == "__main__":
    app.run()

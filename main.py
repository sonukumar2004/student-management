from flask import Flask,render_template,request,session,redirect,url_for,flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash,check_password_hash
from flask_login import login_user,logout_user,login_manager,LoginManager
from flask_login import login_required,current_user
import json

# MY db connection
local_server= True
app = Flask(__name__)
app.secret_key='spark'


# this is for getting unique user access
login_manager=LoginManager(app)
login_manager.login_view='login'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))



# app.config['SQLALCHEMY_DATABASE_URL']='mysql://username:password@localhost/databas_table_name'
app.config['SQLALCHEMY_DATABASE_URI']='mysql://root:@localhost/ss'
db=SQLAlchemy(app)

# here we will create db models that is tables
class Test(db.Model):
    id=db.Column(db.Integer,primary_key=True)
    name=db.Column(db.String(100))
    email=db.Column(db.String(100))

class Department(db.Model):
    cid=db.Column(db.Integer,primary_key=True)
    branch=db.Column(db.String(100))

class Attendence(db.Model):
    aid=db.Column(db.Integer,primary_key=True)
    rollno=db.Column(db.String(100))
    attendance=db.Column(db.Integer())

class Trig(db.Model):
    tid=db.Column(db.Integer,primary_key=True)
    rollno=db.Column(db.String(100))
    action=db.Column(db.String(100))
    timestamp=db.Column(db.String(100))


class User(UserMixin,db.Model):
    id=db.Column(db.Integer,primary_key=True)
    username=db.Column(db.String(50))
    usertype=db.Column(db.String(50))
    email=db.Column(db.String(50),unique=True)
    password=db.Column(db.String(1000))

class Teacher(db.Model):
    t_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    branch = db.Column(db.String(50), nullable=False)
    subcode = db.Column(db.String(20), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    number = db.Column(db.String(15), nullable=False)
 
class Subjects(db.Model):
    subcode=db.Column(db.String(10),primary_key=True)
    name=db.Column(db.String(50))
    
class Student(db.Model):
    id=db.Column(db.Integer,primary_key=True)
    rollno=db.Column(db.String(50))
    sname=db.Column(db.String(50))
    sem=db.Column(db.Integer)
    gender=db.Column(db.String(50))
    branch=db.Column(db.String(50))
    email=db.Column(db.String(50))
    number=db.Column(db.String(12))
    address=db.Column(db.String(100))
    

@app.route('/')
def index(): 
    return render_template('index.html')

@app.route('/studentdetails')
def studentdetails():
    # query=db.engine.execute(f"SELECT * FROM `student`") 
    query=Student.query.all() 
    return render_template('studentdetails.html',query=query)

@app.route('/teacherdetails')
def teacherdetails():
    if current_user.usertype=="teacher":
        # query=db.engine.execute(f"SELECT * FROM `student`") 
        query=Teacher.query.all() 
        return render_template('teacherdetails.html',query=query)
    else:
        flash("Access Denied","warning")
        return render_template('base.html')

@app.route('/triggers')
def triggers():
    # query=db.engine.execute(f"SELECT * FROM `trig`") 
    query=Trig.query.all()
    return render_template('triggers.html',query=query)
    
@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/department',methods=['POST','GET'])
@login_required
def department():
    if current_user.usertype=="teacher":
        if request.method=="POST":
            dept=request.form.get('dept')
            query=Department.query.filter_by(branch=dept).first()
            if query:
                flash("Department Already Exist","warning")
                return redirect('/department')
            dep=Department(branch=dept)
            db.session.add(dep)
            db.session.commit()
            flash("Department Added","success")
        return render_template('department.html')
    else:
        flash("Access Denied","warning")
        return render_template('base.html')


@app.route('/addattendance',methods=['POST','GET'])
@login_required
def addattendance():
    if current_user.usertype=="teacher":
        query=Student.query.all()
        if request.method=="POST":
            rollno=request.form.get('rollno')
            attend=request.form.get('attend')
            atte=Attendence(rollno=rollno,attendance=attend)
            db.session.add(atte)
            db.session.commit()
            flash("Attendance added","warning")
        return render_template('attendance.html',query=query)
    else:
        flash("Access Denied","warning")
        return render_template('base.html')


@app.route('/search', methods=['POST', 'GET'])
def search():
    if request.method == "POST":
        rollno = request.form.get('roll')
        bio = Student.query.filter_by(rollno=rollno).first()

        # Retrieve teacher details based on the student's branch
        if bio:
            branch = bio.branch
            teacher = Teacher.query.filter_by(branch=branch).first()
        else:
            teacher = None

        attend = Attendence.query.filter_by(rollno=rollno).first()

        return render_template('search.html', bio=bio, attend=attend, teacher=teacher)

    return render_template('search.html')





@app.route("/delete/<string:id>",methods=['POST','GET'])
@login_required
def delete(id):
    post=Student.query.filter_by(id=id).first()
    db.session.delete(post)
    db.session.commit()
    # db.engine.execute(f"DELETE FROM `student` WHERE `student`.`id`={id}")
    flash("Slot Deleted Successful","danger")
    return redirect('/studentdetails')

@app.route("/tdelete/<string:id>", methods=['POST', 'GET'])
@login_required
def tdelete(id):
    # Retrieve the teacher record by ID
    post = Teacher.query.filter_by(t_id=id).first()
    if post:
        # Delete the record using SQLAlchemy
        db.session.delete(post)
        db.session.commit()
        flash("Slot Deleted Successfully", "danger")
    else:
        flash("Teacher not found", "warning")  # Handle case when teacher ID doesn't exist
    return redirect('/teacherdetails')


@app.route("/edit/<string:id>",methods=['POST','GET'])
@login_required
def edit(id):
    # dept=db.engine.execute("SELECT * FROM `department`")    
    if request.method=="POST":
        rollno=request.form.get('rollno')
        sname=request.form.get('sname')
        sem=request.form.get('sem')
        gender=request.form.get('gender')
        branch=request.form.get('branch')
        email=request.form.get('email')
        num=request.form.get('num')
        address=request.form.get('address')
        # query=db.engine.execute(f"UPDATE `student` SET `rollno`='{rollno}',`sname`='{sname}',`sem`='{sem}',`gender`='{gender}',`branch`='{branch}',`email`='{email}',`number`='{num}',`address`='{address}'")
        post=Student.query.filter_by(id=id).first()
        post.rollno=rollno
        post.sname=sname
        post.sem=sem
        post.gender=gender
        post.branch=branch
        post.email=email
        post.number=num
        post.address=address
        db.session.commit()
        flash("Updated","success")
        return redirect('/studentdetails')
    dept=Department.query.all()
    posts=Student.query.filter_by(id=id).first()
    return render_template('edit.html',posts=posts,dept=dept)

@app.route("/tedit/<string:t_id>", methods=['POST', 'GET'])
@login_required
def tedit(t_id):
    if current_user.usertype=="teacher":
        # Retrieve the teacher record by ID
        post = Teacher.query.filter_by(t_id=t_id).first()
        if not post:
           flash("Teacher not found", "warning")  # Handle case when teacher ID doesn't exist
           return redirect('/teacherdetails')

        if request.method == "POST":
            name = request.form.get('name')
            branch = request.form.get('branch')
            subcode = request.form.get('subcode')
            email = request.form.get('email')
            num = request.form.get('num')

            # Update the teacher record
            post.name = name
            post.branch = branch
            post.subcode = subcode
            post.email = email
            post.number = num
            db.session.commit()

            flash("Updated", "success")
            return redirect('/teacherdetails')

        dept = Department.query.all()
        return render_template('tedit.html', posts=post, dept=dept)
    else:
        flash("Access Denied","warning")
        return render_template('base.html')



@app.route('/signup',methods=['POST','GET'])
def signup():
    if request.method == "POST":
        username=request.form.get('username')
        usertype=request.form.get('usertype')
        email=request.form.get('email')
        password=request.form.get('password')

        # Check if all necessary fields are provided
        if not all([username, usertype, email, password]):
            flash("All fields must be provided", "warning")
            return render_template('/signup.html')

        user=User.query.filter_by(email=email).first()
        if user:
            flash("Email Already Exist","warning")
            return render_template('/signup.html')

        encpassword=generate_password_hash(password)

        # Create a new User instance and add it to the database
        new_user = User(username=username, usertype=usertype, email=email, password=encpassword)
        db.session.add(new_user)
        db.session.commit()

        flash("Account created successfully", "success")
        return redirect(url_for('login'))  # Redirect to the login page

    # Render the signup page for GET requests
    return render_template('/signup.html')


@app.route('/login',methods=['POST','GET'])
def login():
    if request.method == "POST":
        email=request.form.get('email')
        password=request.form.get('password')
        user=User.query.filter_by(email=email).first()

        if user and check_password_hash(user.password,password):
            login_user(user)
            flash("Login Success","primary")
            return redirect(url_for('index'))
        else:
            flash("invalid credentials","danger")
            return render_template('login.html')    

    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash("Logout Successful","warning")
    return redirect(url_for('login'))



@app.route('/addstudent',methods=['POST','GET'])
@login_required
def addstudent():
    # dept=db.engine.execute("SELECT * FROM `department`")
    dept=Department.query.all()
    if request.method=="POST":
        rollno=request.form.get('rollno')
        sname=request.form.get('sname')
        sem=request.form.get('sem')
        gender=request.form.get('gender')
        branch=request.form.get('branch')
        email=request.form.get('email')
        num=request.form.get('num')
        address=request.form.get('address')
        # query=db.engine.execute(f"INSERT INTO `student` (`rollno`,`sname`,`sem`,`gender`,`branch`,`email`,`number`,`address`) VALUES ('{rollno}','{sname}','{sem}','{gender}','{branch}','{email}','{num}','{address}')")
        query=Student(rollno=rollno,sname=sname,sem=sem,gender=gender,branch=branch,email=email,number=num,address=address)
        db.session.add(query)
        db.session.commit()

        flash("Student Added","info")


    return render_template('student.html',dept=dept)
    

@app.route('/addteacher', methods=['POST', 'GET'])
@login_required
def addteacher():
    if current_user.usertype == "teacher":
        query = Teacher.query.all()
        dept = Department.query.all()  # Assuming you have a Department model
        if request.method == "POST":
            name = request.form.get('name')
            branch = request.form.get('branch')
            subcode = request.form.get('subcode')
            email = request.form.get('email')
            num = request.form.get('num')
            atte = Teacher(name=name, branch=branch, subcode=subcode, email=email, number=num)
            db.session.add(atte)
            db.session.commit()
            flash("Teacher added", "success")  # Use "success" or "warning" for different message styles
        return render_template('teacher.html', query=query, dept=dept)
    else:
        flash("Access Denied", "warning")
        return render_template('base.html')

if __name__ == '__main__':
    app.run(debug=True)
    
@app.route('/test')
def test():
    try:
        Test.query.all()
        return 'My database is Connected'
    except:
        return 'My db is not Connected'


app.run(debug=True)    
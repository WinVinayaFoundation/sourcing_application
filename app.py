from flask import Flask, render_template, request, redirect, url_for
import mysql.connector

app = Flask(__name__)

# MySQL database configuration
db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': 'root',
    'database': 'WVF_job_portal',
}

# Connect to the database
db = mysql.connector.connect(**db_config)

@app.route('/')
def index():
    # Dummy user data for demonstration purposes
    user = {'username': 'guest'}
    cursor = db.cursor()
    cursor.execute("SELECT title, description, company, created_at, location, hr_name FROM jobs_list")
    jobs = cursor.fetchall()
    job_data = []
    companies = set(job[2] for job in jobs)
    locations = set(job[4] for job in jobs)
    hr_names = set(job[5] for job in jobs)
    for job in jobs:
        job_data.append({
            'title': job[0],
            'description': job[1],
            'company': job[2],
            'created_at': job[3],
            'location': job[4],
            'hr_name': job[5]
        })
    return render_template('index.html', user=user, jobs=job_data, companies=companies, locations=locations, hr_names=hr_names)

@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['login-username']
        password = request.form['login-password']
        category = request.form['login_category']

        # Perform user authentication here
        cursor = db.cursor()
        user_id = None
        success_message = None
        error_message = None

        if category == "login_student":
            print("students is executed")
            cursor.execute("SELECT id FROM students WHERE username = %s AND password = %s", (username, password))
            student = cursor.fetchone()
            if student:
                user_id = student[0]
                success_message = "Login successful. Welcome!"
                return redirect(url_for('user_dashboard', user_id=user_id))
            else:
                # Handle the case where corporate user authentication fails
                error_message = "Invalid username or password. Please try again."

        elif category == "login_corporate":
            print("corp is executed")
            cursor.execute("SELECT id FROM corporate WHERE username = %s AND password = %s", (username, password))
            print(cursor)
            corporate = cursor.fetchone()
            print(corporate)
            if corporate:
                user_id = corporate[0]
                print (user_id)
                success_message = "Login successful. Welcome!"
                return redirect(url_for('corp_dashboard', user_id=user_id))
            else:
                # Handle the case where corporate user authentication fails
                error_message = "Invalid username or password. Please try again."

        js_code = ''
        if success_message:
            js_code += f'alert("{success_message}");'
        if error_message:
            js_code += f'alert("{error_message}");'

        return render_template('index.html', show_login=True, js_code=js_code, error_message=error_message)

    return render_template('index.html', show_login=True)

@app.route('/register', methods=['GET', 'POST'])
def register():
    print("In register, method = ", request.method)
    if request.method == 'POST':
        # username = request.form['username']
        # password = request.form['password']
        # category = request.form['category']
        category = request.form['signin-category']
        print("Category = ", category)
        # Insert user data into the appropriate table based on the selected category
        if category == 'student':
            print("In Student")
            username = request.form['std-username']
            password = request.form['std-password']
            
            name = request.form['std-name']
            email = request.form['std-email']
            phone = request.form['std-phone']
            print("Data of student = ", username, password, category, name, email, phone)
            cursor = db.cursor()
            cursor.execute("INSERT INTO students (username, password, name, email, phone) VALUES (%s, %s, %s, %s, %s)", (username, password, name, email, phone))
            db.commit()
            # return redirect(url_for('login'))
        elif category == 'corporate':
            print("In Corporate")
            username = request.form['corp-username']
            password = request.form['corp-password']
            
            company = request.form['corp-company']
            hr_name = request.form['corp-hr_name']
            hr_email = request.form['corp-hr_email']
            hr_phone = request.form['corp-hr_phone']
            print("Data of Company = ", username, password, category, company, hr_name, hr_email, hr_phone)

            cursor = db.cursor()
            cursor.execute("INSERT INTO corporate (username, password, company, hr_name, hr_email, hr_phone) VALUES (%s, %s, %s, %s, %s, %s)", (username, password, company, hr_name, hr_email, hr_phone))
            db.commit()
        print("In register, redirecting to login page")
        return redirect(url_for('login'))  # Redirect to login page after successful registration
    print("In register, redirecting to register page")
    return render_template('register.html')

@app.route('/corp_dashboard/<int:user_id>')
def corp_dashboard(user_id):
    # Logic for corporate dashboard
    cursor = db.cursor()
    cursor.execute("SELECT id, username, company,hr_name, hr_email, hr_phone FROM corporate WHERE id = %s", (user_id,))
    corporate = cursor.fetchone()
    if corporate:
        user_data = {
                    'id': corporate[0],
                    'username': corporate[1],
                    'company': corporate[2],
                    'hr_name': corporate[3],
                    'hr_email': corporate[4],
                    'hr_phone': corporate[5]
                    }

        cursor.execute("SELECT title, description, company, created_at, location, hr_name FROM jobs_list")
        jobs = cursor.fetchall()
        job_data = []
        for job in jobs:
            job_data.append({
                'title': job[0],
                'description': job[1],
                'company': job[2],
                'created_at': job[3],
                'location': job[4],
                'hr_name': job[5]
            })

        # Pass user_data to the template
        return render_template('corp_dashboard.html', user=user_data, jobs=job_data)
    else:
        # Handle the case where user does not exist (optional)
        return "User not found"
    # return render_template('corp_dashboard.html', user_id=user_id)

@app.route('/dashboard/user/<int:user_id>')
def user_dashboard(user_id):
    # Fetch user data from the database based on user_id
    cursor = db.cursor()
    cursor.execute("SELECT id, username, name, phone, email FROM students WHERE id = %s", (user_id,))
    student = cursor.fetchone()
    if student:
        user_data = {
            'id': student[0],
            'username': student[1],
            'name': student[2],
            'phone': student[3],
            'email': student[4]
        }

        # Fetch jobs list
        cursor.execute("SELECT title, description, company, created_at, location, hr_name FROM jobs_list")
        jobs = cursor.fetchall()
        job_data = []
        for job in jobs:
            job_data.append({
                'title': job[0],
                'description': job[1],
                'company': job[2],
                'created_at': job[3],
                'location': job[4],
                'hr_name': job[5]
            })

        # Pass user_data and jobs to the template
        return render_template('user_dashboard.html', user=user_data, jobs=job_data)
    else:
        return "User not found"

@app.route('/post_job', methods=['POST'])
def post_job():
    if request.method == 'POST':
        # Get form data
        job_title = request.form['jobTitle']
        job_description = request.form['jobDescription']
        company_name = request.form['companyName']
        hr_name = request.form['hrName']
        location = request.form['location']

        # Insert job data into the database
        cursor = db.cursor()
        cursor.execute("INSERT INTO jobs_list (title, description, company, hr_name, location) VALUES (%s, %s, %s, %s, %s)", (job_title, job_description, company_name, hr_name, location))
        db.commit()
        
        # Fetch the user_id from the session or database and pass it to url_for
        # Example: user_id = fetch_user_id_from_session_or_database()
        user_id = 1  # Replace 1 with the actual user_id
        return redirect(url_for('corp_dashboard', user_id=user_id))  # Redirect back to corporate dashboard after posting the job


if __name__ == '__main__':
    app.run(debug=True)

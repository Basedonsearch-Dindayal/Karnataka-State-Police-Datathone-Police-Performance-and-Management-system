from flask import Flask,render_template,request,session,redirect,url_for,flash,send_from_directory,make_response
import sqlite3
import datetime
import time
import os
import random
from werkzeug.utils import secure_filename
import folium
import csv
from io import StringIO

status='none'
# creating tables of database

conn = sqlite3.connect('POLICE_RECORD.db')
conn.execute('CREATE TABLE IF NOT EXISTS staff (\
ID VARCHAR(6) PRIMARY KEY NOT NULL UNIQUE,\
NAME VARCHAR(20) NOT NULL, \
PASSWORD TEXT NOT NULL, \
EMAIL TEXT NOT NULL UNIQUE,\
PHONENUMBER  INT NOT NULL UNIQUE,\
AGE INT NOT NULL,\
GENDER CHAR(1) NOT NULL,\
DOB TIMESTAMP NOT NULL,\
JOINING_DATE TIMESTAMP NOT NULL,\
BRANCH VARCHAR(50) NOT NULL,\
DESIGNATION VARCHAR(40) NOT NULL,\
RETIRED_OR_SUSPENDED CHAR(3) NOT NULL,\
IMAGE TEXT NOT NULL,\
ADDRESS TEXT NOT NULL)')

conn.execute('CREATE TABLE IF NOT EXISTS criminal (\
ID VARCHAR(6) PRIMARY KEY NOT NULL UNIQUE,\
NAME VARCHAR(20) NOT NULL, \
PHONENUMBER  INT NOT NULL,\
AGE INT NOT NULL,\
GENDER CHAR(1) NOT NULL,\
DOB TIMESTAMP ,\
JAILED CHAR(1) NOT NULL,\
IMAGE TEXT,\
ADDRESS TEXT NOT NULL)')

conn.execute('CREATE TABLE IF NOT EXISTS complaints (\
District_Name VARCHAR(50) NOT NULL,\
UnitName VARCHAR(50) NOT NULL,\
FIRNo INT NOT NULL,\
RI	 INT NOT NULL,\
Year TIMESTAMP NOT NULL,\
Month TIMSTAMP NOT NULL,\
Offence_From_Date TIMESTAMP NOT NULL,\
Offence_To_Date	 TIMESTAMP NOT NULL,\
FIR_Reg_DateTime TIMESTAMP NOT NULL,\
FIR_Date	 TIMESTAMP NOT NULL,\
FIR_Type VARCHAR(50) NOT NULL,\
FIR_Stage VARCHAR(50) NOT NULL,\
Complaint_Mode VARCHAR(50) NOT NULL,\
CrimeGroup_Name	 VARCHAR(50) NOT NULL,\
CrimeHead_Name	 VARCHAR(50) NOT NULL,\
Latitude	 DOUBLE NOT NULL,\
Longitude	 DOUBLE NOT NULL,\
ActSection	 VARCHAR(50) NOT NULL,\
IOName	 VARCHAR(50) NOT NULL,\
KGID	 INT NOT NULL,\
IOAssigned_Date	 TIMESTAMP,\
Internal_IO	 INT NOT NULL,\
Place_of_Offence	VARCHAR(50) NOT NULL,\
Distance_from_PS	VARCHAR(50) NOT NULL,\
Beat_Name	 VACHAR(50) NOT NULL,\
Village_Area_Name	VARCHAR(50) NOT NULL,\
Male	INT NOT NULL,\
Female	INT NOT NULL,\
Boy	INT NOT NULL,\
Girl	INT NOT NULL,\
Age 	INT NOT NULL,\
VICTIM_COUNT	INT NOT NULL,\
Accused_Count	INT NOT NULL,\
Arrested_Male	INT NOT NULL,\
Arrested_Female	INT NOT NULL,\
Arrested_Count_No	INT NOT NULL,\
Accused_ChargeSheeted_Count	INT NOT NULL,\
Conviction_Count	INT NOT NULL,\
FIR_ID	 VARCHAR(50) NOT NULL,\
Unit_ID	 VARCHAR(50) NOT NULL,\
Crime_No INT NOT NULL)')

conn.close()

conn=sqlite3.connect('PUBLIC.db')
cursor=conn.cursor()
cursor.execute('CREATE TABLE IF NOT EXISTS public (\
AADHAR INT PRIMARY KEY NOT NULL UNIQUE,\
NAME VARCHAR(20) NOT NULL, \
PHONENUMBER  INT NOT NULL,\
PASSWORD TEXT NOT NULL,\
ADDRESS TEXT NOT NULL)')

cursor.execute('CREATE TABLE IF NOT EXISTS public_urgency (\
AADHAR INT NOT NULL,\
TIME TIMESTAMP NOT NULL,\
LATITUDE TEXT NOT NULL,\
LONGITUDE TEXT NOT NULL)')
conn.close()



def seriesdatafun(data):
    inspector_months = {}
    for record in data:
        year_month = f"{record[4]}-{record[5]}"  # Extract year and month from date (e.g., '2024-05')
        inspector = record[18]
        if inspector not in inspector_months:
            inspector_months[inspector] = {}
        if year_month not in inspector_months[inspector]:
            inspector_months[inspector][year_month] = 0
        inspector_months[inspector][year_month] += 1
    
    series_data = []
    for inspector, months in inspector_months.items():
        inspector_data = {
            'name': inspector,
            'data': [[year_month, count] for year_month, count in months.items()]
        }
        series_data.append(inspector_data)
    
    return series_data


def firdata(query):
    conn=sqlite3.connect('POLICE_COMPLAINT.db')
    cursor=conn.cursor()
    allowed_columns = {
    "District_Name", "UnitName", "FIRNo", "RI", "Year", "Month", 
    "Offence_From_Date", "Offence_To_Date", "FIR_Reg_DateTime", "FIR_Date", 
    "FIR_Type", "FIR_Stage", "Complaint_Mode", "CrimeGroup_Name", 
    "CrimeHead_Name", "Latitude", "Longitude", "ActSection", "IOName", 
    "KGID", "IOAssigned_Date", "Internal_IO", "Place_of_Offence", 
    "Distance_from_PS", "Beat_Name", "Village_Area_Name", "Male", 
    "Female", "Boy", "Girl", "Age", "VICTIM_COUNT", "Accused_Count", 
    "Arrested_Male", "Arrested_Female", "Arrested_Count_No", 
    "Accused_ChargeSheeted_Count", "Conviction_Count", "FIR_ID", 
    "Unit_ID", "Crime_No"
}
    if query!='all':
        # Parse the input to get the column name and keyword
        parts = query.strip().split(' ', 1)
        if len(parts) != 2:
            flash("Invalid input format. Please enter in 'column_name keyword' format.")
            return []
        # When you use = for comparison, the keyword must exactly match the column value. Wildcards (%) should not be used with = because they are meant for pattern matching with the LIKE operator.
        column_name, keyword = parts
        column_name = column_name.strip()
        keyword = keyword.strip().lower()
        # Validate the column name
        if column_name not in allowed_columns:
            flash(f"Invalid column name: {column_name}")
            return []
        # Construct the SQL query
        sql = f"SELECT * FROM complaints WHERE LOWER({column_name}) = ?"
        # Execute the query
        cursor.execute(sql, (keyword,))
    else:
        cursor.execute('SELECT * FROM complaints')
    user=cursor.fetchall()
    conn.close()
    return user


def generate_csv(data,header):
    # Create CSV data
    csv_data = StringIO()
    datawriter = csv.writer(csv_data)
    datawriter.writerow(header)
    for row in data:
        datawriter.writerow(row)
    return csv_data.getvalue()


def getstaff(query):
    conn = sqlite3.connect('POLICE_RECORD.db')
    cursor = conn.cursor()
    allowed_columns = {'ID', 'NAME', 'PHONENUMBER', 'AGE', 'DOB', 'JOINING_DATE', 'BRANCH', 'DESIGNATION', 'GENDER', 'RETIRED_OR_SUSPENDED', 'ADDRESS','EMAIL'}
    if query!='all':
        parts = query.strip().split(' ', 1)
        if len(parts) != 2:
            flash("Invalid input format. Please enter in 'column_name keyword' format.")
            return []
        
        column_name, keyword = parts
        # Validate the column name
        column_name = column_name.upper()
        if column_name not in allowed_columns:
            flash(f"Invalid column name: {column_name}")
            return []
        # Construct the SQL query
        sql = f"SELECT * FROM staff WHERE LOWER({column_name}) LIKE ?"
        # Use wildcards for partial matches
        like_keyword = f"%{keyword.strip().lower()}%"
        # Execute the query
        cursor.execute(sql, (like_keyword,))
    else:
        cursor.execute('SELECT * FROM staff')
    userdata=cursor.fetchall()
    conn.close()
    return userdata

def getcriminal(query):
    conn = sqlite3.connect('POLICE_RECORD.db')
    cursor = conn.cursor()
    allowed_columns = {'ID', 'NAME', 'PHONENUMBER', 'AGE', 'DOB', 'GENDER','JAILED','ADDRESS'}
    if query!='all':
        parts = query.strip().split(' ', 1)
        if len(parts) != 2:
            flash("Invalid input format. Please enter in 'column_name keyword' format.")
            return []
        
        column_name, keyword = parts
        # Validate the column name
        column_name = column_name.upper()
        if column_name not in allowed_columns:
            flash(f"Invalid column name: {column_name}")
            return []
        # Construct the SQL query
        sql = f"SELECT * FROM criminal WHERE LOWER({column_name}) LIKE ?"
        # Use wildcards for partial matches
        like_keyword = f"%{keyword.strip().lower()}%"
        # Execute the query
        cursor.execute(sql, (like_keyword,))
    else:
        cursor.execute('SELECT * FROM criminal')
    userdata=cursor.fetchall()
    conn.close()
    return userdata
    

def find_rendzones(data):
    redzones = {}
    years=[2016,2017,2018,2019,2020,2021,2022,2023,2024,2025,2026,2027]
    for i in data:
        if i[0] not in redzones:
            redzones[i[0]]=[0,0,0,0,0,0,0,0,0,0,0,0]
            for j in data:
                if j[0]==i[0]:
                    index=j[4]-2016
                    redzones[i[0]][index]+=1
    return redzones


def find_police(data):
    districts={}
    for i in data:
        if i[18] not in districts:
            districts[i[18]]=1
        else:
            districts[i[18]]+=1
    return districts


def earthmap(data):
    circledata=[]
    for i in data:
        circledata.append([i[15],i[16],1])
    mapobj=folium.Map(location=[23.294059708387206,78.26660156250001],zoom_start=6)
    shapesLayer=folium.FeatureGroup(name='circles').add_to(mapobj)
    bordersStyle = {"color": 'green', 'weight': 2, 'fillOpacity': 0}
    geojsons=['geojsons\KARNATAKA_DISTRICTS.geojson','geojsons\KARNATAKA_STATE.geojson']
    for i in geojsons:
        bordersLayer = folium.GeoJson(
            data=i,
            name=i,
            style_function=lambda x: bordersStyle)
        bordersLayer.add_to(mapobj)
    for cData in circledata:
        folium.Circle(location=[cData[0],cData[1]],
        radius=cData[2],
        weight=5,
        color='red',
        fill=True,
        fill_color='red',
        tooltip=f"{cData[0]} , {cData[1]}",
        fill_opacity=0.1).add_to(shapesLayer)
    folium.LayerControl().add_to(mapobj)
    # Save the map as HTML string
    return mapobj._repr_html_()




app=Flask(__name__)

app.secret_key = 'super-secret-key'
app.config['UPLOAD_FOLDER'] = 'uploads'

@app.route('/public_emergency/<username>',methods=['GET','POST'])
def public_emergency(username):
    
    global status
    if 'user' in session:
        if request.method=='POST':
            latitude=request.form.get('lt')
            longitude=request.form.get('lg')
            conn=sqlite3.connect('PUBLIC.db')
            cursor=conn.cursor()
            print(latitude," ",longitude)
            try:
                cursor.execute('INSERT INTO public_urgency (AADHAR,TIME,LATITUDE,LONGITUDE) VALUES(?,?,?,?)',(username,datetime.datetime.now(),latitude,longitude))
                conn.commit()
            except:
                conn.rollback()
            conn.close()
        return render_template('public_emergency.html',username=username)
    return render_template('ksp.html')

@app.route('/')
def ksp():
    
    global status
    return render_template('ksp.html')

@app.route('/public_login',methods=['GET','POST'])
def public_login():
    
    global status
    if 'user' not in session:
        if request.method=='POST':
            conn=sqlite3.connect('PUBLIC.db')
            cursor=conn.cursor()
            aadhar=int(request.form.get('aadhar'))
            password=request.form.get('password')
            cursor.execute('SELECT * FROM public WHERE AADHAR=? AND PASSWORD=?',(aadhar,password))
            public_data=cursor.fetchone()
            print(public_data)
            if public_data is not None:
                session['user']=public_data[0]
                print('logged in')
                return redirect(url_for('public_emergency',username=session['user'])) 
            conn.close()
        return render_template('public_login.html')
    else:
        return redirect(url_for('public_emergency',username=session['user']))

@app.route('/public_signup',methods=['GET','POST'])
def public_signup():
    
    global status
    if request.method=='POST':
        conn=sqlite3.connect('PUBLIC.db')
        cursor=conn.cursor()
        try:
            cursor.execute('INSERT INTO public (AADHAR,NAME,PHONENUMBER,PASSWORD,ADDRESS) VALUES (?, ?, ?, ?, ?)',
                    (request.form.get("aadhar"), 
                        request.form.get("name"), 
                        request.form.get('Phone'), 
                        request.form.get("password"), 
                        request.form.get('address')))
            conn.commit()
            flash('account created')
        except:
            conn.rollback()
            flash('account creation failed')
        conn.close()
        return redirect(url_for('public_login'))
    return render_template('public_signup.html')

@app.route('/stafflogin',methods=['GET','POST'])
def login():
    
    global status
    global designation
    global workingcondition
    if 'user' not in session:
        if request.method=='POST':
            username = request.form.get('username')
            userpass = request.form.get('password')
            conn = sqlite3.connect('POLICE_RECORD.db')
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM staff WHERE ID=? AND PASSWORD=?", (username, userpass))
            data=cursor.fetchone()
            if data is not None:
                session['user']=username
                print('logged in')
                print(data)
                status='staff'
                designation=data[10]
                workingcondition=data[11]
                return redirect(url_for('home',username=username)) 
            conn.close()
            return redirect(url_for('login'))
        return render_template('login.html')
    else:
        return redirect(url_for('home',username=session['user']))

@app.route('/home/<username>')
def home(username):
    
    global status
    print(status)
    if 'user' in session and status=='staff':
        conn=sqlite3.connect('POLICE_RECORD.db')
        cursor=conn.cursor()
        cursor.execute('SELECT * FROM staff WHERE ID =?',(username,))
        data=cursor.fetchone()
        conn.close()
        return render_template('home.html',username=username,data=data)
    return redirect('/stafflogin')

@app.route('/staff/<username>',methods=['GET','POST'])
def staff(username):
    
    global status
    if 'user' in session and status=='staff':
        
        gender=['M','F','O']
        retiredtatus=['wor','ret','sus']
        if request.method=='POST':
            query=request.form.get('query')
            data=getstaff(query)
            datawl=[list(i[:2]+i[3:]) for i in data]
            for i in datawl:
                i[11]='http://127.0.0.1:5000/uploads/'+i[11]
            csv_data = generate_csv(datawl,['ID','NAME','EMAIL','PHONENUMBER','AGE','GENDER','DOB','JOINING_DATE','BRANCH','DESIGNATION','RETIRED_OR_SUSPENDED','IMAGE','ADDRESS'])
            return render_template('staff.html',data=data,username=username,gender=gender,retiredstatus=retiredtatus,csv_data=csv_data)
        data=getstaff('all')
        print(data)
        datawl=[list(i[:2]+i[3:]) for i in data]
        for i in datawl:
            i[11]='http://127.0.0.1:5000/uploads/'+i[11]
        csv_data = generate_csv(datawl,['ID','NAME','EMAIL','PHONENUMBER','AGE','GENDER','DOB','JOINING_DATE','BRANCH','DESIGNATION','RETIRED_OR_SUSPENDED','IMAGE','ADDRESS'])
        return render_template('staff.html',data=data,username=username,gender=gender,retiredstatus=retiredtatus,csv_data=csv_data)
    return redirect('/stafflogin')

@app.route('/criminal/<username>',methods=['GET','POST'])
def criminal(username):
    
    global status
    if 'user' in session and status=='staff':
        jailed=['Y','N']
        gender=['M','F','O']
        if request.method=='POST':
            query=request.form.get('query')
            data=getcriminal(query)
            datawl=[]
            for i in data:
                datawl.append(list(i))
            for i in datawl:
                i[7]='http://127.0.0.1:5000/uploads/'+i[7]
            csv_data = generate_csv(datawl,['ID', 'NAME', 'PHONENUMBER', 'AGE', 'GENDER', 'DOB', 'JAILED', 'IMAGE', 'ADDRESS'])
            
            return render_template('criminal.html',data=data,username=username,jailed=jailed,gender=gender,csv_data=csv_data)
        data=getcriminal('all')
        print(data)
        datawl=[]
        for i in data:
            print(i)
            datawl.append(list(i))
        for i in datawl:
            i[7]='http://127.0.0.1:5000/uploads/'+i[7]
        csv_data = generate_csv(datawl,['ID', 'NAME', 'PHONENUMBER', 'AGE', 'GENDER', 'DOB', 'JAILED', 'IMAGE', 'ADDRESS'])
            
        return render_template('criminal.html',data=data,username=username,jailed=jailed,gender=gender,csv_data=csv_data)
    return redirect('/stafflogin')

# to send the folder details of uploaded image
@app.route('/uploads/<filename>')
def serve_uploaded_image(filename):
    uploads_folder = os.path.join(app.root_path, 'uploads')
    return send_from_directory(uploads_folder, filename)



@app.route('/download_csv/<username>', methods=['POST'])
def download_csv(username):
    csv_data = request.form.get('csv_data')
    if csv_data:
        response = make_response(csv_data)
        response.headers["Content-Disposition"] = f"attachment; filename={username}_data.csv"
        response.headers["Content-Type"] = "text/csv"
        return response
    else:
        return "No CSV data provided."




@app.route('/add_staff/<username>',methods=['GET','POST'])
def add_staff(username):
    
    global status
    global designation
    global workingcondition
    if 'user' in session and status=='staff':
        if request.method=='POST':
            conn = sqlite3.connect('POLICE_RECORD.db')
            cursor=conn.cursor()
            try:
                image = request.files['image']
                # Validate the uploaded image
                if not allowed_file(image.filename):
                    flash('Invalid file format. Only JPG GIF png jpeg files are allowed.')
                elif image:
                    filename = secure_filename(image.filename)
                    filename,extension=os.path.splitext(filename)
                    filename=f"{str(time.time()).replace('.','_')}{extension}"
                    image_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                    image.save(image_path)
                    cursor.execute("INSERT INTO staff (ID,NAME,PASSWORD,EMAIL,PHONENUMBER,AGE,GENDER,DOB,JOINING_DATE,BRANCH,DESIGNATION,RETIRED_OR_SUSPENDED,IMAGE,ADDRESS) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                    (request.form.get("staff_id"), 
                        request.form.get("staff_name"), 
                        request.form.get("pw"), 
                        request.form.get("email"), 
                        request.form.get('phone'), 
                        request.form.get('age'), 
                        request.form.get('gen'),
                        request.form.get('dob'),
                        request.form.get('jd'),
                        request.form.get('branch').lower(),
                        request.form.get('desig').lower(),
                        request.form.get('sec'),
                        filename,
                        request.form.get('add').lower()))
                    conn.commit()
                    flash('added and published')
            except FileNotFoundError as e:
                print(f"File not found error: {e}")
                conn.rollback()
                flash('failed')
            except sqlite3.Error as e:
                print(f"SQLite error: {e}")
                conn.rollback()
                flash('failed')
            except Exception as e:
                print(f"An unexpected error occurred: {e}")
                conn.rollback()
                flash('failed')
            conn.close()
            return redirect(url_for('staff',username=username))
        if designation=='technical' and workingcondition=='wor':
            return render_template('add_staff.html',username=username)
        else:
            return render_template('notallowed.html',username=username)
    return redirect('/stafflogin')

def allowed_file(filename):
  allowed_extensions = {'jpg', 'gif', 'jpeg', 'png'}
  return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed_extensions



@app.route('/add_criminal/<username>',methods=['GET','POST'])
def add_criminal(username):
    
    global status,designation
    if 'user' in session and status=='staff':
        if request.method=='POST':
            conn = sqlite3.connect('POLICE_RECORD.db')
            cursor=conn.cursor()
            try:
                image = request.files['image']
                # Validate the uploaded image
                if not allowed_file(image.filename):
                    flash('Invalid file format. Only JPG GIF png jpeg files are allowed.')
                elif image:
                    filename = secure_filename(image.filename)
                    filename,extension=os.path.splitext(filename)
                    filename=f"{str(time.time()).replace('.','_')}{extension}"
                    image_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                    image.save(image_path)
                    cursor.execute("INSERT INTO criminal (ID,NAME,PHONENUMBER,AGE,GENDER,DOB,JAILED,IMAGE,ADDRESS) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
                    (request.form.get("criminal_id"), 
                        request.form.get("criminal_name"), 
                        request.form.get('phone'), 
                        request.form.get('age'), 
                        request.form.get('gen'),
                        request.form.get('dob'),
                        request.form.get('jailed'),
                        filename,
                        request.form.get('add').lower()))
                    conn.commit()
                    flash('added and published')
            except FileNotFoundError as e:
                print(f"File not found error: {e}")
                conn.rollback()
                flash('failed')
            except sqlite3.Error as e:
                print(f"SQLite error: {e}")
                conn.rollback()
                flash('failed')
            except Exception as e:
                print(f"An unexpected error occurred: {e}")
                conn.rollback()
                flash('failed')
            conn.close()
            return redirect(url_for('criminal',username=username))
        if designation=='technical' and workingcondition=='wor':
            return render_template('add_criminal.html',username=username)
        else:
            return render_template('notallowed.html',username=username)
    return redirect('/stafflogin')




@app.route('/file_complaint/<username>',methods=['GET','POST'])
def file_complaint(username):
    
    global status
    global designation
    global workingcondition
    if 'user' in session and status=='staff':
        if request.method=='POST':
            conn=sqlite3.connect('POLICE_RECORD.db')
            cursor=conn.cursor()
            try:
                cursor.execute('INSERT INTO complaints (District_Name,UnitName,FIRNo,RI,Year,Month,Offence_From_Date,Offence_To_Date,FIR_Reg_DateTime,FIR_Date,FIR_Type,FIR_Stage,Complaint_Mode,CrimeGroup_Name,CrimeHead_Name,Latitude,Longitude,ActSection,IOName,KGID,IOAssigned_Date,Internal_IO	,Place_of_Offence,Distance_from_PS,Beat_Name,Village_Area_Name,Male,Female,Boy,Girl,Age,VICTIM_COUNT,Accused_Count,Arrested_Male,Arrested_Female,Arrested_Count_No,Accused_ChargeSheeted_Count,Conviction_Count,FIR_ID,Unit_ID,Crime_No) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)',(
                request.form.get('district_name'),
                request.form.get('unit_name'),
                request.form.get('fir_no'),
                request.form.get('ri'),
                request.form.get('year'),
                request.form.get('month'),
                request.form.get('offence_from_date'),
                request.form.get('offence_to_date'),
                request.form.get('fir_reg_datetime'),
                request.form.get('fir_date'),
                request.form.get('fir_type'),
                request.form.get('fir_stage'),
                request.form.get('complaint_mode'),
                request.form.get('crimegroup_name'),
                request.form.get('crimehead_name'),
                request.form.get('latitude'),
                request.form.get('longitude'),
                request.form.get('act_section'),
                request.form.get('io_name'),
                request.form.get('kgid'),
                request.form.get('ioassigned_date'),
                request.form.get('internal_io'),
                request.form.get('place_of_offence'),
                request.form.get('distance_from_ps'),
                request.form.get('beat_name'),
                request.form.get('village_area_name'),
                request.form.get('male'),
                request.form.get('female'),
                request.form.get('boy'),
                request.form.get('girl'),
                request.form.get('age'),
                request.form.get('victim_count'),
                request.form.get('accused_count'),
                request.form.get('arrested_male'),
                request.form.get('arrested_female'),
                request.form.get('arrested_count_no'),
                request.form.get('accused_chargesheeted_count'),
                request.form.get('conviction_count'),
                request.form.get('fir_id'),
                request.form.get('unit_id'),
                request.form.get('crime_no')))
                conn.commit()
                flash('fir added and published')
            except:
                flash('failed')
                conn.rollback
            conn.close()
            return redirect(url_for('analytical_dashboard',username=username))
        if designation=='hawaldar' and workingcondition=='wor':
            return render_template('file_complaint.html',username=username)
        else:
            return render_template('notallowed.html',username=username)
    return redirect('/stafflogin')

@app.route('/analytical_dashboard/<username>',methods=['GET','POST'])
def analytical_dashboard(username):
    
    global status
    if 'user' in session and status=='staff':
        
        if request.method=='POST':
            query=request.form.get('query')
            data=firdata(query)
            districts=find_police(data)
            district=list(districts.keys())
            district_mod=list(districts.values())
            
            redzones=find_rendzones(data)
            htmlmap=earthmap(data)
            print(redzones)
            # redzones={'a':[213, 37, 0, 0, 0, 8, 0, 45, 0, 0, 0, 0],'b':[21, 7, 0, 10, 0, 50, 0, 0, 0, 0, 0, 5],'c':[13, 3, 0, 0, 0, 0, 0, 0, 0, 0, 4,45],'d':[83, 37, 0, 90, 0, 8, 0, 45, 0, 0, 0, 0],'e':[21, 7, 0, 10, 50, 50, 0, 90, 0, 0, 0, 5],'f':[3, 3, 0, 0, 90, 0, 0, 10, 0, 0, 4,45]}

            seriesdata=seriesdatafun(data)
            print(seriesdata)
            csv_data = generate_csv(data,['District_Name', 'UnitName', 'FIRNo', 'RI', 'Year', 'Month', 'Offence_From_Date', 'Offence_To_Date', 'FIR_Reg_DateTime', 'FIR_Date', 'FIR_Type', 'FIR_Stage', 'Complaint_Mode', 'CrimeGroup_Name', 'CrimeHead_Name', 'Latitude', 'Longitude', 'ActSection', 'IOName', 'KGID', 'IOAssigned_Date', 'Internal_IO', 'Place_of_Offence', 'Distance_from_PS', 'Beat_Name', 'Village_Area_Name', 'Male', 'Female', 'Boy', 'Girl', 'Age', 'VICTIM_COUNT', 'Accused_Count', 'Arrested_Male', 'Arrested_Female', 'Arrested_Count_No', 'Accused_ChargeSheeted_Count', 'Conviction_Count', 'FIR_ID', 'Unit_ID', 'Crime_No'])
            return render_template('analytical_dashboard.html',data=data,series_data=seriesdata,htmlmap=htmlmap,district=district,district_mod=district_mod,datalength=len(data),redzones=redzones,username=username,csv_data=csv_data)
            
        data=firdata('all')
        districts=find_police(data)
        district=list(districts.keys())
        district_mod=list(districts.values())
        
        redzones=find_rendzones(data)
        htmlmap=earthmap(data)
        print(redzones)
        csv_data = generate_csv(data,['District_Name', 'UnitName', 'FIRNo', 'RI', 'Year', 'Month', 'Offence_From_Date', 'Offence_To_Date', 'FIR_Reg_DateTime', 'FIR_Date', 'FIR_Type', 'FIR_Stage', 'Complaint_Mode', 'CrimeGroup_Name', 'CrimeHead_Name', 'Latitude', 'Longitude', 'ActSection', 'IOName', 'KGID', 'IOAssigned_Date', 'Internal_IO', 'Place_of_Offence', 'Distance_from_PS', 'Beat_Name', 'Village_Area_Name', 'Male', 'Female', 'Boy', 'Girl', 'Age', 'VICTIM_COUNT', 'Accused_Count', 'Arrested_Male', 'Arrested_Female', 'Arrested_Count_No', 'Accused_ChargeSheeted_Count', 'Conviction_Count', 'FIR_ID', 'Unit_ID', 'Crime_No'])
        # redzones={'a':[213, 37, 0, 0, 0, 8, 0, 45, 0, 0, 0, 0],'b':[21, 7, 0, 10, 0, 50, 0, 0, 0, 0, 0, 5],'c':[13, 3, 0, 0, 0, 0, 0, 0, 0, 0, 4,45],'d':[83, 37, 0, 90, 0, 8, 0, 45, 0, 0, 0, 0],'e':[21, 7, 0, 10, 50, 50, 0, 90, 0, 0, 0, 5],'f':[3, 3, 0, 0, 90, 0, 0, 10, 0, 0, 4,45]}
         
        seriesdata=seriesdatafun(data)
        print(seriesdata)        
        return render_template('analytical_dashboard.html',data=data,series_data=seriesdata,htmlmap=htmlmap,district=district,district_mod=district_mod,datalength=len(data),redzones=redzones,username=username,csv_data=csv_data)
    return redirect('/stafflogin')


@app.route('/navigation_details/<username>')
def navigation_details(username):
    
    global status
    if 'user' in session and status=='staff':
        conn=sqlite3.connect('PUBLIC.db')
        cursor=conn.cursor()
        cursor.execute('SELECT * FROM public_urgency')
        data=cursor.fetchall()
        data=data[::-1]
        conn.close()
        return render_template('navigation.html',data=data,username=username)
    return redirect('/stafflogin')

@app.route("/logout")
def logout():
    global status
    status='none'
    session.pop('user')
    return redirect('/stafflogin')

@app.route("/updatestaff/<username>/<staffid>",methods=['GET','POST'])
def staffupdate(username,staffid):
    global status
    global designation
    global workingcondition
    if 'user' in session and status=='staff':
        if designation=='technical' and workingcondition=='wor':
            conn = sqlite3.connect('POLICE_RECORD.db')
            cursor=conn.cursor()
            try:
                if request.method=='POST':
                    image=request.files['image']
                    if image.filename!="":
                        if not allowed_file(image.filename):
                            flash('Invalid file format. Only JPG GIF png jpeg files are allowed.')
                        elif image:
                            filename = secure_filename(image.filename)
                            image_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                            image.save(image_path)
                            cursor.execute('''UPDATE staff SET NAME=?,EMAIL=?,PHONENUMBER=?,GENDER=?,DOB=?,BRANCH=?,DESIGNATION=?,RETIRED_OR_SUSPENDED=?,IMAGE=?,ADDRESS=? WHERE ID=?''',
                                           (request.form.get("staff_name"),
                                            request.form.get("email"), 
                                            request.form.get('phone'),  
                                            request.form.get('gen'),
                                            request.form.get('dob'),
                                            request.form.get('branch').lower(),
                                            request.form.get('desig').lower(),
                                            request.form.get('sec'),
                                            filename,
                                            request.form.get('add').lower(),staffid)) 
                            conn.commit()
                            flash(f'updated with image{staffid}')
                    else:
                        cursor.execute('''UPDATE staff SET NAME=?,EMAIL=?,PHONENUMBER=?,GENDER=?,DOB=?,BRANCH=?,DESIGNATION=?,RETIRED_OR_SUSPENDED=?,ADDRESS=? WHERE ID=?''',
                                           (request.form.get("staff_name"),
                                            request.form.get("email"), 
                                            request.form.get('phone'),  
                                            request.form.get('gen'),
                                            request.form.get('dob'),
                                            request.form.get('branch').lower(),
                                            request.form.get('desig').lower(),
                                            request.form.get('sec'),
                                            request.form.get('add').lower(),staffid))
                        conn.commit()
                        flash(f'updated without image{staffid}')
            except:
                conn.rollback()
                flash('not updated --failed')
            conn.close()
            return redirect(url_for('staff',username=username))
        else:
            return render_template('notallowed.html',username=username)
    return redirect('/stafflogin')


@app.route("/updatecriminal/<username>/<criminalid>",methods=['GET','POST'])
def criminalupdate(username,criminalid):
    global status
    global designation
    global workingcondition
    if 'user' in session and status=='staff':
        if designation=='technical' and workingcondition=='wor':
            conn = sqlite3.connect('POLICE_RECORD.db')
            cursor=conn.cursor()
            try:
                if request.method=='POST':
                    image=request.files['image']
                    if image.filename!="":
                        if not allowed_file(image.filename):
                            flash('Invalid file format. Only JPG GIF png jpeg files are allowed.')
                        elif image:
                            filename = secure_filename(image.filename)
                            image_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                            image.save(image_path)
                            cursor.execute('''UPDATE criminal SET NAME=?,PHONENUMBER=?,AGE=?,GENDER=?,DOB=?,JAILED=?,IMAGE=?,ADDRESS=? WHERE ID=?''',
                                           (request.form.get("criminal_name"), 
                                            request.form.get('phone'), 
                                            request.form.get('age'), 
                                            request.form.get('gen'),
                                            request.form.get('dob'),
                                            request.form.get('jailed'),
                                            filename,
                                            request.form.get('add').lower(),criminalid)) 
                            conn.commit()
                            flash(f'updated with image{criminalid}')
                    else:
                        cursor.execute('''UPDATE criminal SET NAME=?,PHONENUMBER=?,AGE=?,GENDER=?,DOB=?,JAILED=?,ADDRESS=? WHERE ID=?''',
                                           (request.form.get("criminal_name"), 
                                            request.form.get('phone'), 
                                            request.form.get('age'), 
                                            request.form.get('gen'),
                                            request.form.get('dob'),
                                            request.form.get('jailed'),
                                            request.form.get('add').lower(),criminalid))
                        conn.commit()
                        flash(f'updated without image{criminalid}')
            except:
                conn.rollback()
                flash('not updated --failed')
            conn.close()
            return redirect(url_for('criminal',username=username))
        else:
            return render_template('notallowed.html',username=username)
    return redirect('/stafflogin')

if __name__=="__main__":
    app.run(debug=True)
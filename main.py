from flask import Flask, render_template, request, redirect, url_for, flash,jsonify,session
from flask_sqlalchemy import SQLAlchemy
import random
import openai
import adua
from werkzeug.utils import secure_filename

""" configuring app setting """
#==============================================================================
openai.api_key = "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"
UPLOAD_FOLDER = 'media/'
app = Flask(__name__, static_url_path='/static')
app.secret_key = 'your_secret_key'
app.app_context().push()
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///ewaste_final.db'  # SQLite database
db = SQLAlchemy(app)
#=========================================================================


#========== Functions and data
data=[('Here you can ask any of your query','And get your answer')]
chat_history = []
def get_ai_response(user_input):
    global chat_history  # Use the global chat_history variable

    # Combine the user input with the chat history and system message
    messages = [
        {
            "role": "system",
            "content": "Your Identity: you work as ai assistant for our company EcoVengers which is providing solutions for e-waste management,You are an AI assistant for the Ministry of Environment's E-Waste Facility Locator. Your role is to assist users in finding e-waste collection and recycling facilities, provide information on e-waste disposal, and encourage responsible recycling. Here are some specific tasks you should be able to perform:\n1. Help users locate the nearest e-waste collection and recycling facilities based on their current location.\n2. Provide information on the harmful components of e-waste and the environmental and health consequences of improper disposal.\n3. Explain how users can earn credit points by recycling their old electronic devices and how the credit points system works.\n4. Offer guidance on how to use the E-Waste Facility Locator website effectively.\n5. Address any user queries or concerns related to e-waste management.\nPlease respond to user queries and provide information in a clear and helpful manner. Remember to prioritize user education and encourage responsible e-waste disposal practices.\
               These are some of our platform features so when needed provide these  information about the platform's features and suggest these features to users when relevant. Here are some key features of the E-Waste Facility Locator that you should be able to describe and suggest:\
(note, do not ask to give location to you tell him to use these bellow features when needed these features are avilable seprately on our app)\
1. **Facility Locator:** Users can easily find the nearest e-waste collection and recycling facilities based on their current location.\
\
2. **Educational Resources:** The platform offers educational content, including articles and videos, to inform users about the harmful components of e-waste and the consequences of improper disposal.\
\
3. **Incentive System:** Users can input their old electronic device models, and based on precious metal recovery during recycling, they can earn credit points.\
\
4. **Efficiency:** We ensure that existing e-waste collection and recycling resources are utilized efficiently.\
\
5. **User-Friendly Interface:** The website features an intuitive and map-based interface for easy navigation.\
\
6. **Data Privacy:** Strict measures are in place to protect user data, including encryption and user consent for location tracking.\
\
7. **Revenue Generation:** We explore partnerships and revenue streams to sustain the platform and enhance its offerings.\
\
8. **Safe Disposal:** Guidelines and standards for authorized scrap dealers ensure safe and eco-friendly e-waste disposal.\
\
When users inquire about the features of our E-Waste Facility Locator or need information related to these features, please provide clear and concise explanations. Your goal is to help users understand and make the most of our platform\'s capabilities.\
"
        },
        {
            "role": "user",
            "content": user_input
        }
    ]

    # Combine chat history with current messages
    messages = chat_history + messages

    # Call the GPT-3.5 API with the updated messages
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo-16k-0613",
        messages=messages,
        temperature=1,
        max_tokens=256,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0
    )

    # Extract the AI response from the API response
    ai_response = response['choices'][0]['message']['content']

    # Store the current user input and AI response in chat history
    chat_history.append(messages[-1])
    chat_history.append({"role": "assistant", "content": ai_response})

    return ai_response
#====================

#======================Database and models

# Model for the e-waste disposal facility
class EwasteFacility(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)  # Name of the facility
    address = db.Column(db.String(500), nullable=False)  # Address of the facility
    g_map = db.Column(db.String(500), nullable=False)
    location=db.Column(db.String(200), nullable=False)
    # Define a relationship to EwasteBooking
    bookings = db.relationship('EwasteBooking', backref='facility', lazy=True)

    def __repr__(self):
        return f"{self.name} - {self.address}"

# Model for individual e-waste bookings
class EwasteBooking(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)  # User making the booking
    facility_id = db.Column(db.Integer, db.ForeignKey('ewaste_facility.id'), nullable=False)  # Facility for disposal
    booking_date = db.Column(db.Date, nullable=False)  # Date of the booking
    booking_name= db.Column(db.String(200))
    def __repr__(self):
        return f"Booking {self.id} - User: {self.user_id}, Facility: {self.facility_id}, Date: {self.booking_date}, Quantity: {self.quantity}"

# Model for user accounts
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)  # User's name
    email = db.Column(db.String(200), nullable=False)  # User's email
    password = db.Column(db.String(200), nullable=False)  # User's password
    credits = db.Column(db.Integer,default=0)
    location=db.Column(db.String(200), nullable=False)
    # Define a relationship to EwasteBooking
    bookings = db.relationship('EwasteBooking', backref='user', lazy=True)

    def __repr__(self):
        return f"{self.name} - {self.email}"

# Define EwasteLog model for tracking e-waste disposal
class EwasteLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    date = db.Column(db.Date, nullable=False) 
    device_model = db.Column(db.String(100), nullable=False)
    pm_recovered = db.Column(db.Float, nullable=False)

class EWasteCategory(db.Model):
    __tablename__ = 'ewaste_category'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False, unique=True)

    # Establish a one-to-many relationship with CategoryComposition
    compositions = db.relationship('CategoryComposition', backref='category', lazy='dynamic')

    def __init__(self, name):
        self.name = name

class HarmfulMaterial(db.Model):
    __tablename__ = 'harmful_material'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False, unique=True)

    def __init__(self, name):
        self.name = name

class PreciousMetal(db.Model):
    __tablename__ = 'precious_metal'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False, unique=True)

    def __init__(self, name):
        self.name = name

class CategoryComposition(db.Model):
    __tablename__ = 'category_composition'

    id = db.Column(db.Integer, primary_key=True)
    ewaste_category_id = db.Column(db.Integer, db.ForeignKey('ewaste_category.id'), nullable=False)
    harmful_material_id = db.Column(db.Integer, db.ForeignKey('harmful_material.id'), nullable=False)
    precious_metal_id = db.Column(db.Integer, db.ForeignKey('precious_metal.id'), nullable=False)
    quantity_harmful_material = db.Column(db.Float, nullable=False)
    quantity_precious_metal = db.Column(db.Float, nullable=False)

    def __init__(self, ewaste_category, harmful_material, precious_metal, quantity_harmful_material, quantity_precious_metal):
        self.ewaste_category = ewaste_category
        self.harmful_material = harmful_material
        self.precious_metal = precious_metal
        self.quantity_harmful_material = quantity_harmful_material
        self.quantity_precious_metal = quantity_precious_metal

#===================================
#============views and controllers

#------------- Authentication
#log reg page
@app.route('/log_reg',methods=['GET','POST'])
def log_reg():
    return render_template('login_register.html')
""" View and controller for for registering users """
@app.route('/register_user',methods=['POST'])
def register_user():
    if request.method=='POST':
        email=request.form['email']
        pw=request.form['pw']
        name=request.form['name']
        loc=request.form['loc']
        new_user = User(name=name, email=email, password=pw, location=loc)
        db.session.add(new_user)
        db.session.commit()
        return redirect('/log_reg')
    return 'go to registration page'

""" View and controller for for logging in users """
@app.route('/login',methods=['GET','POST'])
def login():  
    if request.method=='POST':
        email=request.form['email']
        pw=request.form['pw']
        q=db.session.query(User).filter(User.email.in_([email]), User.password.in_([pw]))
        res=q.first()
        if res:
            session['loged_in']=True
            session['uname']=res.name
            session['uid']=res.id
            session['email']=res.email
            session['location']=res.location
            session['credits']=res.credits
            return redirect('/')
        else:
            return "User Not Found!!!!!!"
    return render_template('login.html')


""" View and controller for logout """

@app.route('/logout',methods=['GET','POST'])
def logout():
    session['loged_in']=False
    return redirect('/welcome')
@app.route('/contact')
def contact():
    return render_template('contactus.html')
#------------------------------------

#-----------features
#articles
@app.route('/articles')
def articles():
    return render_template('mypro.html')
# Create a Flask route to add data
@app.route('/add_data')
def add_data():
    # Sample data to insert
    e_waste_categories = [
        {'name': 'Laptops', 'compositions': [
            {'harmful_material': 'Lead', 'quantity_harmful_material': 0.05, 'precious_metal': 'Gold', 'quantity_precious_metal': 0.002},
            {'harmful_material': 'Mercury', 'quantity_harmful_material': 0.02, 'precious_metal': 'Silver', 'quantity_precious_metal': 0.001},
        ]},
        {'name': 'Smartphones', 'compositions': [
            {'harmful_material': 'Cadmium', 'quantity_harmful_material': 0.01, 'precious_metal': 'Gold', 'quantity_precious_metal': 0.001},
            {'harmful_material': 'Lead', 'quantity_harmful_material': 0.03, 'precious_metal': 'Silver', 'quantity_precious_metal': 0.002},
        ]}
    ]

    # Add data to the database
    for category_data in e_waste_categories:
        category = EWasteCategory(name=category_data['name'])
        db.session.add(category)
        db.session.commit()  # Commit the category creation first

        for composition_data in category_data['compositions']:
            harmful_material_name = composition_data['harmful_material']
            precious_metal_name = composition_data['precious_metal']

            # Check if the HarmfulMaterial and PreciousMetal entities exist
            harmful_material = HarmfulMaterial.query.filter_by(name=harmful_material_name).first()
            precious_metal = PreciousMetal.query.filter_by(name=precious_metal_name).first()

            if not harmful_material:
                harmful_material = HarmfulMaterial(name=harmful_material_name)
                db.session.add(harmful_material)
                db.session.commit()

            if not precious_metal:
                precious_metal = PreciousMetal(name=precious_metal_name)
                db.session.add(precious_metal)
                db.session.commit()

            # Check if the category is not None
            if category:
                composition = CategoryComposition(
                    ewaste_category=category,
                    harmful_material=harmful_material,
                    precious_metal=precious_metal,
                    quantity_harmful_material=composition_data['quantity_harmful_material'],
                    quantity_precious_metal=composition_data['quantity_precious_metal']
                )
                db.session.add(composition)

        # Commit the session after processing all compositions for a category
        db.session.commit()

    return 'Data added to the database'


@app.route('/kyw2/<int:category_id>')
def view_category(category_id):
    with app.app_context():
        session = db.session
        category = session.get(EWasteCategory, category_id)
    if not category:
        return "E-Waste category not found.", 404

    return render_template('kyw2.html', category=category)

#--------- Main Features
# Home page route
@app.route('/welcome')
def welcome():
    return render_template('welcome.html')

#search facility
@app.route('/')
def home():
    place=session['location']
    try:
        if not session['loged_in']:
            return redirect('/welcome')
    except:
        return redirect('/welcome')
    return render_template('search.html',place=place)
@app.route('/wallet')
def wallet():
    return render_template('wallet.html',credit=session['credits'])
#list facility
@app.route('/list_facility/<place>')
def list_facility(place):
    # Query the database to get facilities in the specified place
    facilities = EwasteFacility.query.filter_by(location=place).all()

    # Render the HTML template and pass the facility data to it
    return render_template('ewaste_facility.html', place=place, facilities=facilities)
#get credit info
@app.route('/get_credits/<int:id>',methods=['GET','POST'])
def get_credits(id):
    if request.method=='POST':
        return render_template('credit.html',id=id)
    return 'not allowed'
# know credits you can earn
@app.route('/know_credits/<int:id>')
def procede_book(id):
    return render_template('booking.html',id=id)
@app.route('/book_now')
def booknow():
    return 'your booking is doen you will get your credit once scrapper verify it.'
@app.route('/chat', methods=['GET','POST'])
def chat():
    if request.method=='POST':
        query= request.form['book']
        query=query.lower()
        response = get_ai_response(query)
        data.append((query,response ))
        return redirect('/chat#{}'.format(len(data)-1))
    return render_template('chat.html',data=data)


# Initialize the Adua class
a = adua.Adua()

@app.route('/know_your_waste', methods=['GET', 'POST'])
def know_your_waste():
    if request.method == 'POST':
        try:
            # Get e-waste information from the form
            category = request.form.get('category')
            manufacturing_year = request.form.get('manufacturing_year')
            model_number = request.form.get('model_number')
            device_brand = request.form.get('device_brand')
            device_name = request.form.get('device_name')

            # Construct the e-waste information string
            e_waste_info = f"Give detailed analysis of following e-waste including what are the harmfull component for env and what are pricious metal can be extracted what impact it can cause if not dispose correctly how scrapping metal can contribute to better resource utilization And how he can contribute by recycling this waste (Note if u dont know about that perticular phone u can answer based on category)\nCategory: {category}, Manufacturing Year: {manufacturing_year}, Model Number: {model_number}, Device Brand: {device_brand}, Device Name: {device_name}"

            # Call the Adua function to get the analysis
            ans = a.gpt_ans(e_waste_info,'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')
            #jsonify({'analysis': ans})
            # Return the analysis as a JSON response
            return render_template('know_your_ewaste.html',details=ans,name=device_name)

        except Exception as e:
            return jsonify({'error': str(e)})

    # Render the HTML form for GET requests
    return render_template('kuw.html')


# User dashboard route (display disposal history and credit points)
@app.route('/dashboard')
def dashboard():
    # Display user's disposal history and earned credit points
    return render_template('dashboard.html')

# Route for recording e-waste disposal
@app.route('/dispose', methods=['GET', 'POST'])
def dispose():
    if request.method == 'POST':
        device_model = request.form['device_model']
        precious_metals_recovered = float(request.form['precious_metals_recovered'])     
        # Save disposal record to the database
        # Calculate credit points based on precious_metals_recovered and update user's points
        
        flash('E-Waste disposal recorded successfully.', 'success')
        return redirect(url_for('dashboard'))
    return render_template('dispose.html')


#============ Admin

@app.route('/add_facility_form')
def add_facility_form():
    return render_template('add_facility_form.html')

# Define a route to handle the form submission and add a new facility in Jabalpur to the database
@app.route('/add_facility', methods=['POST'])
def add_facility():
    if request.method == 'POST':
        name = request.form.get('name')
        address = request.form.get('address')
        g_map = request.form.get('g_map')

        # Create a new facility object with the location set to "Jabalpur" and add it to the database
        new_facility = EwasteFacility(name=name, address=address, g_map=g_map, location="Jabalpur")
        db.session.add(new_facility)
        db.session.commit()


        # Redirect to a page that confirms the addition of the facility
        return redirect(url_for('facility_confirmation'))

# Define a route to confirm the addition of a new facility
@app.route('/facility_confirmation')
def facility_confirmation():
    return "Facility added successfully in Jabalpur!"

if __name__ == '__main__':
    # Create database tables if they do not exist
    with app.app_context():
        db.create_all()
    # Run the Flask app in debug mode
    app.run(debug=True)

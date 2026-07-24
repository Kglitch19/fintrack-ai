from flask import Flask, jsonify, render_template, request, redirect, url_for, session, flash
import sqlite3, os, re
import pickle
with open("model.pkl", "rb") as f:
    vectorizer, nb_model = pickle.load(f)
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
import pandas as pd
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Replace with a secure key!
data = pd.read_csv("data/financial_data.csv")
with open('model.pkl', 'rb') as f:
    vectorizer, model = pickle.load(f)



@app.route('/')
def home():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    with sqlite3.connect('fintrack.db') as conn:
        c = conn.cursor()
        c.execute('SELECT Transaction_id, Amount, Transaction_type, Description FROM Transactions WHERE User_id = ?', (session['user_id'],))
        transactions = c.fetchall()

        c.execute('SELECT Name FROM Users WHERE User_id = ?', (session['user_id'],))
        username = c.fetchone()[0]

    total_income = sum(t[1] for t in transactions if t[2] == "income")
    total_expenses = sum(t[1] for t in transactions if t[2] == "expense")
   
    return render_template('home.html', transactions=transactions, username=username, total_income=total_income, total_expenses=total_expenses)



@app.route('/about')
def about():
    return render_template('about.html')



@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']
        confirm_password = request.form['confirm_password']

        if password != confirm_password:
            flash("❌ Passwords do not match", "error")
            return render_template('signup.html')
            #return "Passwords do not match"
        
        if len(password) < 8 or not re.search(r'[A-Z]', password) or not re.search(r'\d', password):
            flash("❌ Password too weak — must be at least 8 chars, 1 capital letter, 1 number", "error")
            return render_template('signup.html')
            # return "Password too weak — must be at least 8 chars, 1 capital letter, 1 number"

        hashed_password = generate_password_hash(password)

        conn = sqlite3.connect('fintrack.db')
        cursor = conn.cursor()
        try:
            cursor.execute('INSERT INTO Users (Name, Email, Password_Hash) VALUES (?, ?, ?)',
                           (name, email, hashed_password))
            conn.commit()
        except sqlite3.IntegrityError:
            flash("❌ Email already registered.", "error")
            return render_template('signup.html')
            # return "Email already registered."
        finally:
            conn.close()

        flash("✅ Signup successful! Please login.", "success")
        return redirect(url_for('login'))
    return render_template('signup.html')



@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        print("Received POST request")
        email = request.form['email']
        password = request.form['password']

        try: 
            conn = sqlite3.connect('fintrack.db')
            cursor = conn.cursor()
            cursor.execute('SELECT User_id, Password_Hash FROM Users WHERE Email = ?', (email,))
            user = cursor.fetchone()
        except sqlite3.Error as e:
            flash("❌ Something went wrong. Please try again.", "error")
            print(f"Database error: {e}")
            return render_template('login.html')
        finally: 
            conn.close()

        if user and check_password_hash(user[1], password):
            session['user_id'] = user[0]
            print("Login successful")
            return redirect(url_for('home'))
        else:
            '''print("Invalid credentials")
            return "Invalid credentials"'''
            flash("❌ Invalid credentials", "error")
            return render_template('login.html')
        
    return render_template('login.html')

@app.context_processor
def inject_user():
    if 'user_id' in session:
        conn = sqlite3.connect('fintrack.db')
        c = conn.cursor()
        c.execute('SELECT Name FROM Users WHERE User_id = ?', (session['user_id'],))
        result = c.fetchone()
        conn.close()
        if result:
            return dict(username=result[0])
    return dict(username=None)



@app.route('/profile', methods=['GET', 'POST'])
def profile():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    conn = sqlite3.connect('fintrack.db')
    c = conn.cursor()

    updated = False
    username = email = None  # default

    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']

        # Handle profile picture upload
        if 'profile_pic' in request.files:
            pic = request.files['profile_pic']
            if pic and pic.filename != '':
                ext = os.path.splitext(pic.filename)[1].lower()
                filename = f"{session['user_id']}{ext}"
                save_path = os.path.join(app.root_path, 'static', 'profile_pics', filename)
                pic.save(save_path)

                session['profile_pic_ext'] = ext
                updated = True

        # Check if user details changed
        c.execute('SELECT Name, Email FROM Users WHERE User_id = ?', (session['user_id'],))
        current_user = c.fetchone()

        if current_user and (username != current_user[0] or email != current_user[1]):
            c.execute('UPDATE Users SET Name = ?, Email = ? WHERE User_id = ?',
                      (username, email, session['user_id']))
            conn.commit()
            updated = True

        if updated:
            flash('Profile updated successfully!', 'success')

    # Load user info for display
    c.execute('SELECT Name, Email FROM Users WHERE User_id = ?', (session['user_id'],))
    user = c.fetchone()
    conn.close()

    # Determine profile pic URL
    ext = session.get('profile_pic_ext', '.jpg')
    profile_pic_url = url_for('static', filename=f'profile_pics/{session["user_id"]}{ext}')

    return render_template(
        'profile.html',
        username=user[0],
        email=user[1],
        profile_pic_url=profile_pic_url
    )



''' working code
@app.route('/profile', methods=['GET', 'POST'])
def profile():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    conn = sqlite3.connect('fintrack.db')
    c = conn.cursor()

    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']

        # Handle profile picture upload
        if 'profile_pic' in request.files:
            pic = request.files['profile_pic']
            if pic and pic.filename != '':
                ext = os.path.splitext(pic.filename)[1].lower()  # keep the correct extension
                filename = f"{session['user_id']}{ext}"
                save_path = os.path.join(app.root_path, 'static', 'profile_pics', filename)
                pic.save(save_path)

                # Store extension in session (since DB doesn't have a profile_pic column)
                session['profile_pic_ext'] = ext

        # Update user details
        c.execute('UPDATE Users SET Name = ?, Email = ? WHERE User_id = ?',
                  (username, email, session['user_id']))
        conn.commit()
        flash('Profile updated successfully!')

    # Load updated info
    c.execute('SELECT Name, Email FROM Users WHERE User_id = ?', (session['user_id'],))
    user = c.fetchone()
    conn.close()

    # Determine profile pic URL
    ext = session.get('profile_pic_ext', '.jpg')  # default to .jpg if nothing uploaded
    profile_pic_url = url_for('static', filename=f'profile_pics/{session['user_id']}{ext}')

    return render_template(
        'profile.html',
        username=user[0],
        email=user[1],
        profile_pic_url=profile_pic_url
    )
'''


@app.route('/predict', methods=['POST'])
def predict():
    income = float(request.form['income'])
    expense = float(request.form['expense'])

    with open("nb_model.pkl", "rb") as f:
        model = pickle.load(f)

    result = model.predict([[income, expense]])[0]
    return render_template("prediction.html", prediction=result)



@app.route('/add_transaction', methods=['POST'])
def add_transaction():
    if 'user_id' not in session:
        return redirect(url_for('login'))  # Make sure user is logged in
    print(f"Raw amount received: '{request.form.get('amount')}'")
    try:
        amount = float(request.form['amount'])
    except ValueError:
        flash("❌ Amount must be a number", "error")
        return redirect(url_for('home'))

    if amount <= 0:
        print("Negative amount blocked")
        flash("❌ Amount must be greater than zero", "error")
        return redirect(url_for('home'))    

    transaction_type = request.form['transaction_type'].lower().strip()
    description = request.form['description']
    user_id = session['user_id']

    try:
        with sqlite3.connect('fintrack.db') as conn:
            c = conn.cursor()
            c.execute('''
                INSERT INTO Transactions (User_id, Amount, Transaction_type, transaction_date, description)
                VALUES (?, ?, ?, ?, ?)
            ''', (user_id, amount, transaction_type, datetime.now(), description))
            conn.commit()
    except sqlite3.Error as e:
        flash("❌ Could not save transaction. Please try again.", "error")
        print(f"Database error: {e}")
        
    return redirect(url_for('home'))



@app.route('/edit_transaction/<int:transaction_id>', methods=['GET', 'POST'])
def edit_transaction(transaction_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))

    with sqlite3.connect('fintrack.db') as conn:
        c = conn.cursor()

        if request.method == 'POST':
            amount = request.form['amount']
            description = request.form['description']
            c.execute('''
                UPDATE Transactions
                SET Amount = ?, description = ?
                WHERE Transaction_id = ? AND User_id = ?
            ''', (amount, description, transaction_id, session['user_id']))
            conn.commit()
            return redirect(url_for('home'))

        c.execute('SELECT Amount, description FROM Transactions WHERE Transaction_id = ? AND User_id = ?', (transaction_id, session['user_id']))
        transaction = c.fetchone()

    return render_template('edit_transaction.html', transaction=transaction)



@app.route('/delete_transaction/<int:transaction_id>')
def delete_transaction(transaction_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))

    with sqlite3.connect('fintrack.db') as conn:
        c = conn.cursor()
        c.execute('DELETE FROM Transactions WHERE Transaction_id = ? AND User_id = ?', (transaction_id, session['user_id']))
        conn.commit()

    return redirect(url_for('home'))



@app.route('/data')
def get_data():
    return jsonify(data.to_dict(orient='records'))

def get_incomes(user_id):
    """Fetch all income transactions for a user."""
    with sqlite3.connect('fintrack.db') as conn:
        conn.row_factory = sqlite3.Row
        c = conn.cursor()
        c.execute("""
            SELECT description AS source, Amount AS amount
            FROM Transactions
            WHERE User_id = ? AND Transaction_type = 'income'
        """, (user_id,))
        return c.fetchall()

def get_expenses(user_id):
    """Fetch all expense transactions for a user."""
    with sqlite3.connect('fintrack.db') as conn:
        conn.row_factory = sqlite3.Row
        c = conn.cursor()
        c.execute("""
            SELECT description AS category, Amount AS amount
            FROM Transactions
            WHERE User_id = ? AND Transaction_type = 'expense'
        """, (user_id,))
        return c.fetchall()



@app.route('/analysis')
def analysis():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    user_id = session['user_id']

    # fetch username
    with sqlite3.connect('fintrack.db') as conn:
        c = conn.cursor()
        c.execute('SELECT Name FROM Users WHERE User_id = ?', (user_id,))
        row = c.fetchone()
    conn.close()

    username = row[0] if row else "Unknown"

    # Fetch data from Transactions
    incomes_data = get_incomes(user_id)
    expenses_data = get_expenses(user_id)

    incomes = [row['amount'] for row in incomes_data]
    expenses = [row['amount'] for row in expenses_data]

    income_labels = [row['source'] for row in incomes_data]
    expense_labels = [row['category'] for row in expenses_data]

    total_income = sum(incomes) if incomes else 0
    total_expenses = sum(expenses) if expenses else 0

    # Categories aggregation for expenses
    category_totals = {}
    for row in expenses_data:
        cat = row['category']
        amt = row['amount']
        category_totals[cat] = category_totals.get(cat, 0) + amt

    # --- ML Suggestion / Prediction ---
    suggestion = "Your spending looks balanced."
    if total_expenses > total_income:
        suggestion = "Warning: Expenses exceed income. Reduce spending."
    elif total_income > 0 and total_expenses > 0:
        ratio = total_expenses / total_income
        if ratio > 0.7:
            suggestion = "Caution: Spending over 70% of income."
        elif ratio < 0.4:
            suggestion = "Good job! Saving more than 60% of income."

    # Predictive step: simple trend-based projection
    if len(expenses) > 2:
        avg_expense = sum(expenses[:-1]) / (len(expenses) - 1)
        predicted_next = avg_expense * 1.05  # assume ~5% growth
        if predicted_next > total_income:
            suggestion += " Next month, you may overspend based on recent trends."

    
    # AI-based top expense category
    top_category = None
    top_amount = 0

    if expenses_data:
        # Get descriptions of all expenses for this user
        descriptions = [row['category'] for row in expenses_data]
        amounts = [row['amount'] for row in expenses_data]

        # Transform and predict categories
        X_vec = vectorizer.transform(descriptions)
        predicted_categories = model.predict(X_vec)

        # Aggregate predicted totals
        predicted_totals = {}
        for cat, amt in zip(predicted_categories, amounts):
            predicted_totals[cat] = predicted_totals.get(cat, 0) + amt

        # Find the highest expense category
        top_category, top_amount = max(predicted_totals.items(), key=lambda x: x[1])

    return render_template(
        'analysis.html',
        incomes=incomes, expenses=expenses, username=username,
        income_labels=income_labels, expense_labels=expense_labels,
        income_values=incomes, expense_values=expenses,
        total_income=total_income, total_expenses=total_expenses,
        category_labels=list(category_totals.keys()),
        category_values=list(category_totals.values()),
        ratio_labels=["Income", "Expenses"],
        ratio_values=[total_income, total_expenses],
        ml_suggestion=suggestion,
        top_category=top_category,
        top_amount=top_amount
    )




@app.route('/logout', methods=['POST'])
def logout():
    session.clear()  # wipe out all session data, including flash leftovers
    flash("You have been logged out.", "info")
    # session.pop('user_id', None)
    return redirect(url_for('login'))



if __name__ == '__main__':
    app.run(debug=True)


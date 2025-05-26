from flask import Flask, render_template, redirect, url_for, flash, request, jsonify
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from werkzeug.urls import url_parse
from datetime import datetime, timedelta
from sqlalchemy import func, extract
import os
from dotenv import load_dotenv
from models import db, User, Category, Transaction
from forms import LoginForm, RegistrationForm, TransactionForm, CategoryForm

# Load environment variables
load_dotenv()

# Create Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev')
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///finance_tracker.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize extensions
db.init_app(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Create database tables
with app.app_context():
    db.create_all()

# Auth routes
@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password', 'danger')
            return redirect(url_for('login'))
        
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('dashboard')
        return redirect(next_page)
    
    return render_template('login.html', title='Sign In', form=form)

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Congratulations, you are now a registered user!', 'success')
        return redirect(url_for('login'))
    
    return render_template('register.html', title='Register', form=form)

# Dashboard route
@app.route('/')
@app.route('/dashboard')
@login_required
def dashboard():
    # Get current month's totals
    current_month = datetime.now().month
    current_year = datetime.now().year
    
    monthly_totals = Transaction.query.with_entities(
        Transaction.type,
        func.sum(Transaction.amount).label('total')
    ).filter(
        Transaction.user_id == current_user.id,
        extract('month', Transaction.date) == current_month,
        extract('year', Transaction.date) == current_year
    ).group_by(Transaction.type).all()
    
    # Calculate current balance
    income = next((t[1] for t in monthly_totals if t[0] == 'income'), 0)
    expenses = next((t[1] for t in monthly_totals if t[0] == 'expense'), 0)
    balance = income - expenses
    
    # Get recent transactions
    recent_transactions = Transaction.query.filter_by(
        user_id=current_user.id
    ).order_by(Transaction.date.desc()).limit(5).all()
    
    return render_template('dashboard.html',
                         title='Dashboard',
                         balance=balance,
                         income=income,
                         expenses=expenses,
                         recent_transactions=recent_transactions)

# Transaction routes
@app.route('/transactions')
@login_required
def transactions():
    # Get filter parameters
    month = request.args.get('month', type=int, default=datetime.now().month)
    year = request.args.get('year', type=int, default=datetime.now().year)
    
    # Build query
    query = Transaction.query.filter_by(user_id=current_user.id)
    if month and year:
        query = query.filter(
            extract('month', Transaction.date) == month,
            extract('year', Transaction.date) == year
        )
    
    transactions = query.order_by(Transaction.date.desc()).all()
    
    return render_template('transactions.html',
                         title='Transactions',
                         transactions=transactions,
                         current_month=month,
                         current_year=year)

@app.route('/transactions/new', methods=['GET', 'POST'])
@login_required
def new_transaction():
    form = TransactionForm()
    form.category_id.choices = [(0, 'None')] + [
        (c.id, c.name) for c in current_user.categories
    ]
    
    if form.validate_on_submit():
        transaction = Transaction(
            user_id=current_user.id,
            amount=form.amount.data,
            type=form.type.data,
            date=form.date.data,
            description=form.description.data
        )
        if form.category_id.data and form.category_id.data != 0:
            transaction.category_id = form.category_id.data
        
        db.session.add(transaction)
        db.session.commit()
        flash('Transaction added successfully!', 'success')
        return redirect(url_for('transactions'))
    
    return render_template('transaction_form.html',
                         title='New Transaction',
                         form=form)

@app.route('/transactions/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit_transaction(id):
    transaction = Transaction.query.filter_by(
        id=id,
        user_id=current_user.id
    ).first_or_404()
    
    form = TransactionForm(obj=transaction)
    form.category_id.choices = [(0, 'None')] + [
        (c.id, c.name) for c in current_user.categories
    ]
    
    if form.validate_on_submit():
        transaction.amount = form.amount.data
        transaction.type = form.type.data
        transaction.date = form.date.data
        transaction.description = form.description.data
        transaction.category_id = form.category_id.data if form.category_id.data != 0 else None
        
        db.session.commit()
        flash('Transaction updated successfully!', 'success')
        return redirect(url_for('transactions'))
    
    return render_template('transaction_form.html',
                         title='Edit Transaction',
                         form=form)

@app.route('/transactions/<int:id>/delete', methods=['POST'])
@login_required
def delete_transaction(id):
    transaction = Transaction.query.filter_by(
        id=id,
        user_id=current_user.id
    ).first_or_404()
    
    db.session.delete(transaction)
    db.session.commit()
    flash('Transaction deleted successfully!', 'success')
    return redirect(url_for('transactions'))

# Category routes
@app.route('/categories')
@login_required
def categories():
    categories = Category.query.filter_by(user_id=current_user.id).all()
    return render_template('categories.html',
                         title='Categories',
                         categories=categories)

@app.route('/categories/new', methods=['GET', 'POST'])
@login_required
def new_category():
    form = CategoryForm(current_user.id)
    if form.validate_on_submit():
        category = Category(
            user_id=current_user.id,
            name=form.name.data
        )
        db.session.add(category)
        db.session.commit()
        flash('Category added successfully!', 'success')
        return redirect(url_for('categories'))
    
    return render_template('category_form.html',
                         title='New Category',
                         form=form)

@app.route('/categories/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit_category(id):
    category = Category.query.filter_by(
        id=id,
        user_id=current_user.id
    ).first_or_404()
    
    form = CategoryForm(current_user.id, obj=category)
    if form.validate_on_submit():
        category.name = form.name.data
        db.session.commit()
        flash('Category updated successfully!', 'success')
        return redirect(url_for('categories'))
    
    return render_template('category_form.html',
                         title='Edit Category',
                         form=form)

@app.route('/categories/<int:id>/delete', methods=['POST'])
@login_required
def delete_category(id):
    category = Category.query.filter_by(
        id=id,
        user_id=current_user.id
    ).first_or_404()
    
    if category.transactions.count() > 0:
        flash('Cannot delete category with existing transactions.', 'danger')
        return redirect(url_for('categories'))
    
    db.session.delete(category)
    db.session.commit()
    flash('Category deleted successfully!', 'success')
    return redirect(url_for('categories'))

# API routes for charts
@app.route('/api/transactions/summary')
@login_required
def transaction_summary():
    # Get monthly summary for the last 6 months
    six_months_ago = datetime.now() - timedelta(days=180)
    
    monthly_summary = db.session.query(
        extract('month', Transaction.date).label('month'),
        extract('year', Transaction.date).label('year'),
        Transaction.type,
        func.sum(Transaction.amount).label('total')
    ).filter(
        Transaction.user_id == current_user.id,
        Transaction.date >= six_months_ago
    ).group_by(
        extract('month', Transaction.date),
        extract('year', Transaction.date),
        Transaction.type
    ).all()
    
    # Format data for Chart.js
    months = []
    income_data = []
    expense_data = []
    
    for month, year, type_, total in monthly_summary:
        month_year = f"{int(month)}/{int(year)}"
        if month_year not in months:
            months.append(month_year)
            income_data.append(0)
            expense_data.append(0)
        
        idx = months.index(month_year)
        if type_ == 'income':
            income_data[idx] = float(total)
        else:
            expense_data[idx] = float(total)
    
    return jsonify({
        'labels': months,
        'datasets': [
            {
                'label': 'Income',
                'data': income_data,
                'borderColor': 'rgb(75, 192, 192)',
                'tension': 0.1
            },
            {
                'label': 'Expenses',
                'data': expense_data,
                'borderColor': 'rgb(255, 99, 132)',
                'tension': 0.1
            }
        ]
    })

@app.route('/api/categories/summary')
@login_required
def category_summary():
    # Get category totals for the current month
    current_month = datetime.now().month
    current_year = datetime.now().year
    
    category_totals = db.session.query(
        Category.name,
        func.sum(Transaction.amount).label('total')
    ).join(Transaction).filter(
        Category.user_id == current_user.id,
        Transaction.type == 'expense',
        extract('month', Transaction.date) == current_month,
        extract('year', Transaction.date) == current_year
    ).group_by(Category.name).all()
    
    return jsonify({
        'labels': [c[0] for c in category_totals],
        'data': [float(c[1]) for c in category_totals]
    })

if __name__ == '__main__':
    app.run(debug=True) 
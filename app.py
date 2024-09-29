#------------------------------------------------
# imports
#------------------------------------------------
from datetime import datetime
import json
from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from enum import Enum
# from mockup.initialize import clear_all_models, update_all_tables

#------------------------------------------------
# configurations 
#------------------------------------------------

app = Flask(__name__)

# Enable CORS for all routes
CORS(app)

# Configurations for the database - sqlite
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///library.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

#init SQLAlchemy
db = SQLAlchemy(app)

#------------------------------------------------
# models definition & ENUM
#------------------------------------------------

class LoanType(Enum):
    SHORT_TERM = 1  # Up to 10 days
    MEDIUM_TERM = 2  # Up to 5 days
    LONG_TERM = 3   # Up to 2 days

# Book model
class Book(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(255), nullable=False)
    author = db.Column(db.String(255), nullable=False)
    year_published = db.Column(db.Integer, nullable=True)
    type = db.Column(db.Integer, db.CheckConstraint('type IN (1, 2, 3)'), nullable=False)  # Using integer enum
    is_available = db.Column(db.Boolean, default=True, nullable=False)

    def __repr__(self):
        return f"<Book {self.name}>"

# Customers model
class Customer(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(255), nullable = False)
    city = db.Column(db.String(255), nullable=True)
    age = db.Column(db.String(255), nullable=True)

    def __repr__(self):
        return f"<Customer {self.name}>"
    
# Loan model
class Loan(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True, nullable=False)  # Primary Key, autoincrement
    customer_id = db.Column(db.Integer, db.ForeignKey('customer.id'), nullable=False)  # Foreign key from Customer model
    book_id = db.Column(db.Integer, db.ForeignKey('book.id'), nullable=False)         # Foreign key from Book model
    loan_date = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)       # Default to current date/time
    return_date = db.Column(db.DateTime, nullable=True)                               # Can be null if not returned yet

    # Establish relationships (assuming you have Customer and Book models)
    customer = db.relationship('Customer', backref='loans', lazy=True)
    book = db.relationship('Book', backref='loans', lazy=True)

    def __repr__(self):
        return f"<Loan ID: {self.id}, Customer: {self.customer_id}, Book: {self.book_id}, Loan Date: {self.loan_date}>"


#------------------------------------------------
# Unit Testing - initializing database using jsons
#------------------------------------------------

# Clear existing models/tables
def clear_all_models():
    db.drop_all()
    db.session.commit()
    print("All models/tables have been dropped.")

# Function to load data from JSON file
def load_json_data(file_path):
    with open(file_path, 'r') as json_file:
        return json.load(json_file)

# Function to update the Books table
def update_books():
    books_data = load_json_data('./mockup/books.json')  # Adjust path as needed

    for book_data in books_data:
        book = db.session.get(Book, book_data['ID'])
        
        if not book:
            book = Book(
                id=book_data['ID'],
                name=book_data['name'],
                author=book_data['author'],
                year_published=book_data['year_published'],
                type=book_data['type'],
                is_available=book_data['is_available']
            )
            db.session.add(book)
        else:
            book.name = book_data['name']
            book.author = book_data['author']
            book.year_published = book_data['year_published']
            book.type = book_data['type']
            book.is_available = book_data['is_available']

    db.session.commit()
    print("Books table updated.")

# Function to update the Customers table
def update_customers():
    customers_data = load_json_data('./mockup/customers.json')  # Adjust path as needed

    for customer_data in customers_data:
        customer = db.session.get(Customer, customer_data['id'])
        
        if not customer:
            customer = Customer(
                id=customer_data['id'],
                name=customer_data['name'],
                city=customer_data['city'],
                age=customer_data['age']
            )
            db.session.add(customer)
        else:
            customer.name = customer_data['name']
            customer.city = customer_data['city']
            customer.age = customer_data['age']

    db.session.commit()
    print("Customers table updated.")

# Function to update the Loans table
def update_loans():
    loans_data = load_json_data('./mockup/loans.json')  # Adjust path as needed

    for loan_data in loans_data:
        loan = db.session.get(Loan, loan_data['id'])
        
        if not loan:
            loan = Loan(
                id=loan_data['id'],
                customer_id=loan_data['customer_id'],
                book_id=loan_data['book_id'],
                loan_date=datetime.fromisoformat(loan_data['loan_date']),
                return_date=datetime.fromisoformat(loan_data['return_date']) if loan_data['return_date'] else None
            )
            db.session.add(loan)
        else:
            loan.customer_id = loan_data['customer_id']
            loan.book_id = loan_data['book_id']
            loan.loan_date = datetime.fromisoformat(loan_data['loan_date'])
            loan.return_date = datetime.fromisoformat(loan_data['return_date']) if loan_data['return_date'] else None

    db.session.commit()
    print("Loans table updated.")

# Main function to update all tables
def update_all_tables():
    update_books()
    update_customers()
    update_loans()
    print("All tables updated from JSON files.")

def create_tables():
    db.create_all()
    print("All tables created successfully.")


#------------------------------------------------
# ####### Rest Api #######
#------------------------------------------------

# initialize database
@app.route('/initModels', methods = ['GET'])
def modelsInit():
    clear_all_models()
    create_tables()
    update_all_tables()
    return "tables updated"

#------------------------------------------------
# Item Addition 
#------------------------------------------------

# add a book
@app.route('/createBook', methods = ['POST'])
def createBook():
    try:
        data = request.get_json()
        
        name = data.get('name')
        author = data.get('author')
        type = data.get('type')
        year_published = data.get('year_published', None)

        if not name or not author or int(type) not in [1, 2, 3]:
            return jsonify({"error": "Invalid input. Name, author, and valid type (1, 2, or 3) are required."}), 400
        
        new_customer = Book(
            name = name,
            author = author,
            year_published = year_published,  # This can be None
            type = int(type),  # Now this is an integer
            is_available = True  # Assuming a new book is available by default
        )

        db.session.add(new_customer)
        db.session.commit()
        
        return jsonify({
                'message': 'successful book addition',
                'book':
                {
                    'id':new_customer.id,
                    'name':new_customer.name,
                    'author':new_customer.author,
                    'year_published':new_customer.year_published,
                    'type':new_customer.type
                }}), 201
    except Exception as e:
        jsonify({
            'message': 'error',
            'error': e,
        }), 500

# add a customer
@app.route('/createCustomer', methods = ['POST'])
def createCustomer():
    try:
        data = request.get_json()
        
        name = data.get('name')
        city = data.get('city', None)
        age = data.get('age', None)

        if not name:
            return jsonify({"error": "Invalid input. Name required."}), 400
        
        new_customer = Customer(
            name = name,
            city = city,
            age = age
        )

        db.session.add(new_customer)
        db.session.commit()
        
        return jsonify({
                'message': 'successful customer addition',
                'customer':
                {
                    'id':new_customer.id,
                    'name':new_customer.name,
                    'city':new_customer.city,
                    'age':new_customer.age,
                }}), 201
    except Exception as e:
        jsonify({
            'message': 'error',
            'error': e,
        }), 500

# add loan
@app.route('/createLoan', methods = ['POST'])
def createLoan():
    try:    
        data = request.get_json()
        
        customerID = data.get('customer_id')
        bookID = data.get('book_id')
        loanDate = datetime.strptime(data.get('loan_date'), "%Y-%m-%d %H:%M")
        returnDate = datetime.strptime(data.get('return_date'), "%Y-%m-%d %H:%M")

        loanValidationHelper(customerID, bookID, loanDate, returnDate)

        new_loan = Loan(
            customer_id = customerID,
            book_id = bookID,
            loan_date = loanDate,
            return_date = returnDate
        )

        db.session.add(new_loan)
        db.session.commit()

        return jsonify({
                    'message': 'successful loan addition',
                    'Loan':
                    {
                        'id': new_loan.id,
                        'customer_id':new_loan.customer_id,
                        'book_id':new_loan.book_id,
                        'loan_date':new_loan.loan_date,
                        'return_date':new_loan.return_date,
                    }}), 201
    except Exception as e:
        jsonify({
            'message': 'error',
            'error': e,
        }), 500

#------------------------------------------------
# Show Items list
#------------------------------------------------

# show all books
@app.route('/listBooks', methods=['GET'])
def listBooks():
    try:
        books = Book.query.all()
        booksDictionary = [{
            'id' : book.id,
            'name' : book.name,
            'author' : book.author, 
            'year_published' : book.year_published,
            'type' : book.type,
            'is_available' : book.is_available
        } for book in books]
        return jsonify(booksDictionary), 200
    except Exception as e:
        jsonify({
            'message': 'error',
            'error': e,
        }), 500

# show all customers
@app.route('/listCustomers', methods=['GET'])
def listCustomers():
    try:
        customers = Customer.query.all()
        customersDictionary = [{
            'id': customer.id,
            'name': customer.name,
            'city': customer.city,
            'age': customer.age
        } for customer in customers]
        
        return jsonify(customersDictionary), 200
    
    except Exception as e:
        return jsonify({
            'message': 'error',
            'error': str(e)  # Convert the error to a string
        }), 500

# show all loans
@app.route('/listLoans', methods=['GET'])
def listLoans():
    try:
        loans = Loan.query.all()
        loansDictionary = [{
            'id': loan.id,
            'customer_id':loan.customer_id,
            'book_id':loan.book_id,
            'loan_date':loan.loan_date,
            'return_date':loan.return_date,
        } for loan in loans]
        
        return jsonify(loansDictionary), 200
    
    except Exception as e:
        return jsonify({
            'message': 'error',
            'error': str(e)  # Convert the error to a string
        }), 500

#------------------------------------------------
# Update Item
#------------------------------------------------

# Update a book by ID
@app.route('/updateBook/<int:id>', methods=['PUT'])
def updateBook(id):
    try:
        # Fetch the book by ID
        book = db.session.get(Book, id)
        
        if not book:
            return jsonify({"error": f"Book with ID {id} not found"}), 404

        # Get the JSON data from the request body
        data = request.get_json()

        # Validate and update the 'type' field first
        if 'type' in data:
            try:
                book_type = int(data['type'])  # Convert to int if it's a string
                if book_type not in [1, 2, 3]:  # Validate against your enum values
                    return jsonify({"error": "Invalid type. Must be 1, 2, or 3"}), 400
                book.type = book_type  # Assign the validated type to the book
            except ValueError:
                return jsonify({"error": "Invalid type. Must be an integer (1, 2, or 3)"}), 400

        # Update the other fields if provided
        if 'name' in data:
            book.name = data['name']
        if 'author' in data:
            book.author = data['author']
        if 'year_published' in data:
            book.year_published = data['year_published']
        if 'is_available' in data:
            book.is_available = bool(data['is_available'])

        # Commit the changes to the database
        db.session.commit()

        return jsonify({
            "message": "Book updated successfully",
            "book": {
                'id': book.id,
                'name': book.name,
                'author': book.author,
                'year_published': book.year_published,
                'type': book.type,
                'is_available': book.is_available
            }
        }), 200

    except Exception as e:
        return jsonify({
            "error": "An error occurred while updating the book",
            "details": str(e)
        }), 500

# Update a customer by ID
@app.route('/updateCustomer/<int:id>', methods=['PUT'])
def updateCustomer(id):
    try:
        # Fetch the customer by ID
        customer = db.session.get(Customer, id)
        
        if not customer:
            return jsonify({'users': f"customer with id {id} does not exist"}), 404
        
        data = request.get_json()
        
        # Update the other fields if provided
        if 'name' in data:
            customer.name = data['name']
        if 'city' in data:
            customer.city = data['city']
        if 'age' in data:
            customer.age = data['age']
        
        db.session.commit()
        
        return jsonify({
            "message": "Great Success! customer updated",
            "customer": {
                'id' : customer.id,
                'name' : customer.name,
                'city' : customer.city,
                'age' : customer.age
            }
        }), 200


    except Exception as e:
        return jsonify({
            "error": "An error occurred while updating the book",
            "details": str(e)
        }), 500  

# Update loan dates by ID
@app.route('/updateLoan/<int:id>', methods=['PUT'])
def updateLoan(id):
    try:
        # retrieve record
        loan = db.session.get(Loan, id)

        if not loan:
            return jsonify({"message" : f"no such loan with id {id} exist"}), 404
        
        data = request.get_json()

         # Update loan_date if provided
        if 'loan_date' in data:
            try:
                loan.loan_date = datetime.fromisoformat(data['loan_date'])
            except ValueError:
                return jsonify({"error": "Invalid format for loan_date. Use ISO format (YYYY-MM-DDTHH:MM:SS)"}), 400
            
        if 'return_date' in data:
            try:
                loan.return_date = datetime.fromisoformat(data['return_date'])
            except ValueError:
                return jsonify({"error": "Invalid format for return_date. Use ISO format (YYYY-MM-DDTHH:MM:SS)"}), 400

        db.session.commit()

        # return 'sss'
        return jsonify({
            "message" : "loan updated successfuly",
            "loan":{
                'id':loan.id,
                'customer_id':loan.customer_id,
                'book_id':loan.book_id,
                'loan_date':loan.loan_date,
                'return_date':loan.return_date
            }
        })
    
    except Exception as e:
        pass

#------------------------------------------------
# Delete Item            I did not initialized isActive field, so choosing to implement deletion fully
#------------------------------------------------

@app.route('/deleteBook/<int:book_id>', methods=['DELETE'])
def deleteBook(book_id):
    try:
        # Find the book by ID
        book = Book.query.get(book_id)
        
        if not book:
            return jsonify({"error": "Book not found."}), 404
        
        # Delete all loans associated with the book
        Loan.query.filter_by(book_id=book_id).delete()
        
        # Delete the book
        db.session.delete(book)
        db.session.commit()
        
        return jsonify({"message": f"Book with ID {book_id} and all related loans deleted successfully."}), 200
    
    except Exception as e:
        db.session.rollback()  # Roll back the transaction if an error occurs
        return jsonify({"error": f"An error occurred while deleting the book: {str(e)}"}), 500

@app.route('/deleteCustomer/<int:customer_id>', methods=['DELETE'])
def deleteCustomer(customer_id):
    try:
        # Find the customer by ID
        customer = Customer.query.get(customer_id)
        
        if not customer:
            return jsonify({"error": "Customer not found."}), 404
        
        # Delete all loans associated with the customer
        Loan.query.filter_by(customer_id=customer_id).delete()
        
        # Delete the customer
        db.session.delete(customer)
        db.session.commit()
        
        return jsonify({"message": f"Customer with ID {customer_id} and all related loans deleted successfully."}), 200
    
    except Exception as e:
        db.session.rollback()  # Roll back the transaction if an error occurs
        return jsonify({"error": f"An error occurred while deleting the customer: {str(e)}"}), 500


@app.route('/deleteLoan/<int:loan_id>', methods=['DELETE'])
def deleteLoan(loan_id):
    try:
        # Find the loan by ID
        loan = Loan.query.get(loan_id)
        
        if loan:
            db.session.delete(loan)
            db.session.commit()
            return jsonify({"message": f"Loan with ID {loan_id} deleted successfully."}), 200
        else:
            return jsonify({"error": "Loan not found."}), 404
    
    except Exception as e:
        db.session.rollback()  # Roll back the transaction if an error occurs
        return jsonify({"error": f"An error occurred while deleting the loan: {str(e)}"}), 500

#------------------------------------------------
# Helpers 
#------------------------------------------------

# validates existence of customer & book IDs + loanDate>=returnDate
def loanValidationHelper(customerID, bookID, loanDate, returnDate):
    customer = db.session.get(Customer, customerID)  # Fetch the customer
    if not customer:
        return {"error": f"Customer with ID {customerID} does not exist."}, 400  # Return a 400 Bad Request status

    book = db.session.get(Book, bookID)  # Fetch the customer
    if not book:
        return {"error": f"Book with ID {bookID} does not exist."}, 400  # Return a 400 Bad Request status

    if returnDate and loanDate >= returnDate:
            return {"error": "Loan date must be before the return date."}, 400
#------------------------------------------------
# Rest Api
#------------------------------------------------
if __name__ == '__main__':
    app.run(debug=True)
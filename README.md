# Library Management

A library project which includes Books, Customer and Loans models.
The project is a python projects. First segment of functions is responsible of defining the models.
Then, another segment which is responsible of initiating the DB with data from the json files, that can be found in "mockup" dir.

## Table of Contents

- [Installation](#installation)
- [Usage](#usage)
- [Contributing](#contributing)
- [License](#license)
- [Contact](#contact)

## Installation

Instructions on how to install and set up the project.

```bash
git clone https://github.com/jbgaljb/libraryBackend_flask.git

cd libraryBackend_flask

py -m env venv   # initiating virtual env

pip install requirements.txt
```

## Usage

```bash
py app.py
```

### Routes of Rest api:

/initModels : methods = ['GET']

/createBook : methods = ['POST']

/createCustomer : methods = ['POST']

/createLoan : methods = ['POST']

/listBooks : methods=['GET']

/listCustomers : methods=['GET']

/listLoans : methods=['GET']

/updateBook/<int:id> : methods=['PUT']

/updateCustomer/<int:id> : methods=['PUT']

/updateLoan/<int:id> : methods=['PUT']

/deleteBook/<int:book_id> : methods=['DELETE']

/deleteCustomer/<int:customer_id> : methods=['DELETE']

/deleteLoan/<int:loan_id> : methods=['DELETE']

## Contact

don't contact
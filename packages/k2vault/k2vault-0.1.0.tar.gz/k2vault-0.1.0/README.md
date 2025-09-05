# k2Vault
From here we create the k2Vault Package for our Python code

# Instructions on How-To-Use

The Developer should send the name of their secret as a Parameter to the Library as follows:

    k2vault('[name of the secret]')

and then the return Value from the library is a string so:

    Encrypted_secret = k2vault('[name of the secret]')

mylib/
├── mylib/
│   └── __init__.py
├── setup.py
├── README.md
└── .github/
    └── workflows/
        └── publish.yml

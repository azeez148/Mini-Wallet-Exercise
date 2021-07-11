# Mini-Wallet-Exercise
Mini Wallet Exercise

To run/test the api, follow the below instructions step by step to install this project.
```
git clone --single-branch --branch dev git@github.com:azeez148/Mini-Wallet-Exercise.git 
python3 -m venv env
source env/bin/activate
pip install -r requirements.txt
cd miniwallet
python manage.py makemigrations walletapp 
python manage.py makemigrations
python manage.py migrate walletapp
python manage.py migrate
python manage.py runserver
```

import random
from app import app, db, NameSuggestion  # make sure to replace `your_flask_app_file` with the name of your Flask app file

kinyarwanda_names = ['Uwimana', 'Iradukunda', 'Amizero', 'Kwizera', 'Niyibizi', 'Uwimana', 'Tuyishime', 'Nsabimana', 'Kamanzi', 'Iyamuremye', 'Rukundo', 'Manzi', 'Umuhire', 'Cyusa']
general_names = ['Liam', 'Noah', 'Ethan', 'Mason', 'Lucas', 'Oliver', 'Aiden', 'Logan', 'James', 'Alexander', 'Elijah', 'Benjamin', 'Sebastian', 'Jackson', 'Matthew']

def insert_names(names, category):
    with app.app_context():  # This line is crucial for working within the application context
        for name in names:
            upvotes = random.randint(0, 100)
            new_name_suggestion = NameSuggestion(category=category, name_suggestion=name, your_name="Anonymous", upvotes=upvotes)
            db.session.add(new_name_suggestion)
        db.session.commit()

insert_names(kinyarwanda_names, 'kinyarwanda')
insert_names(general_names, 'general')

print("Names have been inserted into the database with random upvotes.")

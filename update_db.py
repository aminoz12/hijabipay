from app import app, db
import os

# Remove the existing database file
db_file = 'instance/payments.db'
if os.path.exists(db_file):
    os.remove(db_file)

# Create all database tables
with app.app_context():
    db.create_all()

print("Database has been recreated with the latest schema.")
print("You can now restart the Flask application.")

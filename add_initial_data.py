from app import app, db, Manager, Gate

# Create the database tables and add initial data
with app.app_context():
    db.create_all()

    # Add initial managers
    managers = [
        Manager(name='Ibrahim Al-Hamed', email='ihemaa.4@gmail.com', password='A123+123*/'),
        Manager(name='Mashel Al-Hamed', email='s2212001102@uhb.edu.sa', password='password123')
    ]

    # Add initial gates
    gates = [
        Gate(gate_number='1', location='Main Entrance'),
        Gate(gate_number='2', location='Back Entrance')
    ]

    # Add the managers and gates to the session and commit
    db.session.bulk_save_objects(managers)
    db.session.bulk_save_objects(gates)
    db.session.commit()

    print("Initial data added.")

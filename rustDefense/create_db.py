from server import db, Phone, app

with app.app_context():
    db.create_all()
    db.session.commit()

from server import db, Phone
import sys

db.session.add(Phone(sys.argv[0], sys.argv[1]))

db.session.commit()

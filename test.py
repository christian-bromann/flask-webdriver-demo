import os
import nose

parentdir = os.path.dirname(os.path.abspath(__file__))
os.sys.path.insert(0, parentdir)

import flaskr

with flaskr.app.app_context():
            flaskr.init_db()

nose.run()

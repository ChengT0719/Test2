from app import create_app, db
from flask_migrate import Migrate
import os
from app.models import User, Scenic, Collect, Area, Travels, Admin


config = os.getenv("FLASK_CONFIG") or "default"
app = create_app(config)
migrate = Migrate(app, db)


# @app.shell_context_processor
# def make_shell_context():
#     from app.models import User
#     return dict(db=db, User=User)


@app.cli.command()
def test():
    import unittest
    tests = unittest.TestLoader().discover("test2")
    unittest.TextTestRunner(verbosity=2).run(tests)


if __name__ == "__main__":
    app.run(debug=True, port=app.config["SERVER_PORT"])

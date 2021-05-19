from app import create_app, db
from app.main.models.point import Point
from app.main.models.incident import Incident

app = create_app()

@app.shell_context_processor
def make_shell_context():
    return {'db': db, 'Point': Point, 'Incident': Incident }
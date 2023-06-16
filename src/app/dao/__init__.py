from src.app.models import Base, engine
from src.app.models.user import User

Base.metadata.create_all(engine)

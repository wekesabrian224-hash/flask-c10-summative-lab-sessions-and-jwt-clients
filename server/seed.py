from faker import Faker

from config import app, db
from models import User, Note

fake = Faker()

USERS = ["lucky", "sam", "amina"]
NOTES_PER_USER = 8

with app.app_context():
    print("Clearing old data...")
    Note.query.delete()
    User.query.delete()

    print("Seeding users and notes...")
    for username in USERS:
        user = User(username=username)
        user.password = "password123"
        db.session.add(user)
        db.session.flush()  # assigns user.id so the notes can point to it

        for _ in range(NOTES_PER_USER):
            db.session.add(
                Note(
                    title=fake.sentence(nb_words=4),
                    content=fake.paragraph(nb_sentences=3),
                    user_id=user.id,
                )
            )

    db.session.commit()
    print(f"Done: {len(USERS)} users, {len(USERS) * NOTES_PER_USER} notes.")
from sqlalchemy import (
    create_engine,
    Column,
    Integer,
    String,
    Float,
    ForeignKey,
    Table,
    Text,
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
import json
from sqlalchemy.ext.declarative import DeclarativeMeta

Base = declarative_base()

# Association table for the many-to-many relationship
related_lexeme_association = Table(
    "related_lexeme_association",
    Base.metadata,
    Column("word_id", String, ForeignKey("words.id")),
    Column("related_lexeme_id", String, ForeignKey("words.id")),
)


class AlchemyEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj.__class__, DeclarativeMeta):
            # An SQLAlchemy class
            fields = {}
            for field in [
                x for x in dir(obj) if not x.startswith("_") and x != "metadata"
            ]:
                data = obj.__getattribute__(field)
                try:
                    json.dumps(
                        data
                    )  # this will fail on non-encodable values, like other classes
                    fields[field] = data
                except TypeError:
                    fields[field] = None
            # a json-encodable dict
            return fields

        return json.JSONEncoder.default(self, obj)


class Word(Base):
    __tablename__ = "words"
    id = Column(String, primary_key=True)
    strength_bars = Column(Integer)
    infinitive = Column(Text)
    normalized_string = Column(Text)
    pos = Column(Text)
    last_practiced_ms = Column(Integer)
    skill = Column(Text)
    last_practiced = Column(Text)
    strength = Column(Float)
    skill_url_title = Column(Text)
    gender = Column(Text)
    lexeme_id = Column(String)
    word_string = Column(Text)
    # Establish a many-to-many relationship with itself
    related_lexemes = relationship(
        "Word",
        secondary=related_lexeme_association,
        primaryjoin=(related_lexeme_association.c.word_id == id),
        secondaryjoin=(related_lexeme_association.c.related_lexeme_id == id),
        backref="related_by",
    )


# engine = create_engine("sqlite:///data.db")
# Base.metadata.create_all(engine)
# Session = sessionmaker(bind=engine)
# session = Session()
session = None


def insert_word_with_related_lexemes(word_data):
    # Extract related_lexemes from the data and remove the key
    related_lexeme_ids = word_data.pop("related_lexemes", [])
    related_lexemes = []

    # Check if each related lexeme already exists, if not, create a new one
    for lexeme_id in related_lexeme_ids:
        lexeme = session.query(Word).get(lexeme_id)
        if lexeme is None:
            lexeme = Word(id=lexeme_id)
            session.add(lexeme)
        related_lexemes.append(lexeme)

    # Now insert the new word with its related lexemes
    word = session.query(Word).get(word_data["id"])
    if word is None:
        word = Word(**word_data)
        session.add(word)
    else:
        # If the word already exists, update its attributes
        for key, value in word_data.items():
            setattr(word, key, value)

    # Update related lexemes
    word.related_lexemes = related_lexemes
    session.commit()


# def upsert_word(word_data):
#     word = session.query(Word).get(word_data['id'])
#     if word:
#         for key, value in word_data.items():
#             if key == 'related_lexemes':
#                 # Clear existing related lexemes and add the new ones
#                 word.related_lexemes[:] = [RelatedLexeme(id=lexeme_id) for lexeme_id in value]
#             else:
#                 setattr(word, key, value)
#     else:
#         insert_word_with_related_lexemes(word_data)
#     session.commit()


def get_word(word_id, db_file: str = "data.db"):
    init_db_session(db_file)
    return session.query(Word).get(word_id)


def delete_word(word_id):
    word = get_word(word_id)
    if word:
        session.delete(word)
        session.commit()


def read_data(voc_file: str = "voc.json"):
    import json

    # Load the JSON data from file
    with open(voc_file, "r") as file:
        data = json.load(file)
    return data


def dump_to_db(voc_file, db_file):
    init_db_session(db_file)
    data = read_data(voc_file)
    for item in data:
        insert_word_with_related_lexemes(item)


def init_db_session(db_file: str = "data.db"):
    global session
    if not session:
        engine = create_engine(f"sqlite:///{db_file}")
        Base.metadata.create_all(engine)
        Session = sessionmaker(bind=engine)
        session = Session()


if __name__ == "__main__":
    data = read_data()
    for item in data:
        insert_word_with_related_lexemes(item)
    import json

    word = get_word("6b3f32e7cfb1c0eac18d6038e097ceb1")
    print(json.dumps(word.related_lexemes, cls=AlchemyEncoder, indent=4))
    session.close()
    # # Read
    # print(word.word_string)

    # # Update
    # word_data['strength_bars'] = 5
    # upsert_word(word_data)

    # # Delete
    # delete_word("ef7dbc34c11dad1f9b1e85da664211cd")

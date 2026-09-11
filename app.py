from flask import Flask, request, jsonify, render_template
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///readquotely.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

quote_tags = db.Table('quote_tags',
    db.Column('quote_id', db.Integer, db.ForeignKey('quotes.id'), primary_key=True),
    db.Column('tag_id', db.Integer, db.ForeignKey('tags.id'), primary_key=True)
)

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    books = db.relationship('Book', backref='owner', lazy=True, cascade="all, delete-orphan")
    quotes = db.relationship('Quote', backref='author', lazy=True, cascade="all, delete-orphan")

class Book(db.Model):
    __tablename__ = 'books'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    title = db.Column(db.String(150), nullable=False)
    author = db.Column(db.String(100), nullable=False)
    genre = db.Column(db.String(50))
    total_pages = db.Column(db.Integer)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    quotes = db.relationship('Quote', backref='book', lazy=True, cascade="all, delete-orphan")

class Quote(db.Model):
    __tablename__ = 'quotes'
    id = db.Column(db.Integer, primary_key=True)
    book_id = db.Column(db.Integer, db.ForeignKey('books.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    quote_text = db.Column(db.Text, nullable=False)
    page_number = db.Column(db.Integer)
    personal_note = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    tags = db.relationship('Tag', secondary=quote_tags, lazy='subquery',
        backref=db.backref('quotes', lazy=True))

class Tag(db.Model):
    __tablename__ = 'tags'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(30), unique=True, nullable=False)


#1 
@app.route('/', methods=['GET'])
def home():
    return render_template('index.html')
#2
@app.route('/api/users', methods=['POST'])
def create_user():
    data = request.get_json()
    
    yeni_kullanici = User(
        username=data['username'],
        email=data['email'],
        password_hash=data['password'] 
    )
    
    db.session.add(yeni_kullanici)
    db.session.commit() 
    
    return jsonify({"mesaj": "Kullanici basariyla olusturuldu!"}), 201

# 3
@app.route('/api/users', methods=['GET'])
def get_users():
    users = User.query.all()
    result = [{"id": u.id, "username": u.username, "email": u.email} for u in users]
    return jsonify(result), 200

# 4
@app.route('/api/books', methods=['POST'])
def create_book():
    data = request.get_json()
    
    yeni_kitap = Book(
        user_id=data['user_id'], # Kitabı kimin eklediğini bağlıyoruz (Bizim ID'miz 1)
        title=data['title'],
        author=data['author'],
        genre=data.get('genre', ''), # Zorunlu değilse boş kalabilir
        total_pages=data.get('total_pages', 0)
    )
    
    db.session.add(yeni_kitap)
    db.session.commit()
    
    return jsonify({"mesaj": "Kitap basariyla eklendi!"}), 201

# 5
@app.route('/api/quotes', methods=['POST'])
def create_quote():
    data = request.get_json()
    
    yeni_alinti = Quote(
        book_id=data['book_id'], 
        user_id=data['user_id'], 
        quote_text=data['quote_text'],
        page_number=data.get('page_number', 0),
        personal_note=data.get('personal_note', '')
    )
    
    db.session.add(yeni_alinti)
    db.session.commit()
    
    return jsonify({"mesaj": "Alinti basariyla eklendi!"}), 201
#6 
@app.route('/api/books', methods=['GET'])
def get_all_books():
    books = Book.query.all() 
    result = []
    
    for book in books:
        book_data = {
            "id": book.id,
            "title": book.title,
            "author": book.author,
            "genre": book.genre,
            "total_pages": book.total_pages,
            "quotes": [
                {
                    "id": quote.id, 
                    "text": quote.quote_text, 
                    "page": quote.page_number,
                    "note": quote.personal_note
                } for quote in book.quotes
            ]
        }
        result.append(book_data)
        
    return jsonify(result), 200
if __name__ == '__main__':
    app.run(debug=True)
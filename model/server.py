from flask import Flask, request, jsonify
from flask_cors import CORS
import findMusic  # this imports findSongs from findMusic.py

app = Flask(__name__)
CORS(app)  # Enables frontend requests from a different origin

@app.route('/recommend', methods=['POST'])
def recommend_songs():
    data = request.get_json()
    book_title = data.get('bookTitle')
    book_author = data.get('bookAuthor')

    if not book_title or not book_author:
        return jsonify({'error': 'Missing book title or author'}), 400

    try:
        songs = findMusic.findSongs(book_title, book_author)  # This returns a list of dicts

        if not songs:
            return jsonify({'error': 'No matching songs found'}), 404

        return jsonify({'songs': songs}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)

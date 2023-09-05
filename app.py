from flask import Flask, request, jsonify
import requests
from datetime import datetime

app = Flask(__name__)

# Define the base URL of the YouTube comment API
BASE_URL = "https://app.ylytic.com/ylytic/test"

@app.route('/search', methods=['GET'])
def search_comments():
    # Parse query parameters from the request URL
    search_author = request.args.get('search_author')
    at_from = request.args.get('at_from')
    at_to = request.args.get('at_to')
    like_from = int(request.args.get('like_from', 0))
    like_to_str = request.args.get('like_to', '1000000')  # Use a suitable upper bound value
    reply_from = int(request.args.get('reply_from', 0))
    reply_to_str = request.args.get('reply_to', '1000000')  # Use a suitable upper bound value
    search_text = request.args.get('search_text')

    # Replace 'inf' with the upper bound value
    like_to = int(like_to_str) if like_to_str != 'inf' else 1000000
    reply_to = int(reply_to_str) if reply_to_str != 'inf' else 1000000

    # Construct parameters for the existing YouTube comment API
    params = {}

    if search_author:
        params['search_author'] = search_author

    if at_from and at_to:
        params['at_from'] = datetime.strptime(at_from, "%d-%m-%Y").strftime("%Y-%m-%d")
        params['at_to'] = datetime.strptime(at_to, "%d-%m-%Y").strftime("%Y-%m-%d")

    # Make a request to the existing YouTube comment API
    response = requests.get(BASE_URL, params=params)

    if response.status_code == 200:
        comments_data = response.json()  # Parse the JSON response
        comments = comments_data.get('comments', [])  # Get the list of comments

        filtered_comments = []

        # Filter comments based on search criteria
        for comment in comments:
            if (like_from <= comment['like'] <= like_to) \
                    and (reply_from <= comment['reply'] <= reply_to) \
                    and (not search_text or search_text in comment['text']):
                filtered_comments.append(comment)

        return jsonify(filtered_comments)
    else:
        return jsonify({"error": "Failed to fetch comments from the YouTube API"}), 500

@app.route('/')
def home():
    return "Welcome to the YouTube Comment Search API"

if __name__ == '__main__':
    app.run(debug=True)

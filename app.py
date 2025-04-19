from flask import Flask, render_template, request, jsonify, redirect
import requests

app = Flask(__name__)

@app.route('/')
def index():
    return redirect("https://github.com/0xh7ml", code=302)

@app.route('/api', methods=['GET'])
def show_card():
    # Get the username from the query string
    username = request.args.get('username')
    if not username:
        return jsonify({'error': 'Missing username parameter'}), 400

    # Yogosha API call
    url = f'https://api.yogosha.com/api/researchers/{username}'
    headers = {
        'Content-Type': 'application/json',
    }
    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        res = response.json()
        data = {
            "totalReports": res["totalReports"],
            "username": res["username"],
            "averageReportsQuality": res["averageReportsQuality"],
            "allTime": {
                "kudos": res["allTime"]["kudos"],
                "rank": res["allTime"]["rank"]
            },
            "last30DaysRank": res["last30Days"]["rank"],
            "acceptanceRate": res["acceptanceRate"],
            "image": res["avatar"]["filename"],
        }

        # Render the HTML content with the data
        response_headers = {
            'Content-Type': 'text/html',
            'Cache-Control': 's-maxage=3600, stale-while-revalidate=86400',
        }
        rendered_html = render_template('index.html', data=data, headers=response_headers)
        return rendered_html
    else:
        return jsonify({'error': 'User not found'}), 404


if __name__ == '__main__':
    app.run(
        debug=False,
        host='0.0.0.0',
        port=5000
    )
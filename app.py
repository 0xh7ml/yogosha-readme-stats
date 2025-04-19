from flask import Flask, request, jsonify, redirect, Response
import requests
import re

app = Flask(__name__)

def sanitize_username(username):
    """Sanitize username input."""
    if not username or not isinstance(username, str):
        return None
    return re.sub(r'[^a-zA-Z0-9_-]', '', username.strip())

@app.route('/')
def index():
    return redirect("https://github.com/0xh7ml", code=302)

@app.route('/api', methods=['GET'])
def show_card():
    # Get and sanitize username
    username = sanitize_username(request.args.get('username'))
    if not username:
        return jsonify({'error': 'Invalid or missing username parameter'}), 400

    # Yogosha API call
    url = f'https://api.yogosha.com/api/researchers/{username}'
    headers = {'Content-Type': 'application/json'}
    
    try:
        response = requests.get(url, headers=headers, timeout=5)
        response.raise_for_status()
    except requests.RequestException as e:
        return jsonify({'error': 'Failed to fetch data from Yogosha API'}), 503

    if response.status_code == 200:
        try:
            res = response.json()
            data = {
                "totalReports": res.get("totalReports", 0),
                "username": res.get("username", "Unknown"),
                "averageReportsQuality": res.get("averageReportsQuality", 0),
                "allTime": {
                    "kudos": res.get("allTime", {}).get("kudos", 0),
                    "rank": res.get("allTime", {}).get("rank", "N/A")
                },
                "last30DaysRank": res.get("last30Days", {}).get("rank", "N/A"),
                "acceptanceRate": res.get("acceptanceRate", 0),
            }
        except (KeyError, TypeError, ValueError):
            return jsonify({'error': 'Invalid response from Yogosha API'}), 500

        # Response headers
        response_headers = {
            'Cache-Control': 'no-cache, no-store, must-revalidate',
            'Content-Type': 'image/svg+xml',
        }

        # SVG template with Yogosha logo and no circle
        svg_template = f'''
        <svg width="600" height="220" viewBox="0 0 600 220" xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink">
            <style>
                text {{ font-family: 'Verdana', 'Arial', sans-serif; }}
                .title {{ font-weight: bold; font-size: 20px; }}
                .label {{ font-size: 14px; fill: #9ca3af; }}
                .value {{ font-size: 16px; font-weight: 500; }}
            </style>
            
            <!-- Background -->
            <rect x="0" y="0" width="600" height="220" rx="12" fill="#121212"/>

            <!-- Yogosha Logo -->
            <image x="480" y="60" width="100" height="100" preserveAspectRatio="xMidYMid meet"
                   xlink:href="https://yogosha.com/_content/yogosha-strike-force_hollow-2.svg"/>

            <!-- Username -->
            <text x="20" y="40" fill="#ffffff" class="title">{data['username']}'s Yogosha Stats</text>

            <!-- Stats Grid -->
            <g transform="translate(20, 70)">
                <!-- Row 1 -->
                <text x="0" y="0" fill="#eab308" class="label">🏅 Kudos</text>
                <text x="120" y="0" fill="#ffffff" class="value">{data['allTime']['kudos']}</text>
                
                <text x="220" y="0" fill="#22c55e" class="label">🎯 Acceptance</text>
                <text x="340" y="0" fill="#ffffff" class="value">{data['acceptanceRate']}%</text>

                <!-- Row 2 -->
                <text x="0" y="30" fill="#3b82f6" class="label">📄 Reports</text>
                <text x="120" y="30" fill="#ffffff" class="value">{data['totalReports']}</text>
                
                <text x="220" y="30" fill="#a855f7" class="label">✅ Avg Quality</text>
                <text x="340" y="30" fill="#ffffff" class="value">{data['averageReportsQuality']}/5</text>
            </g>

            <!-- Ranking Section -->
            <rect x="20" y="140" width="440" height="60" rx="6" fill="#1a1a1a"/>
            <text x="32" y="175" class="label">🏆 All Time Rank</text>
            <text x="160" y="175" fill="#ffffff" class="value">#{data['allTime']['rank']}</text>
            <text x="260" y="175" class="label">🕒 Last 30 Days</text>
            <text x="380" y="175" fill="#ffffff" class="value">#{data['last30DaysRank']}</text>
        </svg>
        '''

        return Response(svg_template, mimetype='image/svg+xml', headers=response_headers)
    
    return jsonify({'error': 'User not found'}), 404

if __name__ == '__main__':
    app.run(
        debug=False,
        host='0.0.0.0',
        port=5000
    )
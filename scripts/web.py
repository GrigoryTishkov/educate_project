#!/usr/bin/env python3
# GET /top возвращает JSON или HTML таблицу (по ?format=json)

import os
from datetime import datetime
from flask import Flask, request, jsonify, render_template_string
from sqlalchemy import create_engine, select
from sqlalchemy.exc import SQLAlchemyError
from models import top_users_by_posts  # импортируем таблицу из models.py

app = Flask(__name__)

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/postgres")
engine = create_engine(DATABASE_URL, pool_pre_ping=True)

HTML_TEMPLATE = """
<!doctype html>
<html>
<head>
  <meta charset="utf-8">
  <title>Top users by posts</title>
  <style>
    body { font-family: Arial, Helvetica, sans-serif; padding: 24px; }
    table { border-collapse: collapse; width: 480px; }
    th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }
    th { background: #f4f4f4; }
    caption { font-size: 1.2em; margin-bottom: 8px; }
  </style>
</head>
<body>
  <h2>Top users by posts</h2>
  <p>As of: {{ now }}</p>
  {% if rows %}
    <table>
      <thead><tr><th>user_id</th><th>posts_cnt</th><th>calculated_at</th></tr></thead>
      <tbody>
      {% for r in rows %}
        <tr>
          <td>{{ r.user_id }}</td>
          <td>{{ r.posts_cnt }}</td>
          <td>{{ r.calculated_at }}</td>
        </tr>
      {% endfor %}
      </tbody>
    </table>
  {% else %}
    <p>Нет данных в top_users_by_posts.</p>
  {% endif %}
</body>
</html>
"""

@app.route("/top", methods=["GET"])
def top():
    fmt = request.args.get("format", "").lower()
    try:
        with engine.connect() as conn:
            stmt = select(
                top_users_by_posts.c.user_id,
                top_users_by_posts.c.posts_cnt,
                top_users_by_posts.c.calculated_at
            ).order_by(top_users_by_posts.c.posts_cnt.desc())
            res = conn.execute(stmt).mappings().all()
    except SQLAlchemyError as e:
        return ("DB error: " + str(e)), 500

    # convert rows to simple dicts
    rows = [
        {"user_id": r["user_id"], "posts_cnt": r["posts_cnt"], "calculated_at": r["calculated_at"].isoformat() if r["calculated_at"] else None}
        for r in res
    ]

    if fmt == "json" or request.headers.get("Accept", "").lower().startswith("application/json"):
        return jsonify({"rows": rows, "fetched_at": datetime.utcnow().isoformat()})

    return render_template_string(HTML_TEMPLATE, rows=res, now=datetime.utcnow().isoformat())

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("WEB_PORT", 8080)))

#!/usr/bin/env python
"""
Demo script to generate recommendation report for presentation.
Usage: python demo_report.py
"""

import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'recommender_service.settings')
os.environ.setdefault('DATABASE_URL', 'sqlite:///db.sqlite3')
django.setup()

from datetime import datetime
from app.models import UserInteraction, BookSimilarity
from app.recommender import recommender_engine

def generate_html_report():
    """Generate HTML report for demonstration."""

    # Gather data
    total_interactions = UserInteraction.objects.count()
    total_similarities = BookSimilarity.objects.count()

    interaction_stats = {
        'view': UserInteraction.objects.filter(interaction_type='view').count(),
        'cart': UserInteraction.objects.filter(interaction_type='cart').count(),
        'purchase': UserInteraction.objects.filter(interaction_type='purchase').count(),
        'rate': UserInteraction.objects.filter(interaction_type='rate').count(),
    }

    # Get recommendations
    popular = recommender_engine.get_popular_books(limit=10)
    trending = recommender_engine.get_trending_books(limit=10)

    # Get sample user for personalized recommendations
    sample_user = UserInteraction.objects.values('customer_id').first()
    user_id = sample_user['customer_id'] if sample_user else 1

    user_history = list(UserInteraction.objects.filter(
        customer_id=user_id
    ).values('book_id', 'interaction_type')[:10])

    personalized = recommender_engine.get_personalized_recommendations(user_id, limit=10)

    # Get sample book for similar books
    sample_book = UserInteraction.objects.filter(
        interaction_type='purchase'
    ).values('book_id').first()
    book_id = sample_book['book_id'] if sample_book else 1
    similar = recommender_engine.get_similar_books(book_id, limit=10)

    # Top similarities
    top_similarities = list(BookSimilarity.objects.order_by('-score')[:20].values(
        'book_id', 'similar_book_id', 'score'
    ))

    html = f"""<!DOCTYPE html>
<html lang="vi">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Book Recommender System - Demo Report</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }}
        .container {{ max-width: 1200px; margin: 0 auto; }}
        h1 {{
            text-align: center;
            color: white;
            margin-bottom: 30px;
            font-size: 2.5em;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
        }}
        .card {{
            background: white;
            border-radius: 15px;
            padding: 25px;
            margin-bottom: 20px;
            box-shadow: 0 10px 40px rgba(0,0,0,0.2);
        }}
        .card h2 {{
            color: #667eea;
            margin-bottom: 20px;
            padding-bottom: 10px;
            border-bottom: 3px solid #667eea;
        }}
        .stats-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
        }}
        .stat-box {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 20px;
            border-radius: 10px;
            text-align: center;
        }}
        .stat-box .number {{ font-size: 2.5em; font-weight: bold; }}
        .stat-box .label {{ font-size: 0.9em; opacity: 0.9; }}
        table {{
            width: 100%;
            border-collapse: collapse;
            margin-top: 15px;
        }}
        th, td {{
            padding: 12px 15px;
            text-align: left;
            border-bottom: 1px solid #eee;
        }}
        th {{
            background: #f8f9fa;
            font-weight: 600;
            color: #333;
        }}
        tr:hover {{ background: #f8f9fa; }}
        .score {{
            display: inline-block;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 4px 12px;
            border-radius: 20px;
            font-size: 0.85em;
        }}
        .reason {{
            display: inline-block;
            background: #e8f5e9;
            color: #2e7d32;
            padding: 4px 10px;
            border-radius: 5px;
            font-size: 0.8em;
        }}
        .interaction-type {{
            display: inline-block;
            padding: 3px 10px;
            border-radius: 5px;
            font-size: 0.8em;
            font-weight: 500;
        }}
        .type-view {{ background: #e3f2fd; color: #1565c0; }}
        .type-cart {{ background: #fff3e0; color: #ef6c00; }}
        .type-purchase {{ background: #e8f5e9; color: #2e7d32; }}
        .type-rate {{ background: #fce4ec; color: #c2185b; }}
        .architecture {{
            background: #f5f5f5;
            padding: 20px;
            border-radius: 10px;
            font-family: monospace;
            font-size: 0.9em;
            overflow-x: auto;
        }}
        .footer {{
            text-align: center;
            color: white;
            margin-top: 30px;
            opacity: 0.8;
        }}
        .two-col {{ display: grid; grid-template-columns: 1fr 1fr; gap: 20px; }}
        @media (max-width: 768px) {{
            .two-col {{ grid-template-columns: 1fr; }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>Book Recommender System</h1>

        <!-- Overview Stats -->
        <div class="card">
            <h2>Overview Statistics</h2>
            <div class="stats-grid">
                <div class="stat-box">
                    <div class="number">{total_interactions:,}</div>
                    <div class="label">Total Interactions</div>
                </div>
                <div class="stat-box">
                    <div class="number">{total_similarities:,}</div>
                    <div class="label">Book Similarities</div>
                </div>
                <div class="stat-box">
                    <div class="number">{interaction_stats['view']:,}</div>
                    <div class="label">Views</div>
                </div>
                <div class="stat-box">
                    <div class="number">{interaction_stats['cart']:,}</div>
                    <div class="label">Add to Cart</div>
                </div>
                <div class="stat-box">
                    <div class="number">{interaction_stats['purchase']:,}</div>
                    <div class="label">Purchases</div>
                </div>
                <div class="stat-box">
                    <div class="number">{interaction_stats['rate']:,}</div>
                    <div class="label">Ratings</div>
                </div>
            </div>
        </div>

        <!-- System Architecture -->
        <div class="card">
            <h2>System Architecture</h2>
            <div class="architecture">
<pre>
┌─────────────────────────────────────────────────────────────────────────┐
│                        RECOMMENDER SYSTEM                                │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│   ┌──────────────┐    ┌──────────────┐    ┌──────────────┐             │
│   │ order-service│    │ cart-service │    │comment-rate- │             │
│   │              │    │              │    │   service    │             │
│   │  (purchase)  │    │   (cart)     │    │   (rate)     │             │
│   └──────┬───────┘    └──────┬───────┘    └──────┬───────┘             │
│          │                   │                   │                      │
│          └───────────────────┼───────────────────┘                      │
│                              ▼                                          │
│                   ┌─────────────────────┐                               │
│                   │  UserInteraction DB │                               │
│                   │  (view/cart/        │                               │
│                   │   purchase/rate)    │                               │
│                   └──────────┬──────────┘                               │
│                              │                                          │
│          ┌───────────────────┼───────────────────┐                      │
│          ▼                   ▼                   ▼                      │
│   ┌──────────────┐    ┌──────────────┐    ┌──────────────┐             │
│   │ Collaborative│    │Content-Based │    │  Popularity  │             │
│   │  Filtering   │    │  Filtering   │    │    Based     │             │
│   │  (Jaccard)   │    │(category/    │    │  (trending)  │             │
│   │              │    │  author)     │    │              │             │
│   └──────┬───────┘    └──────┬───────┘    └──────┬───────┘             │
│          │                   │                   │                      │
│          └───────────────────┼───────────────────┘                      │
│                              ▼                                          │
│                   ┌─────────────────────┐                               │
│                   │   HYBRID ENGINE     │                               │
│                   │  (combine + rank)   │                               │
│                   └──────────┬──────────┘                               │
│                              │                                          │
│          ┌───────────────────┼───────────────────┐                      │
│          ▼                   ▼                   ▼                      │
│   ┌──────────────┐    ┌──────────────┐    ┌──────────────┐             │
│   │Similar Books │    │ Personalized │    │Popular/      │             │
│   │   API        │    │Recommendations│   │Trending API  │             │
│   └──────────────┘    └──────────────┘    └──────────────┘             │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
</pre>
            </div>
        </div>

        <!-- Popular & Trending -->
        <div class="two-col">
            <div class="card">
                <h2>Popular Books (30 days)</h2>
                <table>
                    <thead>
                        <tr><th>#</th><th>Book ID</th><th>Score</th></tr>
                    </thead>
                    <tbody>
                        {"".join(f'<tr><td>{i+1}</td><td>Book {r["book_id"]}</td><td><span class="score">{r["score"]:.2f}</span></td></tr>' for i, r in enumerate(popular))}
                    </tbody>
                </table>
            </div>
            <div class="card">
                <h2>Trending Books (7 days)</h2>
                <table>
                    <thead>
                        <tr><th>#</th><th>Book ID</th><th>Score</th></tr>
                    </thead>
                    <tbody>
                        {"".join(f'<tr><td>{i+1}</td><td>Book {r["book_id"]}</td><td><span class="score">{r["score"]:.2f}</span></td></tr>' for i, r in enumerate(trending))}
                    </tbody>
                </table>
            </div>
        </div>

        <!-- Similar Books -->
        <div class="card">
            <h2>Similar Books (Collaborative Filtering)</h2>
            <p style="margin-bottom: 15px; color: #666;">
                Books similar to <strong>Book #{book_id}</strong> based on co-purchase patterns:
            </p>
            <table>
                <thead>
                    <tr><th>#</th><th>Similar Book</th><th>Similarity Score</th><th>Method</th></tr>
                </thead>
                <tbody>
                    {"".join(f'<tr><td>{i+1}</td><td>Book {r["book_id"]}</td><td><span class="score">{r["score"]:.4f}</span></td><td><span class="reason">{r["reason"]}</span></td></tr>' for i, r in enumerate(similar))}
                </tbody>
            </table>
        </div>

        <!-- Personalized Recommendations -->
        <div class="card">
            <h2>Personalized Recommendations</h2>
            <p style="margin-bottom: 15px; color: #666;">
                Recommendations for <strong>User #{user_id}</strong>
            </p>

            <h3 style="margin: 20px 0 10px 0; color: #333;">User's Interaction History:</h3>
            <table>
                <thead>
                    <tr><th>Book ID</th><th>Interaction Type</th></tr>
                </thead>
                <tbody>
                    {"".join(f'<tr><td>Book {h["book_id"]}</td><td><span class="interaction-type type-{h["interaction_type"]}">{h["interaction_type"]}</span></td></tr>' for h in user_history)}
                </tbody>
            </table>

            <h3 style="margin: 20px 0 10px 0; color: #333;">Recommended Books:</h3>
            <table>
                <thead>
                    <tr><th>#</th><th>Book ID</th><th>Score</th><th>Reason</th></tr>
                </thead>
                <tbody>
                    {"".join(f'<tr><td>{i+1}</td><td>Book {r["book_id"]}</td><td><span class="score">{r["score"]:.4f}</span></td><td><span class="reason">{r["reason"]}</span></td></tr>' for i, r in enumerate(personalized))}
                </tbody>
            </table>
        </div>

        <!-- Top Similarities -->
        <div class="card">
            <h2>Book Similarity Matrix (Top 20)</h2>
            <p style="margin-bottom: 15px; color: #666;">
                Precomputed similarities using Jaccard coefficient on user co-interactions
            </p>
            <table>
                <thead>
                    <tr><th>Book A</th><th>Book B</th><th>Jaccard Score</th></tr>
                </thead>
                <tbody>
                    {"".join(f'<tr><td>Book {s["book_id"]}</td><td>Book {s["similar_book_id"]}</td><td><span class="score">{s["score"]:.4f}</span></td></tr>' for s in top_similarities)}
                </tbody>
            </table>
        </div>

        <!-- Algorithm Explanation -->
        <div class="card">
            <h2>Algorithm Explanation</h2>
            <div style="line-height: 1.8;">
                <h3 style="color: #667eea; margin: 15px 0 10px 0;">1. Collaborative Filtering (Jaccard Similarity)</h3>
                <p>Tính similarity giữa 2 books dựa trên users đã tương tác với cả 2:</p>
                <div style="background: #f5f5f5; padding: 15px; border-radius: 8px; margin: 10px 0; font-family: monospace;">
                    Jaccard(Book_A, Book_B) = |Users(A) ∩ Users(B)| / |Users(A) ∪ Users(B)|
                </div>

                <h3 style="color: #667eea; margin: 15px 0 10px 0;">2. Interaction Weights</h3>
                <table style="width: auto;">
                    <tr><td>Purchase</td><td><span class="score">5.0</span></td></tr>
                    <tr><td>Add to Cart</td><td><span class="score">3.0</span></td></tr>
                    <tr><td>Rate</td><td><span class="score">2.0</span></td></tr>
                    <tr><td>View</td><td><span class="score">1.0</span></td></tr>
                </table>

                <h3 style="color: #667eea; margin: 15px 0 10px 0;">3. Hybrid Approach</h3>
                <ul style="margin-left: 20px;">
                    <li><strong>Collaborative:</strong> Books mà users tương tự đã mua</li>
                    <li><strong>Content-based:</strong> Books cùng category/author</li>
                    <li><strong>Popularity:</strong> Fallback cho new users (cold start)</li>
                </ul>
            </div>
        </div>

        <div class="footer">
            <p>Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
            <p>BookStore Microservice - Recommender System</p>
        </div>
    </div>
</body>
</html>"""

    return html


def generate_console_report():
    """Generate console report."""
    total_interactions = UserInteraction.objects.count()
    total_similarities = BookSimilarity.objects.count()

    print("=" * 70)
    print("           BOOK RECOMMENDER SYSTEM - DEMO REPORT")
    print("=" * 70)
    print(f"\n  Total Interactions: {total_interactions:,}")
    print(f"  Total Similarities: {total_similarities:,}")

    print("\n" + "-" * 70)
    print("  POPULAR BOOKS (Last 30 days)")
    print("-" * 70)
    popular = recommender_engine.get_popular_books(limit=5)
    for i, rec in enumerate(popular, 1):
        print(f"  {i}. Book #{rec['book_id']:3d}  |  Score: {rec['score']:.2f}")

    print("\n" + "-" * 70)
    print("  TRENDING BOOKS (Last 7 days)")
    print("-" * 70)
    trending = recommender_engine.get_trending_books(limit=5)
    for i, rec in enumerate(trending, 1):
        print(f"  {i}. Book #{rec['book_id']:3d}  |  Score: {rec['score']:.2f}")

    print("\n" + "-" * 70)
    print("  SIMILAR BOOKS (Collaborative Filtering)")
    print("-" * 70)
    sample = UserInteraction.objects.filter(interaction_type='purchase').first()
    if sample:
        similar = recommender_engine.get_similar_books(sample.book_id, limit=5)
        print(f"  Similar to Book #{sample.book_id}:")
        for i, rec in enumerate(similar, 1):
            print(f"    {i}. Book #{rec['book_id']:3d}  |  Score: {rec['score']:.4f}  |  {rec['reason']}")

    print("\n" + "-" * 70)
    print("  PERSONALIZED RECOMMENDATIONS")
    print("-" * 70)
    sample_user = UserInteraction.objects.values('customer_id').first()
    if sample_user:
        user_id = sample_user['customer_id']
        print(f"  For User #{user_id}:")

        history = UserInteraction.objects.filter(customer_id=user_id)[:5]
        print("  History:", ", ".join([f"Book {h.book_id}({h.interaction_type})" for h in history]))

        personalized = recommender_engine.get_personalized_recommendations(user_id, limit=5)
        print("  Recommendations:")
        for i, rec in enumerate(personalized, 1):
            print(f"    {i}. Book #{rec['book_id']:3d}  |  Score: {rec['score']:.4f}  |  {rec['reason']}")

    print("\n" + "=" * 70)
    print("                         END OF REPORT")
    print("=" * 70)


if __name__ == '__main__':
    # Generate console report
    generate_console_report()

    # Generate HTML report
    html = generate_html_report()
    report_path = 'recommendation_report.html'
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write(html)

    print(f"\n  HTML Report saved to: {report_path}")
    print(f"  Open in browser: file://{os.path.abspath(report_path)}")

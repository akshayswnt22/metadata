from app import app, db, Page

with app.app_context():
    # Optional: Clear existing data
    Page.query.delete()

    # Dummy data
    pages = [
        Page(
            title="Python Basics",
            url="https://example.com/python-basics",
            meta_title="Learn Python Basics",
            meta_description="An introduction to Python programming for beginners.",
            meta_keywords="python, programming, beginner, code"
        ),
        Page(
            title="Flask Web Development",
            url="https://example.com/flask-guide",
            meta_title="Web Development with Flask",
            meta_description="Build powerful web applications using Flask.",
            meta_keywords="flask, web, python, framework"
        ),
        Page(
            title="Meta Tags for SEO",
            url="https://example.com/meta-seo",
            meta_title="Understanding Meta Tags",
            meta_description="How meta tags affect search engine optimization.",
            meta_keywords="meta tags, SEO, search engine, optimization"
        ),
        Page(
            title="Machine Learning Guide",
            url="https://example.com/ml-guide",
            meta_title="Intro to Machine Learning",
            meta_description="Start your machine learning journey here.",
            meta_keywords="machine learning, AI, python, data"
        ),
        Page(
            title="Web Security Essentials",
            url="https://example.com/security",
            meta_title="Web App Security",
            meta_description="Best practices for securing web applications.",
            meta_keywords="security, web, flask, HTTPS, API"
        )
    ]

    # Add and commit
    db.session.add_all(pages)
    db.session.commit()

    print("✅ Dummy data inserted.")

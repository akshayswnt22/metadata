from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
import os

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Configure Database
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'metadata.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Admin credentials (for demo only)
ADMIN_USERNAME = 'admin'
ADMIN_PASSWORD = 'admin123'

# Model for storing metadata
class Page(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    url = db.Column(db.String(100), nullable=False)
    meta_title = db.Column(db.String(150))
    meta_description = db.Column(db.Text)
    meta_keywords = db.Column(db.Text)

    def keywords_list(self):
        return [kw.strip().lower() for kw in self.meta_keywords.split(',') if kw.strip()]

with app.app_context():
    db.create_all()


@app.route('/')
def home():
    page = request.args.get('page', 1, type=int)
    per_page = 5
    pagination = Page.query.paginate(page=page, per_page=per_page)
    return render_template('home.html', pages=pagination.items, pagination=pagination)


@app.route('/admin')
def admin():
    if 'admin_logged_in' not in session:
        flash('Please login as admin to view the dashboard.', 'danger')
        return redirect(url_for('login'))

    total_pages = Page.query.count()
    keyword_count = {}
    for page in Page.query.all():
        for kw in page.keywords_list():
            keyword_count[kw] = keyword_count.get(kw, 0) + 1
    sorted_keywords = sorted(keyword_count.items(), key=lambda x: x[1], reverse=True)[:10]
    return render_template('admin.html', total_pages=total_pages, top_keywords=sorted_keywords)

@app.route('/add', methods=['GET', 'POST'])
def add_page():
    if 'admin_logged_in' not in session:
        flash('Please login as admin to access this page.', 'danger')
        return redirect(url_for('login'))

    if request.method == 'POST':
        title = request.form['title']
        url = request.form['url']
        meta_title = request.form['meta_title']
        meta_description = request.form['meta_description']
        meta_keywords = request.form['meta_keywords']

        page = Page(title=title, url=url, meta_title=meta_title, meta_description=meta_description, meta_keywords=meta_keywords)
        db.session.add(page)
        db.session.commit()
        flash('Page added successfully!', 'success')
        return redirect(url_for('home'))
    return render_template('add_page.html')

@app.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit_page(id):
    if 'admin_logged_in' not in session:
        flash('Please login as admin to edit metadata.', 'danger')
        return redirect(url_for('login'))

    page = Page.query.get_or_404(id)
    if request.method == 'POST':
        page.title = request.form['title']
        page.url = request.form['url']
        page.meta_title = request.form['meta_title']
        page.meta_description = request.form['meta_description']
        page.meta_keywords = request.form['meta_keywords']
        db.session.commit()
        flash('Metadata updated successfully!', 'success')
        return redirect(url_for('home'))
    return render_template('edit_page.html', page=page)

@app.route('/delete/<int:id>', methods=['POST'])
def delete_page(id):
    if 'admin_logged_in' not in session:
        flash('Please login as admin to delete metadata.', 'danger')
        return redirect(url_for('login'))

    page = Page.query.get_or_404(id)
    db.session.delete(page)
    db.session.commit()
    flash('Page deleted successfully!', 'info')
    return redirect(url_for('home'))

@app.route('/search')
def search():
    query = request.args.get('q', '')
    results = []
    if query:
        keywords = query.lower().split()
        pages = Page.query.all()
        for page in pages:
            score = sum(kw in page.keywords_list() for kw in keywords)
            if score > 0:
                results.append((score, page))
        results.sort(reverse=True)
    return render_template('search.html', query=query, results=[r[1] for r in results])

@app.route('/report')
def report():
    if 'admin_logged_in' not in session:
        flash('Please login as admin to view the report.', 'danger')
        return redirect(url_for('login'))

    pages = Page.query.all()
    keyword_count = {}
    for page in pages:
        for kw in page.keywords_list():
            keyword_count[kw] = keyword_count.get(kw, 0) + 1
    sorted_keywords = sorted(keyword_count.items(), key=lambda x: x[1], reverse=True)
    return render_template('report.html', pages=pages, keywords=sorted_keywords)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
            session['admin_logged_in'] = True
            flash('Login successful.', 'success')
            return redirect(url_for('home'))
        else:
            flash('Invalid credentials.', 'danger')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('admin_logged_in', None)
    flash('Logged out successfully.', 'info')
    return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(debug=True)

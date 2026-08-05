from flask import Flask, abort, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required

import config as app_config
from auth import auth_bp
from clean import clean
from department_configs import DEPARTMENTS
from extensions import db, login_manager
from extract import extract
from insights import generate_insight
from kpis import calculate_kpis
from models import UploadedReport, User
from report import build_report, format_number
from send import send_report
from uploads import uploads_bp

app = Flask(__name__)
app.secret_key = app_config.SECRET_KEY
app.config["SQLALCHEMY_DATABASE_URI"] = app_config.DATABASE_URL
app.jinja_env.globals["format_number"] = format_number

db.init_app(app)
login_manager.init_app(app)
app.register_blueprint(auth_bp)
app.register_blueprint(uploads_bp)

with app.app_context():
    db.create_all()


@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))


@app.context_processor
def inject_globals():
    my_uploads = []
    if current_user.is_authenticated:
        my_uploads = (
            UploadedReport.query.filter_by(user_id=current_user.id)
            .order_by(UploadedReport.created_at.desc())
            .limit(10)
            .all()
        )
    return {"departments": DEPARTMENTS.values(), "my_uploads": my_uploads, "active_upload_id": None}


THEMES = [
    {"key": "indigo", "name": "Indigo", "swatch": ("#4338ca", "#0d9488")},
    {"key": "dark", "name": "Dark", "swatch": ("#818cf8", "#2dd4bf")},
    {"key": "pink", "name": "Blush & Gold", "swatch": ("#db2777", "#d97706")},
]


def _load_kpis(key: str) -> dict:
    department = DEPARTMENTS[key]
    df = extract(department)
    df = clean(df, department)
    return calculate_kpis(df, department)


@app.route("/")
@login_required
def index():
    summaries = []
    for department in DEPARTMENTS.values():
        try:
            summaries.append({"config": department, "kpis": _load_kpis(department.key)})
        except Exception:
            continue
    return render_template("index.html", summaries=summaries)


@app.route("/department/<key>")
@login_required
def department(key):
    if key not in DEPARTMENTS:
        return redirect(url_for("index"))

    kpis = _load_kpis(key)
    insight = generate_insight(kpis)
    return render_template(
        "department.html",
        active_key=key,
        kpis=kpis,
        insight=insight,
        dry_run=app_config.DRY_RUN,
        send_url=url_for("send", key=key),
        default_email=current_user.email,
    )


@app.route("/department/<key>/send", methods=["POST"])
@login_required
def send(key):
    if key not in DEPARTMENTS:
        return redirect(url_for("index"))

    department_config = DEPARTMENTS[key]
    kpis = _load_kpis(key)
    insight = generate_insight(kpis)
    report_path = build_report(kpis, insight)

    recipient = request.form.get("email", "").strip() or current_user.email
    subject = f"{department_config.display_name} Report — {kpis['period_end']}"
    send_report(report_path, subject=subject, recipients=[recipient])

    verb = "Logged (dry run)" if app_config.DRY_RUN else "Sent"
    flash(f"{verb}: {subject} → {recipient}")
    return redirect(url_for("department", key=key))


@app.route("/settings", methods=["GET", "POST"])
@login_required
def settings():
    valid_keys = {theme["key"] for theme in THEMES}
    if request.method == "POST":
        theme = request.form.get("theme", "indigo")
        current_user.theme = theme if theme in valid_keys else "indigo"
        db.session.commit()
        flash("Preferences saved.")
        return redirect(url_for("settings"))
    return render_template("settings.html", themes=THEMES)


@app.route("/admin")
@login_required
def admin():
    if not current_user.is_owner:
        abort(403)
    users = User.query.order_by(User.created_at.asc()).all()
    return render_template("admin.html", users=users)


if __name__ == "__main__":
    app.run(debug=True)

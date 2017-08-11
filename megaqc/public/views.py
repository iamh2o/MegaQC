# -*- coding: utf-8 -*-
"""Public section, including homepage and signup."""
from flask import Blueprint, flash, redirect, render_template, request, url_for, abort
from flask_login import login_required, login_user, logout_user, current_user

from megaqc.extensions import login_manager, db
from megaqc.public.forms import LoginForm
from megaqc.user.forms import RegisterForm
from megaqc.user.models import User
from megaqc.model.models import Report, PlotConfig
from megaqc.utils import flash_errors

from sqlalchemy.sql import func, distinct

blueprint = Blueprint('public', __name__, static_folder='../static')


@login_manager.user_loader
def load_user(user_id):
    """Load user by ID."""
    return User.query.get(int(user_id))


@blueprint.route('/')
def home():
    """Home page."""
    return render_template('public/home.html')


@blueprint.route('/login/', methods=['GET', 'POST'])
def login():
    """Log in."""
    form = LoginForm(request.form)
    # Handle logging in
    if request.method == 'POST':
        if form.validate_on_submit():
            login_user(form.user)
            flash('Welcome {}! You are now logged in.'.format(current_user.first_name), 'success')
            redirect_url = request.args.get('next') or url_for('public.home')
            return redirect(redirect_url)
        else:
            flash_errors(form)
    return render_template('public/login.html', form=form)

@blueprint.route('/logout/')
@login_required
def logout():
    """Logout."""
    logout_user()
    flash('You are logged out.', 'info')
    return redirect(url_for('public.home'))


@blueprint.route('/register/', methods=['GET', 'POST'])
def register():
    """Register new user."""
    form = RegisterForm(request.form, csrf_enabled=False)
    if form.validate_on_submit():
        user_id = (db.session.query(func.max(User.user_id)).scalar() or 0)+1
        User.create(
            user_id=user_id,
            username=form.username.data,
            email=form.email.data,
            password=form.password.data,
            first_name=form.first_name.data,
            last_name=form.last_name.data,
            active=True
        )
        flash("Thanks for registering! You're now logged in.", 'success')
        return redirect(url_for('public.home'))
    else:
        flash_errors(form)
    return render_template('public/register.html', form=form)


@blueprint.route('/about/')
def about():
    """About page."""
    return render_template('public/about.html')

@blueprint.route('/new_plot/')
@login_required
def new_plot():
    reports = db.session.query(Report).all()
    plot_types = [x[0] for x in db.session.query(distinct(PlotConfig.section)).all()]
    return render_template('public/plot_choice.html', db=db,User=User, reports=reports, user_token=current_user.api_token, plot_types=plot_types)

@blueprint.route('/report_plot/')
@login_required
def report_plot_select():
    reports = db.session.query(Report).all()
    plot_types = [x[0] for x in db.session.query(distinct(PlotConfig.section)).all()]
    return render_template('public/report_plot_select.html', db=db,User=User, reports=reports, user_token=current_user.api_token, plot_types=plot_types)


@blueprint.route('/report_plot/plot/')
@login_required
def report_plot():
    reports = db.session.query(Report).all()
    plot_types = [x[0] for x in db.session.query(distinct(PlotConfig.section)).all()]
    return render_template('public/report_plot.html', db=db,User=User, reports=reports, user_token=current_user.api_token, plot_types=plot_types)


import pandas as pd
from flask import Blueprint, render_template, request, redirect, url_for, flash, app
from flask_login import login_required, current_user


from sqlalchemy import and_

from project import db
from project.models.models import Favorite, Visited, City, MyPlaces

profile_bp = Blueprint('profile', __name__, template_folder='templates')


@profile_bp.route('/profile')
@login_required
def profile():
    current_user_id = current_user.id
    records = db.session.query(MyPlaces).filter(MyPlaces.user_id == current_user_id).all()
    if len(records) == 0:
        flash("You don't have Your places, you can add them by selecting 'Add +' option", 'info')
    return render_template('profile.html', records=records)


@profile_bp.route('/profile', methods=['POST'])
@login_required
def profile_post():
    city_id = request.form.get('id')
    user_id = current_user.id
    if 'delete' in request.form:
        my_place = MyPlaces.query.get_or_404(city_id)
        db.session.delete(my_place)
        db.session.commit()
        flash('Record deleted', 'info')
    elif 'add' in request.form:
        return redirect(url_for('profile.create'))
    else:
        flash('Something went wrong!', 'danger')
    return redirect(url_for('profile.profile'))


@profile_bp.route('/profile/create', methods=['GET', 'POST'])
@login_required
def create():
    if request.method == 'GET':
        return render_template('create.html')
    if request.method == 'POST':
        current_user_id = current_user.id
        name = request.form['name']
        country = request.form['country']
        admin_name = request.form['admin']
        lat = request.form['lat']
        lng = request.form['lng']
        new_place = MyPlaces(user_id=current_user_id, name=name, country=country, admin_name=admin_name, lat=lat,
                             lng=lng)
        db.session.add(new_place)
        db.session.commit()
        return redirect(url_for('profile.profile'))


@profile_bp.route('/profile/favorite')
@login_required
def favorite():
    records = City.query.join(Favorite, City.id == Favorite.city_id).filter(Favorite.user_id == current_user.id).all()
    if len(records) == 0:
        flash("You don't have any favorite cities", 'info')
    return render_template('favorite.html', records=records)


@profile_bp.route('/profile/favorite', methods=['POST'])
@login_required
def favorite_post():
    city_id = request.form.get('id')
    user_id = current_user.id
    if 'delete' in request.form:
        fav_city = Favorite.query.filter(
            and_(
                Favorite.city_id.like(int(city_id)),
                Favorite.user_id.like(int(user_id))
            )
        ).first()
        db.session.delete(fav_city)
        db.session.commit()
        flash('Record deleted', 'info')
    else:
        flash('Something went wrong!', 'danger')
    return redirect(url_for('profile.favorite'))


@profile_bp.route('/profile/visited')
@login_required
def visited():
    records = City.query.join(Visited, City.id == Visited.city_id).filter(Visited.user_id == current_user.id).all()
    if len(records) == 0:
        flash("You don't have any visited cities", 'info')
    return render_template('visited.html', records=records)


@profile_bp.post('/profile/visited')
def delete_visit():
    city_id = request.form.get('id')
    user_id = current_user.id
    if 'delete' in request.form:
        visited_city = Visited.query.filter(
            and_(
                Visited.city_id.like(int(city_id)),
                Visited.user_id.like(int(user_id))
            )
        ).first()
        db.session.delete(visited_city)
        db.session.commit()
        flash('Record deleted', 'info')
    else:
        flash('Something went wrong!', 'danger')
    return redirect(url_for('profile.visited'))


@profile_bp.route('/profile/statistics')
@login_required
def statistics():
    df = pd.read_sql_query(
        "SELECT country, count(*) as Num FROM City INNER JOIN Favorite ON City.id=Favorite.city_id group by country",
        db.session.bind)
    df1 = pd.read_sql_query(
        "SELECT country, count(*) as Num FROM City INNER JOIN Visited ON City.id=Visited.city_id GROUP BY country",
        db.session.bind)

    labels = list(df['country'])
    data = list(df['Num'])
    lbl = 'Favorite cities'
    labels1 = list(df1['country'])
    data1 = list(df1['Num'])
    lbl1 = 'Visited cities'

    return render_template('statistics.html', data=data, labels=labels, lbl=lbl, data1=data1, labels1=labels1,
                           lbl1=lbl1)

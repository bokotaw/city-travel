import folium
import numpy as np
import pandas as pd

from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import current_user
from pandas import DataFrame
from sklearn.neighbors import KDTree
from sqlalchemy import create_engine, and_, or_
from wikipedia import wikipedia, WikipediaPage

from ..models.models import City
from ..models.models import Favorite
from ..models.models import Visited
from .. import db

main_bp = Blueprint('main', __name__, template_folder='templates')


@main_bp.route('/')
def index():
    return render_template('index.html')


ROWS_PER_PAGE = 40


@main_bp.route('/cities')
def cities():
    page = request.args.get('page', type=int)
    records = City.query.paginate(page=page, per_page=ROWS_PER_PAGE)
    return render_template('cities.html', records=records)


@main_bp.route('/cities', methods=['POST'])
def cities_post():
    city_id = request.form.get('id')
    if current_user.is_authenticated:
        user_id = current_user.id
        if 'visited' in request.form:
            visited_city = Visited.query.filter_by(city_id=city_id).first()
            current_user_id = Visited.query.filter_by(user_id=user_id).first()
            if visited_city and current_user_id:
                flash('City already visited', 'info')
                return redirect(url_for('main.cities'))
            else:
                new_visited_city = Visited(city_id=city_id, user_id=user_id)
                db.session.add(new_visited_city)
                db.session.commit()
                flash('City added to visited', 'success')
                return redirect(url_for('main.cities'))
        elif 'favorite' in request.form:
            favorite_city = Favorite.query.filter_by(city_id=city_id).first()
            current_user_id = Favorite.query.filter_by(user_id=user_id).first()
            if favorite_city and current_user_id:
                flash('City already added to favorites', 'info')
                return redirect(url_for('main.cities'))
            else:
                new_favorite_city = Favorite(city_id=city_id, user_id=user_id)
                db.session.add(new_favorite_city)
                db.session.commit()
                flash('City added to favorites', 'success')
                return redirect(url_for('main.cities'))
        elif 'info' in request.form:
            return redirect(url_for('main.city', id=city_id))
        else:
            flash('Error. Something went wrong2!', 'danger')
            return redirect(url_for('main.cities'))
    elif not current_user.is_authenticated:
        if 'info' in request.form:
            return redirect(url_for('main.city', id=city_id))
        else:
            flash('You must be logged', 'warning')
            return redirect(url_for('main.cities'))
    else:
        flash('Error. Something went wrong1!', 'danger')
        return redirect(url_for('main.cities'))


@main_bp.route('/city/<int:id>')
def city(id):
    city = City.query.get_or_404(id)
    try:
        city_info = wikipedia.summary(city.city, sentences=10, auto_suggest=True)
        city_img = WikipediaPage(title=city.city).images[0]
        city_link = wikipedia.page(city.city).url

        df = pd.read_sql_query("Select id, city, lat, lng from city where id != {}".format(city.id), db.session.bind)

        kd = KDTree(np.deg2rad(df[['lat', 'lng']].values), metric='euclidean')
        distances, indices = kd.query(np.deg2rad([[city.lat, city.lng]]), k=3)
        distances = distances * 6371

        nn_cities = df.loc[indices.flatten()]['city'].to_numpy()

        result = db.session.query(City).filter(
            or_(
                City.city.like(str(nn_cities[0])),
                City.city.like(str(nn_cities[1])),
                City.city.like(str(nn_cities[2]))
            )
        ).all()

        return render_template('city.html', city=city, city_info=city_info, city_img=city_img, city_link=city_link,
                               result=result, distances=distances)
    except wikipedia.PageError as e:
        if 'Does not match any pages' in str(e):
            city_info = 'Non info'
            return render_template('city.html', city=city, city_info=city_info)


@main_bp.route('/map')
def map_page():
    small_fg = folium.FeatureGroup(name='Small Cities')
    medium_fg = folium.FeatureGroup(name='Medium Cities')
    big_fg = folium.FeatureGroup(name='Big Cities')

    my_map = folium.Map(
        location=[52.2167, 21.0333],
        zoom_start=7)
    for row in db.session.query(City).all():

        html = f"""
                <div style="width:164px;
                            height:134px;
                            border-radius: 5px;
                            background-color: #98FB98;
                            color: #888888;
                            text-align: center;">
                                <h5 style="margin:14px">{row.city}</h4>
                                <h6 style="margin:12px">Population: {row.population}</h5>
                                <h6 style="margin:12px">Admin. area: {row.admin_name}</h5>
                                <h6 style="margin:12px">Country: {row.country}</h5>
                                <h6 style="margin:12px">Coordinates: {row.lat}, {row.lng}</h5>
                            </div>
            """
        iframe = folium.IFrame(html=html, width=190, height=160)
        if row.population is None or row.population < 50000:
            small_fg.add_child(folium.CircleMarker(
                location=[float(row.lat), float(row.lng)],
                color='green',
                fill_color='green',
                radius=5,
                fill_opacity=0.7,
                popup=folium.Popup(iframe)
            ))
        elif 50000 <= row.population < 500000:
            medium_fg.add_child(folium.CircleMarker(
                location=[float(row.lat), float(row.lng)],
                color='orange',
                fill_color='orange',
                radius=5,
                fill_opacity=0.7,
                popup=folium.Popup(iframe)
            ))
        else:
            big_fg.add_child(folium.CircleMarker(
                location=[float(row.lat), float(row.lng)],
                color='red',
                fill_color='red',
                radius=5,
                fill_opacity=0.7,
                popup=folium.Popup(iframe)
            ))

    my_map.add_child(small_fg)
    my_map.add_child(medium_fg)
    my_map.add_child(big_fg)
    folium.LayerControl().add_to(my_map)

    return render_template('map.html', my_map=my_map._repr_html_())

from flask import Flask, render_template, redirect, url_for, request

from flask import Flask, render_template, redirect, url_for, request
from flask_bootstrap import Bootstrap5
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import Integer, String, Float
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired
import requests

'''
Red underlines? Install the required packages first: 
Open the Terminal in PyCharm (bottom left). 

On Windows type:
python -m pip install -r requirements.txt

On MacOS type:
pip3 install -r requirements.txt

This will install the packages from requirements.txt for this project.
'''


class Base(DeclarativeBase):
    pass


db = SQLAlchemy(model_class=Base)
app = Flask(__name__)
app.config['SECRET_KEY'] = '8BYkEfBA6O6donzWlSihBXox7C0sKR6b'
Bootstrap5(app)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///100-movies-collection.db"
TMDB_API_KEY = 'bbc6c34fceca7fcb7f119a967f861ba4'
db.init_app(app)


# CREATE DB


# CREATE TABLE


class Movie(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(unique=True, nullable=False)
    year: Mapped[int] = mapped_column(nullable=False)
    description: Mapped[str] = mapped_column(nullable=False)
    rating: Mapped[float] = mapped_column(nullable=False)
    ranking: Mapped[int] = mapped_column(nullable=False)
    review: Mapped[str] = mapped_column(nullable=False)
    img_url: Mapped[str] = mapped_column(nullable=False)


with app.app_context():
    db.create_all()


# second_movie = Movie(
#     title="Avatar The Way of Water",
#     year=2022,
#     description="Set more than a decade after the events of the first film, learn the story of the Sully family (Jake, Neytiri, and their kids), the trouble that follows them, the lengths they go to keep each other safe, the battles they fight to stay alive, and the tragedies they endure.",
#     rating=7.3,
#     ranking=9,
#     review="I liked the water.",
#     img_url="https://image.tmdb.org/t/p/w500/t6HIqrRAclMCA60NsSmeqe9RmNV.jpg"
# )
# with app.app_context():
#     db.session.add(second_movie)
#     db.session.commit()

@app.route("/")
def home():
    with app.app_context():
        result = db.session.execute(db.select(Movie).order_by(Movie.rating))
        all_movies = result.scalars().all()
        number_of_movies=len(all_movies)
        for i,movie in enumerate(all_movies):
            movie.ranking=number_of_movies-i
            i+=1
    return render_template("index.html", data=all_movies)


class RateMovieForm(FlaskForm):
    rating = StringField("Your Rating Out of 10 e.g. 7.5")
    review = StringField("Your Review")
    submit = SubmitField("Done")


class AddMovieForm(FlaskForm):
    title = StringField("Movie Title")
    submit = SubmitField("Add Movie")


@app.route("/edit", methods=["GET", "POST"])
def edit():
    form = RateMovieForm()
    movie_id = request.args.get("id")
    movie = db.get_or_404(Movie, movie_id)
    if form.validate_on_submit():
        with app.app_context():
            movie_to_update = db.session.execute(db.select(Movie).filter(
                Movie.id == movie_id)).scalar_one_or_none()
            movie_to_update.rating = float(form["rating"].data)
            movie_to_update.review = str(form["review"].data)
            db.session.commit()
        return redirect(url_for('home'))
    return render_template("edit.html", movie=movie, form=form)


@app.route("/delete")
def delete():
    movie_id = request.args.get("id")
    with app.app_context():
        movie_to_delete = db.session.execute(db.select(Movie).filter(
            Movie.id == movie_id)).scalar_one_or_none()
        db.session.delete(movie_to_delete)
        db.session.commit()
    return redirect(url_for('home'))


@app.route("/add", methods=["GET", "POST"])
def add():
    form = AddMovieForm()
    if form.validate_on_submit():
        title = str(form["title"].data)
        text = '+'.join(title.split())
        url = (f'https://api.themoviedb.org/3/search/movie?query={text}&'
               f'api_key={TMDB_API_KEY}')
        api_call = requests.get(url).json()["results"]
        return render_template("select.html", data=api_call)

    return render_template("add.html", form=form)


@app.route("/find_movie")
def find_movie():
    movie_id = request.args.get('id')
    url = (f"https://api.themoviedb.org/3/movie/"
           f"{movie_id}?api_key=bbc6c34fceca7fcb7f119a967f861ba4")

    response = requests.get(url)
    data = response.json()
    year = data['release_date'].split('-')
    new_movie = Movie(
        title=data['original_title'],
        year=int(year[0]),
        description=data['overview'],
        rating=6.9,
        ranking=5,
        review="abebe",
        img_url=f"https://image.tmdb.org/t/p/w500/{data['poster_path']}"
    )
    with app.app_context():
        db.session.add(new_movie)
        db.session.commit()
        all_movies = db.session.execute(db.select(Movie).order_by(Movie.id))
        all_movies = all_movies.scalars()
        movie_list = []
        for movie in all_movies:
            movie_list.append(movie)
        newest_movie = movie_list[-1]
    return redirect(url_for('edit', id=newest_movie.id))


if __name__ == '__main__':
    app.run(debug=True)

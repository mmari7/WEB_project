from flask import Flask, render_template, redirect, request
from data import db_session
from data.users import User
from data.wishLists import Wishlist
from data.wishes import Wish
from forms.user import RegisterForm
from forms.user import LoginForm
from forms.wishlist import WishlistForm
from flask_login import LoginManager, login_required, login_user, logout_user, current_user
from wb_parce import parser, get_data_category, get_catalogs_wb


app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'
login_manager = LoginManager()
login_manager.init_app(app)


@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.query(User).get(user_id)


@app.route("/")
def index():
    return render_template("index.html")


@app.route('/parse', methods=['GET', 'POST'])
def parse():
    catalog = get_data_category(get_catalogs_wb())[1:]
    try:
        if request.method == 'GET':
            return render_template("parse.html", filter="", catalog=catalog, data_products=[], col=0)
        elif request.method == 'POST':
            print('Нажали на кнопку')
            cat = list(set([i['seo'] for i in catalog if request.form.get(i['seo'])]))
            data_products = []
            discount = int(request.form.get('discount')) if request.form.get('discount') else 0
            for i in cat:
                data_products += parser(seo=i, discount=discount)
            data_products = list(set(data_products))
            if data_products:
                col = len(data_products)
                return render_template("parse.html", message=f"Товары категории: {', '.join(cat)}",
                                       catalog=catalog, data_products=data_products, col=col)
            else:
                return render_template("parse.html", filter="", catalog=catalog, data_products=[], col=0,
                                       message='Нет таких товаров')
    except:
        return render_template("parse.html", filter="", catalog=catalog, data_products=[], col=0,
                               message='Что-то пошло не так')


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        if form.password.data != form.password_again.data:
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Password mismatch")
        db_sess = db_session.create_session()
        if db_sess.query(User).filter(User.email == form.email.data.lower()).first():
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="There is already such a user")
        elif db_sess.query(User).filter(User.name == form.name.data).first():
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="This Username has already taken")
        user = User(
            name=form.name.data,
            email=form.email.data.lower(),
            about=form.about.data
        )
        user.set_password(form.password.data)
        db_sess.add(user)
        wishlist = Wishlist(
            name='all',
            user=user
        )
        db_sess.add(wishlist)
        db_sess.commit()
        return redirect('/login')
    return render_template('register.html', title='Registration', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.email == form.email.data.lower()).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            return redirect("/")
        return render_template('login.html',
                               message="Wrong login or password",
                               form=form)
    return render_template('login.html', title='Log In', form=form)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect("/")


@app.route('/make_wishlist', methods=['GET', 'POST'])
@login_required
def make_wishlist():
    form = WishlistForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        if db_sess.query(Wishlist).filter(Wishlist.name == form.name.data).first():
            return render_template('make_wishlist.html', message="You've already had this wishlist", form=form)
        wishlist = Wishlist()
        wishlist.name = form.name.data
        wishlist.is_private = form.is_private.data
        wishlist.user_id = current_user.id
        db_sess.add(wishlist)
        db_sess.merge(current_user)
        db_sess.commit()
        return redirect('/')
    return render_template('make_wishlist.html', form=form)


@app.route('/wishlist/<wishlist_id>/<wishlist_name>')
@login_required
def wishlist(wishlist_id, wishlist_name):
    db_sess = db_session.create_session()
    wishes = db_sess.query(Wish).filter(Wish.wishlist_id == wishlist_id).all()
    return render_template('wishlist.html', wishes=wishes, wishlist_name=wishlist_name)


@login_required
@app.route("/favorite/<url>/<price>/<name>/<sku>/<wishlist_id>", methods=['GET', 'POST'])
def add_or_exclude_item_to_favorite(url, price, sku, name, wishlist_id):
    db_sess = db_session.create_session()
    wish = db_sess.query(Wish).filter(Wish.wishlist_id == wishlist_id & Wish.name == name).first()
    if wish:
        current_user.wishes.remove(wish)
    else:
        link = f'https://www.wildberries.ru/catalog/{sku}/detail.aspx?targetUrl=BP'
        wish = Wish()
        wish.name = str(name).replace('%20', '')
        wish.price = price
        wish.link = link
        wish.wishlist_id = wishlist_id
    db_sess.add(wish)
    db_sess.commit()
    return redirect(f'/{url}')


def main():
    db_session.global_init("db/app.db")
    app.run(port=1234)


if __name__ == '__main__':
    main()

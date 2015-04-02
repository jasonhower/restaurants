from flask import Flask, render_template, url_for, redirect, request, jsonify
app = Flask(__name__)

from sqlalchemy import create_engine, and_
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Restaurant, MenuItem

engine = create_engine('sqlite:///restaurantmenu.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()

# These routes handle all HTML website services
@app.route('/')
@app.route('/restaurants')
def home():
    # Shows all Restaurants
    restaurants = session.query(Restaurant).all()
    return render_template('restaurants.html', restaurants=restaurants)

@app.route('/restaurant/new', methods=['GET', 'POST'])
def newRestaurant():
    # Add a new Restaurant
    if request.method == "POST":
        newRestaurant = Restaurant(name = request.form['newRestaurant'])
        session.add(newRestaurant)
        session.commit()
        return redirect(url_for('home'))
    else:
        return render_template('newRestaurant.html') 

@app.route('/restaurant/<int:rest_id>/edit', methods=['GET', 'POST'])
def editRestaurant(rest_id):
    # Edits a specifies Restaurant Name
    restaurant = session.query(Restaurant).filter_by(id=rest_id).one()
    if request.method == "POST":
        editRestaurant = session.query(Restaurant).filter_by(id=rest_id).one()
        editRestaurant.name = request.form['editRestaurant']
        session.add(editRestaurant)
        session.commit()
        return redirect(url_for('home'))
    else:
        return render_template('editRestaurant.html', restaurant=restaurant)

@app.route('/restaurant/<int:rest_id>/delete', methods=['GET','POST'])
def deleteRestaurant(rest_id):
    # Deletes a specific restaurant
    restaurant = session.query(Restaurant).filter_by(id=rest_id).one()
    if request.method == "POST":
        deleteRestaurant = session.query(Restaurant).filter_by(id=rest_id).one()
        session.delete(deleteRestaurant)
        session.commit()
        return redirect(url_for('home'))
    else:
        return render_template('deleteRestaurant.html', restaurant=restaurant) 

@app.route('/restaurant/<int:rest_id>')
@app.route('/restaurant/<int:rest_id>/menu')
def showMenu(rest_id):
    # Shows the Menu of a Restaurant
    restaurant = session.query(Restaurant).filter_by(id=rest_id).one()
    items = session.query(MenuItem).filter_by(restaurant_id=rest_id).all()
    return render_template('menu.html', restaurant=restaurant, items=items) 

@app.route('/restaurant/<int:rest_id>/menu/new', methods=['GET','POST'])
def newItem(rest_id):
    # Add a new item to a Restaurant's menu
    restaurant = session.query(Restaurant).filter_by(id=rest_id).one()
    if request.method == "POST":
        newItem = MenuItem(name=request.form['itemName'],price=request.form['itemPrice'] , description=request.form['itemDescription'], restaurant_id=rest_id)
        session.add(newItem)
        session.commit()
        return redirect(url_for('showMenu', rest_id=rest_id))
    else:
        return render_template('newMenuItem.html', restaurant=restaurant) 

@app.route('/restaurant/<int:rest_id>/menu/<int:menu_id>/edit', methods=['GET','POST'])
def editItem(rest_id, menu_id):
    # Edit the item in a Restaurant's Menu
    restaurant = session.query(Restaurant).filter_by(id=rest_id).one()
    item = session.query(MenuItem).filter_by(id=menu_id).one()
    if request.method == "POST":
        item.name = request.form['itemName']
        item.price = request.form['itemPrice']
        item.description = request.form['itemDescription']
        session.add(item)
        session.commit()
        return redirect(url_for('showMenu', rest_id=rest_id))
    else:
        return render_template('editMenuItem.html', restaurant=restaurant, item=item) 

@app.route('/restaurant/<int:rest_id>/menu/<int:menu_id>/delete', methods=['GET','POST'])
def deleteItem(rest_id, menu_id):
    # Delete an item from a Restaurant's Menu
    restaurant = session.query(Restaurant).filter_by(id=rest_id).one()
    item = session.query(MenuItem).filter_by(id=menu_id).one()
    if request.method == "POST":
        session.delete(item)
        session.commit()
        return redirect(url_for('showMenu', rest_id=rest_id))
    else:
        return render_template('deleteMenuItem.html', restaurant=restaurant, item=item) 

# These routes hand all REST API requests. They will respond with JSON
@app.route('/restaurants/JSON')
def restaurantsJSON():
    restaurants = session.query(Restaurant).all()
    return jsonify(Restaurants=[r.serialize for r in restaurants])

@app.route('/restaurant/<int:rest_id>/menu/JSON')
def allItemsJSON(rest_id):
    items = session.query(MenuItem).filter_by(restaurant_id=rest_id).all()
    return jsonify(Items=[i.serialize for i in items])

@app.route('/restaurant/<int:rest_id>/menu/<int:menu_id>/JSON')
def oneItemJSON(rest_id, menu_id):
    item = session.query(MenuItem).filter_by(id=menu_id).one()
    return jsonify(Item=[item.serialize])

if __name__ == "__main__":
    app.debug = True
    app.run(host = '0.0.0.0', port = 8000)

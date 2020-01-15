from flask import (
    Flask,
    render_template,
    request,
    redirect,
    url_for,
    flash,
    jsonify,
    make_response,
    session as login_session
)
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from ic_database_setup import Base, User, Category, Item
from oauth2client.client import (
    flow_from_clientsecrets,
    FlowExchangeError
)

import random
import string
import httplib2
import json
import requests


app = Flask(__name__)
app.secret_key = "super secret key"


CLIENT_ID = json.loads(
    open('client_secrets.json', 'r').read())['web']['client_id']
APPLICATION_NAME = "Category Item Application"


engine = create_engine('sqlite:///itemcategory.db',
                       connect_args={'check_same_thread': False})
Base.metadata.bind = create_engine

DBSession = sessionmaker(bind=engine)
session = DBSession()


# Create a state token to prevent request forgery.
# Store it in the session for later validation.
@app.route('/login')
def showLogin():
    """
    showLogin function returns login.html page.

    showLogin function takes the following parameters.
    args:
    N/A

    returns:
    display login.html page.
    """
    state = ''.join(random.choice(string.ascii_uppercase +
                    string.digits) for x in xrange(32))
    login_session['state'] = state
    # RENDER THE ORIGIN TEMPLATE
    return render_template('login.html', STATE=state)


@app.route('/fbconnect', methods=['POST'])
def fbconnect():
    """
    fbconnect function authenticates facebook user, being called from
    login.html.

    fbconnect function takes the following parameters.
    args:
    N/A

    returns:
    facebook user information after authentication.
    """
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    access_token = request.data
    print "access token received %s " % access_token

    app_id = json.loads(open('fb_client_secrets.json', 'r').read())[
        'web']['app_id']
    app_secret = json.loads(
        open('fb_client_secrets.json', 'r').read())['web']['app_secret']
    url = 'https://graph.facebook.com/oauth/access_token?grant_type='\
        'fb_exchange_token&client_id=%s&client_secret=%s&'\
        'fb_exchange_token=%s' % (app_id, app_secret, access_token)
    h = httplib2.Http()
    result = h.request(url, 'GET')[1]

    # Use token to get user info from API
    userinfo_url = "https://graph.facebook.com/v2.8/me"
    '''
        Due to the formatting for the result from the server token exchange
        we have to split the token first on commas and select the first index
        which gives us the key : value for the server access token then we
        split it on colons to pull out the actual token value and replace the
        remaining quotes with nothing so that it can be used directly in the
        graph api calls
    '''
    token = result.split(',')[0].split(':')[1].replace('"', '')

    url = 'https://graph.facebook.com/v2.8/me?access_token=%s&'\
        'fields=name,id,email' % token
    h = httplib2.Http()
    result = h.request(url, 'GET')[1]
    # print "url sent for API access:%s"% url
    # print "API JSON result: %s" % result
    data = json.loads(result)
    login_session['provider'] = 'facebook'
    login_session['username'] = data["name"]
    login_session['email'] = data["email"]
    login_session['facebook_id'] = data["id"]

    # The token must be stored in the login_session in order to properly logout
    login_session['access_token'] = token

    # Get user picture
    url = 'https://graph.facebook.com/v2.8/me/picture?access_token=%s&'\
        'redirect=0&height=200&width=200' % token
    h = httplib2.Http()
    result = h.request(url, 'GET')[1]
    data = json.loads(result)

    login_session['picture'] = data["data"]["url"]

    # see if user exists
    user_id = getUserID(login_session['email'])
    if not user_id:
        user_id = createUser(login_session)
    login_session['user_id'] = user_id

    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']

    output += '!</h1>'
    output += '<img src="'
    output += login_session['picture']
    output += ' " style = "width: 300px; \
                           height: 300px; \
                           border-radius: 150px; \
                           -webkit-border-radius: 150px; \
                           -moz-border-radius: 150px;"> '

    flash("Now logged in as %s" % login_session['username'])
    return output


@app.route('/fbdisconnect')
def fbdisconnect():
    """
    fbdisconnect function disconnect logged-in facebook user, being called from
    disconnect() function.

    fbdisconnect function takes the following parameters.
    args:
    N/A

    returns:
    facebook user disconnected.
    """
    facebook_id = login_session['facebook_id']
    # The access token must me included to successfully logout
    access_token = login_session['access_token']
    url = 'https://graph.facebook.com/%s/permissions?access_token=%s' \
        % (facebook_id, access_token)
    h = httplib2.Http()
    result = h.request(url, 'DELETE')[1]
    return "you have been logged out"


@app.route('/gconnect', methods=['POST'])
def gconnect():
    """
    gconnect function authenticates google user, being called from
    login.html.

    gconnect function takes the following parameters.
    args:
    N/A

    returns:
    google user information after authentication.
    """
    # Validate state token
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    # Obtain authorization code
    code = request.data

    try:
        # Upgrade the authorization code into a credentials object
        oauth_flow = flow_from_clientsecrets('client_secrets.json', scope='')
        oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(code)
    except FlowExchangeError:
        response = make_response(
            json.dumps('Failed to upgrade the authorization code.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Check that the access token is valid.
    access_token = credentials.access_token
    url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s'
           % access_token)
    h = httplib2.Http()
    result = json.loads(h.request(url, 'GET')[1])
    # If there was an error in the access token info, abort.
    if result.get('error') is not None:
        response = make_response(json.dumps(result.get('error')), 500)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is used for the intended user.
    gplus_id = credentials.id_token['sub']
    if result['user_id'] != gplus_id:
        response = make_response(
            json.dumps("Token's user ID doesn't match given user ID."), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is valid for this app.
    if result['issued_to'] != CLIENT_ID:
        response = make_response(
            json.dumps("Token's client ID does not match app's."), 401)
        print "Token's client ID does not match app's."
        response.headers['Content-Type'] = 'application/json'
        return response

    stored_access_token = login_session.get('access_token')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_access_token is not None and gplus_id == stored_gplus_id:
        response = make_response(json.dumps(
            'Current user is already connected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Store the access token in the session for later use.
    login_session['access_token'] = credentials.access_token
    login_session['gplus_id'] = gplus_id

    # Get user info
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)

    data = answer.json()

    login_session['username'] = data['name']
    login_session['picture'] = data['picture']
    login_session['email'] = data['email']

    # assign provider value so that disconnect() can properly route
    login_session['provider'] = 'google'

    # see if user exists, if it doesn't make a new one
    user_id = getUserID(login_session['email'])
    if not user_id:
        user_id = createUser(login_session)
    login_session['user_id'] = user_id

    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']
    output += '!</h1>'
    output += '<img src="'
    output += login_session['picture']
    output += ' " style = "width: 300px; \
                           height: 300px; \
                           border-radius: 150px; \
                           -webkit-border-radius: 150px; \
                           -moz-border-radius: 150px;"> '
    flash("you are now logged in as %s" % login_session['username'])
    print "done!"
    return output


def createUser(login_session):
    """
    createUser function create the logged-in user as a user with
    this application.

    createUser function takes the following parameters.
    args:
    login_session

    returns:
    a new user is created in user table
    """
    newUser = User(name=login_session['username'],
                   email=login_session['email'])
    session.add(newUser)
    session.commit()
    user = session.query(User).filter_by(email=login_session['email']).one()
    return user.id


def getUserInfo(user_id):
    """
    getUserInfo function gets user information per user_id.

    getUserInfo function takes the following parameters.
    args:
    user_id

    returns:
    a user object for the input user_id
    """
    user = session.query(User).filter_by(id=user_id).one()
    return user


def getUserID(email):
    """
    getUserID function gets user id per logged-in user email.

    getUserID function takes the following parameters.
    args:
    email

    returns:
    the user's id per his/her email
    """
    try:
        user = session.query(User).filter_by(email=email).one()
        return user.id
    except Exception:
        return None


@app.route('/gdisconnect')
def gdisconnect():
    """
    gdisconnect function disconnect logged-in google user, being called from
    disconnect() function.

    gdisconnect function takes the following parameters.
    args:
    N/A

    returns:
    google user disconnected.
    """
    access_token = login_session.get('access_token')
    if access_token is None:
        print 'Access Token is None'
        response = make_response(json.dumps('Current user not connected.'),
                                 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    print 'In gdisconnect access token is %s', access_token
    print 'User name is: '
    print login_session['username']
    url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' \
          % login_session['access_token']
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]
    print 'result is '
    print result
    if result['status'] == '200':
        del login_session['access_token']
        del login_session['gplus_id']
        del login_session['username']
        del login_session['email']
        del login_session['picture']
        response = make_response(json.dumps('Successfully disconnected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        return response
    else:
        response = make_response(json.dumps(
                                'Failed to revoke token for given user.',
                                400))
        response.headers['Content-Type'] = 'application/json'
        return response


# Making an JSON API Endpoint (GET Request)
# view category table data only
@app.route('/categories/JSON')
def categoriesJSON():
    """
    categoriesJSON function show endpoints of category table.

    categoriesJSON function takes the following parameters.
    args:
    N/A

    returns:
    JSON endpoint for categories.
    """
    categories = session.query(Category).all()
    return jsonify(categories=[r.serialize for r in categories])


# view items for a specific category data only
@app.route('/categories/<int:category_id>/item/JSON')
def showItemJSON(category_id):
    """
    showItemJSON function show endpoints of item table per category_id.

    showItemJSON function takes the following parameters.
    args:
    N/A

    returns:
    JSON endpoint for items per category_id.
    """
    category = session.query(Category).filter_by(id=category_id).one()
    items = session.query(Item).filter_by(category_id=category_id).all()
    return jsonify(Items=[i.serialize for i in items])


# view a specific item data only
@app.route('/categories/<int:category_id>/item/<int:item_id>/JSON')
def itemJSON(category_id, item_id):
    """
    itemJSON function show endpoints of a particular item per item_id.

    itemJSON function takes the following parameters.
    args:
    category_id, item_id

    returns:
    JSON endpoint for a particular item per item_id.
    """
    item = session.query(Item).filter_by(id=item_id).one()
    return jsonify(Item=item.serialize)


# Show all categories:
@app.route('/')
@app.route('/categories')
def showCategories():
    """
    showCategories function shows all categories.

    showCategories function takes the following parameters.
    args:
    N/A

    returns:
    display all categories in categories.html page.
    """
    categories = session.query(Category).all()
    return render_template('categories.html', categories=categories)


# Create a new category
@app.route('/category/new', methods=['GET', 'POST'])
def newCategory():
    """
    newCategory function allows user to create a new category.

    newCategory function takes the following parameters.
    args:
    N/A

    returns:
    a new category and stored in category table.
    """
    # check authentication
    if 'username' not in login_session:
        return redirect('/login')
    if request.method == 'POST':  # executed when POST is performed
        newCategory = Category(
            name=request.form['name'],
            user_id=login_session['user_id'])
        session.add(newCategory)
        session.commit()
        flash("New Category Created!")
        return redirect(url_for('showCategories'))
    else:  # executed when GET is performed
        return render_template('newCategory.html')


# Edit a category
@app.route('/category/<int:category_id>/edit', methods=['GET', 'POST'])
def editCategory(category_id):
    """
    editCategory function allows user to edit an existing category per
    category_id.

    editCategory function takes the following parameters.
    args:
    category_id

    returns:
    an existing category is being updated and stored in category table.
    """
    # check authentication
    if 'username' not in login_session:
        return redirect('/login')
    editedCategory = session.query(Category).filter_by(id=category_id).one()
    if editedCategory.user_id != login_session['user_id']:
        return render_template('unauthorized.html')
    if request.method == 'POST':
        if request.form['name']:
            editedCategory.name = request.form['name']
        session.add(editedCategory)
        session.commit()
        flash("Category successfully Edited!")
        return redirect(url_for('showCategories'))
    else:
        return render_template('editCategory.html',
                               category_id=category_id,
                               category=editedCategory)


# Delete a category
@app.route('/category/<int:category_id>/delete', methods=['GET', 'POST'])
def deleteCategory(category_id):
    """
    deleteCategory function allows user to delete an existing category per
    category_id.

    deleteCategory function takes the following parameters.
    args:
    category_id

    returns:
    an existing category is being deleted from category table.
    """
    # check authentication
    if 'username' not in login_session:
        return redirect('/login')
    categoryToDelete = session.query(Category).filter_by(id=category_id).one()
    # check authorization
    if categoryToDelete.user_id != login_session['user_id']:
        return render_template('unauthorized.html')
    if request.method == 'POST':
        session.delete(categoryToDelete)
        session.commit()
        flash("Category Successfully Deleted!")
        return redirect(url_for('showCategories'))
    else:
        return render_template('deleteCategory.html',
                               category=categoryToDelete)


# Show items within a category
@app.route('/category/<int:category_id>/')
@app.route('/category/<int:category_id>/item')
def showItem(category_id):
    """
    showItem function shows all the items belonging to a particular category

    showItem function takes the following parameters.
    args:
    category_id

    returns:
    display all items of a category in item.html.
    """
    # check authentication
    if 'username' not in login_session:
        return redirect('/login')
    category_authorized = 'N'
    category = session.query(Category).filter_by(id=category_id).one()

    # check authorization: determine show/hide "Edit Category" and
    # "Delete Category" button in item.html
    if category.user_id == login_session['user_id']:
        category_authorized = 'Y'

    items = session.query(Item).filter_by(category_id=category_id)
    return render_template(
        'item.html',
        items=items,
        category=category,
        c_authorized=category_authorized,
        login_user_id=login_session['user_id'])


# Create a new category item
@app.route('/category/<int:category_id>/item/new', methods=['GET', 'POST'])
def newItem(category_id):
    """
    newItem function creates a new item of a particular category

    newItem function takes the following parameters.
    args:
    category_id

    returns:
    create a new item in newItem.html.
    """
    # check authentication
    if 'username' not in login_session:
        return redirect('/login')
    if request.method == 'POST':  # executed when POST is performed
        newItem = Item(
            name=request.form['name'],
            description=request.form['description'],
            category_id=category_id,
            user_id=login_session['user_id'])
        app.logger.debug("output: " + str(category_id))
        session.add(newItem)
        session.commit()
        flash("Category Item Created!")
        return redirect(url_for('showItem', category_id=category_id))
    else:  # executed when GET is performed
        return render_template('newItem.html', category_id=category_id)


# Edit a category item
@app.route('/category/<int:category_id>/<int:item_id>/edit',
           methods=['GET', 'POST'])
def editItem(category_id, item_id):
    """
    editItem function edits an existing item

    editItem function takes the following parameters.
    args:
    category_id, item_id

    returns:
    edit an existing item in editItem.html.
    """
    # check authentication
    if 'username' not in login_session:
        return redirect('/login')
    editedItem = session.query(Item).filter_by(id=item_id).one()
    # check authorization
    if editedItem.user_id != login_session['user_id']:
        return render_template('unauthorized.html')
    if request.method == 'POST':
        if request.form['name']:
            editedItem.name = request.form['name']
        if request.form['description']:
            editedItem.description = request.form['description']
        session.add(editedItem)
        session.commit()
        flash("Category Item Successfully Edited (item.html)")
        return redirect(url_for('showItem', category_id=category_id))
    else:
        return render_template('editItem.html',
                               category_id=category_id,
                               item_id=item_id,
                               item=editedItem)


# Delete a category item
@app.route('/category/<int:category_id>/<int:item_id>/delete',
           methods=['GET', 'POST'])
def deleteItem(category_id, item_id):
    """
    deleteItem function deletes an existing item

    deleteItem function takes the following parameters.
    args:
    category_id, item_id

    returns:
    delete an existing item in deleteItem.html.
    """
    # check authentication
    if 'username' not in login_session:
        return redirect('/login')
    itemToDelete = session.query(Item).filter_by(id=item_id).one()
    # check authorization
    if itemToDelete.user_id != login_session['user_id']:
        return render_template('unauthorized.html')
    if request.method == 'POST':
        session.delete(itemToDelete)
        session.commit()
        flash("Category Item Successfully Deleted (categories.html)")
        return redirect(url_for('showItem', category_id=category_id))
    else:
        return render_template('deleteItem.html', item=itemToDelete)


# Disconnect based on provider either google or facebook
@app.route('/disconnect')
def disconnect():
    """
    disconnect function allows user to log out

    disconnect function takes the following parameters.
    args:
    N/A

    returns:
    user log out through a link in header.html.
    """
    if 'provider' in login_session:
        if login_session['provider'] == 'google':
            gdisconnect()
            # del login_session['gplus_id']
            # del login_session['access_token']
        if login_session['provider'] == 'facebook':
            fbdisconnect()
            del login_session['facebook_id']
        # del login_session['username']
        # del login_session['email']
        # del login_session['picture']
        del login_session['user_id']
        del login_session['provider']
        flash("You have successfully been logged out.")
        return redirect(url_for('showLogin'))
    else:
        flash("You were not logged in")
        return redirect(url_for('showLogin'))


if __name__ == '__main__':
    app.secret_ley = 'super_secret_key'
    app.debug = True
    app.run(host='0.0.0.0', port=8000)

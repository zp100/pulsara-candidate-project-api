################################################################
#   File:   app.y
#   Desc:   Python Flask RESTful back-end for managing
#               requests.
#   Author: Zachariah Preston
#   Date:   2024-01-11
################################################################

# Import packages.
import flask
import mysql.connector as sql

# App setup.
app = flask.Flask(__name__)



################################################################
#   Func:   root
#   Desc:   Route function for root URL.
#   Params: None
#   Ret:    <flask.Response>: HTTP response that contains the
#               queried data as a JSON object.
################################################################
@app.route('/', methods=['GET'])
def root():
    # Test that the database is accessible.
    try:
        # Connect to the MySQL database.
        conn = sql.connect(
            host='localhost',
            user='root',
            password='password',
            database='main',
        )
        cur = conn.cursor()
    except sql.errors.DatabaseError:
        # Couldn't connect to database.
        flask.abort(503, 'Server failed to connect to the SQL database.')

    # DEBUG
    # Do a sample query that gets the entities in the database.
    cur.execute("""
        select entity_type, name
        from TBL_ENTITIES;
    """)

    # Loop through the entries to sort them into hospitals and EMS's.
    etys = {
        'hospital_list': [],
        'ems_list': [],
    }
    for (entity_type, name) in cur:
        # Check which type of entity it is.
        if entity_type == 'HOSPITAL':
            # Add to hospital list.
            etys['hospital_list'].append(name)
        elif entity_type == 'EMS':
            # Add to EMS list.
            etys['ems_list'].append(name)
        else:
            # Error.
            flask.abort(400, f"Unrecognized entity type of \"{entity_type}\" for entity with name \"{name}\".")

    # Return the data as a JSON response.
    return flask.jsonify(etys)

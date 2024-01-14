##############################################################################
#   File    app.py
#   Desc    Python Flask RESTful back-end API for managing requests.
#   Author  Zachariah Preston
#   Date    2024-01-11
##############################################################################

# Import packages.
import flask
import mysql.connector as sql

# App setup.
app = flask.Flask(__name__)



##############################################################################
#   Func    root
#   Desc    Route function for whole API.
#   Params  None
#   Return  <Response>: HTTP response that contains the queried data as a
#               JSON object, or an error message if an error occured.
##############################################################################
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
        # Error.
        response_json = {
            'error': 'Server failed to connect to the SQL database.',
        }
        return flask.jsonify(response_json), 503

    # Check if the ID wasn't provided in the request.
    if 'id' not in flask.request.json:
        # Error.
        response_json = {
            'error': 'Invalid request JSON.',
        }
        return flask.jsonify(response_json), 400

    # Execute the request, and return the data as a JSON response.
    response_json = process_request(cur, flask.request.json)
    return flask.jsonify(response_json)



##############################################################################
#   Func    process_request
#   Desc    Processes a JSON request and creates a JSON response.
#   Params  <MySQLCursor> cur: Cursor of the database connection.
#           <dict> request_json: Request's JSON data.
#   Ret     <dict>: Response's JSON data.
##############################################################################
def process_request(cur, request_json):
    # Get the ID from the request.
    ent_id = request_json['id']

    # Get the data from the database, and organize the records into relationships.
    records = query(cur, ent_id)
    relationships = create_relationships(records)

    # Return the data as a JSON response.
    response_json = {
        'relationships': relationships,
    }
    return response_json




##############################################################################
#   Func    query
#   Desc    Performs an SQL query on the database using the given arguments.
#   Params  <MySQLCursor> cur: Cursor of the database connection.
#           <int> ent_id: ID of the entity.
#   Ret     <list>: List of records that include the entity.
##############################################################################
def query(cur, ent_id):
    # Get all relationships that includes this ID, as well as the info for the
    # two entities included in those relationship.
    cur.execute("""
        select SRC.id, SRC.name, SRC.entity_type, DEST.id, DEST.name,
            DEST.entity_type, REL.relationship_type,
            REL.id, REL.patient_type, REL.contact_phone, REL.instructions
        from TBL_ENTITY_RELATIONSHIPS as REL
        left join TBL_ENTITIES as SRC on (
            REL.source_entity_id = SRC.id
        )
        left join TBL_ENTITIES as DEST on (
            REL.destination_entity_id = DEST.id
        )
        where REL.source_entity_id = %s
        or REL.destination_entity_id = %s;
    """, [
        ent_id,
        ent_id,
    ])

    # Return all of the records.
    return cur.fetchall()



##############################################################################
#   Func    create_relationships
#   Desc    Organizes records from a query into a listing of relationships.
#   Params  <list> records: List of records from the query result.
#   Ret     <dict>: All of the relationships for the records.
##############################################################################
def create_relationships(records):
    # Loop through the records and create relationships from them.
    relationships = {}
    for (source_id, source_name, source_type, destination_id, \
    destination_name, destination_type, relationship_type, patient_id, \
    patient_type, contact_phone, instructions) in records:
        # Check if this relationship type isn't yet in the response.
        if relationship_type not in relationships:
            # Create the type.
            relationships[relationship_type] = []

        # Create the sub-dicts for this relationship.
        source = {
            'id': source_id,
            'name': source_name,
            'type': source_type,
        }
        destination = {
            'id': destination_id,
            'name': destination_name,
            'type': destination_type,
        }
        patient = {
            'id': patient_id,
            'type': patient_type,
            'contact_phone': contact_phone,
            'instructions': instructions,
        }

        # Loop through the relationships of the given type to check if one
        # already exists for these entities.
        is_found = False
        for rel in relationships[relationship_type]:
            # Check if it matches.
            if (rel['source']['id'] == source_id) \
            and (rel['destination']['id'] == destination_id):
                # Just add the patient type.
                rel['patient_types'].append(patient)
                is_found = True
        
        # Check if no existing relationship was found.
        if not is_found:
            # Create a new relationship.
            relationships[relationship_type].append({
                'source': source,
                'destination': destination,
                'patient_types': [
                    patient,
                ],
            })

    # Return the relationships.
    return relationships

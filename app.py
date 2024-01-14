######################################################################################################################
#   File    app.py
#   Desc    Python Flask RESTful back-end API for managing requests.
#   Author  Zachariah Preston
#   Date    2024-01-11
######################################################################################################################

# Import packages.
import flask
import mysql.connector as sql

# App setup.
app = flask.Flask(__name__)

# Database credentials.
SQL_HOST = 'localhost'
SQL_USER = 'root'
SQL_PASSWORD = 'password'
SQL_DATABASE = 'main'



######################################################################################################################
#   Func    root
#   Desc    Route function for whole API.
#   Params  None
#   Return  <Response>: HTTP response that contains the queried data as a JSON object, or an error message if an
#               error occured.
######################################################################################################################
@app.route('/', methods=['GET'])
def root():
    # Test that the database is accessible.
    try:
        # Connect to the MySQL database.
        conn = sql.connect(
            host=SQL_HOST,
            user=SQL_USER,
            password=SQL_PASSWORD,
            database=SQL_DATABASE,
        )
        cur = conn.cursor()
    except sql.errors.DatabaseError:
        # Error.
        response_json = {
            'error': 'Server failed to connect to the SQL database.',
        }
        return flask.jsonify(response_json), 503

    # Check if the ID wasn't provided in the request.
    if ('id' not in flask.request.json) or not isinstance(flask.request.json['id'], int):
        # Error.
        response_json = {
            'error': 'Invalid request JSON.',
        }
        return flask.jsonify(response_json), 400

    # Execute the request, and return the data as a JSON response.
    response_json = process_request(cur, flask.request.json)
    return flask.jsonify(response_json)



######################################################################################################################
#   Func    process_request
#   Desc    Processes a JSON request and creates a JSON response.
#   Params  <MySQLCursor> cur: Cursor of the database connection.
#           <dict> request_json: Request's JSON data.
#   Ret     <dict>: Response's JSON data.
######################################################################################################################
def process_request(cur, request_json):
    # Get the arguments from the request.
    ent_id = request_json['id']
    relationship_types = (request_json['relationship_types'] if 'relationship_types' in request_json else None)
    entity_types = (request_json['entity_types'] if 'entity_types' in request_json else None)
    associativity = (request_json['associativity'] if 'associativity' in request_json else None)

    # Get the data from the database, and organize the records into relationships.
    records = query(cur, ent_id, relationship_types, entity_types, associativity)
    relationships = create_relationships(records)

    # Return the data as a JSON response.
    response_json = {
        'relationships': relationships,
    }
    return response_json




######################################################################################################################
#   Func    query
#   Desc    Performs an SQL query on the database using the given arguments.
#   Params  <MySQLCursor> cur: Cursor of the database connection.
#           <int> ent_id: ID of the entity.
#           optional <list> relationship_types: List of valid relationship types to filter by.
#           optional <list> entity_types: List of valid entity types (for the other entity in the relationship) to
#               filter by.
#           optional <str> associativity: Can be either 'source' to only allow relationships where the subject entity
#               is the source or can be 'destination' to only allow relationships where the subject entity is the
#               destination.
#   Ret     <list>: List of records that include the entity and match the filters.
######################################################################################################################
def query(cur, ent_id, relationship_types=None, entity_types=None, associativity=None):
    # Start with a query that gets all of the necessary fields.
    query = """
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
        where true
    """
    query_args = []

    # Check if relationship types were provided.
    if isinstance(relationship_types, list):
        # Add to the query filters.
        query += ' and REL.relationship_type in ('
        for rt in relationship_types:
            if isinstance(rt, str):
                query += '%s, '
                query_args.append(rt)

        # Remove the trailing comma and add the closing parenthesis.
        query = query[:-2] + ')'

    # Check if associativity was provided.
    if isinstance(associativity, str) and (associativity == 'source'):
        # Only allow source.
        query += ' and REL.source_entity_id = %s'
        query_args.append(ent_id)
    elif isinstance(associativity, str) and (associativity == 'destination'):
        # Only allow destination.
        query += ' and REL.destination_entity_id = %s'
        query_args.append(ent_id)
    else:
        # Allow either.
        query += """ and (
            REL.source_entity_id = %s
            or REL.destination_entity_id = %s
        )"""
        query_args.append(ent_id)
        query_args.append(ent_id)

    # Add ending semicolon.
    query += ';'

    # Execute the query.
    cur.execute(query, query_args)

    # Return all of the records.
    return cur.fetchall()



######################################################################################################################
#   Func    create_relationships
#   Desc    Organizes records from a query into a listing of relationships.
#   Params  <list> records: List of records from the query result.
#   Ret     <dict>: All of the relationships for the records.
######################################################################################################################
def create_relationships(records):
    # Loop through the records and create relationships from them.
    relationships = {}
    for (source_id, source_name, source_type, destination_id, destination_name, destination_type, relationship_type, \
    patient_id, patient_type, contact_phone, instructions) in records:
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

        # Loop through the relationships of the given type to check if one already exists for these entities.
        is_found = False
        for rel in relationships[relationship_type]:
            # Check if it matches.
            if (rel['source']['id'] == source_id) and (rel['destination']['id'] == destination_id):
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

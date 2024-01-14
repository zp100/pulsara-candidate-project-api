# pulsara-candidate-project-api

Back-end candidate project for Pulsara's "Full Stack Software Engineer" position.

### Design Assumptions

-   For simplicity, the API is fully public with no sign-in or API key required.
-   It's only designed for the provided database, so the host/username/password for it are hard-coded.
-   As an API, no UI is provided and the query options must be included in the HTTP requests.

## Setup

### Requirements

-   Access to the Docker image
-   Python 3.10 or later
-   `pip` and `git`

### Download

Clone this GitHub repository:
```
git clone https://github.com/zp100/pulsara-candidate-project-api.git
cd pulsara-candidate-project-api
```

### Docker and MySQL

Install the Docker image, then run it as a container. This will host the MySQL database locally on port 3306. The database can be connected to via the Docker container's shell:
```
mysql --host=localhost --user=root --password=password main
```
You can now directly query the `main` database. For example, to list all tables in the database:
```
mysql> show tables;
+--------------------------+
| Tables_in_main           |
+--------------------------+
| TBL_ENTITIES             |
| TBL_ENTITY_RELATIONSHIPS |
+--------------------------+
2 rows in set (0.01 sec)

```

### Python

Install the required Python package dependencies for this project. If you want to avoid installing these packages globally, first create a virtual environment:
```
python3 -m venv .env
source .env/bin/activate
```
Whether the Python virtual environment is created or not, next install the dependencies:
```
pip install -r requirements.txt
```
You can go back to global-only packages by deactivating the virtual environment:
```
source .env/bin/deactivate
```
It will also be deactivated when you close the terminal.

## Usage

### Running

If you created a Python virtual environment, first make sure that it's active:
```
source .env/bin/activate
```
Then you can run the API by hosting a local Flask server:
```
flask run
```

### Testing

The server expects a JSON GET request, so it can't be accessed through normal means such as a browser. To get data from the server, the files "test_client.py" and "request.json" have been included. The "request.json" file includes the parameters for the API query, and the "test_client.py" will execute that query. So to get the data from the API, first make sure that the MySQL database and Flask server are both running, then open another terminal and run the client:
```
python3 test_client.py
```
Then if no errors have occured, a file named "response.json" will be created with the data from the server. For example, if the request was for the entity with ID 1:
```
{
    "id": 1,
    "associativity": "source"
}
```
Then the response will have an organized collection of all relationships for that entity:
```
{
    "relationships": {
        "TRANSFER": [
            {
                "destination": {
                    "id": 2,
                    "name": "Hospital - Metro Central",
                    "type": "HOSPITAL"
                },
                "patient_types": [
                    {
                        "contact_phone": "555-555-5555xtf1-2-1",
                        "id": 46,
                        "instructions": "Wait for Pulsara call for confirmation after request",
                        "type": "STEMI"
                    },
                    {
                        "contact_phone": "555-555-5555xtf1-2-2",
                        "id": 47,
                        "instructions": "Wait for Pulsara call for confirmation after request",
                        "type": "STROKE"
                    },
                    {
                        "contact_phone": "555-555-5555xtf1-2-3",
                        "id": 48,
                        "instructions": "a",
                        "type": "GENERAL"
                    }
                ],
                "source": {
                    "id": 1,
                    "name": "Hospital - Rural West",
                    "type": "HOSPITAL"
                }
            }
        ]
    }
}
```

### Request Syntax

The server supports the following parameters from the "request.json" file:
-   `"id"`: Required integer. Gets relationships for this ID's entity.
-   `"relationship_types"`: List of strings. If provided, only gets relationships of this type.
-   `"associativity"`: Either `"source"` or `"destination"`. If it's `"source"`, only gets relationships where the ID's entity is the source. If it's `"destination"`, only gets relationships where the ID's entity is the destination.

Filters that are improperly formatted will be ignored.
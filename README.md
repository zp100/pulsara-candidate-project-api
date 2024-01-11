# pulsara-candidate-project-api
Back-end canditate project for Pulsara's "Full Stack Software Engineer" position.

## Setup

### Requirements
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

### Running
Once the installations are complete, you can run the program by hosting a local server:
```
flask run
```
Then you can access the project at http://127.0.0.1:5000, such as with a browser.

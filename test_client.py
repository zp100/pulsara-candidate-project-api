##############################################################################
#   File:   test_client.py
#   Desc:   Client that accesses the API, for testing purposes.
#   Author: Zachariah Preston
#   Date:   2024-01-13
##############################################################################

# Import packages.
import json
import requests



##############################################################################
#   Func:   main
#   Desc:   Main function. Requests data from the API.
#   Params: None
#   Ret:    None
##############################################################################
def main():
    # Open the request store file.
    with open('request.json', 'r') as file:
        # Load the request JSON object.
        request_json = json.load(file)

    # Get the data from the API.
    response = requests.get('http://127.0.0.1:5000', json=request_json)

    # Check if the request was successful.
    code = response.status_code
    data = response.json()
    if code == 200:
        # Open the response store file.
        with open('response.json', 'w') as file:
            # Store the response JSON data.
            json.dump(data, file, indent=4)
    else:
        # Error.
        error_message = data['error']
        raise Exception(f"[HTTP {code}] {error_message}")



# Boilerplate.
if __name__ == '__main__':
    main()

# README

## How to run the app

- Clone the repository
- Generate a virtual env `python3 -m venv venv` (https://docs.python.org/3/library/venv.html)
- Start the virtual environment `source venv/bin/activate`
- and run `pip install -r requirements.txt`

Once requirements are installed then proceed to run the following:

- `python manage.py makemigrations`
- `python manage.py migrate`
- `python manage.py create_test_data 100`
    - Creates a test user with a token you can use to query the api
    - You can use the email from this test user as well as password “password” on the login/logout endpoints
    - You can use this token in your rest client to test endpoints (postman, insomnia etc)
- `python manage.py runserver`

## How to view API docs
- Make a note of the token from the step above
- navigate to [http://localhost:8000/docs/](http://localhost:8000/docs/)
- Click on Authorize
- Copy and paste your token into the field as "Token --value-of-token--"
- Click authorize
- You are now ready to use the API

## Setting up your local environment

vscode

- Linting and formatting (black and isort)
    - [https://cereblanco.medium.com/setup-black-and-isort-in-vscode-514804590bf9](https://cereblanco.medium.com/setup-black-and-isort-in-vscode-514804590bf9)

Another IDE

…

## Tests

- Tests can be found under tests/
    - There are tests for the following
    - creating addresses
    - retrieving addresses
    - updating addresses
    - deleting addresses
- Tests can be run using the following command

```jsx
pytest tests/<name_of_app>/<test_file_name>.py OR pytest
```

## Assumptions

- Running the create_test_data script was to created from the POV of a user registering/existing and receiving a token - please use this to get started
- That when a user wants to delete an address, that they enter an “edit” mode where they can select multiple addresses at once (if they wanted to) and delete them.
- That if we want to query for many thousands of addresses, then fetching them should be paginated
- That we’re using something like google address validation/autocomplete on the frontend
- That an address cannot be added if its missing inputs
- Addresses with the same address line one and zip code cannot exist, they must be unique
- I named the django migration relavant to addressbook rather than auto generating it
- One assumption I made on authentication was that a user already exists with an email and a password, and that at this point we're generating a token for them to use this API. I could have made a separate endpoint for registering a user but was not sure if it was part of the bonus tasks.
- That tokens need to expire after a day and are regenerated on reauth
- I've used SQLLite for the exercise, but would consider using postgresql if this was a production env

## Questions

- Is it incorrect to rely on the frontend here to validate the address? I was thinking that google address validation might be used for example, but how reliable is it? My implementation I think leans towards the naïve side, but I would like to chat more about this as Im not 100% sure!
- Whats the flexibility on deleting addresses? are there constraints on whether or not its allowed based on certain circumstances?
- Is there a strong preference between DRF’s token implementation and a JWT? Curiosity question from my POV

## Things I didn’t get time to finish/would do If I had more time

- Adding test coverage for the bonus task of authenticating and logging out. I exposed endpoints on the service that could handle authenticating (assuming a user had signed up prior - I wasn’t sure about adding this as it was not too clear in the spec so my assumption was that it existed)
    - I did not have time to add test coverage for this, but I did explain what kind of things I’d test for under `tests/authentication/test_authentication.py`
    - I considered token expiration
    - I struggled to get API docs generated properly for authentication. So I have added it here
    
    ## Login
    
    [`http://localhost:8000/authentication/login/`](http://localhost:8000/authentication/login/)
    
    Payload
    
    ```jsx
    {
    	"email": "email@email.com",
    	"password": "password"
    }
    ```
    
    Response
    
    201 - User signed in, token created, returns a token payload
    
    404 - a user that does not exist attempts auth
    
    400 - Invalid credentials used to authenticate
    
    ## Logout
    
    [`http://localhost:8000/authentication/logout/`](http://localhost:8000/authentication/login/)
    
    Response
    
    200 - User is signed out
    
- I didn’t get time to add filtering for addresses
- Validation for cities. Im not sure if its required but I would have liked to have added it if I had more time
- Validation on zip codes (post codes). I would have liked to have added it if I had more time
- Dockerising this service to make onboarding consistent for current and future developers / streamlining development
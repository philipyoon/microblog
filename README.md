# Microblog 

Followed [Miguel Grinberg's Blog](https://blog.miguelgrinberg.com/index) to create a Microblog, where users share short posts (think Twitter) and can follow other users.

[**Link to Microblog website**](https://philips-microblog.herokuapp.com/)

- Deployed with Heroku cloud service
- App structured with modular approach using flask blueprints and templates
- Database using PostgreSQL and SQLAlchemy object relation mapper
  - Using Werkzeug python library for secure password storage using salted hashes
  - Database migration support with Alembic 
- Full-text search implemented with Elasticsearch, using service provider Searchbox
- Front end was done with basic HTML templates and CSS framework Bootstrap
- Secure email password reset using JSON web tokens 

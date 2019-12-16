### To run:

Change line 23 in app.py to wherever you checked the code out.
Make sure pandas and sqlite3 modules are installed as well.

This python flask app is used to manage a sqlite3 database and present to the user books they have searched for and saved.  It also has the ability to delete a saved book.

The app will create a database if it doesn't exist.
It will check to see if a user exists and if it's password is correct.
If the user does not exist it will create it.

When adding books it will use a unique constraint on
The user, the book title, and the book author in order to avoid duplicates.

Where practical exceptions are caught and logic/usage errors are returned to the user.

Some css files are used to styling, however styling is not my strongest skill.

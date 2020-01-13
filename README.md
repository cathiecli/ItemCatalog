## Project: Item Catalog

This project is to develop a web application that provides a list of Items
within a variety of categories and integrate third party user registration
and authentication.  Authenticated users should have the ability to post,
edit and delete their own items.

### Description

The following files are for database related tasks:
***ic_database_setup.py***: python file for setting up tables, once it is being run, itemcategory.db will be generated
***ic_database_insert.py***: python file for inserting data into tables
***ic_database_select.py***: python file for viewing tables data
***ic_database_delete.py***: python file for deleting tables data

Image files, CSS files, etc. are saved in ***static*** directory
Web HTML files are saved in ***templates*** directory

Third-party Authentication and Authorization OAuth 2.0 JSON configuration files
***client_secrets.json***: for Google sign in
***fb_client_secrets.json***: for Facebook sign in

Notes:
  1. If change(s) made on 3rd party application configuration, such as Google or Facebook,
  a new JSON file version needs to be generated and stored in the same location and with
  the same file name
  2. One business rule is users can only Edit/Delete the category/item he/she created by
  himself/herself

***application.py***: main application program file
***README.md***: project README file

### Getting Started
##### Dependencies

This project depends on correctly installing **vagrant** Linux-based virtual machine (VM)


##### Executing and Testing Application

   To execute the program, please follow these steps:
   1. Navigate to */vagrant* directory where the program files are stored
   2. Bring up VM by typing `vagrant up`
   3. Type `vagrant ssh` to open Ubuntu vm
   4. Navigate to project directory by `cd /vagrant/catalog` and run
   `vagrant@vagrant:/vagrant/catalog$ python application.py`

   To check Python code against the PEP 8 style conventions, please run:
   `vagrant@vagrant:/vagrant/catalog$ pycodestyle --first application.py`

   5. Access and test application by visiting http://localhost:8000/login locally

### Authors

 Cong Li

### Version History

0.1 - Initial Release on 01-02-2020

### License

This project is licensed under the cl9451

### Acknowledgments

Inspiration, code snippets, etc.
    [Google Developer APIs & Services](https://console.developers.google.com/apis)
    [facebook for developers](https://developers.facebook.com/apps)

# Molecule-Parser

This full-stack program was created for the course, CIS-2750 (Software Systems Development & Integration), taught by Professor Stefan Kremer at the University of Guelph in the Winter 2023 semester.

This program simulates a molecule parser that allows users to upload and view chemical spatial data files (.sdf files). The program also allows users to modify atom features in the display such as colour, gradient, and radius size. This program is hosted through a python webserver and can be used through browsers.

### Compilation Commands

1. Clone/download this repository on your local computer
2. Open a terminal window in your cloned repository.
3. Run ```make```. This should generate ```molecule_wrap.c``` and ```molecule.py``` files, along with some .o (object) and .so (library) files.
4. To locate .so libraries in your computer, run ```export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:.```
5. Run ```python3 server.py 8080```
6. In a browser of choice (i.e., Chrome, Safari, Firefox, etc), run ```http://localhost:8080```
7. To exit program in terminal, run ```ctrl + c```

Please note, you may need to modify the python library pathways inside the makefile to compile the program. You may also need to change the python version in step 5 to match the version installed on your computer. You may also change the port number as desired.

### Project components

* mol.h - A header file for mol.c file
* mol.c - A C function library that allows basic molecule manipulation
* makefile - A file with set of rules for quick program compilation 
* molecule.i - A file containing the preproccessed C source code (including headers)
* MolDisplay.py - A Python library that generates SVG images of molecules for display
* server.py - A python webserver to allow sdf file uploading/viewing
* molsql.py - A file Python library that creates a SQLite database and supports database operations for this project
* index.html - A basic HTML webpage for the program
* style.css - A CSS file to add some basic stylistic features to the webpage
* index.js - A series of AJAX action listeners that communicate with the Python webserver to perform various tasks
* sdf-files directory - contains valid sdf files samples for testing purposes

### Video Demonstration


### Future Improvements
In the future, it would be nice to add security features to the webserver such as data encryption and user authentication to maintain user privacy and prevent the program from being exploited.

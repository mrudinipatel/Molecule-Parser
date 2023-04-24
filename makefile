CC = clang
CFLAGS = -Wall -pedantic -std=c99
INCLUDE = Library/Frameworks/Python.framework/Versions/3.9/include/python3.9 
LIB = /Library/Frameworks/Python.framework/Versions/3.9/lib

all: libmol.so _molecule.so

libmol.so: mol.o
	$(CC) -shared -o libmol.so mol.o

mol.o: mol.c mol.h
	$(CC) -c -fPIC $(CFLAGS) mol.c -o mol.o

_molecule.so: molecule_wrap.o libmol.so
	$(CC) molecule_wrap.o -shared -o _molecule.so libmol.so -L$(LIB) -lpython3.9 -lm -dynamiclib

molecule_wrap.o: molecule_wrap.c
	$(CC) -c -fPIC $(CFLAGS) molecule_wrap.c -I/$(INCLUDE) -o molecule_wrap.o

molecule_wrap.c molecule.py: molecule.i
	swig -python molecule.i

main: clean all
	$(CC) $(CFLAGS) -L. main.c -o main -lmol -lm 

clean:
	rm -rf *.o *.so main

# -------- FOR SCHOOL SERVERS USE THIS MAKEFILE: --------

# CC = clang
# CFLAGS = -Wall -pedantic -std=c99
# INCLUDE = usr/include/python3.7m
# LIB = /usr/lib/python3.7/config-3.7m-x86_64-linux-gnu

# all: libmol.so _molecule.so

# libmol.so: mol.o
# 	$(CC) -shared -o libmol.so mol.o

# mol.o: mol.c mol.h
# 	$(CC) -c -fPIC $(CFLAGS) mol.c -o mol.o

# _molecule.so: molecule_wrap.o libmol.so
# 	$(CC) molecule_wrap.o -shared -o _molecule.so libmol.so -L$(LIB) -lpython3.7 -lm

# molecule_wrap.o: molecule_wrap.c
# 	$(CC) -c -fPIC $(CFLAGS) molecule_wrap.c -I/$(INCLUDE) -o molecule_wrap.o

# molecule_wrap.c molecule.py: molecule.i
# 	swig3.0 -python molecule.i

# main: clean all
# 	$(CC) $(CFLAGS) -L. main.c -o main -lmol -lm

# clean:
# 	rm -rf *.o *.so main

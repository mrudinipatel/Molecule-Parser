#include <stdio.h>
#include <stdlib.h>
#include <string.h> 
#include <math.h>
#include "mol.h"

#ifndef M_PI 
#define M_PI 3.14159265358979
#endif

void atomset (atom *atom, char element[3], double *x, double *y, double *z){
    /*
     * This function checks if the element value is empty, if so it prints an error message
     * and exits the program (since this is a void function). I then set the atom structure's
     * attributes as instructed. Please note, it is crucial to use strcpy here.
    */

    if (strcmp(element, "") == 0){
        printf("This element string is empty, please run again to enter a valid input.\n");
        exit(0);
    }

    atom->x = *x;
    atom->y = *y;
    atom->z = *z;
    strcpy(atom->element, element);
}

void atomget (atom *atom, char element[3], double *x, double *y, double *z){
    /*
     * In this function, I am retrieving the atom structure's attributes as instructed.
     * Again, it is important to use strcpy here (otherwise program may break in append 
     * functions).
    */

    *x = atom->x;
    *y = atom->y;
    *z = atom->z;
    strcpy(element, atom->element);
}

void bondset (bond *bond, unsigned short *a1, unsigned short *a2, atom**atoms, unsigned char *epairs){
    /*
     * In this function, I am setting the bond structure's attributes as instructed
     * (updated for A2).
    */

    bond->a1 = *a1;
    bond->a2 = *a2;
    bond->atoms = *atoms;
    bond->epairs = *epairs;

    compute_coords(bond);
}

void bondget (bond *bond, unsigned short *a1, unsigned short *a2, atom**atoms, unsigned char *epairs){
    /*
     * In this function, I am retrieving the bond structure's attributes as instructed
     * (updated for A2).
    */

    *a1 = bond->a1;
    *a2 = bond->a2;
    *atoms = bond->atoms;
    *epairs = bond->epairs;
}


void compute_coords (bond *bond){
    /*
     * This function calculates all the 'double' values inside of the
     * the bond structure.
    */
    bond->x1 = bond->atoms[bond->a1].x;
    bond->y1 = bond->atoms[bond->a1].y;

    bond->x2 = bond->atoms[bond->a2].x;
    bond->y2 = bond->atoms[bond->a2].y;

    double average = 0;
    average = ((bond->atoms[bond->a1].z) + (bond->atoms[bond->a2].z)) / 2;
    bond->z = average;

    double distance = 0;
    distance = sqrt(pow((bond->x2 - bond->x1), 2) + pow((bond->y2 - bond->y1), 2));
    bond->len = distance;

    bond->dx = (bond->x2 - bond->x1) / bond->len;
    bond->dy = (bond->y2 - bond->y1) / bond->len;
}


molecule * molmalloc (unsigned short atom_max, unsigned short bond_max){
    /*
     * This function allocates appropriate memory for the atoms, atom_ptrs, bonds, and bond_ptrs
     * arrays inside the molecule structure and intitializes the other attributes as instructed.
     * This function also checks is each malloc statement returns NULL. If so, it frees 
     * previously allocated memoryusing molfree and returns NULL to the main function as a
     * form of error handling.
    */
    molecule * mol = malloc(sizeof(molecule));

    if (mol == NULL){
        return NULL;
    }

    mol->atom_max = atom_max;
    mol->atom_no = 0;
    mol->atoms = malloc(sizeof(atom) * atom_max);

    if (mol->atoms == NULL){
        molfree(mol);
        return NULL;
    }

    mol->atom_ptrs = malloc(sizeof(atom*) * atom_max);

    if (mol->atom_ptrs == NULL){
        molfree(mol);
        return NULL;
    }
    
    mol->bond_max = bond_max;
    mol->bond_no = 0;
    mol->bonds = malloc(sizeof(bond) * bond_max);

    if (mol->bonds == NULL){
        molfree(mol);

        return NULL;
    }

    mol->bond_ptrs = malloc(sizeof(bond*) * bond_max);

    if (mol->bond_ptrs == NULL){
        molfree(mol);
        return NULL;
    }

    return mol;
}

molecule * molcopy (molecule *src){
    /*
     * This function copies the molecule into a newly allocated molecule (using molmalloc).
     * After successfully copying the molecule, I append both, the atoms and bonds, of the 
     * molecule to the new molecule. 
    */
    molecule * mole = molmalloc(src->atom_max, src->bond_max);

    if (mole == NULL){
        return NULL;
    }
    
    mole->atom_max = src->atom_max;
    mole->bond_max = src->bond_max;

    for (int i = 0; i < src->atom_no; i++){
        molappend_atom(mole, &src->atoms[i]);
    }

    for (int j = 0; j < src->bond_no; j++){
        molappend_bond(mole, &src->bonds[j]);
    }

    return mole;
}

void molfree (molecule *ptr){
    /*
     * This function frees all allocated arrays inside the molecule structure
     * including the pointer itself.
    */
    if (ptr == NULL){
        return;
    }
    
    free(ptr->atoms);
    free(ptr->atom_ptrs);
    free(ptr->bonds);
    free(ptr->bond_ptrs);
    free(ptr);
}

void molappend_atom (molecule *molecule, atom *atom){
    /*
     * This function navigates through all possible 'appending cases':
     * 1) If atom_max is 0, it increments the atom_max value and reallocates memory to the atom
     *    arrays inside the structure.
     * 2) If atom_max is equal to atom_no, it doubles the atom_max value and reallocates memory
     *    to the atom arrays inside the structure. 
     * As the default case, it appends to the "atom_no'th" index inside the atoms 
     * array and sets the address of the atom_ptrs array to the newly appended atoms
     * index before incrementing atom_no.
     * Please Note: after reallocing, I have manually reset the addresses inside the 
     * atom_ptrs array to avoid the addresses from being overwritten. Also, after each
     * realloc I have decided to check for NULL returns as a form of error handling. 
     * Instead of returning, I print an error message to stderr and exit the program
     * (since this a void function, I could not return NULL).
    */

    if(molecule->atom_max == 0){
        (molecule->atom_max)++;

        molecule->atoms = realloc(molecule->atoms, sizeof(struct atom));
        molecule->atom_ptrs = realloc(molecule->atom_ptrs, sizeof(struct atom*));

        if (molecule->atoms == NULL || molecule->atom_ptrs == NULL){
            fprintf(stderr, "The realloc has failed. Please try again.\n");
            exit(0);
        }

        for (int i = 0; i < molecule->atom_no; i++){
            molecule->atom_ptrs[i] = (molecule->atoms+i);
        }
    }
    else if (molecule->atom_no == molecule->atom_max){
        molecule->atom_max = molecule->atom_max * 2;

        molecule->atoms = realloc(molecule->atoms, sizeof(struct atom) * molecule->atom_max);
        molecule->atom_ptrs = realloc(molecule->atom_ptrs, sizeof(struct atom*) * molecule->atom_max);

        if (molecule->atoms == NULL || molecule->atom_ptrs == NULL){
            fprintf(stderr, "The realloc has failed. Please try again.\n");
            exit(0);
        }

        for (int i = 0; i < molecule->atom_no; i++){
            molecule->atom_ptrs[i] = (molecule->atoms+i);
        }
    }

    molecule->atoms[molecule->atom_no].x = atom->x;
    molecule->atoms[molecule->atom_no].y = atom->y;
    molecule->atoms[molecule->atom_no].z = atom->z;
    strcpy(molecule->atoms[molecule->atom_no].element, atom->element);
    
    molecule->atom_ptrs[molecule->atom_no] = &(molecule->atoms[molecule->atom_no]);

    (molecule->atom_no)++;
}

void molappend_bond (molecule *molecule, bond *bond){
    /*
     * This function logic is the same as that of molappend_atom(), just with bonds.
     * I also use bondset to append the 'epairs' attribute instead of strcpy as done in 
     * molappend_atom(). Modified for A2.
    */

    if(molecule->bond_max == 0){
        (molecule->bond_max)++;

        molecule->bonds = realloc(molecule->bonds, sizeof(struct bond));
        molecule->bond_ptrs = realloc(molecule->bond_ptrs, sizeof(struct bond*));

        if (molecule->bonds == NULL || molecule->bond_ptrs == NULL){
            fprintf(stderr, "The realloc has failed. Please try again.\n");
            exit(0);
        }

        for (int i = 0; i < molecule->bond_no; i++){
            molecule->bond_ptrs[i] = (molecule->bonds+i);
        }
    }
    else if (molecule->bond_no == molecule->bond_max){
        molecule->bond_max = molecule->bond_max * 2;

        molecule->bonds = realloc(molecule->bonds, sizeof(struct bond) * molecule->bond_max);
        molecule->bond_ptrs = realloc(molecule->bond_ptrs, sizeof(struct bond*) * molecule->bond_max);
        
        if (molecule->bonds == NULL || molecule->bond_ptrs == NULL){
            fprintf(stderr, "The realloc has failed. Please try again.\n");
            exit(0);
        }

        for (int i = 0; i < molecule->bond_no; i++){
            molecule->bond_ptrs[i] = (molecule->bonds+i);
        }
    }

    molecule->bonds[molecule->bond_no].a1 = bond->a1;
    molecule->bonds[molecule->bond_no].a2 = bond->a2;
    //bondset(&(molecule->bonds[molecule->bond_no]), bond->a1, bond->a2, bond->epairs);
    bondset(&(molecule->bonds[molecule->bond_no]), &bond->a1, &bond->a2, &bond->atoms, &bond->epairs);
    
    molecule->bond_ptrs[molecule->bond_no] = &(molecule->bonds[molecule->bond_no]);

    (molecule->bond_no)++;
}



int compareAtoms(const void *a, const void *b){  
    /*
     * In this function, I dereference the const void pointers being passed in and 
     * compare the z values of each atom, returning appropriate integer values for 
     * each case -- as specified in documentation/lecture (slides).
    */  
    const atom * a1 = *(const atom**)a;
    const atom * a2 = *(const atom**)b;

    if (a1->z < a2->z){
        return -1;
    }
    else if (a1->z > a2->z){
        return 1;
    }

    return 0;
}

int bond_comp (const void *a, const void *b){
    // Modified bond compare function from A1 for A2

    const bond * b1 = *(const bond**)a;
    const bond * b2 = *(const bond**)b;

    double avg1 = b1->z;
    double avg2 = b2->z;

    if (avg1 < avg2){
        return -1;
    }
    else if (avg1 > avg2){
        return 1;
    }

    return 0;
}

void molsort (molecule *molecule){
    /*
     * In this function I am sorting the atom_ptrs and bond_ptrs arrays using
     * C's built-in qsort() function. I make calls to two separate compare functions (see above).
    */
    qsort(molecule->atom_ptrs, molecule->atom_no, sizeof(atom*), compareAtoms);

    qsort(molecule->bond_ptrs, molecule->bond_no, sizeof(bond*), bond_comp);
}



void xrotation (xform_matrix xform_matrix, unsigned short deg){
    /*
     * This function I am setting the matrix indexes to specific values
     * (based on wikipedia's matrix x axis rotation formulas - mentioned in lectures as well).
     * Before I do this, I am converting the passed in degree value to radians, using the
     * M_PI value from the <math.h> C library.
    */

    double radians = (deg * M_PI) / 180.0;

    xform_matrix[0][0] = 1;
    xform_matrix[0][1] = 0;
    xform_matrix[0][2] = 0;
    
    xform_matrix[1][0] = 0;
    xform_matrix[1][1] = cos(radians);
    xform_matrix[1][2] = -sin(radians);
    
    xform_matrix[2][0] = 0;
    xform_matrix[2][1] = sin(radians);
    xform_matrix[2][2] = cos(radians);
}

void yrotation (xform_matrix xform_matrix, unsigned short deg){
    /*
     * This function I am setting the matrix indexes to specific values
     * (based on wikipedia's matrix y axis rotation formulas - mentioned in lectures as well).
     * Before I do this, I am converting the passed in degree value to radians, using the
     * M_PI value from the <math.h> C library.
    */

    double radians = (deg * M_PI) / 180.0;

    xform_matrix[0][0] = cos(radians);
    xform_matrix[0][1] = 0;
    xform_matrix[0][2] = sin(radians);
    
    xform_matrix[1][0] = 0;
    xform_matrix[1][1] = 1;
    xform_matrix[1][2] = 0;
    
    xform_matrix[2][0] = -sin(radians);
    xform_matrix[2][1] = 0;
    xform_matrix[2][2] = cos(radians);
}

void zrotation (xform_matrix xform_matrix, unsigned short deg){
    /*
     * This function I am setting the matrix indexes to specific values
     * (based on wikipedia's matrix z axis rotation formulas - mentioned in lectures as well).
     * Before I do this, I am converting the passed in degree value to radians, using the
     * M_PI value from the <math.h> C library.
    */

    double radians = (deg * M_PI) / 180.0;

    xform_matrix[0][0] = cos(radians);
    xform_matrix[0][1] = -sin(radians);
    xform_matrix[0][2] = 0;
    
    xform_matrix[1][0] = sin(radians);
    xform_matrix[1][1] = cos(radians);
    xform_matrix[1][2] = 0;
    
    xform_matrix[2][0] = 0;
    xform_matrix[2][1] = 0;
    xform_matrix[2][2] = 1;
}

void mol_xform (molecule *molecule, xform_matrix matrix){
    /*
     * In this function, I am performing a matrix multiplication using the 3x3 matrix
     * and the x, y, z values inside each atom. I do this inside a loop where I also 
     * declare temp variables to store the current x, y, z values to avoid overriding
     * during the transformation. Added 2nd loop for A2.
    */

    for (int i = 0; i < molecule->atom_no; i++){
        double xTemp = molecule->atoms[i].x;
        double yTemp = molecule->atoms[i].y;
        double zTemp = molecule->atoms[i].z;

        molecule->atoms[i].x = (matrix[0][0] * xTemp) + (matrix[0][1] * yTemp) + (matrix[0][2] * zTemp);
        molecule->atoms[i].y = (matrix[1][0] * xTemp) + (matrix[1][1] * yTemp) + (matrix[1][2] * zTemp);
        molecule->atoms[i].z = (matrix[2][0] * xTemp) + (matrix[2][1] * yTemp) + (matrix[2][2] * zTemp);
    }

    for (int j = 0; j < molecule->bond_no; j++){
        compute_coords(&molecule->bonds[j]);
    }
}





import sqlite3
import os
import MolDisplay

class Database:
    def __init__(self, reset=False):
       # Default case creates molecule database, but if reset is true then it
       # deletes the existing database before creating a new one
       file = 'molecules.db'
       exists = os.path.exists(file)
       
       if reset and exists:
            os.remove(file)

       self.conn = sqlite3.connect(file)
       self.cursor = self.conn.cursor()

    def create_tables(self):
        # This method creates the 6 required tables using SQLite commands
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS Elements (
                ELEMENT_NO INTEGER NOT NULL,
                ELEMENT_CODE VARCHAR(3) PRIMARY KEY NOT NULL,
                ELEMENT_NAME VARCHAR(32) NOT NULL,
                COLOUR1 CHAR(6) NOT NULL,
                COLOUR2 CHAR(6) NOT NULL,
                COLOUR3 CHAR(6) NOT NULL,
                RADIUS DECIMAL(3) NOT NULL
            )
        """)

        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS Atoms (
                ATOM_ID INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
                ELEMENT_CODE VARCHAR(3) NOT NULL,
                X DECIMAL(7,4) NOT NULL,
                Y DECIMAL(7,4) NOT NULL,
                Z DECIMAL(7,4) NOT NULL,
                FOREIGN KEY (ELEMENT_CODE) REFERENCES Elements(ELEMENT_CODE)
            )
        """)

        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS Bonds (
                BOND_ID INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
                A1 INTEGER NOT NULL,
                A2 INTEGER NOT NULL,
                EPAIRS INTEGER NOT NULL
            )
        """)

        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS Molecules (
                MOLECULE_ID INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
                NAME TEXT UNIQUE NOT NULL
            )
        """)

        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS MoleculeAtom (
                MOLECULE_ID INTEGER NOT NULL,
                ATOM_ID INTEGER NOT NULL,
                FOREIGN KEY (MOLECULE_ID) REFERENCES Molecules(MOLECULE_ID),
                FOREIGN KEY (ATOM_ID) REFERENCES Atoms(ATOM_ID),
                PRIMARY KEY (MOLECULE_ID, ATOM_ID)
            )
        """)

        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS MoleculeBond (
                MOLECULE_ID INTEGER NOT NULL,
                BOND_ID INTEGER NOT NULL,
                FOREIGN KEY (MOLECULE_ID) REFERENCES Molecules(MOLECULE_ID),
                FOREIGN KEY (BOND_ID) REFERENCES Bonds(BOND_ID),
                PRIMARY KEY (MOLECULE_ID, BOND_ID)
            )
        """)

    def __setitem__(self, table, values):
        # Sets tuple value(s) inside the appropriate table
        query = f"INSERT INTO {table} VALUES {values}"

        self.cursor.execute(query)
        self.conn.commit()

    def add_atom(self, molname, atom):
        # This method adds atom entries to the Atoms/MoleculeAtom tables
        # by linking the atom_id value from the Atoms table.
        values = (atom.element, atom.x, atom.y, atom.z)
        table = 'Atoms'
        query = f"INSERT INTO {table} (ELEMENT_CODE, X, Y, Z) VALUES {values}"
        
        self.cursor.execute(query)
        atom_id = self.cursor.lastrowid
        
        lookup = f"SELECT MOLECULE_ID FROM Molecules WHERE NAME = '{molname}'"
        molecule_id = self.conn.execute(lookup).fetchone()[0]

        table2 = 'MoleculeAtom'
        values2 = (molecule_id, atom_id)
        query2 = f"INSERT INTO {table2} (MOLECULE_ID, ATOM_ID) VALUES {values2}"
        self.cursor.execute(query2)

        self.conn.commit()

    def add_bond(self, molname, bond):
        # This method adds bond entries to the Bonds/MoleculeBond tables
        # by linking the bond_id value from the Bonds table.
        values = (bond.a1, bond.a2, bond.epairs)
        table = 'Bonds'
        query = f"INSERT INTO {table} (A1, A2, EPAIRS) VALUES {values}"

        self.cursor.execute(query)
        bond_id = self.cursor.lastrowid
        
        lookup = f"SELECT MOLECULE_ID FROM Molecules WHERE NAME = '{molname}'"
        molecule_id = self.conn.execute(lookup).fetchone()[0]

        table2 = 'MoleculeBond'
        values2 = (molecule_id, bond_id)
        query2 = f"INSERT INTO {table2} (MOLECULE_ID, BOND_ID) VALUES {values2}"
        self.cursor.execute(query2)

        self.conn.commit()

    def add_molecule(self, name, fp):
        # Adds entries to the Molecules table as instructed in outline pdf
        mol = MolDisplay.Molecule()
        mol.parse(fp)
        table = 'Molecules'

        query = f"INSERT INTO {table} (NAME) VALUES ('{name}')"
        self.cursor.execute(query)
        self.conn.commit()

        for i in range(mol.atom_no):
            atm = mol.get_atom(i)
            self.add_atom(name, atm)

        for j in range(mol.bond_no):
            bnd = mol.get_bond(j)
            self.add_bond(name, bnd)

    def load_mol(self, name):
        # Retrieves all atoms and bond entries using JOIN SQLite commands and appends them
        mol = MolDisplay.Molecule()

        atomQuery = f"""
            SELECT atoms.*
            FROM atoms
            JOIN molecules ON moleculeAtom.molecule_id = molecules.molecule_id
            JOIN moleculeAtom ON atoms.atom_id = moleculeAtom.atom_id
            WHERE molecules.name = "{name}"
        """
        atomOutput = self.cursor.execute(atomQuery).fetchall()

        for i in atomOutput:
            mol.append_atom(str(i[1]), float(i[2]), float(i[3]), float(i[4]))

        bondQuery = f"""
            SELECT bonds.*
            FROM bonds
            JOIN molecules ON moleculeBond.molecule_id = molecules.molecule_id
            JOIN moleculeBond ON bonds.bond_id = moleculeBond.bond_id
            WHERE molecules.name = "{name}"
        """
        bondOutput = self.cursor.execute(bondQuery).fetchall()

        for j in bondOutput:
            mol.append_bond(int(j[1]), int(j[2]), int(j[3]))

        self.conn.commit()
        return mol

    def radius(self):
        # Adds radius values to existing dictionary
        query = f"SELECT ELEMENT_CODE, RADIUS FROM Elements"
        
        output = self.cursor.execute(query).fetchall()
        output = dict(output)
        
        self.conn.commit()
        return output
    
    def element_name(self):
        # Adds element_name values to existing dictionary
        query = f"SELECT ELEMENT_CODE, ELEMENT_NAME FROM Elements"
        
        output = self.cursor.execute(query).fetchall()
        output = dict(output)

        self.conn.commit()
        return output

    def radial_gradients(self):
        # Returns appropriate svg string to create radial gradients for all atoms
        query = f"SELECT ELEMENT_NAME, COLOUR1, COLOUR2, COLOUR3 FROM Elements"
        output = self.cursor.execute(query).fetchall()
        self.conn.commit()

        allGradients = []

        for i in output:
            element_name, c1, c2, c3 = i
            radialGradientSVG = """
                <radialGradient id="%s" cx="-50%%" cy="-50%%" r="220%%" fx="20%%" fy="20%%">
                <stop offset="0%%" stop-color="#%s"/>
                <stop offset="50%%" stop-color="#%s"/>
                <stop offset="100%%" stop-color="#%s"/>
                </radialGradient>
            """ % (element_name, c1, c2, c3)
            allGradients.append(radialGradientSVG)

        retString = "".join(allGradients)

        return retString


# "main" for testing purposes
# if __name__ == "__main__":
#     db = Database(reset=True)
#     db.create_tables()
    
#     db['Elements'] = ( 1, 'H', 'Hydrogen', 'FFFFFF', '050505', '020202', 25 )
#     db['Elements'] = ( 6, 'C', 'Carbon', '808080', '010101', '000000', 40 )
#     db['Elements'] = ( 7, 'N', 'Nitrogen', '0000FF', '000005', '000002', 40 )
#     db['Elements'] = ( 8, 'O', 'Oxygen', 'FF0000', '050000', '020000', 40 )
    
#     fp = open( 'water-3D-structure-CT1000292221.sdf' )
#     db.add_molecule( 'Water', fp )
  
#     fp = open( 'caffeine-3D-structure-CT1001987571.sdf' )
#     db.add_molecule( 'Caffeine', fp )
   
#     fp = open( 'CID_31260.sdf' )
#     db.add_molecule( 'Isopentanol', fp )
    
#     MolDisplay.radius = db.radius()
#     MolDisplay.element_name = db.element_name()
#     MolDisplay.header += db.radial_gradients()
    
#     for molecule in [ 'Water', 'Caffeine', 'Isopentanol' ]:
#         mol = db.load_mol( molecule )
#         mol.sort()
#         fp = open( molecule + ".svg", "w" )
#         fp.write( mol.svg() )
#         fp.close()

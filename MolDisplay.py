import molecule

# Implemented A3 changes to these 2 dictionaries
radius = {}
element_name = {}

header = """<svg version="1.1" width="1000" height="1000" xmlns="http://www.w3.org/2000/svg">"""

footer = """</svg>"""

offsetx = 500
offsety = 500

# This section of the code implements the Atom and Bond classes and the Molecule subclass.
class Atom:
    def __init__(self, c_atom):
        # initializing the class and z variable as instructed
        self.atom = c_atom
        self.z = c_atom.z

    def __str__(self):
        # returning a string with relevant values as instructed (testing purposes)
        return f"Element: {self.atom.element} \nx: {self.atom.x} \ny: {self.atom.y} \nz: {self.atom.z}"
    
    def svg(self):
        # calculates cx and cy values. Retrieves radius and colour fields.
        x = (self.atom.x * 100.0) + offsetx
        y = (self.atom.y * 100.0) + offsety
        
        r = radius[self.atom.element]
        
        colour = element_name[self.atom.element]
        return f'  <circle cx="{x:.2f}" cy="{y:.2f}" r="{r}" fill="url(#{colour})"/>\n'

class Bond:
    def __init__(self, c_bond):
        # intializing the class and z variable as instructed
        self.bond = c_bond
        self.z = c_bond.z

    def __str__(self):
        # returning a string with relevant values as instructed (testing purposes)
        return f"x1: {self.bond.x1} x2: {self.bond.x2} y1: {self.bond.y1} y2: {self.bond.y2} z: {self.bond.z} len: {self.bond.len} dx: {self.bond.dx} dy: {self.bond.dy} a1: {self.bond.a1} a2: {self.bond.a2} epairs: {self.bond.epairs}"
    
    def svg(self):
        # calculating coordinates for all 4 polygon corners (order is intentional here)
        p1x = ((self.bond.x1 * 100) + offsetx) - (self.bond.dy * 10)
        p1y = ((self.bond.y1 * 100) + offsety) + (self.bond.dx * 10)

        p2x = ((self.bond.x1 * 100) + offsetx) + (self.bond.dy * 10)
        p2y = ((self.bond.y1 * 100) + offsety) - (self.bond.dx * 10)

        p3x = ((self.bond.x2 * 100) + offsetx) + (self.bond.dy * 10)
        p3y = ((self.bond.y2 * 100) + offsety) - (self.bond.dx * 10)

        p4x = ((self.bond.x2 * 100) + offsetx) - (self.bond.dy * 10)
        p4y = ((self.bond.y2 * 100) + offsety) + (self.bond.dx * 10)

        return ' <polygon points="%.2f,%.2f %.2f,%.2f %.2f,%.2f %.2f,%.2f" fill="green"/>\n' % (p1x, p1y, p2x, p2y, p3x, p3y, p4x, p4y)
       
class Molecule (molecule.molecule):
    def __str__ (self):
        # returning a string with relvant values as instructed (testing purposes)
        return f"atom_max: {self.atom_max} atom_no: {self.atom_no} bond_max: {self.bond_max} bond_no: {self.bond_no}\n"
    
    def svg(self):
        # Retrieving atoms and bonds inside lists. 
        # Merging these two lists together, before sorting them using python's built-in
        # "sorted()" function. Appending sorted list's svg attribute to header and footer.
        # Returning this svg string from the method.
        a1, b1, both, svgs = ([] for i in range(4))
        
        for i in range(self.atom_no):
            atm = Atom(self.get_atom(i))
            a1.append(atm)

        for j in range(self.bond_no):
            bnd = Bond(self.get_bond(j))
            b1.append(bnd)

        both = a1 + b1 

        sortedList = sorted(both, key=lambda x: x.z)

        for obj in sortedList:
            svgs.append(obj.svg())

        retStr = header + ''.join(svgs) + footer
        return retStr

    def parse(self, file_object):
        # Skipping over first 4 header lines inside the sdf file.
        # Storing atom_no and bond_no values from 4th line in the file.
        # Looping through atom_no times to extract/append x, y, z, and element values.
        # Looping through bond_no times to extract/append a1, a2, and epairs values.
        x, y, z = 0, 0, 0
        a1, a2, epairs = 0, 0, 0

        for i in range(3):
            next(file_object)

        fourth = file_object.readline().strip()
        fourth = fourth.split()

        atom_no = int(fourth[0])
        bond_no = int(fourth[1])

        for i in range(atom_no):
            atomLine = file_object.readline().strip()
            x, y, z, element = atomLine.split()[:4]
            self.append_atom(str(element), float(x), float(y), float(z))

        for i in range(bond_no):
            bondLine = file_object.readline().strip()
            a1, a2, epairs = bondLine.split()[:3]

            # This is apart of A3 - Part 0
            a1 = int(a1) - 1
            a2 = int(a2) - 1

            self.append_bond(int(a1), int(a2), int(epairs))

# export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:.

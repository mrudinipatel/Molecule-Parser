import sys
from io import BytesIO, TextIOWrapper
from http.server import HTTPServer, BaseHTTPRequestHandler
import MolDisplay
from molsql import Database
import cgi
import json
import molecule

db = Database(reset=True)
db.create_tables()

db['Elements'] = ( 1, 'H', 'Hydrogen', 'FFFFFF', '050505', '020202', 25 )
db['Elements'] = ( 6, 'C', 'Carbon', '808080', '010101', '000000', 40 )
db['Elements'] = ( 7, 'N', 'Nitrogen', '0000FF', '000005', '000002', 40 )
db['Elements'] = ( 8, 'O', 'Oxygen', 'FF0000', '050000', '020000', 40 )

class MyHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/":
            with open("index.html", "rb") as f:
                htmlContent = f.read()

            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(htmlContent)
        elif self.path == "/style.css":
            with open("style.css", "rb") as f:
                cssContent = f.read()

            self.send_response(200)
            self.send_header('Content-type', 'text/css')
            self.end_headers()
            self.wfile.write(cssContent)
        elif self.path == "/index.js":
          with open("index.js", "rb") as f:
              jsContent = f.read()

          self.send_response(200)
          self.send_header('Content-type', 'text/javascript')
          self.end_headers()
          self.wfile.write(jsContent)
        elif self.path == '/showTable':
            query = f"SELECT * FROM Elements"
            elInfo = db.cursor.execute(query).fetchall()
            db.conn.commit()

            self.send_response(200)
            self.send_header("Content-type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps(elInfo).encode())
        else:
            self.send_response(404)
            self.end_headers()
            self.wfile.write(bytes("404: not found", "utf-8"))
      
    def do_POST(self):
        if self.path == "/molecule":
            cgi.parse_header(self.headers['Content-Type'])

            form = cgi.FieldStorage(
                fp = self.rfile,
                headers = self.headers,
                environ = {'REQUEST_METHOD': 'POST'}
            )

            file_name = form['sdf_file'].file
            name = form.getvalue('mol_name')

            contentLength = int(self.headers['Content-Length'])
            info = file_name.read(contentLength)
            obj = TextIOWrapper(BytesIO(info))

            db.add_molecule(name, obj)

            nums = db.load_mol(name)
            nums = str(nums)
            start = "atom_no: "
            end = " bond_max: "
            atom_no = (nums.split(start))[1].split(end)[0]
            bond_no = nums.split("bond_no: ",1)[1]
            bond_no = bond_no.rstrip()
            returnStr = name + " (Atoms: " + atom_no + " bonds: " + bond_no + ")"

            self.send_response(200)
            self.send_header("Content-type", "text/plain")
            self.end_headers()
            self.wfile.write(bytes(returnStr, "utf-8"))
        elif self.path == '/selected':
            contentLength = int(self.headers['Content-Length'])
            body = self.rfile.read(contentLength)

            opt = repr(body.decode('utf-8'))
            opt = opt.replace("'", "")
            opt = opt.split(' (')[0]

            loadedMol = db.load_mol(opt)

            MolDisplay.radius = db.radius()
            MolDisplay.element_name = db.element_name()
            MolDisplay.header += db.radial_gradients()

            loadedMol.sort()
            svg = loadedMol.svg()

            self.send_response(200)
            self.send_header("Content-type", "image/svg+xml")
            self.end_headers()
            self.wfile.write(svg.encode())
        elif self.path == '/rotate':
            cgi.parse_header(self.headers['Content-Type'])

            form = cgi.FieldStorage(
                fp = self.rfile,
                headers = self.headers,
                environ = {'REQUEST_METHOD': 'POST'}
            )
            
            x_coor = int(form['x'].value)
            y_coor = int(form['y'].value)
            z_coor = int(form['z'].value)
            molName = form.getvalue('molVal')
            molName = molName.split(' (')[0]

            loadedMol = db.load_mol(molName)
            mx = molecule.mx_wrapper(x_coor,y_coor,z_coor)
            loadedMol.xform(mx.xform_matrix)
            
            loadedMol.sort()
            svg = loadedMol.svg()

            self.send_response(200)
            self.send_header("Content-type", "image/svg+xml")
            self.end_headers()
            self.wfile.write(svg.encode())
        elif self.path == '/addElements':
            cgi.parse_header(self.headers['Content-Type'])

            form = cgi.FieldStorage(
                fp = self.rfile,
                headers = self.headers,
                environ = {'REQUEST_METHOD': 'POST'}
            )

            num = form['el_num'].value
            code = (form['el_code'].value).upper()
            el_name = form['el_name'].value
            c1 = form['c1'].value
            c2 = form['c2'].value
            c3 = form['c3'].value
            rad = form['radius'].value

            db['Elements'] = (num, code, el_name, c1, c2, c3, rad)

            new_element = {
                'num': num,
                'code': code,
                'el_name': el_name,
                'c1': c1,
                'c2': c2,
                'c3': c3,
                'rad': rad
            }

            self.send_response(200)
            self.send_header("Content-type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps(new_element).encode())
        elif self.path == '/removeRow':
            contentLength = int(self.headers["Content-Length"])
            body = self.rfile.read(contentLength)
            rowData = json.loads(body)
            code = rowData['element_code']

            query = f"DELETE FROM Elements WHERE ELEMENT_CODE = '{code}'"
            db.cursor.execute(query)

            self.send_response(200)
            self.send_header("Content-type", "text/plain")
            self.end_headers()
        else:
            self.send_response(404)
            self.end_headers()
            self.wfile.write(bytes("404: not found", "utf-8"))

httpd = HTTPServer(('localhost', int(sys.argv[1])), MyHandler)
httpd.serve_forever()


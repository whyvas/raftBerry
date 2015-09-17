from pykml import parser

root = parser.fromstring(open('piDock.kml', 'r').read())
print root.Document.Folder.Placemark.Point.coordinates

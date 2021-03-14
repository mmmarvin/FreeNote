##################
#
#    FreeNote v.1.00
#    Copyright (C) 2019 Marvin Manese
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <https://www.gnu.org/licenses/>.
# 
##################
import PyQt5
from PyQt5.QtWidgets import *
from detail import note

def main():
	app = QApplication([])
	
	windows = []
	notes = note.loadNotes()
	if len(notes) > 0:
		showAbout = True
		for noteSetting in notes:
			noteWindow = note.NoteWindow(noteSetting, windows)
			noteWindow.show()
			windows.append(noteWindow)
			showAbout = False
		notes.clear()
	else:
		noteWindow = note.NoteWindow(None, windows)
		noteWindow.show()
		windows.append(noteWindow)
	
	app.aboutToQuit.connect(note.NoteWindow.exit)
	app.exec_()
	
if __name__ == "__main__": 
	main()

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
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from pathlib import Path
import json
import io
import os

class AddActionObject:
	def __init__(self, windows):
		self.__mWindows = windows
		
	def __call__(self):
		newWindow = NoteWindow(None, self.__mWindows)
		newWindow.show()
		self.__mWindows.append(newWindow)
		
class CloseActionObject:
	def __init__(self, window, windows):
		self.__mWindow = window
		self.__mWindows = windows
		
	def __call__(self):
		if len(self.__mWindows) > 1:
			self.__mWindow.close()
			self.__mWindows.remove(self.__mWindow)
			
class DraggableToolBar(QToolBar):
	def __init__(self, parent):
		super().__init__(parent)
		self.__mParent = parent
		self.__mPressed = False
		self.__mDiffX = 0
		self.__mDiffY = 0
		
	def mousePressEvent(self, event):
		if event.button() == Qt.LeftButton:
			self.__mPressed = True
			self.__mDiffX = event.globalX() - self.__mParent.geometry().left()
			self.__mDiffY = event.globalY() - self.__mParent.geometry().top()
			
	def mouseReleaseEvent(self, event):
		if event.button() == Qt.LeftButton:
			self.__mPressed = False
			
	def mouseMoveEvent(self, event):
		if self.__mPressed == True:
			windowWidth = self.__mParent.geometry().width()
			windowHeight = self.__mParent.geometry().height()
			self.__mParent.setGeometry(event.globalX() - self.__mDiffX, event.globalY() - self.__mDiffY, windowWidth, windowHeight)
			
	def contextMenuEvent(self, event):
		pass
					
class NoteWindow(QMainWindow):
	def __init__(self, noteSetting, windows):
		super().__init__()
		super().setGeometry(0, 0, 200, 200)
		self.setWindowFlags(Qt.FramelessWindowHint)
		self.__mWindowList = windows
		self.__mTextEdit = QTextEdit(self)
		self.__mTextEdit.setStyleSheet("QTextEdit { background: rgb(255, 255, 198); selection-background-color: rgb(159, 159, 0); }")
		self.__mTextEdit.setFrameStyle(QFrame.NoFrame)
		self.__mToolBar = DraggableToolBar(self)
		self.__mToolBar.setStyleSheet("QToolBar { background: rgb(255, 255, 198); border: none; } QToolButton:!hover {background-color: rgb(255, 255, 198)}")
		self.__mToolBar.setMovable(False)
		self.addToolBar(self.__mToolBar)
		self.statusBar().setSizeGripEnabled(True)
		self.statusBar().setStyleSheet("QStatusBar { background: rgb(255, 255, 198); border: none; }")
		
		self.__mAddNoteAction = QAction(QIcon("res/add.png"), self.tr("Add Note"), self)
		self.__mRemoveNoteAction = QAction(QIcon("res/subtract.png"), self.tr("Remove Note"), self)
		self.__mFontNoteAction = QAction(QIcon("res/font.png"), self.tr("Change Font..."), self)
		self.__mToolBar.addAction(self.__mAddNoteAction)
		self.__mToolBar.addAction(self.__mRemoveNoteAction)
		self.__mToolBar.addAction(self.__mFontNoteAction)
		
		self.__mAddNoteAction.triggered.connect(AddActionObject(windows))
		self.__mRemoveNoteAction.triggered.connect(CloseActionObject(self, windows))
		self.__mFontNoteAction.triggered.connect(self.__changeFont)
				
		super().setCentralWidget(self.__mTextEdit)
		if noteSetting != None:
			super().setGeometry(noteSetting.getPositionX(), 
								noteSetting.getPositionY(), 
								noteSetting.getWidth(), 
								noteSetting.getHeight())
			self.__mTextEdit.document().setDefaultFont(noteSetting.getFont())
			self.__mTextEdit.setText(noteSetting.getString())
      
	def exit(self):
		saveNotes(self)
			
	def __changeFont(self):
		font = QFontDialog.getFont(self)
		if font[1]:
			self.__mTextEdit.document().setDefaultFont(font[0])
			
	def __showAbout(self):
		QMessageBox.about(self, "About", "<center><img src=\"res/about.png\"><br /><br /><font size=4>FreeNote v.1.00</font><br /><font size=3>by Marvin Manese</font><br><br><font size=2>Copyright (c) 2019</font></center>")
		
	def keyPressEvent(self, event):
		if event.key() == Qt.Key_F1:
			self.__showAbout()
						
	def getFont(self):
		return self.__mTextEdit.document().defaultFont()
		
	def getString(self):
		return self.__mTextEdit.toPlainText()
		
class NoteSettings:
	def __init__(self, noteString, x, y, width, height, font):
		self.__mNoteString = noteString
		self.__mX = x
		self.__mY = y
		self.__mWidth = width
		self.__mHeight = height
		self.__mFont = font
		
	def getFont(self):
		return self.__mFont
		
	def getString(self):
		return self.__mNoteString
		
	def getPositionX(self):
		return self.__mX
		
	def getPositionY(self):
		return self.__mY
		
	def getWidth(self):
		return self.__mWidth
		
	def getHeight(self):
		return self.__mHeight
		
def _combineLines(lines):
	ret = ""
	for line in lines:
		ret = ret + line + "\n"
	return ret
        
def loadNotes():
	notes = []
	if os.path.exists(os.path.join(os.path.join(str(Path.home()), ".notes"), "notes.json")):
		with open(os.path.join(os.path.join(str(Path.home()), ".notes"), "notes.json")) as file:
			try:
				data = json.load(file)
				if data != None:
					for note in data:
						try:
							notes.append(NoteSettings(_combineLines(note["text"]), note["x"], note["y"], note["width"], note["height"], QFont(note["font name"], note["font size"], note["font weight"], note["font italic"])))
						except:
							continue
			except:
				return notes
	return notes

def saveNotes(windows):
	notesParentDirectory = os.path.join(str(Path.home()), ".notes")
	if not os.path.exists(notesParentDirectory):
		os.mkdir(os.path.join(str(Path.home()), ".notes"))
	
	with open(os.path.join(notesParentDirectory, "notes.json"), "w") as file:
		file.write("[\n")
		firstWritten = False
		for window in windows:
			if len(window.getString()) > 0:
				if firstWritten == True:
					file.write(",\n")
				file.write("\t{\n")
				file.write("\t\t\"x\": ")
				file.write(str(window.x()) + ",\n")
				file.write("\t\t\"y\": ")
				file.write(str(window.y()) + ",\n")
				file.write("\t\t\"width\": ")
				file.write(str(window.width()) + ",\n")
				file.write("\t\t\"height\": ")
				file.write(str(window.height()) + ",\n")
				
				font = window.getFont()
				file.write("\t\t\"font name\": \"")
				file.write(str(font.family()) + "\",\n")
				file.write("\t\t\"font size\": ")
				file.write(str(font.pointSize()) + ",\n")
				file.write("\t\t\"font weight\": ")
				file.write(str(font.weight()) + ",\n")
				file.write("\t\t\"font italic\": ")
				if font.italic():
					file.write("true,\n")
				else:
					file.write("false,\n")
				
				file.write("\t\t\"text\": [\n")
				lineReader = io.StringIO(window.getString())
				line = lineReader.readline()
				
				firstLineWritten = False
				while len(line) > 0:
					if line[len(line) - 1] == '\n':
						line = line[:-1]
					if firstLineWritten:
						file.write(",\n")
					file.write("\t\t\t\"" + line + "\"")
					line = lineReader.readline()
					firstLineWritten = True
				file.write("\n\t\t]\n")
				
				file.write("\t}")
				firstWritten = True
		file.write("\n]\n")

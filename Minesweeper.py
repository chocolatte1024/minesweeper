from tkinter import *
from tkinter import messagebox
import random

class MSSquare(Label):
    '''represents a Minesweeper square'''

    def __init__(self, master, coord):
        '''MSSquare(master, coord) --> MSSquare
        Creates an unexposed MSSquare'''
        Label.__init__(self,master,height=1,width=2,text='',\
                       bg='white',font=('Arial', 18),relief = 'raised')
        self.coord = coord # (row, column) coordinate tuple
        self.isbomb = False # begin out not as bombs
        self.isflagged = False # begin not flagged
        self.exposed = False # begin as unexposed
        self.gameover = False # not game over
        # Set up listeners
        self.bind('<Button-1>', self.expose)
        self.bind('<Button-2>', self.flag_change)
        self.bind('<Button-3>', self.flag_change)

    def get_coord(self):
        '''MSSquare.get_coord() --> tuple
        Returns the (row, column) coordinate of the cell'''
        return self.coord

    def is_bomb(self):
        '''MSSquare.is_bomb() --> bool
        Returns if MSSquare is a bomb'''
        return self.isbomb

    def is_exposed(self):
        '''MSSquare.is_exposed() --> bool
        Returns if MSSquare is exposed'''
        return self.exposed

    def is_flagged(self):
        '''MSSquare.is_flagged() --> bool
        Returns if MSSquare is flagged'''
        return self.isflagged

    def is_game_over(self):
        '''MSSquare.is_game_over() --> bool
        Tells if thee game is over'''
        return self.gameover

    def set_bomb(self):
        '''MSSquare.set_bomb() --> None
        Makes the square a bomb'''
        self.isbomb = True

    def set_game_over(self):
        '''MSSquare.set_game_over() --> None
        Stops the square from being edited'''
        self.gameover = True

    def get_adjacent(self):
        '''MSSquare.get_adjacent() --> tuple
        Returns xRange, yRange for min and max of adjacent squares'''
        # Find coordinates
        xCoord = self.get_coord()[0]
        yCoord = self.get_coord()[1]
        # Get adjacent squares
        xRange = (xCoord-1, xCoord+2)
        yRange = (yCoord-1, yCoord+2)
        return xRange, yRange

    def expose(self, event):
        '''Handler function for left click
        Uncovers square, ends game if its a bomb'''
        if self.is_flagged() or self.is_exposed() or self.is_game_over():
            pass
        elif self.is_bomb(): 
            self.master.lose()
        else: # Uncover the square
            self.exposed = True
            (xRange, yRange) = self.get_adjacent()
            self.num = self.master.count_bombs(xRange, yRange)
            self['relief'] = 'sunken'
            self['bg'] = 'light gray'
            if self.num == 0: # no number and show adjacent
                self['text'] = ''
                self.master.expose_adjacent(self)
            else:
                colormap = ['','blue','darkgreen','red','purple','maroon',\
                            'cyan','black','dim gray'] # set up colors
                self['fg'] = colormap[self.num]
                self['text'] = self.num
            if self.master.is_winner() and not self.master.message_shown():
                self.master.win() # make sure that message only shown once

    def flag_change(self, event):
        '''MSSquare.flag_change(event) --> None
        Flags square if unflagged, unflags square if flagged'''
        self.isflagged = not self.isflagged
        if self.is_exposed() or self.is_game_over(): # not allowed
            pass
        elif self.is_flagged(): # if now flagged
            self['text'] = '*'
            self.master.update_label(1)
        else: # if unflagged
            self['text'] = ''
            self.master.update_label(-1)

class MSFrame(Frame):
    '''object for a Minesweeper grid'''

    def __init__(self, master, width, height, numBombs):
        '''MSFrame(master,width,height,numBombs) --> MSFrame
        creates a new Minesweeper grid'''
        Frame.__init__(self, master, bg='black')
        self.grid()
        self.gameover = False # start as not game over
        # Place down the squares
        self.squares = {}
        for row in range(height):
            for column in range(width):
                coord = (row, column)
                self.squares[coord] = MSSquare(self, coord)
                self.squares[coord].grid(row=row,column=column)
        # Choose the bombs
        self.coordList = list(self.squares.keys()) # list of tuples for coords
        self.bombSquares = random.sample(self.coordList, k=numBombs)
        self.safeSquares = self.coordList[:]
        for coord in self.bombSquares:
            self.squares[coord].set_bomb() # make them bombs
            self.safeSquares.remove(coord) # not a safe square
        # Add flag counter label
        self.labelFrame = Frame(self,bg='black') # new frame
        self.flagLabel = Label(self.labelFrame,text=numBombs,font=('Arial', 24))
        self.flagLabel.grid(row=height+1)
        self.labelFrame.grid(row=height+1,column=0,columnspan=width)

    def get_squares(self):
        '''MSFrame.get_squares() --> list
        Returns list of all coords for squares'''
        return self.coordList

    def count_bombs(self, xRange, yRange):
        '''MSFrame.count_bombs() --> int
        Returns the number of bombs in range
        xRange, yRange: tuple for min and max for range'''
        counter = 0
        # Go through every square
        for x in range(xRange[0], xRange[1]):
            for y in range(yRange[0], yRange[1]):
                try:
                    if self.squares[(x, y)].is_bomb(): 
                        counter += 1
                except: # if it goes off the grid
                    pass
        return counter

    def expose_adjacent(self, square):
        '''MSFrame.expose_adjacent() --> None
        Exposes squares adjacent to blank square'''
        (xRange, yRange) = square.get_adjacent() # find neighboring squares
        # Uncover every square
        for x in range(xRange[0], xRange[1]):
            for y in range(yRange[0], yRange[1]):
                try:
                    self.squares[(x, y)].expose(0) 
                except: # if it goes off the grid
                    pass

    def update_label(self, value):
        '''MSFrame.update_label(value) --> None
        Decreases flag label by value, use negative to increase'''
        self.flagLabel['text'] -= value

    def is_winner(self):
        '''MSFrame.is_winner() --> bool
        Checks if every safe square has been exposed'''
        for coord in self.safeSquares:
            if not self.squares[coord].is_exposed(): # every safe square
                return False
        return True

    def message_shown(self):
        '''MSFrame.message_shown() --> bool
        Checks if the winning message has been shown'''
        return self.gameover

    def win(self):
        '''MSFrame.win() --> None
        Ends the game after all squares have been exposed'''
        messagebox.showinfo('Minesweeper','Congratulations -- you won!',\
                            parent=self)
        self.gameover = True
        for square in self.squares.values(): # cannot be altered
            square.set_game_over()

    def lose(self):
        '''MSFrame.lose() --> None
        Ends the game after clicking a bomb'''
        for square in self.squares.values():
            square.set_game_over() # cannot be altered
        # Show message
        messagebox.showerror('Minesweeper','KABOOM! You lose.',parent=self)
        # Show bomb squares
        for coord in self.bombSquares:
            bombSquare = self.squares[coord]
            if not bombSquare.is_flagged(): # show the ones not flagged
                bombSquare['text'] = '*'
                bombSquare['bg'] = 'red'
        # Show incorrectly flagged squares
        for coord in self.safeSquares:
            safeSquare = self.squares[coord]
            if safeSquare.is_flagged():
                safeSquare['bg'] = 'light green' # turn them green
        
class SelectionFrame(Frame):
    '''allows player to select difficulty of game'''

    def __init__(self, master):
        '''SelectionFrame(master) --> SelectionFrame'''
        Frame.__init__(self, master)
        self.grid()
        Label(self,text='Choose the difficulty.').grid(row=0,column=1,columnspan=2)
        Button(self,text='Easy:\n10x12\n15 bombs',command=self.easy_MS).grid(row=1,column=0)
        Button(self,text='Medium:\n16x20\n40 bombs',command=self.med_MS).grid(row=1,column=1)
        Button(self,text='Hard:\n20x25\n99 bombs',command=self.hard_MS).grid(row=1,column=2)
        Button(self,text='\nSurprise!\n',command=self.surprise_MS).grid(row=1,column=3)

    def easy_MS(self):
        self.master.destroy()
        play_minesweeper(12, 10, 15)

    def med_MS(self):
        self.master.destroy()
        play_minesweeper(20, 16, 40)

    def hard_MS(self):
        self.master.destroy()
        play_minesweeper(25, 20, 99)

    def surprise_MS(self):
        self.master.destroy()
        play_minesweeper(20, 15, 1)
                                                                         
def play_minesweeper(width,height,numBombs):
    '''play_minesweeper(width,height,numBombs)
    loads a width x height game of Minesweeper with numBombs bombs'''
    root = Tk()
    root.title('Minesweeper')
    msf = MSFrame(root, width, height, numBombs)
    root.mainloop()

root = Tk()
root.title('Level Selection')
lsf = SelectionFrame(root)
root.mainloop()

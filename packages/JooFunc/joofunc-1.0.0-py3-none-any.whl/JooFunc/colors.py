import re,curses
from colorama import init, Fore, Back, Style

init(autoreset=True)

fc = Fore.CYAN
fg = Fore.GREEN
fw = Fore.WHITE
fr = Fore.RED
fb = Fore.BLUE
fy = Fore.YELLOW
fm = Fore.MAGENTA

bc = Back.CYAN
bg = Back.GREEN
bw = Back.WHITE
br = Back.RED
bb = Back.BLUE
by = Fore.YELLOW
bm = Fore.MAGENTA

sd = Style.DIM
sn = Style.NORMAL
sb = Style.BRIGHT

def get_color(color_str:str,type:str) -> str:
    if type=='curser':
        if color_str in ['red','RED','R']: return curses.color_pair(1)
        if color_str in ['blue','BLUE','B']: return curses.color_pair(2)
        if color_str in ['white','WHITE','W']: return curses.color_pair(3)
        if color_str in ['black','BLACK','BK']: return curses.color_pair(4)
        if color_str in ['green','GREEN','G']: return curses.color_pair(5)
        if color_str in ['yellow','YELLOW','Y']: return curses.color_pair(6)
        if color_str in ['megenta','MEGENTA','M']: return curses.color_pair(7)
        if color_str in ['cyan','CYAN','C']: return curses.color_pair(8)
    if color_str in ['red','RED','R']: return fr
    if color_str in ['blue','BLUE','B']: return fb
    if color_str in ['white','WHITE','W']: return fw
    if color_str in ['black','BLACK','BK']: return fb
    if color_str in ['green','GREEN','G']: return fg
    if color_str in ['yellow','YELLOW','Y']: return fy
    if color_str in ['megenta','MEGENTA','M']: return fm
    if color_str in ['cyan','CYAN','C']: return fc
    return None

def extract_colors_from_string(text:str,sep:str,type='normal') -> list:
    finall_data = []
    Colors = re.findall(sep+r'\w+'+sep,text)
    counter = 0
    for color in Colors:
        color_index = text.index(color)+len(color)
        try:
            next_color = Colors[counter+1]
            text_need = text[color_index:text.index(next_color)]
        except:
            text_need = text[color_index:]
        text = text[color_index:]
        color = re.search(r'(\w+)',color).group(1)
        if get_color(color,type):
            finall_data.append({
                'text':text_need,
                'color':color
            })
        counter+=1
    return finall_data

class TerminalControllerProgress:
    def __init__(self,**args) -> None:
        if args:
            self._control = curses.initscr(args)
        else:
            self._control = curses.initscr()

        self._control.nodelay(1) # Don't block waiting for input.
        curses.echo()

        curses.start_color()
        curses.init_pair(1, curses.COLOR_RED, curses.COLOR_BLACK) # red
        curses.init_pair(2, curses.COLOR_BLUE, curses.COLOR_BLACK) # blue
        curses.init_pair(3, curses.COLOR_WHITE, curses.COLOR_BLACK) # white
        curses.init_pair(4, curses.COLOR_BLACK, curses.COLOR_BLACK) # black
        curses.init_pair(5, curses.COLOR_GREEN, curses.COLOR_BLACK) # green
        curses.init_pair(6, curses.COLOR_YELLOW, curses.COLOR_BLACK) # yellow
        curses.init_pair(7, curses.COLOR_MAGENTA, curses.COLOR_BLACK) # megenta
        curses.init_pair(8, curses.COLOR_CYAN, curses.COLOR_BLACK) # cyan

    def add_line(self,line_row:int,line_hight:int,text:str,sep='%'):
        """
        line_row -> int : start terminal row line\n
        line_hight -> int : start terminal height line\n
        text -> str\n
        sep -> str\n
        Just Put '%COLOR%' in ur string to color it\n
        ex: "Some%GREEN% in%YELLOW%my %RED%String"\n
        Note: You Can Add Your Own seprator in var "sep"
        =============================================\n
        Colors List:
        Yellow: %YELLOW% or %Y%\n
        Blue: %BLUE% or %B%\n
        Green: %GREEN% or %G%\n
        BLACK: %BLACK% or %BK%\n
        White: %WHITE% or %W%\n
        Megenta: %MEGENTA% or %M%\n
        Cyan: %CYAN% or %C%\n
        =============================================\n
        """
        data = extract_colors_from_string(text,sep,'curser')
        if data:
            for i in data:
                color = get_color(i['color'],'curser')
                ttext = i['text']
                if ttext==data[0]['text']:
                    try:
                        self._control.addstr(line_row,line_hight,ttext,color)
                    except:
                        try:
                            self._control.addstr(
                                line_row,line_hight,ttext,get_color('white','curser')
                            )
                        except: pass
                else:
                    try:
                        self._control.addstr(ttext,color)
                    except:
                        try:
                           self._control.addstr(text,get_color('white','curser'))
                        except: pass
        else:
            try:
                self._control.addstr(line_row,line_hight,text,get_color("white",'curser'))
            except: pass
    def add_string(self,text_data:str|list,seplines='\n',start_row=0,start_hieght=0,color_sep='%'):
        """
        Type String Normal And End Line With '\\n'
        Or Type Your Custom seprator ex: ^,&,*,%,7,31
        ----------------------------------
        Remember to Put '%COLOR%' OR '%B%' First char in Color Name\n\r in ur string to color it\n
        ex: "Some%GREEN% in%YELLOW%my %RED%String"
        """
        strings = text_data if type(text_data)==list else text_data.split(seplines)
        for text in strings:
            self.add_line(start_row,start_hieght,text,color_sep)
            start_row+=1

    def print(self):
        "Print And Start New Progress in Console"
        self._control.refresh()

    def get_input(self) -> int:
        return get_char_by_number(abs(self._control.getch()))
    def end(self):
        "End The Progress Console"
        self._control.clear()
        curses.echo()
        curses.nocbreak()
        curses.endwin()

class NormalProgress:
    def __init__(self,constant_text={}) -> None:
        self._text = []

    def add_line(self,text:str,sep='%'):
        """
        line_row -> int : start terminal row line\n
        line_hight -> int : start terminal height line\n
        text -> str\n
        sep -> str\n
        Just Put '%COLOR%' in ur string to color it\n
        ex: "Some%GREEN% in%YELLOW%my %RED%String"\n
        Note: You Can Add Your Own seprator in var "sep"
        =============================================\n
        Colors List:
        Yellow: %YELLOW% or %Y%\n
        Blue: %BLUE% or %B%\n
        Green: %GREEN% or %G%\n
        BLACK: %BLACK% or %BK%\n
        White: %WHITE% or %W%\n
        Megenta: %MEGENTA% or %M%\n
        Cyan: %CYAN% or %C%\n
        =============================================\n
        """
        data = extract_colors_from_string(text,sep,'normal')
        if data:
            d = ""
            for i in data:
                d += get_color(i['color'],'normal')+i['text']
            self._text.append(d)
        else:
            self._text.append(text)
    def add_string(self,text_data:str|list,seplines='\n',color_sep='%'):
        """
        Type String Normal And End Line With '\\n'
        Or Type Your Custom seprator ex: ^,&,*,%,7,31
        ----------------------------------
        Remember to Put '%COLOR%' OR '%B%' First char in Color Name\n\r in ur string to color it\n
        ex: "Some%GREEN% in%YELLOW%my %RED%String"
        """
        strings = text_data if type(text_data)==list else text_data.split(seplines)
        for text in strings:
            self.add_line(text,color_sep)

    def print(self):
        "Print And Start New Progress in Console"
        for text in self._text:
            print(text)
        self._text = []
# curses.wrapper(Main)
# 65 -> 96
# 97 -> 122 A

def get_number_by_char(char='c'):
    char = char.lower()
    counter = 1
    for i in range(97,122):
        if ord(char)==i: return counter
        counter+=1
def get_char_by_number(num=3):
    counter=1
    for i in range(97,122):
        if num==counter: return chr(i)
        counter+=1



from .progressbar import (
    NormalProgressBar,TerminalProgressBar,
    EmptyProgressBar
)
from .func import clear,getCurrentPath,Faker,requests

DEFAULT_FILENAME = "filename.joo"

DEFAULT_MIN_TEMP_FILES = 1
DEFAULT_MAX_TEMP_FILES = 10 # 5000
DEFAULT_SIZE_TEMP_FILE = 10485760 # 1MB

def DEFAULT_CLEAR():
    clear()


DEFAULT_THREADS = 8
DEFAULT_PATH = getCurrentPath()
DEFAULT_TEMP_EXT = ".downUnknown"
DEFAULT_TEMP_FOLDER = ""
DEFAULT_HEADERS = {'User-Agent': Faker().user_agent()}
DEFAULT_SESSION = requests

DEFAULT_COLOR_SEP = '!'
DEFAULT_VAR_SEP = '&'
DEFAULT_PROGRESSBAR = "normal"
# Single url
DEFAULT_RANGE_TEXT = [
    "!G!      \r-.....!G!Download Page!R!.....-",
    "-"*50,
    "!B!Server Type.......!W!: !G!Read Size Success",
    "-"*50,
    "!Y!File Name.........!W!: !G!&FileName&",
    "!Y!File Path.........!W!: !G!&FilePath&",
    "!Y!Total Size........!W!: !G!&FileSize&",
    "-"*50,
    "!G!Time Left.........!W!: !R!&TimeLeft&",
    "!G!Elepesed Time.....!W!: !R!&TimeElep&",
    "!G!Downloaded Bytes..!W!: !R!&Downloaded&     ",
    "!G!Founded Bytes.....!W!: !R!&Found&     ",
    "!G!Download Speed....!W!: !R!&Speed&     ",
    "!G!Progress Bar......!W!: &ProgressBar& !Y!&Percent&   ",
    "!G!Progress..........!W!: &ProgressData&    ",
    "!G!Formated Progress.!W!: &FProgressData&   ",
    "-"*50
]
DEFAULT_NO_RANGE_TEXT = [
    "           !G!-.....!G!Download Page!R!.....-",
    "-"*50,
    "!B!Server Type.......!W!: !R!Read Size Failed",
    "-"*50,
    "!Y!File Name.........!W!: !G!&FileName&",
    "!Y!File Path.........!W!: !G!&FilePath&",
    "-"*50,
    "!G!Time Left.........!W!: !R!&TimeLeft&",
    "!G!Elepesed Time.....!W!: !R!&TimeElep&",
    "!G!Downloaded Bytes..!W!: !R!&Downloaded&       ",
    "!G!Download Speed....!W!: !R!&Speed&     ",
    "!G!Progress..........!W!: &ProgressData&     ",
    "!G!Formated Progress.!W!: &FProgressData&    ",
    "-"*50
]
DEFAULT_AFTER_DOWNLOAD_TEXT = [
    "          !G!-.....!G!After Download Page!R!.....-",
    "-"*50,
    "!B!Download Status.......!W!: &Status&",
    "-"*50,
    "!Y!File Name.........!W!: !G!&FileName&",
    "!Y!File Path.........!W!: !G!&FilePath&",
    "!Y!File Size.........!W!: !G!&FileSize&",
    "!Y!Time Left.........!W!: !G!&TLeft&",
    "!Y!Downloaded........!W!: !G!&Downloaded&   ",
    "!Y!Founded...........!W!: !G!&Founded&",
    "-"*50,
    "!Y!Collecting Files!W!: &Reading&",
    "-"*50
]

# Multi URL in one file
DEFAULT_MULTI_RANGE_TEXT = [
    "!G!        -.....!G!Download Page!R!.....-",
    "-"*50,
    "!B!Server Type.......!W!: !G!Read Size Success",
    "-"*50,
    "!Y!File Name.........!W!: !G!&FileName&",
    "!Y!File Path.........!W!: !G!&FilePath&",
    "!Y!Current File......!W!: !G!&CurrentFile&",
    "!Y!Current File Size.!W!: !G!&CurrentFileSize&",
    "!Y!Total Files.......!W!: !G!&Files&",
    "!Y!Total Size........!W!: !G!&FileSize&",
    "-"*50,
    "!G!Time Left.........!W!: !R!&TimeLeft&",
    "!G!Elepesed Time.....!W!: !R!&TimeElep&",
    "!G!Files.............!W!: !R!&Files&!W!/&TFiles&   ",
    "!G!Downloaded Bytes..!W!: !R!&Downloaded&     ",
    "!G!Founded Bytes.....!W!: !R!&Found&     ",
    "!G!Download Speed....!W!: !R!&Speed&     ",
    "!G!Progress Bar......!W!: &ProgressBar& !Y!&Percent&   ",
    "!G!Progress..........!W!: &ProgressData&    ",
    "!G!Formated Progress.!W!: &FProgressData&   ",
    "-"*50
]
DEFAULT_MULTI_NO_RANGE_TEXT = [
    "!G!        -.....!G!Download Page!R!.....-",
    "-"*50,
    "!B!Server Type.......!W!: !R!Read Size Failed",
    "-"*50,
    "!Y!File Name.........!W!: !G!&FileName&",
    "!Y!File Path.........!W!: !G!&FilePath&",
    "!Y!Current File......!W!: !G!&CurrentFile&",
    "!Y!Current File Size.!W!: !G!&CurrentFileSize&",
    "!Y!Total Files.......!W!: !G!&Files&",
    "-"*50,
    "!G!Time Left.........!W!: !R!&TimeLeft&",
    "!G!Elepesed Time.....!W!: !R!&TimeElep&",
    "!G!Files.............!W!: !R!&Files&!W!/&TFiles&   ",
    "!G!Downloaded Bytes..!W!: !R!&Downloaded&     ",
    "!G!Download Speed....!W!: !R!&Speed&     ",
    "-"*50
]
DEFAULT_MULTI_AFTER_DOWNLOAD_TEXT = [
    "          !G!-.....!G!After Download Page!R!.....-",
    "-"*50,
    "!B!Download Status.......!W!: !G!&Status&",
    "-"*50,
    "!Y!File Name.........!W!: !G!&FileName&",
    "!Y!File Path.........!W!: !G!&FilePath&",
    "!Y!File Size.........!W!: !G!&FileSize&",
    "!Y!Time Left.........!W!: !G!&TLeft&",
    "!Y!Downloaded........!W!: !G!&Downloaded&   ",
    "!Y!Founded...........!W!: !G!&Founded&",
    "-"*50,
    "!Y!Please Wait..."
    "!Y!Collecting Files!W!: &Reading&",
    "-"*50
]

from .func import (
    removePath, convertSeconds,
    convert_size,
    makeFile, remove_char, re,
    requests, ThreadPoolExecutor, math, os,
    Self, time, requests,
    encrypt
)
from .errors import InternetConnectionError
from .default_data import *
import logging,pickle

logging.basicConfig(
    filename='LOG_JOO_SERVER.txt',
    filemode='w',
    encoding='utf-8',
    format='%(asctime)s - %(message)s',
    datefmt='%d-%b-%y %H:%M:%S'
)

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


def getRange(size: int, threads: int) -> list:
    range_list = []
    chunk_size = int(math.ceil(int(size) / int(threads)))
    i = 0
    for _ in range(threads):
        if(i + chunk_size) < int(size):
            entry = '%s-%s' % (i, i + chunk_size - 1)
        else:
            entry = '%s-%s' % (i, int(size))
        i += chunk_size
        range_list.append(entry)
    return range_list


def getLastBytes(ranges: list, threads: int, ext: str, temp_path: str) -> list:
    new_ranges = []
    for i in ranges:
        s = i.split('-')
        new_ranges.append(abs(int(s[1])-int(s[0])))
    for index in range(threads):
        filepath = temp_path.replace('$c', str(index))
        expected_filesize = new_ranges[index]
        try:
            real_filesize = os.path.getsize(filepath)
            if real_filesize in [expected_filesize+1, expected_filesize]:
                ranges[index] = expected_filesize+1
        except:
            pass
    return ranges

def isFileExist(path: str, size: int) -> bool:
    if size == 0 and os.path.exists(path):
        return True
    if os.path.exists(path) and os.path.getsize(path) == size:
        return True
    return False

class MethodRequest:
    def add(self, url: str, method='HEAD', session=requests, headers=DEFAULT_HEADERS) -> Self:
        try:
            m = session.head
            if method in ['Get', 'GET']:
                m = session.get
            elif method in ['Options', 'OPTIONS']:
                m = session.options
            elif method in ['Delete', 'DELETE']:
                m = session.delete
            self._response = m(url, headers=headers, stream=True)
            self._response.raise_for_status()
        except:
            raise InternetConnectionError(f"Can`t Connect To Server: {url}")

        self._url = url
        self._headers = self._response.headers
        try:
            self._size = int(self._headers.get('Content-Length'))
        except:
            self._size = 0
        self._fsize = convert_size(self._size)

        try:
            self._filename = remove_char(re.findall(
                "filename=\"(.+)\";", self._headers['Content-Disposition'])[0])
        except:
            self._filename = url.split('/')[-1]
        self._ctype = self._headers.get('Content-Type')
        self._accept_range = (
            'Accept-Ranges' in self._headers and self._headers['Accept-Ranges'] == 'bytes')
        return self

    @property
    def url(self) -> str:
        return self._url

    @property
    def size(self) -> int:
        return self._size

    @property
    def fsize(self) -> str:
        return self._fsize

    @property
    def name(self) -> str:
        return self._filename

    @property
    def type(self) -> str:
        return self._ctype

    @property
    def AcceptRange(self) -> bool:
        return self._accept_range

    @property
    def headers(self) -> dict:
        return self._headers

    @property
    def response(self) -> requests:
        return self._response

class DownloaderStream:
    def __init__(self, status: dict) -> None:
        self._s = status

    @property
    def status(self) -> str: return self._s["status"]
    @property
    def time(self) -> str: return self._s["time"]
    @property
    def fullpath(self) -> str: return self._s["fullpath"]
    @property
    def filename(self) -> str: return self._s["filename"]
    @property
    def path(self) -> str: return self._s["path"]
    @property
    def filesize(self) -> int: return self._s["filesize"]
    @property
    def formated_filesize(self) -> str: return self._s["formated_filesize"]
    @property
    def founded(self) -> str: return self._s["founded"]
    @property
    def formated_founded(self) -> str: return self._s["formated_founded"]
    @property
    def downloaded(self) -> str: return self._s["downloaded"]
    @property
    def formated_downloaded(self) -> str: return self._s["formated_downloaded"]

class _MultiDownload:
    def __init__(self) -> None:
        self._last_status = {}
        self._total_downloaded = 0
        self._all_status = []
        self._request_reader = MethodRequest()
        self._last_status = DownloaderStream

    def new(self,
            urls: list,
            filename=DEFAULT_FILENAME,
            path=DEFAULT_PATH,
            headers=DEFAULT_HEADERS,
            session=DEFAULT_SESSION,
            threads=DEFAULT_THREADS,
            max_size=DEFAULT_SIZE_TEMP_FILE,
            progress='normal',
            range_text=DEFAULT_MULTI_RANGE_TEXT,
            no_range_text=DEFAULT_MULTI_NO_RANGE_TEXT,
            after_text=DEFAULT_MULTI_AFTER_DOWNLOAD_TEXT,
            clear_func=DEFAULT_CLEAR,
            same_file=True,
            check_file_with_size=True) -> Self:

        self._same_file = same_file

        self._clear_func = clear_func
        self._progressbar_range_text = range_text
        self._progressbar_no_range_text = no_range_text
        self._progressbar_after_text = after_text

        self._prog = progress
        self._filename = filename if filename else DEFAULT_FILENAME
        self.__threadObj = ThreadPoolExecutor(max_workers=threads)
        self._real_urls = []
        self._urls = urls
        self._number_of_urls = len(urls)
        self._size = 0
        self._threads = threads
        self._max_size = max_size
        # Extract Size
        for t in [self.__threadObj.submit(self._request_reader.add, url, 'GET', session, headers) for url in urls]:
            s = t.result()
            self._size += s.size
            self._real_urls.append(s)

        self._formated_filesize = convert_size(self._size)
        self._path = path
        self._headers = headers
        self._session = session
        self._temp_path = self._path+f".temp_{self._filename}_{self._size}"

        return self

    def start(self) -> DownloaderStream:
        counter = 0
        self._current = 0
        self._founded = 0
        self._downloaded = 0

        self._prog.new(
            self._size,
            self._progressbar_range_text if self._size else self._progressbar_no_range_text,
            "&", "!",
            {
                "FileName": self._filename,
                "FilePath": self._path,
            }
        )
        self._time = time.time()

        makeFile(self._temp_path)
        # try:
        for obj in self._real_urls:
            filename = self._filename+"."+str(counter)
            filesize = obj.size
            pth = self._temp_path+"/"+filename

            if not isFileExist(pth, filesize):
                response = self._session.get(
                    obj.url, headers=self._headers, stream=True)
                f = open(pth, 'wb')
                for bytes in response.iter_content(self._max_size):
                    self._clear_func()
                    if bytes:
                        f.write(bytes)
                        self._current += len(bytes)
                        self._clear_func()
                        self._prog.updateProgress(
                            self._current, {
                                "CurrentFile": filename,
                                "CurrentFileSize": obj.fsize,
                                "Files": str(counter),
                                "FileSize": self._formated_filesize,
                                "TFiles": str(self._number_of_urls),
                                "Downloaded": convert_size(self._downloaded),
                                "Found": convert_size(self._founded)
                            }
                        )
                f.close()
                self._downloaded += filesize
            else:
                self._prog.updateProgress(
                    self._current, {
                        "CurrentFile": obj.name,
                        "CurrentFileSize": obj.fsize,
                        "Files": str(counter),
                        "FileSize": self._formated_filesize,
                        "TFiles": str(self._number_of_urls),
                        "Downloaded": convert_size(self._downloaded),
                        "Found": convert_size(self._founded)
                    }
                )
                self._founded += filesize
                self._current += filesize
            counter += 1

        self._c(counter)
        status = "Success"

        self._last_status = DownloaderStream({
            "status": status,
            "fullpath": self._path+self._filename,
            "time": convertSeconds(int(time.time()-self._time)),
            "path": self._path,
            "filename": self._filename,
            "filesize": self._size,
            "formated_filesize": self._formated_filesize,
            "formated_founded": convert_size(self._founded),
            "founded": self._founded,
            "downloaded": self._downloaded,
            "formated_downloaded": convert_size(self._downloaded)
        })
        return self._last_status

    def _c(self, counter: int):
        self._prog.new(
            self._size,
            self._progressbar_after_text, '&', '!',
            {
                "Status": "Success",
                "FileSize": str(self._size),
                "TLeft": convertSeconds(int(time.time()-self._time)),
                "Downloaded": convert_size(self._downloaded),
                "Founded": convert_size(self._founded),
                "FileName": self._filename,
                "FilePath": self._path
            }
        )
        with open(self._path+self._filename, 'wb') as f:
            for c in range(counter):
                self._clear_func()
                filename = self._filename+'.'+str(c)
                f.write(
                    open(self._temp_path+"/"+filename, 'rb').read()
                )
                self._prog.updateProgress(
                    self._size,
                    {
                        "Reading": f"!R!{c+1}!W!/!G!{counter}"
                    }
                )
            self._clear_func()
        self._prog.endProgress()
        removePath(self._temp_path)

    @property
    def last_status(self) -> DownloaderStream:
        return self._last_status

class _NormalDownload:
    def __init__(self) -> None:
        self._total_downloaded_size = 0
        self._all_status = []
        self._last_status = {}
        self._request_read = MethodRequest()

    def new(self,
            url: str,
            filename=None,
            path=DEFAULT_PATH,
            headers=DEFAULT_HEADERS,
            temp_ext=DEFAULT_TEMP_EXT,
            threads=DEFAULT_THREADS,
            session=DEFAULT_SESSION,
            temp_folder="",
            max_thread_len_no_size=DEFAULT_SIZE_TEMP_FILE,
            max_temp_files=DEFAULT_MAX_TEMP_FILES,
            progressbar=DEFAULT_PROGRESSBAR,
            range_progress_text=DEFAULT_RANGE_TEXT,
            no_range_progress_text=DEFAULT_NO_RANGE_TEXT,
            after_progress_text=DEFAULT_AFTER_DOWNLOAD_TEXT,
            var_sep=DEFAULT_VAR_SEP,
            color_sep=DEFAULT_COLOR_SEP,
            clear_func=DEFAULT_CLEAR,
            check_file_with_size=True,

            save_or_load_data=True) -> Self:
    
        self._save_or_load_data = save_or_load_data
        logger.info("Setting Download Data:-")
        self._server_range_text = range_progress_text
        self._server_no_range_text = no_range_progress_text
        self._after_text = after_progress_text

        self._clear_func = clear_func
        logger.info(f"  -> Clear Function: {clear_func}")
        url_headers = self._request_read.add(url, 'GET', session, headers)
        logger.info(f"  -> Get URL Data\n{url_headers}")
        size = url_headers.size

        self._fsize = convert_size(size)
        if filename == None:
            filename = url_headers.name


        # isTemp = False
        # if save_or_load_data:
        #     if isFileExist("TempData/"+filename,0):
        #         self = pickle.load(open("TempData/"+filename+".temp_yt_joo",'r'))
        #         return None

        logger.info(f"  -> File Size: {self._fsize}")
        logger.info(f"  -> File Name: {filename}")

        if temp_folder == "":
            temp_folder = '.temp_'+encrypt(remove_char(filename))+encrypt(self._fsize)
        logger.info(f"  -> Temp Folder: {temp_folder}")

        self._headers = headers
        self._path = path
        self._tempext = temp_ext
        self._session = session
        self._url = url
        self._filename = filename
        self._temp_folder = temp_folder
        self._temp_ext = temp_ext
        self._temp_path = path+temp_folder
        self._temp_file_path = self._temp_path+'/'+encrypt(self._filename)+".$c"+self._temp_ext


        logger.info(f"  -> Temp File Path: {self._temp_file_path}")

        self._fullpath = path+filename
        logger.info(f"  -> Full Path: {self._fullpath}")

        self._isFileExist = isFileExist(
            self._fullpath, size if check_file_with_size else 0)
        self._max_temp_files = max_temp_files
        logger.info(f"  -> File Found: {self._isFileExist}")

        if url_headers.AcceptRange and size > 0:
            logger.info(f"  -> Accept Range and Size: True")
            self._down_ranges = getLastBytes(
                getRange(size, self._max_temp_files),
                self._max_temp_files,
                temp_ext,
                self._temp_file_path
            )
            logger.info(f"  -> Set Range Data: {self._down_ranges}")
            self._size = size
            self._fsize = convert_size(size)
            self._threads = threads
            logger.info(f"  -> Set Number of Threads: {threads}")
            self._text_progress = self._server_range_text
        else:
            logger.warning(f"  -> Accept Range and Size: False")
            self._max_len = max_thread_len_no_size
            self._size = 0
            self._threads = 0
            self._text_progress = self._server_no_range_text

        self._prog = progressbar
        self._var_sep = var_sep
        self._color_sep = color_sep

        return self

    def __downloadThreadByRange(self, path: str, range: str | int) -> int:
        if type(range) == str:
            chunk = self._session.get(
                self._url, headers={'Range': f'bytes={range}'}, stream=True).content
            open(path, 'wb').write(chunk)
            self._current += len(chunk)
            self._downloaded += len(chunk)
        else:
            self._current += int(range)
            self._founded += int(range)

    def start(self, user_args={}) -> DownloaderStream:
        logger.info("Collecting Data Done...!")
        logger.info('='*50)
        logger.info("Download Start")
        self._current = 0
        self._downloaded = 0
        self._founded = 0
        self._counter_temp_files = 0
        time_ele = time.time()
        status = "found"

        if not self._isFileExist:
            logger.info("File Not Exist, Creating Path")
            makeFile(self._temp_path)
            logger.info("Done Path")

            logger.info("Create New ProgressBar With Args")
            self._prog.new(
                self._size,
                self._text_progress,
                self._var_sep,
                self._color_sep,
                {
                    "FileName": self._filename,
                    "FilePath": self._fullpath,
                    "FileSize": self._fsize
                } | user_args
            )
            logger.info("ProgressBar Start")
            status = self.__startDownload()
            self._prog.endProgress()
            self._prog.new(
                self._size,
                self._after_text,
                self._var_sep,
                self._color_sep,
                {
                    "FileName": self._filename,
                    "FilePath": self._fullpath,
                    "FileSize": self._fsize,
                    "TLeft": convertSeconds(int(time.time()-time_ele)),
                    "Downloaded": convert_size(self._downloaded),
                    "Founded": convert_size(self._founded),
                    "Status": "!G!Success"
                } | user_args
            )
            self._c()
            self._prog.endProgress()
        removePath(self._temp_path)

        _status = {
            "status": status,
            "time": convertSeconds(time.time()-time_ele),
            "fullpath": self._fullpath,
            "path": self._path,
            "filename": self._filename,
            "filesize": self._current,
            "formated_filesize": convert_size(self._current),
            "founded": self._founded,
            "formated_founded": convert_size(self._founded),
            "downloaded": self._downloaded,
            "formated_downloaded": convert_size(self._downloaded)
        }
        self._last_status = DownloaderStream(_status)
        self._all_status.append(self._last_status)
        self._total_downloaded_size += self._current
        
        return self._last_status

    def __startDownload(self) -> str:
        if self._size > 0:
            logger.info("Download With Size")
            return self.__downloadWithSize()
        logger.info("Download Without Size")

        return self.__downloadWithOutSize()

    def __downloadWithSize(self):
        logger.info("Create Thread Object")
        ex = ThreadPoolExecutor(max_workers=self._threads)
        logger.info(f"Number OF Parts: {len(self._down_ranges)}")

        logger.info(f"Add Parts To Thread Object: {ex}")
        for counter in range(len(self._down_ranges)):
            logger.info(
                f"Part {counter}: {self._down_ranges[counter]} -> Start")
            ex.submit(
                self.__downloadThreadByRange(
                    self._temp_file_path.replace("$c", str(counter)),
                    self._down_ranges[counter]
                )
            )

        logger.info("+"*10)
        while self._current < self._size:
            self._clear_func()
            self._prog.updateProgress(
                self._current,
                {
                    "Downloaded": convert_size(self._downloaded),
                    "Found": convert_size(self._founded)
                }
            )
            logger.info(
                f"Downloading: {convert_size(self._downloaded)} - {convert_size(self._current)}")
            time.sleep(0.2)
        self._counter_temp_files = self._max_temp_files
        return "downloaded"

    def __downloadWithOutSize(self,):
        counter = 0
        response = self._session.get(
            self._url,
            headers=self._headers,
            allow_redirects=True,
            stream=True
        )
        for chunk in response.iter_content(chunk_size=1048576):
            self._current += len(chunk)
            self._clear_func()
            self._prog.updateProgress(
                self._current,
                {"Downloaded": convert_size(self._downloaded)}
            )
            if chunk:
                open(
                    self._temp_file_path.replace("$c", str(counter)), 'wb'
                ).write(chunk)
                counter += 1
                self._downloaded += len(chunk)
        self._counter_temp_files = counter
        return "downloaded"

    def _c(self):
        logger.info("Download Complete")
        logger.info("Collecting Files")
        with open(self._fullpath, 'wb') as f:
            for t in range(self._counter_temp_files):
                self._clear_func()
                f.write(
                    open(
                        self._temp_file_path.replace("$c", str(t)),
                        'rb'
                    ).read()
                )
                self._prog.updateProgress(
                    self._current,
                    {
                        "Reading": f"!R!{t+1}!W!/!G!{self._counter_temp_files}   "
                    }
                )
                logger.info(f"Reading: {t+1}/{self._counter_temp_files}   ")
        logger.info("Completed...!")

    @property
    def last_status(self) -> DownloaderStream:
        return self._last_status

    @property
    def all_download_status(self) -> dict:
        return self._all_status


class Downloader:
    def __init__(self) -> None:
        self._status_data = []
        logger.info("Downloader Object Start")

    def new(self,
            url: str | list,
            filename=None,
            path=DEFAULT_PATH,
            headers=DEFAULT_HEADERS,
            temp_ext=DEFAULT_TEMP_EXT,
            threads=DEFAULT_THREADS,
            session=DEFAULT_SESSION,
            temp_folder="",
            max_thread_len_no_size=DEFAULT_SIZE_TEMP_FILE,
            max_temp_files=DEFAULT_MAX_TEMP_FILES,
            progressbar=DEFAULT_PROGRESSBAR,
            range_progress_text=[],
            no_range_progress_text=[],
            after_progress_text=[],
            var_sep=DEFAULT_VAR_SEP,
            color_sep=DEFAULT_COLOR_SEP,
            clear_func=DEFAULT_CLEAR,
            same_file=True,
            max_size=DEFAULT_SIZE_TEMP_FILE,
            check_file_with_size=True) -> _NormalDownload | _MultiDownload:

        logger.info("Start New Function From (Downloader class)")
        if len(url) == 1 and type(url) == list:
            url = url[0]
        logger.info(f"Found:\n {url}")
        logger.info(f"ProgressBar is: {progressbar}")

        # Progress Bar Data
        progressbar_class = EmptyProgressBar()
        if progressbar == 'normal':
            progressbar_class = NormalProgressBar()
        elif progressbar == 'best':
            progressbar_class = TerminalProgressBar()
        else:
            progressbar_class = progressbar()
        logger.info(f"ProgressBar Class is: {progressbar_class}")
        logger.info(f"ProgressBar Type: {progressbar}")

        if type(url) == str:
            logger.info(f"-> Download is Normal")
            logger.info("="*50)

            return _NormalDownload().new(
                url,
                filename,
                path, headers,
                temp_ext,
                threads,
                session,
                temp_folder,
                max_thread_len_no_size,
                max_temp_files,
                progressbar_class,
                range_progress_text if range_progress_text else DEFAULT_RANGE_TEXT,
                no_range_progress_text if no_range_progress_text else DEFAULT_NO_RANGE_TEXT,
                after_progress_text if after_progress_text else DEFAULT_AFTER_DOWNLOAD_TEXT,
                var_sep,
                color_sep,
                clear_func,
                check_file_with_size
            )

        if type(url) == list and same_file:
            return _MultiDownload().new(
                url,
                filename,
                path, headers,
                session,
                threads,
                max_size,
                progressbar_class,
                range_progress_text if range_progress_text else DEFAULT_MULTI_RANGE_TEXT,
                no_range_progress_text if no_range_progress_text else DEFAULT_MULTI_NO_RANGE_TEXT,
                after_progress_text if after_progress_text else DEFAULT_MULTI_AFTER_DOWNLOAD_TEXT,
                # var_sep,
                # color_sep,
                clear_func,
                True,
                check_file_with_size
            )

        if type(url) == list and same_file:
            return _MultiDownload().new()

# url = 'https://www.python.org/ftp/python/3.10.5/python-3.10.5-amd64.exe'

# import pprint
# s = Downloader().new(
#     [url,url],
#     progressbar='normal',
#     same_file=True
# ).start()


# pprint.pprint(vars(s))

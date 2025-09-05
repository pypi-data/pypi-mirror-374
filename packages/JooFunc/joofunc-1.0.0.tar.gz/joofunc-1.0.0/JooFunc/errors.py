import sys
from .colors import fr,fw,fg,fc

class YTE(Exception): pass
class YoutubeLinkError(YTE):
    def __init__(self, url: str):
        msg = f'\r[{fr}-{fw}] {fr}Error: {fc}"{url}"{fr} Not YouTube URL{fw}'
        sys.exit(msg)
        super().__init__(msg)

class ChannelNotExist(YTE):
    def __init__(self, channe_url: str):
        msg = f'\r[{fr}-{fw}] {fr}Error: {fc}"{channe_url}"{fr} Channel Unavailable OR Deleted{fw}'
        sys.exit(msg)
        super().__init__(msg)

class ChannelLinkError(YTE):
    def __init__(self, url) -> None:
        msg = f'\r[{fr}-{fw}] {fr}Error: {fc}"{url}" {fw}-{fr} Invalid Channel URL{fw}'
        sys.exit(msg)
        super().__init__(msg)

class ChannelUrlUnavailable(YTE):
    def __init__(self, url: str):
        msg = f'\r[{fr}-{fw}] {fr}Error: {fc}"{url}" {fw}-{fr} Not Channel URL{fw}'
        sys.exit(msg)
        super().__init__(msg)

class ChannelIDUnavailable(YTE):
    def __init__(self, id) -> None:
        msg = f'\r[{fr}-{fw}] {fr}Error: {fc}"{id}" {fw}-{fr} Channel ID Not Found{fw}'
        sys.exit(msg)
        super().__init__(msg)

class ChannelUserUnavailable(YTE):
    def __init__(self,user) -> None:
        msg = f'\r[{fr}-{fw}] {fr}Error: {fc}"{user}" {fw}-{fr} Channel User Not Found{fw}'
        sys.exit(msg)
        super().__init__(msg)

class ChannelInfoError(YTE):
    def __init__(self, url: str):
        msg = f'\r[{fr}-{fw}] {fr}Error: {fc}"{url}" {fw}-{fr} Can`t Extract Info{fw}'
        sys.exit(msg)
        super().__init__(msg)

class ChannelFileError(YTE):
    def __init__(self, url: str):
        msg = f'\r[{fr}-{fw}] {fr}Error: {fc}"{url}" {fw}-{fr} Can`t Decyrpt File{fw}'
        sys.exit(msg)
        super().__init__(msg)

class ChannelUrlCheck(YTE):
    def __init__(self, url) -> None:
        msg = f'\r[{fr}-{fw}] {fr}Error: {fc}"{url}" {fw}-{fr} Check From Channel URL{fw}'
        sys.exit(msg)
        super().__init__(msg)

class PlayListUrlUnavailable(YTE):
    def __init__(self, id) -> None:
        msg = f'\r[{fr}-{fw}] {fr}Error: {fc}"{id}" {fw}-{fr} PlayList Deleted OR Not Exist{fw}'
        sys.exit(msg)
        super().__init__(msg)

class PlayListIDUnavailable(YTE):
    def __init__(self, id) -> None:
        msg = f'\r[{fr}-{fw}] {fr}Error: {fc}"{id}" {fw}-{fr} Invalid PlayList ID{fw}'
        sys.exit(msg)
        super().__init__(msg)

class PlayListLinkError(YTE):
    def __init__(self, url) -> None:
        msg = f'\r[{fr}-{fw}] {fr}Error: {fc}"{url}" {fw}-{fr} Invalid Playlist URL{fw}'
        sys.exit(msg)
        super().__init__(msg)

class PlayListCheckUrl(YTE):
    def __init__(self, url) -> None:
        msg = f'\r[{fr}-{fw}] {fr}Error: {fc}"{url}" {fw}-{fr} Check From Playlist URL{fw}'
        sys.exit(msg)
        super().__init__(msg)

class PlayListInfoError(YTE):
    def __init__(self, url: str):
        msg = f'\r[{fr}-{fw}] {fr}Error: {fc}"{url}" {fw}-{fr} Can`t Extract Info{fw}'
        sys.exit(msg)
        super().__init__(msg)


class PlayListUrlCheck(YTE):
    def __init__(self, url) -> None:
        msg = f'\r[{fr}-{fw}] {fr}Error: {fc}"{url}" {fw}-{fr} Check From PlayList URL{fw}'
        sys.exit(msg)
        super().__init__(msg)


class PlaylistRangeError(YTE):
    def __init__(self, r) -> None:
        msg = f'\r[{fr}-{fw}] {fr}Error: {fc}"{str(r)}" {fw}-{fr} Invalid Range{fw}'
        sys.exit(msg)
        super().__init__(msg)


class VidoeIDUnavailable(YTE):
    def __init__(self, url) -> None:
        msg = f'\r[{fr}-{fw}] {fr}Error: {fc}"{url}" {fw}-{fr} Invalid Video ID{fw}'
        sys.exit(msg)
        super().__init__(msg)

class VideoUrlUnavailable(YTE):
    def __init__(self, url) -> None:
        msg = f'\r[{fr}-{fw}] {fr}Error: {fc}"{url}" {fw}-{fr} Invalid Video URL{fw}'
        sys.exit(msg)
        super().__init__(msg)

class VideoUrlCheck(YTE):
    def __init__(self, url) -> None:
        msg = f'\r[{fr}-{fw}] {fr}Error: {fc}"{url}" {fw}-{fr} Check From Video URL{fw}'
        sys.exit(msg)
        super().__init__(msg)

class APIError(YTE):
    def __init__(self,api="") -> None:
        if(api == ''): 
            super().__init__()
            return
        msg = f'\r[{fr}-{fw}] {fr}Error: {fc}"{api}" {fw}-{fr} Please, Change Api {fw}'
        sys.exit(msg)
        super().__init__(msg)

class NoSpaceError(YTE):
    def __init__(self) -> None:
        msg = f'\r[{fr}-{fw}] {fr}Error: {fc} No Space Left {fw}'
        sys.exit(msg)
        super().__init__(msg)


class RapidApiError(YTE):
    def __init__(self,api="") -> None:
        if(api == ''): 
            super().__init__()
            return
        msg = f'\r[{fr}-{fw}] {fr}Error: {fc}"{api}" {fw}-{fr} Please, Change Rapid Api {fw}'
        sys.exit(msg)
        super().__init__(msg)
class TooManyRequestsError(YTE):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)

class YTVResError(YTE):
    def __init__(self, res) -> None:
        msg = f'\r[{fr}-{fw}] {fr}Error: {fc}"{res}" {fw}-{fr} Unavalible Resolution {fw}'
        sys.exit(msg)
        super().__init__(msg)

class DownloadError(YTE):
    def __init__(self, res) -> None:
        msg = f'\r[{fr}-{fw}] {fr}Error: {fr}Download Not Complete {fw}'
        sys.exit(msg)
        super().__init__(msg)

class DownloadTooSlow(YTE):
    def __init__(self, res) -> None:
        msg = f'\r[{fr}-{fw}] {fr}Error: {fr}{res}{fr} Speed Too Slow - Renew Link{fw}'
        sys.exit(msg)
        super().__init__(msg)

class FileError(YTE):
    def __init__(self, name) -> None:
        msg = f'\r[{fr}-{fw}] {fr}Error: "{fg}{name}{fr}" {fr}Can`t Extract File Info{fw}'
        super().__init__(msg)

class SettingsError(YTE):
    def __init__(self, name) -> None:
        msg = f'\r[{fr}-{fw}] {fr}Error: "{fg}{name}{fr}" {fr}Please , Fix Setting File{fw}'
        super().__init__(msg)


class ConnectError(YTE):
    def __init__(self,id) -> None:
        msg = f'\r[{fr}-{fw}] {fr}Error: "{fg}{id}{fr}" {fr}Please , Connect To Website First..!{fw}'
        sys.exit(msg)
        super().__init__(msg)


class ResNotFoundError(YTE):
    def __init__(self,res) -> None:
        msg = f'\r[{fr}-{fw}] {fr}Error: "{fg}{res}{fr}" {fr}Res Not Found{fw}'
        sys.exit(msg)
        super().__init__(msg)


class UrlNotFoundError(YTE):
    def __init__(self,res) -> None:
        msg = f'\r[{fr}-{fw}] {fr}Error: "{fg}{res}{fr}" {fr}Invalid Stream url{fw}'
        sys.exit(msg)
        super().__init__(msg)


class Y2ComConnectError(YTE):
    def __init__(self) -> None:
        msg = f'\r[{fr}-{fw}] {fr}Error{fw}: {fr}Can`t Connect To Y2mate.com Server{fw}'
        sys.exit(msg)
        super().__init__(msg)


class Y2IsConnectError(YTE):
    def __init__(self) -> None:
        msg = f'\r[{fr}-{fw}] {fr}Error{fw}: {fr}Can`t Connect To Y2mate.is Server{fw}'
        sys.exit(msg)
        super().__init__(msg)


class YDLConnectionError(YTE):
    def __init__(self) -> None:
        msg = f'\r[{fr}YDL{fw}] {fr}Error{fw}: Can`t Extract Data with YDL{fw}'
        sys.exit(msg)
        super().__init__(msg)


class InternetConnectionError(YTE):
    def __init__(self,url:str) -> None:
        msg = f'\r[{fr}-{fw}] {fr}Error{fw}: Check From Internet Connection{fw}'
        sys.exit(msg)
        super().__init__(msg)

class InternetTimeOut(YTE):
    def __init__(self,url:str) -> None:
        msg = f'\r[{fr}-{fw}] {fr}Error{fw}: Connection TimeOut{fw}'
        sys.exit(msg)
        super().__init__(msg)

class CheckFromUrlConnection(YTE):
    def __init__(self,url:str) -> None:
        msg = f'\r[{fr}-{fw}] {fr}Error{fw}: "{url}" Check From Url{fw}'
        sys.exit(msg)
        super().__init__(msg)



class FileNotFoundError(YTE):
    def __init__(self,path:str) -> None:
        msg = f'\r[{fr}-{fw}] {fr}Error{fw}: "{path}" Can`t Find File Path{fw}'
        sys.exit(msg)
        super().__init__(msg)

class IDNotFoundError(YTE):
    def __init__(self,id:str) -> None:
        msg = f'\r[{fr}-{fw}] {fr}Error{fw}: "{id}" Video ID Not Found{fw}'
        sys.exit(msg)
        super().__init__(msg)
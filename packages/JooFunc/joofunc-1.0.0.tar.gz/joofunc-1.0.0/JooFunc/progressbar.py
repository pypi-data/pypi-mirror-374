from .func import (
    convertSeconds,convert_size,findall_reg,
    time,Self
)
from .colors import NormalProgress, TerminalControllerProgress

def format_progress_string(text:str|list,args:dict,sep:str) -> list:
    counter=0
    if type(text)==str: text = [text]
    for i in text:
        for key in findall_reg(f"\{sep}(.*?)\{sep}",i,True):
            if key in args:
                text[counter] = text[counter].replace(sep+key+sep,args[key])
        counter+=1
    return text

class TerminalProgressBar:
    def new(self,total:int,text:list|str,var_sep='$',color_sep='%',user_args_constant={}) -> Self:
        """
            Signs:\n
            var_sep = '$' for variables\n
            color_sep = '%' for colors\n
            OR u can Put Your but Note not the SAME
            ==========================================\n
            $TimeLeft$ print Time Left\n
            $TimeElep$ print Elepesed Time\n
            $Speed$ print Internet Speed\n
            $Percent$ print Percent in String\n
            $Current$ print Current Value in String\n
            $FCurrent$ print Formated Current Bytes in String\n
            $Total$ print Total Bytes in String\n
            $FTotal$ print Formated Total Bytes in String\n
            $ProgressData$ print ('Current'/'Total')\n
            $FProgressData$ print Formated ('formated Current'/'formated Total')\n
            $ProgressBar$ print Progress Bar '━━━━━━━━━━━━━━'\n
            $userPress$ print what user enter\n
            $pause_resume_msg$ print pause or resume input msg\n
            $stopmsg$ print stop msg\n
            ============================================\n
            Please Note:\n
                -:user_args:-
            Add Any Values You Want\n
            Add Replace it with value name\n
            $Any Value You Want$ set Same Name in Var\n
            ============================================
        """
        self._console = TerminalControllerProgress()
        self.__start_speed = time.time()
        self._text = text
        self._total = total
        self._c_sep = color_sep
        self._v_sep = var_sep
        self._constant_args = user_args_constant
        return self

    def updateProgress(self,current:int,user_args={}) -> None:
        total = self._total
        add_vars = user_args
        if current==0: current=1
        current_time = int(abs(time.time()-self.__start_speed))
        try: d = int(current / current_time)
        except: d = 1
        speed = convert_size(d)
        fcurrent = convert_size(current)
        
        if total==0:
            total = 1
            progress_bar = f"%G%{'━' * 20}%W%"
            perc = "0.00"
            ftotal = "0"
            bytes_data = f'%R%{current}%W%'
            formated_bytes_data = f'%R%{fcurrent}%W%'
            time_ele = convertSeconds(int(current/(20*current)))
        else:
            done = int(20 * current / total)
            progress_bar = f"%G%{'━' * done}%R%{'━' * (20-done)}%W%"
            perc = format((current / total) * 100,".2f")
            ftotal = convert_size(total)
            bytes_data = f'%R%{current}%W% / %G%{total}%W%'
            formated_bytes_data = f'%R%{fcurrent}%W% / %G%{ftotal}%W%'
            try: time_ele = convertSeconds(int((total-current)/d))
            except: time_ele = "00:00:01"
        #if(d<=100000): raise DownloadTooSlow(speed)
        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ ░

        add_vars["Current"] = current
        add_vars["FCurrent"] = fcurrent
        add_vars["Total"] = total
        add_vars["FTotal"] = ftotal
        add_vars["TimeLeft"] = convertSeconds(current_time)
        add_vars["TimeElep"] = time_ele
        add_vars["Speed"] = speed
        add_vars["Percent"] = perc+" %"
        add_vars["ProgressData"] = bytes_data.replace('%',self._c_sep)
        add_vars["FProgressData"] = formated_bytes_data.replace('%',self._c_sep)
        add_vars["ProgressBar"] = progress_bar.replace('%',self._c_sep)

        self._console.add_string(
            format_progress_string(self._text[:],add_vars|self._constant_args,self._v_sep),
            color_sep=self._c_sep
        )
        self._console.print()
    def get_pressed(self) -> str: return self._console.get_input()
    def endProgress(self): self._console.end()

class NormalProgressBar:
    def new(self,total:int,text:list|str,var_sep='$',color_sep='%',user_args_constant={}) -> Self:
        """
            Signs:\n
            var_sep = '$' for variables\n
            color_sep = '%' for colors\n
            OR u can Put Your but Note not the SAME
            ==========================================\n
            $TimeLeft$ print Time Left\n
            $TimeElep$ print Elepesed Time\n
            $Speed$ print Internet Speed\n
            $Percent$ print Percent in String\n
            $Current$ print Current Value in String\n
            $FCurrent$ print Formated Current Bytes in String\n
            $Total$ print Total Bytes in String\n
            $FTotal$ print Formated Total Bytes in String\n
            $ProgressData$ print ('Current'/'Total')\n
            $FProgressData$ print Formated ('formated Current'/'formated Total')\n
            $ProgressBar$ print Progress Bar '━━━━━━━━━━━━━━'\n
            $userPress$ print what user enter\n
            $pause_resume_msg$ print pause or resume input msg\n
            $stopmsg$ print stop msg\n
            ============================================\n
            Please Note:\n
                -:user_args:-
            Add Any Values You Want\n
            Add Replace it with value name\n
            $Any Value You Want$ set Same Name in Var\n
            ============================================
        """
        self._console = NormalProgress()
        self.__start_speed = time.time()
        self._text = text
        self._total = total
        self._c_sep = color_sep
        self._v_sep = var_sep
        self._constant_args = user_args_constant
        return self

    def updateProgress(self,current:int,user_args={}) -> None:
        total = self._total
        add_vars = user_args
        if current==0: current=1
        current_time = int(abs(time.time()-self.__start_speed))
        try: d = int(current / current_time)
        except: d = 1
        speed = convert_size(d)
        fcurrent = convert_size(current)
        
        if total==0:
            total = 1
            progress_bar = f"%G%{'━' * 20}%W%"
            perc = "0.00"
            ftotal = "0"
            bytes_data = f'%R%{current}%W%'
            formated_bytes_data = f'%R%{fcurrent}%W%'
            time_ele = convertSeconds(int(current/(20*current)))
        else:
            done = int(20 * current / total)
            progress_bar = f"%G%{'━' * done}%R%{'━' * (20-done)}%W%"
            perc = format((current / total) * 100,".2f")
            ftotal = convert_size(total)
            bytes_data = f'%R%{current}%W% / %G%{total}%W%'
            formated_bytes_data = f'%R%{fcurrent}%W% / %G%{ftotal}%W%'
            try: time_ele = convertSeconds(int((total-current)/d))
            except: time_ele = "00:00:01"
        #if(d<=100000): raise DownloadTooSlow(speed)
        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ ░

        add_vars["Current"] = current
        add_vars["FCurrent"] = fcurrent
        add_vars["Total"] = total
        add_vars["FTotal"] = ftotal
        add_vars["TimeLeft"] = convertSeconds(current_time)
        add_vars["TimeElep"] = time_ele
        add_vars["Speed"] = speed
        add_vars["Percent"] = perc+" %"
        add_vars["ProgressData"] = bytes_data.replace('%',self._c_sep)
        add_vars["FProgressData"] = formated_bytes_data.replace('%',self._c_sep)
        add_vars["ProgressBar"] = progress_bar.replace('%',self._c_sep)

        self._console.add_string(
            format_progress_string(self._text[:],add_vars|self._constant_args,self._v_sep),
            color_sep=self._c_sep
        )
        self._console.print()

    def endProgress(self):
        self._text = []

class EmptyProgressBar:
    def __init__(self) -> None:
        pass
    def new(self,*args,**arg):
        pass
    def updateProgress(self,*arg,**args):
        pass
    def endProgress(self):
        pass

# s = NormalProgressBar().new(0,
# [
#     "          !G!-.....!G!After Download Page!R!.....-",
#     "-"*50,
#     "!B!Download Status.......!W!: &status&",
#     "-"*50,
#     "!Y!File Name.........!W!: !G!&FileName&",
#     "!Y!File Path.........!W!: !G!&FilePath&",
#     "!Y!Current FileName..!W!: !G!&FileDownload&",
#     "!Y!Current FileName..!W!: !G!&fd&",
#     "!Y!Total!W!: !G!&FProgressData&",
#     "-"*50,
#     "!R!Please Wait........",
#     "!G!Reading Temp Files!W!: !Y!&tempFiles&!W!/&totalFiles&",
#     "-"*50
# ],
# '&','!',{"fd":"none"})

# i = 10
# while(i<=1000000):
#     clear()
#     s.updateProgress(i)
#     i+=100
#     time.sleep(1)
# s.endProgress()


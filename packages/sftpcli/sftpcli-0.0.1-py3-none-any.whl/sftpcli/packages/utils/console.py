from colorama import Fore, Style, init
import sys

init(autoreset=True)


class Console:
    @classmethod
    def __print(cls, color, symbol, *args):
        message = " ".join(args)
        output = f"{color}{symbol} {message}"
        sys.stdout.write(f"{output}\n")
        return output

    @classmethod
    def success(cls, *args):
        return cls.__print(Fore.LIGHTGREEN_EX, "[✓]", *args)

    @classmethod
    def error(cls, *args):
        return cls.__print(Fore.LIGHTRED_EX, "[✗]", *args)
    
    
    @classmethod
    def info(cls, *args):
        return cls.__print(f"{Fore.LIGHTWHITE_EX}{Style.BRIGHT}", "[i]", *args)
    
    
    @classmethod
    def warn(cls, *args):
        return cls.__print(f"{Fore.LIGHTYELLOW_EX}{Style.BRIGHT}", "[!]", *args)

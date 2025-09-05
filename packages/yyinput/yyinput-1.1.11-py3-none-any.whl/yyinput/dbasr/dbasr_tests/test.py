

import os 
import sys
# for path in sys.path:
#     print(path)


from yyinput.dbasr import DBASR


if __name__ == "__main__":
    dbasr = DBASR()
    res=dbasr._is_terminal_focused()
    print(res)


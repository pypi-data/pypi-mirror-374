from ui.app import HanaDbExolorer
from db import DBCleanup

def main() -> None:
    HanaDbExolorer().run()
    DBCleanup()

if __name__ == "__main__":
    main()
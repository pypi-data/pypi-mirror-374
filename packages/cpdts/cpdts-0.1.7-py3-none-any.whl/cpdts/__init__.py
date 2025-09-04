

import fire 
from .fire_project import fire_create 



class ENTRY(object):
    """主入口类"""
    
    def fire(self,name) -> None:
        fire_create(name)

    




def main() -> None:
    """Main function to run the CLI."""
    fire.Fire(ENTRY)


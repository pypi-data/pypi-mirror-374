

import fire 



class ENTRY(object):
    
    def hello(self):
        print("hello")


def main() -> None:
    """Main function to run the CLI."""
    fire.Fire(ENTRY)
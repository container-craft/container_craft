from abc import ABC, abstractmethod
import argparse

class McPkgAbstractCommands(ABC):
    
    @abstractmethod
    def args(self, subparser: argparse.ArgumentParser):
        """
        This method should define the arguments for the specific command. 
        example:
        subparser.add_argument("-p", "--provider", help="Provider to search (modrith(default), curse_forge, hangar, local)", type=str, default="modrith
        """
        pass
    
    @abstractmethod
    def run(self, subparser: argparse.Namespace) -> bool:
        """
        Run the command and return True if successful, False otherwise.
        this method should handle the logic of the command.
        example:
        if not any(vars(subparser).values()):
            subparser.print_help()
            return False    
        """
        pass

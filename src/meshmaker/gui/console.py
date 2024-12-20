from qtconsole.rich_jupyter_widget import RichJupyterWidget
from qtconsole.inprocess import QtInProcessKernelManager

class InteractiveConsole(RichJupyterWidget):
    '''
    A console widget that can execute Python code and display rich output.
    '''
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # Create kernel manager and kernel
        kernel_manager = QtInProcessKernelManager()
        kernel_manager.start_kernel()
        
        # Create kernel client
        kernel_client = kernel_manager.client()
        kernel_client.start_channels()
        
        # Set up the console with the kernel
        self.kernel_manager = kernel_manager
        self.kernel_client = kernel_client
        
        # Configure appearance
        self.syntax_style = 'solarized-dark'
        self.set_default_style(colors='linux')



    def print(self, message):
        '''
        Print a message to the console output.

        Args:
            message (str): The string message to display in the console.
        '''
        if not isinstance(message, str):
            raise ValueError("The message must be a string.")
        
        # Use the kernel to execute a Python print command
        self.kernel_client.execute(f'print("{message}")')
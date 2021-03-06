## Installing Jupyter, Python Module, quick walk-through

Jupyter is an interactive programming environment that runs in the browser. Jupyter can support multiple programming languages but we will only be using it for Python 3.

To run the OpenTrons SDK you will need to ensure you have Python 3 installed. We recommend you install [Anaconda](https://www.continuum.io/downloads) before going any further, this will install Python 3 for you. When installing Anaconda we recommend you use the `Graphical Installer` for `Python3.5`.

After Anaconda and Python 3 are installed, you can get started installing Jupyter by following the official [Jupyter Installation Guide](http://jupyter.readthedocs.io/en/latest/install.html).

If you have finished setting up Python 3 and you have finished going through the Jupyter installation guide it is now time to run Jupyter.


## Launch Jupyter Notebook App:

1. Click on spotlight, type `terminal` to open a terminal window.
2. Create and Enter the startup folder by typing `mkdir some_folder_name && cd some_folder_name`.
3. Type jupyter notebook to launch the Jupyter Notebook App (it will appear in a new browser window or tab).


## Programming in Jupyter Notebook: Hello World!

When the Jupyter Notebook App is launched on your browser, follow these steps to open a `Notebook`

* Navigate towards the `New` dropdown menu button towards the top right hand side of the screen Jupyter Notebook App. Click the `New` menu button and scroll down and click `python [conda root]`.

A new tab should open in your browser and you should have an empty text box.

* Type `print('hello world')` in the text box and scroll to the top menu bar and press they `play button >| ` to execute the code in the text box. This will cause Jupyter to execute the code in the text box and return you the computed result, which should be 'Hello World'.

After running the aforementioned step a new text box will appear for you to write code in. We will use this text box to install the Opentrons API.

* Copy paste this statement into the new text box `!pip install --upgrade git+git://github.com/OpenTrons/opentrons_sdk.git@master#egg=opentrons`

The should execute the installation process of the Opentrons API. The last line of this installation process should say `Successfully installed opentrons-sdk-1.0`

If you made it this far without any errors then you are done! You should treat yourself well tonight and celebrate your successes generously!

If you want to learn more about Jupyter Notebook Navigation [check this out](http://nbviewer.jupyter.org/github/jupyter/notebook/blob/master/docs/source/examples/Notebook/Notebook%20Basics.ipynb):

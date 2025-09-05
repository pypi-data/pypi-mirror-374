# pybreathe: a python package for respiratory air flow rates analysis

## Get started

First of all, we highly recommend that you install [miniconda](https://www.anaconda.com/docs/getting-started/miniconda/install) on your machine.

To set up the virtual environment required for respiratory flow analysis, open **Anaconda prompt** and please run (only the first time):

```bash
$ conda create --name pybreathe
$ conda activate pybreathe
$ pip install pybreathe
$ conda install conda-forge::jupyterlab
```

If you encounter an error stating that `pip` cannot be found, then run: `$ conda install anaconda::pip`

Then, every time you want to analyze data, open **Anaconda prompt** and activate the virtual environment with:

```bash
$ conda activate pybreathe
```

(do not reinstall `pybreathe` each time)

To get started with `pybreathe` API, we strongly recommend that you use and refer to the example scripts. The package comes with [example scripts](https://github.com/tcoustillet/pybreathe/tree/main/examples) based on simulated breathing signals that are representative of the data that can be collected experimentally. They explain the milestones involved in carrying out an analysis (feature extraction) and they supply useful documentation.

Run the example script (or any other) with:

```bash
$ jupyter lab example.ipynb
```

> /!\ You must either be in the same directory as your .ipynb file, or specify the absolute path. You can either move to your directory with the `$ cd` command (*e.g.*, `$ cd algo/test`) or you can type the command : `$ jupyter lab ` and then drag and drop your file into the terminal. This will automatically copy the absolute path of your file: `$ jupyter lab '/home/tcoustillet/algo/test/example.ipynb'`

Once the example notebook is open, you can run the cells one by one and understand how `pybreathe` works. To analyse your own data, create a new notebook and refer to the examples for how the API works.

Finally, to quit the analysis, please follow these steps:

- Right clic on your .ipynb file in the tree, then "Shut Down Kernel"
- Clic on "File", the "Shut Down"
- When you regain control in your terminal, run:

```bash
$ conda deactivate
```

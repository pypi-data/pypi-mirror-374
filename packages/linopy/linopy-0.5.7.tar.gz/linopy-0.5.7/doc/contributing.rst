
============
Contributing
============

We welcome anyone interested in contributing to this project,
be it with new ideas, suggestions, by filing bug reports or
contributing code.

You are invited to submit pull requests / issues to our
`Github repository <https://github.com/pypsa/linopy>`_.

For linting, formatting and checking your code contributions
against our guidelines (e.g. we use `Black <https://github.com/psf/black>`_ as code style
and use `pre-commit <https://pre-commit.com/index.html>`_:

1. Installation ``conda install -c conda-forge pre-commit`` or ``pip install pre-commit``
2. Usage:
    * To automatically activate ``pre-commit`` on every ``git commit``: Run ``pre-commit install``
    * To manually run it: ``pre-commit run --all``

Contributing examples
=====================

Nice examples are always welcome.

You can even submit your `Jupyter notebook`_ (``.ipynb``) directly
as an example.
For contributing notebooks (and working with notebooks in `git`
in general) we have compiled a workflow for you which we suggest
you follow:

* Locally install `this precommit hook for git`_

This obviously has to be done only once.
The hook checks if any of the notebooks you are including in a commit
contain a non-empty output cells.

Then for every notebook:

1. Write the notebook (let's call it ``foo.ipynb``) and place it
   in ``examples/foo.ipynb``.
2. Ask yourself: Is the output in each of the notebook's cells
   relevant for to example?

    * Yes: Leave it there.
      Just make sure to keep the amount of pictures/... to a minimum.
    * No: Clear the output of all cells,
      e.g. `Edit -> Clear all output` in JupyterLab.

3. Provide a link to the documentation:
   Include a file ``foo.nblink`` located in ``doc/examples/foo.nblink``
   with this content

   .. code-block:
        {
            'path' : '../../examples/foo.ipynb'
        }

    Adjust the path for your file's name.
    This ``nblink`` allows us to link your notebook into the documentation.
4. Link your file in the documentation:

   Either

    * Include your ``examples/foo.nblink`` directly into one of
      the documentations toctrees; or
    * Tell us where in the documentation you want your example to show up

5. Commit your changes.
   If the precommit hook you installed above kicks in, confirm
   your decision ('y') or go back ('n') and delete the output
   of the notebook's cells.
6. Create a pull request for us to accept your example.

The support for the the ``.ipynb`` notebook format in our documentation
is realised via the extensions `nbsphinx`_ and `nbsphinx_link`_.

.. _Jupyter notebook: https://jupyter-notebook-beginner-guide.readthedocs.io/en/latest/what_is_jupyter.html
.. _this precommit hook for git: https://jamesfolberth.org/articles/2017/08/07/git-commit-hook-for-jupyter-notebooks/
.. _nbsphinx: https://nbsphinx.readthedocs.io/en/0.4.2/installation.html
.. _nbsphinx_link: https://nbsphinx.readthedocs.io/en/latest/

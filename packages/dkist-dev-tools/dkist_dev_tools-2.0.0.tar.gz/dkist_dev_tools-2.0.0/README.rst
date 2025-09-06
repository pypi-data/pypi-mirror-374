dkist-dev-tools
===============

|codecov|

Overview
---------
This repo contains a suite of tools that will hopefully be helpful to developers of the `dkist-processing-*` stack.
More tools will be added as we learn more about how we use them, but if you know of something you want then please add it!

Install
-------

Using pipx (recommended)
########################

By using pipx you can install `ddt` with a specific python version that can still be run from anywhere on your system.
First, find out the path to a python version that matches what is used by the DKIST processing workers. This may be your
system-level python, but, more likely, it will be in some other virtual environment. I recommend creating an environment
*just* to provide a correct python version for `dkist-dev-tools`.

For example, using conda:

.. code-block:: bash

    conda create -y -n dkist-dev-tools python=3.12
    conda activate dkist-dev-tools
    pipx install dkist-dev-tools --python $(which python) --include-deps

After running this commands you should have access to the `ddt` command line function from *any* terminal and environment,
not just the conda env you created. Neat!

**NOTE:** Since `dkist-dev-tools` v1.2.0 the `--include-deps` option is required to get a working installation when
using pipx. Without it the necessary `towncrier` binary will not be made available for the changelog functionality.


Using base pip
##############

Probably do this in a virtual environment that matches the python version used by the DKISTDC.

.. code-block:: bash

    pip install dkist-dev-tools

Shell Completion
################

If you want shell completion then add the following to your shell rc file:

bash
^^^^

Add to ``~/.bashrc``

.. code-block:: bash

    eval "$(_DDT_COMPLETE=bash_source ddt)"

zsh
^^^

Add to ``~/.zshrc``

.. code-block:: zsh

    eval "$(_DDT_COMPLETE=zsh_source ddt)"


Tools
-----

The top-level command is called `ddt`. The subcommands are shown below

Freeze Dependencies
###################

.. code-block:: bash

    ddt freeze [-d project_dir] VERSION


This command prepares for a new version of a project by freezing a complete set of dependencies under the "frozen" pip extra
in pyproject.toml. This allows airflow workers (or human users) to install with ``pip install dkist-processing-INSTRUMENT[frozen]``
and always get the exact same environment for a given version.

There is no need to worry about your current python environment (besides the version); a fresh temporary environment is
used to install the project and inspect the dependencies. This temporary environment is deleted when we're done with it.

After this script is run the pyproject.toml file in the ``project_dir`` will be updated in two places:

* The ``project.optional-dependencies.frozen`` node will either be created or updated to show the full list of dependencies
  in the as-built environment.

* The ``tool.dkist-dev-tools`` node will be either created or updated to show when the command was run and with what version.
  This information is used to check the project prior to building a new release on Bitbucket.

You will have to commit these changes yourself.

Render Changelog(s)
###################

.. code-block:: bash

    ddt changelog [-s] VERSION

This command uses `towncrier` to render an update to CHANGELOG from fragments in the changelog fragment directory.
If science fragments also exist then the SCIENCE_CHANGELOG will also be updated.

By default a draft of the changes will be shown and the user asked to confirm that it looks correct.
Passing the ``-s`` option skips this step.

All changes will need to be manually committed.

Check Release Conditions
########################

.. code-block:: bash

    ddt check

This group of commands is used to check that the main commands were run properly for the current version about to be released.

Check Dependencies Frozen
^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: bash

    ddt check freeze [-d project_dir]

Confirm that the version frozen into a pyproject.toml file matches the current version. The current version comes first
from the BITBUCKET_TAG environmental variable. If this is not set then the version is inferred from a "v*" git tag on HEAD.

Check Changelog Status
^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: bash

    ddt check changelog

If git HEAD is a tagged version then check that the changelog has been correctly rendered and no fragments remain.
Otherwise run `towncrier check`, which makes sure fragments exist if there is a diff between the current branch and origin/main.


.. |codecov| image:: https://codecov.io/bb/dkistdc/dkist-dev-tools/graph/badge.svg?token=Y0Q0CTLZX5
   :target: https://codecov.io/bb/dkistdc/dkist-dev-tools

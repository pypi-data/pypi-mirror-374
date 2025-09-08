
.. image:: https://readthedocs.org/projects/pygithub-mate/badge/?version=latest
    :target: https://pygithub-mate.readthedocs.io/en/latest/
    :alt: Documentation Status

.. image:: https://github.com/MacHu-GWU/pygithub_mate-project/actions/workflows/main.yml/badge.svg
    :target: https://github.com/MacHu-GWU/pygithub_mate-project/actions?query=workflow:CI

.. image:: https://codecov.io/gh/MacHu-GWU/pygithub_mate-project/branch/main/graph/badge.svg
    :target: https://codecov.io/gh/MacHu-GWU/pygithub_mate-project

.. image:: https://img.shields.io/pypi/v/pygithub-mate.svg
    :target: https://pypi.python.org/pypi/pygithub-mate

.. image:: https://img.shields.io/pypi/l/pygithub-mate.svg
    :target: https://pypi.python.org/pypi/pygithub-mate

.. image:: https://img.shields.io/pypi/pyversions/pygithub-mate.svg
    :target: https://pypi.python.org/pypi/pygithub-mate

.. image:: https://img.shields.io/badge/✍️_Release_History!--None.svg?style=social&logo=github
    :target: https://github.com/MacHu-GWU/pygithub_mate-project/blob/main/release-history.rst

.. image:: https://img.shields.io/badge/⭐_Star_me_on_GitHub!--None.svg?style=social&logo=github
    :target: https://github.com/MacHu-GWU/pygithub_mate-project

------

.. image:: https://img.shields.io/badge/Link-API-blue.svg
    :target: https://pygithub-mate.readthedocs.io/en/latest/py-modindex.html

.. image:: https://img.shields.io/badge/Link-Install-blue.svg
    :target: `install`_

.. image:: https://img.shields.io/badge/Link-GitHub-blue.svg
    :target: https://github.com/MacHu-GWU/pygithub_mate-project

.. image:: https://img.shields.io/badge/Link-Submit_Issue-blue.svg
    :target: https://github.com/MacHu-GWU/pygithub_mate-project/issues

.. image:: https://img.shields.io/badge/Link-Request_Feature-blue.svg
    :target: https://github.com/MacHu-GWU/pygithub_mate-project/issues

.. image:: https://img.shields.io/badge/Link-Download-blue.svg
    :target: https://pypi.org/pypi/pygithub-mate#files


Welcome to ``pygithub_mate`` Documentation
==============================================================================
.. image:: https://pygithub-mate.readthedocs.io/en/latest/_static/pygithub_mate-logo.png
    :target: https://pygithub-mate.readthedocs.io/en/latest/

pygithub_mate is a user-friendly Python library that builds upon PyGithub to provide both simple wrappers and sophisticated workflow automation for GitHub operations. While PyGithub offers comprehensive access to the GitHub API, pygithub_mate focuses on making common tasks more intuitive and reliable through carefully designed abstractions and intelligent workflows.

The library offers two types of functionality: direct API wrappers that simplify common operations like tag and release creation, and advanced workflow methods that handle complex multi-step processes automatically. For example, while creating a simple tag is straightforward, the put_tag_on_commit method intelligently handles scenarios like checking if a tag already exists, whether it points to the correct commit, and automatically cleaning up and recreating tags when necessary.

Built around the command pattern, pygithub_mate encapsulates GitHub operations as self-contained, configurable objects with comprehensive logging and error handling. This design makes it particularly valuable for automation scripts, CI/CD pipelines, and release management workflows where reliability and visibility into the process are essential.


.. _install:

Install
------------------------------------------------------------------------------

``pygithub_mate`` is released on PyPI, so all you need is to:

.. code-block:: console

    $ pip install pygithub-mate

To upgrade to latest version:

.. code-block:: console

    $ pip install --upgrade pygithub-mate

dkist-processing-core
=====================

|codecov|

Overview
--------
The dkist-processing-core package provides an abstraction layer between the dkist data processing code, the workflow
engine that supports it (Airflow), and the logging infrastructure. By providing the abstraction layer to Airflow
specifically a versioning system is implemented.

.. image:: https://bitbucket.org/dkistdc/dkist-processing-core/raw/faf0c57f2155d03889fcd54bc1676a8a219f6ee3/docs/auto_proc_brick.png
  :width: 600
  :alt: Core, Common, and Instrument Brick Diagram

There are 4 main entities which implement the abstraction which are described below.

*Task* : The Task defines the interface used by a processing pipeline for a step in a workflow.
By conforming to this interface (i.e. subclassing) the processing pipelines can remain agnostic of how the tasks will ultimately be run.
The Task additionally implements some methods that should be global for all dkist processing tasks based on the infrastructure it will run on (e.g. application performance monitoring infrastructure).

*Node* : The job of the Node is to translate a Task into code that can instantiate that task.
Instantiations of a Task can vary depending on the target environment e.g. a virtual environment with a BashOperator for Airflow vs. straight python for a notebook.

*Workflow* : The Workflow defines the interface used by the processing pipeline to chain tasks together in a directed graph.
The Workflow transforms this graph into the workflow engine format by providing any wrapping boilerplate, task ordering, and selecting the appropriate Node instantiation.

*Build Utils* : The Build Utils are the capstone layer which aims to ease the transformation process for multiple workflows at a time during a processing pipeline's build process.


Usage
-----
The Workflow and Task are the primary objects used by client libraries.
The Task is used as a base class and the subclass must at a minimum implement run.
A Workflow is used to give the tasks an order of execution and a name for the flow.

.. code-block:: python

    from dkist_processing_core import TaskBase
    from dkist_processing_core import Workflow

    # Task definitions
    class MyTask1(TaskBase):
        def run(self):
            print("Running MyTask1")


    class MyTask2(TaskBase):
        def run(self):
            print("Running MyTask2")

    # Workflow definition
    # MyTask1 -> MyTask2
    w = Workflow(process_category="My", process_name="Workflow", workflow_package=__package__, workflow_version="dev")
    w.add_node(MyTask1, upstreams=None)
    w.add_node(MyTask2, upstreams=MyTask1)


Using dkist-processing-core for data processing with Airflow involves a project structure and
build process that results in code artifacts deployed to `PyPI <https://pypi.org/project/dkist-processing-core/>`_ and a
zip of workflow artifacts deployed to artifactory.

.. image:: https://bitbucket.org/dkistdc/dkist-processing-core/raw/faf0c57f2155d03889fcd54bc1676a8a219f6ee3/docs/auto-proc-concept-model.png
  :width: 600
  :alt: Build Artifacts Diagram

The client dkist data processing libraries should implement a structure and build pipeline using `dkist-processing-test <https://bitbucket.org/dkistdc/dkist-processing-test/src/main/>`_
as an example.  The build pipelines for a client repo can leverage the `build_utils <dkist_processing_core/build_utils.py>`_ for test and export.

Specifically for Airflow, the resulting deployment has the versioned workflow artifacts all available to the scheduler
and the versioned code artifacts available to workers for task execution

.. image:: https://bitbucket.org/dkistdc/dkist-processing-core/raw/faf0c57f2155d03889fcd54bc1676a8a219f6ee3/docs/automated-processing-deployed.png
  :width: 800
  :alt: Airflow Deployment Diagram

Build
-----
dkist-processing-core is built using `bitbucket-pipelines <bitbucket-pipelines.yml>`_

Deployment
----------
dkist-processing-core is deployed to `PyPI <https://pypi.org/project/dkist-processing-core/>`_

Environment Variables
---------------------

.. list-table::
   :widths: 10 70 10 10
   :header-rows: 1

   * - Variable
     - Description
     - Type
     - Default
   * - BUILD_VERSION
     - Build/Export pipelines only.  This is the value that will be appended to all artifacts and represents their unique version
     - STR
     - dev
   * - MESH_CONFIG
     - Provides the dkistdc cloud mesh configuration.  Specifically the location of the message broker
     - JSON
     - ``{}``
   * - ISB_USERNAME
     - Message broker user name
     - STR
     - guest
   * - ISB_PASSWORD
     - Message broker password
     - STR
     - guest
   * - ISB_EXCHANGE
     - Message Broker Exchange name for publishing messages
     - STR
     - master.direct.x
   * - ISB_QUEUE_TYPE
     - Message Broker queue type for transporting messages
     - STR
     - classic
   * - ELASTIC_APM_SERVICE_NAME
     - Service Name used by Elastic Application Performance Monitoring
     - STR
     -
   * - ELASTIC_APM_OTHER_OPTIONS
     - Dictionary of configuration for the Elastic Application Performance Monitoring client
     - STR
     - ``{}``
   * - ELASTIC_APM_ENABLED
     - Flag to disable/enable Elastic Application Performance Monitoring client calls which are chatty if not connected to an APM server.
     - BOOL
     - FALSE
   * - BUILD_VERSION
     - Version of the pipeline.  When built this makes its way into the workflow or dag name.
     - STR
     - dev

Development
-----------
A prerequisite for test execution is a running instance of rabbitmq and docker on the local machine.
For RabbitMQ the tests will use the default guest/guest credentials and a host ip of 127.0.0.1 and port of 5672 to connect to the broker.
Getting docker set up varies by system, but the tests will use the default unix socket for the docker daemon.

To run the tests locally, clone the repository and install the package in editable mode with the test extras.

.. code-block:: bash

    git clone git@bitbucket.org:dkistdc/dkist-processing-core.git
    cd dkist-processing-core
    pre-commit install
    pip install -e .[test]
    # RabbitMQ and Docker needs to be running
    pytest -v --cov dkist_processing_core

Changelog
#########

When you make **any** change to this repository it **MUST** be accompanied by a changelog file.
The changelog for this repository uses the `towncrier <https://github.com/twisted/towncrier>`__ package.
Entries in the changelog for the next release are added as individual files (one per change) to the ``changelog/`` directory.

Writing a Changelog Entry
^^^^^^^^^^^^^^^^^^^^^^^^^

A changelog entry accompanying a change should be added to the ``changelog/`` directory.
The name of a file in this directory follows a specific template::

  <PULL REQUEST NUMBER>.<TYPE>[.<COUNTER>].rst

The fields have the following meanings:

* ``<PULL REQUEST NUMBER>``: This is the number of the pull request, so people can jump from the changelog entry to the diff on BitBucket.
* ``<TYPE>``: This is the type of the change and must be one of the values described below.
* ``<COUNTER>``: This is an optional field, if you make more than one change of the same type you can append a counter to the subsequent changes, i.e. ``100.bugfix.rst`` and ``100.bugfix.1.rst`` for two bugfix changes in the same PR.

The list of possible types is defined the the towncrier section of ``pyproject.toml``, the types are:

* ``feature``: This change is a new code feature.
* ``bugfix``: This is a change which fixes a bug.
* ``doc``: A documentation change.
* ``removal``: A deprecation or removal of public API.
* ``misc``: Any small change which doesn't fit anywhere else, such as a change to the package infrastructure.


Rendering the Changelog at Release Time
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

When you are about to tag a release first you must run ``towncrier`` to render the changelog.
The steps for this are as follows:

* Run `towncrier build --version vx.y.z` using the version number you want to tag.
* Agree to have towncrier remove the fragments.
* Add and commit your changes.
* Tag the release.

**NOTE:** If you forget to add a Changelog entry to a tagged release (either manually or automatically with ``towncrier``)
then the Bitbucket pipeline will fail. To be able to use the same tag you must delete it locally and on the remote branch:

.. code-block:: bash

    # First, actually update the CHANGELOG and commit the update
    git commit

    # Delete tags
    git tag -d vWHATEVER.THE.VERSION
    git push --delete origin vWHATEVER.THE.VERSION

    # Re-tag with the same version
    git tag vWHATEVER.THE.VERSION
    git push --tags origin main

.. |codecov| image:: https://codecov.io/bb/dkistdc/dkist-processing-core/graph/badge.svg?token=SB18SCBJ8Q
 :target: https://codecov.io/bb/dkistdc/dkist-processing-core

====================================
Encrypting Messages With KafkaCrypto
====================================

OpenMSIStream implements encryption of messages sent and received through Kafka using a wrapper around a library called `KafkaCrypto <https://github.com/tmcqueen-materials/kafkacrypto>`_. KafkaCrypto provides message-layer encryption for Kafka assuming an untrusted broker, meaning that the keys and values of messages stored within topics are encrypted. The initial encryption is performed before production using a custom Serializer, and decryption is performed after consumption using a custom Deserializer. Please see the documentation for KafkaCrypto for more information.

Introduction
------------

KafkaCrypto has been wrapped in OpenMSIStream to minimize setup while maximizing flexibility. Successfully producing/consuming encrypted messages requires a few steps after installing OpenMSIStream:

#. Create a new topic to hold encrypted messages. (It is not possible to mix unencrypted and encrypted messages within a topic.)
#. Create additional key-passing topics (if automatic topic creation is turned off). These new topics are "sub-topics" of the topic created in the previous step, and have special names to reflect this. If the newly-created topic that will hold encrypted messages is called "topic," for example, then topics called "topic.keys", "topic.reqs", and "topic.subs" must also be created. These sub-topics can be regularly compacted, and do not benefit from having any more than 1 partition.
#. Provision each node that will act as a producer to, or consumer from, a topic containing encrypted messages (more details below)
#. Add a ``[kafkacrypto]`` section to the config file(s) you use for producers and consumers that will handle encrypted messages (more details below)

Lastly, note that **consuming encrypted messages requires that the producer that produced them is actively running** so that encryption keys can be validated. Users should not, therefore, use OpenMSIStream programs such as :doc:`UploadDataFile <main_programs/upload_data_file>` that automatically shut down producers without user input to produce encrypted messages and should instead use longer-running programs like :doc:`DataFileUploadDirectory <main_programs/data_file_upload_directory>`.

Provisioning a node
-------------------

KafkaCrypto manages which producers and consumers are permitted to send and receive messages to which topics, and keeps these producers and consumers interacting with one another through the key exchange sub-topics. Setting up a set of producers/consumers for a particular topic or set of topics is called "provisioning".

KafkaCrypto provides `a Python script <https://raw.githubusercontent.com/tmcqueen-materials/kafkacrypto/master/tools/simple-provision.py>`_ to walk users through this process. You can invoke this provisioning script in OpenMSIStream using the command::

    ProvisionNode

and following the prompts (the defaults are sensible). If, for any reason, the ``ProvisionNode`` command can't find the ``simple-provision.py`` script, you can download it from the link above and rerun the command while providing its location like::

    ProvisionNode --script-path [path_to_provision_script]

(But OpenMSIStream should be able to do this on its own in most installation contexts.)

Some applications of OpenMSIStream will need to use a different or unique script for provisioning nodes ("online" provision is a common one, only available from a private repository); in those cases you can download the script and provide the path to it as an argument to the ``ProvisionNode`` command as shown above.

For any other issues with provisioning please refer to KafkaCrypto's documentation.

Successfully running the ``ProvisionNode`` command will create a new subdirectory in the OpenMSIStream `config_files directory <https://github.com/openmsi/openmsistream/tree/main/openmsistream/kafka_wrapper/config_files>`_ with a name corresponding to the node ID, containing a ``my-node-id.config`` file, a ``my-node-id.crypto`` file, and a ``my-node-id.seed`` file [#f1]_. KafkaCrypto needs the ``my-node-id.config`` file to setup producers and consumers, and that file is not secret. The ``my-node-id.crypto`` and ``my-node-id.seed`` files, however, should never be saved or transmitted plaintext (files with this pattern `are in the .gitignore <https://github.com/openmsi/openmsistream/blob/main/.gitignore>`_ so if everything is running in the expected way this won't be an issue). An example of one of these created directories can be found `here <https://github.com/openmsi/openmsistream/tree/main/openmsistream/kafka_wrapper/config_files/testing_node>`_ with all files intact because they're used for testing.

Additional configurations needed
--------------------------------

To point OpenMSIStream to the config file that's created, one of two options must be added to the regular OpenMSIStream config file passed :doc:`as discussed in the documentation here <main_programs>` (for example). Both options list a single new parameter under a heading called ``[kafkacrypto]``. 

The first option is to add just the node id, like ``node_id = my-node-id``, which works if a directory called ``my-node-id`` exists in the location expected from running the ``ProvisionNode`` command. 

If provisioning has been performed without using the ``ProvisionNode`` command, or if the config, crypto, and seed files are in some location other than a new directory within the config files directory, then the second option should be used, where instead of the ``node_id`` a parameter ``config_file = path_to_config_file`` is added, where ``path_to_config_file`` is the path to the ``my-node-id.config`` file. When this second options is used, it is assumed that the ``my-node-id.crypto`` and ``my-node-id.seed`` files exist in the same directory as the ``my-node-id.config`` file.

An example of a config file used to set up producers/consumers passing encrypted messages `can be found here <https://github.com/openmsi/openmsistream/blob/main/openmsistream/kafka_wrapper/config_files/test_encrypted.config>`_, referencing the same example "testing_node" node as linked to above.

Mixing encrypted and unencrypted messages in topics (not recommended)
---------------------------------------------------------------------

For rare use cases where encryption is being enabled or disabled across a platform, or when encrypted and unencrypted messages get mixed up in topics, the "``--treat_undecryptable_as_plaintext``" flag can be added to any consumer program to speed up processing of messages that will **never** be able to be decrypted. When that flag is added, undecryptable message keys and values will be returned as raw binary, which may or may not work as expected downstream (messages that were not encrypted *should* get processed normally). Be warned that adding this flag voids all guarantees of using encryption.

Often paired with "``--max_wait_per_decrypt``" and/or "``--max_initial_wait_per_decrypt``" to cut down hang time on encrypted messages.

Undecryptable messages (for ``DataFileDownloadDirectory``)
----------------------------------------------------------

If any messages cannot be successfully decrypted by a :doc:`DataFileDownloadDirectory <main_programs/data_file_download_directory>` for any reason, the binary contents of their encrypted keys and values will be written out to timestamped files in a special subdirectory called "``ENCRYPTED_MESSAGES``" inside the reconstruction directory. One file will be written for the encrypted key and another will be written for the encrypted value. These files can be decrypted later if necessary.

If any undercryptable messages are found, warnings will be logged with the paths to the encrypted key/value files.

It is absolutely possible that transient issues may affect the key-passing necessary to successfully decrypt encrypted messages. In many of these cases, when those issues are resolved, the encrypted messages would only need to be produced to the topic a second time and any online consumers would then be able to process them successfully. For cases such as these, OpenMSIStream includes a small script to read the encrypted key/value files written to the ``ENCRYPTED_MESSAGES`` directory and re-produce them to the topic from which they originated. You can run it using the following command::

    ReproduceUndecryptableMessages [config_file] [path_to_encrypted_messages_dir]

where ``[config_file]`` is the path to a **KakfaCrypo-formatted config file** like the `example available in the repository <https://github.com/openmsi/openmsistream/blob/main/openmsistream/tools/undecryptable_messages/reproduce-encrypted-letters-example.config>`_, and ``[path_to_encrypted_dir]`` is the path to the ``ENCRYPTED_MESSAGES`` directory holding key/value files to re-produce to their original topics.

The script will run until all messages have been re-produced, and the original files will not be deleted from the ``ENCRYPTED_MESSAGES`` directory.

.. rubric:: Footnotes

.. [#f1] Experienced users are also welcome to move the files from any other previously-run node provision into a new directory named for the node ID inside the config_files directory, though this may be more complicated than using :ref:`the second option discussed for dealing with config files <Additional configurations needed>`, depending on how OpenMSIStream was installed.

"""
A set of Consumers sharing a subscribed topic, group ID, and (optionally)
KafkaCrypto instance for key passing
"""

# imports
import kafka
from confluent_kafka.admin import AdminClient
from confluent_kafka import TopicPartition
from openmsitoolbox import LogOwner
from .utilities import reset_to_beginning_on_assign
from .config_file_parser import KafkaConfigFileParser
from .openmsistream_consumer import OpenMSIStreamConsumer


class ConsumerGroup(LogOwner):
    """
    Class for working with a group of consumers sharing a single
    :class:`kafkacrypto.KafkaCrypto` instance

    :param config_path: Path to the config file that should be used to define Consumers in the group
    :type config_path: :class:`pathlib.Path`
    :param consumer_topic_name: The name of the topic to which the Consumers should be subscribed
    :type consumer_topic_name: str
    :param consumer_group_id: The ID string that should be used for each Consumer in the group.
        "create_new" (the default) will create a new UID to use.
    :type consumer_group_id: str, optional
    :param kafkacrypto: The :class:`~OpenMSIStreamKafkaCrypto` object that should be used
        to instantiate Consumers. Only needed if a single specific
        :class:`~OpenMSIStreamKafkaCrypto` instance should be shared.
    :type kafkacrypto: :class:`~OpenMSIStreamKafkaCrypto`, optional
    :param treat_undecryptable_as_plaintext: If True, the KafkaCrypto Deserializers
        will immediately return any keys/values that are not possibly decryptable as
        binary data. This allows faster handling of messages that will never be
        decryptable, such as when enabling or disabling encryption across a platform,
        or when unencrypted messages are mixed in a topic with encrypted messages.
    :type treat_undecryptable_as_plaintext: boolean, optional
    :param max_wait_per_decrypt: Number of seconds a KafkaCrypto Deserializer
        waits before giving up.
    :type max_wait_per_decrypt: float, optional
    :param max_initial_wait_per_decrypt: Number of seconds a KafkaCrypto Deserializer
        waits the first time before giving up.
    :type max_initial_wait_per_decrypt: float, optional
    :param kwargs: Other keyword arguments will be added to the underlying Consumer's
        configurations, with underscores in their names replaced with dots.
    :type kwargs: dict
    """

    @property
    def consumer_topic_name(self):
        """
        Name of the topic to which Consumers are subscribed
        """
        return self.__consumer_topic_name

    @property
    def consumer_group_id(self):
        """
        String ID of Consumers in the group
        """
        return self.__consumer_group_id

    @property
    def kafkacrypto(self):
        """
        The KafkaCrypto object handling key passing and deserialization
        for the group of Consumers (if applicable)
        """
        return (
            self.__c_kwargs["kafkacrypto"] if "kafkacrypto" in self.__c_kwargs else None
        )

    def __init__(
        self,
        config_path,
        consumer_topic_name,
        *,
        consumer_group_id="create_new",
        kafkacrypto=None,
        treat_undecryptable_as_plaintext=False,
        max_wait_per_decrypt=5.0,
        max_initial_wait_per_decrypt=60.0,
        **kwargs,
    ):
        """
        Constructor method
        """
        super().__init__(**kwargs)
        self.__group_starting_offsets = self.__get_group_starting_offsets(
            config_path, consumer_topic_name, consumer_group_id
        )
        self.__consumer_topic_name = consumer_topic_name
        self.__c_args, self.__c_kwargs = OpenMSIStreamConsumer.get_consumer_args_kwargs(
            config_path,
            group_id=consumer_group_id,
            logger=self.logger,
            kafkacrypto=kafkacrypto,
            treat_undecryptable_as_plaintext=treat_undecryptable_as_plaintext,
            max_wait_per_decrypt=max_wait_per_decrypt,
            max_initial_wait_per_decrypt=max_initial_wait_per_decrypt,
        )
        if len(self.__c_args) > 1 and "group.id" in self.__c_args[1]:
            self.__consumer_group_id = self.__c_args[1]["group.id"]
        else:
            self.__consumer_group_id = consumer_group_id

    def get_new_subscribed_consumer(self, *, restart_at_beginning=False, **kwargs):
        """
        Return a new Consumer, subscribed to the topic and with the shared group ID.
        Call this function from a child thread to get thread-independent Consumers.

        Note: This function just creates and subscribes the Consumer. Polling it, closing
        it, and everything else must be handled by whatever calls this function.

        :param restart_at_beginning: if True, the new Consumer will start reading partitions
            from the earliest messages available, regardless of Consumer group ID and
            auto.offset.reset values. Useful when re-reading messages.
        :type restart_at_beginning: bool, optional
        :param kwargs: other keyword arguments are passed to the
            :class:`~OpenMSIStreamConsumer` constructor method
        :type kwargs: dict

        :return: a Consumer created using the configs set in the constructor/from `kwargs`,
            subscribed to the topic
        :rtype: :class:`~OpenMSIStreamConsumer`
        """
        consumer = OpenMSIStreamConsumer(
            *self.__c_args,
            **kwargs,
            starting_offsets=self.__group_starting_offsets,
            **self.__c_kwargs,
        )
        if restart_at_beginning:
            consumer.subscribe(
                [self.__consumer_topic_name], on_assign=reset_to_beginning_on_assign
            )
        else:
            consumer.subscribe([self.__consumer_topic_name])
        return consumer

    def close(self):
        """
        Wrapper around :func:`kafkacrypto.KafkaCrypto.close`.
        """
        if "kafkacrypto" not in self.__c_kwargs:
            return
        self.__c_kwargs["kafkacrypto"].close()
        self.__c_kwargs["kafkacrypto"] = None

    def __get_group_starting_offsets(
        self, config_path, consumer_topic_name, consumer_group_id, n_retries=10
    ):
        """
        Return a list of TopicPartitions listing the starting offsets for each partition
        in the topic for the given consumer group ID

        Retries a configurable number of times if it fails at first, since there can be
        some lag involved

        Re-raises any errors encountered in getting the necessary metadata,
        returning None if that happens
        """
        caught_exc = None
        while n_retries > 0:
            cfp = KafkaConfigFileParser(config_path)
            starting_offsets = []
            try:
                cluster_metadata = AdminClient(cfp.broker_configs).list_topics(
                    topic=consumer_topic_name
                )
                n_partitions = len(
                    cluster_metadata.topics[consumer_topic_name].partitions
                )
                if n_partitions <= 0:
                    raise RuntimeError(
                        f"ERROR: number of partitions for topic {consumer_topic_name} is "
                        f"{n_partitions}"
                    )
                kac_kwargs = {}
                for k, v in cfp.broker_configs.items():
                    if k in ("sasl.username", "sasl.password"):
                        key = k.replace(".", "_plain_")
                    else:
                        key = k.replace(".", "_")
                    kac_kwargs[key] = v
                parts = [
                    kafka.TopicPartition(consumer_topic_name, p_i)
                    for p_i in range(n_partitions)
                ]
                tp_offsets = kafka.KafkaAdminClient(
                    **kac_kwargs
                ).list_consumer_group_offsets(
                    group_id=consumer_group_id, partitions=parts
                )
                if len(tp_offsets) != n_partitions:
                    errmsg = (
                        f"Found {n_partitions} partitions for topic {consumer_topic_name} but got "
                        f"{len(tp_offsets)} TopicPartitions listing current consumer group offsets"
                    )
                    raise RuntimeError(errmsg)
                for t_p, offset_metadata in tp_offsets.items():
                    starting_offsets.append(
                        TopicPartition(t_p.topic, t_p.partition, offset_metadata.offset)
                    )
                return starting_offsets
            except Exception as exc:
                caught_exc = exc
                n_retries -= 1
        if caught_exc:
            errmsg = (
                f'ERROR: encountered an exception when gathering initial "{consumer_topic_name}" '
                f'topic offsets for consumer group ID "{consumer_group_id}". '
                "The error will be logged below and re-raised."
            )
            self.logger.error(errmsg, exc_info=caught_exc, reraise=True)
        return None

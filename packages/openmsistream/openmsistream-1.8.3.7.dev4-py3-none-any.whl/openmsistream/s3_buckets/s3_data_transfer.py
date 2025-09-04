"""Small class to effect transfer of a datafile to an S3 bucket"""

from botocore.exceptions import ClientError
from .s3_service import S3Service


class S3DataTransfer(S3Service):
    """
    Small class to effect transfer of a datafile to an S3 bucket
    """

    def __init__(self, s3_config, *args, **kwargs):
        super().__init__(s3_config, *args, **kwargs)

    def transfer_object_stream(self, object_key, datafile):
        """
        Transfer the contents of a DataFile Consumed from chunks in a topic to an S3 bucket
        """
        content = None
        try:
            content = datafile.bytestring
        except AttributeError:
            with open(datafile.full_filepath, "rb") as fp:
                content = fp.read()
        file_name = str(datafile.filename)
        try:
            self.s3_client.put_object(
                Body=content,
                Bucket=self.bucket_name,
                Key=object_key,
                # GrantRead=self.grant_read
            )
            msg = f"{file_name} successfully transferred into {self.bucket_name}/{object_key}"
            self.logger.debug(msg)
        except ClientError as err:
            errmsg = (
                f"{err.response}: failed to transfer {file_name} into "
                f"{self.bucket_name}/{object_key}"
            )
            self.logger.error(errmsg, exc_info=err)

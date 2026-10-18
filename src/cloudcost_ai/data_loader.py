import io
import time
import oci
import pandas as pd

from cloudcost_ai.config import OCI_CONFIG_FILE,OCI_PROFILE
from cloudcost_ai.utils.logger import get_logger
from cloudcost_ai.utils.exception import CustomException

logger=get_logger(__name__)


def load_billing_data(bucket_name:str,object_name:str)->pd.DataFrame:

    try:
        logger.info("loading oci configuration")
        config=oci.config.from_file(
            file_location=str(OCI_CONFIG_FILE),
            profile_name=OCI_PROFILE,
        )

        client=oci.object_storage.ObjectStorageClient(config,timeout=(10,300))
        namespace=client.get_namespace().data

        logger.info("downloading object :%s",object_name)

        response=client.get_object(
            namespace_name=namespace,
            bucket_name=bucket_name,
            object_name=object_name,
        )

        csv_content=response.data.content

        dataframe=pd.read_csv(io.BytesIO(csv_content))

        logger.info(
            "Successfully loaded %s rows and %s columns",
            dataframe.shape[0],
            dataframe.shape[1]
        )

        return dataframe

    except Exception as error:
        logger.exception("Error loading OCI configuration")
        raise CustomException(error) from error

def download_object_with_retry(client,namespace,bucket_name,object_name,max_attempts=3):

    for attempt in range(1,max_attempts+1):
        try:
            logger.info(
                "Attempt %d: Downloading object %s from bucket %s",
                attempt,
                object_name,
                bucket_name 
            )
            response=client.get_object(
                namespace_name=namespace,
                bucket_name=bucket_name,
                object_name=object_name
            )

            return response.data.content
        except Exception as error:
            logger.exception("Download attempt %s failed", attempt)

            if attempt == max_attempts:
                raise

            time.sleep(2 * attempt)
import httpx
import mimetypes

import os
from .base_client import PinnacleBase, AsyncPinnacleBase
from .utils import parse_inbound


class Pinnacle(PinnacleBase):

    def upload(self, file_path: str):
        """
        Upload media to Pinnacle's server and return the presigned download url.

        Parameters
        ----------
        file_path : str
            The file path to the media to be uploaded.

        Returns
        -------
        download_url : str
            The presigned download url of the uploaded media

        Examples
        --------
        from rcs import Pinnacle

        client = Pinnacle(
            api_key="YOUR_API_KEY",
        )

        media_url = client.upload("path/to/media")
        """

        file_type = mimetypes.guess_type(file_path)[0]

        if not file_type:
            raise Exception("Could not determine the file type")

        upload_response = self.tools.upload_url(
            content_type=file_type,
            size=os.stat(file_path).st_size,
            name=os.path.basename(file_path),
        )

        upload_url = upload_response.upload
        download_url = upload_response.download

        if not upload_url:
            raise Exception("Failed to get upload url")

        if not download_url:
            raise Exception("Failed to get download url")

        with open(file_path, "rb") as file:
            response = httpx.put(
                upload_url,
                headers={
                    "Content-Type": file_type,
                },
                content=file,
            )

            if response.status_code != 200:
                raise Exception(f"Failed to upload file: {response.text}")

        return download_url

    @staticmethod
    def parse_inbound_message(
        data: dict,
    ):
        """
        Parse the inbound message data.

        Parameters
        ----------
        data : dict
            The inbound message data to be parsed.

        Returns
        -------
        inbound_message : Union[
            InboundActionMessage,
            InboundTextMessage,
            InboundLocationMessage,
            InboundMediaMessage,
        ]
            The parsed inbound message data.


        Examples
        --------
        from rcs import Pinnacle

        data = {
            "message_type": "text",
            "text": "Hello, World!",
            "from": "+12345678901",
            "to": "+10987654321",
            "metadata": None
        }
        parsed_data = Pinnacle.parse_inbound_message(data)
        """

        return parse_inbound(data)


class AsyncPinnacle(AsyncPinnacleBase):

    async def upload(self, file_path: str):
        """
        Upload media to Pinnacle's server and return the presigned download url.

        Parameters
        ----------
        file_path : str
            The file path to the media to be uploaded.

        Returns
        -------
        download_url : str
            The presigned download url of the uploaded media

        Examples
        --------

        client = AsyncPinnacle(
            api_key="YOUR_API_KEY",
        )

        media_url = await client.upload("path/to/media")
        """

        file_type = mimetypes.guess_type(file_path)[0]

        if not file_type:
            raise Exception("Could not determine the file type")

        upload_response = await self.tools.upload_url(
            content_type=file_type,
            size=os.stat(file_path).st_size,
            name=os.path.basename(file_path),
        )

        upload_url = upload_response.upload
        download_url = upload_response.download

        if not upload_url:
            raise Exception("Failed to get upload url")

        if not download_url:
            raise Exception("Failed to get download url")

        with open(file_path, "rb") as file:
            content = file.read()
            async with httpx.AsyncClient() as client:
                response = await client.put(
                    upload_url,
                    headers={
                        "Content-Type": file_type,
                    },
                    content=content,
                )

                if response.status_code != 200:
                    raise Exception(f"Failed to upload file: {response.text}")

        return download_url

    @staticmethod
    def parse_inbound_message(
        data: dict,
    ):
        """
        Parse the inbound message data.

        Parameters
        ----------
        data : dict
            The inbound message data to be parsed.

        Returns
        -------
        inbound_message : Union[
            InboundActionMessage,
            InboundTextMessage,
            InboundLocationMessage,
            InboundMediaMessage,
        ]
            The parsed inbound message data.


        Examples
        --------
        from rcs import Pinnacle

        data = {
            "message_type": "text",
            "text": "Hello, World!",
            "from": "+12345678901",
            "to": "+10987654321",
            "metadata": None
        }
        parsed_data = Pinnacle.parse_inbound_message(data)
        """
        return parse_inbound(data)

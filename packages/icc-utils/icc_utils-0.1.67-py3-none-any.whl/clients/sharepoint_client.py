import io
import msal
import asyncio
import aiohttp
import pandas as pd
from datetime import datetime, timezone, timedelta

from icc_utils.utils.exceptions import SharepointError


class SharePointClient:

    def __init__(self, tenant_id, client_id, client_secret):

        self._tenant_id: str = tenant_id
        self._client_id: str = client_id
        self._client_secret: str = client_secret

        self._scope = ["https://graph.microsoft.com/.default"]
        self._graph = "https://graph.microsoft.com/v1.0"
        self._authority = f"https://login.microsoftonline.com/{self._tenant_id}"

        self._msal_app: msal.ConfidentialClientApplication = msal.ConfidentialClientApplication(
            client_id=self._client_id,
            client_credential=self._client_secret,
            authority=self._authority,
            token_cache=msal.TokenCache()
        )

        self._access_token = self._msal_app.acquire_token_for_client(scopes=self._scope)["access_token"]
        self._headers: dict = {"Authorization": f"Bearer {self._access_token}"}

        self._site_id: str = None
        self._drive_id: str = None

    async def get_file_urls(self, session: aiohttp.ClientSession, drive_id: str = None, folder_id: str = None, file_id: str = None, extension: str = None, lookback_days: int = 0) -> dict:
        if folder_id:
            url = f"https://graph.microsoft.com/v1.0/drives/{drive_id}/items/{folder_id}/children"
            cutoff_date = datetime.now(timezone.utc) - timedelta(days=lookback_days) if lookback_days > 0 else None
            result: dict[str, str] = {}

            while url:
                try:
                    async with session.get(url, headers=self._headers) as response:
                        if response.status == 200:
                            data = await response.json()
                            for file in data.get("value", []):
                                name = file.get("name", "")
                                if not name.lower().endswith(extension.lower()):
                                    continue

                                modified = file.get("lastModifiedDateTime")
                                if modified:
                                    last_modified = datetime.fromisoformat(modified.replace("Z", "+00:00"))
                                    if cutoff_date and last_modified < cutoff_date:
                                        continue

                                download_url = file.get("@microsoft.graph.downloadUrl")
                                if download_url:
                                    result[name] = download_url

                            # Continue pagination if present
                            url = data.get("@odata.nextLink")
                        elif response.status == 503:
                            # Throttling or temporary service unavailability
                            retry_after = int(response.headers.get("Retry-After", 5))
                            await asyncio.sleep(retry_after)
                        else:
                            error_text = await response.text()
                            break
                except aiohttp.ClientError as e:
                    break

            return result
        else:
            url = f"https://graph.microsoft.com/v1.0/drives/{drive_id}/items/{file_id}"
            async with session.get(url, headers=self._headers) as response:
                metadata = await response.json()
                download_url = metadata.get('@microsoft.graph.downloadUrl')
                return download_url

    @staticmethod
    async def cache_excel_file(session: aiohttp.ClientSession, download_url: str, retries: int = 5, delay: float = 30.0) -> pd.ExcelFile:
        """
        Download an Excel file with retry logic and return a pd.ExcelFile.
        Retries on 429 and 5xx responses, and on aiohttp client errors.

        Args:
            session: existing aiohttp.ClientSession
            download_url: direct Graph download URL
            retries: max attempts
            delay: base delay seconds for exponential backoff

        Raises:
            SharepointError on failure after retries or non-retryable HTTP errors.
        """
        last_exception = None

        for attempt in range(1, retries + 1):
            try:
                async with session.get(download_url) as response:
                    if response.status == 200:
                        content = await response.read()
                        return pd.ExcelFile(io.BytesIO(content), engine="openpyxl")

                    # Decide if this status should be retried
                    retryable = (
                            response.status == 429
                            or response.status >= 500
                    )

                    if not retryable:
                        text = await response.text()
                        raise SharepointError(
                            f"Failed to download Excel file: HTTP {response.status} - {text[:200]}"
                        )

                    # Retryable: compute sleep, using Retry-After if provided
                    if attempt == retries:
                        text = await response.text()
                        raise SharepointError(
                            f"Failed after {retries} attempts: HTTP {response.status} - {text[:200]}"
                        )

                    retry_after = response.headers.get("Retry-After")
                    sleep_s = float(retry_after) if retry_after else delay * (2 ** (attempt - 1))
                    await asyncio.sleep(sleep_s)
                    continue  # next attempt

            except aiohttp.ClientError as e:
                last_exc = e
                if attempt == retries:
                    raise SharepointError(f"Network error after {retries} attempts: {e}") from e
                sleep_s = delay * (2 ** (attempt - 1))
                await asyncio.sleep(sleep_s)
                continue

        raise SharepointError("Unexpected failure") from last_exception


    ##############################################################################

    # async def _get_site_id(self, session):
    #     url = f'https://graph.microsoft.com/v1.0/sites/'
    #     async with session.get(url, headers=self._headers) as response:
    #         data = await response.json()
    #         df = pd.DataFrame(data.get("value", []))
    #         site_id = df.set_index('name')['id'].get('Services - Data Processing')
    #         return site_id
    #
    # async def _get_drive_id(self, session):
    #     self._site_id = await self._get_site_id(session)
    #     url = f'https://graph.microsoft.com/v1.0/sites/{self._site_id}/drives'
    #     async with session.get(url, headers=self._headers) as response:
    #         data = await response.json()
    #         df = pd.DataFrame(data.get("value", []))
    #         drive_id = df.set_index('name')['id'].get('Documents')
    #         return drive_id
    #
    # async def _get_root_folder_id(self, session):
    #     self._site_id = await self._get_site_id(session)
    #     self._drive_id = await self._get_drive_id(session)
    #     url = f'https://graph.microsoft.com/v1.0/sites/{self._site_id}/drives/{self._drive_id}/root/children'
    #     async with session.get(url, headers=self._headers) as response:
    #         data = await response.json()
    #         df = pd.DataFrame(data.get("value", []))
    #         trackers_id = df.set_index('name')['id'].get('Trackers')
    #         return trackers_id
    #
    # async def _get_root_folder_ids(self):
    #     async with aiohttp.ClientSession() as session:
    #         self._drive_id = await self._get_drive_id(session)
    #         root_folder_id = await self._get_root_folder_id(session)
    #
    #         url = f'https://graph.microsoft.com/v1.0/sites/{self._site_id}drives/{self._drive_id}/items/{root_folder_id}/children'
    #
    #         async with session.get(url, headers=self._headers) as response:
    #             data = await response.json()
    #             df = pd.DataFrame(data.get("value", []))
    #             df = df[['name', 'id']]
    #             return df.set_index("name")["id"].to_dict()
    #
    # def get_root_folder_ids(self):
    #     return asyncio.run(self._get_root_folder_ids())
    #
    # async def _get_folder_contents(self, folder_id):
    #     url = f"https://graph.microsoft.com/v1.0/sites/{self._site_id}/drives/{self._drive_id}/items/{folder_id}/children"
    #     async with aiohttp.ClientSession() as session:
    #         async with session.get(url, headers=self._headers) as response:
    #             data = await response.json()
    #             df = pd.DataFrame(data.get("value", []))
    #             print(df)
    #
    # def get_folder_contents(self, folder_id):
    #     return asyncio.run(self._get_folder_contents(folder_id))

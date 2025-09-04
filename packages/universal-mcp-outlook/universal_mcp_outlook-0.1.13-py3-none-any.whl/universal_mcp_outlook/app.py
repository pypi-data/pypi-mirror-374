from typing import Any, Optional, List
from universal_mcp.applications import APIApplication
from universal_mcp.integrations import Integration
from urllib.parse import urlparse, parse_qs  # <-- THIS IS THE CRITICAL FIX
import concurrent.futures

class OutlookApp(APIApplication):
    def __init__(self, integration: Integration = None, **kwargs) -> None:
        super().__init__(name="outlook", integration=integration, **kwargs)
        self.base_url = "https://graph.microsoft.com/v1.0"

    def users_message_reply(
        self,
        user_id: str,
        message_id: str,
        comment: Optional[str] = None,
        message: Optional[dict[str, Any]] = None,
    ) -> Any:
        """
        Replies to a specific message for a user using the POST method, accepting JSON content in the request body and returning status codes indicating success or error.

        Args:
            user_id (string): user-id
            message_id (string): message-id
            comment (string): A comment to include in the reply. Example: 'Thank you for your email. Here is my reply.'.
            message (object): A message object to specify additional properties for the reply, such as attachments. Example: {'subject': 'RE: Project Update', 'body': {'contentType': 'Text', 'content': 'Thank you for the update. Looking forward to the next steps.'}, 'toRecipients': [{'emailAddress': {'address': 'alice@contoso.com'}}], 'attachments': [{'@odata.type': '#microsoft.graph.fileAttachment', 'name': 'agenda.pdf', 'contentType': 'application/pdf', 'contentBytes': 'SGVsbG8gV29ybGQh'}]}.

        Returns:
            Any: Success

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            users.message, important
        """
        if user_id is None:
            raise ValueError("Missing required parameter 'user-id'.")
        if message_id is None:
            raise ValueError("Missing required parameter 'message-id'.")
        request_body_data = None
        request_body_data = {
            "comment": comment,
            "message": message,
        }
        request_body_data = {
            k: v for k, v in request_body_data.items() if v is not None
        }
        url = f"{self.base_url}/users/{user_id}/messages/{message_id}/reply"
        query_params = {}
        response = self._post(
            url,
            data=request_body_data,
            params=query_params,
            content_type="application/json",
        )
        return self._handle_response(response)

    def user_send_mail(
        self,
        user_id: str,
        message: dict[str, Any],
        saveToSentItems: Optional[bool] = None,
    ) -> Any:
        """
        Sends an email on behalf of the specified user, accepting the email details as JSON in the request body and returning a 204 No Content response on success.

        Args:
            user_id (string): user-id
            message (object): message Example: {'subject': 'Meet for lunch?', 'body': {'contentType': 'Text', 'content': 'The new cafeteria is open.'}, 'toRecipients': [{'emailAddress': {'address': 'frannis@contoso.com'}}], 'ccRecipients': [{'emailAddress': {'address': 'danas@contoso.com'}}], 'bccRecipients': [{'emailAddress': {'address': 'bccuser@contoso.com'}}], 'attachments': [{'@odata.type': '#microsoft.graph.fileAttachment', 'name': 'attachment.txt', 'contentType': 'text/plain', 'contentBytes': 'SGVsbG8gV29ybGQh'}]}.
            saveToSentItems (boolean): saveToSentItems Example: 'False'.

        Returns:
            Any: Success

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            users.user.Actions, important
        """
        if user_id is None:
            raise ValueError("Missing required parameter 'user-id'.")
        request_body_data = None
        request_body_data = {
            "message": message,
            "saveToSentItems": saveToSentItems,
        }
        request_body_data = {
            k: v for k, v in request_body_data.items() if v is not None
        }
        url = f"{self.base_url}/users/{user_id}/sendMail"
        query_params = {}
        response = self._post(
            url,
            data=request_body_data,
            params=query_params,
            content_type="application/json",
        )
        return self._handle_response(response)

    def user_get_mail_folder(
        self,
        user_id: str,
        mailFolder_id: str,
        includeHiddenFolders: Optional[str] = None,
        select: Optional[List[str]] = None,
        expand: Optional[List[str]] = None,
    ) -> Any:
        """
        Retrieves a specific mail folder for a specified user using optional query parameters to include hidden folders or select/expand properties.

        Args:
            user_id (string): user-id
            mailFolder_id (string): mailFolder-id
            includeHiddenFolders (string): Include Hidden Folders
            select (array): Select properties to be returned
            expand (array): Expand related entities

        Returns:
            Any: Retrieved navigation property

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            users.mailFolder, important
        """
        if user_id is None:
            raise ValueError("Missing required parameter 'user-id'.")
        if mailFolder_id is None:
            raise ValueError("Missing required parameter 'mailFolder-id'.")
        url = f"{self.base_url}/users/{user_id}/mailFolders/{mailFolder_id}"
        query_params = {
            k: v
            for k, v in [
                ("includeHiddenFolders", includeHiddenFolders),
                ("$select", select),
                ("$expand", expand),
            ]
            if v is not None
        }
        response = self._get(url, params=query_params)
        return self._handle_response(response)

    def user_list_message(
        self,
        user_id: str,
        next_link: Optional[str] = None,
        select: list[str] = ["bodyPreview"],
        includeHiddenMessages: Optional[str] = None,
        top: Optional[int] = 5,
        skip: Optional[int] = None,
        search: Optional[str] = None,
        filter: Optional[str] = None,
        count: Optional[bool] = None,
        orderby: Optional[List[str]] = None,
        expand: Optional[List[str]] = None,
    ) -> dict[str, Any]:
        """
        Retrieves a list of messages for a user with detailed information, using concurrent processing to efficiently fetch message details.

        Args:
            user_id (string): user-id
            next_link (string): URL from previous response to fetch next page. If provided, other parameters are ignored.
            select (list): Select properties to be returned. Defaults to ['bodyPreview'].
            includeHiddenMessages (string): Include Hidden Messages
            top (integer): Show only the first n items Example: '50'.
            skip (integer): Skip the first n items
            search (string): Search items by search phrases
            filter (string): Filter items by property values
            count (boolean): Include count of items
            orderby (array): Order items by property values
            expand (array): Expand related entities

        Returns:
            dict[str, Any]: Dictionary containing detailed messages and next page link for pagination

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            users.message, important
        """
        if user_id is None:
            raise ValueError("Missing required parameter 'user-id'.")
        if next_link:
            data = self.get_from_url(next_link)
        else:
            url = f"{self.base_url}/users/{user_id}/messages"
            query_params = {
                k: v
                for k, v in [
                    ("includeHiddenMessages", includeHiddenMessages),
                    ("$top", top),
                    ("$skip", skip),
                    ("$search", search),
                    ("$filter", filter),
                    ("$count", count),
                    ("$orderby", orderby),
                    ("$select", select),
                    ("$expand", expand),
                ]
                if v is not None
            }
            response = self._get(url, params=query_params)
            data = self._handle_response(response)
        
        # Extract message IDs
        messages = data.get("value", [])
        message_ids = [msg.get("id") for msg in messages if msg.get("id")]
        
        # Use ThreadPoolExecutor to get detailed information for each message in parallel
        detailed_messages = []
        if message_ids:
            with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
                future_to_message_id = {
                    executor.submit(self.user_get_message, user_id, message_id): message_id 
                    for message_id in message_ids
                }
                
                for future in concurrent.futures.as_completed(future_to_message_id):
                    try:
                        result = future.result()
                        detailed_messages.append(result)
                    except Exception as e:
                       
                        pass
        
        return {
            "messages": detailed_messages,
            "next_link": data.get("@odata.nextLink"),
            "count": data.get("@odata.count")
        }

 
    def user_get_message(
        self,
        user_id: str,
        message_id: str,
        includeHiddenMessages: Optional[str] = None,
        select: Optional[List[str]] = None,
        expand: Optional[List[str]] = None,
    ) -> Any:
        """
        Retrieves a specific message for a user, optionally including hidden messages, selecting specific fields, or expanding related data.

        Args:
            user_id (string): user-id
            message_id (string): message-id
            includeHiddenMessages (string): Include Hidden Messages
            select (array): Select properties to be returned
            expand (array): Expand related entities

        Returns:
            Any: Retrieved navigation property

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            users.message, important
        """
        if user_id is None:
            raise ValueError("Missing required parameter 'user-id'.")
        if message_id is None:
            raise ValueError("Missing required parameter 'message-id'.")
        url = f"{self.base_url}/users/{user_id}/messages/{message_id}"
        query_params = {
            k: v
            for k, v in [
                ("includeHiddenMessages", includeHiddenMessages),
                ("$select", select),
                ("$expand", expand),
            ]
            if v is not None
        }
        response = self._get(url, params=query_params)
        return self._handle_response(response)

    def user_delete_message(self, user_id: str, message_id: str) -> Any:
        """
        Deletes a specific message for a given user using the DELETE method and optional If-Match header for conditional requests.

        Args:
            user_id (string): user-id
            message_id (string): message-id

        Returns:
            Any: Success

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            users.message, important
        """
        if user_id is None:
            raise ValueError("Missing required parameter 'user-id'.")
        if message_id is None:
            raise ValueError("Missing required parameter 'message-id'.")
        url = f"{self.base_url}/users/{user_id}/messages/{message_id}"
        query_params = {}
        response = self._delete(url, params=query_params)
        return self._handle_response(response)

    def user_message_list_attachment(
        self,
        user_id: str,
        message_id: str,
        top: Optional[int] = None,
        skip: Optional[int] = None,
        search: Optional[str] = None,
        filter: Optional[str] = None,
        count: Optional[bool] = None,
        orderby: Optional[List[str]] = None,
        select: Optional[List[str]] = None,
        expand: Optional[List[str]] = None,
    ) -> dict[str, Any]:
        """
        Retrieves attachments associated with a specified user’s message, supporting filtering, pagination, and field selection via query parameters.

        Args:
            user_id (string): user-id
            message_id (string): message-id
            top (integer): Show only the first n items Example: '50'.
            skip (integer): Skip the first n items
            search (string): Search items by search phrases
            filter (string): Filter items by property values
            count (boolean): Include count of items
            orderby (array): Order items by property values
            select (array): Select properties to be returned
            expand (array): Expand related entities

        Returns:
            dict[str, Any]: Retrieved collection

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            users.message, important
        """
        if user_id is None:
            raise ValueError("Missing required parameter 'user-id'.")
        if message_id is None:
            raise ValueError("Missing required parameter 'message-id'.")
        url = f"{self.base_url}/users/{user_id}/messages/{message_id}/attachments"
        query_params = {
            k: v
            for k, v in [
                ("$top", top),
                ("$skip", skip),
                ("$search", search),
                ("$filter", filter),
                ("$count", count),
                ("$orderby", orderby),
                ("$select", select),
                ("$expand", expand),
            ]
            if v is not None
        }
        response = self._get(url, params=query_params)
        return self._handle_response(response)
    
    def get_user_id(
        self,
        select: list[str] = ["userPrincipalName"],
    ) -> dict[str, Any]:
        """
        Retrieves the current user.

        Args:
            select (list): Properties to be returned. Defaults to ['userPrincipalName'].

        Returns:
            dict[str, Any]: Current user information

        Raises:
            HTTPStatusError: Raised when the API request fails with detailed error information including status code and response body.

        Tags:
            me, important
        """
        url = f"{self.base_url}/me"
        query_params = {
            "$select": select,
        }
        response = self._get(url, params=query_params)
        return self._handle_response(response)

    def get_from_url(self, url: str) -> dict[str, Any]:
        """
        Makes a GET request to a full @odata.nextLink or @odata.deltaLink URL.
        """
        if not url:
            raise ValueError("Missing required parameter 'url'.")
        if not url.startswith(self.base_url):
            raise ValueError(
                f"The provided URL '{url}' does not start with the expected base URL '{self.base_url}'."
            )
        relative_part = url[len(self.base_url):]
        parsed_relative = urlparse(relative_part)
        path_only = parsed_relative.path
        params = {k: v[0] for k, v in parse_qs(parsed_relative.query).items()}
        response = self._get(path_only, params=params)
        return self._handle_response(response)

    def list_tools(self):
        return [
            self.users_message_reply,
            self.user_send_mail,
            self.user_get_mail_folder,
            self.user_list_message,
            self.user_get_message,
            self.user_delete_message,
            self.user_message_list_attachment,
            self.get_user_id,
            self.get_from_url,
        ]

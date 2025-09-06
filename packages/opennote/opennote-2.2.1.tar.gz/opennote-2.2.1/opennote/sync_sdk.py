from typing import Optional, List, Literal
import httpx
from opennote.api_types import (
    VideoCreateJobRequest,
    VideoCreateJobResponse,
    VideoJobStatusResponse,
    JournalsResponse,
    JournalContentResponse,
    VideoAPIRequestMessage,
    FlashcardCreateRequest,
    FlashcardCreateResponse,
    PracticeProblemSetJobCreateRequest,
    PracticeProblemSetJobCreateResponse,
    PracticeProblemSetStatusResponse,
    GradeFRQResponse,
    GradeFRQRequest,
    PracticeProblem,
)
from opennote.base_client import BaseClient
from opennote.api_types import OPENNOTE_BASE_URL, MODEL_CHOICES


class Video:
    """Video endpoints for Opennote API."""
    
    def __init__(self, client: "OpennoteClient"):
        self._client = client

    def create(
        self,
        messages: Optional[List[VideoAPIRequestMessage]] = None,
        model: Optional[MODEL_CHOICES] = "picasso",
        include_sources: Optional[bool] = False,
        search_for: Optional[str] = None,
        source_count: Optional[int] = 3,
        length: Optional[int] = 3,
        script: Optional[str] = None,
        upload_to_s3: Optional[bool] = False,
        title: Optional[str] = "",
        webhook_url: Optional[str] = None,
    ) -> VideoCreateJobResponse:
        """
        Create a new video job.
        
        Args:
            messages: List of messages for video script generation
            model: Model to use (default: "picasso")
            include_sources: Whether to gather web data for the script
            search_for: Query to search the web (max 100 chars)
            source_count: Number of web sources to gather (1-5)
            length: Number of paragraphs in script (1-5)
            script: Pre-written script with sections delimited by '-----' (max 6000 chars)
            upload_to_s3: Whether to upload video to S3
            title: Title of the video
            webhook_url: URL to send the final completion status to (same response type as the status endpoint)
        Returns:
            VideoCreateJobResponse with success status and video_id
        """
        request = VideoCreateJobRequest(
            messages=messages,
            model=model,
            include_sources=include_sources,
            search_for=search_for,
            source_count=source_count,
            length=length,
            script=script,
            upload_to_s3=upload_to_s3,
            title=title,
            webhook_url=webhook_url,
        )
        
        response = self._client._request(
            "POST",
            "/v1/video/create",
            json=request.model_dump(exclude_none=True),
        )
        return VideoCreateJobResponse(**response)

    def status(self, video_id: str) -> VideoJobStatusResponse:
        """
        Get the status of a video job.
        
        Args:
            video_id: ID of the video job
            
        Returns:
            VideoJobStatusResponse with status and completion details
        """
        if not video_id:
            raise ValueError("video_id must be provided")
        
        response = self._client._request(
            "GET",
            f"/v1/video/status/{video_id}",
        )
        return VideoJobStatusResponse(**response)


class Journals:
    """Journal endpoints for Opennote API."""
    
    def __init__(self, client: "OpennoteClient"):
        self._client = client

    def list(self, page_token: Optional[int] = None) -> JournalsResponse:
        """
        List journals with pagination.
        
        Args:
            page_token: Token for pagination
            
        Returns:
            JournalsResponse with list of journals and next page token
        """
        params = {}
        if page_token is not None:
            params["page_token"] = page_token
            
        response = self._client._request(
            "GET",
            "/v1/journals/list",
            params=params,
        )
        return JournalsResponse(**response)

    def content(self, journal_id: str) -> JournalContentResponse:
        """
        Get content of a specific journal.
        
        Args:
            journal_id: ID of the journal
            
        Returns:
            JournalContentResponse with journal content
        """
        if not journal_id:
            raise ValueError("journal_id must be provided")
        
        response = self._client._request(
            "GET",
            f"/v1/journals/content/{journal_id}",
        )
        return JournalContentResponse(**response)
    

class Flashcards:
    """Flashcard endpoints for Opennote API."""
    
    def __init__(self, client: "OpennoteClient"):
        self._client = client

    def create(self, set_description: str, count: int = 10, set_name: Optional[str] = None) -> FlashcardCreateResponse:
        """
        Create a new flashcard set.

        Args:
            set_description: The description of the flashcard set, i.e. what you want to include in the set.
            count: The number of flashcards to generate
            set_name: The name of the flashcard set, if you want to provide one. If you do not, one will be generated for you at additional cost.

        Returns:
            FlashcardCreateResponse with success status and flashcard set name
        """
        if not set_description:
            raise ValueError("set_description must be provided")
        if not count:
            raise ValueError("count must be provided")

        request = FlashcardCreateRequest(set_description=set_description, count=count, set_name=set_name)
        response = self._client._request("POST", "/v1/interactives/flashcards/create", json=request.model_dump(exclude_none=True))
        return FlashcardCreateResponse(**response)


class PracticeProblemSets:
    """Practice problem set endpoints for Opennote API."""
    
    def __init__(self, client: "OpennoteClient"):
        self._client = client

    def create(self, set_description: str, count: int = 5, set_name: Optional[str] = None, search_for_problems: bool = False, webhook_url: Optional[str] = None) -> PracticeProblemSetJobCreateResponse:
        """
        Create a new practice problem set.
        """
        request = PracticeProblemSetJobCreateRequest(set_description=set_description, count=count, set_name=set_name, search_for_problems=search_for_problems, webhook_url=webhook_url)
        response = self._client._request("POST", "/v1/interactives/practice/create", json=request.model_dump(exclude_none=True))
        return PracticeProblemSetJobCreateResponse(**response)

    def status(self, set_id: str) -> PracticeProblemSetStatusResponse:
        """
        Get the status of a practice problem set.
        """
        response = self._client._request("GET", f"/v1/interactives/practice/status/{set_id}")
        return PracticeProblemSetStatusResponse(**response)

    def grade(self, problem: PracticeProblem) -> GradeFRQResponse:
        """
        Grade a practice problem set.
        """
        request = GradeFRQRequest(problem=problem)
        response = self._client._request("POST", f"/v1/interactives/practice/grade", json=request.model_dump(exclude_none=True))
        return GradeFRQResponse(**response)


class OpennoteClient(BaseClient):
    """Synchronous client for Opennote API."""
    
    def __init__(
        self,
        api_key: str,
        base_url: str = OPENNOTE_BASE_URL,
        timeout: float = 60.0,
        max_retries: int = 3,
    ):
        super().__init__(api_key, base_url, timeout, max_retries)
        self.video = Video(self)
        self.journals = Journals(self)
        self.flashcards = Flashcards(self)
        self.practice = PracticeProblemSets(self)
        self._client = None

    def __enter__(self):
        self._client = httpx.Client(
            base_url=self.base_url,
            headers=self._get_headers(),
            timeout=self.timeout,
        )
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self._client:
            self._client.close()

    def _request(
        self,
        method: str,
        path: str,
        **kwargs
    ) -> dict:
        """Make a request to the API."""
        if not self._client:
            # Create a client for one-off requests
            with httpx.Client(
                base_url=self.base_url,
                headers=self._get_headers(),
                timeout=self.timeout,
            ) as client:
                response = client.request(method, path, **kwargs)
                return self._process_response(response)
        else:
            response = self._client.request(method, path, **kwargs)
            return self._process_response(response)

    def health(self) -> dict:
        """Check API health status."""
        return self._request("GET", "/v1/health")


Opennote: OpennoteClient = OpennoteClient

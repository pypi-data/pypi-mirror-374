import random
from datetime import datetime, timezone
from logging import Logger as NativeLogger
import traceback
from typing import Any, Callable, Optional

from core_infinity_stones.errors.base_error import HttpError
from core_infinity_stones.logging.native_logger import json_event_logger
from core_infinity_stones.logging.schemas import (
    ErrorEvent,
    Event,
    EventLevel,
    EventWithTracesDetails,
    RequestDetails,
)


class Logger:
    def __init__(
        self,
        trace_id: str,
        logger: NativeLogger = json_event_logger,
        request_details: Optional[RequestDetails] = None,
        context_metadata: dict[str, Any] = {},
        topics: set[str] = set(),
        event_codes_to_sampling_percentages_map: Optional[dict[str, int]] = None,
    ):
        """
        Initialize the Logger instance.

        Args:
            trace_id (str): The trace ID for the current request or context.

            logger (NativeLogger): The logger instance to use for logging events.

            request_details (Optional[RequestDetails]): Details about the request,
              such as path, method, and query parameters.

            context_metadata (dict[str, Any]): A dictionary to hold additional context metadata
                that will be included in every log entry.

            topics (set[str]): A set of topics associated with the logger instance.

            event_codes_to_sampling_percentages_map (Optional[dict[str, int]]): A mapping of event
                codes to their sampling percentages.
                This is a dictionary where keys are event codes and values are integers between 0 and 100,
                representing the probability of logging the specified event.
                If None, all events will be logged with 100% sampling.
                If an event code is not present in the map, it will default to 100% sampling.
        """
        self.trace_id = trace_id
        self.logger = logger
        self.request_details = request_details
        self.event_codes_to_sampling_percentages_map = (
            event_codes_to_sampling_percentages_map
        )
        self.context_metadata = context_metadata
        self.topics = topics

    def add_context_metadata(self, key: str, value: Any) -> None:
        self.context_metadata[key] = value

    def remove_context_metadata(self, key: str) -> None:
        self.context_metadata.pop(key, None)

    def add_topic(self, topic: str) -> None:
        self.topics.add(topic)

    def remove_topic(self, topic: str) -> None:
        self.topics.discard(topic)

    def info(self, event: Event) -> None:
        self.log_event(event, logging_level=EventLevel.INFO)

    def warning(self, event: Event) -> None:
        self.log_event(event, logging_level=EventLevel.WARNING)

    def error(self, error: HttpError) -> None:
        event_code = error.debug_details.debug_code

        if not self._should_log_based_on_sampling_percentage(event_code):
            return

        error_event = self._format_error(error)

        self.logger.error(
            error.debug_details.debug_message, extra={"event": error_event}
        )

    def log_event(self, event: Event, logging_level: EventLevel) -> None:
        if not self._should_log_based_on_sampling_percentage(event.code):
            return

        sampling_percentage = (
            self.event_codes_to_sampling_percentages_map.get(event.code, 100)
            if self.event_codes_to_sampling_percentages_map
            else 100
        )

        event_with_tracing_details = EventWithTracesDetails.from_event(
            event,
            trace_id=self.trace_id,
            level=logging_level,
            sampling_percentage=sampling_percentage,
            context_metadata=self.context_metadata,
            topics=self.topics,
            request_details=self.request_details,
        )

        extra = {"event": event_with_tracing_details}

        if logging_level == EventLevel.INFO:
            self.logger.info(event.message, extra=extra)
        elif logging_level == EventLevel.WARNING:
            self.logger.warning(event.message, extra=extra)

    def _format_error(self, error: Optional[BaseException]) -> Optional[dict[str, Any]]:
        """
        Formats the error into a string representation.
        """
        if error is None:
            return None

        if isinstance(error, HttpError):
            event_code = error.debug_details.debug_code

            original_error_details = self._format_error(error.debug_details.caused_by)

            sampling_percentage = (
                self.event_codes_to_sampling_percentages_map.get(event_code, 100)
                if self.event_codes_to_sampling_percentages_map
                else 100
            )

            error_topics = self.topics.copy()

            if error.debug_details.topic:
                error_topics.add(error.debug_details.topic)

            return ErrorEvent(
                id=str(error.debug_details.id),
                trace_id=self.trace_id,
                code=event_code,
                topics=error_topics if error_topics else None,
                level=EventLevel.ERROR,
                path=self.request_details.path if self.request_details else None,
                method=self.request_details.method if self.request_details else None,
                query_params=self.request_details.query_params if self.request_details else None,
                user_agent=self.request_details.user_agent if self.request_details else None,
                message=error.debug_details.debug_message,
                context_metadata=self.context_metadata if self.context_metadata else None,
                details=error.debug_details.debug_details,
                severity=error.debug_details.severity,
                occurred_while=error.debug_details.occurred_while,
                caused_by=original_error_details,
                status_code=error.public_details.status_code,
                public_code=error.public_details.code,
                public_message=error.public_details.message,
                public_details=error.public_details.details,
                sampling_percentage=sampling_percentage,
                timestamp=datetime.now(tz=timezone.utc).isoformat(),
            ).model_dump(mode="json")

        return {
            "type": type(error).__name__,
            "message": str(error),
            "stack_trace": traceback.format_exception(
                type(error), error, error.__traceback__
            ),
        }


    def _should_log_based_on_sampling_percentage(self, event_code: str) -> bool:
        """
        Determines whether an event should be logged based on its code and the configured sampling percentages.
        """

        if not self.event_codes_to_sampling_percentages_map:
            return True

        sampling_percentage = self.event_codes_to_sampling_percentages_map.get(event_code, 100)

        if sampling_percentage <= 0:
            return False

        if sampling_percentage >= 100:
            return True

        return random.randint(0, 100) < sampling_percentage
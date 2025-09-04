from enum import Enum
from typing import Union

from armada_client.armada.event_pb2 import (
    JobSubmittedEvent,
    JobQueuedEvent,
    JobLeasedEvent,
    JobLeaseReturnedEvent,
    JobLeaseExpiredEvent,
    JobPendingEvent,
    JobRunningEvent,
    JobIngressInfoEvent,
    JobFailedEvent,
    JobPreemptingEvent,
    JobPreemptedEvent,
    JobSucceededEvent,
    JobUtilisationEvent,
    JobReprioritizingEvent,
    JobReprioritizedEvent,
    JobCancellingEvent,
    JobCancelledEvent,
    JobTerminatedEvent
)


class EventType(Enum):
    """
    Enum for the event states.
    """

    submitted = "submitted"
    queued = "queued"
    leased = "leased"
    lease_returned = "lease_returned"
    lease_expired = "lease_expired"
    pending = "pending"
    running = "running"
    failed = "failed"
    succeeded = "succeeded"
    reprioritized = "reprioritized"
    cancelling = "cancelling"
    cancelled = "cancelled"
    utilisation = "utilisation"
    ingress_info = "ingress_info"
    reprioritizing = "reprioritizing"
    preempted = "preempted"
    preempting = "preempting"


class JobState(Enum):
    """
    Enum for the job states.
    Used by cancel_jobset.
    """

    QUEUED = 0
    PENDING = 1
    RUNNING = 2
    SUCCEEDED = 3
    FAILED = 4
    UNKNOWN = 5
    SUBMITTED = 6
    LEASED = 7
    PREEMPTED = 8
    CANCELLED = 9
    REJECTED = 10


# Union for the Job Event Types.
OneOfJobEvent = Union[
    JobSubmittedEvent,
    JobQueuedEvent,
    JobLeasedEvent,
    JobLeaseReturnedEvent,
    JobLeaseExpiredEvent,
    JobPendingEvent,
    JobRunningEvent,
    JobIngressInfoEvent,
    JobFailedEvent,
    JobPreemptingEvent,
    JobPreemptedEvent,
    JobSucceededEvent,
    JobUtilisationEvent,
    JobReprioritizingEvent,
    JobReprioritizedEvent,
    JobCancellingEvent,
    JobCancelledEvent,
    JobTerminatedEvent
]

from datetime import datetime
from typing import Optional, List

from .base import KafkaEvent


class TripTrackerEvent(KafkaEvent):
    """
    component - element which executes redirect to different page

    section: banner slider, single banner, product slider, etc.;
    component: banner, product, image;
    social button: tiktok, facebook, instagram
    """

    id: int
    session_uuid: str
    event_name: str
    record_date: str
    source: str
    language: str
    client_id: str
    app_instance_id: Optional[str]
    user_id: Optional[int]
    page: Optional[str]
    referrer: Optional[str]
    device_type: Optional[str]
    device: Optional[str]
    browser: Optional[str]
    os: Optional[str]
    ip_address: Optional[str]
    user_agent: Optional[str]
    cookies: dict = {}
    query_params: dict = {}
    component_type: Optional[str]
    component_id: Optional[int]

    def to_str(self) -> str:
        return f"{self.id} - {self.event_name}"


class TripTrackerClickEvent(TripTrackerEvent):
    """
    object types

    section: banner slider, single banner, product slider, etc.;
    component: banner, product, image;
    social button: tiktok, facebook, instagram
    """

    object_type: str
    object_id: Optional[int]


class TripTrackerItemActionEvent(TripTrackerEvent):
    """
    view_item,
    add_to_cart, add_to_wishlist,
    remove_from_cart, remove_from_wishlist

    quantity goes to extra params
    """

    object_id: int
    extra_params: dict


class TripTrackerCheckoutEvent(TripTrackerEvent):
    """

    step goes to extra_params
    """
    extra_params: dict
    items: List[dict]


class TripTrackerPurchaseEvent(TripTrackerEvent):
    """

    coupon goes to extra_params
    """
    object_id: int
    extra_params: dict
    items: List[dict]


class TripTrackerAuthEvent(TripTrackerEvent):
    """

    vendor goes to extra_param
    """
    extra_params: dict

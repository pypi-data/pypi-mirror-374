
from .topics import KafkaTopic


class KafkaTripTrackerTopic(KafkaTopic):

    # views
    PAGE_VIEW = 'page_view'
    CART_BAG_VIEW = 'cart_bag_view'
    PROFILE_SETTINGS_VIEW = 'profile_settings'
    ORDER_DETAIL_PAGE_VIEW = 'order_detail_page'

    # popups
    LOGIN_POPUP = 'login_popup'
    REGISTER_POPUP = 'register_popup'
    CART_POPUP = 'cart_popup'
    RECOVER_POPUP = 'recover_popup'

    # clicks
    SECTION_CLICK = 'section_click'
    COMPONENT_CLICK = 'component_click'
    SOCIAL_BUTTON_CLICK = 'social_button_click'

    # mobile app events
    SCREEN_VIEW = 'screen_view'
    APP_INSTALL = 'app_install'
    APP_UPDATE = 'app_update'
    APP_DELETE = 'app_delete'

    # ecommerce events
    SEARCH = 'search'
    VIEW_ITEM = 'view_item'
    ADD_TO_CART = 'add_to_cart'
    REMOVE_FROM_CART = 'remove_from_cart'
    ADD_TO_WISHLIST = 'add_to_wishlist'
    REMOVE_FROM_WISHLIST = 'remove_from_wishlist'
    CHECKOUT = 'checkout'
    PURCHASE = 'purchase'

    # user actions
    USER_LOGIN = 'login'
    USER_LOGOUT = 'logout'
    USER_REGISTRATION = 'sign_up'
    B2B_USER_REGISTRATION = 'b2b_sign_up'


import i18n

def translate(key: str, **kwargs) -> str:
    """Translates a given localization key using the i18n system.

    This function acts as a wrapper around `i18n.t`, making it easier to perform
    translations throughout the application. It allows passing variables to be interpolated
    in the translated string via keyword arguments.

    Args:
        key (str): The dot-separated key representing the string to translate
        **kwargs: Arbitrary keyword arguments containing variables to be interpolated
            in the localized message. Each argument should match a placeholder in the
            translation string (e.g., name="Project1", code="ABC123").

    Returns:
        str: The translated string with variables interpolated if provided.
    """
    return i18n.t(key, **kwargs)

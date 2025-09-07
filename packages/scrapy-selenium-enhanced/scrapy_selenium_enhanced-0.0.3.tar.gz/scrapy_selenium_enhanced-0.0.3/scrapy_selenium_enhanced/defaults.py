USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.6367.91 Safari/537.36"

_DEFAULT_DRIVER_ARGUMENTS = [
    '--no-sandbox',
    '--disable-dev-shm-usage',
    '--disable-gpu',
    '--window-size=800,600',
    '--disk-cache-size=0',
    '--disable-blink-features=AutomationControlled',  
]

def get_driver_arguments_with(user_agent: str, headless: bool = True) -> list:
    """Quick helper to get default driver arguments with custom user agent and headless mode.

    Args:
        user_agent (str): User agent (e.g. user agent from settings)
        headless (bool, optional): Enable headless or not. Defaults to True.

    Returns:
        list: a list of driver arguments
    """
    driver_arguments = _DEFAULT_DRIVER_ARGUMENTS.copy()
    driver_arguments.append(f'user-agent={user_agent}')
    if headless:
        driver_arguments.append('--headless=new')
    return driver_arguments

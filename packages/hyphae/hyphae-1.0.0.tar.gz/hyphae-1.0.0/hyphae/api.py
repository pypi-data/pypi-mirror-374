


from truffle.hyphae.hooks_pb2 import AppEnvState

_app_env_state : AppEnvState = AppEnvState()

def get_app_env_state() -> AppEnvState:
    """Retrieve the current application environment state."""
    global _app_env_state
    return _app_env_state

def set_app_env_state(state: AppEnvState):
    """Set the application environment state."""
    global _app_env_state
    _app_env_state.CopyFrom(state)



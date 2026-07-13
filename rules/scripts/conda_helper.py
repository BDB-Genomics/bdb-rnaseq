import sys

def get_conda_env(env_path, workflow):
    is_singularity = False
    try:
        if workflow.deployment_settings.use_singularity:
            is_singularity = True
    except AttributeError:
        pass

    if not is_singularity:
        for arg in sys.argv:
            if "singularity" in arg.lower() or "apptainer" in arg.lower():
                is_singularity = True
                break

    if is_singularity:
        return None
    return env_path

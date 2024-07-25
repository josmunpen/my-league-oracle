from prefect import flow

if __name__ == "__main__":
    flow.from_source(
        source="https://github.com/prefecthq/demos.git", 
        entrypoint="repo_info.py:get_repo_info"
    ).deploy(
        name="deploy_code_demos", 
        work_pool_name="work-pool-2", 
    )
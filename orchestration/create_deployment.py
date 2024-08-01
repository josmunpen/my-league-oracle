from prefect import flow

if __name__ == "__main__":
    flow.from_source(
        source="https://github.com/josmunpen/laliga-oracle.git", 
        entrypoint="orchestration/code_flow.py:hola_mundo",
        ref="prefect-aux"
    ).deploy(
        name="deploy_code_test_liga", 
        work_pool_name="work-pool-2", 
    )
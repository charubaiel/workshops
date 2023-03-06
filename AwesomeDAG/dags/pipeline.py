from dagster import (define_asset_job,
                    schedule,
                    repository,
                    with_resources)

from dagstermill import local_output_notebook_io_manager

from dags.ops import (download_imdb_crew,
                download_imdb_names,
                download_imdb_principals,
                download_imdb_ratings,
                download_imdb_titles
                )
from dags.ops import (clean_cast,
                      clean_names,
                        clean_crew,
                        clean_titles,
                        create_title_dict,
                        create_names_dict
                )
from dags.ops import result_dataset,save_data,save_big_data,asset_notebook


update_imdb = define_asset_job(name='update_imdb_data',
                                config={'ops': {"ratings":
                                                    {"config": {'min_votes':100}}
                                                },
                                        },
                                tags={"dagster/max_retries": 1,
                                    "dagster/retry_strategy": "ALL_STEPS"})



@schedule(
    cron_schedule="00 */10 */3 * *",
    job=update_imdb,
    execution_timezone="Europe/Moscow",
)
def update_imdb_schedule():
    return {}



@repository()
def avito_dagster_parse():

    
    jobs = [update_imdb]

    assets = [download_imdb_crew,
            download_imdb_names,
            download_imdb_principals,
            download_imdb_ratings,
            download_imdb_titles,
            clean_cast,
            clean_crew,
            clean_names,
            clean_titles,
            create_title_dict,
            create_names_dict,
            result_dataset,
            save_data,
            save_big_data,
            asset_notebook
            ]

    schedules = [update_imdb_schedule]

    res = with_resources(
            assets,
            resource_defs={
                "output_notebook_io_manager": local_output_notebook_io_manager,
            },
        )
    return [ 
            jobs,
            schedules,
            res
            ]
{{
    config(
        materialized='incremental', 
        partition_by={
            "field": "starttime", 
            "data_type": "timestamp", 
            "granularity": "day"
        }, 
        cluster_by=["bikeid", "usertype"]
    )
}}

select * from `development`.bike_trips
{{
    config(
        materialized="incremental", 
        partition_by={
            "field": "start_time", 
            "data_type": "timestamp", 
            "granularity": "day"
        }, 
        cluster_by=["bike_id", "user_type"]
    )
}}

select * from {{ ref("stg_bike_trips") }}
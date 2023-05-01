{{
    config(
        materialized="view", 
    )
}}

-- Identify unique primary keys by deduplicating transactions and ignore unknown bike
with trip_data as (
    select
        *, 
        row_number() over(partition by bike_id, start_time order by start_time) as rn
    from {{ target.dataset }}.bike_trips
    where bike_id is not null
)
select
    {{ dbt_utils.generate_surrogate_key(["bike_id", "start_time"]) }} as trip_id, 
    bike_id, 
    start_time, 
    extract(hour from start_time) as start_hour, 
    extract(dayofweek from start_time) as start_day_of_week, 
    end_time, 
    start_station_id, 
    end_station_id, 
    start_station_name, 
    end_station_name, 
    start_station_latitude, 
    start_station_longitude, 
    end_station_latitude, 
    end_station_longitude, 
    {{ is_the_same_start_end_station(start_station_id, end_station_id) }} as is_the_same_start_end_station, 
    trip_duration, 
    user_type, 
    gender, 
    birth_year
from trip_data
where rn = 1

{% if target.name == "dev" %}
limit 100
{% endif %}
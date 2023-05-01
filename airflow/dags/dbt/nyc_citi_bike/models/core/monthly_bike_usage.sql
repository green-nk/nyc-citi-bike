{{
    config(
        materialized="view", 
    )
}}

select
  bike_id, 
  total_minute_trip_duration / n_trips as avg_bike_usage
from (
    select
        bike_id, 
        sum(trip_duration) / 60 as total_minute_trip_duration,  
        count(trip_duration) as n_trips
    from {{ target.dataset }}.fact_bike_trips
    where date(start_time) >= (select extract(date from min(start_time)) from {{ target.dataset }}.fact_bike_trips)
    group by bike_id
)

{% if target.name == "dev" %}
limit 100
{% endif %}
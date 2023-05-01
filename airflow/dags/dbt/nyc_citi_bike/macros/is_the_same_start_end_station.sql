{# Check if the trip has the same start and end station #}

{% macro is_the_same_start_end_station(start_station_id, end_station_id) %}

    case
        when start_station_id = end_station_id then 1
        else 0
    end

{% endmacro %}
#!/bin/bash

dbt run --select $1 --profiles-dir $2 --project-dir $3
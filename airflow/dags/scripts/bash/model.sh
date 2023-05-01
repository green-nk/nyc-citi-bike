#!/bin/bash

cd $3
dbt run --select $1 --profiles-dir $2 --project-dir $3
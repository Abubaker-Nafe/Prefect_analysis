Prefect keeps watching and waiting for any data insertion in receipts collection (in mongodb).
When an insertion happens, prefect runs multiple tasks in which does some calculations & analysis.
After the calculations, a task named "write_to_sql" writes all of the results into separated tables to save them.

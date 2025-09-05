# In order to persist sqlite3 database in a volume
volume_dir="/local_db"
app_project="/app/spartaqube/local_db"
db_file="db.sqlite3"

if [ -f "$volume_dir/$db_file" ]; then # db exists in the volume, we copy (replace basically) it in the app project
    cp "$volume_dir/$db_file" "$app_project/"
    echo "Update db app project using volume."
else # db does not exists in volume (first launch, we copy it from the app project to the volume)
    cp "$app_project/$db_file" "$volume_dir/"
    echo "Copy initial db to volume"
fi

bash -c '/app/docker/ssh_startup.sh'
bash -c '/app/docker/data_store_startup.sh'
bash -c 'supervisord; service supervisor start &'
bash -c "nginx -g 'daemon off;'"
# bash -c 'tail -f /dev/null'
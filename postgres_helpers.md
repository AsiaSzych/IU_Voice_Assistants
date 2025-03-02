## Entracting local volume into backup data and including it in the image
### must be in the rasa_chatbot/actions/database foler

1. Create a volume (if not already created) 
    1. docker volume create rasa_postgres_data
2. Start a container 
    1.  docker run -d   --name rasa_postgres_container   -e POSTGRES_USER=rasa_user   -e POSTGRES_PASSWORD=rasa_password   -e POSTGRES_DB=rasa_db   -p 5432:5432   -v rasa_postgres_data:/var/lib/postgresql/data postgres:13
3. load data to database (usually only in first run - create table and initialize) 
4. Export volume data to backup fiel 
    1. docker run --rm -v rasa_postgres_data:/data -v $(pwd):/backup alpine sh -c "ls -lah /data && tar czf /backup/pg_data_backup.tar.gz -C /data ."
5. Remove running container
    1.  docker stop rasa_postgres_container
    2. docker rm rasa_postgres_container  
6. Build image 
    1. docker build . -t aszych/iu_rasa_database:0.0.x
7. Run image to check 
    1. docker run -d 
        --name shared_postgres_container 
        -e POSTGRES_USER=rasa_user 
        -e POSTGRES_PASSWORD=rasa_password 
        -e POSTGRES_DB=rasa_db 
        -p 5432:5432 
        -v rasa_postgres_data:/var/lib/postgresql/data 
        aszych/iu_rasa_database:0.0.x
    2. Run scripts to check if all data are in the database and if conneciton works
8. Push image to repo
    1. docker push aszych/iu_rasa_database:0.0.x
9. Run docker compose and use app! 
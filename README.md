# Status
The status website for studsec!

# Running locally
To run the website locally use:
```bash
cd ./data
docker-compose up
```

# Submitting logs
To connect a server to the status, It should send a POST request to the 
`/report/<uuid>/<hmac>` endpoint with the following JSON structure:

```
{
    "secret":"<secret>"
    "data":"<data>"
}
```
Additionally, a test script is provided sending some 

# Database access
To attach a shell to the database, please attach a shell to the container and run the following command:
```bash
mongosh -u $MONGO_INITDB_ROOT_USERNAME -p $MONGO_INITDB_ROOT_PASSWORD
```

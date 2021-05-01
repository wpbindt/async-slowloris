To spin up a local test server running apache running at `localhost:80`, run
```
docker build -t fake-server .
```
and then
```
docker run -dit --name test-server -p 80:80 test-server
```


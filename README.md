Website monitoring application
====

The solution gets target's configuration from a file which should be located in settings directory. The specific file to take configuratin from should be specified
as an argument (OR system variable `SETTINGS_FILE`)

database connection should be specified by system variable `DB_CONNECTION_STRING`


Running the application
====
Check Makefile file for available options:

make `unit-test` - run unit-tests

make `run` - runs the application within docker and connects to aiven database. e.g.
`SETTINGS_FILE=settings_single.json DB_CONNECTION_STRING=postgres://avnadmin:<password>@pg-2759775f-andreydubas1991-c170.a.aivencloud.com:13805/website-monitoring?sslmode=require make run`
`SETTINGS_FILE`and DB_CONNECTION_STRING are __mandatory__

make `run-env` - run 3 components: database, request mock and the app within a docker network.
It is recommended to run it with SETTINGS_FILE=integration-test-settings.json, e.g.
`SETTINGS_FILE=integration-test-settings.json make run-env`

make `stop-env` - stop running the application within docker network

make `run-local` - runs the app in venv

Architecture description
====
There is a loop that controls
 - running new requests. All the target objects located in an heapsort array. Everytime a target should be checked, the application takes it from the heapsort and creates RunningRequest object and puts it into another heapsort object.
 - RunningRequest gets removed from heapsort array in 2 cases:
   - response come
   - timeout
   
  It is impossible to predict when exactly a response will come, that is the reason why RinnignRequest object is strongly coupled with heapsort (once a response comes, the corresponding request is deleted by an index that is contained within object), and why I needed custom heapsort implementation (for index tracking purpose).
   We remove timeouted request from the bottom of the array, where a request with lower `wait_until` is located.
These decisions are taked under assunption that there could be many (potentially thousands) requests for the same target.  

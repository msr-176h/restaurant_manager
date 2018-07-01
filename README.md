# app. for managing restaurant inforamtion.

## Environment
  ubuntu 16.04

## Steps to install
1. install mongodb
  ```shell
  # apt-get install mongodb
  ```

2. install dependencies
  ```shell
  # pip install -r requirements.txt
  ```

## Steps to run

1. copy configs
  ```shell
  $ cp configs.py.dst configs.py
  ```
1. set user id/pass and secret key of digest auth
  ```shell
  $ vi configs.py
    // 2-1. set user id/pass in "users"
    //      e.g., users = {"userid": "pass"}
    // 2-2. set secret key in "SECRET_KEY"
  ```
3. execute app.
  ```shell
  $ python app.py
  ```
4. acceess via web browser (visit http://IP_addr:port)
